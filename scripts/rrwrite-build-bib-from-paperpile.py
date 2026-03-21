#!/usr/bin/env python3
"""
Build BibTeX bibliography from Paperpile citations using CrossRef API.

Reads parsed Paperpile citations, queries CrossRef API with author+year,
fetches BibTeX entries via DOI content negotiation, and generates:
- literature_citations.bib (BibTeX bibliography)
- paperpile_mapping.json (Paperpile code → BibTeX key mapping)
- citation_extraction_report.md (quality report)
- citations_failed.json (failed lookups for manual review)
"""

import re
import json
import time
import argparse
import requests
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from collections import defaultdict
from difflib import SequenceMatcher


class CrossRefAPI:
    """CrossRef API client for DOI and BibTeX lookup."""

    BASE_URL = "https://api.crossref.org/works"
    RATE_LIMIT_DELAY = 0.1  # 10 requests/second (polite rate limit)

    def __init__(self, email: Optional[str] = None):
        """
        Initialize CrossRef API client.

        Args:
            email: Contact email for polite API usage
        """
        self.email = email
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': f'RRWrite/1.0 (mailto:{email})' if email else 'RRWrite/1.0'
        })

    def search_by_author_year(
        self,
        author: str,
        year: str,
        title_hint: Optional[str] = None,
        max_results: int = 5
    ) -> List[Dict]:
        """
        Search CrossRef for papers by author and year.

        Args:
            author: First author surname
            year: Publication year
            title_hint: Optional title keywords for better matching
            max_results: Maximum results to return

        Returns:
            List of work metadata dictionaries
        """
        # Build query
        query_parts = [f'{author} {year}']
        if title_hint:
            query_parts.append(title_hint)

        params = {
            'query.author': author,
            'query.bibliographic': year,
            'rows': max_results,
            'sort': 'relevance'
        }

        try:
            time.sleep(self.RATE_LIMIT_DELAY)
            response = self.session.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            items = data.get('message', {}).get('items', [])

            return items

        except Exception as e:
            print(f"CrossRef search failed for {author} {year}: {e}")
            return []

    def fetch_bibtex(self, doi: str) -> Optional[str]:
        """
        Fetch BibTeX entry for a DOI using content negotiation.

        Args:
            doi: DOI string

        Returns:
            BibTeX entry string or None if failed
        """
        url = f"https://doi.org/{doi}"
        headers = {
            'Accept': 'application/x-bibtex'
        }

        try:
            time.sleep(self.RATE_LIMIT_DELAY)
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            return response.text

        except Exception as e:
            print(f"BibTeX fetch failed for DOI {doi}: {e}")
            return None


def rank_results_by_relevance(
    results: List[Dict],
    target_author: str,
    target_year: str
) -> List[Tuple[Dict, float]]:
    """
    Rank CrossRef results by relevance to target citation.

    Scoring criteria:
    - First author surname match: +0.5
    - Year exact match: +0.3
    - Year within ±1: +0.2
    - Title similarity: +0.2 (if title available)

    Args:
        results: CrossRef search results
        target_author: Target first author surname
        target_year: Target publication year

    Returns:
        List of (result, score) tuples sorted by score
    """
    ranked = []

    for result in results:
        score = 0.0

        # Check first author match
        authors = result.get('author', [])
        if authors:
            first_author = authors[0].get('family', '').lower()
            if first_author == target_author.lower():
                score += 0.5
            elif target_author.lower() in first_author:
                score += 0.3

        # Check year match
        pub_year = result.get('published-print', {}).get('date-parts', [[None]])[0][0]
        if pub_year is None:
            pub_year = result.get('published-online', {}).get('date-parts', [[None]])[0][0]

        if pub_year:
            year_str = str(pub_year)
            if year_str == target_year:
                score += 0.3
            elif abs(int(year_str) - int(target_year)) <= 1:
                score += 0.2

        # Add to ranked list
        ranked.append((result, score))

    # Sort by score descending
    ranked.sort(key=lambda x: x[1], reverse=True)

    return ranked


