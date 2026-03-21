#!/usr/bin/env python3
"""
Fix Formatting Issues in Google Doc

Detects and fixes:
1. Extra blank lines between paragraphs/sections
2. Headings not in proper heading style
3. Headings concatenated with text (missing newlines)
"""

import sys
import re
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/documents']


def get_service(credentials_path='credentials.json'):
    """Get Google Docs service"""
    creds = service_account.Credentials.from_service_account_file(
        credentials_path, scopes=SCOPES)
    return build('docs', 'v1', credentials=creds)


class FormattingFixer:
    """Fix common formatting issues in Google Docs"""

    def __init__(self, service, document_id: str):
        self.service = service
        self.document_id = document_id

    def diagnose(self):
        """Diagnose formatting issues"""
        print(f"\n{'='*80}")
        print(f"FORMATTING DIAGNOSTICS")
        print(f"{'='*80}\n")

        doc = self.service.documents().get(documentId=self.document_id).execute()
        content = doc.get('body', {}).get('content', [])

        issues = []

        # Track consecutive newlines
        consecutive_newlines = 0
        last_element_type = None

        for i, element in enumerate(content):
            if 'paragraph' in element:
                para = element['paragraph']
                style = para.get('paragraphStyle', {}).get('namedStyleType', '')

                # Get text content
                text = ''.join([
                    e['textRun'].get('content', '')
                    for e in para.get('elements', [])
                    if 'textRun' in e
                ])

                # Check for excessive newlines (empty paragraphs)
                if text.strip() == '':
                    consecutive_newlines += 1
                    if consecutive_newlines >= 3:
                        issues.append({
                            'type': 'excessive_newlines',
                            'index': element.get('startIndex'),
                            'count': consecutive_newlines,
                            'context': f"After {last_element_type}"
                        })
                else:
                    consecutive_newlines = 0

                # Check for heading text without heading style
                if style == 'NORMAL_TEXT' and text.strip():
                    # Check if it looks like a heading
                    if (text.strip().endswith(':') or
                        (text.strip()[0].isupper() and len(text.strip().split()) <= 10 and
                         not text.strip().endswith('.'))):
                        # Could be a heading
                        issues.append({
                            'type': 'potential_heading',
                            'index': element.get('startIndex'),
                            'text': text.strip()[:60],
                            'style': style
                        })

                # Check for concatenated text (heading merged with previous paragraph)
                if text.strip():
                    # Look for patterns like "text.Introduction" or "text.Methods"
                    section_names = ['Introduction', 'Methods', 'Results', 'Discussion',
                                   'Abstract', 'Conclusion', 'References', 'Availability']
                    for section in section_names:
                        if section in text and not text.strip().startswith(section):
                            # Section name appears mid-text
                            match = re.search(rf'[a-z]\.?{section}', text)
                            if match:
                                issues.append({
                                    'type': 'concatenated_heading',
                                    'index': element.get('startIndex'),
                                    'text': text[max(0, match.start()-20):match.end()+20],
                                    'section': section
                                })

                last_element_type = style

        # Report issues
        print(f"Found {len(issues)} formatting issues:\n")

        issues_by_type = {}
        for issue in issues:
            issue_type = issue['type']
            if issue_type not in issues_by_type:
                issues_by_type[issue_type] = []
            issues_by_type[issue_type].append(issue)

        for issue_type, issue_list in issues_by_type.items():
            print(f"\n{issue_type.upper().replace('_', ' ')} ({len(issue_list)} found):")
            print(f"{'-'*80}")
            for issue in issue_list[:5]:  # Show first 5
                if issue_type == 'excessive_newlines':
                    print(f"  • Index {issue['index']}: {issue['count']} consecutive blank lines")
                    print(f"    Context: {issue['context']}")
                elif issue_type == 'potential_heading':
                    print(f"  • Index {issue['index']}: '{issue['text']}'")
                    print(f"    Current style: {issue['style']} (should be HEADING?)")
                elif issue_type == 'concatenated_heading':
                    print(f"  • Index {issue['index']}: '{issue['text']}'")
                    print(f"    Section '{issue['section']}' concatenated with text")

            if len(issue_list) > 5:
                print(f"  ... and {len(issue_list) - 5} more")

        return issues

    def fix_excessive_newlines(self, dry_run=True):
        """Remove excessive blank lines (3+ consecutive)"""
        print(f"\n{'='*80}")
        print(f"{'[DRY RUN] ' if dry_run else ''}FIXING EXCESSIVE NEWLINES")
        print(f"{'='*80}\n")

        doc = self.service.documents().get(documentId=self.document_id).execute()
        content = doc.get('body', {}).get('content', [])

        # Find sequences of 3+ blank paragraphs
        blank_sequences = []
        current_sequence = []

        for element in content:
            if 'paragraph' in element:
                para = element['paragraph']
                text = ''.join([
                    e['textRun'].get('content', '')
                    for e in para.get('elements', [])
                    if 'textRun' in e
                ])

                if text.strip() == '':
                    current_sequence.append((element.get('startIndex'), element.get('endIndex')))
                else:
                    if len(current_sequence) >= 3:
                        blank_sequences.append(current_sequence)
                    current_sequence = []

        if len(current_sequence) >= 3:
            blank_sequences.append(current_sequence)

        print(f"Found {len(blank_sequences)} sequences of 3+ blank lines")

        if dry_run or not blank_sequences:
            return True

        # Delete excessive blanks (keep max 2)
        requests = []
        for sequence in blank_sequences:
            # Delete all but first 2 blank lines
            for start, end in sequence[2:]:
                requests.append({
                    'deleteContentRange': {
                        'range': {'startIndex': start, 'endIndex': end}
                    }
                })

        if requests:
            print(f"Deleting {len(requests)} excessive blank lines...")
            # Process in reverse order
            requests.reverse()

            try:
                result = self.service.documents().batchUpdate(
                    documentId=self.document_id,
                    body={'requests': requests}
                ).execute()
                print(f"✅ Removed {len(requests)} excessive blank lines")
                return True
            except HttpError as error:
                print(f'❌ Error: {error}')
                return False

        return True

    def fix_concatenated_headings(self, dry_run=True):
        """Fix headings concatenated with previous text"""
        print(f"\n{'='*80}")
        print(f"{'[DRY RUN] ' if dry_run else ''}FIXING CONCATENATED HEADINGS")
        print(f"{'='*80}\n")

        doc = self.service.documents().get(documentId=self.document_id).execute()
        content = doc.get('body', {}).get('content', [])

        issues = []
        section_names = ['Introduction', 'Methods', 'Results', 'Discussion',
                        'Abstract', 'Conclusion', 'References', 'Availability']

        for element in content:
            if 'paragraph' in element:
                para = element['paragraph']
                text = ''.join([
                    e['textRun'].get('content', '')
                    for e in para.get('elements', [])
                    if 'textRun' in e
                ])

                for section in section_names:
                    # Look for patterns like "text.Introduction" or "ecosystems.Methods"
                    match = re.search(rf'([a-z]\.?)\s*({section})\s+\d+', text)
                    if match:
                        issues.append({
                            'start': element.get('startIndex'),
                            'end': element.get('endIndex'),
                            'text': text,
                            'section': section,
                            'match_pos': match.start(2)  # Position of section name
                        })
                        break

        print(f"Found {len(issues)} concatenated headings")
        for issue in issues[:5]:
            print(f"  • '{issue['text'][:80]}'")

        if dry_run or not issues:
            return True

        # For each issue, we need to:
        # 1. Split the text at the section name
        # 2. Delete the old paragraph
        # 3. Insert the first part
        # 4. Insert newlines
        # 5. Insert the section name with proper heading style

        # This is complex - recommend manual fix for now
        print(f"\n⚠️ Automatic fix for concatenated headings requires manual intervention")
        print(f"   Please manually add newlines before these section headings:")
        for issue in issues:
            print(f"   - {issue['section']} at index {issue['start']}")

        return True


