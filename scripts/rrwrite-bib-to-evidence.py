#!/usr/bin/env python3
"""
Generate literature_evidence.csv from BibTeX bibliography.

Parses BibTeX entries and extracts metadata into CSV format compatible
with RRWrite's citation validation system.

CSV columns:
- citation_key: BibTeX key (e.g., park2023)
- doi: DOI from BibTeX entry
- title: Article title
- authors: Full author list
- year: Publication year
- journal: Journal name
- abstract: Abstract text (optionally fetched via DOI API)
- citation_type: Inferred type (research_article, method, review, etc.)
"""

import re
import csv
import time
import argparse
import requests
from pathlib import Path
from typing import List, Dict, Optional
import bibtexparser
from bibtexparser.bparser import BibTexParser


def parse_bib_file(bib_path: Path) -> List[Dict]:
    """
    Parse BibTeX file and extract entries.

    Args:
        bib_path: Path to .bib file

    Returns:
        List of entry dictionaries
    """
    with open(bib_path, 'r', encoding='utf-8') as f:
        parser = BibTexParser(common_strings=True)
        bib_database = bibtexparser.load(f, parser=parser)

    return bib_database.entries


def extract_metadata(entry: Dict) -> Dict[str, str]:
    """
    Extract metadata from BibTeX entry.

    Args:
        entry: BibTeX entry dictionary

    Returns:
        Metadata dictionary
    """
    # Get citation key (ID field)
    citation_key = entry.get('ID', '')

    # Extract fields
    doi = entry.get('doi', '')
    title = entry.get('title', '')
    journal = entry.get('journal', '')
    year = entry.get('year', '')

    # Parse authors
    author_str = entry.get('author', '')
    authors = parse_authors(author_str)

    # Infer citation type
    citation_type = infer_citation_type(entry)

    return {
        'citation_key': citation_key,
        'doi': doi,
        'title': clean_text(title),
        'authors': authors,
        'year': year,
        'journal': clean_text(journal),
        'abstract': '',  # Will be fetched if --fetch-abstracts enabled
        'citation_type': citation_type
    }


def parse_authors(author_str: str) -> str:
    """
    Parse author string from BibTeX format to readable format.

    BibTeX format: "Lastname, Firstname and Lastname, Firstname"
    Output format: "Lastname F., Lastname F., ..."

    Args:
        author_str: Author string from BibTeX

    Returns:
        Formatted author string
    """
    if not author_str:
        return ''

    # Split on 'and'
    authors = [a.strip() for a in author_str.split(' and ')]

    formatted = []
    for author in authors[:10]:  # Limit to first 10 authors
        # Handle "Lastname, Firstname" format
        if ',' in author:
            parts = author.split(',', 1)
            lastname = parts[0].strip()
            firstname = parts[1].strip() if len(parts) > 1 else ''

            # Get first initial
            initial = firstname[0] + '.' if firstname else ''
            formatted.append(f"{lastname} {initial}".strip())
        else:
            # Handle "Firstname Lastname" format
            formatted.append(author)

    # Add "et al." if more than 10 authors
    if len(authors) > 10:
        formatted.append('et al.')

    return ', '.join(formatted)


def clean_text(text: str) -> str:
    """
    Clean text by removing LaTeX commands and extra whitespace.

    Args:
        text: Raw text

    Returns:
        Cleaned text
    """
    # Remove LaTeX braces
    text = re.sub(r'[{}]', '', text)

    # Remove LaTeX commands
    text = re.sub(r'\\[a-zA-Z]+', '', text)

    # Normalize whitespace
    text = ' '.join(text.split())

    return text


def infer_citation_type(entry: Dict) -> str:
    """
    Infer citation type from BibTeX entry.

    Types:
    - research_article: Original research
    - review: Review article
    - method: Method/tool paper
    - dataset: Dataset description
    - book: Book or book chapter
    - preprint: Preprint (arXiv, bioRxiv)
    - conference: Conference proceeding

    Args:
        entry: BibTeX entry

    Returns:
        Citation type string
    """
    entry_type = entry.get('ENTRYTYPE', '').lower()
    title = entry.get('title', '').lower()
    journal = entry.get('journal', '').lower()

    # Preprint detection
    if 'arxiv' in journal or 'biorxiv' in journal or 'medrxiv' in journal:
        return 'preprint'

    # Conference detection
    if entry_type in ['inproceedings', 'conference']:
        return 'conference'

    # Book detection
    if entry_type in ['book', 'incollection', 'inbook']:
        return 'book'

    # Review detection (title-based)
    review_keywords = ['review', 'survey', 'meta-analysis', 'systematic review']
    if any(keyword in title for keyword in review_keywords):
        return 'review'

    # Method/tool detection (title-based)
    method_keywords = ['method', 'tool', 'software', 'algorithm', 'approach', 'pipeline']
    if any(keyword in title for keyword in method_keywords):
        return 'method'

    # Dataset detection (title-based)
    dataset_keywords = ['database', 'dataset', 'collection', 'resource', 'repository']
    if any(keyword in title for keyword in dataset_keywords):
        return 'dataset'

    # Default: research article
    return 'research_article'


