#!/usr/bin/env python3
"""
Safe Google Docs Editor with Style Preservation and Paperpile Link Protection

This module provides segment-based editing that:
1. Preserves text styles (font size, family, formatting)
2. Protects Paperpile citation links using fuzzy matching
3. Prevents index shifting corruption

Usage:
    from safe_gdoc_editor import SafeGoogleDocEditor

    editor = SafeGoogleDocEditor(service, document_id)
    editor.replace_section('Introduction', new_text, dry_run=True)
"""

import re
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import json

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from citation_matcher import CitationMatcher, CitationLink


@dataclass
class TextStyle:
    """Represents text formatting style"""
    font_family: Optional[str] = None
    font_size: Optional[int] = None
    bold: bool = False
    italic: bool = False
    underline: bool = False

    def to_dict(self) -> Dict:
        """Convert to Google Docs API format"""
        style = {}
        if self.font_family:
            # Google Docs API uses weightedFontFamily, not fontFamily
            style['weightedFontFamily'] = {
                'fontFamily': self.font_family,
                'weight': 400  # Normal weight
            }
        if self.font_size:
            style['fontSize'] = {'magnitude': self.font_size, 'unit': 'PT'}
        if self.bold:
            style['bold'] = self.bold
        if self.italic:
            style['italic'] = self.italic
        if self.underline:
            style['underline'] = self.underline
        return style

    def to_fields(self) -> str:
        """Get fields mask for API requests"""
        fields = []
        if self.font_family:
            fields.append('weightedFontFamily')
        if self.font_size:
            fields.append('fontSize')
        if self.bold:
            fields.append('bold')
        if self.italic:
            fields.append('italic')
        if self.underline:
            fields.append('underline')
        return ','.join(fields) if fields else '*'


@dataclass
class SectionContent:
    """Represents a document section with metadata"""
    section_name: str
    text: str
    links: List[CitationLink]
    style: TextStyle
    start_index: int  # Position in document
    end_index: int    # Position in document


