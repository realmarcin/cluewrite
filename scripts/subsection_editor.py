#!/usr/bin/env python3
"""
Subsection Editor - Replace subsections while preserving tables

Strategy: Process Results section-by-subsection instead of all at once
Each subsection has simpler structure = easier to handle safely
"""

from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from googleapiclient.errors import HttpError


@dataclass
class SubsectionContent:
    """Content within a subsection"""
    heading: str
    paragraphs: List[Tuple[int, int, str]]  # (start, end, text)
    tables: List[Tuple[int, int]]  # (start, end)
    subsection_start: int
    subsection_end: int


class SubsectionEditor:
    """
    Editor that works on subsections (HEADING_3 level)
    """

    def __init__(self, service, document_id: str):
        self.service = service
        self.document_id = document_id

    def find_results_subsections(self) -> List[str]:
        """Find all subsection headings in Results"""
        doc = self.service.documents().get(documentId=self.document_id).execute()
        content = doc.get('body', {}).get('content', [])

        in_results = False
        subsections = []

        for element in content:
            if 'paragraph' in element:
                para = element['paragraph']
                style = para.get('paragraphStyle', {}).get('namedStyleType', '')
                text = ''.join([e['textRun'].get('content', '') for e in para.get('elements', []) if 'textRun' in e]).strip()

                if style == 'HEADING_2' and 'Results' in text:
                    in_results = True
                    continue

                if in_results and style == 'HEADING_2':
                    break

                if in_results and style == 'HEADING_3' and text:
                    subsections.append(text)

        return subsections

    def extract_subsection(self, subsection_heading: str) -> Optional[SubsectionContent]:
        """
        Extract a specific subsection's content

        Returns paragraphs and tables within that subsection
        """
        print(f"\n📖 Extracting subsection: {subsection_heading[:50]}...")

        doc = self.service.documents().get(documentId=self.document_id).execute()
        content = doc.get('body', {}).get('content', [])

        in_subsection = False
        subsection_start = None
        subsection_end = None
        paragraphs = []
        tables = []

        for element in content:
            # Check for our subsection heading
            if 'paragraph' in element:
                para = element['paragraph']
                style = para.get('paragraphStyle', {}).get('namedStyleType', '')
                text = ''.join([e['textRun'].get('content', '') for e in para.get('elements', []) if 'textRun' in e]).strip()

                # Found our subsection
                if style == 'HEADING_3' and subsection_heading in text:
                    in_subsection = True
                    subsection_start = element.get('endIndex')  # Start after heading
                    continue

                # Next subsection or main section = end of our subsection
                if in_subsection and style in ['HEADING_2', 'HEADING_3']:
                    subsection_end = element.get('startIndex')
                    break

                # Collect paragraphs in subsection
                if in_subsection and style == 'NORMAL_TEXT':
                    para_text = ''.join([e['textRun'].get('content', '') for e in para.get('elements', []) if 'textRun' in e])
                    if para_text.strip():
                        paragraphs.append((
                            element.get('startIndex'),
                            element.get('endIndex'),
                            para_text
                        ))

            # Collect tables in subsection
            elif 'table' in element and in_subsection:
                tables.append((element.get('startIndex'), element.get('endIndex')))

        if not paragraphs and not tables:
            print(f"  ⚠️ No content found")
            return None

        print(f"  ✓ Found {len(paragraphs)} paragraphs, {len(tables)} tables")

        return SubsectionContent(
            heading=subsection_heading,
            paragraphs=paragraphs,
            tables=tables,
            subsection_start=subsection_start or 0,
            subsection_end=subsection_end or len(content)
        )

    def replace_subsection_text(
        self,
        subsection: SubsectionContent,
        new_text: str,
        dry_run: bool = False
    ) -> bool:
        """
        Replace text in subsection while preserving tables

        Uses simple deleteContentRange + insertText for each paragraph
        """
        print(f"\n{'[DRY RUN] ' if dry_run else ''}Replacing subsection: {subsection.heading[:40]}...")

        if dry_run:
            print(f"  Paragraphs: {len(subsection.paragraphs)}")
            print(f"  Tables: {len(subsection.tables)} ← PRESERVED")
            print(f"  New text: {len(new_text):,} chars")
            return True

        # Build requests - delete all paragraph ranges, insert new text
        requests = []

        # Delete paragraphs in reverse order
        for start, end, text in sorted(subsection.paragraphs, reverse=True):
            requests.append({
                'deleteContentRange': {
                    'range': {
                        'startIndex': start,
                        'endIndex': end
                    }
                }
            })

        # Determine safe insertion point
        # If tables exist before first paragraph, insert after last leading table
        insertion_index = subsection.subsection_start

        if subsection.tables and subsection.paragraphs:
            first_table_start = subsection.tables[0][0]
            first_para_start = subsection.paragraphs[0][0]

            # If table comes before paragraphs, insert after the last consecutive leading table
            if first_table_start < first_para_start:
                last_leading_table_end = subsection.tables[0][1]

                for table_start, table_end in subsection.tables[1:]:
                    # Check if this table is still before first paragraph
                    if table_end <= first_para_start:
                        last_leading_table_end = table_end
                    else:
                        break

                insertion_index = last_leading_table_end
                print(f"  ℹ️  Adjusted insertion index to {insertion_index} (after leading table(s))")

        # Insert new text at safe insertion point
        requests.append({
            'insertText': {
                'location': {
                    'index': insertion_index
                },
                'text': new_text + '\n\n'
            }
        })

        # Execute
        try:
            result = self.service.documents().batchUpdate(
                documentId=self.document_id,
                body={'requests': requests}
            ).execute()

            print(f"  ✅ Replaced successfully")
            return True

        except HttpError as error:
            print(f'  ❌ Error: {error}')
            return False


if __name__ == '__main__':
    print("Use via apply_manuscript_edits.py")
