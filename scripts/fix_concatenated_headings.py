#!/usr/bin/env python3
"""
Fix Concatenated Section Headings

Finds text like "ecosystems.Introduction 800" and adds newlines to separate them.
"""

import sys
import re
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/documents']


def get_service(credentials_path='credentials.json'):
    creds = service_account.Credentials.from_service_account_file(
        credentials_path, scopes=SCOPES)
    return build('docs', 'v1', credentials=creds)


def find_concatenated_headings(service, document_id):
    """Find concatenated section headings"""
    doc = service.documents().get(documentId=document_id).execute()
    content = doc.get('body', {}).get('content', [])

    section_names = ['Introduction', 'Methods', 'Results', 'Discussion',
                    'Abstract', 'Conclusion', 'References', 'Availability']

    issues = []

    for element in content:
        if 'paragraph' in element:
            para = element['paragraph']
            text = ''.join([
                e['textRun'].get('content', '')
                for e in para.get('elements', [])
                if 'textRun' in e
            ])

            for section in section_names:
                # Look for concatenated section headings, excluding journal citations

                # Pattern 1: "text.Section NUMBER" (e.g., "ecosystems.Introduction 800")
                pattern1 = rf'([a-z])\.\s*({section})\s+(\d+)'

                # Pattern 2: "text.Section (" (e.g., "investigation.Results (")
                pattern2 = rf'([a-z])\.\s*({section})\s*\('

                # Pattern 3: "text.Section:" (e.g., "ecology.Conclusion:")
                pattern3 = rf'([a-z])\.\s*({section}):'

                match = None
                for pattern in [pattern1, pattern2, pattern3]:
                    match = re.search(pattern, text)
                    if match:
                        # Exclude if it looks like a journal citation
                        # Check for "Nature Methods", "PLOS Methods", etc.
                        if text[max(0, match.start()-20):match.start()].strip().endswith(('Nature', 'PLOS', 'BMC')):
                            match = None
                            continue
                        break

                if match:
                    # Calculate absolute position in document
                    para_start = element.get('startIndex')
                    match_start = para_start + match.start()
                    match_end = para_start + match.end()

                    # Position where we need to insert newline (before section name)
                    insert_pos = para_start + match.start(2)

                    issues.append({
                        'section': section,
                        'para_start': para_start,
                        'para_end': element.get('endIndex'),
                        'match_pos': insert_pos,
                        'text': text.strip(),
                        'context': text[max(0, match.start()-30):match.end()+30]
                    })
                    break  # Only one issue per paragraph

    return issues


def fix_concatenated_headings(service, document_id, dry_run=True):
    """Fix concatenated headings by inserting newlines"""

    issues = find_concatenated_headings(service, document_id)

    print(f"\n{'='*80}")
    print(f"{'[DRY RUN] ' if dry_run else ''}FIXING CONCATENATED HEADINGS")
    print(f"{'='*80}\n")

    print(f"Found {len(issues)} concatenated headings:\n")

    for i, issue in enumerate(issues, 1):
        print(f"{i}. {issue['section']} at index {issue['match_pos']}")
        print(f"   Context: ...{issue['context']}...")
        print()

    if dry_run or not issues:
        return True

    # Insert newlines before each section heading
    # Process in reverse order to avoid index shifting
    requests = []

    for issue in sorted(issues, key=lambda x: x['match_pos'], reverse=True):
        # Insert two newlines before the section name
        requests.append({
            'insertText': {
                'location': {'index': issue['match_pos']},
                'text': '\n\n'
            }
        })

    if requests:
        try:
            print(f"Inserting newlines before {len(requests)} section headings...")
            result = service.documents().batchUpdate(
                documentId=document_id,
                body={'requests': requests}
            ).execute()
            print(f"✅ Fixed {len(requests)} concatenated headings")
            return True
        except HttpError as error:
            print(f'❌ Error: {error}')
            return False

    return True


def main():
    if len(sys.argv) < 2:
        print("Usage: python fix_concatenated_headings.py DOCUMENT_ID [--fix]")
        sys.exit(1)

    document_id = sys.argv[1]
    fix_mode = '--fix' in sys.argv

    service = get_service()

    if fix_mode:
        fix_concatenated_headings(service, document_id, dry_run=False)
    else:
        fix_concatenated_headings(service, document_id, dry_run=True)
        print(f"\n💡 To apply fixes, run:")
        print(f"   python fix_concatenated_headings.py {document_id} --fix")


if __name__ == '__main__':
    main()