class SafeGoogleDocEditor:
    """
    Safe editor for Google Docs with style preservation and link protection
    """

    SECTION_MARKERS = [
        'Abstract', 'Introduction', 'Results', 'Discussion',
        'Methods', 'Conclusion', 'References', 'Acknowledgments',
        'Data Availability', 'Author Contributions'
    ]

    def __init__(self, service, document_id: str, fuzzy_threshold: float = 0.85):
        """
        Initialize editor

        Args:
            service: Google Docs API service object
            document_id: Google Document ID
            fuzzy_threshold: Similarity threshold for citation matching (0-1)
        """
        self.service = service
        self.document_id = document_id
        self.matcher = CitationMatcher(similarity_threshold=fuzzy_threshold)

    def extract_section(self, section_name: str) -> Optional[SectionContent]:
        """
        Extract a section with text, links, and style

        Returns:
            SectionContent object or None if section not found
        """
        print(f"\n📖 Extracting section: {section_name}")

        try:
            doc = self.service.documents().get(documentId=self.document_id).execute()
            content = doc.get('body', {}).get('content', [])

            section_text_parts = []
            section_links = []
            dominant_style = None
            in_section = False
            section_start_index = None
            section_end_index = None
            current_char_index = 1

            for element in content:
                if 'paragraph' in element:
                    para = element['paragraph']
                    para_start = element.get('startIndex', current_char_index)
                    para_end = element.get('endIndex', current_char_index)
                    para_text = ''

                    for elem in para.get('elements', []):
                        if 'textRun' in elem:
                            text_run = elem['textRun']
                            text_content = text_run.get('content', '')
                            elem_start = elem.get('startIndex', current_char_index)
                            elem_end = elem.get('endIndex', current_char_index)

                            # Check if this marks the section start
                            if not in_section and section_name in text_content:
                                if para.get('paragraphStyle', {}).get('namedStyleType', '').startswith('HEADING'):
                                    in_section = True
                                    section_start_index = para_end  # Start after heading
                                    print(f"  ✓ Found section header at index {section_start_index}")
                                    continue

                            if in_section:
                                # Check if we've hit the next section
                                if any(marker in text_content and marker != section_name
                                      for marker in self.SECTION_MARKERS):
                                    if para.get('paragraphStyle', {}).get('namedStyleType', '').startswith('HEADING'):
                                        section_end_index = para_start
                                        in_section = False
                                        break

                                para_text += text_content

                                # Extract dominant text style (from first substantial text run)
                                if not dominant_style and len(text_content.strip()) > 10:
                                    dominant_style = self._extract_text_style(text_run)

                                # Extract Paperpile links
                                if 'textStyle' in text_run and 'link' in text_run['textStyle']:
                                    link = text_run['textStyle']['link']
                                    url = link.get('url', '')

                                    if 'paperpile.com' in url:
                                        # Calculate position relative to section start
                                        relative_start = len(''.join(section_text_parts))
                                        relative_end = relative_start + len(text_content.strip())

                                        section_links.append(CitationLink(
                                            text=text_content.strip(),
                                            url=url,
                                            start_index=relative_start,
                                            end_index=relative_end
                                        ))

                            current_char_index = elem_end

                    if in_section and para_text.strip():
                        section_text_parts.append(para_text)

                    current_char_index = para_end

                    if section_end_index:
                        break

            if not section_text_parts:
                print(f"  ⚠️ Section '{section_name}' not found or empty")
                return None

            section_text = ''.join(section_text_parts)

            # Ensure we have a valid style (use Google Docs default: 11pt Arial)
            final_style = dominant_style or TextStyle(font_family='Arial', font_size=11)

            print(f"  ✓ Extracted {len(section_text):,} characters")
            print(f"  ✓ Found {len(section_links)} Paperpile citations")
            print(f"  ✓ Dominant style: {final_style.font_size}pt {final_style.font_family}")

            return SectionContent(
                section_name=section_name,
                text=section_text,
                links=section_links,
                style=final_style,
                start_index=section_start_index or 1,
                end_index=section_end_index or current_char_index
            )

        except HttpError as error:
            print(f'❌ Error reading document: {error}')
            return None

    def _extract_text_style(self, text_run: Dict) -> TextStyle:
        """Extract TextStyle from a Google Docs text run"""
        style_data = text_run.get('textStyle', {})

        # Extract fontSize - it might be in different formats
        font_size = None
        if 'fontSize' in style_data:
            font_size_data = style_data['fontSize']
            if isinstance(font_size_data, dict):
                font_size = font_size_data.get('magnitude')
            else:
                font_size = font_size_data

        # Provide sensible defaults for Google Docs (11pt Arial is standard)
        return TextStyle(
            font_family=style_data.get('fontFamily') or 'Arial',
            font_size=font_size or 11,
            bold=style_data.get('bold', False),
            italic=style_data.get('italic', False),
            underline=style_data.get('underline', False)
        )

    def build_replacement_requests(
        self,
        section: SectionContent,
        new_text: str,
        new_links: List[CitationLink]
    ) -> List[Dict]:
        """
        Build API requests to replace section with style preservation

        Returns:
            List of request objects for batchUpdate
        """
        requests = []

        # Request 1: Delete old section content
        # Subtract 1 from endIndex to avoid protected newline at segment end
        requests.append({
            'deleteContentRange': {
                'range': {
                    'startIndex': section.start_index,
                    'endIndex': max(section.start_index + 1, section.end_index - 1)
                }
            }
        })

        # Request 2: Insert new text
        requests.append({
            'insertText': {
                'location': {
                    'index': section.start_index
                },
                'text': new_text
            }
        })

        # Request 3: Apply text style to entire section
        new_end_index = section.start_index + len(new_text)
        style_dict = section.style.to_dict()

        if style_dict:
            requests.append({
                'updateTextStyle': {
                    'range': {
                        'startIndex': section.start_index,
                        'endIndex': new_end_index
                    },
                    'textStyle': style_dict,
                    'fields': section.style.to_fields()
                }
            })

        # Requests 4+: Apply Paperpile links
        for link in new_links:
            abs_start = section.start_index + link.start_index
            abs_end = section.start_index + link.end_index

            requests.append({
                'updateTextStyle': {
                    'range': {
                        'startIndex': abs_start,
                        'endIndex': abs_end
                    },
                    'textStyle': {
                        'link': {
                            'url': link.url
                        }
                    },
                    'fields': 'link'
                }
            })

        return requests

    def replace_section(
        self,
        section_name: str,
        new_text: str,
        dry_run: bool = False
    ) -> bool:
        """
        Replace a section while preserving style and Paperpile links

        Args:
            section_name: Name of section to replace
            new_text: New text content
            dry_run: If True, preview changes without applying

        Returns:
            True if successful, False otherwise
        """
        print(f"\n{'[DRY RUN] ' if dry_run else ''}Replacing section: {section_name}")

        # Step 1: Extract current section
        section = self.extract_section(section_name)
        if not section:
            return False

        # Step 2: Match citations using fuzzy matching
        new_links, modified_text, unmatched = self.matcher.match_citations(
            section.links,
            new_text,
            prepend_cite=True
        )

        if dry_run:
            self._print_dry_run_summary(section, modified_text, new_links, unmatched)
            return True

        # Step 3: Build API requests
        requests = self.build_replacement_requests(section, modified_text, new_links)
        print(f"\n📝 Generated {len(requests)} API requests")

        # Step 4: Execute
        try:
            result = self.service.documents().batchUpdate(
                documentId=self.document_id,
                body={'requests': requests}
            ).execute()

            print(f"✅ Section replaced successfully!")
            print(f"   • Style preserved: {section.style.font_size}pt {section.style.font_family}")
            print(f"   • {len(new_links)} Paperpile citations preserved")
            if unmatched:
                print(f"   • {len(unmatched)} citations marked with 'cite' prefix")
            return True

        except HttpError as error:
            print(f'❌ Error applying replacement: {error}')
            return False

    def _print_dry_run_summary(
        self,
        section: SectionContent,
        modified_text: str,
        new_links: List[CitationLink],
        unmatched: List[str]
    ):
        """Print detailed dry run summary"""
        print(f"\n{'='*60}")
        print(f"DRY RUN SUMMARY")
        print(f"{'='*60}")

        print(f"\n📊 Text changes:")
        print(f"   Old: {len(section.text):,} characters")
        print(f"   New: {len(modified_text):,} characters")
        print(f"   Δ: {len(modified_text) - len(section.text):+,} characters")

        print(f"\n🎨 Style preservation:")
        print(f"   Font: {section.style.font_family}")
        print(f"   Size: {section.style.font_size}pt")
        print(f"   Bold: {section.style.bold}")
        print(f"   Italic: {section.style.italic}")

        print(f"\n📎 Citation changes:")
        print(f"   Old Paperpile links: {len(section.links)}")
        new_citations = self.matcher.find_citations_in_text(modified_text)
        print(f"   New citations found: {len(new_citations)}")
        print(f"   Matched (will preserve): {len(new_links)}")
        print(f"   Prepended with 'cite': {len(unmatched)}")

        # Calculate removed citations
        old_texts = {self.matcher.normalize_citation(link.text) for link in section.links}
        new_texts = {self.matcher.normalize_citation(cite[0]) for cite in new_citations}
        removed = old_texts - new_texts

        if removed:
            print(f"\n⚠️ Citations removed from section ({len(removed)}):")
            for cite in sorted(removed)[:5]:
                print(f"   - {cite}")
            if len(removed) > 5:
                print(f"   ... and {len(removed) - 5} more")

        print(f"\n✅ Ready to proceed:")
        print(f"   • Style will be preserved ({section.style.font_size}pt {section.style.font_family})")
        print(f"   • {len(new_links)} Paperpile links will be preserved")
        print(f"   • {len(unmatched)} citations marked with 'cite' prefix")
        print(f"{'='*60}")


if __name__ == '__main__':
    print("Use apply_manuscript_edits.py for batch operations")
