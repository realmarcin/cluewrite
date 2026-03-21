#!/usr/bin/env python3
"""
Test subsection replacement with the fixed subsection_editor
"""

import sys
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Import subsection editor
from subsection_editor import SubsectionEditor

# Import manuscript parser
from apply_manuscript_edits import ManuscriptParser

SCOPES = ['https://www.googleapis.com/auth/documents']


def test_subsection_replacement(
    document_id: str,
    manuscript_path: Path,
    subsection_heading: str,
    credentials_path='credentials.json'
):
    """Test replacing a specific subsection"""

    print(f"\n{'='*80}")
    print(f"TESTING SUBSECTION REPLACEMENT")
    print(f"{'='*80}")
    print(f"Subsection: {subsection_heading}")
    print(f"Manuscript: {manuscript_path}")
    print(f"{'='*80}\n")

    # Authenticate
    creds = service_account.Credentials.from_service_account_file(
        credentials_path, scopes=SCOPES)
    service = build('docs', 'v1', credentials=creds)

    # Create subsection editor
    editor = SubsectionEditor(service, document_id)

    # Find subsection in Google Doc
    subsection = editor.extract_subsection(subsection_heading)

    if not subsection:
        print(f"❌ Could not find subsection: {subsection_heading}")
        return False

    # Extract new text from manuscript
    parser = ManuscriptParser(manuscript_path)

    # For now, extract the whole Results section and find the subsection
    # This is a simplified approach - ideally we'd extract specific subsections
    results_text = parser.extract_section('results')

    if not results_text:
        print(f"❌ Could not extract Results section from manuscript")
        return False

    # Find the subsection in the Results text
    # Simple approach: look for the heading pattern
    import re

    # Try to match the subsection heading (accounting for variations)
    # For "Validation and Functional Interpretation of Important Metagenome Features with Full Length Protein Sequence Analysis"
    # Match "Validation and Functional Interpretation..."
    patterns = [
        r'###\s+' + re.escape(subsection_heading) + r'[^\n]*\n+(.*?)(?=\n###|\Z)',
        r'###\s+Validation and Functional[^\n]*\n+(.*?)(?=\n###|\Z)',  # Shortened
    ]

    subsection_text = None
    for pattern in patterns:
        match = re.search(pattern, results_text, re.DOTALL)
        if match:
            subsection_text = match.group(1).strip()
            break

    if not subsection_text:
        print(f"❌ Could not find subsection text in manuscript")
        print(f"   Tried patterns:")
        for p in patterns:
            print(f"   - {p[:80]}...")
        return False

    # Clean markdown from subsection text
    from apply_manuscript_edits import BatchEditOrchestrator
    cleaned_text = BatchEditOrchestrator.clean_markdown(None, subsection_text)

    print(f"\n📝 Extracted subsection text:")
    print(f"   Length: {len(cleaned_text):,} characters")
    print(f"   Preview: {cleaned_text[:200]}...")
    print()

    # DRY RUN first
    print(f"{'='*80}")
    print(f"DRY RUN")
    print(f"{'='*80}")
    success = editor.replace_subsection_text(subsection, cleaned_text, dry_run=True)

    if not success:
        print(f"❌ Dry run failed")
        return False

    # Ask user to confirm
    response = input(f"\nProceed with actual replacement? (y/n): ")
    if response.lower() != 'y':
        print("Cancelled.")
        return False

    # ACTUAL REPLACEMENT
    print(f"\n{'='*80}")
    print(f"ACTUAL REPLACEMENT")
    print(f"{'='*80}")
    success = editor.replace_subsection_text(subsection, cleaned_text, dry_run=False)

    if success:
        print(f"\n✅ Subsection replaced successfully!")
    else:
        print(f"\n❌ Replacement failed")

    return success


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("Usage: python test_subsection_replacement.py DOCUMENT_ID MANUSCRIPT_FILE SUBSECTION_HEADING")
        print()
        print("Example:")
        print("  python test_subsection_replacement.py \\")
        print("    1gwjtHp863cFv61rJ3gd7l2RGje6tQy6he3bC8YFBuSU \\")
        print("    manuscript/kbaseeco_v2/manuscript_v2_final.md \\")
        print("    'Validation and Functional Interpretation of Important Metagenome Features with Full Length Protein Sequence Analysis'")
        sys.exit(1)

    document_id = sys.argv[1]
    manuscript_file = Path(sys.argv[2])
    subsection_heading = sys.argv[3]

    test_subsection_replacement(document_id, manuscript_file, subsection_heading)
