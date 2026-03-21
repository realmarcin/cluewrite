#!/usr/bin/env python3
"""
Generate structured comparison reports between manuscript versions.

This script compares two versions of a manuscript and generates both
JSON (machine-readable) and Markdown (human-readable) diff reports.
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

# Add scripts directory to path
SCRIPTS_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPTS_DIR))

from rrwrite_diff_generator import DiffReportGenerator, validate_diff_report
from rrwrite_issue_resolver import IssueResolver


def generate_markdown_report(diff_report: dict, output_path: Path) -> None:
    """
    Generate human-readable Markdown diff report.

    Args:
        diff_report: Diff report dictionary
        output_path: Path to output .md file
    """
    md_lines = []

    # Header
    md_lines.append(f"# Manuscript Comparison Report")
    md_lines.append("")
    md_lines.append(f"**Version:** {diff_report['metadata']['version_old']} → {diff_report['metadata']['version_new']}")
    md_lines.append(f"**Type:** {diff_report['metadata']['comparison_type']}")
    md_lines.append(f"**Generated:** {diff_report['metadata']['timestamp']}")
    md_lines.append("")

    # Summary
    md_lines.append("## Summary")
    md_lines.append("")
    summary = diff_report['summary']
    md_lines.append(f"- **Total changes:** {summary['total_changes']}")
    md_lines.append(f"- **Sections modified:** {summary['sections_modified']}")
    md_lines.append(f"- **Citations added:** {summary['citations_added']}")
    md_lines.append(f"- **Citations removed:** {summary['citations_removed']}")
    md_lines.append(f"- **Word count delta:** {summary['word_count_delta']:+d}")
    md_lines.append(f"- **Issues resolved:** {summary.get('issues_resolved', 0)}")
    md_lines.append(f"- **Issues remaining:** {summary.get('issues_remaining', 0)}")
    md_lines.append("")

    # Metrics (if available)
    if diff_report.get('metrics'):
        metrics = diff_report['metrics']
        md_lines.append("## Progress Metrics")
        md_lines.append("")
        md_lines.append(f"- **Improvement rate:** {metrics.get('improvement_rate', 0):.1%}")
        md_lines.append(f"- **Quality score (old):** {metrics.get('quality_score_old', 0):.2f}")
        md_lines.append(f"- **Quality score (new):** {metrics.get('quality_score_new', 0):.2f}")
        md_lines.append(f"- **Convergence:** {metrics.get('convergence_indicator', 'unknown')}")
        md_lines.append("")

    # Section Changes
    md_lines.append("## Section Changes")
    md_lines.append("")

    for section in diff_report['sections']:
        if section['status'] == 'unchanged':
            continue

        md_lines.append(f"### {section['section_name'].title()}")
        md_lines.append("")
        md_lines.append(f"**Status:** {section['status']}")
        md_lines.append("")

        changes = section['changes']
        md_lines.append(f"- Lines added: {changes['additions']}")
        md_lines.append(f"- Lines deleted: {changes['deletions']}")
        md_lines.append(f"- Lines modified: {changes['modifications']}")
        md_lines.append(f"- Word count: {changes['word_count_old']} → {changes['word_count_new']} ({changes['word_count_delta']:+d})")
        md_lines.append(f"- Similarity: {changes['similarity_score']:.1%}")
        md_lines.append("")

        if section.get('notable_changes'):
            md_lines.append("**Notable changes:**")
            md_lines.append("")
            for change in section['notable_changes']:
                md_lines.append(f"- {change}")
            md_lines.append("")

    # Citation Changes
    md_lines.append("## Citation Changes")
    md_lines.append("")

    citations = diff_report['citations']

    if citations['added']:
        md_lines.append("### Added Citations")
        md_lines.append("")
        for cite in citations['added']:
            md_lines.append(f"- **{cite['citation_key']}** ({cite['section']})")
            if cite.get('context'):
                md_lines.append(f"  - Context: {cite['context']}")
        md_lines.append("")

    if citations['removed']:
        md_lines.append("### Removed Citations")
        md_lines.append("")
        for cite in citations['removed']:
            md_lines.append(f"- **{cite['citation_key']}** ({cite['section']})")
        md_lines.append("")

    # Issue Resolution
    issues = diff_report.get('issues', {})

    if issues.get('resolved'):
        md_lines.append("## Resolved Issues")
        md_lines.append("")
        for issue in issues['resolved']:
            md_lines.append(f"### {issue['issue_id']}")
            md_lines.append("")
            md_lines.append(f"**Description:** {issue['description']}")
            md_lines.append("")
            md_lines.append(f"- **Section:** {issue.get('section', 'N/A')}")
            md_lines.append(f"- **Severity:** {issue.get('severity', 'N/A')}")
            md_lines.append(f"- **Resolution:** {issue.get('resolution_type', 'N/A')}")
            md_lines.append(f"- **Evidence:** {issue.get('evidence', 'N/A')}")
            md_lines.append("")

    if issues.get('persisting'):
        md_lines.append("## Persisting Issues")
        md_lines.append("")
        md_lines.append(f"{len(issues['persisting'])} issues remain unresolved:")
        md_lines.append("")
        for issue in issues['persisting']:
            md_lines.append(f"- [{issue['severity']}] {issue['description']}")
        md_lines.append("")

    if issues.get('new'):
        md_lines.append("## New Issues")
        md_lines.append("")
        md_lines.append(f"{len(issues['new'])} new issues introduced:")
        md_lines.append("")
        for issue in issues['new']:
            md_lines.append(f"- [{issue['severity']}] {issue['description']}")
        md_lines.append("")

    # Write file
    output_path.write_text('\n'.join(md_lines), encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(
        description="Generate comparison report between manuscript versions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Compare revision iterations (v1 → v2 in same directory)
  %(prog)s --manuscript-dir manuscript/project_v1 --version-old 1 --version-new 2 --type revision

  # Compare across versions (different directories)
  %(prog)s --manuscript-dir manuscript/project_v2 --version-old 1 --version-new 1 --type version \\
           --dir-old manuscript/project_v1

  # Compare using git commits
  %(prog)s --manuscript-dir manuscript/project_v1 --version-old 1 --version-new 2 \\
           --git-commit-old abc123 --git-commit-new def456
        """
    )

    parser.add_argument(
        "--manuscript-dir",
        type=Path,
        required=True,
        help="Path to manuscript directory"
    )

    parser.add_argument(
        "--version-old",
        type=int,
        required=True,
        help="Old version number"
    )

    parser.add_argument(
        "--version-new",
        type=int,
        required=True,
        help="New version number"
    )

    parser.add_argument(
        "--type",
        choices=["revision", "version", "manual"],
        default="revision",
        help="Type of comparison (default: revision)"
    )

    parser.add_argument(
        "--git-commit-old",
        help="Git commit hash for old version (optional)"
    )

    parser.add_argument(
        "--git-commit-new",
        help="Git commit hash for new version (optional)"
    )

    parser.add_argument(
        "--dir-old",
        type=Path,
        help="Directory for old version (for cross-version comparison)"
    )

    parser.add_argument(
        "--output-json",
        type=Path,
        help="Output path for JSON report (default: manuscript_dir/diff_report_vX_to_vY.json)"
    )

    parser.add_argument(
        "--output-md",
        type=Path,
        help="Output path for Markdown report (default: manuscript_dir/diff_report_vX_to_vY.md)"
    )

    parser.add_argument(
        "--skip-validation",
        action="store_true",
        help="Skip JSON schema validation"
    )

    args = parser.parse_args()

    # Determine manuscript directory for old version
    if args.type == "version" and args.dir_old:
        manuscript_dir_old = args.dir_old
    else:
        manuscript_dir_old = args.manuscript_dir

    # Initialize generator
    generator = DiffReportGenerator(manuscript_dir_old)

    print(f"Generating diff report: v{args.version_old} → v{args.version_new}")
    print(f"Comparison type: {args.type}")

    # Generate diff report
    diff_report = generator.generate_diff_report(
        args.version_old,
        args.version_new,
        args.type,
        args.git_commit_old,
        args.git_commit_new
    )

    # Enrich with issue tracking (if critiques exist)
    resolver = IssueResolver(args.manuscript_dir)
    try:
        diff_report = resolver.enrich_diff_report_with_issues(
            diff_report,
            args.version_old,
            args.version_new
        )
        print("✓ Enriched with issue tracking data")
    except Exception as e:
        print(f"⚠ Could not enrich with issue data: {e}")

    # Validate against schema
    if not args.skip_validation:
        schema_path = SCRIPTS_DIR.parent / "schemas" / "diff_report_schema.json"
        if schema_path.exists():
            is_valid, errors = validate_diff_report(diff_report, schema_path)
            if is_valid:
                print("✓ Diff report validates against schema")
            else:
                print("✗ Validation errors:")
                for error in errors:
                    print(f"  {error}")
                print("\nProceeding anyway...")

    # Determine output paths
    if not args.output_json:
        args.output_json = args.manuscript_dir / f"diff_report_v{args.version_old}_to_v{args.version_new}.json"

    if not args.output_md:
        args.output_md = args.manuscript_dir / f"diff_report_v{args.version_old}_to_v{args.version_new}.md"

    # Write JSON report
    with open(args.output_json, 'w', encoding='utf-8') as f:
        json.dump(diff_report, f, indent=2)
    print(f"✓ JSON report: {args.output_json}")

    # Write Markdown report
    generate_markdown_report(diff_report, args.output_md)
    print(f"✓ Markdown report: {args.output_md}")

    # Summary
    print("\n" + "=" * 60)
    print("Summary:")
    print(f"  Total changes: {diff_report['summary']['total_changes']}")
    print(f"  Sections modified: {diff_report['summary']['sections_modified']}")
    print(f"  Citations added: {diff_report['summary']['citations_added']}")
    print(f"  Word count delta: {diff_report['summary']['word_count_delta']:+d}")
    if diff_report['summary'].get('issues_resolved') is not None:
        print(f"  Issues resolved: {diff_report['summary']['issues_resolved']}")
        print(f"  Issues remaining: {diff_report['summary']['issues_remaining']}")

    if diff_report.get('metrics'):
        metrics = diff_report['metrics']
        print(f"\nMetrics:")
        print(f"  Improvement rate: {metrics.get('improvement_rate', 0):.1%}")
        print(f"  Convergence: {metrics.get('convergence_indicator', 'unknown')}")

    print("=" * 60)


if __name__ == "__main__":
    main()
