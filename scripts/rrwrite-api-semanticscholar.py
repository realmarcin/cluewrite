#!/usr/bin/env python3
"""
Semantic Scholar API integration for literature search.

Free API with no authentication required.
Returns: title, abstract, DOI, authors, year, citation count, URL
"""

import argparse
import json
import sys
from typing import List, Dict, Any
from pathlib import Path

import requests


def format_authors(authors: List[Dict]) -> str:
    """
    Format author list as string.

    Args:
        authors: List of author dictionaries with 'name' field

    Returns:
        Formatted author string (e.g., "Smith J, Jones A, et al.")
    """
    if not authors:
        return ""

    author_names = [a.get("name", "") for a in authors[:3]]
    if len(authors) > 3:
        author_names.append("et al.")

    return ", ".join(author_names)


def search_semantic_scholar(
    query: str,
    max_results: int = 20,
    year_min: int = None,
    year_max: int = None
) -> List[Dict[str, Any]]:
    """
    Search Semantic Scholar API.

    Args:
        query: Search query
        max_results: Maximum number of results (default: 20)
        year_min: Minimum publication year filter
        year_max: Maximum publication year filter

    Returns:
        List of paper dictionaries with:
        - title: Paper title
        - abstract: Abstract text
        - doi: DOI identifier
        - citations: Citation count
        - year: Publication year
        - authors: Formatted author string
        - url: Semantic Scholar URL
        - source: "Semantic Scholar"

    Examples:
        >>> results = search_semantic_scholar("LinkML schema", max_results=5)
        >>> len(results) <= 5
        True
        >>> all('doi' in r for r in results)
        True
    """
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        "query": query,
        "limit": max_results,
        "fields": "title,abstract,citationCount,externalIds,url,year,authors,venue"
    }

    # Add year filters if specified
    if year_min:
        params["year"] = f"{year_min}-"
    if year_max:
        if year_min:
            params["year"] = f"{year_min}-{year_max}"
        else:
            params["year"] = f"-{year_max}"

    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()

        results = []
        for paper in data.get("data", []):
            # Extract DOI from externalIds
            external_ids = paper.get("externalIds", {})
            doi = external_ids.get("DOI", "")
            arxiv = external_ids.get("ArXiv", "")

            # Format authors
            authors = paper.get("authors", [])
            author_str = format_authors(authors)

            # Get venue (journal/conference)
            venue = paper.get("venue", "")

            results.append({
                "title": paper.get("title", ""),
                "abstract": paper.get("abstract", ""),
                "doi": doi,
                "arxiv": arxiv,
                "citations": paper.get("citationCount", 0),
                "year": paper.get("year", ""),
                "authors": author_str,
                "venue": venue,
                "url": paper.get("url", ""),
                "source": "Semantic Scholar"
            })

        return results

    except requests.exceptions.RequestException as e:
        print(f"Error: Semantic Scholar API request failed: {e}", file=sys.stderr)
        return []
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse API response: {e}", file=sys.stderr)
        return []


def filter_by_citations(papers: List[Dict], min_citations: int = 50) -> List[Dict]:
    """
    Filter papers by minimum citation count.

    Args:
        papers: List of paper dictionaries
        min_citations: Minimum citation threshold

    Returns:
        Filtered list of papers
    """
    return [p for p in papers if p.get("citations", 0) >= min_citations]


def prioritize_papers(
    papers: List[Dict],
    highly_cited_threshold: int = 100,
    recent_year: int = 2024
) -> List[Dict]:
    """
    Prioritize papers: highly-cited foundational + recent advances.

    Args:
        papers: List of paper dictionaries
        highly_cited_threshold: Citation threshold for foundational papers
        recent_year: Year threshold for recent papers

    Returns:
        Prioritized list (highly-cited first, then recent)
    """
    # Separate highly-cited and recent
    highly_cited = [p for p in papers if p.get("citations", 0) >= highly_cited_threshold]
    recent = [p for p in papers if p.get("year", 0) >= recent_year]

    # Sort highly-cited by citation count (descending)
    highly_cited.sort(key=lambda p: p.get("citations", 0), reverse=True)

    # Sort recent by year (descending)
    recent.sort(key=lambda p: p.get("year", 0), reverse=True)

    # Combine: top highly-cited + recent papers (avoid duplicates)
    seen_dois = set()
    prioritized = []

    for paper in highly_cited[:10]:  # Top 10 highly-cited
        doi = paper.get("doi", "")
        if doi and doi not in seen_dois:
            prioritized.append(paper)
            seen_dois.add(doi)

    for paper in recent[:10]:  # Top 10 recent
        doi = paper.get("doi", "")
        if doi and doi not in seen_dois:
            prioritized.append(paper)
            seen_dois.add(doi)

    return prioritized


def main():
    """Command-line interface for Semantic Scholar search."""
    parser = argparse.ArgumentParser(
        description="Search Semantic Scholar API for academic papers"
    )
    parser.add_argument("query", help="Search query")
    parser.add_argument(
        "--max-results",
        type=int,
        default=20,
        help="Maximum results (default: 20)"
    )
    parser.add_argument(
        "--year-min",
        type=int,
        help="Minimum publication year"
    )
    parser.add_argument(
        "--year-max",
        type=int,
        help="Maximum publication year"
    )
    parser.add_argument(
        "--min-citations",
        type=int,
        help="Filter by minimum citations"
    )
    parser.add_argument(
        "--prioritize",
        action="store_true",
        help="Prioritize highly-cited + recent papers"
    )
    parser.add_argument(
        "--output",
        help="Output JSON file (default: stdout)"
    )

    args = parser.parse_args()

    # Search
    print(f"Searching Semantic Scholar: '{args.query}'", file=sys.stderr)
    results = search_semantic_scholar(
        args.query,
        args.max_results,
        args.year_min,
        args.year_max
    )

    print(f"Found {len(results)} papers", file=sys.stderr)

    # Filter by citations if requested
    if args.min_citations:
        results = filter_by_citations(results, args.min_citations)
        print(f"Filtered to {len(results)} papers (≥{args.min_citations} citations)", file=sys.stderr)

    # Prioritize if requested
    if args.prioritize:
        results = prioritize_papers(results)
        print(f"Prioritized to {len(results)} papers", file=sys.stderr)

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
