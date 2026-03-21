#!/usr/bin/env python3
"""
Convert Paperpile citation links to BibTeX keys in manuscript.

Transforms:
    [(Author et al. YEAR)](https://paperpile.com/c/PROJECT/CODE)
To:
    [authorYEAR]

Usage:
    python scripts/rrwrite-convert-paperpile-citations.py \
        --manuscript manuscript/kbaseeco_v2/manuscript_v2.md \
        --mapping manuscript/kbaseeco_v2/paperpile_mapping.json \
        --output manuscript/kbaseeco_v2/manuscript_v2_bibtex.md
"""

import re
import json
import argparse
from pathlib import Path
from typing import Dict


def convert_paperpile_to_bibtex(
    text: str,
    mapping: Dict[str, str]
) -> tuple[str, int, int]:
    """
    Convert Paperpile citation links to BibTeX keys.

    Args:
        text: Text with Paperpile citations
        mapping: Dictionary mapping Paperpile codes to BibTeX keys

    Returns:
        Tuple of (converted_text, converted_count, skipped_count)
    """
    # Pattern: [(display text)](https://paperpile.com/c/PROJECT/CODE)
    pattern = r'\[(.*?)\]\(https://paperpile\.com/c/[^/]+/([^\)]+)\)'

    converted_count = 0
    skipped_count = 0

    def replace_citation(match):
        nonlocal converted_count, skipped_count

        display_text = match.group(1)
        paperpile_code = match.group(2)

        # Look up BibTeX key
        if paperpile_code in mapping:
            bibtex_key = mapping[paperpile_code]
            converted_count += 1
            return f'[{bibtex_key}]'
        else:
            # Keep original if not in mapping
            skipped_count += 1
            return match.group(0)

    converted_text = re.sub(pattern, replace_citation, text)

    return converted_text, converted_count, skipped_count


def main():
    parser = argparse.ArgumentParser(
        description='Convert Paperpile citations to BibTeX format'
    )
    parser.add_argument(
        '--manuscript',
        type=Path,
        required=True,
        help='Path to manuscript file with Paperpile citations'
    )
    parser.add_argument(
        '--mapping',
        type=Path,
        required=True,
        help='Path to paperpile_mapping.json'
    )
    parser.add_argument(
        '--output',
        type=Path,
        required=True,
        help='Output file path for converted manuscript'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show conversion preview without writing output'
    )

    args = parser.parse_args()

    # Validate inputs
    if not args.manuscript.exists():
        print(f"Error: Manuscript not found: {args.manuscript}")
        return 1

    if not args.mapping.exists():
        print(f"Error: Mapping file not found: {args.mapping}")
        return 1

    # Load mapping
    try:
        with open(args.mapping, 'r') as f:
            mapping = json.load(f)
    except Exception as e:
        print(f"Error loading mapping: {e}")
        return 1

    # Read manuscript
    try:
        with open(args.manuscript, 'r', encoding='utf-8') as f:
            text = f.read()
    except Exception as e:
        print(f"Error reading manuscript: {e}")
        return 1

    # Convert citations
    converted_text, converted_count, skipped_count = convert_paperpile_to_bibtex(
        text,
        mapping
    )

    # Summary
    print(f"Conversion summary:")
    print(f"  ✓ Converted: {converted_count} citations")
    if skipped_count > 0:
        print(f"  ⚠️  Skipped: {skipped_count} citations (not in mapping)")

    if args.dry_run:
        print("\n📋 Preview (first 1000 characters):")
        print(converted_text[:1000])
        print("\nDry run mode - no files written")
        return 0

    # Write output
    try:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(converted_text)
        print(f"\n✓ Converted manuscript written to: {args.output}")
    except Exception as e:
        print(f"Error writing output: {e}")
        return 1

    return 0


if __name__ == '__main__':
    exit(main())