def fetch_abstract_from_doi(doi: str) -> Optional[str]:
    """
    Fetch abstract via DOI using CrossRef API.

    Args:
        doi: DOI string

    Returns:
        Abstract text or None if not found
    """
    try:
        url = f"https://api.crossref.org/works/{doi}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data = response.json()
        abstract = data.get('message', {}).get('abstract', '')

        # Clean JATS XML tags if present
        abstract = re.sub(r'<[^>]+>', '', abstract)

        return clean_text(abstract) if abstract else None

    except Exception as e:
        print(f"Warning: Failed to fetch abstract for DOI {doi}: {e}")
        return None


def write_evidence_csv(
    metadata_list: List[Dict],
    output_path: Path,
    fetch_abstracts: bool = False
) -> None:
    """
    Write metadata to CSV file.

    Args:
        metadata_list: List of metadata dictionaries
        output_path: Output CSV path
        fetch_abstracts: Whether to fetch abstracts via DOI API
    """
    # Define CSV columns
    fieldnames = [
        'citation_key',
        'doi',
        'title',
        'authors',
        'year',
        'journal',
        'abstract',
        'citation_type'
    ]

    # Fetch abstracts if enabled
    if fetch_abstracts:
        print("\nFetching abstracts via CrossRef API...")
        for i, metadata in enumerate(metadata_list, 1):
            doi = metadata.get('doi', '')
            if doi:
                print(f"  {i}/{len(metadata_list)}: {metadata['citation_key']}...", end=' ')
                abstract = fetch_abstract_from_doi(doi)
                if abstract:
                    metadata['abstract'] = abstract
                    print("✓")
                else:
                    print("✗")
                time.sleep(0.1)  # Rate limiting

    # Write CSV
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(metadata_list)


def generate_statistics(metadata_list: List[Dict]) -> Dict:
    """
    Generate statistics about extracted metadata.

    Args:
        metadata_list: List of metadata dictionaries

    Returns:
        Statistics dictionary
    """
    from collections import Counter

    # Count by type
    type_counts = Counter(m['citation_type'] for m in metadata_list)

    # Count by year
    year_counts = Counter(m['year'] for m in metadata_list if m['year'])

    # Count with DOI
    with_doi = sum(1 for m in metadata_list if m['doi'])

    # Count with abstract
    with_abstract = sum(1 for m in metadata_list if m['abstract'])

    return {
        'total_entries': len(metadata_list),
        'with_doi': with_doi,
        'with_abstract': with_abstract,
        'type_distribution': dict(type_counts.most_common()),
        'year_range': {
            'earliest': min(m['year'] for m in metadata_list if m['year']),
            'latest': max(m['year'] for m in metadata_list if m['year'])
        } if any(m['year'] for m in metadata_list) else None
    }


def main():
    parser = argparse.ArgumentParser(
        description='Generate literature_evidence.csv from BibTeX bibliography'
    )
    parser.add_argument(
        '--bib',
        type=Path,
        required=True,
        help='Path to BibTeX file (.bib)'
    )
    parser.add_argument(
        '--output',
        type=Path,
        required=True,
        help='Output CSV file path'
    )
    parser.add_argument(
        '--fetch-abstracts',
        action='store_true',
        help='Fetch abstracts via CrossRef API (slower, recommended for complete evidence)'
    )
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Print statistics to stdout'
    )

    args = parser.parse_args()

    # Validate inputs
    if not args.bib.exists():
        print(f"Error: BibTeX file not found: {args.bib}")
        return 1

    # Check for bibtexparser
    try:
        import bibtexparser
    except ImportError:
        print("Error: bibtexparser not installed")
        print("Install with: pip install bibtexparser")
        return 1

    # Parse BibTeX file
    print(f"Parsing BibTeX file: {args.bib}")
    entries = parse_bib_file(args.bib)

    if not entries:
        print("Error: No entries found in BibTeX file")
        return 1

    print(f"Found {len(entries)} BibTeX entries")

    # Extract metadata
    metadata_list = []
    for entry in entries:
        metadata = extract_metadata(entry)
        metadata_list.append(metadata)

    # Write CSV
    args.output.parent.mkdir(parents=True, exist_ok=True)
    write_evidence_csv(metadata_list, args.output, fetch_abstracts=args.fetch_abstracts)

    print(f"\n✓ Evidence CSV written to: {args.output}")
    print(f"  {len(metadata_list)} entries")

    # Print statistics
    if args.stats:
        stats = generate_statistics(metadata_list)

        print("\n=== Statistics ===")
        print(f"Total entries: {stats['total_entries']}")
        print(f"Entries with DOI: {stats['with_doi']}")
        print(f"Entries with abstract: {stats['with_abstract']}")

        if stats['year_range']:
            print(f"\nYear range: {stats['year_range']['earliest']} - {stats['year_range']['latest']}")

        print("\nCitation type distribution:")
        for cite_type, count in stats['type_distribution'].items():
            print(f"  {cite_type}: {count}")

    return 0


if __name__ == '__main__':
    exit(main())
