#!/usr/bin/env python3
"""
Combined literature search using Semantic Scholar + PubMed APIs with caching.

This script combines:
- Semantic Scholar API (all domains, citation counts)
- PubMed E-utilities API (biomedical focus, PMID)
- Request caching (24-hour SQLite cache)
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Dict, Any
import subprocess

# Check for requests_cache availability
try:
    import requests_cache
    CACHE_AVAILABLE = True
except ImportError:
    CACHE_AVAILABLE = False
    print("Warning: requests_cache not installed. Install with: pip install requests-cache", file=sys.stderr)


def setup_cache(cache_dir: Path):
    """
    Setup request caching if available.

    Args:
        cache_dir: Directory for cache files
    """
    if not CACHE_AVAILABLE:
        return

    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_file = cache_dir / "literature_cache"

    requests_cache.install_cache(
        str(cache_file),
        backend="sqlite",
        expire_after=86400  # 24 hours
    )

    print(f"Cache enabled: {cache_file}.sqlite (24 hour expiry)", file=sys.stderr)


def search_semantic_scholar(
    query: str,
    max_results: int = 20,
    script_path: Path = None
) -> List[Dict]:
    """
    Search Semantic Scholar via Python script.

    Args:
        query: Search query
        max_results: Maximum results
        script_path: Path to rrwrite-api-semanticscholar.py script

    Returns:
        List of paper dictionaries
    """
    if script_path is None:
        script_path = Path(__file__).parent / "rrwrite-api-semanticscholar.py"

    cmd = [
        "python3",
        str(script_path),
        query,
        "--max-results", str(max_results),
        "--prioritize"  # Prioritize highly-cited + recent
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            print(f"Semantic Scholar error: {result.stderr}", file=sys.stderr)
            return []

        data = json.loads(result.stdout)
        return data.get("papers", [])

    except Exception as e:
        print(f"Semantic Scholar failed: {e}", file=sys.stderr)
        return []


def search_pubmed(
    query: str,
    max_results: int = 20,
    script_path: Path = None
) -> List[Dict]:
    """
    Search PubMed via Python script.

    Args:
        query: Search query
        max_results: Maximum results
        script_path: Path to rrwrite-api-pubmed.py script

    Returns:
        List of paper dictionaries
    """
    if script_path is None:
        script_path = Path(__file__).parent / "rrwrite-api-pubmed.py"

    cmd = [
        "python3",
        str(script_path),
        query,
        "--max-results", str(max_results)
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=45
        )

        if result.returncode != 0:
            print(f"PubMed error: {result.stderr}", file=sys.stderr)
            return []

        data = json.loads(result.stdout)
        return data.get("papers", [])

    except Exception as e:
        print(f"PubMed failed: {e}", file=sys.stderr)
        return []


def deduplicate_papers(papers: List[Dict]) -> List[Dict]:
    """
    Remove duplicate papers based on DOI or title.

    Args:
        papers: List of paper dictionaries

    Returns:
        Deduplicated list
    """
    seen_dois = set()
    seen_titles = set()
    unique_papers = []

    for paper in papers:
        doi = paper.get("doi", "").strip().lower()
        title = paper.get("title", "").strip().lower()

        # Skip if we've seen this DOI
        if doi and doi in seen_dois:
            continue

        # Skip if we've seen this exact title
        if title and title in seen_titles:
            continue

        # Add to unique list
        unique_papers.append(paper)

        if doi:
            seen_dois.add(doi)
        if title:
            seen_titles.add(title)

    return unique_papers


def merge_results(
    semantic_results: List[Dict],
    pubmed_results: List[Dict]
) -> Dict[str, Any]:
    """
    Merge and deduplicate results from both sources.

    Args:
        semantic_results: Papers from Semantic Scholar
        pubmed_results: Papers from PubMed

    Returns:
        Merged result dictionary
    """
    # Combine all papers
    all_papers = semantic_results + pubmed_results

    # Deduplicate
    unique_papers = deduplicate_papers(all_papers)

    # Sort by citations (if available) and year
    def sort_key(paper):
        citations = paper.get("citations", 0)
        year = paper.get("year", 0)
        # Convert year to int if string
        if isinstance(year, str):
            try:
                year = int(year)
            except (ValueError, TypeError):
                year = 0
        return (-citations, -year)  # Descending order

    unique_papers.sort(key=sort_key)

    return {
        "papers": unique_papers,
        "counts": {
            "semantic_scholar": len(semantic_results),
            "pubmed": len(pubmed_results),
            "total_unique": len(unique_papers)
        }
    }


def search_literature(
    query: str,
    max_results: int = 20,
    use_pubmed: bool = True,
    use_semantic_scholar: bool = True,
    cache_dir: Path = None
) -> Dict[str, Any]:
    """
    Search literature using multiple APIs.

    Args:
        query: Search query
        max_results: Maximum results per source
        use_pubmed: Include PubMed search
        use_semantic_scholar: Include Semantic Scholar search
        cache_dir: Directory for request cache

    Returns:
        Dictionary with merged results
    """
    # Setup caching
    if cache_dir:
        setup_cache(cache_dir)

    results = {
        "query": query,
        "semantic_scholar": [],
        "pubmed": []
    }

    # Search Semantic Scholar
    if use_semantic_scholar:
        print(f"\n=== Searching Semantic Scholar ===", file=sys.stderr)
        semantic_results = search_semantic_scholar(query, max_results)
        results["semantic_scholar"] = semantic_results
        print(f"Found {len(semantic_results)} papers", file=sys.stderr)

    # Search PubMed
    if use_pubmed:
        print(f"\n=== Searching PubMed ===", file=sys.stderr)
        pubmed_results = search_pubmed(query, max_results)
        results["pubmed"] = pubmed_results
        print(f"Found {len(pubmed_results)} papers", file=sys.stderr)

    # Merge results
    print(f"\n=== Merging Results ===", file=sys.stderr)
    merged = merge_results(
        results["semantic_scholar"],
        results["pubmed"]
    )

    print(f"Total unique papers: {merged['counts']['total_unique']}", file=sys.stderr)

    return {
        "query": query,
        "papers": merged["papers"],
        "counts": merged["counts"]
    }


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description="Search academic literature using Semantic Scholar + PubMed APIs"
    )
    parser.add_argument("query", help="Search query")
    parser.add_argument(
        "--max-results",
        type=int,
        default=20,
        help="Maximum results per source (default: 20)"
    )
    parser.add_argument(
        "--no-pubmed",
        action="store_true",
        help="Disable PubMed search"
    )
    parser.add_argument(
        "--no-semantic-scholar",
        action="store_true",
        help="Disable Semantic Scholar search"
    )
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=Path("manuscript/.cache"),
        help="Cache directory (default: manuscript/.cache)"
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output JSON file (default: stdout)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose output"
    )

    args = parser.parse_args()

    # Search
    results = search_literature(
        query=args.query,
        max_results=args.max_results,
        use_pubmed=not args.no_pubmed,
        use_semantic_scholar=not args.no_semantic_scholar,
        cache_dir=args.cache_dir
    )

    # Add metadata
    results["search_config"] = {
        "semantic_scholar_enabled": not args.no_semantic_scholar,
        "pubmed_enabled": not args.no_pubmed,
        "max_results_per_source": args.max_results
    }

    # Output
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nResults written to {args.output}", file=sys.stderr)
    else:
        print(json.dumps(results, indent=2))

    return 0


if __name__ == "__main__":
    sys.exit(main())
