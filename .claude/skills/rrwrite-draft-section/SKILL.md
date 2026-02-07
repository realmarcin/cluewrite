---
name: rrwrite-draft-section
description: Drafts a specific manuscript section using repository data and citation indices. Enforces fact-checking via Python tools.
arguments:
  - name: target_dir
    description: Output directory for manuscript files (e.g., manuscript/repo_v1)
    default: manuscript
allowed-tools:
context: fork
---
# Section Drafting Protocol

## Inputs
*   **Section Name:** (e.g., "Methods", "Results", "Introduction") provided by the user or plan.
*   **Target Directory:** Output directory for manuscript files (e.g., manuscript/repo_v1), default: manuscript
*   **Context Files:** The list of code/data files identified in `{target_dir}/outline.md`.

## Workflow
1.  **Read Outline:** Read `{target_dir}/outline.md` to understand section requirements and evidence files.
2.  **Load Word Limits:** Check section-specific word limits:
    ```bash
    python scripts/rrwrite-config-manager.py --section {section_name}
    ```
    This ensures the draft meets the target word count (±20% variance allowed).
3.  **Load Context:** Read the specified code/data files. DO NOT read unrelated files to save tokens.
4.  **Load Citations:** Read `references.bib` or `{target_dir}/literature_citations.bib` to find relevant citation keys.
5.  **Drafting:** Write the text in Markdown, adhering to word limits from step 2.
    *   Use **LaTeX** for math (e.g., `$x^2$`).
    *   Use **[Key]** format for citations (e.g., `[smith2020]`).
    *   **Style:** Formal academic prose. Passive voice for Methods; Active voice for Results.

## Fact-Checking Requirement
**CRITICAL:** You must verify all numerical claims.
*   Before finalizing a sentence containing a number, locate that number in the source file (`*.csv` or `*.log`).
*   If the number involves a calculation (e.g., mean, p-value), generate a temporary Python script to compute it from the raw data and verify your claim.
*   **Command:** `python scripts/rrwrite-verify-stats.py --file <PATH> --col [NAME] --op [mean/max/min]`

## Figure referencing
*   Ensure every Figure mentioned is referenced as "Figure X" (capitalized).
*   Describe the figure content based on the generating script's logic (e.g., "Figure 1 visualizes the t-SNE projection...").

## Section-Specific Guidelines

### Data and Code Availability Section
When drafting the Availability (or "Data and Code Availability") section:

**Should include:**
- Repository URL (GitHub, GitLab, etc.)
- License information (MIT, Apache, GPL, etc.)
- Installation instructions or reference to installation docs
- Documentation locations
- Data repository locations (Zenodo, Figshare, Dryad, etc.)
- Software version or DOI if available
- System requirements (Python version, dependencies)

**Should NOT include:**
- General methodology citations (FAIR principles, reproducibility papers)
- Citations unless specifically about tools/platforms (e.g., [zenodo2023] for Zenodo DOI, [docker2024] for containerization)
- Research methodology or background information
- Discussion of data analysis approaches

**Format:** Concise, factual statements. 50-150 words typical.

**Example (correct):**
```markdown
# Data and Code Availability

Source code is available at https://github.com/user/project under the MIT license.
Installation requires Python 3.10+ and can be completed via `pip install project`.
Complete documentation is hosted at https://project.readthedocs.io.
All experimental data are deposited in Zenodo (DOI: 10.5281/zenodo.1234567).
```

**Example (incorrect - has inappropriate citations):**
```markdown
... complete documentation following FAIR principles [Wilkinson2016].
```

## Output and Naming (per schema: schemas/manuscript.yaml)

Write the section to `{target_dir}/SECTIONNAME.md` where SECTIONNAME is:
- `abstract.md` for Abstract
- `introduction.md` for Introduction
- `methods.md` for Methods
- `results.md` for Results
- `discussion.md` for Discussion
- `conclusion.md` for Conclusion
- `availability.md` for Data and Code Availability

## Validation

After drafting, validate the section:
```bash
python scripts/rrwrite-validate-manuscript.py --file {target_dir}/SECTIONNAME.md --type section
```

## State Update

After successful validation, update workflow state:
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path('scripts').resolve()))
from rrwrite_state_manager import StateManager

manager = StateManager(output_dir="{target_dir}")
manager.add_section_completed("SECTIONNAME")  # e.g., "methods", "results"
```

Display updated progress:
```bash
python scripts/rrwrite-status.py --output-dir {target_dir}
```

Report validation status and updated workflow progress. If validation fails, fix issues and re-validate.
