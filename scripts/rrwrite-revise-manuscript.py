#!/usr/bin/env python3
"""
RRWrite Manuscript Reviser

Orchestrates automated revision of manuscript based on critique reports.
Iteratively addresses issues using specialized section revisers with convergence detection.

Usage:
    python scripts/rrwrite-revise-manuscript.py --manuscript-dir manuscript/repo_v1
    python scripts/rrwrite-revise-manuscript.py --manuscript-dir manuscript/repo_v1 --max-iterations 3
    python scripts/rrwrite-revise-manuscript.py --manuscript-dir manuscript/repo_v1 --dry-run
"""

import sys
import subprocess
from pathlib import Path
from typing import List, Dict, Optional
import logging
import argparse

# Import revision components
try:
    from rrwrite_revision_parser import CritiqueParser, Issue
    from rrwrite_revision_context import RevisionContext
    from rrwrite_section_reviser import get_reviser
    from rrwrite_state_manager import StateManager
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent))
    from rrwrite_revision_parser import CritiqueParser, Issue
    from rrwrite_revision_context import RevisionContext
    from rrwrite_section_reviser import get_reviser
    from rrwrite_state_manager import StateManager


class RevisionOrchestrator:
    """Manages the iterative revision loop."""

    def __init__(
        self,
        manuscript_dir: Path,
        max_revisions: int = 2,
        min_improvement: float = 0.05,
        dry_run: bool = False
    ):
        """Initialize revision orchestrator.

        Args:
            manuscript_dir: Path to manuscript directory
            max_revisions: Maximum number of revision iterations
            min_improvement: Minimum improvement rate to continue (default: 5%)
            dry_run: If True, don't save changes or commit
        """
        self.manuscript_dir = Path(manuscript_dir).resolve()
        self.max_revisions = max_revisions
        self.min_improvement = min_improvement
        self.dry_run = dry_run
        self.logger = logging.getLogger(__name__)

        # Initialize components
        self.state_manager = StateManager(output_dir=self.manuscript_dir, enable_git=not dry_run)
        self.critique_parser = CritiqueParser(self.manuscript_dir)
        self.context = RevisionContext(self.manuscript_dir)

        # Track current version
        self.current_version = 1

    def run_revision_loop(self):
        """Main revision loop: parse → revise → validate → critique → converge."""

        print(f"\n{'='*60}")
        print(f"Starting Automated Revision")
        print(f"{'='*60}")
        print(f"Manuscript: {self.manuscript_dir}")
        print(f"Max iterations: {self.max_revisions}")
        print(f"Min improvement: {self.min_improvement*100}%")
        if self.dry_run:
            print("DRY RUN - No changes will be saved")
        print(f"{'='*60}\n")

        # Initialize revision state
        if not self.dry_run:
            self.state_manager.start_revision(self.max_revisions)

        # Main iteration loop
        for iteration in range(1, self.max_revisions + 1):
            print(f"\n{'='*60}")
            print(f"REVISION ITERATION {iteration}/{self.max_revisions}")
            print(f"{'='*60}\n")

            # Step 1: Parse critique reports
            print(f"Parsing critique reports (version {self.current_version})...")
            issues = self.critique_parser.parse_critique_reports(version=self.current_version)

            if not issues:
                print("✗ No critique reports found. Run critique first.")
                return

            # Infer sections
            issues = self.critique_parser.infer_all_sections(issues)

            # Count issues before
            metrics_before = self.critique_parser.count_issues(issues)
            print(f"Found {metrics_before['major']} major issues, {metrics_before['minor']} minor issues")

            # Step 2: Check if already converged
            if metrics_before['major'] == 0:
                print(f"\n✓ All major issues resolved!")
                if not self.dry_run:
                    self.state_manager.complete_revision("converged", "major_issues_resolved")
                return

            # Step 3: Map issues to sections
            print(f"\nMapping issues to sections...")
            section_issue_map = self.critique_parser.group_by_section(issues)

            for section, section_issues in section_issue_map.items():
                major = sum(1 for i in section_issues if i.severity == "major")
                minor = sum(1 for i in section_issues if i.severity == "minor")
                print(f"  - {section}: {major} major, {minor} minor")

            # Step 4: Revise sections
            print(f"\nRevising sections...")
            sections_revised = []

            for section, section_issues in section_issue_map.items():
                # Skip manuscript_full (cross-cutting issues)
                if section == "manuscript_full":
                    print(f"  ⊘ Skipping manuscript_full (cross-cutting issues)")
                    continue

                # Get section file
                section_file = self.manuscript_dir / f"{section}.md"

                if not section_file.exists():
                    print(f"  ✗ Section file not found: {section}.md")
                    continue

                # Create reviser
                reviser = get_reviser(section, section_file, section_issues, self.context)

                # Revise
                print(f"  Revising {section}...", end=" ")
                result = reviser.revise()

                if result.success:
                    print(f"✓ ({len(result.changes_made)} changes)")

                    # Save if not dry run
                    if not self.dry_run and result.validation.passed:
                        with open(section_file, 'w', encoding='utf-8') as f:
                            f.write(result.content)
                        sections_revised.append(section)
                    elif self.dry_run:
                        sections_revised.append(section)
                        print(f"    (Dry run - not saved)")

                    # Show changes
                    for change in result.changes_made[:3]:  # Show first 3
                        print(f"    - {change}")
                    if len(result.changes_made) > 3:
                        print(f"    ... and {len(result.changes_made) - 3} more")

                else:
                    print(f"✗ Validation failed")
                    for error in result.validation.errors:
                        print(f"    ERROR: {error}")

            if not sections_revised:
                print(f"\n⚠ No sections were successfully revised")
                if not self.dry_run:
                    self.state_manager.complete_revision("stalled", "no_sections_revised")
                return

            # Step 5: Re-assemble manuscript
            print(f"\nRe-assembling manuscript...")
            if not self.dry_run:
                try:
                    self._run_assembly()
                    print(f"  ✓ Manuscript assembled")
                except Exception as e:
                    print(f"  ✗ Assembly failed: {e}")
                    return
            else:
                print(f"  (Dry run - skipping assembly)")

            # Step 6: Re-run critique
            self.current_version += 1
            print(f"\nRe-running critique (version {self.current_version})...")

            if not self.dry_run:
                try:
                    self._run_critique(self.current_version)
                    print(f"  ✓ Critique complete")
                except Exception as e:
                    print(f"  ✗ Critique failed: {e}")
                    return
            else:
                print(f"  (Dry run - skipping critique)")

            # Step 7: Parse new critique
            if not self.dry_run:
                new_issues = self.critique_parser.parse_critique_reports(version=self.current_version)
                new_issues = self.critique_parser.infer_all_sections(new_issues)
                metrics_after = self.critique_parser.count_issues(new_issues)
            else:
                # In dry run, assume improvement
                metrics_after = {
                    'major': max(0, metrics_before['major'] - len(sections_revised)),
                    'minor': max(0, metrics_before['minor'] - len(sections_revised))
                }

            # Step 8: Calculate improvement
            major_resolved = metrics_before['major'] - metrics_after['major']
            improvement_rate = major_resolved / metrics_before['major'] if metrics_before['major'] > 0 else 0.0

            print(f"\nAfter revision:")
            print(f"  Major issues: {metrics_before['major']} → {metrics_after['major']} ({major_resolved} resolved)")
            print(f"  Minor issues: {metrics_before['minor']} → {metrics_after['minor']}")
            print(f"  Improvement rate: {improvement_rate*100:.1f}%")

            # Step 9: Update state
            if not self.dry_run:
                critique_files = {
                    "content": f"critique_content_v{self.current_version}.md",
                    "format": f"critique_format_v{self.current_version}.md"
                }
                self.state_manager.update_revision_iteration(
                    iteration=iteration,
                    sections_revised=sections_revised,
                    metrics_before=metrics_before,
                    metrics_after=metrics_after,
                    critique_files=critique_files
                )

            # Step 10: Check convergence
            should_stop, reason = self.state_manager.check_revision_convergence(
                metrics_after=metrics_after,
                iteration=iteration,
                max_revisions=self.max_revisions,
                improvement_rate=improvement_rate,
                min_improvement=self.min_improvement
            )

            # Step 11: Git commit
            if not self.dry_run:
                self._git_commit_iteration(iteration, metrics_before, metrics_after)

            # Check if should stop
            if should_stop:
                print(f"\n{'='*60}")
                print(f"Revision converged: {reason}")
                print(f"{'='*60}\n")

                if not self.dry_run:
                    convergence_status = "converged" if reason == "major_issues_resolved" else "stalled"
                    self.state_manager.complete_revision(convergence_status, reason)

                break

        # Print final summary
        self._print_summary()

    def _run_assembly(self):
        """Re-assemble manuscript after revisions."""
        assembly_script = Path(__file__).parent / "rrwrite-assemble-manuscript.py"

        cmd = [
            sys.executable,
            str(assembly_script),
            "--manuscript-dir", str(self.manuscript_dir),
            "--no-critique"  # Don't re-run critique, we'll do it separately
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            raise Exception(f"Assembly failed: {result.stderr}")

    def _run_critique(self, version: int):
        """Re-run critique on updated manuscript."""
        # Run content critique
        content_script = Path(__file__).parent / "rrwrite-critique-content.py"
        content_output = self.manuscript_dir / f"critique_content_v{version}.md"

        cmd_content = [
            sys.executable,
            str(content_script),
            "--file", str(self.manuscript_dir / "manuscript_full.md"),
            "--output", str(content_output)
        ]

        result = subprocess.run(cmd_content, capture_output=True, text=True)

        # Note: critique scripts return exit code 1 when issues found (expected behavior)
        # Only treat as error if output file wasn't created
        if not content_output.exists():
            error_msg = result.stderr if result.stderr else result.stdout
            raise Exception(f"Content critique failed: {error_msg}")

        # Run format critique
        format_script = Path(__file__).parent / "rrwrite-critique-format.py"
        format_output = self.manuscript_dir / f"critique_format_v{version}.md"

        cmd_format = [
            sys.executable,
            str(format_script),
            "--file", str(self.manuscript_dir / "manuscript_full.md"),
            "--output", str(format_output)
        ]

        result = subprocess.run(cmd_format, capture_output=True, text=True)

        # Note: critique scripts return exit code 1 when issues found (expected behavior)
        # Only treat as error if output file wasn't created
        if not format_output.exists():
            error_msg = result.stderr if result.stderr else result.stdout
            raise Exception(f"Format critique failed: {error_msg}")

    def _git_commit_iteration(self, iteration: int, metrics_before: Dict, metrics_after: Dict):
        """Commit iteration changes to git."""
        major_resolved = metrics_before['major'] - metrics_after['major']
        minor_resolved = metrics_before['minor'] - metrics_after['minor']

        description = f"Revision iteration {iteration}"
        metadata = {
            "major_resolved": major_resolved,
            "minor_resolved": minor_resolved,
            "major_remaining": metrics_after['major'],
            "minor_remaining": metrics_after['minor']
        }

        # Commit all files
        files = [
            "*.md",
            ".rrwrite/state.json"
        ]

        self.state_manager.commit_stage(
            files=files,
            stage=f"revision_iter_{iteration}",
            description=description,
            **metadata
        )

    def _print_summary(self):
        """Print final revision summary."""
        if self.dry_run:
            print("\n(Dry run - no changes saved)")
            return

        summary = self.state_manager.get_revision_summary()

        if summary["status"] == "not_started":
            return

        print(f"\n{'='*60}")
        print(f"REVISION SUMMARY")
        print(f"{'='*60}")
        print(f"Total iterations: {summary['iterations']}")

        if summary['iterations'] > 0:
            print(f"\nIssues resolved:")
            print(f"  Major: {summary['issues_initial']['major']} → {summary['issues_final']['major']} ({summary['total_major_resolved']} resolved)")
            print(f"  Minor: {summary['issues_initial']['minor']} → {summary['issues_final']['minor']} ({summary['total_minor_resolved']} resolved)")

            print(f"\nConvergence: {summary['convergence_reason']}")

            if summary['issues_final']['major'] == 0:
                print(f"\n✓ All major issues resolved!")
            else:
                print(f"\n⚠ {summary['issues_final']['major']} major issues remaining")

        print(f"{'='*60}\n")


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Automated manuscript revision based on critique reports",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Default: 2 iterations, auto mode
  python scripts/rrwrite-revise-manuscript.py --manuscript-dir manuscript/repo_v1

  # Custom iterations
  python scripts/rrwrite-revise-manuscript.py --manuscript-dir manuscript/repo_v1 --max-iterations 3

  # Dry run (show planned revisions)
  python scripts/rrwrite-revise-manuscript.py --manuscript-dir manuscript/repo_v1 --dry-run

  # Custom improvement threshold
  python scripts/rrwrite-revise-manuscript.py --manuscript-dir manuscript/repo_v1 --min-improvement 0.10
        """
    )

    parser.add_argument(
        "--manuscript-dir",
        required=True,
        help="Manuscript directory containing critique reports"
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=2,
        help="Maximum number of revision iterations (default: 2)"
    )
    parser.add_argument(
        "--min-improvement",
        type=float,
        default=0.05,
        help="Minimum improvement rate to continue (default: 0.05 = 5%%)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show planned revisions without saving changes"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose output"
    )

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format='%(levelname)s: %(message)s'
    )

    # Validate manuscript directory
    manuscript_dir = Path(args.manuscript_dir)
    if not manuscript_dir.exists():
        print(f"✗ Manuscript directory not found: {manuscript_dir}")
        sys.exit(1)

    # Check for critique reports
    critique_v1_content = manuscript_dir / "critique_content_v1.md"
    critique_v1_format = manuscript_dir / "critique_format_v1.md"

    if not critique_v1_content.exists() and not critique_v1_format.exists():
        print(f"✗ No critique reports found in {manuscript_dir}")
        print(f"  Run critique first: python scripts/rrwrite-critique-manuscript.py --manuscript-dir {manuscript_dir}")
        sys.exit(1)

    # Create orchestrator
    orchestrator = RevisionOrchestrator(
        manuscript_dir=manuscript_dir,
        max_revisions=args.max_iterations,
        min_improvement=args.min_improvement,
        dry_run=args.dry_run
    )

    # Run revision loop
    try:
        orchestrator.run_revision_loop()
    except KeyboardInterrupt:
        print("\n\n✗ Revision interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Revision failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
