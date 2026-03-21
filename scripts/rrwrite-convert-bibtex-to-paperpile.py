#!/usr/bin/env python3
"""
Convert BibTeX keys to Paperpile citation links in manuscript.

Transforms:
    [authorYEAR]
To:
    [(Author et al. YEAR)](https://paperpile.com/c/PROJECT/CODE)

Usage:
    python scripts/rrwrite-convert-bibtex-to-paperpile.py \
        --manuscript manuscript/kbaseeco_v2/manuscript_v2_bibtex.md \
        --mapping manuscript/kbaseeco_v2/paperpile_mapping.json \
        --output manuscript/kbaseeco_v2/manuscript_v2_paperpile.md \
        --project-code aBwggu
"""

import re
import json
import argparse
from pathlib import Path
from typing import Dict


def format_author_year(bibtex_key: str) -> str:
    """
    Format BibTeX key as display text.

    Examples:
        park2023 → (Park et al. 2023)
        zhang2024 → (Zhang et al. 2024)

    Args:
        bibtex_key: BibTeX citation key

    Returns:
        Formatted display text
    """
    # Extract author and year from key
    # Pattern: lowercase_author + 4-digit year
    match = re.match(r'([a-z]+)(\d{4})', bibtex_key)

    if match:
        author = match.group(1).capitalize()
        year = match.group(2)
        return f"({author} et al. {year})"
    else:
        # Fallback: use key as-is
        return f"({bibtex_key})"


def convert_bibtex_to_paperpile(
    text: str,
    mapping: Dict[str, str],
    project_code: str = "aBwggu"
) -> tuple[str, int, int]:
    """
    Convert BibTeX keys to Paperpile citation links.

    Args:
        text: Text with BibTeX citations
        mapping: Dictionary mapping Paperpile codes to BibTeX keys
        project_code: Paperpile project code (default: aBwggu)

    Returns:
        Tuple of (converted_text, converted_count, skipped_count)
    """
    # Create reverse mapping: BibTeX key → Paperpile code
    reverse_mapping = {v: k for k, v in mapping.items()}

    # Pattern: [authorYEAR] (BibTeX citation)
    pattern = r'\[([a-zA-Z]+\d{4}[a-z]?)\]'

    converted_count = 0
    skipped_count = 0

    def replace_citation(match):
        nonlocal converted_count, skipped_count

        bibtex_key = match.group(1)

        # Look up Paperpile code
        if bibtex_key in reverse_mapping:
            paperpile_code = reverse_mapping[bibtex_key]
            display_text = format_author_year(bibtex_key)
            converted_count += 1
            return f'[{display_text}](https://paperpile.com/c/{project_code}/{paperpile_code})'
        else:
            # Keep original if not in mapping
            skipped_count += 1
            return match.group(0)

    converted_text = re.sub(pattern, replace_citation, text)

    return converted_text, converted_count, skipped_count


def main():
    parser = argparse.ArgumentParser(
        description='Convert BibTeX citations to Paperpile format'
    )
    parser.add_argument(
        '--manuscript',
        type=Path,
        required=True,
        help='Path to manuscript file with BibTeX citations'
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
        '--project-code',
        type=str,
        default='aBwggu',
        help='Paperpile project code (default: aBwggu)'
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
    converted_text, converted_count, skipped_count = convert_bibtex_to_paperpile(
        text,
        mapping,
        project_code=args.project_code
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
