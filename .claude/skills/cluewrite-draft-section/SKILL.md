---
name: cluewrite-draft-section
description: Drafts a specific manuscript section using repository data and citation indices. Enforces fact-checking via Python tools.
allowed-tools:
context: fork
---
# Section Drafting Protocol

## Inputs
*   **Section Name:** (e.g., "Methods", "Results", "Introduction") provided by the user or plan.
*   **Context Files:** The list of code/data files identified in `manuscript/outline.md`.

## Workflow
1.  **Read Outline:** Read `manuscript/outline.md` to understand section requirements and evidence files.
2.  **Load Context:** Read the specified code/data files. DO NOT read unrelated files to save tokens.
3.  **Load Citations:** Read `references.bib` or `manuscript/literature_citations.bib` to find relevant citation keys.
4.  **Drafting:** Write the text in Markdown.
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

## Output and Naming (per schema: schemas/manuscript.yaml)

Write the section to `manuscript/SECTIONNAME.md` where SECTIONNAME is:
- `abstract.md` for Abstract
- `introduction.md` for Introduction
- `methods.md` for Methods
- `results.md` for Results
- `discussion.md` for Discussion
- `conclusion.md` for Conclusion

## Validation

After drafting, validate the section:
```bash
python scripts/cluewrite-validate-manuscript.py --file manuscript/SECTIONNAME.md --type section
```

Report validation status. If validation fails, fix issues and re-validate.
