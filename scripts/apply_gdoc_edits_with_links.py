#!/usr/bin/env python3
"""
Apply Google Doc Edits While Preserving Paperpile Citation Links

This script uses the Google Docs API to replace section text while intelligently
preserving Paperpile citation links by:
1. Extracting link positions from original text
2. Finding matching citations in new text
3. Rebuilding the section with links reapplied

Usage:
    python scripts/apply_gdoc_edits_with_links.py \
        --document-id DOC_ID \
        --section Introduction \
        --new-text-file manuscript/kbaseeco_v2/sections/introduction_v2.md \
        --dry-run
"""

import argparse
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import json

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


SCOPES = ['https://www.googleapis.com/auth/documents']


@dataclass
class CitationLink:
    """Represents a Paperpile citation link"""
    text: str  # e.g., "(Zhao et al. 2022)"
    url: str   # e.g., "https://paperpile.com/c/aBwggu/g8fB"
    start_index: int  # Character position in text
    end_index: int    # Character position in text


@dataclass
class SectionContent:
    """Represents a document section with metadata"""
    section_name: str
    text: str
    links: List[CitationLink]
    start_index: int  # Position in document
    end_index: int    # Position in document


def authenticate(credentials_path: Path):
    """Authenticate with Google Docs API"""
    try:
        with open(credentials_path, 'r') as f:
            cred_data = json.load(f)

        if cred_data.get('type') == 'service_account':
            print("🔑 Using service account authentication")
            creds = service_account.Credentials.from_service_account_file(
                str(credentials_path), scopes=SCOPES)
            return creds
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        raise


def extract_section(service, document_id: str, section_name: str) -> Optional[SectionContent]:
    """
    Extract a section from the document with all its links

    Returns SectionContent with text, links, and document positions
    """
    print(f"\n📖 Reading section: {section_name}")

    try:
        doc = service.documents().get(documentId=document_id).execute()
        content = doc.get('body', {}).get('content', [])

        section_text_parts = []
        section_links = []
        in_section = False
        section_start_index = None
        section_end_index = None
        current_char_index = 1  # Google Docs indices start at 1

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
                            # Check if it's a heading (not just mentioned in text)
                            if para.get('paragraphStyle', {}).get('namedStyleType', '').startswith('HEADING'):
                                in_section = True
                                section_start_index = para_start
                                print(f"  ✓ Found section header at index {section_start_index}")
                                continue  # Skip the header itself

                        if in_section:
                            # Check if we've hit the next section
                            next_section_markers = ['Introduction', 'Results', 'Discussion', 'Methods',
                                                   'Conclusion', 'References', 'Acknowledgments']
                            if any(marker in text_content and marker != section_name
                                  for marker in next_section_markers):
                                if para.get('paragraphStyle', {}).get('namedStyleType', '').startswith('HEADING'):
                                    section_end_index = para_start
                                    in_section = False
                                    break

                            para_text += text_content

                            # Extract links
                            if 'textStyle' in text_run and 'link' in text_run['textStyle']:
                                link = text_run['textStyle']['link']
                                url = link.get('url', '')

                                # Only capture Paperpile links
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

        print(f"  ✓ Extracted {len(section_text)} characters")
        print(f"  ✓ Found {len(section_links)} Paperpile citations")

        return SectionContent(
            section_name=section_name,
            text=section_text,
            links=section_links,
            start_index=section_start_index or 1,
            end_index=section_end_index or current_char_index
        )

    except HttpError as error:
        print(f'❌ Error reading document: {error}')
        return None


