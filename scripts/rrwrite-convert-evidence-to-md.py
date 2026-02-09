#!/usr/bin/env python3
"""
Convert literature_evidence.csv to literature_evidence.md format.

Reads CSV format evidence and converts to markdown format per
EVIDENCE_TRACKING.md protocol.
"""

import argparse
import csv
from pathlib import Path
from datetime import datetime


def read_citations_bib(bib_file: Path) -> dict:
    """
    Parse BibTeX file to extract citation metadata.

    Returns:
        Dictionary mapping citation_key to metadata dict
    """
    citations = {}

    if not bib_file.exists():
        return citations

    content = bib_file.read_text()

    # Simple BibTeX parser (handles basic entries)
    import re

    # Match @type{key, ... }
    entries = re.finditer(
        r'@(\w+)\{([^,]+),\s*\n(.*?)\n\}',
        content,
        re.DOTALL
    )

    for match in entries:
        entry_type, key, fields_text = match.groups()

        # Parse fields
        fields = {}
        for field_match in re.finditer(
            r'(\w+)\s*=\s*\{([^}]+)\}',
            fields_text
        ):
            field_name, field_value = field_match.groups()
            fields[field_name.lower()] = field_value.strip()

        citations[key] = {
            'type': entry_type,
            'title': fields.get('title', 'Unknown Title'),
            'author': fields.get('author', 'Unknown Authors'),
            'venue': fields.get('journal') or fields.get('booktitle', 'Unknown Venue'),
            'year': fields.get('year', 'Unknown Year'),
            'doi': fields.get('doi', ''),
            'url': fields.get('url', '')
        }

    return citations


def convert_csv_to_markdown(
    csv_file: Path,
    bib_file: Path,
    output_file: Path
):
    """
    Convert CSV evidence to markdown format.

    Args:
        csv_file: Path to literature_evidence.csv
        bib_file: Path to literature_citations.bib
        output_file: Path to output literature_evidence.md
    """
    # Read BibTeX citations for metadata
    citations = read_citations_bib(bib_file)

    # Read CSV
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        evidence_entries = list(reader)

    # Generate markdown
    md = f"""# Literature Evidence

**Generated**: {datetime.now().strftime('%Y-%m-%d')}
**Purpose**: Verbatim quotes supporting cited claims

---

"""

    for entry in evidence_entries:
        citation_key = entry['citation_key']
        doi = entry['doi']
        evidence = entry['evidence']

        # Get metadata from BibTeX if available
        cite_meta = citations.get(citation_key, {})

        title = cite_meta.get('title', 'Unknown Title')
        authors = cite_meta.get('author', 'Unknown Authors')
        venue = cite_meta.get('venue', 'Unknown Venue')
        year = cite_meta.get('year', '')
        url = doi if doi.startswith('http') else f"https://doi.org/{doi}" if doi and not doi.startswith('arXiv') else doi

        # Format authors (simplify if needed)
        if ' and ' in authors:
            author_list = authors.split(' and ')
            if len(author_list) > 3:
                authors = f"{author_list[0]} et al."

        md += f"""## {citation_key}: {title}

**Authors**: {authors}
**Venue**: {venue}, {year}
**DOI**: {doi if doi else 'N/A'}
**URL**: {url if url else 'N/A'}

**Evidence Quote**:
> "{evidence}"

**Key Findings**:
- (Extract from full paper if needed)

---

"""

    # Write output
    output_file.write_text(md)
    print(f"✓ Converted {len(evidence_entries)} evidence entries to {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description='Convert literature_evidence.csv to markdown format'
    )
    parser.add_argument(
        '--csv',
        type=Path,
        required=True,
        help='Input CSV file (literature_evidence.csv)'
    )
    parser.add_argument(
        '--bib',
        type=Path,
        required=True,
        help='BibTeX file for metadata (literature_citations.bib)'
    )
    parser.add_argument(
        '--output',
        type=Path,
        required=True,
        help='Output markdown file (literature_evidence.md)'
    )

    args = parser.parse_args()

    if not args.csv.exists():
        print(f"Error: CSV file not found: {args.csv}")
        return 1

    if not args.bib.exists():
        print(f"Warning: BibTeX file not found: {args.bib}")
        print("Proceeding without citation metadata...")

    convert_csv_to_markdown(args.csv, args.bib, args.output)

    return 0


if __name__ == '__main__':
    exit(main())