def generate_citation_key(
    author: str,
    year: str,
    existing_keys: set
) -> str:
    """
    Generate BibTeX citation key following RRWrite convention.

    Format: {firstauthor}{year} (e.g., park2023)
    Handle collisions: park2023a, park2023b, etc.

    Args:
        author: First author surname
        year: Publication year
        existing_keys: Set of already-used keys

    Returns:
        Unique citation key
    """
    # Base key: lowercase author + year
    base_key = f"{author.lower()}{year}"

    # Check for collision
    if base_key not in existing_keys:
        return base_key

    # Add suffix: a, b, c, ...
    for suffix in 'abcdefghijklmnopqrstuvwxyz':
        key = f"{base_key}{suffix}"
        if key not in existing_keys:
            return key

    # Fallback: numeric suffix
    counter = 1
    while True:
        key = f"{base_key}_{counter}"
        if key not in existing_keys:
            return key
        counter += 1


def update_bibtex_key(bibtex_entry: str, new_key: str) -> str:
    """
    Update citation key in BibTeX entry.

    Args:
        bibtex_entry: Original BibTeX entry
        new_key: New citation key

    Returns:
        Updated BibTeX entry
    """
    # Pattern: @article{OLD_KEY, or @inproceedings{OLD_KEY,
    pattern = r'(@\w+\{)[^,]+'
    replacement = f'\\1{new_key}'

    return re.sub(pattern, replacement, bibtex_entry, count=1)


def process_citations(
    citations: List[Dict],
    api: CrossRefAPI,
    confidence_threshold: float = 0.5
) -> Tuple[List[Dict], List[Dict], Dict[str, str]]:
    """
    Process citations: lookup DOIs, fetch BibTeX, generate mapping.

    Args:
        citations: Parsed Paperpile citations
        api: CrossRef API client
        confidence_threshold: Minimum confidence score for auto-accept

    Returns:
        Tuple of (successful_entries, failed_entries, paperpile_mapping)
    """
    successful = []
    failed = []
    paperpile_mapping = {}
    existing_keys = set()

    total = len(citations)

    for i, citation in enumerate(citations, 1):
        print(f"Processing {i}/{total}: {citation['display_text']}...", end=' ')

        author = citation.get('author')
        year = citation.get('year')

        if not author or not year:
            print("❌ Parse failed")
            failed.append({
                'citation': citation,
                'reason': 'Failed to parse author or year from display text'
            })
            continue

        # Search CrossRef
        results = api.search_by_author_year(author, year)

        if not results:
            print("❌ No results")
            failed.append({
                'citation': citation,
                'reason': 'No CrossRef results found'
            })
            continue

        # Rank results
        ranked = rank_results_by_relevance(results, author, year)

        if not ranked or ranked[0][1] < confidence_threshold:
            print(f"⚠️  Low confidence ({ranked[0][1]:.2f})")
            failed.append({
                'citation': citation,
                'reason': f'Low confidence match (score: {ranked[0][1]:.2f})',
                'top_candidate': {
                    'doi': ranked[0][0].get('DOI'),
                    'title': ranked[0][0].get('title', [''])[0],
                    'score': ranked[0][1]
                } if ranked else None
            })
            continue

        # Get best match
        best_match, score = ranked[0]
        doi = best_match.get('DOI')

        if not doi:
            print("❌ No DOI")
            failed.append({
                'citation': citation,
                'reason': 'No DOI in CrossRef result'
            })
            continue

        # Fetch BibTeX
        bibtex = api.fetch_bibtex(doi)

        if not bibtex:
            print("❌ BibTeX fetch failed")
            failed.append({
                'citation': citation,
                'reason': 'Failed to fetch BibTeX from DOI',
                'doi': doi
            })
            continue

        # Generate citation key
        citation_key = generate_citation_key(author, year, existing_keys)
        existing_keys.add(citation_key)

        # Update BibTeX key
        bibtex = update_bibtex_key(bibtex, citation_key)

        # Handle multi-citations (codes with '+')
        paperpile_code = citation['paperpile_code']
        if '+' in paperpile_code:
            # For now, map entire code to single key
            # TODO: Could split and create multiple entries
            paperpile_mapping[paperpile_code] = citation_key
        else:
            paperpile_mapping[paperpile_code] = citation_key

        successful.append({
            'citation': citation,
            'citation_key': citation_key,
            'doi': doi,
            'bibtex': bibtex,
            'confidence_score': score
        })

        print(f"✓ {citation_key} (score: {score:.2f})")

    return successful, failed, paperpile_mapping


def write_bib_file(entries: List[Dict], output_path: Path) -> None:
    """Write BibTeX entries to .bib file."""
    with open(output_path, 'w', encoding='utf-8') as f:
        for entry in entries:
            f.write(entry['bibtex'])
            f.write('\n\n')


