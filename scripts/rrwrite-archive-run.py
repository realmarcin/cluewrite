#!/usr/bin/env python3
"""
Archive current manuscript state as a complete workflow run.

Usage:
    python scripts/rrwrite-archive-run.py
    python scripts/rrwrite-archive-run.py --description "nature-methods-v1"
    python scripts/rrwrite-archive-run.py --journal "PLOS Computational Biology"
"""

import argparse
import sys
import shutil
import json
from pathlib import Path
from datetime import datetime
import subprocess

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from rrwrite_state_manager import StateManager
except ImportError:
    import rrwrite_state_manager
    StateManager = rrwrite_state_manager.StateManager


def get_git_commit() -> str:
    """Get current git commit hash.

    Returns:
        Short commit hash or 'nogit'
    """
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    return "nogit"


def create_run_metadata(run_dir: Path, state: dict, journal: str = None) -> dict:
    """Create run metadata file.

    Args:
        run_dir: Run directory path
        state: Current state dictionary
        journal: Target journal

    Returns:
        Metadata dictionary
    """
    metadata = {
        "run_id": run_dir.name,
        "created_at": datetime.now().isoformat(),
        "target_journal": journal or state.get("target_journal"),
        "git_commit": get_git_commit(),
        "workflow_status": state.get("workflow_status", {}),
        "rrwrite_version": "1.0.0"
    }

    return metadata


def archive_run(description: str = None, journal: str = None) -> None:
    """Archive current manuscript state as a run.

    Args:
        description: Optional description for run directory name
        journal: Target journal for this run
    """
    # Initialize state manager
    manager = StateManager()

    # Check manuscript directory exists
    if not manager.manuscript_dir.exists():
        print(f"Error: manuscript/ directory not found in {manager.project_root}")
        sys.exit(1)

    # Read current state
    state = manager.read_state()
    if state is None:
        print("Warning: No state file found. Creating basic state.")
        state = manager.initialize_state()

    # Create run directory name
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    if description:
        run_id = f"{timestamp}_{description}"
    else:
        run_id = timestamp

    # Create runs directory if needed
    runs_dir = manager.manuscript_dir / "runs"
    runs_dir.mkdir(exist_ok=True)

    # Create run directory
    run_dir = runs_dir / run_id
    if run_dir.exists():
        print(f"Error: Run directory already exists: {run_dir}")
        sys.exit(1)

    run_dir.mkdir()

    print(f"Archiving current state to: {run_dir.relative_to(manager.project_root)}")
    print()

    # Files to archive (if they exist)
    files_to_copy = [
        "outline.md",
        "literature.md",
        "literature_citations.bib",
        "literature_evidence.csv",
        "abstract.md",
        "introduction.md",
        "methods.md",
        "results.md",
        "discussion.md",
        "conclusion.md",
        "full_manuscript.md",
    ]

    # Also copy any critique files
    for critique_file in manager.manuscript_dir.glob("critique_*.md"):
        files_to_copy.append(critique_file.name)

    # Copy files
    copied_files = []
    for filename in files_to_copy:
        src = manager.manuscript_dir / filename
        if src.exists():
            dst = run_dir / filename
            shutil.copy2(src, dst)
            copied_files.append(filename)
            print(f"  ✓ Copied: {filename}")

    if not copied_files:
        print("  Warning: No files found to archive")

    # Copy PROJECT.md and references.bib from project root
    for filename in ["PROJECT.md", "references.bib"]:
        src = manager.project_root / filename
        if src.exists():
            dst = run_dir / filename
            shutil.copy2(src, dst)
            copied_files.append(filename)
            print(f"  ✓ Copied: {filename}")

    # Create run metadata
    metadata = create_run_metadata(run_dir, state, journal)
    metadata["files"] = copied_files

    metadata_file = run_dir / "run_metadata.json"
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"  ✓ Created: run_metadata.json")

    print()

    # Update state with run info
    outputs = {filename: f"runs/{run_id}/{filename}" for filename in copied_files}
    manager.add_run(run_id, target_journal=journal, outputs=outputs)
    manager.complete_run(run_id, outputs=outputs)

    # Create git tag if in a git repo
    git_commit = get_git_commit()
    if git_commit != "nogit":
        try:
            tag_name = f"run-{run_id}"
            result = subprocess.run(
                ["git", "tag", "-a", tag_name, "-m", f"Workflow run: {run_id}"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                print(f"✓ Created Git tag: {tag_name}")
                print()
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

    # Display summary
    print("=" * 60)
    print("Run Archived Successfully")
    print("=" * 60)
    print()
    print(f"Run ID: {run_id}")
    print(f"Location: {run_dir.relative_to(manager.project_root)}")
    print(f"Files archived: {len(copied_files)}")
    if journal or state.get("target_journal"):
        print(f"Target journal: {journal or state.get('target_journal')}")
    print()

    print("Next steps:")
    print("  1. Active workspace remains in manuscript/")
    print("  2. Continue refining current version, or")
    print("  3. Start new run for different journal/approach")
    print()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Archive current manuscript state as a workflow run"
    )
    parser.add_argument(
        "--description",
        "-d",
        help="Short description for run (e.g., 'nature-methods-v1')"
    )
    parser.add_argument(
        "--journal",
        "-j",
        help="Target journal for this run"
    )

    args = parser.parse_args()

    archive_run(description=args.description, journal=args.journal)


if __name__ == "__main__":
    main()
