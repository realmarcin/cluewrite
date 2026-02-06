# RRWrite Versioning and Progress Tracking Guide

This guide explains how RRWrite tracks your manuscript development progress, versions outputs, and manages workflow runs.

## Overview

RRWrite uses a **hybrid versioning approach** that combines:

1. **Git** - For collaboration and full history
2. **State tracking** - For workflow progress and provenance
3. **Workflow runs** - For archiving complete manuscripts
4. **Semantic versioning** - For critiques and major iterations

## Quick Start

### View Your Progress

```bash
# Basic status
python scripts/rrwrite-status.py

# Detailed status with file history
python scripts/rrwrite-status.py --detailed
```

### Archive a Complete Run

```bash
# Archive current state
python scripts/rrwrite-archive-run.py --description "nature-methods-v1"

# Archive with specific journal
python scripts/rrwrite-archive-run.py --journal "PLOS Computational Biology"
```

### Compare Two Runs

```bash
python scripts/rrwrite-compare-runs.py \
  manuscript/runs/2026-02-05_143022_nature-methods \
  manuscript/runs/2026-02-08_091530_plos-revised
```

---

## How It Works

### 1. Active Workspace (manuscript/)

Your day-to-day work happens in the `manuscript/` directory:

```
manuscript/
├── outline.md              # Latest outline
├── literature.md           # Latest literature review
├── abstract.md            # Latest sections
├── methods.md
├── results.md
├── critique_manuscript_v1.md   # Versioned critiques
├── critique_manuscript_v2.md
└── .rrwrite/
    └── state.json         # Progress tracking
```

**Key points:**
- Files are **Git-versioned** (commit regularly!)
- State file tracks which stages are complete
- Critiques use semantic versioning (`_v1`, `_v2`, etc.)

### 2. State Tracking (.rrwrite/state.json)

The state file tracks:
- **Workflow stages**: plan → research → draft → critique → assembly
- **Section progress**: Which sections are drafted
- **Critique iterations**: Review cycles and recommendations
- **Provenance**: Input files, verification runs, Git commits

**View state:**
```bash
python scripts/rrwrite-status.py
```

**Example output:**
```
RRWrite Project Status
======================
Project: protein-structure-prediction
Target Journal: Nature Methods
Last Updated: 2026-02-05 14:30

Workflow Progress:
  ✓ Planning (outline.md)
  ✓ Literature Research (23 papers)
  ⚠ Drafting (4/5 sections)
  ✓ Critique (v2 - Accept with Minor Revisions)
  ○ Final Assembly

Next Steps:
  1. Draft Discussion section
  2. Address critique issues (2 minor)
  3. Assemble final manuscript
```

### 3. Workflow Runs (manuscript/runs/)

Archive complete manuscripts as timestamped runs:

```
manuscript/runs/
├── 2026-02-05_143022_nature-methods/
│   ├── run_metadata.json
│   ├── outline.md
│   ├── literature.md
│   ├── abstract.md
│   ├── introduction.md
│   ├── methods.md
│   ├── results.md
│   ├── discussion.md
│   ├── full_manuscript.md
│   └── critique_manuscript_v1.md
│
└── 2026-02-08_091530_plos-revised/
    └── [complete manuscript files]
```

**Use cases:**
- Archive manuscript for different journals
- Save milestones before major revisions
- Compare different approaches

### 4. Git Versioning

All files are Git-tracked for:
- Collaboration with coauthors
- Full history and recovery
- Branching for different versions

**Best practice:**
```bash
# Commit after each significant change
git add manuscript/
git commit -m "Revise Methods: add sample size justification"

# RRWrite warns if you have uncommitted changes
```

---

## Workflow Examples

### Example 1: Starting a New Manuscript

```bash
# 1. Initialize project
cd /my/research/project
~/repo-research-writer/install.sh setup-project

# 2. Edit context
nano CLUEWRITE.md

# 3. Use skills in order
```

In your AI agent:
```
User: "Use /rrwrite-plan-manuscript for Nature Methods"
Claude: ✓ Created outline.md
        ✓ Workflow progress: Planning complete (1/5)

User: "Use /rrwrite-research-literature"
Claude: ✓ Found 23 papers
        ✓ Workflow progress: Research complete (2/5)

User: "Show status"
Claude: [Displays rrwrite-status.py output]
```

