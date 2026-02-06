---
name: cluewrite-plan-manuscript
description: Analyzes the repository structure and generates a detailed manuscript outline based on target journal guidelines (Nature, PLOS, Bioinformatics).
allowed-tools:
---
# Manuscript Planning Protocol

## Phase 1: Repository Reconnaissance
1.  **Map Structure:** Execute `tree -L 2 --prune` to understand the project layout.
2.  **Locate Assets:**
    *   Find all data files (`*.csv`, `*.xlsx`) in `data/`.
    *   Find all analysis notebooks (`*.ipynb`) and scripts (`*.py`).
    *   Find all figures (`*.png`, `*.pdf`).
3.  **Read Context:** Read `README.md` and `CLUEWRITE.md` to understand the project goals.

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
Generate a file named `manuscript/outline.md`. For each section in the template:
1.  **Write a Description:** What represents the core argument of this section?
2.  **Link Files:** Explicitly list the relative paths of the code/data files that support this section.
    *   *Example:* "Results > Section 2.1: Performance. Supports: `results/accuracy_table.csv`, `figures/fig2_roc.png`."
3.  **Word Count Target:** Specify estimated word count for each section.

## Required Structure (per schema: schemas/manuscript.yaml)

The outline MUST include:
- Filename: `manuscript/outline.md`
- Target journal specification
- Sections with:
  - Section name (Abstract, Introduction, Methods, Results, Discussion)
  - Word count targets
  - Evidence files (data, scripts, figures)
  - Key points to cover

## Output and Validation

1. Create `manuscript/outline.md` with the structured plan
2. Validate the outline:
   ```bash
   python scripts/cluewrite-validate-manuscript.py --file manuscript/outline.md --type outline
   ```
3. If validation passes, confirm creation and ask user to review
4. If validation fails, fix issues and re-validate

Confirm the creation of `manuscript/outline.md` and validation status.
