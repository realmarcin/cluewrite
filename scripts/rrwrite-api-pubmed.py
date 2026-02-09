#!/usr/bin/env python3
"""
PubMed E-utilities API integration for biomedical literature search.

Free API with no authentication required (rate limited to 3 requests/second).
Returns: PMID, DOI, title, authors, journal, year, abstract
"""

import argparse
import json
import sys
import time
from typing import List, Dict, Any
from pathlib import Path
import xml.etree.ElementTree as ET

import requests


class PubMedAPI:
    """PubMed E-utilities API client."""

    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    RATE_LIMIT_DELAY = 0.34  # ~3 requests/second

    def __init__(self, email: str = None):
        """
        Initialize PubMed API client.

        Args:
            email: Optional email for API usage tracking (recommended by NCBI)
        """
        self.email = email
        self.last_request_time = 0

    def _rate_limit(self):
        """Enforce rate limiting (3 requests/second)."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.RATE_LIMIT_DELAY:
            time.sleep(self.RATE_LIMIT_DELAY - elapsed)
        self.last_request_time = time.time()

    def search(self, query: str, max_results: int = 20) -> List[str]:
        """
        Search PubMed and return PMIDs.

        Args:
            query: Search query (PubMed syntax)
            max_results: Maximum results

        Returns:
            List of PMIDs
        """
        self._rate_limit()

        url = f"{self.BASE_URL}esearch.fcgi"
        params = {
            "db": "pubmed",
            "term": query,
            "retmax": max_results,
            "retmode": "json",
            "sort": "relevance"
        }

        if self.email:
            params["email"] = self.email

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            pmids = data.get("esearchresult", {}).get("idlist", [])
            return pmids

        except Exception as e:
            print(f"Error: PubMed search failed: {e}", file=sys.stderr)
            return []

    def fetch_summaries(self, pmids: List[str]) -> List[Dict[str, Any]]:
        """
        Fetch article summaries for PMIDs.

        Args:
            pmids: List of PMIDs

        Returns:
            List of article dictionaries
        """
        if not pmids:
            return []

        self._rate_limit()

        url = f"{self.BASE_URL}esummary.fcgi"
        params = {
            "db": "pubmed",
            "id": ",".join(pmids),
            "retmode": "json"
        }

        if self.email:
            params["email"] = self.email

        try:
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()

            articles = []
            for pmid in pmids:
                if pmid in data.get("result", {}):
                    article = data["result"][pmid]
                    articles.append({
                        "pmid": pmid,
                        "title": article.get("title", ""),
                        "authors": self._format_authors(article.get("authors", [])),
                        "journal": article.get("fulljournalname", ""),
                        "pub_date": article.get("pubdate", ""),
                        "year": self._extract_year(article.get("pubdate", "")),
                        "doi": self._extract_doi(article.get("elocationid", "")),
                        "source": "PubMed",
                        "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                        "abstract": ""  # Filled by fetch_abstracts
                    })

            return articles

        except Exception as e:
            print(f"Error: Failed to fetch summaries: {e}", file=sys.stderr)
            return []

    def fetch_abstracts(self, pmids: List[str]) -> Dict[str, str]:
        """
        Fetch abstracts for PMIDs via efetch (XML).

        Args:
            pmids: List of PMIDs

        Returns:
            Dictionary mapping PMID -> abstract text
        """
        if not pmids:
            return {}

        self._rate_limit()

        url = f"{self.BASE_URL}efetch.fcgi"
        params = {
            "db": "pubmed",
            "id": ",".join(pmids),
            "retmode": "xml"
        }

        if self.email:
            params["email"] = self.email

        try:
            response = requests.get(url, params=params, timeout=20)
            response.raise_for_status()

            # Parse XML
            root = ET.fromstring(response.content)
            abstracts = {}

            for article in root.findall(".//PubmedArticle"):
                pmid_elem = article.find(".//PMID")
                abstract_elem = article.find(".//AbstractText")

                if pmid_elem is not None and abstract_elem is not None:
                    pmid = pmid_elem.text
                    abstract = abstract_elem.text or ""
                    abstracts[pmid] = abstract

            return abstracts

        except Exception as e:
            print(f"Error: Failed to fetch abstracts: {e}", file=sys.stderr)
            return {}

    def _format_authors(self, authors_data: List) -> str:
        """Format author list as string."""
        if not authors_data:
            return ""

        author_names = []
        for author in authors_data[:3]:  # First 3 authors
            name = author.get("name", "")
            if name:
                author_names.append(name)

        if len(authors_data) > 3:
            author_names.append("et al.")

        return ", ".join(author_names)

    def _extract_year(self, pub_date: str) -> str:
        """Extract year from publication date string."""
        if not pub_date:
            return ""

        # Try to extract 4-digit year
        import re
        match = re.search(r'\b(19|20)\d{2}\b', pub_date)
        if match:
            return match.group(0)

        return ""

    def _extract_doi(self, elocationid: str) -> str:
        """Extract DOI from elocationid field."""
        if not elocationid:
            return ""

        # elocationid format: "doi: 10.1234/journal.2024.001"
        if "doi:" in elocationid.lower():
            return elocationid.split("doi:")[-1].strip()

        # Check if it looks like a DOI
        if elocationid.startswith("10."):
            return elocationid

        return ""


def search_pubmed(
    query: str,
    max_results: int = 20,
    email: str = None
) -> List[Dict[str, Any]]:
    """
    Search PubMed and return article metadata.

    Args:
        query: Search query
        max_results: Maximum results
        email: Optional email for API tracking

    Returns:
        List of paper dictionaries with PMID, DOI, title, authors, abstract
    """
    api = PubMedAPI(email=email)

    # Step 1: Search for PMIDs
    print(f"Searching PubMed: '{query}'", file=sys.stderr)
    pmids = api.search(query, max_results)

    if not pmids:
        print("No results found", file=sys.stderr)
        return []

    print(f"Found {len(pmids)} PMIDs", file=sys.stderr)

    # Step 2: Fetch article summaries
    articles = api.fetch_summaries(pmids)

    # Step 3: Fetch abstracts
    print(f"Fetching abstracts for {len(pmids)} articles", file=sys.stderr)
    abstracts = api.fetch_abstracts(pmids)

    # Add abstracts to articles
    for article in articles:
        pmid = article["pmid"]
        article["abstract"] = abstracts.get(pmid, "")

    return articles


def main():
    """Command-line interface for PubMed search."""
    parser = argparse.ArgumentParser(
        description="Search PubMed E-utilities API for biomedical papers"
    )
    parser.add_argument("query", help="Search query (PubMed syntax)")
    parser.add_argument(
        "--max-results",
        type=int,
        default=20,
        help="Maximum results (default: 20)"
    )
    parser.add_argument(
        "--email",
        help="Email for NCBI API tracking (recommended)"
    )
    parser.add_argument(
        "--output",
        help="Output JSON file (default: stdout)"
    )

    args = parser.parse_args()

    # Search
    results = search_pubmed(args.query, args.max_results, args.email)

    print(f"Retrieved {len(results)} complete articles", file=sys.stderr)

    # Output
    output_data = {
        "query": args.query,
        "result_count": len(results),
        "papers": results
    }

    if args.output:
        with open(args.output, 'w') as f:
            json.dump(output_data, f, indent=2)
        print(f"Results written to {args.output}", file=sys.stderr)
    else:
        print(json.dumps(output_data, indent=2))

    return 0


if __name__ == "__main__":
    sys.exit(main())
