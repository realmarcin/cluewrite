#!/usr/bin/env python3
"""
Convert TSV data tables to markdown table format for inclusion in manuscripts.

This utility reads TSV files (e.g., from data_tables/) and generates
properly formatted markdown tables that can be inserted into manuscript sections.

Usage:
    # Convert single TSV file
    python scripts/rrwrite-convert-tsv-to-table.py --input data_tables/repository_statistics.tsv

    # Convert with custom caption
    python scripts/rrwrite-convert-tsv-to-table.py \
        --input data_tables/repository_statistics.tsv \
        --caption "Repository statistics summary"

    # Convert and save to file
    python scripts/rrwrite-convert-tsv-to-table.py \
        --input data_tables/repository_statistics.tsv \
        --output tables/table1.md

    # Convert multiple tables
    python scripts/rrwrite-convert-tsv-to-table.py \
        --input-dir data_tables/ \
        --output-dir tables/
"""

import argparse
import csv
from pathlib import Path


def convert_tsv_to_markdown(tsv_file, caption=None, max_rows=None):
    """
    Convert a TSV file to markdown table format.

    Args:
        tsv_file: Path to TSV file
        caption: Optional table caption
        max_rows: Maximum number of data rows to include (None = all)

    Returns:
        String containing markdown table
    """
    tsv_file = Path(tsv_file)

    if not tsv_file.exists():
        raise FileNotFoundError(f"TSV file not found: {tsv_file}")

    # Read TSV, skipping comment lines
    with open(tsv_file, 'r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        rows = [row for row in reader if row and not row[0].startswith('#')]

    if not rows:
        return "<!-- Empty table -->\n"

    # Build markdown table
    lines = []

    # Add caption if provided
    if caption:
        lines.append(f"**{caption}**\n")

    # Header row
    header = rows[0]
    lines.append("| " + " | ".join(header) + " |")

    # Separator row
    lines.append("| " + " | ".join(["---"] * len(header)) + " |")

    # Data rows
    data_rows = rows[1:max_rows+1] if max_rows else rows[1:]
    for row in data_rows:
        # Pad row if necessary
        padded_row = row + [""] * (len(header) - len(row))
        lines.append("| " + " | ".join(padded_row[:len(header)]) + " |")

    # Add truncation note if rows were limited
    if max_rows and len(rows) - 1 > max_rows:
        lines.append(f"\n*Note: Showing {max_rows} of {len(rows)-1} rows*")

    return "\n".join(lines) + "\n"


def convert_directory(input_dir, output_dir, max_rows=None):
    """
    Convert all TSV files in a directory to markdown tables.

    Args:
        input_dir: Directory containing TSV files
        output_dir: Directory to write markdown tables
        max_rows: Maximum rows per table
    """
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)

    if not input_dir.exists():
        raise FileNotFoundError(f"Input directory not found: {input_dir}")

    output_dir.mkdir(parents=True, exist_ok=True)

    tsv_files = list(input_dir.glob("*.tsv"))

    if not tsv_files:
        print(f"No TSV files found in {input_dir}")
        return

    print(f"Converting {len(tsv_files)} TSV files from {input_dir}...")

    for tsv_file in tsv_files:
        # Generate caption from filename
        caption = tsv_file.stem.replace('_', ' ').title()

        # Convert to markdown
        markdown = convert_tsv_to_markdown(
            tsv_file,
            caption=caption,
            max_rows=max_rows
        )

        # Write output file
        output_file = output_dir / f"{tsv_file.stem}.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markdown)

        print(f"  ✓ {tsv_file.name} → {output_file.name}")


def main():
    parser = argparse.ArgumentParser(
        description="Convert TSV data tables to markdown format"
    )

    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        '--input',
        help='Path to single TSV file to convert'
    )
    input_group.add_argument(
        '--input-dir',
        help='Directory containing TSV files to convert'
    )

    # Output options
    parser.add_argument(
        '--output',
        help='Output markdown file path (for --input mode)'
    )
    parser.add_argument(
        '--output-dir',
        help='Output directory for markdown files (for --input-dir mode)'
    )

    # Table options
    parser.add_argument(
        '--caption',
        help='Table caption (for --input mode)'
    )
    parser.add_argument(
        '--max-rows',
        type=int,
        help='Maximum number of data rows to include (default: all)'
    )

    args = parser.parse_args()

    # Single file conversion
    if args.input:
        markdown = convert_tsv_to_markdown(
            args.input,
            caption=args.caption,
            max_rows=args.max_rows
        )

        if args.output:
            output_file = Path(args.output)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(markdown)
            print(f"✓ Table saved to: {output_file}")
        else:
            # Print to stdout
            print(markdown)

    # Directory conversion
    elif args.input_dir:
        if not args.output_dir:
            print("Error: --output-dir required when using --input-dir")
            return 1

        convert_directory(
            args.input_dir,
            args.output_dir,
            max_rows=args.max_rows
        )


if __name__ == '__main__':
    exit(main() or 0)
