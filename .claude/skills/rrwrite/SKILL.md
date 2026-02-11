---
name: rrwrite
description: Generate manuscript from GitHub repo or local path with automated revision
arguments:
  - name: repository
    description: GitHub URL or local repository path
    required: true
  - name: output_dir
    description: Output directory for manuscript (e.g., manuscript/repo_v1)
    required: false
  - name: max_revisions
    description: After critique, automatically revise up to N times (0=disabled, default 0)
    default: 0
  - name: journal
    description: Target journal (bioinformatics, nature, plos)
    default: bioinformatics
allowed-tools:
context: fork
---
# RRWrite: Repository-to-Manuscript Workflow

User-friendly wrapper around `/rrwrite-workflow` with cleaner parameter names.

## Usage

```bash
/rrwrite --repository <path-or-url> --output-dir <manuscript-dir> --max-revisions <N>
```

## Implementation

This skill simply calls `/rrwrite-workflow` with parameter mapping:

```bash
# Map user-friendly parameters to workflow parameters:
# --repository → --repo_path
# --output-dir → --target_dir
# --max_revisions → --max_revisions (same)
# --journal → --journal (same)

/rrwrite-workflow \
  --repo_path {repository} \
  --target_dir {output_dir} \
  --max_revisions {max_revisions} \
  --journal {journal}
```

## Examples

```bash
# Full workflow with 2 automated revisions
/rrwrite --repository /path/to/repo --output-dir manuscript/repo_v4 --max-revisions 2

# Without automated revision (default)
/rrwrite --repository /path/to/repo --output-dir manuscript/repo_v4

# With specific journal
/rrwrite --repository /path/to/repo --output-dir manuscript/repo_v4 --journal nature --max-revisions 2
```

## What It Does

1. **Analyze repository** → Extract structure, generate data tables
2. **Plan manuscript** → Create outline with section targets
3. **Assess journal** → Match to journal requirements
4. **Research literature** → Find citations, build evidence database
5. **Draft sections** → Write all manuscript sections
6. **Assemble manuscript** → Combine sections with figures
7. **Critique** → Run content and format review
8. **Revise (if max_revisions > 0)** → Automatically revise with convergence detection

See `/rrwrite-workflow` documentation for detailed phase-by-phase breakdown.
