#!/usr/bin/env python3
"""
Europe PMC API client for biomedical literature search.

Europe PMC provides access to life sciences literature including:
- PubMed Central full-text articles
- Agricultural and biological sciences
- Patents, clinical guidelines, theses
- No API key required
- Rate limit: ~3 requests/second

Usage:
    python scripts/rrwrite-api-europepmc.py "query" --max-results 20
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


class EuropePMCClient:
    """Client for Europe PMC API"""

    BASE_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest"

    def __init__(self):
        """Initialize Europe PMC client"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'RRWriteLiteratureSearch/1.0'
        })

    def search(self, query: str, max_results: int = 20, year_min: int = None) -> List[Dict]:
        """
        Search Europe PMC for papers.

        Args:
            query: Search query
            max_results: Maximum results to return
            year_min: Minimum publication year filter

        Returns:
            List of paper dictionaries
        """
        papers = []
        page_size = min(max_results, 1000)  # Europe PMC max
        cursor_mark = '*'

        # Add year filter to query
        search_query = query
        if year_min:
            search_query = f"({query}) AND (FIRST_PDATE:[{year_min} TO 2100])"

        while len(papers) < max_results:
            params = {
                'query': search_query,
                'format': 'json',
                'pageSize': page_size,
                'cursorMark': cursor_mark,
                'sort': 'CITED desc'  # Sort by citations
            }

            try:
                response = self.session.get(
                    f"{self.BASE_URL}/search",
                    params=params,
                    timeout=30
                )

                if response.status_code == 429:
                    print("Rate limited, waiting 10 seconds...", file=sys.stderr)
                    time.sleep(10)
                    continue

                response.raise_for_status()
                data = response.json()

                results = data.get('resultList', {}).get('result', [])
                if not results:
                    break

                for article in results:
                    if len(papers) >= max_results:
                        break

                    paper = self._parse_article(article)
                    if paper:
                        papers.append(paper)

                # Check for next cursor
                next_cursor = data.get('nextCursorMark')
                if not next_cursor or next_cursor == cursor_mark:
                    break

                cursor_mark = next_cursor
                time.sleep(0.34)  # ~3 req/sec

            except requests.exceptions.RequestException as e:
                print(f"Europe PMC API error: {e}", file=sys.stderr)
                break

        return papers

    def _parse_article(self, article: Dict) -> Dict:
        """Parse Europe PMC article into standardized format"""

        # Extract DOI
        doi = article.get('doi', '')

        # Extract authors
        author_list = article.get('authorString', 'Unknown authors')

        # Extract year
        pub_year = article.get('pubYear')
        if pub_year:
            try:
                year = int(pub_year)
            except (ValueError, TypeError):
                year = None
        else:
            year = None

        # Extract abstract
        abstract = article.get('abstractText', '')

        # Extract title
        title = article.get('title', '')

        # Extract journal
        journal = article.get('journalTitle', '')

        # Citation count
        cited_by = article.get('citedByCount', 0)
        if cited_by:
            try:
                citations = int(cited_by)
            except (ValueError, TypeError):
                citations = 0
        else:
            citations = 0

        # PMC ID and PMID
        pmcid = article.get('pmcid', '')
        pmid = article.get('pmid', '')

        return {
            'title': title,
            'authors': author_list,
            'year': year,
            'doi': doi,
            'abstract': abstract,
            'journal': journal,
            'citations': citations,
            'citationCount': citations,
            'pmid': pmid,
            'pmcid': pmcid,
            'source': 'europepmc'
        }


def main():
    parser = argparse.ArgumentParser(
        description='Search Europe PMC for biomedical literature',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument('query', help='Search query')
    parser.add_argument('--max-results', type=int, default=20, help='Maximum results (default: 20)')
    parser.add_argument('--year-min', type=int, help='Minimum publication year')
    parser.add_argument('--output', help='Output JSON file (default: stdout)')

    args = parser.parse_args()

    # Search
    print(f"Searching Europe PMC: '{args.query}'", file=sys.stderr)

    client = EuropePMCClient()
    papers = client.search(
        query=args.query,
        max_results=args.max_results,
        year_min=args.year_min
    )

    print(f"Found {len(papers)} papers", file=sys.stderr)

    # Output
    result = {
        'query': args.query,
        'source': 'europepmc',
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
