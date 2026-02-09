# RRWrite Versioning and Progress Tracking - Implementation Plan

**Date**: 2026-02-07
**Status**: 📋 PLAN - Ready for Review
**Based on**: Comprehensive research of Snakemake, Nextflow, DVC, Quarto, Jupyter, arXiv, academic workflows

---

## Executive Summary

This plan implements a **hybrid versioning strategy** combining Git-based version control with semantic version directories for major milestones. The system will:

- ✅ Version all pipeline outputs automatically
- ✅ Track progress and enable smart resume of failed runs
- ✅ Integrate with Git for full audit trail
- ✅ Align with academic manuscript versioning (arXiv-style v1, v2, v3)
- ✅ Support both complete pipeline runs and individual task executions
- ✅ Provide cleanup and archival for old versions

**Recommended Strategy**: **Option D (Git-based) + Semantic Directories**

---

## Current State Analysis

### What RRWrite Currently Does

**Directory structure:**
```
manuscript/
└── repo_v1/
    ├── .rrwrite/state.json
    ├── outline.md
    ├── abstract.md
    ├── introduction.md
    └── ...
```

**Version management:**
- Auto-increments version number based on existing directories
- Semantic versions: `repo_v1`, `repo_v2`, `repo_v3`
- User can specify version with `--version v2` flag

**State tracking:**
- JSON file: `.rrwrite/state.json`
- Tracks workflow stages (plan, research, drafting, etc.)
- Per-stage metadata: status, file path, timestamp, git commit

**File handling:**
- Overwrites files within same version
- No history preservation (relies on external Git if user manages it)

### What's Missing

1. ❌ **No datestamping** - Can't tell WHEN a version was created from directory name
2. ❌ **No checksums** - Can't detect if input files changed requiring rerun
3. ❌ **No smart resume** - Reruns everything, even if inputs unchanged
4. ❌ **No automatic Git integration** - Users must manage Git manually
5. ❌ **No cleanup/archival** - Old versions accumulate indefinitely
6. ❌ **Limited rerun tracking** - Doesn't track which steps were redone
7. ❌ **No dependency tracking** - Can't determine minimal rerun set

---

## Proposed Architecture

### 1. Directory Structure (Unchanged - Semantic Versions)

**Keep current semantic versioning for directories:**

```
manuscript/
├── .rrwrite/
│   └── global_state.json         # NEW: Tracks all manuscript versions
├── repo_v1/                      # Semantic version for major iterations
│   ├── .git/                     # NEW: Git repository (auto-initialized)
│   ├── .rrwrite/
│   │   ├── state.json           # Enhanced state file
│   │   ├── checksums.json       # NEW: File hashes for change detection
│   │   └── config.yaml          # NEW: Version-specific configuration
│   ├── sections/
│   │   ├── abstract.md
│   │   ├── introduction.md
│   │   └── ...
│   ├── outline.md
│   ├── literature.md
│   ├── literature_evidence.md
│   ├── repo_evidence.md
│   ├── manuscript.md            # Assembled manuscript
│   └── critique_v1.md           # Critique with version suffix
└── repo_v2/                      # Next major version
    └── ...
```

**Why semantic versions (not timestamps)?**
- ✅ Matches academic publishing (arXiv v1, v2, v3)
- ✅ Clear progression and milestone marking
- ✅ Easy to remember and reference ("use version 2")
- ✅ Semantic meaning (v1 = initial, v2 = revision, v3 = final)

**Why NOT timestamps?**
- ❌ No semantic meaning ("what was 20260207_143022?")
- ❌ Cluttered with partial/failed runs
- ❌ Hard to identify submission vs draft versions

**Compromise**: Add creation timestamp to state file, not directory name.

### 2. File Versioning Within Runs

**Strategy: Overwrite + Git Commits**

| File Type | Strategy | Rationale |
|-----------|----------|-----------|
| **Section MD files** | Overwrite + Git | Clean namespace, Git shows full history |
| **Critique reports** | Version suffix | Compare feedback across iterations |
| **Assembled manuscript** | Overwrite + Git | Latest version always `manuscript.md` |
| **Evidence files** | Append + Git | Accumulate evidence, track additions |
| **State files** | Overwrite + archive | Current state clear, history preserved |
| **Generated PDFs** | Semantic naming | `manuscript_submission_v1.pdf` |

**Examples:**

```bash
# Section files - overwrite
manuscript/repo_v1/abstract.md              # Latest version
# History in Git: git log abstract.md

# Critique files - version suffix
manuscript/repo_v1/critique_v1.md           # First critique
manuscript/repo_v1/critique_v2.md           # After revisions
manuscript/repo_v1/critique_v3.md           # Final review

# PDFs - semantic naming
manuscript/repo_v1/manuscript_draft_v1.pdf
manuscript/repo_v1/manuscript_submission_v1.pdf
manuscript/repo_v1/manuscript_revision_v1.pdf
```

