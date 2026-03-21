#!/usr/bin/env python3
"""
Extract tables from DOCX files.

Extracts all tables from a DOCX file and saves them as TSV files
for comparison with source data files.
"""

import argparse
import sys
from pathlib import Path
from typing import List, Dict
import json

try:
    from docx import Document
except ImportError:
    print("Error: python-docx not installed. Run: pip3 install python-docx")
    sys.exit(1)


def extract_tables_from_docx(docx_path: Path) -> List[Dict]:
    """Extract all tables from DOCX file."""
    doc = Document(docx_path)
    tables_data = []

    for table_idx, table in enumerate(doc.tables, start=1):
        # Extract table content
        rows = []
        for row in table.rows:
            row_data = [cell.text.strip() for cell in row.cells]
            rows.append(row_data)

        # Determine table dimensions
        num_rows = len(rows)
        num_cols = len(rows[0]) if rows else 0

        # Try to infer table caption from preceding paragraph
        caption = None
        # In Word, table captions are often in the paragraph before the table
        # We'll need to search through paragraphs to find this

        table_info = {
            "table_number": table_idx,
            "num_rows": num_rows,
            "num_cols": num_cols,
            "caption": caption,
            "header": rows[0] if rows else [],
            "data": rows,
            "preview": rows[:5] if len(rows) > 5 else rows
        }

        tables_data.append(table_info)

    return tables_data


def save_table_as_tsv(table_data: Dict, output_path: Path):
    """Save table data as TSV file."""
    with open(output_path, 'w') as f:
        for row in table_data["data"]:
            f.write("\t".join(row) + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Extract tables from DOCX file"
    )
    parser.add_argument(
        "--docx",
        type=Path,
        required=True,
        help="Path to DOCX file"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Output directory for extracted tables"
    )

    args = parser.parse_args()

    if not args.docx.exists():
        print(f"Error: DOCX file not found: {args.docx}")
        sys.exit(1)

    args.output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Extracting tables from: {args.docx}")
    tables = extract_tables_from_docx(args.docx)

    print(f"\nFound {len(tables)} tables")

    # Save each table
    table_info_list = []
    for table in tables:
        table_num = table["table_number"]

        # Save as TSV
        tsv_path = args.output_dir / f"extracted_table_{table_num}.tsv"
        save_table_as_tsv(table, tsv_path)

        # Print preview
        print(f"\n{'='*80}")
        print(f"Table {table_num}: {table['num_rows']}x{table['num_cols']}")
        if table['caption']:
            print(f"Caption: {table['caption']}")
        print(f"Saved to: {tsv_path}")

        print("\nPreview (first 5 rows):")
        for row in table['preview']:
            print("  " + " | ".join(row[:5]))  # Show first 5 columns

        # Save metadata
        table_info_list.append({
            "table_number": table_num,
            "dimensions": f"{table['num_rows']}x{table['num_cols']}",
            "caption": table['caption'],
            "file": str(tsv_path.name),
            "header": table['header'][:5] if len(table['header']) > 5 else table['header']
        })

    # Save summary
    summary_path = args.output_dir / "tables_summary.json"
    with open(summary_path, 'w') as f:
        json.dump(table_info_list, f, indent=2)

    print(f"\n{'='*80}")
    print(f"Summary saved to: {summary_path}")


if __name__ == "__main__":
    main()
