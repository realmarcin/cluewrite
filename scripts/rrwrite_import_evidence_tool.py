#!/usr/bin/env python3
"""
Import and reuse literature evidence from previous manuscript versions.

This script detects previous versions, validates their evidence,
and imports valid evidence as a starting point for new versions.
"""

import argparse
import sys
import json
import shutil
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from datetime import datetime
import pandas as pd
import subprocess


def get_git_commit() -> Optional[str]:
    """Get current git commit hash."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None


def detect_previous_version(current_dir: Path) -> Optional[Tuple[Path, Dict]]:
    """
    Find most recent previous version with completed literature research.

    Args:
        current_dir: Current manuscript directory

    Returns:
        Tuple of (version_path, state_dict) or None if not found
    """
    parent_dir = current_dir.parent
    current_dir = current_dir.resolve()

    # Find all sibling directories with .rrwrite/state.json
    candidates = []

    for sibling in parent_dir.glob("*/"):
        sibling = sibling.resolve()

        # Skip current directory
        if sibling == current_dir:
            continue

        # Check for state file
        state_file = sibling / ".rrwrite" / "state.json"
        if not state_file.exists():
            continue

        # Load state
        try:
            with open(state_file, "r") as f:
                state = json.load(f)
        except Exception:
            continue

        # Check if research phase completed
        research_status = state.get("workflow_status", {}).get("research", {})
        if research_status.get("status") == "completed":
            created_at = state.get("created_at", "")
            papers_found = research_status.get("papers_found", 0)

            if papers_found > 0:
                candidates.append((sibling, state, created_at))

    # Return most recent by creation date
    if candidates:
        candidates.sort(key=lambda x: x[2], reverse=True)
        return candidates[0][0], candidates[0][1]

    return None


def validate_source_evidence(source_dir: Path) -> Tuple[bool, str]:
    """
    Validate that source directory has required evidence files.

    Args:
        source_dir: Source manuscript directory

    Returns:
        Tuple of (is_valid, error_message)
    """
    required_files = [
        "literature_evidence.csv",
        "literature_citations.bib",
        "literature.md"
    ]

    missing_files = []
    for filename in required_files:
        file_path = source_dir / filename
        if not file_path.exists():
            missing_files.append(filename)

    if missing_files:
        return False, f"Missing files: {', '.join(missing_files)}"

    return True, ""


def import_evidence(
    source_dir: Path,
    target_dir: Path,
    validate: bool = True,
    timeout: int = 5
) -> Dict:
    """
    Import and validate evidence from source to target directory.

    Args:
        source_dir: Source manuscript directory
        target_dir: Target manuscript directory
        validate: Whether to validate DOIs
        timeout: HTTP request timeout for validation

    Returns:
        Dictionary with import results and statistics
    """
    # Validate source
    is_valid, error_msg = validate_source_evidence(source_dir)
    if not is_valid:
        print(f"Error: {error_msg}", file=sys.stderr)
        sys.exit(1)

    # Create target directory if needed
    target_dir.mkdir(parents=True, exist_ok=True)

    # Import files
    results = {
        "source_dir": str(source_dir),
        "target_dir": str(target_dir),
        "timestamp": datetime.now().isoformat(),
        "git_commit": get_git_commit(),
        "files_imported": [],
        "validation_summary": {}
    }

    # Copy literature.md
    shutil.copy2(
        source_dir / "literature.md",
        target_dir / "literature.md"
    )
    results["files_imported"].append("literature.md")

    # Validate and import evidence CSV
    if validate:
        print("Validating evidence DOIs...")
        # Import validation function
        sys.path.insert(0, str(Path(__file__).parent))
        from rrwrite_validate_evidence_tool import validate_evidence_file, generate_validation_summary

        # Validate
        validation_df = validate_evidence_file(
            source_dir / "literature_evidence.csv",
            validate_dois=True,
            check_freshness_flag=True,
            timeout=timeout
        )

        # Filter out papers to remove
        valid_df = validation_df[validation_df["action"] != "remove"].copy()

        # Drop validation columns before saving
        cols_to_drop = ["doi_status", "freshness", "action", "reason"]
        valid_df = valid_df.drop(columns=cols_to_drop)

        # Save validated evidence
        valid_df.to_csv(target_dir / "literature_evidence.csv", index=False)

        # Generate summary
        summary = generate_validation_summary(validation_df)
        results["validation_summary"] = summary

        # Save full validation report
        validation_df.to_csv(
            target_dir / "literature_evidence_validation.csv",
            index=False
        )

        print(f"✓ Imported {len(valid_df)} of {len(validation_df)} papers")
        print(f"  Valid: {summary['valid_papers']}")
        print(f"  Needs review: {summary['needs_review']}")
        print(f"  Removed (invalid DOI): {summary['to_remove']}")

    else:
        # Copy without validation
        shutil.copy2(
            source_dir / "literature_evidence.csv",
            target_dir / "literature_evidence.csv"
        )
        # Count papers
        df = pd.read_csv(source_dir / "literature_evidence.csv")
        results["validation_summary"] = {
            "total_papers": len(df),
            "valid_papers": len(df),
            "needs_review": 0,
            "to_remove": 0,
            "validation_skipped": True
        }

    results["files_imported"].append("literature_evidence.csv")

    # Import citations.bib (filter to match valid evidence)
    import_citations_bib(
        source_dir / "literature_citations.bib",
        target_dir / "literature_evidence.csv",
        target_dir / "literature_citations.bib"
    )
    results["files_imported"].append("literature_citations.bib")

    return results


def import_citations_bib(
    source_bib: Path,
    evidence_csv: Path,
    target_bib: Path
) -> None:
    """
    Import .bib file, filtering to citation keys in evidence CSV.

    Args:
        source_bib: Source .bib file
        evidence_csv: Evidence CSV (used to filter citations)
        target_bib: Target .bib file
    """
    # Read valid citation keys from evidence
    df = pd.read_csv(evidence_csv)
    valid_keys = set(df["citation_key"].unique())

    # Read .bib file
    with open(source_bib, "r") as f:
        bib_content = f.read()

    # Parse entries (simple parser)
    entries = []
    current_entry = []
    in_entry = False

    for line in bib_content.split("\n"):
        if line.startswith("@"):
            # Start of new entry
            if current_entry:
                entries.append("\n".join(current_entry))
            current_entry = [line]
            in_entry = True
        elif in_entry:
            current_entry.append(line)
            if line.strip() == "}":
                # End of entry
                entries.append("\n".join(current_entry))
                current_entry = []
                in_entry = False

    # Filter entries by citation key
    filtered_entries = []
    for entry in entries:
        # Extract citation key (first line: @type{key,)
        first_line = entry.split("\n")[0]
        if "{" in first_line:
            key = first_line.split("{")[1].split(",")[0].strip()
            if key in valid_keys:
                filtered_entries.append(entry)

    # Write filtered .bib
    with open(target_bib, "w") as f:
        f.write("\n\n".join(filtered_entries))


def generate_provenance_metadata(
    source_dir: Path,
    target_dir: Path,
    import_results: Dict,
    source_state: Dict
) -> Dict:
    """
    Generate provenance metadata for the import.

    Args:
        source_dir: Source manuscript directory
        target_dir: Target manuscript directory
        import_results: Results from import_evidence()
        source_state: Source version state.json

    Returns:
        Provenance metadata dictionary
    """
    metadata = {
        "version": "1.0",
        "created": datetime.now().isoformat(),
        "source_version": str(source_dir),
        "source_git_commit": source_state.get("git_commit"),
        "target_git_commit": import_results.get("git_commit"),
        "validation_summary": {
            "papers_total_in_source": import_results["validation_summary"]["total_papers"],
            "papers_imported": import_results["validation_summary"]["valid_papers"],
            "papers_removed": import_results["validation_summary"]["to_remove"],
            "papers_need_review": import_results["validation_summary"]["needs_review"],
            "validation_timestamp": import_results["timestamp"]
        },
        "files_imported": import_results["files_imported"]
    }

    return metadata


def merge_evidence(
    old_csv: Path,
    new_csv: Path,
    output_csv: Path
) -> Dict:
    """
    Merge old (imported) and new (fresh search) evidence.

    Deduplicates by DOI, keeping the newest evidence quote.

    Args:
        old_csv: Old evidence CSV (imported from previous version)
        new_csv: New evidence CSV (from fresh literature search)
        output_csv: Output merged CSV

    Returns:
        Dictionary with merge statistics
    """
    # Load CSVs
    old_df = pd.read_csv(old_csv)
    new_df = pd.read_csv(new_csv)

    # Tag source
    old_df["source"] = "previous"
    new_df["source"] = "new"

    # Combine
    combined_df = pd.concat([old_df, new_df], ignore_index=True)

    # Deduplicate by DOI (keep first occurrence, which is from old)
    # But if we want newest, we need to reverse
    # Actually, let's keep new over old if DOI matches
    combined_df = combined_df.drop_duplicates(subset=["doi"], keep="last")

    # Count statistics
    stats = {
        "papers_old": len(old_df),
        "papers_new": len(new_df),
        "papers_merged": len(combined_df),
        "duplicates_removed": len(old_df) + len(new_df) - len(combined_df),
        "from_previous": len(combined_df[combined_df["source"] == "previous"]),
        "from_new_search": len(combined_df[combined_df["source"] == "new"])
    }

    # Drop source column before saving
    combined_df = combined_df.drop(columns=["source"])

    # Save
    combined_df.to_csv(output_csv, index=False)

    return stats


def display_detection_info(version_path: Path, state: Dict) -> None:
    """Display information about detected previous version."""
    research = state.get("workflow_status", {}).get("research", {})

    print("\n" + "=" * 60)
    print("✓ Detected previous version:")
    print("=" * 60)
    print(f"Path: {version_path}")
    print(f"Created: {state.get('created_at', 'unknown')}")
    print(f"Papers: {research.get('papers_found', 0)}")
    print(f"Status: Research completed")

    if research.get("source_version"):
        print(f"(This version already imported from: {research['source_version']})")

    print("=" * 60)
    print("\nReuse literature from previous version as starting point?")
    print("This will:")
    print("  - Import literature review and citations")
    print("  - Validate all DOIs (check if still accessible)")
    print("  - Allow you to expand with new recent papers")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Import literature evidence from previous manuscript versions"
    )
    parser.add_argument(
        "--target-dir",
        type=Path,
        help="Target manuscript directory (current version)"
    )
    parser.add_argument(
        "--source",
        type=Path,
        help="Source manuscript directory (previous version, optional - auto-detected if not provided)"
    )
    parser.add_argument(
        "--detect-only",
        action="store_true",
        help="Only detect previous version, don't import"
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        default=True,
        help="Validate DOIs (default: true)"
    )
    parser.add_argument(
        "--no-validate",
        action="store_true",
        help="Skip DOI validation"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=5,
        help="HTTP request timeout in seconds (default: 5)"
    )
    parser.add_argument(
        "--merge",
        action="store_true",
        help="Merge mode: combine old and new evidence"
    )
    parser.add_argument(
        "--old",
        type=Path,
        help="Old evidence CSV (for merge mode)"
    )
    parser.add_argument(
        "--new",
        type=Path,
        help="New evidence CSV (for merge mode)"
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output merged CSV (for merge mode)"
    )

    args = parser.parse_args()

    # Merge mode
    if args.merge:
        if not all([args.old, args.new, args.output]):
            print("Error: --merge requires --old, --new, and --output", file=sys.stderr)
            sys.exit(1)

        print(f"Merging evidence from {args.old} and {args.new}...")
        stats = merge_evidence(args.old, args.new, args.output)

        print("\n" + "=" * 60)
        print("MERGE COMPLETE")
        print("=" * 60)
        print(f"Papers from previous version: {stats['from_previous']}")
        print(f"Papers from new search: {stats['from_new_search']}")
        print(f"Duplicates removed: {stats['duplicates_removed']}")
        print(f"Total merged papers: {stats['papers_merged']}")
        print("=" * 60)
        print(f"\nMerged evidence saved to: {args.output}")

        sys.exit(0)

    # Import mode
    if not args.target_dir:
        print("Error: --target-dir required", file=sys.stderr)
        sys.exit(1)

    target_dir = args.target_dir.resolve()

    # Detect or use provided source
    if args.source:
        source_dir = args.source.resolve()

        # Load source state
        source_state_file = source_dir / ".rrwrite" / "state.json"
        if not source_state_file.exists():
            print(f"Error: Source state file not found: {source_state_file}", file=sys.stderr)
            sys.exit(1)

        with open(source_state_file, "r") as f:
            source_state = json.load(f)

    else:
        # Auto-detect
        result = detect_previous_version(target_dir)

        if result is None:
            print("No previous version with completed research found.")
            sys.exit(0)

        source_dir, source_state = result

    # Display detection info
    display_detection_info(source_dir, source_state)

    # Detect-only mode
    if args.detect_only:
        sys.exit(0)

    # Import
    validate_dois = not args.no_validate

    print("\nImporting evidence...")
    import_results = import_evidence(
        source_dir,
        target_dir,
        validate=validate_dois,
        timeout=args.timeout
    )

    # Generate provenance metadata
    metadata = generate_provenance_metadata(
        source_dir,
        target_dir,
        import_results,
        source_state
    )

    # Save metadata
    metadata_file = target_dir / "literature_evidence_metadata.json"
    with open(metadata_file, "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"\n✓ Provenance metadata saved to: {metadata_file}")

    # Summary
    print("\n" + "=" * 60)
    print("IMPORT COMPLETE")
    print("=" * 60)
    print(f"Source: {source_dir.name}")
    print(f"Target: {target_dir}")
    print(f"Papers imported: {import_results['validation_summary']['valid_papers']}")
    if validate_dois:
        print(f"Papers removed (invalid DOI): {import_results['validation_summary']['to_remove']}")
        print(f"Papers needing review: {import_results['validation_summary']['needs_review']}")
    print("=" * 60)


if __name__ == "__main__":
    main()