### 3. Git Integration (NEW)

**Auto-initialize Git repository in each version directory:**

```bash
# When creating new version
cd manuscript/repo_v1/
git init
git add .gitignore README.md
git commit -m "Initialize manuscript version 1"
```

**Auto-commit after each major stage:**

```bash
# After planning
git add outline.md .rrwrite/state.json
git commit -m "[RRWrite] Complete plan: Generated outline for Nature Biotechnology

Stage: plan
Journal: Nature Biotechnology
Files: outline.md
Status: completed
Timestamp: 2026-02-07 14:30:22

Co-Authored-By: RRWrite <rrwrite@research.ai>"

# After drafting introduction
git add sections/introduction.md .rrwrite/state.json .rrwrite/checksums.json
git commit -m "[RRWrite] Complete drafting: Introduction section

Stage: drafting
Section: introduction
Word count: 1,247
Citations: 15
Status: completed
Timestamp: 2026-02-07 15:45:10

Co-Authored-By: RRWrite <rrwrite@research.ai>"
```

**Tagging for milestones:**

```bash
# User or RRWrite creates tags
git tag -a submission-v1 -m "Ready for journal submission (Nature Biotechnology)"
git tag -a revision-v1 -m "First revision addressing reviewer comments"
git tag -a final-v1 -m "Accepted manuscript, final version"
```

**Benefits:**
- Full audit trail (who, what, when, why)
- Diff any two states instantly
- Rollback to any previous state
- Lightweight (Git compression)
- Industry standard tool

**User control:**
```bash
# Disable auto-commit if user wants manual control
rrwrite draft --section introduction --no-auto-commit

# Custom commit message
rrwrite draft --section introduction --commit-message "Revise intro based on advisor feedback"
```

### 4. Enhanced State Tracking (MODIFIED)

**New state.json structure:**

```json
{
  "version": "2.0",
  "schema_version": "2.0",

  "run_metadata": {
    "run_id": "20260207_143022",
    "created_at": "2026-02-07T14:30:22Z",
    "last_updated": "2026-02-07T17:45:10Z",
    "manuscript_version": "v1",
    "repository_path": "/path/to/research-repo",
    "repository_commit": "abc123d",
    "target_journal": "Nature Biotechnology",
    "user": "marcin",
    "rrwrite_version": "0.1.0"
  },

  "workflow_status": {
    "plan": {
      "status": "completed",
      "dependencies": [],
      "inputs": {
        "repository_analysis.json": "sha256:abc123..."
      },
      "outputs": {
        "outline.md": "sha256:def456..."
      },
      "started_at": "2026-02-07T14:30:22Z",
      "completed_at": "2026-02-07T14:32:15Z",
      "duration_seconds": 113,
      "git_commit": "abc123d",
      "error": null,
      "rerun_count": 0,
      "skipped": false,
      "skip_reason": null
    },

    "assessment": {
      "status": "completed",
      "dependencies": ["plan"],
      "inputs": {
        "outline.md": "sha256:def456..."
      },
      "outputs": {
        "journal_assessment.md": "sha256:ghi789...",
        "journal_guidelines.md": "sha256:jkl012..."
      },
      "started_at": "2026-02-07T14:32:20Z",
      "completed_at": "2026-02-07T14:35:45Z",
      "duration_seconds": 205,
      "git_commit": "def456e",
      "metadata": {
        "journal_initial": "bioinformatics",
        "journal_confirmed": "nature_biotechnology",
        "compatibility_score": 0.87
      },
      "error": null,
      "rerun_count": 0,
      "skipped": false
    },

    "research": {
      "status": "completed",
      "dependencies": ["plan"],
      "inputs": {
        "outline.md": "sha256:def456..."
      },
      "outputs": {
        "literature.md": "sha256:mno345...",
        "literature_citations.bib": "sha256:pqr678...",
        "literature_evidence.md": "sha256:stu901..."
      },
      "started_at": "2026-02-07T14:36:00Z",
      "completed_at": "2026-02-07T14:42:30Z",
      "duration_seconds": 390,
      "git_commit": "ghi789f",
      "metadata": {
        "papers_found": 23,
        "api_sources": ["semantic_scholar", "pubmed"]
      },
      "error": null,
      "rerun_count": 0,
      "skipped": false
    },

    "drafting": {
      "status": "in_progress",
      "dependencies": ["plan", "research", "assessment"],
      "sections": {
        "abstract": {
          "status": "completed",
          "file": "sections/abstract.md",
          "checksum": "sha256:vwx234...",
          "started_at": "2026-02-07T14:43:00Z",
          "completed_at": "2026-02-07T14:48:15Z",
          "git_commit": "jkl012g",
          "word_count": 247,
          "citations": 3,
          "rerun_count": 0
        },
        "introduction": {
          "status": "completed",
          "file": "sections/introduction.md",
          "checksum": "sha256:yza567...",
          "started_at": "2026-02-07T14:50:00Z",
          "completed_at": "2026-02-07T15:05:30Z",
          "git_commit": "mno345h",
          "word_count": 1247,
          "citations": 15,
          "rerun_count": 1
        },
        "methods": {
          "status": "not_started",
          "file": null,
          "checksum": null
        }
      }
    }
  },

  "checksums": {
    "outline.md": "sha256:def456...",
    "sections/abstract.md": "sha256:vwx234...",
    "sections/introduction.md": "sha256:yza567..."
  },

  "git": {
    "repository_initialized": true,
    "current_commit": "mno345h",
    "tags": ["draft-v1"],
    "branch": "main"
  }
}
```

