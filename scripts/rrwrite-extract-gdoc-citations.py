#!/usr/bin/env python3
"""
Extract citations from Google Doc DOCX export.

Supports multiple citation formats:
- Paperpile hyperlinks: [(Author2024)](https://paperpile.com/c/PROJECT/CODE)
- Bracketed citations: [Author2024]
- Numbered citations: [1], [2], etc.

Outputs structured JSON with citation metadata for gap analysis.

Usage:
    python scripts/rrwrite-extract-gdoc-citations.py \
        --docx manuscript.docx \
        --output extracted_citations.json \
        --stats
"""

import argparse
import json
import re
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Set, Tuple
from collections import defaultdict

try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    print("Warning: python-docx not installed. Install with: pip install python-docx", file=sys.stderr)


def extract_paperpile_citations(text: str) -> List[Dict]:
    """
    Extract Paperpile citation hyperlinks.

    Pattern: [(display text)](https://paperpile.com/c/PROJECT/CODE)
    """
    pattern = r'\[(.*?)\]\(https://paperpile\.com/c/([^/]+)/([^\)]+)\)'
    citations = []
    seen = set()

    for match in re.finditer(pattern, text):
        display_text = match.group(1)
        project_code = match.group(2)
        paperpile_code = match.group(3)

        # Parse author and year from display text
        author, year = parse_author_year(display_text)

        citation_key = f"{project_code}/{paperpile_code}"

        if citation_key not in seen:
            citations.append({
                'type': 'paperpile',
                'display_text': display_text,
                'project_code': project_code,
                'paperpile_code': paperpile_code,
                'author': author,
                'year': year,
                'url': f"https://paperpile.com/c/{project_code}/{paperpile_code}"
            })
            seen.add(citation_key)

    return citations


def extract_bracketed_citations(text: str) -> List[Dict]:
    """
    Extract bracketed citations like [Author2024] or [Author2024a].

    Excludes:
    - Numbered citations [1], [2]
    - Paperpile hyperlinks (handled separately)
    - Markdown links [text](url)
    """
    # Match [AuthorYEAR] pattern (not just numbers)
    pattern = r'\[([A-Z][a-zA-Z]+\d{4}[a-z]?)\]'
    citations = []
    seen = set()

    for match in re.finditer(pattern, text):
        citation_key = match.group(1)

        if citation_key not in seen:
            # Parse author and year
            year_match = re.search(r'(\d{4})', citation_key)
            author = citation_key[:year_match.start()] if year_match else citation_key
            year = year_match.group(1) if year_match else None

            citations.append({
                'type': 'bracketed',
                'citation_key': citation_key,
                'author': author,
                'year': year
            })
            seen.add(citation_key)

    return citations


def extract_numbered_citations(text: str) -> List[Dict]:
    """
    Extract numbered citations like [1], [2], [3-5].

    Only extracts if pattern appears consistently (suggests numbered style).
    """
    # Match [N] or [N-M] patterns
    pattern = r'\[(\d+(?:-\d+)?)\]'
    citations = []
    seen = set()

    for match in re.finditer(pattern, text):
        number = match.group(1)

        if number not in seen:
            citations.append({
                'type': 'numbered',
                'number': number
            })
            seen.add(number)

    # Only return if we found at least 3 numbered citations (suggests numbered style)
    return citations if len(citations) >= 3 else []


def parse_author_year(text: str) -> Tuple[str, str]:
    """
    Parse author and year from citation display text.

    Examples:
        "Park et al. 2023" -> ("Park", "2023")
        "(Park et al. 2023)" -> ("Park", "2023")
        "Zhang et al. 2024" -> ("Zhang", "2024")
    """
    # Strip parentheses
    text = text.strip().strip('()')

    # Extract year (4-digit number)
    year_match = re.search(r'\b(19\d{2}|20\d{2})\b', text)
    year = year_match.group(1) if year_match else None

    # Extract author (first capitalized word)
    author_match = re.search(r'^([A-Z][a-z]+)', text)
    author = author_match.group(1) if author_match else None

    return author, year


def read_docx_text(docx_path: Path) -> str:
    """Extract all text from DOCX file preserving hyperlinks"""
    if not DOCX_AVAILABLE:
        raise ImportError("python-docx required for DOCX parsing")

    doc = Document(docx_path)

    # Extract text from all paragraphs
    paragraphs = []
    for para in doc.paragraphs:
        # Get full text with hyperlinks preserved (via XML)
        para_text = para.text
        paragraphs.append(para_text)

    # Also check hyperlinks in XML
    hyperlinks = []
    for rel in doc.part.rels.values():
        if "hyperlink" in rel.reltype:
            target_url = rel.target_ref
            if "paperpile.com" in target_url:
                hyperlinks.append(target_url)

    full_text = "\n".join(paragraphs)

    return full_text


