#!/usr/bin/env python3
"""
OpenAlex API client for literature search.

OpenAlex is a free, open catalog of scholarly papers, authors, institutions, and more.
- 250M+ works (papers, books, datasets)
- Citation counts, abstracts, DOIs
- No API key required (but polite pool recommended)
- Rate limit: 100,000 requests/day (10 req/sec with polite pool)

Usage:
    python scripts/rrwrite-api-openalex.py "query" --max-results 20
"""

import argparse
import json
import sys
import time
from typing import List, Dict
from urllib.parse import quote

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("Error: requests not installed. Install with: pip install requests")
    sys.exit(1)


class OpenAlexClient:
    """Client for OpenAlex API"""

    BASE_URL = "https://api.openalex.org"

    def __init__(self, email: str = "research@example.org"):
        """
        Initialize OpenAlex client.

        Args:
            email: Contact email for polite pool (faster rate limits)
        """
        self.email = email
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': f'RRWriteLiteratureSearch/1.0 (mailto:{email})'
        })

    def search(self, query: str, max_results: int = 20, year_min: int = None) -> List[Dict]:
        """
        Search OpenAlex for papers.

        Args:
            query: Search query
            max_results: Maximum results to return
            year_min: Minimum publication year filter

        Returns:
            List of paper dictionaries
        """
        papers = []
        per_page = min(max_results, 200)  # OpenAlex max per page
        page = 1

        # Build filter parameters
        filters = []
        if year_min:
            filters.append(f"publication_year:>{year_min}")

        filter_str = ",".join(filters) if filters else None

        while len(papers) < max_results:
            params = {
                'search': query,
                'per-page': per_page,
                'page': page,
                'mailto': self.email  # Polite pool
            }

            if filter_str:
                params['filter'] = filter_str

            # Sort by citation count (relevance)
            params['sort'] = 'cited_by_count:desc'

            try:
                response = self.session.get(
                    f"{self.BASE_URL}/works",
                    params=params,
                    timeout=30
                )

                if response.status_code == 429:
                    # Rate limited
                    print("Rate limited, waiting 60 seconds...", file=sys.stderr)
                    time.sleep(60)
                    continue

                response.raise_for_status()
                data = response.json()

                results = data.get('results', [])
                if not results:
                    break

                for work in results:
                    if len(papers) >= max_results:
                        break

                    paper = self._parse_work(work)
                    if paper:
                        papers.append(paper)

                # Check if more pages available
                meta = data.get('meta', {})
                if not meta.get('next_cursor'):
                    break

                page += 1
                time.sleep(0.1)  # Be polite

            except requests.exceptions.RequestException as e:
                print(f"OpenAlex API error: {e}", file=sys.stderr)
                break

        return papers

    def _parse_work(self, work: Dict) -> Dict:
        """Parse OpenAlex work into standardized paper format"""

        # Extract DOI
        doi = work.get('doi', '').replace('https://doi.org/', '')

        # Extract authors
        authorships = work.get('authorships', [])
        authors = ', '.join([
            a.get('author', {}).get('display_name', 'Unknown')
            for a in authorships[:3]  # First 3 authors
        ])
        if len(authorships) > 3:
            authors += ' et al.'

        # Extract year
        year = work.get('publication_year')

        # Extract abstract (inverted index format)
        abstract_inverted = work.get('abstract_inverted_index', {})
        abstract = self._reconstruct_abstract(abstract_inverted) if abstract_inverted else None

        # Extract title
        title = work.get('title', '')

        # Extract journal/venue
        primary_location = work.get('primary_location', {})
        source = primary_location.get('source', {})
        journal = source.get('display_name', '')

        # Citation count
        cited_by_count = work.get('cited_by_count', 0)

        # OpenAlex ID
        openalex_id = work.get('id', '').replace('https://openalex.org/', '')

        return {
            'title': title,
            'authors': authors,
            'year': year,
            'doi': doi,
            'abstract': abstract,
            'journal': journal,
            'citations': cited_by_count,
            'citationCount': cited_by_count,  # Alias for compatibility
            'openalex_id': openalex_id,
            'source': 'openalex'
        }

    def _reconstruct_abstract(self, inverted_index: Dict) -> str:
        """
        Reconstruct abstract from OpenAlex inverted index format.

        Args:
            inverted_index: Dict mapping words to position lists

        Returns:
            Reconstructed abstract text
        """
        if not inverted_index:
            return None

        # Find max position
        max_pos = 0
        for positions in inverted_index.values():
            if positions:
                max_pos = max(max_pos, max(positions))

        # Reconstruct
        words = [''] * (max_pos + 1)
        for word, positions in inverted_index.items():
            for pos in positions:
                words[pos] = word

        return ' '.join(words)


def main():
    parser = argparse.ArgumentParser(
        description='Search OpenAlex for academic papers',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument('query', help='Search query')
    parser.add_argument('--max-results', type=int, default=20, help='Maximum results (default: 20)')
    parser.add_argument('--year-min', type=int, help='Minimum publication year')
    parser.add_argument('--email', default='research@example.org', help='Contact email for polite pool')
    parser.add_argument('--output', help='Output JSON file (default: stdout)')

    args = parser.parse_args()

    # Search
    print(f"Searching OpenAlex: '{args.query}'", file=sys.stderr)

    client = OpenAlexClient(email=args.email)
    papers = client.search(
        query=args.query,
        max_results=args.max_results,
        year_min=args.year_min
    )

    print(f"Found {len(papers)} papers", file=sys.stderr)

    # Output
    result = {
        'query': args.query,
        'source': 'openalex',
        'count': len(papers),
        'papers': papers
    }

    if args.output:
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2)
    else:
        print(json.dumps(result, indent=2))

    return 0


if __name__ == '__main__':
    sys.exit(main())
