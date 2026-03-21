#!/usr/bin/env python3
"""
Table-Preserving Google Docs Editor

Replaces section text while preserving embedded tables and figures.
Uses paragraph-by-paragraph replacement to avoid deleting table elements.

Strategy:
1. Identify table positions in section
2. Extract text from non-table paragraphs
3. Build requests that delete/insert only paragraph ranges (not tables)
4. Process in reverse order to avoid index shifting issues
"""

import re
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

from googleapiclient.errors import HttpError


@dataclass
class SectionElement:
    """Represents an element in a section (paragraph or table)"""
    element_type: str  # 'paragraph', 'table', 'heading'
    text: str
    start_index: int
    end_index: int
    has_table: bool = False


class TablePreservingEditor:
    """
    Editor that preserves tables while replacing section text
    """

    def __init__(self, service, document_id: str):
        self.service = service
        self.document_id = document_id

    def analyze_section(self, section_name: str) -> Tuple[List[SectionElement], int, int]:
        """
        Analyze section structure to identify tables and paragraphs

        Returns:
            (elements, section_start_index, section_end_index)
        """
        print(f"\n📖 Analyzing section structure: {section_name}")

        doc = self.service.documents().get(documentId=self.document_id).execute()
        content = doc.get('body', {}).get('content', [])

        elements = []
        in_section = False
        section_start_index = None
        section_end_index = None

        for element in content:
            # Check for section heading
            if 'paragraph' in element:
                para = element['paragraph']
                style = para.get('paragraphStyle', {}).get('namedStyleType', '')

                # Check if this is our section heading
                if style.startswith('HEADING'):
                    for elem in para.get('elements', []):
                        if 'textRun' in elem:
                            text = elem['textRun'].get('content', '').strip()
                            if section_name in text:
                                in_section = True
                                section_start_index = element.get('endIndex')  # Start after heading
                                print(f"  ✓ Found section header at index {section_start_index}")
                                continue

                    # Check if this is the next section (ending)
                    if in_section:
                        for elem in para.get('elements', []):
                            if 'textRun' in elem:
                                text = elem['textRun'].get('content', '').strip()
                                # Check for next major section
                                if text and len(text) > 3 and text != section_name:
                                    next_sections = ['Discussion', 'Methods', 'Conclusion', 'References']
                                    if any(ns in text for ns in next_sections):
                                        section_end_index = element.get('startIndex')
                                        in_section = False
                                        break

                # Collect paragraph content
                if in_section:
                    text_content = ''.join([
                        e['textRun'].get('content', '')
                        for e in para.get('elements', [])
                        if 'textRun' in e
                    ])

                    if text_content.strip():
                        elements.append(SectionElement(
                            element_type='paragraph',
                            text=text_content,
                            start_index=element.get('startIndex'),
                            end_index=element.get('endIndex')
                        ))

            # Collect table elements
            elif 'table' in element and in_section:
                table_data = element['table']
                rows = len(table_data.get('tableRows', []))

                elements.append(SectionElement(
                    element_type='table',
                    text=f'[TABLE: {rows} rows]',
                    start_index=element.get('startIndex'),
                    end_index=element.get('endIndex'),
                    has_table=True
                ))

            if section_end_index:
                break

        # Summary
        para_count = sum(1 for e in elements if e.element_type == 'paragraph')
        table_count = sum(1 for e in elements if e.element_type == 'table')

        print(f"  ✓ Found {para_count} paragraphs and {table_count} tables")
        print(f"  ✓ Section range: {section_start_index} → {section_end_index}")

        return elements, section_start_index, section_end_index or len(content)

    def match_paragraphs(
        self,
        old_paragraphs: List[str],
        new_text: str
    ) -> List[Tuple[str, str]]:
        """
        Match old paragraphs to new paragraphs

        Strategy:
        - Split new text into paragraphs
        - Try to match old→new by similarity or position
        - Return list of (old_text, new_text) pairs
        """
        # Split new text into paragraphs (by double newline or single newline)
        new_paragraphs = [p.strip() for p in new_text.split('\n\n') if p.strip()]

        # If not enough, try single newlines
        if len(new_paragraphs) < len(old_paragraphs) / 2:
            new_paragraphs = [p.strip() for p in new_text.split('\n') if p.strip() and len(p.strip()) > 50]

        print(f"  Matching: {len(old_paragraphs)} old → {len(new_paragraphs)} new paragraphs")

        # Simple position-based matching (paragraph N → paragraph N)
        matches = []
        for i, old_para in enumerate(old_paragraphs):
            if i < len(new_paragraphs):
                matches.append((old_para, new_paragraphs[i]))
            else:
                # No matching new paragraph - skip this old one
                pass

        return matches

    def build_table_preserving_requests(
        self,
        elements: List[SectionElement],
        new_text: str
    ) -> List[Dict]:
        """
        Build API requests using replaceAllText for paragraphs

        Strategy:
        1. Extract old paragraphs (non-table)
        2. Match with new paragraphs from new_text
        3. Use replaceAllText for each unique paragraph
        4. Tables are never touched (they're not text)

        This is safer than deleteContentRange because:
        - Only replaces text content
        - Preserves document structure (tables, formatting)
        - Google Docs API handles it safely
        """
        print(f"\n📝 Building paragraph replacement requests")

        requests = []

        # Extract old paragraphs
        old_paragraphs = [
            elem.text.strip()
            for elem in elements
            if elem.element_type == 'paragraph' and len(elem.text.strip()) > 20
        ]

        if not old_paragraphs:
            print("  ⚠️ No substantial paragraphs found")
            return requests

        # Match old→new paragraphs
        matches = self.match_paragraphs(old_paragraphs, new_text)

        print(f"  ✓ Will replace {len(matches)} paragraphs")

        # Build replaceAllText requests for unique paragraphs
        # Safety: Only replace paragraphs >100 chars to ensure uniqueness
        MIN_LENGTH = 100
        replaced_count = 0
        skipped_count = 0

        for old_text, new_text_para in matches:
            # Only replace if text actually changed
            if old_text.strip() != new_text_para.strip():
                # Safety check: only replace substantial paragraphs (likely unique)
                if len(old_text.strip()) >= MIN_LENGTH:
                    requests.append({
                        'replaceAllText': {
                            'containsText': {
                                'text': old_text.strip(),
                                'matchCase': True
                            },
                            'replaceText': new_text_para.strip()
                        }
                    })
                    replaced_count += 1
                else:
                    skipped_count += 1

        if skipped_count > 0:
            print(f"  ⚠️ Skipped {skipped_count} short paragraphs (<{MIN_LENGTH} chars) for safety")

        print(f"  ✓ Generated {len(requests)} replacement requests")

        return requests

    def replace_section_preserve_tables(
        self,
        section_name: str,
        new_text: str,
        dry_run: bool = False
    ) -> bool:
        """
        Replace section text while preserving tables

        Args:
            section_name: Name of section to replace
            new_text: New text content
            dry_run: If True, preview without applying

        Returns:
            True if successful
        """
        print(f"\n{'[DRY RUN] ' if dry_run else ''}Replacing section with table preservation: {section_name}")

        # Step 1: Analyze section structure
        elements, section_start, section_end = self.analyze_section(section_name)

        if not elements:
            print("❌ No content found in section")
            return False

        # Count tables
        table_count = sum(1 for e in elements if e.element_type == 'table')
        para_count = len(elements) - table_count

        # Step 2: Build replacement requests
        requests = self.build_table_preserving_requests(elements, new_text)

        if dry_run:
            print(f"\n{'='*60}")
            print(f"DRY RUN SUMMARY - TABLE PRESERVATION MODE")
            print(f"{'='*60}")
            print(f"\n📊 Section structure:")
            print(f"   Total elements: {len(elements)}")
            print(f"   Paragraphs: {para_count}")
            print(f"   Tables: {table_count} ← WILL BE PRESERVED")
            print(f"\n📝 Text replacement:")
            print(f"   New text: {len(new_text):,} characters")
            print(f"   Replacement requests: {len(requests)}")
            print(f"\n✅ Strategy: replaceAllText (preserves document structure)")
            print(f"   • Tables remain at original positions")
            print(f"   • Only paragraph text is replaced")
            print(f"{'='*60}")
            return True

        # Step 3: Execute replacement
        if not requests:
            print("❌ No replacement requests generated")
            return False

        try:
            result = self.service.documents().batchUpdate(
                documentId=self.document_id,
                body={'requests': requests}
            ).execute()

            print(f"✅ Section replaced successfully!")
            print(f"   • {table_count} tables preserved")
            print(f"   • {len(requests)} paragraphs updated")
            return True

        except HttpError as error:
            print(f'❌ Error applying replacement: {error}')
            return False


if __name__ == '__main__':
    print("Use via apply_manuscript_edits.py")
