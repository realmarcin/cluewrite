#!/usr/bin/env python3
"""
Surgical Section Editor - Preserves Tables with Precise Range Operations

Uses deleteContentRange + insertText on specific paragraph ranges only.
Tables remain completely untouched.

Strategy:
1. Map section structure: [para1, table1, para2, para3, table2, ...]
2. Build operations list (process in reverse order to avoid index shifting)
3. For each paragraph range:
   - Delete exact range
   - Insert new text at that position
4. Tables at different ranges are never touched

Key difference from previous approach:
- NOT using replaceAllText (too broad, affects headings)
- Using deleteContentRange with EXACT paragraph indices
- Processing in reverse order (end → start) to manage shifting
"""

import re
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

from googleapiclient.errors import HttpError


@dataclass
class ContentElement:
    """Represents a content element (paragraph or table)"""
    element_type: str  # 'paragraph' or 'table'
    text: str
    start_index: int
    end_index: int
    style_type: str = ''  # For detecting if it's a heading


class SurgicalSectionEditor:
    """
    Surgical editor that replaces paragraphs while preserving tables
    """

    def __init__(self, service, document_id: str):
        self.service = service
        self.document_id = document_id

    def map_section_structure(self, section_name: str) -> Tuple[List[ContentElement], int, int]:
        """
        Map the complete structure of a section

        Returns:
            (elements, section_start, section_end)
        """
        print(f"\n📖 Mapping section structure: {section_name}")

        doc = self.service.documents().get(documentId=self.document_id).execute()
        content = doc.get('body', {}).get('content', [])

        elements = []
        in_section = False
        section_start = None
        section_end = None

        for element in content:
            # Check for section heading
            if 'paragraph' in element:
                para = element['paragraph']
                style = para.get('paragraphStyle', {}).get('namedStyleType', '')

                # Detect section start
                if style.startswith('HEADING'):
                    text = ''.join([e['textRun'].get('content', '') for e in para.get('elements', []) if 'textRun' in e]).strip()

                    if section_name in text:
                        in_section = True
                        section_start = element.get('endIndex')  # Start after heading
                        print(f"  ✓ Section starts at index {section_start}")
                        continue

                    # Detect section end
                    if in_section and text:
                        next_sections = ['Discussion', 'Methods', 'Conclusion', 'References']
                        if any(ns in text for ns in next_sections):
                            section_end = element.get('startIndex')
                            in_section = False
                            break

                # Collect paragraph elements within section
                if in_section:
                    para_text = ''.join([e['textRun'].get('content', '') for e in para.get('elements', []) if 'textRun' in e])

                    if para_text.strip():
                        elements.append(ContentElement(
                            element_type='paragraph',
                            text=para_text,
                            start_index=element.get('startIndex'),
                            end_index=element.get('endIndex'),
                            style_type=style
                        ))

            # Collect table elements
            elif 'table' in element and in_section:
                table = element['table']
                rows = len(table.get('tableRows', []))

                elements.append(ContentElement(
                    element_type='table',
                    text=f'[TABLE: {rows} rows]',
                    start_index=element.get('startIndex'),
                    end_index=element.get('endIndex')
                ))

        # Summary
        para_count = sum(1 for e in elements if e.element_type == 'paragraph')
        table_count = sum(1 for e in elements if e.element_type == 'table')

        print(f"  ✓ Found {para_count} paragraphs, {table_count} tables")
        print(f"  ✓ Range: {section_start} → {section_end or 'end'}")

        return elements, section_start, section_end or len(content)

    def build_surgical_requests(
        self,
        elements: List[ContentElement],
        new_text: str,
        section_start: int
    ) -> List[Dict]:
        """
        Build surgical replacement requests

        Strategy:
        1. Separate paragraphs from tables
        2. Delete ALL paragraph ranges (tables untouched)
        3. Insert new text at section start
        4. All operations in single batchUpdate (atomic)
        """
        print(f"\n🔪 Building surgical replacement requests")

        # Split new text into paragraphs
        new_paragraphs = [p.strip() for p in new_text.split('\n\n') if p.strip() and len(p.strip()) > 20]

        # Filter out only NORMAL paragraphs (not tables, not headings)
        # Skip paragraphs that are headings (subsections)
        paragraph_elements = [
            e for e in elements
            if e.element_type == 'paragraph' and not e.style_type.startswith('HEADING')
        ]

        heading_count = sum(1 for e in elements if e.element_type == 'paragraph' and e.style_type.startswith('HEADING'))

        print(f"  Old paragraphs (normal text): {len(paragraph_elements)}")
        print(f"  Headings (preserved): {heading_count}")
        print(f"  New paragraphs: {len(new_paragraphs)}")

        # Build request list (process in REVERSE order to avoid index shifting)
        requests = []

        # Step 1: Delete all paragraph ranges (reverse order)
        paragraph_ranges = [(e.start_index, e.end_index) for e in paragraph_elements]
        paragraph_ranges.sort(reverse=True)  # Process from end to start

        for start, end in paragraph_ranges:
            requests.append({
                'deleteContentRange': {
                    'range': {
                        'startIndex': start,
                        'endIndex': end
                    }
                }
            })

        # Step 2: Insert all new text at section start
        # After deletions, tables remain but paragraphs are gone
        full_new_text = '\n\n'.join(new_paragraphs)

        requests.append({
            'insertText': {
                'location': {
                    'index': section_start
                },
                'text': full_new_text + '\n\n'
            }
        })

        print(f"  ✓ Generated {len(requests)} requests")
        print(f"    - {len(paragraph_ranges)} deletions (paragraphs only)")
        print(f"    - 1 insertion ({len(full_new_text):,} chars)")

        return requests

    def replace_section_surgical(
        self,
        section_name: str,
        new_text: str,
        dry_run: bool = False
    ) -> bool:
        """
        Surgically replace section preserving tables

        Args:
            section_name: Section to replace
            new_text: New text content
            dry_run: Preview mode

        Returns:
            Success status
        """
        print(f"\n{'[DRY RUN] ' if dry_run else ''}🔪 SURGICAL SECTION REPLACEMENT")

        # Map structure
        elements, section_start, section_end = self.map_section_structure(section_name)

        if not elements:
            print("❌ No content found")
            return False

        # Count elements
        para_count = sum(1 for e in elements if e.element_type == 'paragraph')
        table_count = sum(1 for e in elements if e.element_type == 'table')

        if dry_run:
            print(f"\n{'='*60}")
            print(f"DRY RUN - SURGICAL MODE")
            print(f"{'='*60}")
            print(f"\n📊 Current structure:")
            print(f"   Paragraphs: {para_count}")
            print(f"   Tables: {table_count} ← PRESERVED")
            print(f"\n📝 New content: {len(new_text):,} characters")
            print(f"\n✅ Strategy:")
            print(f"   1. Delete {para_count} paragraph ranges")
            print(f"   2. Insert new text at position {section_start}")
            print(f"   3. Tables remain at original positions")
            print(f"{'='*60}")
            return True

        # Build requests
        requests = self.build_surgical_requests(elements, new_text, section_start)

        if not requests:
            print("❌ No requests generated")
            return False

        # Execute
        try:
            result = self.service.documents().batchUpdate(
                documentId=self.document_id,
                body={'requests': requests}
            ).execute()

            print(f"✅ Section replaced successfully!")
            print(f"   • {table_count} tables preserved")
            print(f"   • {para_count} paragraphs replaced")
            return True

        except HttpError as error:
            print(f'❌ Error: {error}')
            return False


if __name__ == '__main__':
    print("Use via apply_manuscript_edits.py")
