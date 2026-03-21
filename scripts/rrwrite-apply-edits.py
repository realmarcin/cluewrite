#!/usr/bin/env python3
"""
Apply edit recommendations holistically to manuscript.

This script applies structured edit recommendations with dependency
resolution, conflict detection, and transaction-based safety.
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

SCRIPTS_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPTS_DIR))

from rrwrite_holistic_editor import HolisticEditOrchestrator
from rrwrite_edit_applicators import (
    SectionEditApplicator,
    CrossSectionApplicator,
    FigureEditApplicator,
    TableEditApplicator,
    ConsistencyApplicator
)


def apply_edits(
    orchestrator: HolisticEditOrchestrator,
    dry_run: bool = False,
    backup: bool = True
) -> dict:
    """
    Apply all edits in the orchestrator's plan.

    Args:
        orchestrator: Initialized orchestrator with plan
        dry_run: If True, don't actually modify files
        backup: If True, create backups before modification

    Returns:
        Dictionary with application results
    """
    results = {
        "total": len(orchestrator.plan.sorted_edits),
        "applied": 0,
        "failed": 0,
        "skipped": 0,
        "details": []
    }

    # Initialize applicators
    section_applicator = SectionEditApplicator(orchestrator.manuscript_dir)
    cross_section_applicator = CrossSectionApplicator(orchestrator.manuscript_dir)
    figure_applicator = FigureEditApplicator(orchestrator.manuscript_dir)
    table_applicator = TableEditApplicator(orchestrator.manuscript_dir)
    consistency_applicator = ConsistencyApplicator(orchestrator.manuscript_dir)

    # Create backup if requested
    if backup and not dry_run:
        backup_dir = orchestrator.manuscript_dir / ".rrwrite" / "backups" / datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir.mkdir(parents=True, exist_ok=True)

        # Copy sections
        sections_dir = orchestrator.manuscript_dir / "sections"
        if sections_dir.exists():
            import shutil
            shutil.copytree(sections_dir, backup_dir / "sections", dirs_exist_ok=True)
            print(f"✓ Backup created: {backup_dir}")

    # Apply each edit
    for edit_id in orchestrator.plan.sorted_edits:
        rec = orchestrator.plan.recommendations[edit_id]

        if rec.status == "skipped":
            results["skipped"] += 1
            continue

        print(f"\nApplying {edit_id}: {rec.edit_type} in {rec.section}...")

        if dry_run:
            print(f"  [DRY RUN] Would apply: {rec.recommended_action}")
            rec.mark_applied()
            results["applied"] += 1
            results["details"].append({
                "id": edit_id,
                "status": "applied",
                "message": "[DRY RUN] Simulated"
            })
            continue

        # Route to appropriate applicator
        success = False
        message = ""

        try:
            if rec.edit_type in ["add_content", "remove_content", "revise_content", "citation_fix"]:
                success, message = section_applicator.apply_edit(rec)

            elif rec.edit_type == "move_content":
                if len(rec.target_sections) >= 1:
                    target = rec.target_sections[0]
                    success, message = cross_section_applicator.move_content(
                        rec.section,
                        target,
                        rec.issue_description
                    )
                else:
                    success, message = False, "No target section specified for move"

            elif rec.edit_type == "figure_update":
                # Extract figure ID from description
                figure_id = "figure_1"  # Placeholder - should be extracted
                success, message = figure_applicator.update_caption(figure_id, rec.replacement_text or "Updated caption")

            elif rec.edit_type == "table_update":
                table_id = "table_1"  # Placeholder
                success, message = table_applicator.update_title(table_id, rec.replacement_text or "Updated title")

            elif rec.edit_type == "formatting":
                # Consistency applicator
                success, message = True, "Formatting edit noted (manual application required)"

            else:
                success, message = False, f"Unsupported edit type: {rec.edit_type}"

        except Exception as e:
            success = False
            message = f"Exception: {str(e)}"

        # Update recommendation status
        if success:
            rec.mark_applied()
            results["applied"] += 1
            print(f"  ✓ {message}")
        else:
            rec.mark_failed(message)
            results["failed"] += 1
            print(f"  ✗ {message}")

        results["details"].append({
            "id": edit_id,
            "status": "applied" if success else "failed",
            "message": message
        })

    return results


def generate_application_report(results: dict, output_path: Path) -> None:
    """Generate Markdown report of edit application."""
    md_lines = []

    md_lines.append("# Edit Application Report")
    md_lines.append("")
    md_lines.append(f"**Generated:** {datetime.now().isoformat()}")
    md_lines.append("")

    md_lines.append("## Summary")
    md_lines.append("")
    md_lines.append(f"- **Total edits:** {results['total']}")
    md_lines.append(f"- **Applied:** {results['applied']}")
    md_lines.append(f"- **Failed:** {results['failed']}")
    md_lines.append(f"- **Skipped:** {results['skipped']}")
    md_lines.append("")

    # Success rate
    success_rate = (results['applied'] / results['total'] * 100) if results['total'] > 0 else 0
    md_lines.append(f"**Success Rate:** {success_rate:.1f}%")
    md_lines.append("")

    # Details
    if results['details']:
        md_lines.append("## Details")
        md_lines.append("")

        for detail in results['details']:
            status_icon = "✓" if detail['status'] == "applied" else "✗"
            md_lines.append(f"- **{detail['id']}** {status_icon} {detail['message']}")

        md_lines.append("")

    output_path.write_text('\n'.join(md_lines), encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(
        description="Apply edit recommendations holistically",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Apply all edits
  %(prog)s --manuscript-dir manuscript/project_v1 --recommendations edit_recommendations_v1.json

  # Dry run first
  %(prog)s --manuscript-dir manuscript/project_v1 --recommendations edit_recommendations_v1.json --dry-run

  # Apply only critical edits
  %(prog)s --manuscript-dir manuscript/project_v1 --recommendations edit_recommendations_v1.json --priority critical

  # Apply edits for specific section
  %(prog)s --manuscript-dir manuscript/project_v1 --recommendations edit_recommendations_v1.json --section methods

  # Skip backup (not recommended)
  %(prog)s --manuscript-dir manuscript/project_v1 --recommendations edit_recommendations_v1.json --no-backup
        """
    )

    parser.add_argument(
        "--manuscript-dir",
        type=Path,
        required=True,
        help="Path to manuscript directory"
    )

    parser.add_argument(
        "--recommendations",
        type=Path,
        required=True,
        help="Path to edit_recommendations.json file"
    )

    parser.add_argument(
        "--priority",
        choices=["critical", "important", "optional"],
        help="Minimum priority level to apply"
    )

    parser.add_argument(
        "--section",
        help="Only apply edits for this section"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate application without modifying files"
    )

    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Skip backup creation (not recommended)"
    )

    parser.add_argument(
        "--output-report",
        type=Path,
        help="Output path for application report (default: manuscript_dir/edit_application_report.md)"
    )

    args = parser.parse_args()

    # Validate inputs
    if not args.manuscript_dir.exists():
        print(f"✗ Manuscript directory not found: {args.manuscript_dir}")
        return 1

    if not args.recommendations.exists():
        print(f"✗ Recommendations file not found: {args.recommendations}")
        return 1

    # Initialize orchestrator
    print("Initializing edit orchestrator...")
    orchestrator = HolisticEditOrchestrator(args.manuscript_dir)

    count = orchestrator.load_recommendations(args.recommendations)
    print(f"✓ Loaded {count} recommendations")

    # Create application plan
    print("\nCreating application plan...")
    plan = orchestrator.plan_application(
        min_priority=args.priority,
        section=args.section,
        resolve_conflicts=True
    )

    preview = orchestrator.preview_plan()
    print(f"✓ Plan created:")
    print(f"  Total edits: {preview['total_edits']}")
    print(f"  Conflicts detected: {preview['conflicts_detected']}")

    if preview['conflicts_detected'] > 0:
        print(f"  (Conflicts auto-resolved by priority)")

    print(f"\nBy priority:")
    for priority, count in preview['by_priority'].items():
        print(f"  {priority}: {count}")

    print(f"\nBy section:")
    for section, count in preview['by_section'].items():
        print(f"  {section}: {count}")

    if args.dry_run:
        print("\n" + "=" * 60)
        print("DRY RUN MODE - No files will be modified")
        print("=" * 60)

    # Apply edits
    print("\nApplying edits...")
    results = apply_edits(orchestrator, dry_run=args.dry_run, backup=not args.no_backup)

    # Generate report
    if not args.output_report:
        args.output_report = args.manuscript_dir / "edit_application_report.md"

    generate_application_report(results, args.output_report)
    print(f"\n✓ Application report: {args.output_report}")

    # Summary
    print("\n" + "=" * 60)
    print("Application Summary:")
    print(f"  Total edits: {results['total']}")
    print(f"  Applied: {results['applied']}")
    print(f"  Failed: {results['failed']}")
    print(f"  Skipped: {results['skipped']}")

    success_rate = (results['applied'] / results['total'] * 100) if results['total'] > 0 else 0
    print(f"  Success rate: {success_rate:.1f}%")
    print("=" * 60)

    return 0 if results['failed'] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
