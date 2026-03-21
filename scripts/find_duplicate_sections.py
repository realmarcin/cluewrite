#!/usr/bin/env python3
"""
Find duplicate sections in Google Doc
"""

import sys
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/documents']


def get_service(credentials_path='credentials.json'):
    creds = service_account.Credentials.from_service_account_file(
        credentials_path, scopes=SCOPES)
    return build('docs', 'v1', credentials=creds)


def find_all_sections(document_id):
    """Find all section headings in document"""
    service = get_service()
    doc = service.documents().get(documentId=document_id).execute()
    content = doc.get('body', {}).get('content', [])

    sections = []

    for i, element in enumerate(content):
        if 'paragraph' in element:
            para = element['paragraph']
            style = para.get('paragraphStyle', {}).get('namedStyleType', '')

            # Get text
            text = ''.join([
                e['textRun'].get('content', '')
                for e in para.get('elements', [])
                if 'textRun' in e
            ]).strip()

            # Check if it's a heading
            if style.startswith('HEADING') and text:
                sections.append({
                    'index': element.get('startIndex'),
                    'end': element.get('endIndex'),
                    'style': style,
                    'text': text[:80],
                    'element_num': i
                })

    return sections


def main():
    if len(sys.argv) < 2:
        print("Usage: python find_duplicate_sections.py DOCUMENT_ID")
        sys.exit(1)

    document_id = sys.argv[1]
    sections = find_all_sections(document_id)

    print(f"\n{'='*80}")
    print(f"ALL SECTIONS IN DOCUMENT ({len(sections)} found)")
    print(f"{'='*80}\n")

    # Group by section name
    section_counts = {}
    for section in sections:
        # Extract main section name (first word usually)
        name = section['text'].split()[0] if section['text'].split() else section['text']
        if name not in section_counts:
            section_counts[name] = []
        section_counts[name].append(section)

    # Show all sections in order
    for section in sections:
        print(f"Index {section['index']:6d} | {section['style']:10s} | {section['text']}")

    # Highlight duplicates
    print(f"\n{'='*80}")
    print(f"DUPLICATE SECTIONS")
    print(f"{'='*80}\n")

    duplicates = {name: secs for name, secs in section_counts.items() if len(secs) > 1}

    if duplicates:
        for name, secs in duplicates.items():
            print(f"\n'{name}' appears {len(secs)} times:")
            for i, sec in enumerate(secs, 1):
                print(f"  {i}. Index {sec['index']:6d} | {sec['style']:10s} | {sec['text']}")
    else:
        print("No duplicate sections found.")

    # Check for Methods specifically
    methods_sections = [s for s in sections if 'method' in s['text'].lower()]
    if len(methods_sections) > 1:
        print(f"\n{'='*80}")
        print(f"⚠️  FOUND {len(methods_sections)} METHODS SECTIONS:")
        print(f"{'='*80}\n")
        for i, sec in enumerate(methods_sections, 1):
            print(f"{i}. Index {sec['index']:6d} | {sec['style']:10s} | {sec['text']}")


if __name__ == '__main__':
    main()
