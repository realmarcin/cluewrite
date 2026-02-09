---
name: rrwrite-draft-section
description: Use when outline is complete and you need to draft a specific section (abstract, introduction, methods, results, discussion, availability). Do NOT use before outline exists or for entire manuscript at once. Enforces citation verification and fact-checking.
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

### Task Decomposition: The 2-5 Minute Rule

Break section drafting into verifiable micro-tasks (see `docs/2-5-minute-rule.md` for full pattern).

**Pattern:** Each task has (1) requirement, (2) action, (3) verification, (4) checkpoint.

**Example: Methods Section (800 words)**
- Task 1: Data collection paragraph (2 min, 180 words, 2-3 citations)
- Task 2: Analysis methods paragraph (3 min, 225 words, tool citations only)
- Task 3: Validation paragraph (2 min, 175 words)
- Task 4: Reproducibility paragraph (2 min, 125 words, URLs + versions)
- Task 5: Final assembly (1 min, verify total 705 words in 640-960 range)

**After each task:**
```python
from rrwrite_state_manager import StateManager
manager = StateManager(output_dir="{target_dir}")
manager.update_section_progress(section="{section}", completed_tasks=["task1"], total_tasks=5)
```

### Detailed Steps

1.  **Read Outline:** Read `{target_dir}/outline.md` to understand section requirements and evidence files.
2.  **Load Word Limits:** Check section-specific word limits:
    ```bash
    python scripts/rrwrite-config-manager.py --section {section_name}
    ```
    This ensures the draft meets the target word count (±20% variance allowed).
3.  **Load Context:** Read the specified code/data files. DO NOT read unrelated files to save tokens.
4.  **Load Citations:** Read `references.bib` or `{target_dir}/literature_citations.bib` to find relevant citation keys.
5.  **Drafting:** Write the text in Markdown using 2-5 minute task chunks, adhering to word limits from step 2.
    *   Use **LaTeX** for math (e.g., `$x^2$`).
    *   Use **[Key]** format for citations (e.g., `[smith2020]`).
    *   **Style:** Formal academic prose. Passive voice for Methods; Active voice for Results.
    *   **Verify each task** before moving to next (word count, citation validity)

## Fact-Checking Requirement
**CRITICAL:** You must verify all numerical claims.
*   Before finalizing a sentence containing a number, locate that number in the source file (`*.csv` or `*.log`).
*   If the number involves a calculation (e.g., mean, p-value), generate a temporary Python script to compute it from the raw data and verify your claim.
*   **Command:** `python scripts/rrwrite-verify-stats.py --file <PATH> --col [NAME] --op [mean/max/min]`

## Figure referencing
*   Ensure every Figure mentioned is referenced as "Figure X" (capitalized).
*   Describe the figure content based on the generating script's logic (e.g., "Figure 1 visualizes the t-SNE projection...").

## Table discovery and inclusion

### When to include tables

Include tables when:
1. Data communicates more clearly in tabular format than prose
2. Comparing 3+ items or showing multiple metrics
3. Within journal table limits (Bioinformatics: 5, Nature: 4, PLOS: 10)

### Discovering available data tables

Before drafting, check for pre-generated TSV tables from repository analysis:

```python
from pathlib import Path
import sys
sys.path.append(str(Path.cwd() / "scripts"))
from rrwrite_table_generator import TableSelector

# Check for available tables
data_tables_dir = Path("{target_dir}") / "data_tables"

if data_tables_dir.exists():
    available_tables = TableSelector.get_tables_for_section(
        section_name="{section_name}",
        data_tables_dir=data_tables_dir
    )

    print(f"Found {len(available_tables)} relevant data tables for {section_name}:")
    for table_info in available_tables:
        if table_info['exists']:
            print(f"  - {table_info['name']}")
```

### Loading and formatting tables

To include a table in your section:

```python
import pandas as pd
from rrwrite_table_generator import TableGenerator

# Load TSV table
df = pd.read_csv("data_tables/repository_statistics.tsv", sep='\t', comment='#')

# Optional: Filter or transform data
df = df.head(10)  # Limit to top 10 rows

# Format as markdown table
table_md = TableGenerator.format_markdown_table(
    df,
    caption="**Table 1: Repository composition by file type**",
    alignment={'file_count': 'right', 'total_size_mb': 'right'}
)

# Include in section text
section_text = f"""
The repository structure is summarized in Table 1, showing the distribution
of files across categories.

{table_md}

As shown in Table 1, the repository contains...
"""
```

### Table reference format

- **First mention:** "Table 1: Repository composition" (full caption)
- **Subsequent mentions:** "Table 1" or "(Table 1)"
- **Numbering:** Sequential across entire manuscript (Table 1, Table 2, Table 3...)

### Available table files

Tables generated during repository analysis:

| File | Content | Best for sections |
|------|---------|-------------------|
| `file_inventory.tsv` | Complete file listing with metadata | Results (filtered) |
| `repository_statistics.tsv` | Summary metrics by category | Methods, Results |
| `size_distribution.tsv` | File size distribution quartiles | Results |
| `research_indicators.tsv` | Detected research topics | Introduction, Methods |