**New fields:**
- `run_id`: Unique identifier for this run (timestamp-based)
- `dependencies`: Which stages must complete before this one
- `inputs`/`outputs`: Files with checksums for change detection
- `duration_seconds`: Performance tracking
- `metadata`: Stage-specific information
- `rerun_count`: How many times stage was redone
- `skipped`/`skip_reason`: Why stage was skipped (if applicable)

### 5. Checksum-Based Change Detection (NEW)

**File: `.rrwrite/checksums.json`**

```json
{
  "version": "1.0",
  "algorithm": "sha256",
  "files": {
    "outline.md": {
      "checksum": "sha256:def456...",
      "size_bytes": 8214,
      "modified_at": "2026-02-07T14:32:15Z",
      "git_commit": "abc123d"
    },
    "sections/introduction.md": {
      "checksum": "sha256:yza567...",
      "size_bytes": 5799,
      "modified_at": "2026-02-07T15:05:30Z",
      "git_commit": "mno345h"
    }
  }
}
```

**Usage:**
```python
# Before regenerating a section, check if inputs changed
current_outline_checksum = compute_sha256("outline.md")
stored_checksum = checksums["outline.md"]["checksum"]

if current_outline_checksum == stored_checksum:
    print("Outline unchanged, can skip regeneration")
else:
    print("Outline modified, regenerating section")
```

### 6. Smart Resume Capability (NEW)

**Detect which stages need rerun based on input changes:**

```python
def needs_rerun(stage: str, state: dict, checksums: dict) -> bool:
    """
    Determine if stage needs to be rerun.

    Returns True if:
    - Stage never completed
    - Stage failed
    - Input files changed (checksum mismatch)
    - Dependencies changed
    """
    stage_status = state["workflow_status"][stage]

    # Never completed or failed
    if stage_status["status"] in ["not_started", "failed"]:
        return True

    # Check if inputs changed
    for input_file, expected_checksum in stage_status["inputs"].items():
        current_checksum = compute_checksum(input_file)
        if current_checksum != expected_checksum:
            return True

    # Check if dependencies changed
    for dep_stage in stage_status["dependencies"]:
        if state["workflow_status"][dep_stage]["status"] != "completed":
            return True
        # If dependency was recently rerun, this stage needs rerun
        if state["workflow_status"][dep_stage]["rerun_count"] > 0:
            return True

    return False
```

**Usage:**
```bash
# Resume failed pipeline run
rrwrite resume

# RRWrite checks each stage:
# ✓ plan: completed, inputs unchanged → SKIP
# ✓ research: completed, inputs unchanged → SKIP
# ✗ drafting: failed on introduction section → RERUN from introduction
# ✗ assembly: not started → RUN
# ✗ critique: not started → RUN
```

---

## Implementation Phases

### Phase 1: Foundation (Week 1) - CRITICAL

#### 1.1 Enhanced State Schema

**File to modify**: `scripts/rrwrite_state_manager.py`

**Changes:**
```python
class StateManager:
    SCHEMA_VERSION = "2.0"

    def __init__(self, output_dir: str):
        self.state = {
            "version": self.SCHEMA_VERSION,
            "run_metadata": {
                "run_id": self._generate_run_id(),
                "created_at": self._timestamp(),
                "manuscript_version": self._extract_version(output_dir),
                # ... other metadata
            },
            "workflow_status": {
                # Enhanced stage structure
            },
            "checksums": {},
            "git": {
                "repository_initialized": False,
                "current_commit": None,
                "tags": [],
                "branch": "main"
            }
        }

    def _generate_run_id(self) -> str:
        """Generate unique run ID (timestamp-based)."""
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    def update_stage_status(self, stage: str, status: str, **kwargs):
        """Update stage with enhanced metadata."""
        # Add inputs, outputs, checksums, duration, etc.
        pass
```

