#!/usr/bin/env python3
"""
Delete misplaced Methods section from Results
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


def delete_misplaced_methods(document_id, dry_run=True):
    """Delete Methods content that was incorrectly inserted in Results"""

    service = get_service()
    doc = service.documents().get(documentId=document_id).execute()
    content = doc.get('body', {}).get('content', [])

    # Find the misplaced Methods section
    # It starts with "Metagenome Feature Data Preparation" (HEADING_3) around index 23181
    # It ends before "Discussion" (HEADING_2) around index 37943

    misplaced_start = None
    misplaced_end = None

    in_results = False
    for element in content:
        if 'paragraph' in element:
            para = element['paragraph']
            style = para.get('paragraphStyle', {}).get('namedStyleType', '')
            text = ''.join([
                e['textRun'].get('content', '')
                for e in para.get('elements', [])
                if 'textRun' in e
            ]).strip()

            # Track Results section
            if style == 'HEADING_2' and text.startswith('Results'):
                in_results = True
                continue

            # In Results, find "Metagenome Feature Data Preparation" heading (not in Results context)
            if in_results and style == 'HEADING_3' and 'Metagenome Feature Data Preparation' in text:
                # Check if previous content doesn't suggest this belongs in Results
                misplaced_start = element.get('startIndex')
                print(f"Found misplaced Methods start at index {misplaced_start}")
                print(f"  Text: {text[:60]}")
                continue

            # Find Discussion heading (end of misplaced section)
            if misplaced_start and style == 'HEADING_2' and text.startswith('Discussion'):
                misplaced_end = element.get('startIndex')
                print(f"Found end at Discussion, index {misplaced_end}")
                break

    if not misplaced_start or not misplaced_end:
        print("Could not find misplaced Methods section boundaries")
        return False

    print(f"\n{'='*80}")
    print(f"MISPLACED METHODS SECTION")
    print(f"{'='*80}")
    print(f"Start: {misplaced_start}")
    print(f"End: {misplaced_end}")
    print(f"Size: {misplaced_end - misplaced_start} characters")
    print()

    if dry_run:
        print(f"[DRY RUN] Would delete content from {misplaced_start} to {misplaced_end}")
        return True

    # Delete the misplaced section
    print(f"Deleting misplaced Methods section...")

    try:
        requests = [{
            'deleteContentRange': {
                'range': {
                    'startIndex': misplaced_start,
                    'endIndex': misplaced_end
                }
            }
        }]

        result = service.documents().batchUpdate(
            documentId=document_id,
            body={'requests': requests}
        ).execute()

        print(f"✅ Deleted misplaced Methods section ({misplaced_end - misplaced_start} chars)")
        return True

    except HttpError as error:
        print(f'❌ Error: {error}')
        return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python delete_misplaced_methods.py DOCUMENT_ID [--delete]")
        sys.exit(1)

    document_id = sys.argv[1]
    delete_mode = '--delete' in sys.argv

    if delete_mode:
        delete_misplaced_methods(document_id, dry_run=False)
    else:
        delete_misplaced_methods(document_id, dry_run=True)
        print(f"\n💡 To delete misplaced Methods, run:")
        print(f"   python delete_misplaced_methods.py {document_id} --delete")


if __name__ == '__main__':
    main()
