#!/usr/bin/env python3
"""
Replace Methods section with v2 content - targeted approach
Ensures we target the actual HEADING_2 Methods section, not references
"""

import sys
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

sys.path.insert(0, '/Users/marcin/Documents/VIMSS/ontology/repo-research-writer/scripts')
from safe_gdoc_editor import SafeGoogleDocEditor
from citation_matcher import CitationMatcher

SCOPES = ['https://www.googleapis.com/auth/documents']


def get_service(credentials_path='credentials.json'):
    creds = service_account.Credentials.from_service_account_file(
        credentials_path, scopes=SCOPES)
    return build('docs', 'v1', credentials=creds)


def find_methods_section_heading(service, document_id):
    """Find the actual HEADING_2 Methods section (not references)"""
    doc = service.documents().get(documentId=document_id).execute()
    content = doc.get('body', {}).get('content', [])

    methods_sections = []

    for element in content:
        if 'paragraph' in element:
            para = element['paragraph']
            style = para.get('paragraphStyle', {}).get('namedStyleType', '')
            text = ''.join([
                e['textRun'].get('content', '')
                for e in para.get('elements', [])
                if 'textRun' in e
            ]).strip()

            # Look for HEADING_2 that starts with "Methods"
            if style == 'HEADING_2' and text.startswith('Methods'):
                methods_sections.append({
                    'index': element.get('startIndex'),
                    'end': element.get('endIndex'),
                    'text': text
                })

    return methods_sections


def replace_methods_section(document_id, manuscript_path, dry_run=True):
    """Replace the Methods section with v2 content"""

    service = get_service()

    # Find all Methods sections
    methods_sections = find_methods_section_heading(service, document_id)

    print(f"\n{'='*80}")
    print(f"METHODS SECTION REPLACEMENT")
    print(f"{'='*80}\n")

    print(f"Found {len(methods_sections)} Methods HEADING_2 sections:")
    for i, section in enumerate(methods_sections, 1):
        print(f"  {i}. Index {section['index']}: {section['text']}")

    if len(methods_sections) == 0:
        print("❌ No Methods section found!")
        return False

    if len(methods_sections) > 1:
        print(f"\n⚠️  Multiple Methods sections found!")
        print(f"   Will target the LAST one (most likely the correct location)")
        target_section = methods_sections[-1]  # Last one
    else:
        target_section = methods_sections[0]

    print(f"\n📍 Targeting Methods section at index {target_section['index']}")

    if dry_run:
        print(f"\n[DRY RUN] Would replace Methods section at index {target_section['index']}")
        return True

    # Use SafeGoogleDocEditor to replace the section
    print(f"\nReplacing Methods section...")

    # Load manuscript
    from apply_manuscript_edits import ManuscriptParser
    parser = ManuscriptParser(manuscript_path)
    new_methods_text = parser.extract_section('methods')

    if not new_methods_text:
        print("❌ Could not extract Methods from manuscript")
        return False

    print(f"  Extracted {len(new_methods_text):,} characters from v2 manuscript")

    # Create editor
    editor = SafeGoogleDocEditor(service, document_id)

    # Replace section
    success = editor.replace_section('Methods', new_methods_text, dry_run=False)

    if success:
        print(f"\n✅ Methods section replaced successfully!")
    else:
        print(f"\n❌ Methods section replacement failed")

    return success


def main():
    if len(sys.argv) < 3:
        print("Usage: python replace_methods_targeted.py DOCUMENT_ID MANUSCRIPT_PATH [--replace]")
        print()
        print("Example:")
        print("  python replace_methods_targeted.py \\")
        print("    1gwjtHp863cFv61rJ3gd7l2RGje6tQy6he3bC8YFBuSU \\")
        print("    manuscript/kbaseeco_v2/manuscript_v2_final.md \\")
        print("    --replace")
        sys.exit(1)

    document_id = sys.argv[1]
    manuscript_path = Path(sys.argv[2])
    replace_mode = '--replace' in sys.argv

    if replace_mode:
        replace_methods_section(document_id, manuscript_path, dry_run=False)
    else:
        replace_methods_section(document_id, manuscript_path, dry_run=True)
        print(f"\n💡 To replace Methods section, run:")
        print(f"   python replace_methods_targeted.py {document_id} {manuscript_path} --replace")


if __name__ == '__main__':
    main()
