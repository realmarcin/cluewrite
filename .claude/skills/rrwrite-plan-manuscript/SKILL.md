---
name: rrwrite-plan-manuscript
description: Use after repository analysis completes and you need manuscript structure. Creates detailed outline with section content, word targets, evidence mapping. Do NOT use before analysis or when outline exists.
arguments:
  - name: target_dir
    description: Output directory for manuscript files (e.g., manuscript/repo_v1)
    default: manuscript
allowed-tools:
---
# Manuscript Planning Protocol

## Phase 0.5: Check Repository Analysis Status

Before beginning reconnaissance, check if repository analysis has been performed:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path('scripts').resolve()))
from rrwrite_state_manager import StateManager

manager = StateManager(output_dir="{target_dir}", enable_git=False)
state = manager.state

repo_analysis_status = state.get("workflow_status", {}).get("repository_analysis", {}).get("status")

if repo_analysis_status != "completed":
    print("")
    print("=" * 60)
    print("RECOMMENDATION: Run Repository Analysis First")
    print("=" * 60)
    print("")
    print("For best results, analyze your repository before planning:")
    print("  /rrwrite-analyze-repository --repo-path <path> --target-dir {target_dir}")
    print("")

    response = input("Proceed with planning without analysis? [y/N]: ").strip().lower()
    if response not in ['y', 'yes']:
        print("\nExiting. Please run repository analysis first.")
        sys.exit(0)
    else:
        print("\nProceeding with planning without repository analysis...")
else:
    print("✓ Repository analysis found - using existing analysis data")
```

## Phase 1: Repository Reconnaissance
1.  **Map Structure:** Execute `tree -L 2 --prune` to understand the project layout.
2.  **Locate Assets:**
    *   Find all data files (`*.csv`, `*.xlsx`) in `data/`.
    *   Find all analysis notebooks (`*.ipynb`) and scripts (`*.py`).
    *   Find all figures (`*.png`, `*.pdf`).
3.  **Read Context:** Read `README.md` and `PROJECT.md` to understand the project goals.

## Phase 1.5: Load Word Limit Configuration
Before planning sections, load the word limit configuration for the target journal:

```bash
python scripts/rrwrite-config-manager.py --journal {journal} --export
```

This returns:
- Total manuscript word limit
- Per-section word targets (min, target, max)
- Journal-specific formatting requirements

**IMPORTANT**: Use these limits when specifying word counts in the outline. The default 6000-word total ensures concise, focused manuscripts.

## Phase 2: Journal Template Selection
Ask the user for the target journal. Based on the response, adopt the corresponding structure:

### Option A: Nature Methods
*   **Structure:** Introduction -> Results -> Discussion -> Methods.
*   **Focus:** Novelty, Comparison to SOTA.
*   **Constraints:** Methods section limited; move extensive details to Supplementary.

### Option B: PLOS Computational Biology
*   **Structure:** Abstract -> Author Summary -> Introduction -> Results -> Discussion -> Methods.
*   **Focus:** Reproducibility, Biological Insight.
*   **Constraints:** Mandatory "Author Summary" (non-technical).

### Option C: Bioinformatics
*   **Structure:** Abstract -> Intro -> Algorithm -> Implementation -> Discussion.
*   **Focus:** Software utility, Performance benchmarks.

## Phase 3: Outline Synthesis
Generate a file named `{target_dir}/outline.md` (where {target_dir} is the output directory specified when calling this skill, default: manuscript). For each section in the template:
1.  **Write a Description:** What represents the core argument of this section?
2.  **Link Files:** Explicitly list the relative paths of the code/data files that support this section.
    *   *Example:* "Results > Section 2.1: Performance. Supports: `results/accuracy_table.csv`, `figures/fig2_roc.png`."
3.  **Word Count Target:** Use the word limits from Phase 1.5 configuration. Include min, target, and max for each section.

## Required Structure (per schema: schemas/manuscript.yaml)

The outline MUST include:
- Filename: `{target_dir}/outline.md`
- Target journal specification
- Sections with:
  - Section name (Abstract, Introduction, Methods, Results, Discussion)
  - Word count targets
  - Evidence files (data, scripts, figures)
  - Key points to cover

## Output and Validation

1. Create `{target_dir}/outline.md` with the structured plan
2. Validate the outline:
   ```bash
   python scripts/rrwrite-validate-manuscript.py --file {target_dir}/outline.md --type outline
   ```
3. Update workflow state (mark planning stage as completed):
   ```python
   import sys
   from pathlib import Path
   sys.path.insert(0, str(Path('scripts').resolve()))
   from rrwrite_state_manager import StateManager

   manager = StateManager(output_dir="{target_dir}")
   manager.update_workflow_stage("plan", status="completed", file_path="{target_dir}/outline.md")
   ```
4. Display progress:
   ```bash
   python scripts/rrwrite-status.py --output-dir {target_dir}
   ```
5. If validation passes, confirm creation and ask user to review
6. If validation fails, fix issues and re-validate

Confirm the creation of `{target_dir}/outline.md` and validation status. Show the updated workflow status.
