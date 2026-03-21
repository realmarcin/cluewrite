#!/usr/bin/env python3
"""
Extract Paperpile citations from manuscript and parse metadata.

Parses Paperpile citation links in the format:
    [(Author et al. YEAR)](https://paperpile.com/c/aBwggu/CODE)

Outputs JSON with parsed metadata for subsequent BibTeX lookup.
"""

import re
import json
import argparse
from pathlib import Path
from typing import List, Dict, Optional
from collections import defaultdict


def extract_paperpile_citations(text: str) -> List[Dict[str, str]]:
    """
    Extract all Paperpile citations from text.

    Args:
        text: Manuscript text

    Returns:
        List of dictionaries with citation metadata
    """
    # Pattern: [(display text)](https://paperpile.com/c/PROJECT/CODE)
    pattern = r'\[(.*?)\]\(https://paperpile\.com/c/([^/]+)/([^\)]+)\)'

    citations = []
    seen_codes = set()

    for match in re.finditer(pattern, text):
        display_text = match.group(1)
        project_code = match.group(2)
        paperpile_code = match.group(3)

        # Parse display text to extract author and year
        author, year = parse_display_text(display_text)

        # Create unique key for deduplication
        citation_key = f"{project_code}/{paperpile_code}"

        if citation_key not in seen_codes:
            citations.append({
                'display_text': display_text,
                'project_code': project_code,
                'paperpile_code': paperpile_code,
                'author': author,
                'year': year,
                'full_url': match.group(0)
            })
            seen_codes.add(citation_key)

    return citations


def parse_display_text(display_text: str) -> tuple[Optional[str], Optional[str]]:
    """
    Parse display text to extract author and year.

    Examples:
        "Park et al. 2023" -> ("Park", "2023")
        "(Park et al. 2023)" -> ("Park", "2023")
        "Zhang et al. 2024" -> ("Zhang", "2024")
        "Zhao et al. 2022" -> ("Zhao", "2022")

    Args:
        display_text: Citation display text

    Returns:
        Tuple of (author, year)
    """
    # Strip leading/trailing parentheses and whitespace
    display_text = display_text.strip().strip('()')

    # Pattern: Author et al. YEAR or Author YEAR
    year_pattern = r'\b(19\d{2}|20\d{2})\b'
    year_match = re.search(year_pattern, display_text)

    if year_match:
        year = year_match.group(1)

        # Extract author (first word before 'et al.' or year)
        author_pattern = r'^([A-Z][a-z]+)'
        author_match = re.search(author_pattern, display_text)

        if author_match:
            author = author_match.group(1)
            return author, year

    # If parsing fails, return None
    return None, None


def analyze_multi_citations(citations: List[Dict]) -> Dict:
    """
    Analyze citations with multiple references (codes separated by '+').

    Args:
        citations: List of citation dictionaries

    Returns:
        Statistics about multi-citations
    """
    multi_cites = []

    for citation in citations:
        code = citation['paperpile_code']
        if '+' in code:
            parts = code.split('+')
            multi_cites.append({
                'display_text': citation['display_text'],
                'codes': parts,
                'count': len(parts)
            })

    return {
        'total_multi_citations': len(multi_cites),
        'examples': multi_cites[:5] if multi_cites else []
    }


def generate_statistics(citations: List[Dict]) -> Dict:
    """
    Generate statistics about extracted citations.

    Args:
        citations: List of citation dictionaries

    Returns:
        Statistics dictionary
    """
    # Count by year
    year_counts = defaultdict(int)
    for citation in citations:
        if citation['year']:
            year_counts[citation['year']] += 1

    # Count by author
    author_counts = defaultdict(int)
    for citation in citations:
        if citation['author']:
            author_counts[citation['author']] += 1

    # Multi-citation analysis
    multi_stats = analyze_multi_citations(citations)

    # Parse failures
    parse_failures = [
        c for c in citations
        if c['author'] is None or c['year'] is None
    ]

    return {
        'total_citations': len(citations),
        'unique_authors': len(author_counts),
        'year_range': {
            'earliest': min(year_counts.keys()) if year_counts else None,
            'latest': max(year_counts.keys()) if year_counts else None
        },
        'top_years': dict(sorted(
            year_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]),
        'top_authors': dict(sorted(
            author_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]),
        'multi_citations': multi_stats,
        'parse_failures': len(parse_failures),
        'parse_failure_examples': [
            c['display_text'] for c in parse_failures[:5]
        ]
    }


def main():
    parser = argparse.ArgumentParser(
        description='Extract Paperpile citations from manuscript'
    )
    parser.add_argument(
        '--manuscript',
        type=Path,
        required=True,
        help='Path to manuscript file (.md)'
    )
    parser.add_argument(
        '--output',
        type=Path,
        required=True,
        help='Output JSON file for parsed citations'
    )
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Print statistics to stdout'
    )

    args = parser.parse_args()

    # Validate inputs
    if not args.manuscript.exists():
        print(f"Error: Manuscript not found: {args.manuscript}")
        return 1

    # Read manuscript
    with open(args.manuscript, 'r', encoding='utf-8') as f:
        text = f.read()

    # Extract citations
    citations = extract_paperpile_citations(text)

    if not citations:
        print("Warning: No Paperpile citations found in manuscript")
        return 1

    # Generate statistics
    stats = generate_statistics(citations)

    # Write output
    from datetime import datetime
    output_data = {
        'manuscript': str(args.manuscript),
        'extracted_at': datetime.now().isoformat(),
        'statistics': stats,
        'citations': citations
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2)

    # Print summary
    print(f"✓ Extracted {len(citations)} unique Paperpile citations")
    print(f"✓ Output written to: {args.output}")

    if args.stats:
        print("\n=== Citation Statistics ===")
        print(f"Total citations: {stats['total_citations']}")
        print(f"Unique authors: {stats['unique_authors']}")
        print(f"Year range: {stats['year_range']['earliest']} - {stats['year_range']['latest']}")
        print(f"\nTop 5 years:")
        for year, count in stats['top_years'].items():
            print(f"  {year}: {count}")
        print(f"\nTop 5 authors:")
        for author, count in stats['top_authors'].items():
            print(f"  {author}: {count}")

        if stats['multi_citations']['total_multi_citations'] > 0:
            print(f"\nMulti-citations: {stats['multi_citations']['total_multi_citations']}")
            print("Examples:")
            for example in stats['multi_citations']['examples']:
                print(f"  {example['display_text']} ({example['count']} refs)")

        if stats['parse_failures'] > 0:
            print(f"\n⚠️  Parse failures: {stats['parse_failures']}")
            print("Examples:")
            for failure in stats['parse_failure_examples']:
                print(f"  {failure}")

    return 0


if __name__ == '__main__':
    exit(main())