def find_citations_in_text(text: str) -> List[Tuple[str, int, int]]:
    """
    Find all citation patterns in text

    Returns list of (citation_text, start_pos, end_pos)
    """
    # Patterns for citations
    patterns = [
        r'\([A-Z][a-z]+\s+et\s+al\.\s+\d{4}[a-z]?\)',  # (Smith et al. 2020)
        r'\([A-Z][a-z]+\s+and\s+[A-Z][a-z]+\s+\d{4}[a-z]?\)',  # (Smith and Jones 2020)
        r'\([A-Z][a-z]+\s+\d{4}[a-z]?\)',  # (Smith 2020)
        r'\([A-Z][a-z]+\s+et\s+al\.\s+\d{4}[a-z]?(?:;\s*[A-Z][a-z]+\s+et\s+al\.\s+\d{4}[a-z]?)+\)',  # Multiple citations
    ]

    citations = []
    for pattern in patterns:
        for match in re.finditer(pattern, text):
            citations.append((match.group(), match.start(), match.end()))

    # Sort by position
    citations.sort(key=lambda x: x[1])

    return citations


def match_citations(old_links: List[CitationLink], new_text: str) -> Tuple[List[CitationLink], str, List[str]]:
    """
    Match old Paperpile links to their positions in new text
    Prepend 'cite' to unmatched citations for easy identification

    Strategy:
    1. Find all citation patterns in new text
    2. Match them to old citations by text similarity
    3. Assign old URLs to matched citations in new text
    4. Prepend 'cite' to unmatched citations

    Returns:
        (matched_links, modified_text, unmatched_list)
    """
    print(f"\n🔗 Matching {len(old_links)} citations to new text...")

    # Find all citations in new text
    new_citations = find_citations_in_text(new_text)
    print(f"  ✓ Found {len(new_citations)} citation patterns in new text")

    # Create a map of citation text to URL
    citation_to_url = {}
    for link in old_links:
        # Normalize citation text (remove extra whitespace)
        normalized = ' '.join(link.text.split())
        citation_to_url[normalized] = link.url

    # Match new citations to old URLs and prepend 'cite' to unmatched
    matched_links = []
    unmatched_citations = []
    text_modifications = []  # (position, old_text, new_text)

    for cite_text, start, end in new_citations:
        normalized = ' '.join(cite_text.split())

        if normalized in citation_to_url:
            # This citation has a Paperpile link - will be preserved
            matched_links.append(CitationLink(
                text=cite_text,
                url=citation_to_url[normalized],
                start_index=start,
                end_index=end
            ))
        else:
            # No Paperpile link - prepend 'cite' for identification
            unmatched_citations.append(cite_text)
            text_modifications.append((start, end, cite_text))

    # Apply 'cite' prefix to unmatched citations (in reverse order to preserve positions)
    modified_text = new_text
    for start, end, cite_text in reversed(text_modifications):
        modified_text = modified_text[:start] + 'cite' + modified_text[start:]

    # Recalculate matched link positions after 'cite' insertions
    # Each 'cite' prefix adds 4 characters before citations that come after it
    cite_prefix_count = 0
    final_matched_links = []

    for link in matched_links:
        # Count how many 'cite' prefixes were added before this link
        offset = 0
        for mod_start, mod_end, _ in text_modifications:
            if mod_start < link.start_index:
                offset += 4  # length of 'cite'

        final_matched_links.append(CitationLink(
            text=link.text,
            url=link.url,
            start_index=link.start_index + offset,
            end_index=link.end_index + offset
        ))

    print(f"  ✓ Matched {len(final_matched_links)}/{len(new_citations)} citations")

    if unmatched_citations:
        print(f"\n  ⚠️ {len(unmatched_citations)} citations prepended with 'cite' (no Paperpile link):")
        for cite in unmatched_citations:
            print(f"     - cite{cite}")
        print(f"  → Easy to find and convert to Paperpile links later")

    return final_matched_links, modified_text, unmatched_citations


def build_replacement_requests(
    section: SectionContent,
    new_text: str,
    new_links: List[CitationLink]
) -> List[Dict]:
    """
    Build Google Docs API requests to replace section and restore links

    Returns list of request objects for batchUpdate
    """
    requests = []

    # Request 1: Delete old section content
    requests.append({
        'deleteContentRange': {
            'range': {
                'startIndex': section.start_index,
                'endIndex': section.end_index
            }
        }
    })

    # Request 2: Insert new text at the same position
    requests.append({
        'insertText': {
            'location': {
                'index': section.start_index
            },
            'text': new_text
        }
    })

    # Requests 3+: Apply links to citation text
    # Note: Indices are relative to the document AFTER the insert
    for link in new_links:
        # Calculate absolute position (section_start + relative position)
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


