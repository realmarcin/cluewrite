#!/usr/bin/env python3
"""
Validate literature evidence from previous manuscript versions.

This script validates DOIs and checks paper freshness to ensure
evidence from previous versions is still accurate and accessible.
"""

import argparse
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import pandas as pd
import requests
from datetime import datetime
import json


def validate_doi(doi: str, timeout: int = 5) -> str:
    """
    Validate a DOI by checking if it resolves.

    Args:
        doi: DOI string (with or without https://doi.org/ prefix)
        timeout: HTTP request timeout in seconds

    Returns:
        Status: "valid", "invalid", or "unknown"
    """
    # Clean DOI
    doi_clean = doi.replace("https://doi.org/", "").strip()
    if not doi_clean:
        return "invalid"

    # Try to resolve DOI
    url = f"https://doi.org/{doi_clean}"
    try:
        response = requests.head(url, timeout=timeout, allow_redirects=True)
        if response.status_code == 200:
            return "valid"
        elif response.status_code == 404:
            return "invalid"
        else:
            return "unknown"
    except requests.exceptions.Timeout:
        return "unknown"
    except requests.exceptions.RequestException:
        return "unknown"


def check_freshness(year: int, current_year: int = None) -> str:
    """
    Check if a paper is fresh, stale, or old.

    Args:
        year: Publication year
        current_year: Current year (defaults to now)

    Returns:
        Status: "fresh" (<5 years), "stale" (5-10 years), or "old" (>10 years)
    """
    if current_year is None:
        current_year = datetime.now().year

    age = current_year - year

    if age < 5:
        return "fresh"
    elif age < 10:
        return "stale"
    else:
        return "old"


def extract_year_from_citation(citation: str) -> int:
    """
    Extract publication year from citation string.

    Args:
        citation: Citation string (e.g., "Author et al. (2020)")

    Returns:
        Year as integer, or current year if not found
    """
    import re

    # Look for 4-digit year
    match = re.search(r'\((\d{4})\)', citation)
    if match:
        return int(match.group(1))

    match = re.search(r'\b(\d{4})\b', citation)
    if match:
        return int(match.group(1))

    # Default to current year if not found
    return datetime.now().year


def validate_evidence_file(
    csv_path: Path,
    validate_dois: bool = True,
    check_freshness_flag: bool = True,
    timeout: int = 5
) -> pd.DataFrame:
    """
    Validate an evidence CSV file.

    Args:
        csv_path: Path to literature_evidence.csv
        validate_dois: Whether to validate DOIs (requires network)
        check_freshness_flag: Whether to check paper freshness
        timeout: HTTP request timeout in seconds

    Returns:
        DataFrame with validation results including:
        - All original columns
        - doi_status: "valid", "invalid", or "unknown"
        - freshness: "fresh", "stale", or "old"
        - action: "keep", "review", or "remove"
        - reason: Description of status
    """
    # Load CSV
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"Error reading CSV: {e}", file=sys.stderr)
        sys.exit(1)

    # Check required columns
    required_cols = ["doi", "citation_key", "citation", "evidence_quote"]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        print(f"Error: Missing required columns: {missing_cols}", file=sys.stderr)
        sys.exit(1)

    # Initialize validation columns
    df["doi_status"] = "unknown"
    df["freshness"] = "unknown"
    df["action"] = "keep"
    df["reason"] = ""

    # Validate each row
    for idx, row in df.iterrows():
        reasons = []

        # Validate DOI
        if validate_dois and pd.notna(row["doi"]):
            status = validate_doi(row["doi"], timeout=timeout)
            df.at[idx, "doi_status"] = status

            if status == "invalid":
                df.at[idx, "action"] = "remove"
                reasons.append("DOI does not resolve")
            elif status == "unknown":
                reasons.append("DOI validation failed (network error)")
        else:
            df.at[idx, "doi_status"] = "not_checked"

        # Check freshness
        if check_freshness_flag and pd.notna(row["citation"]):
            year = extract_year_from_citation(row["citation"])
            freshness = check_freshness(year)
            df.at[idx, "freshness"] = freshness

            if freshness == "stale":
                if df.at[idx, "action"] == "keep":
                    df.at[idx, "action"] = "review"
                reasons.append(f"Paper is {datetime.now().year - year} years old")
            elif freshness == "old":
                if df.at[idx, "action"] == "keep":
                    df.at[idx, "action"] = "review"
                reasons.append(f"Paper is {datetime.now().year - year} years old")

        # Set reason
        if reasons:
            df.at[idx, "reason"] = "; ".join(reasons)
        else:
            df.at[idx, "reason"] = "Valid"

    return df


