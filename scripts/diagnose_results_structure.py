#!/usr/bin/env python3
"""
Diagnose Google Doc Results section structure
Shows all subsections, their content types, and potential issues
"""

import sys
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/documents']


def get_service(credentials_path='credentials.json'):
    """Get Google Docs service"""
    creds = service_account.Credentials.from_service_account_file(
        credentials_path, scopes=SCOPES)
    return build('docs', 'v1', credentials=creds)


def diagnose_results_section(document_id: str, credentials_path='credentials.json'):
    """Diagnose Results section structure"""

    service = get_service(credentials_path)

    # Get document
    doc = service.documents().get(documentId=document_id).execute()
    content = doc.get('body', {}).get('content', [])

    print("\n" + "="*80)
    print("RESULTS SECTION STRUCTURE DIAGNOSIS")
    print("="*80)

    in_results = False
    current_subsection = None
    subsection_data = []

    for i, element in enumerate(content):
        if 'paragraph' in element:
            para = element['paragraph']
            style = para.get('paragraphStyle', {}).get('namedStyleType', '')
            text = ''.join([
                e['textRun'].get('content', '')
                for e in para.get('elements', [])
                if 'textRun' in e
            ]).strip()

            # Detect Results section start
            if style == 'HEADING_2' and 'Results' in text:
                in_results = True
                print(f"\n✓ Found Results section at index {element.get('startIndex')}")
                continue

            # Detect Results section end
            if in_results and style == 'HEADING_2':
                print(f"\n✓ Results section ends at index {element.get('startIndex')}")
                break

            # Collect subsections
            if in_results and style == 'HEADING_3' and text:
                if current_subsection:
                    subsection_data.append(current_subsection)

                current_subsection = {
                    'heading': text,
                    'start': element.get('startIndex'),
                    'end': element.get('endIndex'),
                    'paragraphs': [],
                    'tables': [],
                    'index_in_doc': i
                }
                print(f"\n{'='*80}")
                print(f"Subsection {len(subsection_data)+1}: {text}")
                print(f"Start: {element.get('startIndex')}, End: {element.get('endIndex')}")

            # Collect paragraphs
            elif in_results and current_subsection and style == 'NORMAL_TEXT':
                para_text = ''.join([
                    e['textRun'].get('content', '')
                    for e in para.get('elements', [])
                    if 'textRun' in e
                ])

                if para_text.strip():
                    current_subsection['paragraphs'].append({
                        'start': element.get('startIndex'),
                        'end': element.get('endIndex'),
                        'text': para_text[:100] + "..." if len(para_text) > 100 else para_text,
                        'length': len(para_text)
                    })

        # Collect tables
        elif 'table' in element and in_results and current_subsection:
            table = element['table']
            rows = len(table.get('tableRows', []))
            cols = len(table.get('tableRows', [])[0].get('tableCells', [])) if rows > 0 else 0

            current_subsection['tables'].append({
                'start': element.get('startIndex'),
                'end': element.get('endIndex'),
                'rows': rows,
                'cols': cols
            })

    # Add last subsection
    if current_subsection:
        subsection_data.append(current_subsection)

    # Print detailed summary
    print(f"\n{'='*80}")
    print(f"SUMMARY: Found {len(subsection_data)} subsections in Results")
    print(f"{'='*80}\n")

    for i, subsec in enumerate(subsection_data, 1):
        print(f"\n{i}. {subsec['heading']}")
        print(f"   Range: {subsec['start']} → {subsec['end']}")
        print(f"   Content:")
        print(f"     - Paragraphs: {len(subsec['paragraphs'])}")

        if subsec['paragraphs']:
            total_text = sum(p['length'] for p in subsec['paragraphs'])
            print(f"       Total text: {total_text:,} characters")
            print(f"       First paragraph: {subsec['paragraphs'][0]['text'][:80]}...")

            # Show paragraph ranges for debugging
            print(f"       Paragraph ranges:")
            for j, p in enumerate(subsec['paragraphs'][:3], 1):  # Show first 3
                print(f"         P{j}: {p['start']}-{p['end']} ({p['length']} chars)")
            if len(subsec['paragraphs']) > 3:
                print(f"         ... and {len(subsec['paragraphs'])-3} more")

        print(f"     - Tables: {len(subsec['tables'])}")
        if subsec['tables']:
            for j, table in enumerate(subsec['tables'], 1):
                print(f"       Table {j}: {table['rows']}x{table['cols']} at {table['start']}-{table['end']}")

            # Check if any paragraphs are between tables (problematic)
            if len(subsec['tables']) >= 2:
                table_ranges = [(t['start'], t['end']) for t in subsec['tables']]
                para_between_tables = []
                for p in subsec['paragraphs']:
                    for i in range(len(table_ranges)-1):
                        if table_ranges[i][1] < p['start'] < table_ranges[i+1][0]:
                            para_between_tables.append(p)
                if para_between_tables:
                    print(f"       ⚠️  {len(para_between_tables)} paragraphs between tables (complex structure)")

        # Check for potential API issues
        issues = []
        if len(subsec['paragraphs']) == 0:
            issues.append("NO PARAGRAPHS (nothing to replace!)")
        if len(subsec['tables']) > 3:
            issues.append(f"MANY TABLES ({len(subsec['tables'])})")

        if issues:
            print(f"   ⚠️  POTENTIAL ISSUES: {', '.join(issues)}")

    return subsection_data


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python diagnose_results_structure.py DOCUMENT_ID")
        sys.exit(1)

    document_id = sys.argv[1]
    diagnose_results_section(document_id)
