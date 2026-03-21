#!/usr/bin/env python3
"""
Unified critique wrapper - calls both content and format review.

This script orchestrates the two-stage review process:
1. Content review (rrwrite-critique-content.py) - scientific validity
2. Format review (rrwrite-critique-format.py) - citation/structure compliance

Usage:
    python scripts/rrwrite-critique-manuscript.py --manuscript-dir manuscript/MicroGrowAgents_v6
"""

import argparse
import subprocess
import sys
from pathlib import Path


def run_critique(manuscript_dir: Path, version: int = 1, journal: str = None) -> bool:
    """
    Run both content and format critique on manuscript.

    Args:
        manuscript_dir: Directory containing full_manuscript.md
        version: Critique version number (default: 1)
        journal: Target journal for format compliance (optional)

    Returns:
        True if both critiques succeeded
    """
    manuscript_file = manuscript_dir / "full_manuscript.md"

    if not manuscript_file.exists():
        print(f"✗ Manuscript not found: {manuscript_file}")
        return False

    # Define output files
    content_output = manuscript_dir / f"critique_content_v{version}.md"
    format_output = manuscript_dir / f"critique_format_v{version}.md"

    scripts_dir = Path(__file__).parent

    # Run content critique
    print(f"Running content review (v{version})...")
    content_script = scripts_dir / "rrwrite-critique-content.py"

    if not content_script.exists():
        print(f"✗ Content script not found: {content_script}")
        return False

    try:
        cmd = [
            sys.executable,
            str(content_script),
            '--file', str(manuscript_file),
            '--output', str(content_output)
        ]

        # Note: critique scripts exit with code 1 if issues found, which is expected
        result = subprocess.run(cmd, capture_output=True, text=True)

        # Print the output (includes issue counts)
        if result.stdout:
            print(result.stdout.strip())

        # Only fail if critique file wasn't created
        if not content_output.exists():
            print(f"✗ Content review failed - output not created")
            if result.stderr:
                print(result.stderr)
            return False

    except Exception as e:
        print(f"✗ Error running content review: {e}")
        return False

    # Run format critique
    print(f"Running format review (v{version})...")
    format_script = scripts_dir / "rrwrite-critique-format.py"

    if not format_script.exists():
        print(f"✗ Format script not found: {format_script}")
        return False

    try:
        cmd = [
            sys.executable,
            str(format_script),
            '--file', str(manuscript_file),
            '--output', str(format_output)
        ]

        # Add journal parameter if provided
        if journal:
            cmd.extend(['--journal', journal])

        # Note: critique scripts exit with code 1 if issues found, which is expected
        result = subprocess.run(cmd, capture_output=True, text=True)

        # Print the output (includes issue counts)
        if result.stdout:
            print(result.stdout.strip())

        # Only fail if critique file wasn't created
        if not format_output.exists():
            print(f"✗ Format review failed - output not created")
            if result.stderr:
                print(result.stderr)
            return False

    except Exception as e:
        print(f"✗ Error running format review: {e}")
        return False

    # Summary
    print(f"\n✓ Critique v{version} completed")
    print(f"  Content: {content_output.name}")
    print(f"  Format: {format_output.name}")

    return True


def main():
    parser = argparse.ArgumentParser(
        description='Unified manuscript critique (content + format review)'
    )
    parser.add_argument(
        '--manuscript-dir',
        type=Path,
        required=True,
        help='Directory containing full_manuscript.md'
    )
    parser.add_argument(
        '--version',
        type=int,
        default=1,
        help='Critique version number (default: 1)'
    )
    parser.add_argument(
        '--journal',
        choices=['nature', 'plos', 'bioinformatics'],
        help='Target journal for format compliance'
    )

    args = parser.parse_args()

    success = run_critique(args.manuscript_dir, args.version, args.journal)

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