**New methods to add:**
- `compute_checksums(files: List[str]) -> dict`
- `validate_dependencies(stage: str) -> bool`
- `get_stage_inputs(stage: str) -> List[str]`
- `get_stage_outputs(stage: str) -> List[str]`
- `needs_rerun(stage: str) -> bool`

#### 1.2 Checksum Computation

**New file**: `scripts/rrwrite_checksum.py`

```python
import hashlib
from pathlib import Path
from typing import Dict

def compute_sha256(file_path: Path) -> str:
    """Compute SHA256 checksum of file."""
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            sha256.update(chunk)
    return f"sha256:{sha256.hexdigest()}"

def compute_checksums(files: List[Path]) -> Dict[str, dict]:
    """Compute checksums for multiple files."""
    checksums = {}
    for file_path in files:
        if not file_path.exists():
            continue
        checksums[str(file_path)] = {
            "checksum": compute_sha256(file_path),
            "size_bytes": file_path.stat().st_size,
            "modified_at": datetime.fromtimestamp(
                file_path.stat().st_mtime
            ).isoformat()
        }
    return checksums
```

**Integration**: Call after each stage completion to update checksums.

#### 1.3 Git Auto-Initialization

**File to modify**: `scripts/rrwrite_state_manager.py`

**New method:**
```python
def initialize_git_repository(self, output_dir: Path):
    """Initialize Git repository in output directory if not exists."""
    git_dir = output_dir / ".git"

    if git_dir.exists():
        print("Git repository already exists")
        self.state["git"]["repository_initialized"] = True
        return

    # Initialize Git
    subprocess.run(["git", "init"], cwd=output_dir, check=True)

    # Create .gitignore
    gitignore_content = """
# RRWrite temporary files
.rrwrite/cache/
.rrwrite/tmp/

# Large binary outputs
*.pdf
*.docx

# Python cache
__pycache__/
*.pyc

# OS files
.DS_Store
Thumbs.db
"""
    (output_dir / ".gitignore").write_text(gitignore_content)

    # Initial commit
    subprocess.run(["git", "add", ".gitignore"], cwd=output_dir)
    subprocess.run(
        ["git", "commit", "-m", "Initialize RRWrite manuscript"],
        cwd=output_dir
    )

    self.state["git"]["repository_initialized"] = True
    self.state["git"]["current_commit"] = self._get_git_commit(output_dir)
```

#### 1.4 Git Auto-Commit

**New file**: `scripts/rrwrite_git.py`

```python
import subprocess
from pathlib import Path
from datetime import datetime

class GitManager:
    """Manage Git operations for RRWrite."""

    def __init__(self, repo_path: Path, auto_commit: bool = True):
        self.repo_path = repo_path
        self.auto_commit = auto_commit

    def commit(self,
               files: List[str],
               stage: str,
               description: str,
               metadata: dict = None):
        """
        Commit files with structured message.

        Args:
            files: List of file paths to commit
            stage: Workflow stage (plan, research, drafting, etc.)
            description: Human-readable description
            metadata: Additional metadata for commit message
        """
        if not self.auto_commit:
            return None

        # Stage files
        subprocess.run(
            ["git", "add"] + files,
            cwd=self.repo_path,
            check=True
        )

        # Format commit message
        msg = f"[RRWrite] Complete {stage}: {description}\n\n"
        msg += f"Stage: {stage}\n"

        if metadata:
            for key, value in metadata.items():
                msg += f"{key.title()}: {value}\n"

        msg += f"Status: completed\n"
        msg += f"Timestamp: {datetime.now().isoformat()}\n\n"
        msg += "Co-Authored-By: RRWrite <rrwrite@research.ai>"

        # Commit
        subprocess.run(
            ["git", "commit", "-m", msg],
            cwd=self.repo_path,
            check=True
        )

        # Get commit hash
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )
        return result.stdout.strip()

    def tag(self, tag_name: str, message: str):
        """Create annotated Git tag."""
        subprocess.run(
            ["git", "tag", "-a", tag_name, "-m", message],
            cwd=self.repo_path,
            check=True
        )
```

**Integration**: Call `git_manager.commit()` after each stage completion.

### Phase 2: Smart Resume (Week 2)

#### 2.1 Dependency Resolution

**File**: `scripts/rrwrite_dependency.py`