def main():
    if len(sys.argv) < 2:
        print("Usage: python fix_formatting_issues.py DOCUMENT_ID [--fix]")
        print()
        print("Examples:")
        print("  # Diagnose only")
        print("  python fix_formatting_issues.py 1gwjtHp863cFv61rJ3gd7l2RGje6tQy6he3bC8YFBuSU")
        print()
        print("  # Fix issues")
        print("  python fix_formatting_issues.py 1gwjtHp863cFv61rJ3gd7l2RGje6tQy6he3bC8YFBuSU --fix")
        sys.exit(1)

    document_id = sys.argv[1]
    fix_mode = '--fix' in sys.argv

    service = get_service()
    fixer = FormattingFixer(service, document_id)

    # Diagnose
    issues = fixer.diagnose()

    if not issues:
        print(f"\n✅ No formatting issues found!")
        return

    if fix_mode:
        print(f"\n{'='*80}")
        print(f"APPLYING FIXES")
        print(f"{'='*80}")

        # Fix excessive newlines
        fixer.fix_excessive_newlines(dry_run=False)

        # Fix concatenated headings (manual for now)
        fixer.fix_concatenated_headings(dry_run=False)
    else:
        print(f"\n💡 To fix these issues, run:")
        print(f"   python fix_formatting_issues.py {document_id} --fix")


if __name__ == '__main__':
    main()