def generate_validation_summary(validation_df: pd.DataFrame) -> Dict:
    """
    Generate summary statistics from validation results.

    Args:
        validation_df: DataFrame with validation results

    Returns:
        Dictionary with summary statistics
    """
    total = len(validation_df)

    # Count by DOI status
    doi_counts = validation_df["doi_status"].value_counts().to_dict()

    # Count by freshness
    freshness_counts = validation_df["freshness"].value_counts().to_dict()

    # Count by action
    action_counts = validation_df["action"].value_counts().to_dict()

    return {
        "total_papers": total,
        "doi_status": doi_counts,
        "freshness": freshness_counts,
        "action": action_counts,
        "valid_papers": action_counts.get("keep", 0),
        "needs_review": action_counts.get("review", 0),
        "to_remove": action_counts.get("remove", 0)
    }


def main():
    parser = argparse.ArgumentParser(
        description="Validate literature evidence from previous versions"
    )
    parser.add_argument(
        "--csv",
        type=Path,
        required=True,
        help="Path to literature_evidence.csv"
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Path to save validation results (default: {csv}_validation.csv)"
    )
    parser.add_argument(
        "--no-doi-check",
        action="store_true",
        help="Skip DOI validation (faster, no network needed)"
    )
    parser.add_argument(
        "--no-freshness-check",
        action="store_true",
        help="Skip freshness checking"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=5,
        help="HTTP request timeout in seconds (default: 5)"
    )
    parser.add_argument(
        "--summary-only",
        action="store_true",
        help="Print summary statistics only (no CSV output)"
    )

    args = parser.parse_args()

    # Validate CSV path
    if not args.csv.exists():
        print(f"Error: CSV file not found: {args.csv}", file=sys.stderr)
        sys.exit(1)

    # Set output path
    if args.output is None:
        args.output = args.csv.parent / f"{args.csv.stem}_validation.csv"

    # Run validation
    print(f"Validating evidence from: {args.csv}")
    if not args.no_doi_check:
        print("Validating DOIs (this may take a while)...")

    validation_df = validate_evidence_file(
        args.csv,
        validate_dois=not args.no_doi_check,
        check_freshness_flag=not args.no_freshness_check,
        timeout=args.timeout
    )

    # Generate summary
    summary = generate_validation_summary(validation_df)

    # Print summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    print(f"Total papers: {summary['total_papers']}")
    print(f"\nDOI Status:")
    for status, count in summary['doi_status'].items():
        print(f"  {status}: {count}")
    print(f"\nFreshness:")
    for freshness, count in summary['freshness'].items():
        print(f"  {freshness}: {count}")
    print(f"\nRecommended Actions:")
    print(f"  ✓ Keep: {summary['valid_papers']}")
    print(f"  ⚠ Review: {summary['needs_review']}")
    print(f"  ✗ Remove: {summary['to_remove']}")
    print("=" * 60)

    # Save results
    if not args.summary_only:
        validation_df.to_csv(args.output, index=False)
        print(f"\nValidation results saved to: {args.output}")

    # Exit with error code if any papers need removal
    if summary['to_remove'] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