```python
class DependencyResolver:
    """Resolve workflow stage dependencies."""

    DEPENDENCIES = {
        "repository_analysis": [],
        "plan": ["repository_analysis"],
        "assessment": ["plan"],
        "research": ["plan"],
        "drafting": ["plan", "research", "assessment"],
        "assembly": ["drafting"],
        "critique": ["assembly"],
        "verification": ["assembly"]
    }

    def get_dependencies(self, stage: str) -> List[str]:
        """Get direct dependencies for stage."""
        return self.DEPENDENCIES.get(stage, [])

    def get_all_dependencies(self, stage: str) -> List[str]:
        """Get all dependencies (recursive)."""
        deps = []
        to_process = [stage]

        while to_process:
            current = to_process.pop(0)
            for dep in self.get_dependencies(current):
                if dep not in deps:
                    deps.append(dep)
                    to_process.append(dep)

        return deps

    def needs_rerun(self,
                   stage: str,
                   state: dict,
                   checksums: dict) -> tuple[bool, str]:
        """
        Check if stage needs rerun.

        Returns:
            (needs_rerun: bool, reason: str)
        """
        stage_data = state["workflow_status"].get(stage, {})

        # Never completed
        if stage_data.get("status") != "completed":
            return True, "not_completed"

        # Check input checksums
        for input_file, expected_checksum in stage_data.get("inputs", {}).items():
            current_checksum = checksums.get(input_file, {}).get("checksum")
            if current_checksum != expected_checksum:
                return True, f"input_changed:{input_file}"

        # Check dependencies
        for dep_stage in self.get_dependencies(stage):
            dep_data = state["workflow_status"].get(dep_stage, {})
            if dep_data.get("status") != "completed":
                return True, f"dependency_incomplete:{dep_stage}"
            if dep_data.get("rerun_count", 0) > 0:
                return True, f"dependency_rerun:{dep_stage}"

        return False, "up_to_date"

    def get_rerun_stages(self, state: dict, checksums: dict) -> List[str]:
        """Get minimal set of stages that need rerun."""
        rerun = []

        for stage in self.DEPENDENCIES.keys():
            needs_rerun, reason = self.needs_rerun(stage, state, checksums)
            if needs_rerun:
                rerun.append(stage)

        return rerun
```

#### 2.2 Resume Command

**File**: `scripts/rrwrite-resume.py`

```python
#!/usr/bin/env python3
"""Resume failed or incomplete RRWrite pipeline run."""

import argparse
from pathlib import Path
from rrwrite_state_manager import StateManager
from rrwrite_checksum import compute_checksums
from rrwrite_dependency import DependencyResolver

def main():
    parser = argparse.ArgumentParser(description="Resume RRWrite pipeline")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--force", action="store_true",
                       help="Force rerun all stages")
    args = parser.parse_args()

    # Load state
    manager = StateManager(output_dir=args.output_dir)
    state = manager.load_state()

    # Compute current checksums
    all_files = list(args.output_dir.glob("**/*.md"))
    current_checksums = compute_checksums(all_files)

    # Determine what needs to rerun
    resolver = DependencyResolver()
    rerun_stages = resolver.get_rerun_stages(state, current_checksums)

    if not rerun_stages:
        print("✓ All stages up to date, nothing to rerun")
        return 0

    print(f"Found {len(rerun_stages)} stages to rerun:")
    for stage in rerun_stages:
        needs_rerun, reason = resolver.needs_rerun(stage, state, current_checksums)
        print(f"  - {stage}: {reason}")

    # Execute reruns (call appropriate skills)
    # Implementation depends on skill execution framework

    return 0

if __name__ == "__main__":
    exit(main())
```

### Phase 3: Version Management Commands (Week 3)

#### 3.1 Global State Tracking

**New file**: `manuscript/.rrwrite/global_state.json`

```json
{
  "version": "1.0",
  "versions": {
    "repo_v1": {
      "created_at": "2026-02-07T14:30:22Z",
      "last_updated": "2026-02-07T17:45:10Z",
      "status": "completed",
      "git_tags": ["draft-v1", "submission-v1"],
      "target_journal": "Nature Biotechnology",
      "repository_commit": "abc123d",
      "notes": "Initial submission version"
    },
    "repo_v2": {
      "created_at": "2026-02-10T09:15:00Z",
      "last_updated": "2026-02-10T16:30:45Z",
      "status": "in_progress",
      "git_tags": [],
      "target_journal": "Nature Biotechnology",
      "repository_commit": "def456e",
      "notes": "Revision addressing reviewer comments"
    }
  },
  "current_version": "repo_v2"
}
```

#### 3.2 Version Management Script

**New file**: `scripts/rrwrite-versions.py`

