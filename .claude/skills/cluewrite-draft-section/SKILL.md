---
name: cluewrite-draft-section
description: Drafts a specific manuscript section using repository data and citation indices. Enforces fact-checking via Python tools.
allowed-tools:
context: fork
---
# Section Drafting Protocol

## Inputs
*   **Section Name:** (e.g., "Methods") provided by the user or plan.
*   **Context Files:** The list of code/data files identified in `manuscript_plan.md`.

## Workflow
1.  **Load Context:** Read the specified code/data files. DO NOT read unrelated files to save tokens.
2.  **Load Citations:** Read `bib_index.md` to find relevant citation keys.
3.  **Drafting:** Write the text in Markdown.
    *   Use **LaTeX** for math (e.g., `$x^2$`).
    *   Use **[Key]** format for citations (e.g., `[smith2020]`).
    *   **Style:** Formal academic prose. Passive voice for Methods; Active voice for Results.

## Fact-Checking Requirement
**CRITICAL:** You must verify all numerical claims.
*   Before finalizing a sentence containing a number, locate that number in the source file (`*.csv` or `*.log`).
*   If the number involves a calculation (e.g., mean, p-value), generate a temporary Python script to compute it from the raw data and verify your claim.
*   **Command:** `python scripts/cluewrite-verify-stats.py --file <PATH> --col [NAME] --op [mean/max/min]`

## Figure referencing
*   Ensure every Figure mentioned is referenced as "Figure X" (capitalized).
*   Describe the figure content based on the generating script's logic (e.g., "Figure 1 visualizes the t-SNE projection...").

## Output
Append the drafted text to `cluewrite-drafts/section_name.md`.
