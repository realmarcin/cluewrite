#!/usr/bin/env python3
"""
Fix Methods subsection heading styles
Convert bold Normal text to Heading 3 for subsection headings
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


def fix_methods_headings(document_id, dry_run=True):
    """Fix Methods subsection heading styles"""

    service = get_service()
    doc = service.documents().get(documentId=document_id).execute()
    content = doc.get('body', {}).get('content', [])

    # Known Methods subsection headings from v2 manuscript
    subsection_headings = [
        'Generation of metagenome features for ML',
        'Model training, evaluation, comparison, and selection',
        'Feature permutation and importance analysis',
        'Sequence-based validation of characteristic features',
        'Characteristic feature significance analysis',
        'Confusion Matrix Analysis',
        'Tanglegram analysis of ecosystem hierarchies and ecosystem classifications',
        'Ecosystem network versus ecosystem hierarchy comparison',
        'Metagenome Feature Data Preparation',  # Opening bold heading
    ]

    print(f"\n{'='*80}")
    print(f"{'[DRY RUN] ' if dry_run else ''}FIXING METHODS SUBSECTION HEADING STYLES")
    print(f"{'='*80}\n")

    # Find Methods section first
    in_methods = False
    methods_start = None
    headings_to_fix = []

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
                methods_start = element.get('startIndex')
                print(f"Found Methods section at index {methods_start}")
                continue

            # End of Methods section
            if in_methods and style == 'HEADING_2':
                print(f"Methods section ends at index {element.get('startIndex')}")
                break

            # In Methods, find paragraphs that should be Heading 3
            if in_methods and style == 'NORMAL_TEXT':
                # Check if this text matches a known subsection heading
                for heading in subsection_headings:
                    if heading in text:
                        # Check if text is bold
                        elements = para.get('elements', [])
                        is_bold = False
                        for elem in elements:
                            if 'textRun' in elem:
                                text_style = elem['textRun'].get('textStyle', {})
                                if text_style.get('bold', False):
                                    is_bold = True
                                    break

                        if is_bold or text.strip() == heading:
                            headings_to_fix.append({
                                'start': element.get('startIndex'),
                                'end': element.get('endIndex'),
                                'text': text[:60]
                            })
                            print(f"  Found heading to fix: {text[:60]}")
                            break

    print(f"\nFound {len(headings_to_fix)} subsection headings to convert to Heading 3")

    if dry_run or not headings_to_fix:
        return True

    # Create requests to update paragraph styles
    requests = []

    for heading in headings_to_fix:
        # Update paragraph style to HEADING_3
        requests.append({
            'updateParagraphStyle': {
                'range': {
                    'startIndex': heading['start'],
                    'endIndex': heading['end']
                },
                'paragraphStyle': {
                    'namedStyleType': 'HEADING_3'
                },
                'fields': 'namedStyleType'
            }
        })

    print(f"\nApplying Heading 3 style to {len(requests)} subsections...")

    try:
        result = service.documents().batchUpdate(
            documentId=document_id,
            body={'requests': requests}
        ).execute()

        print(f"✅ Updated {len(requests)} subsection headings to Heading 3")
        return True

    except HttpError as error:
        print(f'❌ Error: {error}')
        return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python fix_methods_heading_styles.py DOCUMENT_ID [--fix]")
        sys.exit(1)

    document_id = sys.argv[1]
    fix_mode = '--fix' in sys.argv

    if fix_mode:
        fix_methods_headings(document_id, dry_run=False)
    else:
        fix_methods_headings(document_id, dry_run=True)
        print(f"\n💡 To apply fixes, run:")
        print(f"   python fix_methods_heading_styles.py {document_id} --fix")


if __name__ == '__main__':
    main()