```python
#!/usr/bin/env python3
"""Manage RRWrite manuscript versions."""

import argparse
import json
from pathlib import Path
from datetime import datetime

class VersionManager:
    """Manage manuscript versions."""

    def __init__(self, manuscript_dir: Path = Path("manuscript")):
        self.manuscript_dir = manuscript_dir
        self.global_state_file = manuscript_dir / ".rrwrite" / "global_state.json"

    def list_versions(self):
        """List all manuscript versions."""
        state = self._load_global_state()

        print("Manuscript Versions:")
        print("=" * 60)

        for version, data in state["versions"].items():
            status_icon = "✓" if data["status"] == "completed" else "⏳"
            print(f"\n{status_icon} {version}")
            print(f"   Created: {data['created_at']}")
            print(f"   Journal: {data['target_journal']}")
            print(f"   Status: {data['status']}")
            if data['git_tags']:
                print(f"   Tags: {', '.join(data['git_tags'])}")
            if data['notes']:
                print(f"   Notes: {data['notes']}")

    def create_version(self, repo_name: str) -> str:
        """Create new version directory."""
        state = self._load_global_state()

        # Find next version number
        existing_versions = [
            int(v.split('_v')[1])
            for v in state["versions"].keys()
            if v.startswith(repo_name)
        ]
        next_version = max(existing_versions, default=0) + 1

        version_name = f"{repo_name}_v{next_version}"
        version_dir = self.manuscript_dir / version_name
        version_dir.mkdir(parents=True, exist_ok=True)

        # Update global state
        state["versions"][version_name] = {
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "status": "in_progress",
            "git_tags": [],
            "target_journal": None,
            "repository_commit": None,
            "notes": ""
        }
        state["current_version"] = version_name

        self._save_global_state(state)

        return version_name

    def compare_versions(self, v1: str, v2: str):
        """Compare two versions."""
        # Use git diff or file comparison
        # Show word count changes, citation changes, etc.
        pass

def main():
    parser = argparse.ArgumentParser(description="Manage manuscript versions")
    subparsers = parser.add_subparsers(dest="command")

    # List command
    subparsers.add_parser("list", help="List all versions")

    # Create command
    create_parser = subparsers.add_parser("new", help="Create new version")
    create_parser.add_argument("--repo-name", required=True)

    # Compare command
    compare_parser = subparsers.add_parser("compare", help="Compare versions")
    compare_parser.add_argument("v1")
    compare_parser.add_argument("v2")

    args = parser.parse_args()

    manager = VersionManager()

    if args.command == "list":
        manager.list_versions()
    elif args.command == "new":
        version = manager.create_version(args.repo_name)
        print(f"✓ Created new version: {version}")
    elif args.command == "compare":
        manager.compare_versions(args.v1, args.v2)

    return 0

if __name__ == "__main__":
    exit(main())
```

### Phase 4: Cleanup and Archival (Week 4)

#### 4.1 Configuration File

**New file**: `.rrwrite/config.yaml`

```yaml
versioning:
  strategy: semantic                # semantic | timestamp | hybrid
  auto_increment: true              # Auto-increment version number
  directory_format: "{repo}_v{version}"

git:
  auto_commit: true                 # Auto-commit after each stage
  commit_format: "[RRWrite] {stage}: {description}"
  auto_tag: false                   # Auto-tag major milestones
  author_name: "RRWrite"
  author_email: "rrwrite@research.ai"

file_versioning:
  sections: overwrite               # overwrite | version_suffix
  critique: version_suffix          # version_suffix | overwrite
  manuscript: overwrite
  evidence: append

tracking:
  checksum_algorithm: sha256
  track_dependencies: true
  track_performance: true
  track_git_commit: true

retention:
  enabled: true
  keep_versions: 5                  # Keep last N versions
  keep_days: 90                     # Keep versions from last N days
  keep_tagged: all                  # Always keep tagged versions
  archive_after_days: 30            # Archive after N days

resume:
  enabled: true                     # Allow resuming failed runs
  invalidate_on_input_change: true  # Rerun if inputs changed
  cache_intermediate: true          # Cache intermediate results
```

#### 4.2 Cleanup Script

**New file**: `scripts/rrwrite-cleanup.py`