def write_mapping_file(mapping: Dict[str, str], output_path: Path) -> None:
    """Write Paperpile mapping to JSON file."""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(mapping, f, indent=2, sort_keys=True)


def write_report(
    successful: List[Dict],
    failed: List[Dict],
    output_path: Path
) -> None:
    """Write extraction quality report."""
    total = len(successful) + len(failed)
    success_rate = len(successful) / total * 100 if total > 0 else 0

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# Citation Extraction Report\n\n")

        f.write("## Summary Statistics\n\n")
        f.write(f"- **Total citations**: {total}\n")
        f.write(f"- **Successfully matched**: {len(successful)} ({success_rate:.1f}%)\n")
        f.write(f"- **Failed matches**: {len(failed)} ({100-success_rate:.1f}%)\n\n")

        if successful:
            f.write("## Successfully Matched Citations\n\n")
            for entry in successful:
                citation = entry['citation']
                f.write(f"- `{entry['citation_key']}`: {citation['display_text']}\n")
                f.write(f"  - DOI: {entry['doi']}\n")
                f.write(f"  - Confidence: {entry['confidence_score']:.2f}\n")

        if failed:
            f.write("\n## Failed Matches (Manual Review Required)\n\n")
            for failure in failed:
                citation = failure['citation']
                f.write(f"- {citation['display_text']} (Paperpile: {citation['paperpile_code']})\n")
                f.write(f"  - **Reason**: {failure['reason']}\n")
                if 'top_candidate' in failure and failure['top_candidate']:
                    cand = failure['top_candidate']
                    f.write(f"  - **Suggested**: {cand['title']} (DOI: {cand['doi']}, score: {cand['score']:.2f})\n")


def write_failed_json(failed: List[Dict], output_path: Path) -> None:
    """Write failed citations to JSON for manual review."""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(failed, f, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description='Build BibTeX bibliography from Paperpile citations'
    )
    parser.add_argument(
        '--citations',
        type=Path,
        required=True,
        help='Path to extracted citations JSON (from rrwrite-extract-paperpile-citations.py)'
    )
    parser.add_argument(
        '--output-bib',
        type=Path,
        required=True,
        help='Output BibTeX file path'
    )
    parser.add_argument(
        '--output-mapping',
        type=Path,
        required=True,
        help='Output Paperpile mapping JSON path'
    )
    parser.add_argument(
        '--email',
        type=str,
        help='Contact email for polite CrossRef API usage'
    )
    parser.add_argument(
        '--confidence-threshold',
        type=float,
        default=0.5,
        help='Minimum confidence score for auto-accept (default: 0.5)'
    )

    args = parser.parse_args()

    # Load citations
    if not args.citations.exists():
        print(f"Error: Citations file not found: {args.citations}")
        return 1

    with open(args.citations, 'r', encoding='utf-8') as f:
        data = json.load(f)
        citations = data.get('citations', [])

    if not citations:
        print("Error: No citations found in input file")
        return 1

    print(f"Loaded {len(citations)} citations from {args.citations}")

    # Initialize API
    api = CrossRefAPI(email=args.email)

    # Process citations
    print("\n=== Querying CrossRef API ===\n")
    successful, failed, mapping = process_citations(
        citations,
        api,
        confidence_threshold=args.confidence_threshold
    )

    # Write outputs
    args.output_bib.parent.mkdir(parents=True, exist_ok=True)

    write_bib_file(successful, args.output_bib)
    print(f"\n✓ BibTeX written to: {args.output_bib}")

    write_mapping_file(mapping, args.output_mapping)
    print(f"✓ Mapping written to: {args.output_mapping}")

    # Write report
    report_path = args.output_bib.parent / 'citation_extraction_report.md'
    write_report(successful, failed, report_path)
    print(f"✓ Report written to: {report_path}")

    # Write failed citations
    if failed:
        failed_path = args.output_bib.parent / 'citations_failed.json'
        write_failed_json(failed, failed_path)
        print(f"⚠️  Failed citations written to: {failed_path}")
        print(f"   {len(failed)} citations require manual review")

    # Summary
    print(f"\n=== Summary ===")
    print(f"✓ Successful: {len(successful)}")
    print(f"❌ Failed: {len(failed)}")
    print(f"Success rate: {len(successful)/(len(successful)+len(failed))*100:.1f}%")

    return 0


if __name__ == '__main__':
    exit(main())