### Example 2: Iterating on Critiques

```bash
# First critique
Use /rrwrite-critique-manuscript for the full manuscript

# Output: critique_manuscript_v1.md
# Recommendation: MAJOR REVISIONS (3 major, 7 minor)

# Revise sections
Use /rrwrite-draft-section to revise Methods addressing sample size

# Second critique
Use /rrwrite-critique-manuscript for the full manuscript

# Output: critique_manuscript_v2.md
# Recommendation: ACCEPT WITH MINOR REVISIONS (0 major, 2 minor)
```

State file tracks both critique iterations:
```json
{
  "critique": {
    "iterations": [
      {
        "version": 1,
        "recommendation": "MAJOR_REVISIONS",
        "major_issues": 3,
        "minor_issues": 7
      },
      {
        "version": 2,
        "recommendation": "ACCEPT_WITH_MINOR_REVISIONS",
        "major_issues": 0,
        "minor_issues": 2
      }
    ]
  }
}
```

### Example 3: Archiving for Different Journals

```bash
# Finish Nature Methods version
python scripts/rrwrite-archive-run.py --description "nature-methods-v1"

# Now modify for PLOS (different structure, longer Methods, add Author Summary)
Use /rrwrite-draft-section for Author Summary
Use /rrwrite-draft-section to expand Methods section

# Archive PLOS version
python scripts/rrwrite-archive-run.py --description "plos-comp-bio-v1"

# Compare versions
python scripts/rrwrite-compare-runs.py \
  manuscript/runs/*nature-methods-v1 \
  manuscript/runs/*plos-comp-bio-v1
```

---

## File Naming Conventions

### Standard Sections
```
manuscript/abstract.md
manuscript/introduction.md
manuscript/methods.md
manuscript/results.md
manuscript/discussion.md
manuscript/conclusion.md  (optional)
```

### Critiques (Semantic Versioning)
```
manuscript/critique_outline_v1.md
manuscript/critique_outline_v2.md
manuscript/critique_literature_v1.md
manuscript/critique_manuscript_v1.md
manuscript/critique_manuscript_v2.md
```

**Pattern:** `critique_TYPE_vN.md`
- `TYPE`: outline, literature, section, manuscript
- `N`: Version number (increments with each iteration)

### Archived Runs
```
manuscript/runs/YYYY-MM-DD_HHMMSS_description/
```

**Pattern:** `YYYY-MM-DD_HHMMSS_descriptor`
- Timestamp for unique sorting
- Optional descriptor (journal name, milestone)

---

## Git Integration

### Automatic Checkpoint Warnings

RRWrite warns before overwriting files with uncommitted changes:

```
⚠️  Warning: Uncommitted changes detected

You have uncommitted changes in manuscript/
About to overwrite/modify: methods.md

Recommendation:
  git add manuscript/
  git commit -m "Save before regenerating methods.md"
```

### File History Tracking

State file records Git commits for provenance:

```json
{
  "workflow_status": {
    "plan": {
      "status": "completed",
      "file": "manuscript/outline.md",
      "completed_at": "2026-02-05T14:30:22",
      "git_commit": "a1b2c3d"
    }
  }
}
```

### Run Tagging

Archived runs create Git tags:

```bash
git tag run-2026-02-05_143022_nature-methods
```

---

## Collaboration

### Team Workflow

1. **State file in Git** - Tracks team progress
2. **Each author commits** independently
3. **Pull before running** skills
4. **Merge conflicts** handled by Git

**Example:**
```bash
# Before starting work
git pull

# After making changes
git add manuscript/
git commit -m "Draft Results section"
git push

# Check team progress
python scripts/rrwrite-status.py
```

### Working on Different Sections Simultaneously

Use Git branches:

```bash
# Author 1: Methods section
git checkout -b methods-revision
Use /rrwrite-draft-section for Methods
git commit -am "Revise Methods"

# Author 2: Discussion section
git checkout -b discussion-revision
Use /rrwrite-draft-section for Discussion
git commit -am "Revise Discussion"

# Merge when both done
git checkout main
git merge methods-revision
git merge discussion-revision
```