```python
#!/usr/bin/env python3
"""Cleanup old manuscript versions based on retention policy."""

import argparse
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import yaml

class CleanupManager:
    """Manage cleanup of old manuscript versions."""

    def __init__(self, manuscript_dir: Path, config: dict):
        self.manuscript_dir = manuscript_dir
        self.config = config

    def get_versions_to_delete(self) -> List[Path]:
        """Determine which versions to delete based on policy."""
        versions = list(self.manuscript_dir.glob("*_v*/"))
        to_delete = []

        # Load global state for metadata
        global_state_file = self.manuscript_dir / ".rrwrite" / "global_state.json"
        with open(global_state_file) as f:
            global_state = json.load(f)

        # Sort by creation date
        versions_with_dates = []
        for v in versions:
            version_name = v.name
            created_at_str = global_state["versions"][version_name]["created_at"]
            created_at = datetime.fromisoformat(created_at_str)
            versions_with_dates.append((v, created_at, version_name))

        versions_with_dates.sort(key=lambda x: x[1])

        # Apply retention rules
        keep_count = self.config["retention"]["keep_versions"]
        keep_days = self.config["retention"]["keep_days"]
        cutoff_date = datetime.now() - timedelta(days=keep_days)

        for version_dir, created_at, version_name in versions_with_dates:
            # Always keep tagged versions
            if global_state["versions"][version_name]["git_tags"]:
                continue

            # Keep last N versions
            if versions_with_dates.index((version_dir, created_at, version_name)) >= len(versions_with_dates) - keep_count:
                continue

            # Keep recent versions
            if created_at > cutoff_date:
                continue

            # This version can be deleted
            to_delete.append(version_dir)

        return to_delete

    def archive_version(self, version_dir: Path):
        """Archive version to compressed tar.gz."""
        archive_dir = self.manuscript_dir / ".rrwrite" / "archive"
        archive_dir.mkdir(parents=True, exist_ok=True)

        archive_name = f"{version_dir.name}_{datetime.now().strftime('%Y%m%d')}.tar.gz"
        archive_path = archive_dir / archive_name

        shutil.make_archive(
            archive_path.with_suffix(''),
            'gztar',
            version_dir
        )

        return archive_path

    def cleanup(self, dry_run: bool = True):
        """Execute cleanup."""
        to_delete = self.get_versions_to_delete()

        if not to_delete:
            print("No versions to cleanup")
            return

        print(f"Found {len(to_delete)} versions to cleanup:")
        for v in to_delete:
            print(f"  - {v.name}")

        if dry_run:
            print("\n(Dry run - no files deleted)")
            return

        # Archive before delete
        for v in to_delete:
            print(f"Archiving {v.name}...")
            archive_path = self.archive_version(v)
            print(f"  Archived to: {archive_path}")

            print(f"Deleting {v.name}...")
            shutil.rmtree(v)

        print(f"✓ Cleanup complete")

def main():
    parser = argparse.ArgumentParser(description="Cleanup old manuscript versions")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be deleted")
    parser.add_argument("--manuscript-dir", type=Path, default=Path("manuscript"))
    args = parser.parse_args()

    # Load config
    config_file = Path(".rrwrite/config.yaml")
    with open(config_file) as f:
        config = yaml.safe_load(f)

    manager = CleanupManager(args.manuscript_dir, config)
    manager.cleanup(dry_run=args.dry_run)

    return 0

if __name__ == "__main__":
    exit(main())
```

---

## Usage Examples

### Example 1: Initial Manuscript Generation

```bash
# Run full pipeline
rrwrite run-all --repo /path/to/research-repo --journal "Nature Biotechnology"

# Creates:
# manuscript/research-repo_v1/
# - Git initialized
# - Auto-commits after each stage
# - State tracking with checksums
# - Final tag: draft-v1
```

### Example 2: Resume After Failure

```bash
# Pipeline fails during drafting
rrwrite run-all --repo /path/to/research-repo
# Error: Introduction generation failed

# Fix issue (e.g., update repository)
# Resume from failure point
rrwrite resume --output-dir manuscript/research-repo_v1

# RRWrite:
# ✓ plan: completed, inputs unchanged → SKIP
# ✓ research: completed, inputs unchanged → SKIP
# ✗ drafting: failed on introduction → RERUN from introduction
# ➡ assembly: not started → RUN after drafting completes
# ➡ critique: not started → RUN after assembly completes
```

### Example 3: Regenerate One Section

```bash
# Critique suggests improving introduction
rrwrite draft --section introduction --force

# RRWrite:
# - Regenerates introduction.md (overwrites)
# - Git commit: "Regenerate introduction addressing critique feedback"
# - Updates checksums
# - Increments rerun_count
# - Dependent stages (assembly) now stale
```

### Example 4: Create Revision Version

```bash
# Reviewer comments received
# Create new version for major revision
rrwrite run-all --repo /path/to/research-repo --new-version

# Creates:
# manuscript/research-repo_v2/
# - Fresh Git repository
# - Fresh state tracking
# - Previous v1 preserved with tag "submission-v1"
```

### Example 5: Cleanup Old Versions

```bash
# Check what would be deleted
rrwrite cleanup --dry-run

# Execute cleanup
rrwrite cleanup

# Archives and deletes versions:
# - Older than 90 days
# - Beyond last 5 versions
# - Not tagged
```

---

## Migration Path

### Current Users (Existing Manuscripts)

**Option 1: Continue as-is**
- Existing manuscripts work unchanged
- New features optional

**Option 2: Migrate to new system**
```bash
# Initialize Git in existing version
cd manuscript/repo_v1/
git init
git add .
git commit -m "Migrate to new versioning system"

# Update state file format
python scripts/rrwrite-migrate-state.py --output-dir manuscript/repo_v1
```