def deduplicate_citations(citations: List[Dict]) -> List[Dict]:
    """Remove duplicate citations across different extraction methods"""
    seen_keys = set()
    unique = []

    for cit in citations:
        # Generate unique key based on citation type
        if cit['type'] == 'paperpile':
            key = f"paperpile:{cit['paperpile_code']}"
        elif cit['type'] == 'bracketed':
            key = f"bracketed:{cit['citation_key']}"
        elif cit['type'] == 'numbered':
            key = f"numbered:{cit['number']}"
        else:
            key = str(cit)

        if key not in seen_keys:
            unique.append(cit)
            seen_keys.add(key)

    return unique


def generate_statistics(citations: List[Dict]) -> Dict:
    """Generate statistics about extracted citations"""

    # Count by type
    by_type = defaultdict(int)
    for cit in citations:
        by_type[cit['type']] += 1

    # Count by year (if available)
    by_year = defaultdict(int)
    for cit in citations:
        year = cit.get('year')
        if year:
            by_year[year] += 1

    # Count by author (if available)
    by_author = defaultdict(int)
    for cit in citations:
        author = cit.get('author')
        if author:
            by_author[author] += 1

    return {
        'total_citations': len(citations),
        'by_type': dict(by_type),
        'by_year': dict(sorted(by_year.items(), reverse=True)),
        'by_author': dict(sorted(by_author.items(), key=lambda x: x[1], reverse=True)[:10]),
        'year_range': {
            'earliest': min(by_year.keys()) if by_year else None,
            'latest': max(by_year.keys()) if by_year else None
        }
    }


def main():
    parser = argparse.ArgumentParser(
        description='Extract citations from Google Doc DOCX export',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        '--docx',
        type=Path,
        required=True,
        help='Input DOCX file'
    )
    parser.add_argument(
        '--output',
        type=Path,
        required=True,
        help='Output JSON file'
    )
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Print statistics to stdout'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Verbose output'
    )

    args = parser.parse_args()

    # Validate inputs
    if not args.docx.exists():
        print(f"❌ Error: DOCX file not found: {args.docx}", file=sys.stderr)
        return 1

    if not DOCX_AVAILABLE:
        print(f"❌ Error: python-docx not installed", file=sys.stderr)
        print("Install with: pip install python-docx", file=sys.stderr)
        return 1

    try:
        # Read DOCX text
        if args.verbose:
            print(f"📖 Reading DOCX file: {args.docx}")

        text = read_docx_text(args.docx)

        if args.verbose:
            print(f"  Length: {len(text)} characters")

        # Extract citations (all formats)
        all_citations = []

        paperpile_cites = extract_paperpile_citations(text)
        all_citations.extend(paperpile_cites)
        if args.verbose:
            print(f"  Paperpile citations: {len(paperpile_cites)}")

        bracketed_cites = extract_bracketed_citations(text)
        all_citations.extend(bracketed_cites)
        if args.verbose:
            print(f"  Bracketed citations: {len(bracketed_cites)}")

        numbered_cites = extract_numbered_citations(text)
        all_citations.extend(numbered_cites)
        if args.verbose:
            print(f"  Numbered citations: {len(numbered_cites)}")

        # Deduplicate
        citations = deduplicate_citations(all_citations)

        if not citations:
            print("⚠️  Warning: No citations found in document", file=sys.stderr)

        # Generate statistics
        stats = generate_statistics(citations)

        # Build output
        output_data = {
            'docx_file': str(args.docx),
            'extracted_at': datetime.now().isoformat(),
            'statistics': stats,
            'citations': citations
        }

        # Write output
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2)

        print(f"✓ Extracted {len(citations)} unique citations")
        print(f"✓ Output written to: {args.output}")

        # Print statistics
        if args.stats:
            print("\n=== Citation Statistics ===")
            print(f"Total citations: {stats['total_citations']}")
            print(f"\nBy type:")
            for cit_type, count in stats['by_type'].items():
                print(f"  {cit_type}: {count}")

            if stats['year_range']['earliest']:
                print(f"\nYear range: {stats['year_range']['earliest']} - {stats['year_range']['latest']}")

            if stats['by_year']:
                print(f"\nTop years:")
                for year, count in list(stats['by_year'].items())[:5]:
                    print(f"  {year}: {count}")

            if stats['by_author']:
                print(f"\nTop authors:")
                for author, count in list(stats['by_author'].items())[:5]:
                    print(f"  {author}: {count}")

        return 0

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