## Section-Specific Guidelines

### Methods Section Citations

When drafting Methods sections, cite ONLY specific tools, datasets, and methodologies that were actually used:

**✅ Appropriate citations:**
- Specific software tools used (e.g., [LinkML2024] for schema validation)
- Datasets accessed (e.g., [GTDB2024] for taxonomic data)
- Published algorithms implemented (e.g., [Smith2020] for MaxPro design)
- Computational methods applied (e.g., [Jones2019] for embedding generation)
- Analysis frameworks employed (e.g., [pandas2023] for data processing)

**❌ Inappropriate citations:**
- Abstract principles (FAIR data sharing, reproducibility frameworks)
- General best practices papers
- Related tools NOT used in this work
- Methodological reviews unless specific method was implemented
- Workflow standards not explicitly followed

**Rationale:** Methods describes what YOU did, not general principles. Abstract concepts belong in Introduction (motivation) or Discussion (broader context).

**Example (correct):**
```markdown
Schema validation was performed using LinkML specifications [LinkML2024].
```

**Example (incorrect):**
```markdown
All data followed FAIR principles [Wilkinson2016].
```

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

### Results Section Citations

When drafting Results sections, cite ONLY to report what was observed or measured, not to explain concepts or provide justification:

**✅ Appropriate citations:**
- Papers/datasets that were analyzed or benchmarked against (e.g., [Smith2020] for comparison dataset)
- Examples of findings from your analysis (e.g., "identified 29 papers including [ExamplePaper2024]")
- Tools whose performance was measured (e.g., [Tool2024] achieved 85% accuracy in our tests)
- Specific data sources that were processed (e.g., analyzed sequences from [GTDB2024])

**❌ Inappropriate citations:**
- Explaining what concepts mean (e.g., "establishing provenance chains [citations]")
- Justifying why you did something (e.g., "addressing concerns about hallucination [citations]")
- Discussing future possibilities (e.g., "for future integration with standards [citations]")
- Providing background context or motivation

**Rationale:** Results reports OBSERVATIONS and MEASUREMENTS from your work. Explanations, justifications, and contextual citations belong in Introduction (motivation/background) or Discussion (interpretation/implications).

**Example (correct):**
```markdown
The literature search identified 29 papers spanning reproducible research [Wilkinson2016, Barker2022], computational notebooks [Pimentel2023], and AI-assisted writing [CHI2024, Ros2025].
```
(These are examples of papers found - actual results being reported)

**Example (incorrect):**
```markdown
Literature evidence tracking established provenance chains between claims and sources [Himmelstein2019, CliVER2024].
```
(This explains what provenance chains are/do, not reporting a measurement)

**Example (incorrect):**
```markdown
This evidence chain addresses concerns about hallucination in AI writing [CliVER2024].
```
(This justifies WHY we did something - belongs in Introduction or Discussion)

## Output and Naming (per schema: schemas/manuscript.yaml)

Write the section to `{target_dir}/SECTIONNAME.md` where SECTIONNAME is:
- `abstract.md` for Abstract
- `introduction.md` for Introduction
- `methods.md` for Methods
- `results.md` for Results
- `discussion.md` for Discussion
- `conclusion.md` for Conclusion
- `availability.md` for Data and Code Availability

## The Iron Law of Academic Drafting

**NO SECTION COMPLETION WITHOUT VERIFICATION CHECKLIST**

| Rationalization | Reality |
|-----------------|---------|
| "I'll fix citations after drafting all sections" | Citations-after = "what did I write about?" Citations-during = "what should I write about?" Missing citations means unsupported claims. |
| "Word count is close enough" | Journals auto-reject at word limit violations. ±20% ensures safety margin for editing. |
| "This is just a first draft, doesn't need perfect citations" | First drafts with incomplete citations → forgotten sources → plagiarism risk. Evidence tracking starts now. |
| "I can verify citations manually later" | Manual verification misses 40% of issues. Automated validation takes 5 seconds. |
| "The DOI check is too strict" | DOIs are permanent identifiers. If DOI fails now, it's unavailable to readers later. |

## Verification Gate (MANDATORY)

### BEFORE claiming section complete:

**1. IDENTIFY:** What proves this section is complete?
   → Validation command that checks word count, citations, structure

**2. RUN:** Execute validation fresh
```bash
python scripts/rrwrite-validate-manuscript.py \
  --file {target_dir}/SECTIONNAME.md \
  --type section
```

**3. READ:** Complete validation output, verify exit code

**4. VERIFY:** Do all checks pass?
   - [ ] Word count within ±20% of target
   - [ ] All citations have DOIs in literature_evidence.csv
   - [ ] No orphaned figure/table references
   - [ ] Required subsections present (if applicable)
   - [ ] Exit code = 0

**5. ONLY THEN:** Update StateManager with completion status

## State Update

After successful validation (exit code 0), update workflow state:
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

## If Validation Fails

**DO NOT:**
- Update state as complete
- Move to next section
- Rationalize failures away

**DO:**
1. Read complete error message
2. Fix specific issues listed
3. Re-run validation
4. Verify exit code = 0
5. Then update state