### New Users

All new features enabled by default:
- Git auto-initialized
- Auto-commits enabled
- Smart resume available
- Checksum tracking active

---

## Testing Plan

### Unit Tests

1. **Checksum computation**
   - Test SHA256 calculation
   - Test file change detection
   - Test checksum persistence

2. **Dependency resolution**
   - Test dependency graph
   - Test needs_rerun logic
   - Test minimal rerun set calculation

3. **Git operations**
   - Test auto-commit
   - Test tagging
   - Test commit message formatting

4. **State management**
   - Test state schema validation
   - Test state updates
   - Test backward compatibility

### Integration Tests

1. **Full pipeline run**
   - Test all stages complete
   - Test Git commits created
   - Test checksums updated

2. **Resume functionality**
   - Test resume after failure
   - Test skip unchanged stages
   - Test rerun dependent stages

3. **Version management**
   - Test version creation
   - Test version listing
   - Test version comparison

4. **Cleanup**
   - Test retention policy
   - Test archival
   - Test deletion

---

## Configuration and Defaults

### Default Configuration

**File**: `templates/config_default.yaml`

```yaml
versioning:
  strategy: semantic
  auto_increment: true
  directory_format: "{repo}_v{version}"

git:
  auto_commit: true
  auto_tag: false

retention:
  enabled: true
  keep_versions: 5
  keep_days: 90
  keep_tagged: all

resume:
  enabled: true
  invalidate_on_input_change: true
```

### Per-Version Override

Users can create `.rrwrite/config.yaml` in version directory to override global defaults.

---

## Documentation Updates

### User Guide Updates

1. **New section**: "Version Management"
   - Explain semantic versioning
   - When to create new version
   - How to use Git tags

2. **New section**: "Resuming Failed Runs"
   - How resume works
   - When stages are skipped
   - How to force rerun

3. **Updated section**: "File Organization"
   - Git repository structure
   - State file explanation
   - Checksum tracking

### Developer Guide

1. **New section**: "State Schema v2.0"
   - Field descriptions
   - Backward compatibility
   - Migration guide

2. **New section**: "Dependency System"
   - Stage dependencies
   - Change detection
   - Rerun logic

---

## Success Criteria

✅ **Functional:**
- All outputs versioned automatically
- Git commits created after each stage
- Resume skips unchanged stages
- Version management commands work
- Cleanup respects retention policy

✅ **Performance:**
- Resume saves >50% time on partial reruns
- Checksum computation < 1 second for typical manuscript

✅ **Usability:**
- Works without user intervention (auto-commit optional)
- Clear error messages
- Backward compatible with existing manuscripts

✅ **Quality:**
- Full audit trail via Git
- Reproducible at any commit
- No data loss on failure

---

## Timeline

| Phase | Duration | Deliverables |
|-------|----------|--------------|
| Phase 1: Foundation | Week 1 | Enhanced state, checksums, Git auto-init/commit |
| Phase 2: Smart Resume | Week 2 | Dependency resolution, resume command |
| Phase 3: Version Management | Week 3 | Version commands, comparison tools |
| Phase 4: Cleanup | Week 4 | Retention policy, archival, cleanup |
| **Testing & Documentation** | Week 5 | Unit tests, integration tests, user guide |

**Total: 5 weeks**

---

## Questions for Review

1. **Git auto-commit default**: Should it be enabled by default or opt-in?
   - **Recommendation**: Enabled by default with clear opt-out (`--no-auto-commit`)

2. **Version directory format**: Stay with `repo_v1` or add timestamp `repo_v1_20260207`?
   - **Recommendation**: Stay with `repo_v1` (timestamp in state file)

3. **Retention policy defaults**: 5 versions, 90 days appropriate?
   - **Recommendation**: Yes, but make configurable

4. **Critique file versioning**: Version suffix `critique_v1.md` or overwrite?
   - **Recommendation**: Version suffix (compare iterations useful)

5. **PDF naming**: Include version in filename `manuscript_submission_v1.pdf`?
   - **Recommendation**: Yes, especially for submission vs revision

---

## Approval Checklist

- [ ] Architecture approved (Git + semantic directories)
- [ ] State schema v2.0 design approved
- [ ] Git integration approach approved (auto-commit, tagging)
- [ ] Resume logic approved (checksum-based change detection)
- [ ] Retention policy approved (keep 5 versions, 90 days, all tagged)
- [ ] Implementation phases approved (5 weeks timeline)
- [ ] Configuration defaults approved
- [ ] Migration path for existing users approved

---

**Status**: 📋 Ready for review and approval
**Next Step**: Approve plan → Begin Phase 1 implementation
