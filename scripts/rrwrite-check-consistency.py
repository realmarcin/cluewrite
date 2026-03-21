#!/usr/bin/env python3
"""
Check manuscript consistency and generate report.
"""

import argparse
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPTS_DIR))

from rrwrite_consistency_checker import ConsistencyChecker


def main():
    parser = argparse.ArgumentParser(
        description="Check manuscript consistency",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check all consistency issues
  %(prog)s --manuscript-dir manuscript/project_v1

  # Check specific types
  %(prog)s --manuscript-dir manuscript/project_v1 --check terminology,citations

  # Custom output location
  %(prog)s --manuscript-dir manuscript/project_v1 --output consistency_check.md
        """
    )

    parser.add_argument(
        "--manuscript-dir",
        type=Path,
        required=True,
        help="Path to manuscript directory"
    )

    parser.add_argument(
        "--check",
        help="Comma-separated list of checks (terminology,citations,figures,tables,abbreviations). Default: all"
    )

    parser.add_argument(
        "--output",
        type=Path,
        help="Output path for report (default: manuscript_dir/consistency_report.md)"
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Also output JSON report"
    )

    args = parser.parse_args()

    if not args.manuscript_dir.exists():
        print(f"✗ Manuscript directory not found: {args.manuscript_dir}")
        return 1

    print(f"Checking manuscript consistency in {args.manuscript_dir}...")

    checker = ConsistencyChecker(args.manuscript_dir)

    # Run checks
    if args.check:
        check_types = [c.strip() for c in args.check.split(',')]
        issues = []

        for check_type in check_types:
            print(f"  Running {check_type} check...")
            if check_type == "terminology":
                issues.extend(checker.check_terminology())
            elif check_type == "citations":
                issues.extend(checker.check_citation_style())
            elif check_type == "figures":
                issues.extend(checker.check_figure_numbering())
            elif check_type == "tables":
                issues.extend(checker.check_table_numbering())
            elif check_type == "abbreviations":
                issues.extend(checker.check_abbreviations())
            else:
                print(f"  ⚠ Unknown check type: {check_type}")

        checker.issues = issues
    else:
        print("  Running all checks...")
        issues = checker.check_all()

    print(f"\n✓ Found {len(issues)} consistency issues")

    # Print summary
    if issues:
        by_severity = {}
        for issue in issues:
            severity = issue['severity']
            by_severity[severity] = by_severity.get(severity, 0) + 1

        print("\nBy severity:")
        for severity in ["critical", "major", "minor"]:
            if severity in by_severity:
                print(f"  {severity.title()}: {by_severity[severity]}")

    # Generate report
    if not args.output:
        args.output = args.manuscript_dir / "consistency_report.md"

    checker.generate_report(args.output)
    print(f"\n✓ Markdown report: {args.output}")

    # JSON output
    if args.json:
        import json
        json_path = args.output.with_suffix('.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump({"issues": issues}, f, indent=2)
        print(f"✓ JSON report: {json_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