---

## Migration

### Migrating Existing Projects

If you have an existing RRWrite project without state tracking:

```bash
# Run migration script
python scripts/rrwrite-migrate-v1.py

# Output:
# ✓ State tracking enabled
# ✓ Detected files:
#   • Outline: outline.md
#   • Sections: abstract, introduction, methods
#
# Next: Commit migration
```

The migration script:
- Detects existing files
- Creates state.json with current progress
- Updates .gitignore
- Preserves all existing work

---

## Best Practices

### 1. Commit Frequently
```bash
# After each skill run
git add manuscript/
git commit -m "Descriptive message"
```

### 2. Archive Major Milestones
```bash
# Before major revisions
python scripts/rrwrite-archive-run.py --description "pre-revision-round-2"

# Before submitting
python scripts/rrwrite-archive-run.py --description "submitted-version"
```

### 3. Check Status Regularly
```bash
# See what's done and what's next
python scripts/rrwrite-status.py
```

### 4. Use Descriptive Run Names
```bash
# Good
python scripts/rrwrite-archive-run.py --description "nature-methods-final"

# Less helpful
python scripts/rrwrite-archive-run.py --description "version2"
```

### 5. Keep State File in Git
The `.rrwrite/state.json` file should be committed for collaboration:
```bash
git add manuscript/.rrwrite/state.json
git commit -m "Update workflow progress"
```

---

## Troubleshooting

### State File Issues

**Problem:** State file shows wrong progress

**Solution:** Edit manually or reinitialize
```bash
# View current state
cat manuscript/.rrwrite/state.json

# Reinitialize (backs up existing)
python scripts/rrwrite-state-manager.py init --project-name "my-project"
```

### Missing Files

**Problem:** Deleted a file that state thinks is complete

**Solution:** Recover from Git or re-generate
```bash
# Option 1: Recover from Git
git checkout manuscript/results.md

# Option 2: Recover from archived run
cp manuscript/runs/2026-02-05_*/results.md manuscript/

# Option 3: Re-generate
Use /rrwrite-draft-section for Results
```

### Merge Conflicts in State File

**Problem:** Two team members updated state simultaneously

**Solution:** Accept both changes (state is append-only for most fields)
```bash
# Merge conflict in state.json
# Usually safe to accept both versions and manually merge JSON

# Or: Let one person's changes win
git checkout --theirs manuscript/.rrwrite/state.json
```

---

## Advanced Features

### Provenance Tracking

State file captures verification runs:

```json
{
  "provenance": {
    "verification_runs": [
      {
        "timestamp": "2026-02-08T09:10:00",
        "script": "rrwrite-verify-stats.py",
        "file": "data/results.csv",
        "column": "accuracy",
        "operation": "mean",
        "result": 0.8734
      }
    ]
  }
}
```

### Custom Run Metadata

Archive runs include custom metadata:

```bash
# Archived run includes
# - All manuscript files
# - run_metadata.json with provenance
# - Git commit hash
# - Target journal
# - Creation timestamp
```

---

## Summary

| Aspect | Solution | When to Use |
|--------|----------|-------------|
| **Day-to-day work** | Git commits | After each change |
| **Progress tracking** | State file | Automatic (skills update) |
| **Complete manuscripts** | Archived runs | Major milestones, journal submissions |
| **Critique iterations** | Semantic versioning | After each review cycle |
| **Collaboration** | Git + state file | Working with coauthors |
| **Comparison** | Compare-runs script | Evaluating different approaches |

---

## Getting Help

```bash
# View status help
python scripts/rrwrite-status.py --help

# View archive help
python scripts/rrwrite-archive-run.py --help

# View compare help
python scripts/rrwrite-compare-runs.py --help

# View migrate help
python scripts/rrwrite-migrate-v1.py --help
```

For more information, see:
- `WORKFLOW.md` - Complete manuscript workflow
- `README.md` - Project overview
- `REFACTORING_SUMMARY.md` - Recent changes
