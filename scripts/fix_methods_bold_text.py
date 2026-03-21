#!/usr/bin/env python3
"""
Remove bold formatting from Methods paragraph text
Keep only Normal text (not bold) for regular paragraphs
"""

import sys
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/documents']


def get_service(credentials_path='credentials.json'):
    creds = service_account.Credentials.from_service_account_file(
        credentials_path, scopes=SCOPES)
    return build('docs', 'v1', credentials=creds)


def fix_methods_bold_text(document_id, dry_run=True):
    """Remove bold formatting from Methods paragraph text"""

    service = get_service()
    doc = service.documents().get(documentId=document_id).execute()
    content = doc.get('body', {}).get('content', [])

    print(f"\n{'='*80}")
    print(f"{'[DRY RUN] ' if dry_run else ''}REMOVING BOLD FROM METHODS PARAGRAPHS")
    print(f"{'='*80}\n")

    # Find Methods section and collect bold text ranges
    in_methods = False
    bold_ranges = []

    for element in content:
        if 'paragraph' in element:
            para = element['paragraph']
            style = para.get('paragraphStyle', {}).get('namedStyleType', '')

            # Get text
            text = ''.join([
                e['textRun'].get('content', '')
                for e in para.get('elements', [])
                if 'textRun' in e
            ]).strip()

            # Track Methods section
            if style == 'HEADING_2' and text.startswith('Methods'):
                in_methods = True
                print(f"Found Methods section at index {element.get('startIndex')}")
                continue

            # End of Methods
            if in_methods and style == 'HEADING_2':
                print(f"Methods section ends at index {element.get('startIndex')}")
                break

            # In Methods, find bold text in NORMAL_TEXT paragraphs
            if in_methods and style == 'NORMAL_TEXT':
                elements = para.get('elements', [])

                for elem in elements:
                    if 'textRun' in elem:
                        text_run = elem['textRun']
                        text_style = text_run.get('textStyle', {})

                        # Check if bold
                        if text_style.get('bold', False):
                            start = elem.get('startIndex')
                            end = elem.get('endIndex')
                            content_text = text_run.get('content', '')

                            bold_ranges.append({
                                'start': start,
                                'end': end,
                                'text': content_text[:50]
                            })

    print(f"\nFound {len(bold_ranges)} bold text ranges in Methods paragraphs")

    if bold_ranges and not dry_run:
        # Show first few examples
        for i, br in enumerate(bold_ranges[:3], 1):
            print(f"  {i}. Index {br['start']}-{br['end']}: {br['text']}...")

    if dry_run or not bold_ranges:
        return True

    # Create requests to remove bold formatting
    requests = []

    for bold_range in bold_ranges:
        requests.append({
            'updateTextStyle': {
                'range': {
                    'startIndex': bold_range['start'],
                    'endIndex': bold_range['end']
                },
                'textStyle': {
                    'bold': False
                },
                'fields': 'bold'
            }
        })

    print(f"\nRemoving bold formatting from {len(requests)} text ranges...")

    try:
        # Process in batches of 100 to avoid API limits
        batch_size = 100
        for i in range(0, len(requests), batch_size):
            batch = requests[i:i+batch_size]
            result = service.documents().batchUpdate(
                documentId=document_id,
                body={'requests': batch}
            ).execute()
            print(f"  Processed batch {i//batch_size + 1} ({len(batch)} ranges)")

        print(f"\n✅ Removed bold formatting from {len(requests)} text ranges")
        return True

    except HttpError as error:
        print(f'❌ Error: {error}')
        return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python fix_methods_bold_text.py DOCUMENT_ID [--fix]")
        sys.exit(1)

    document_id = sys.argv[1]
    fix_mode = '--fix' in sys.argv

    if fix_mode:
        fix_methods_bold_text(document_id, dry_run=False)
    else:
        fix_methods_bold_text(document_id, dry_run=True)
        print(f"\n💡 To remove bold formatting, run:")
        print(f"   python fix_methods_bold_text.py {document_id} --fix")


if __name__ == '__main__':
    main()