def apply_section_replacement(
    service,
    document_id: str,
    section_name: str,
    new_text: str,
    dry_run: bool = False
) -> bool:
    """
    Replace a section while preserving Paperpile citation links
    """
    print(f"\n{'[DRY RUN] ' if dry_run else ''}Replacing section: {section_name}")

    # Step 1: Extract current section with links
    section = extract_section(service, document_id, section_name)
    if not section:
        return False

    # Step 2: Match citations in new text and prepend 'cite' to unmatched
    new_links, modified_text, unmatched = match_citations(section.links, new_text)

    if dry_run:
        print(f"\n{'='*60}")
        print(f"DRY RUN SUMMARY")
        print(f"{'='*60}")
        print(f"📊 Text changes:")
        print(f"   Old: {len(section.text):,} characters")
        print(f"   New: {len(modified_text):,} characters")
        print(f"   Δ: {len(modified_text) - len(section.text):+,} characters")
        print(f"\n📎 Citation changes:")
        print(f"   Old Paperpile links: {len(section.links)}")
        print(f"   New citations found: {len(find_citations_in_text(new_text))}")
        print(f"   Matched (will preserve): {len(new_links)}")
        print(f"   Prepended with 'cite': {len(unmatched)}")

        # Calculate removed citations
        old_cite_texts = {' '.join(link.text.split()) for link in section.links}
        new_cite_texts = {' '.join(cite[0].split()) for cite in find_citations_in_text(new_text)}
        removed = old_cite_texts - new_cite_texts

        if removed:
            print(f"\n⚠️ Citations removed from section ({len(removed)}):")
            for cite in sorted(removed)[:5]:  # Show first 5
                print(f"   - {cite}")
            if len(removed) > 5:
                print(f"   ... and {len(removed) - 5} more")

        print(f"\n✅ Ready to proceed:")
        print(f"   • {len(new_links)} Paperpile links will be preserved")
        print(f"   • {len(unmatched)} citations marked with 'cite' prefix")
        print(f"{'='*60}")
        return True

    # Step 3: Build API requests with modified text
    requests = build_replacement_requests(section, modified_text, new_links)
    print(f"\n📝 Generated {len(requests)} API requests")

    # Step 4: Execute replacement
    try:
        result = service.documents().batchUpdate(
            documentId=document_id,
            body={'requests': requests}
        ).execute()

        print(f"✅ Section replaced successfully!")
        print(f"   {len(new_links)} Paperpile citations preserved")
        return True

    except HttpError as error:
        print(f'❌ Error applying replacement: {error}')
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Replace Google Doc sections while preserving Paperpile links"
    )
    parser.add_argument('--document-id', required=True, help="Google Doc ID")
    parser.add_argument('--section', required=True,
                       choices=['Introduction', 'Results', 'Discussion', 'Methods'],
                       help="Section to replace")
    parser.add_argument('--new-text', required=True, help="New text content (or path to file)")
    parser.add_argument('--credentials', type=Path, default=Path('credentials.json'),
                       help="Path to credentials.json")
    parser.add_argument('--dry-run', action='store_true', help="Preview without applying")

    args = parser.parse_args()

    # Load new text
    new_text_path = Path(args.new_text)
    if new_text_path.exists():
        new_text = new_text_path.read_text()
        print(f"📄 Loaded new text from: {new_text_path}")
    else:
        new_text = args.new_text

    # Authenticate
    creds = authenticate(args.credentials)
    service = build('docs', 'v1', credentials=creds)

    # Apply replacement
    success = apply_section_replacement(
        service,
        args.document_id,
        args.section,
        new_text,
        args.dry_run
    )

    if success:
        if args.dry_run:
            print("\n💡 Run without --dry-run to apply changes")
        else:
            print(f"\n🔗 View document: https://docs.google.com/document/d/{args.document_id}/edit")

    return 0 if success else 1


if __name__ == '__main__':
    exit(main())
