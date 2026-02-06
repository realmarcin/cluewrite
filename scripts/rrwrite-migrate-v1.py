#!/usr/bin/env python3
"""
Migrate existing RRWrite project to v1.0 with state tracking.

Usage:
    python scripts/rrwrite-migrate-v1.py
    python scripts/rrwrite-migrate-v1.py --project-dir /path/to/project
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime
import subprocess
import shutil

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from rrwrite_state_manager import StateManager
except ImportError:
    import rrwrite_state_manager
    StateManager = rrwrite_state_manager.StateManager


def get_file_mtime(file_path: Path) -> str:
    """Get file modification time as ISO timestamp.

    Args:
        file_path: Path to file

    Returns:
        ISO timestamp or None
    """
    if not file_path.exists():
        return None

    try:
        mtime = file_path.stat().st_mtime
        return datetime.fromtimestamp(mtime).isoformat()
    except OSError:
        return None


def migrate_project(project_dir: str = ".") -> None:
    """Migrate existing project to v1.0 state tracking.

    Args:
        project_dir: Project directory path
    """
    project_root = Path(project_dir).resolve()
    manuscript_dir = project_root / "manuscript"

    print("=" * 60)
    print("RRWrite Migration to v1.0")
    print("=" * 60)
    print()
    print(f"Project directory: {project_root}")
    print()

    # Check if already migrated
    state_manager = StateManager(project_dir)
    if state_manager.read_state() is not None:
        print("✓ Project already has state tracking enabled.")
        print()
        print("Run 'python scripts/rrwrite-status.py' to view status.")
        return

    # Create manuscript directory if it doesn't exist
    if not manuscript_dir.exists():
        print("Creating manuscript/ directory...")
        manuscript_dir.mkdir(parents=True)

    # Create .rrwrite directory
    state_dir = manuscript_dir / ".rrwrite"
    if not state_dir.exists():
        print("Creating manuscript/.rrwrite/ directory...")
        state_dir.mkdir(parents=True)

    # Create runs directory
    runs_dir = manuscript_dir / "runs"
    if not runs_dir.exists():
        print("Creating manuscript/runs/ directory...")
        runs_dir.mkdir(parents=True)

    # Detect existing files
    print()
    print("Scanning for existing files...")
    print()

    detected_files = {}

    # Check for outline
    for name in ["outline.md", "manuscript_plan.md"]:
        file_path = manuscript_dir / name
        if file_path.exists():
            detected_files["outline"] = {
                "file": name,
                "mtime": get_file_mtime(file_path)
            }
            print(f"  ✓ Found outline: {name}")
            break

    # Check for literature review
    for name in ["literature.md", "literature_review.md"]:
        file_path = manuscript_dir / name
        if file_path.exists():
            detected_files["literature"] = {
                "file": name,
                "mtime": get_file_mtime(file_path)
            }
            print(f"  ✓ Found literature: {name}")
            break

    # Check for sections
    sections = ["abstract", "introduction", "methods", "results", "discussion", "conclusion"]
    found_sections = []
    for section in sections:
        file_path = manuscript_dir / f"{section}.md"
        if file_path.exists():
            found_sections.append(section)
            print(f"  ✓ Found section: {section}.md")

    if found_sections:
        detected_files["sections"] = found_sections

    # Check for critiques
    critique_files = list(manuscript_dir.glob("critique_*.md"))
    if critique_files:
        print(f"  ✓ Found {len(critique_files)} critique file(s)")
        detected_files["critiques"] = [f.name for f in critique_files]

    # Check for full manuscript
    if (manuscript_dir / "full_manuscript.md").exists():
        print(f"  ✓ Found full_manuscript.md")
        detected_files["full_manuscript"] = "full_manuscript.md"

    if not detected_files:
        print("  No existing manuscript files found.")

    print()

    # Initialize state file
    print("Initializing state file...")

    # Get project name from directory
    project_name = project_root.name

    # Try to detect target journal from PROJECT.md
    target_journal = None
    cluewrite_file = project_root / "PROJECT.md"
    if cluewrite_file.exists():
        try:
            with open(cluewrite_file, 'r') as f:
                content = f.read().lower()
                if "nature" in content:
                    target_journal = "Nature Methods"
                elif "plos" in content:
                    target_journal = "PLOS Computational Biology"
                elif "bioinformatics" in content:
                    target_journal = "Bioinformatics"
        except IOError:
            pass

    # Initialize state
    state = state_manager.initialize_state(
        project_name=project_name,
        target_journal=target_journal
    )

    # Update state based on detected files
    if "outline" in detected_files:
        state_manager.update_workflow_stage(
            "plan",
            status="completed",
            file_path=f"manuscript/{detected_files['outline']['file']}",
            completed_at=detected_files['outline']['mtime']
        )
        print(f"  ✓ Marked planning stage as completed")

    if "literature" in detected_files:
        state_manager.update_workflow_stage(
            "research",
            status="completed",
            file_path=f"manuscript/{detected_files['literature']['file']}",
            completed_at=detected_files['literature']['mtime']
        )
        print(f"  ✓ Marked research stage as completed")

    if "sections" in detected_files:
        for section in detected_files["sections"]:
            state_manager.add_section_completed(section)
        print(f"  ✓ Marked {len(detected_files['sections'])} sections as completed")

    if "full_manuscript" in detected_files:
        state_manager.update_workflow_stage(
            "assembly",
            status="completed",
            file_path="manuscript/full_manuscript.md"
        )
        print(f"  ✓ Marked assembly stage as completed")

    print()

    # Update .gitignore if it exists
    gitignore_file = project_root / ".gitignore"
    if gitignore_file.exists():
        try:
            with open(gitignore_file, 'r') as f:
                content = f.read()

            # Check if already has state tracking patterns
            if ".rrwrite" not in content:
                print("Updating .gitignore...")
                with open(gitignore_file, 'a') as f:
                    f.write("\n# State tracking (keep in Git for collaboration)\n")
                    f.write("!manuscript/.rrwrite/\n")
                    f.write("!manuscript/.rrwrite/state.json\n")
                    f.write("\n# Archived runs (optional)\n")
                    f.write("# manuscript/runs/\n")
                print("  ✓ Updated .gitignore")
        except IOError:
            print("  ⚠ Could not update .gitignore")

    print()

    # Display summary
    print("=" * 60)
    print("Migration Complete!")
    print("=" * 60)
    print()
    print("✓ State tracking enabled")
    print(f"✓ State file: manuscript/.rrwrite/state.json")
    print()

    if detected_files:
        print("Detected files:")
        if "outline" in detected_files:
            print(f"  • Outline: {detected_files['outline']['file']}")
        if "literature" in detected_files:
            print(f"  • Literature: {detected_files['literature']['file']}")
        if "sections" in detected_files:
            print(f"  • Sections: {', '.join(detected_files['sections'])}")
        if "critiques" in detected_files:
            print(f"  • Critiques: {len(detected_files['critiques'])} file(s)")
        print()

    print("Next steps:")
    print("  1. View status: python scripts/rrwrite-status.py")
    print("  2. Commit migration:")
    print("       git add -A")
    print('       git commit -m "Migrate to RRWrite v1.0 with state tracking"')
    print()
    print("  3. Continue working with RRWrite skills")
    print()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Migrate existing RRWrite project to v1.0"
    )
    parser.add_argument(
        "--project-dir",
        default=".",
        help="Project directory (default: current directory)"
    )

    args = parser.parse_args()

    migrate_project(args.project_dir)


if __name__ == "__main__":
    main()
