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
Generate a file named `manuscript_plan.md`. For each section in the template:
1.  **Write a Description:** What represents the core argument of this section?
2.  **Link Files:** Explicitly list the relative paths of the code/data files that support this section.
    *   *Example:* "Results > Section 2.1: Performance. Supports: `results/accuracy_table.csv`, `figures/fig2_roc.png`."

## Output
Confirm the creation of `manuscript_plan.md` and ask the user to review the logical flow.
