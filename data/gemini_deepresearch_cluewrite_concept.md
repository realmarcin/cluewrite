Automated Manuscript Generation Systems: A Repository-Driven Agentic Framework
1. Introduction: The Agentic Turn in Scientific Publishing
The convergence of computational research and generative artificial intelligence has precipitated a fundamental shift in the scientific workflow. Historically, the translation of raw experimental data—residing in code repositories, Jupyter notebooks, and heterogeneous data files—into a coherent, publication-ready manuscript has been a manual, labor-intensive process prone to transcription errors and narrative inconsistencies. The emergence of "Claude Code" and its associated "Agent Skills" architecture offers a solution to this bottleneck, enabling the construction of autonomous pipelines that treat the GitHub repository not merely as a storage backend, but as the primary input vector for deterministic manuscript generation.1
This report provides an exhaustive technical analysis and implementation guide for architecting a "Scientific Writer" system within the Claude ecosystem. Unlike generic chatbots that operate on transient context, this system leverages the persistent, file-system-aware capabilities of Claude Code to ingest, analyze, plan, draft, and review scientific literature directly from the source code. The analysis is grounded in the principle of progressive disclosure, a design pattern that manages the immense complexity of scientific publishing—ranging from Nature Methods formatting constraints to Bioinformatics citation styles—by compartmentalizing capabilities into modular, interlinked skills.3
We posit that the optimal approach for a repository-driven writing system is not a monolithic "Write Paper" command, but a federated network of specialized skills (Planning, Archiving, Drafting, Reviewing) orchestrated by a central context manager. This modular architecture allows for the integration of deterministic Python tools for fact-checking, ensuring that the quantitative claims in the manuscript are mathematically consistent with the underlying CSV data and analysis scripts.5
2. Architectural Foundations of Repository-Driven Writing
The transition from standard prompting to "Agent Skills" requires a rigorous definition of the system architecture. A skill in Claude Code is defined by a SKILL.md file located in a .claude/skills/ directory, containing YAML frontmatter for configuration and Markdown instructions for execution logic. However, for a system tasked with writing a 15,000-word thesis or a rigorous journal article, the architecture must support state persistence, complex dependency management, and tool execution.
2.1 The Hybrid "K-Dense" Architecture
Analysis of existing scientific writing plugins, such as the K-Dense-AI framework, reveals that high-performance agentic systems employ a hybrid architecture combining hierarchical planning with specialized execution tools.7 This contrasts with "flat" architectures where a single agent attempts to handle all tasks. The hybrid model separates Context (Project State) from Capability (Skill Logic).

Architectural Component
Responsibility
Implementation Artifact
Global Context
Maintains the "Memory" of the project: current hypothesis, manuscript status, and stylistic preferences.
CLAUDE.md (Root Directory) 9
Capability Store
Defines the atomic actions the agent can perform: "Summarize Data", "Draft Methods", "Verify Statistics".
.claude/skills/*/SKILL.md
Execution Layer
Performs deterministic operations: parsing BibTeX, running statistical checks, cleaning notebooks.
scripts/*.py (Python Tools) 3
Orchestrator
Manages the flow of information between skills, handling subagent delegation for parallel tasks.
plan-manuscript Skill (Planner) 11

2.2 Progressive Disclosure and Token Management
A primary constraint in processing scientific repositories is the context window. A typical repository might contain gigabytes of data and code. Loading the entire codebase is infeasible. The "Agent Skills" standard utilizes progressive disclosure to solve this.3
Level 1 (Discovery): The agent sees only the name and description of the skill in the YAML frontmatter. This costs minimal tokens.
Level 2 (Activation): When the agent invokes a skill (e.g., extract-results), it loads the instruction body of that specific SKILL.md.
Level 3 (Deep Dive): If the skill requires specific reference materials (e.g., the 50-page Nature style guide), these are stored in separate files (e.g., templates/nature_guide.md) and only read if the specific conditional logic in the skill triggers it.3
This mechanism allows the system to support dozens of journal formats and data types without overwhelming the agent's working memory, a critical requirement for generating high-quality, hallucination-free text.4
2.3 The Role of CLAUDE.md in State Persistence
While skills define what the agent can do, CLAUDE.md defines what is currently happening. In a manuscript generation workflow, CLAUDE.md acts as the project's "ledger".10
It records the Target Journal (e.g., "Targeting Bioinformatics, strict 7-page limit").
It tracks Section Status (e.g., "Introduction: Complete", "Results: Drafting").
It stores Key Findings summarized from the code, preventing the agent from needing to re-read raw data files constantly.9
The interaction between the ephemeral SKILL.md and the persistent CLAUDE.md is what enables "long-horizon" tasks like writing a full paper over multiple sessions.12
3. The Ingestion Layer: From Code to Context
Before a single sentence can be written, the repository must be ingested and semantically mapped. Scientific repositories often contain "noise"—large binary data, redundant logs, and complex directory structures—that must be filtered to extract the "Signal" (methodology, results, logic).13
3.1 The "Smart Ingest" Protocol
We define a specialized skill, ingest-repo, tasked with creating a "Cognitive Map" of the project. This skill leverages the Bash tool to execute a traversal script (often based on gitingest logic) that generates a condensed representation of the codebase.13
3.1.1 Handling Jupyter Notebooks (.ipynb)
Jupyter notebooks are the lingua franca of computational science but are notoriously poor inputs for LLMs due to their raw JSON structure and embedded base64 images, which inflate token counts significantly without adding semantic value.15 The ingestion skill must implement a cleaning routine:
Parse JSON: Read the .ipynb file structure.
Strip Outputs: Remove output cells containing image blobs or massive text dumps.
Extract Semantics: Retain markdown cells (which often contain the scientist's reasoning) and code cells.
Format Conversion: Convert the retained content into a flat Python script or a Markdown document with explicit cell delimiters.
This process reduces the token load of a notebook by up to 94%, as demonstrated in optimization case studies.15 The resulting "clean" file is what the drafting agent reads, not the raw notebook.
3.1.2 BibTeX Extraction and Indexing
Hallucinated citations are a cardinal sin in scientific writing. To prevent this, the ingestion layer must index the project's references.bib or .bbl files. We employ a Python script (extract_bib.py) that parses these files and generates a lookup index.17
Input: references.bib (often thousands of lines).
Process: Python's bibtexparser library extracts the citation key, title, author, and year.
Output: A searchable index file (bib_index.md) containing compact entries: [smith2020]: "Title of Paper" (2020).
This index allows the drafting agent to identify the correct citation key (e.g., \cite{smith2020}) by searching for keywords in the title, without needing to load the full BibTeX database into context.19
3.2 The Repository Map
The output of the ingestion phase is a high-level summary stored in CLAUDE.md or a temporary repo_map.md. This summary includes:
Data Dictionary: A list of CSVs in data/processed/ with their column headers (extracted via head -n 1).
Methodology Graph: A mapping of which scripts generate which figures (e.g., plot_fig1.py -> figures/fig1.png). This allows the writer to attribute the correct methodology to each visual result.21
4. The Planning Engine: Structuring the Narrative
Once the repository is mapped, the "Planner" skill (plan-manuscript) is engaged. This skill is responsible for architectural decision-making: selecting the target journal template and outlining the narrative arc.22
4.1 Journal-Specific Constraints and Templates
Scientific journals impose rigid structural constraints. The Planning Skill must possess a library of templates that enforce these rules. A comparison of key journal requirements highlights the necessity of this specialization.23

Journal
Structure Flow
Key Constraints
Citation Style
Nature Methods
Intro  Results  Discussion  Methods
Methods section at the end; emphasis on utility and novelty; strict length limits.
Superscript Number `` 24
Bioinformatics
Abstract  Intro  System/Methods  Implementation  Discussion
Requires "Data Availability" section; focus on algorithmic novelty.
Name-Year (Smith, 2020) 27
PLOS Comp Bio
Abstract  Author Summary  Intro  Results  Discussion  Methods
Mandatory "Author Summary" (non-technical abstract); extensive reproducibility requirements.
Numbered `` 26

The Planning Skill prompts the user to select a target journal. Based on the selection, it loads the corresponding structural template (e.g., .claude/skills/scientific-planning/templates/nature_methods.md).
4.2 The "Story Arc" Synthesis
The Planner analyzes the "Key Findings" (extracted during ingestion) and maps them to the journal template.
Input: repo_map.md, Key Findings, Target Journal Template.
Process: The agent uses "Chain of Thought" reasoning to order the results logically.28
Step 1: Identify the primary claim (e.g., "Method X outperforms Y").
Step 2: Select the figure that proves this claim (e.g., fig_accuracy.png).
Step 3: Assign this pair to the "Results" section.
Step 4: Identify the code describing Method X (e.g., src/model.py) and assign it to the "Methods" section.
Output: A highly detailed outline.md where every subsection is annotated with the specific file paths containing the supporting evidence.
This explicit linking of Claim  File is the defining feature of a repository-driven workflow, preventing the "hallucination of provenance" where models attribute results to non-existent experiments.11
5. The Drafting Engine: Text Generation with Verification
The "Drafting" phase involves the heavy lifting of text generation. To manage the complexity and length (often 10,000+ words for full manuscripts), we utilize a modular "Drafting Engine" composed of the draft-section skill and a suite of Python verification tools.
5.1 Subagent Delegation (context: fork)
Writing a robust "Methods" section requires a different context than writing the "Discussion." The Methods section needs access to code files; the Discussion needs access to literature notes. Loading all files simultaneously dilutes the context. We employ the Subagent Pattern using the context: fork directive in the skill definition.11
The Orchestrator: Loops through the outline.md.
The Worker: For each section, the Orchestrator forks a new subagent.
"You are now the Methods Writer. Read src/main.py and src/preprocessing.py. Draft the 'Data Processing' section following the PLOS style guide."
The Merge: The subagent returns the Markdown text, which the Orchestrator appends to the master draft.
This isolation ensures that variable names from the code (e.g., df_clean, p_val_array) are fresh in the subagent's memory, leading to precise technical descriptions.
5.2 The "Fact-Checking Loop" Implementation
A critical requirement for scientific AI is the elimination of numerical hallucinations. The Drafting Engine integrates a Fact-Checking Loop directly into the generation process.5 We define a Python tool verify_stats.py that the agent must use when reporting results.
The Workflow:
Generation: The agent drafts a sentence: "The model achieved an accuracy of 96.5%."
Detection: The skill instruction forces the agent to identify numerical claims.
Verification: The agent executes python verify_stats.py --file results.csv --col accuracy --op max.
Correction:
If the script returns 0.965, the text stands.
If the script returns 0.962, the agent rewrites the sentence to "96.2%".
This Tool-Augmented Generation ensures that the manuscript is a faithful representation of the data files, creating a "verifiable chain of evidence" from CSV to PDF.3
5.3 Handling Mathematical Notation and Equations
Scientific manuscripts rely heavily on LaTeX for mathematical precision. The Drafting Skill must be instructed to use standard LaTeX delimiters (e.g., $equation$) within the Markdown text.
Constraint: "All variable names in the text must match the variable names in the Python code."
Implementation: If the Python code uses sigma_val, the text should reference  (sigma). The drafting skill uses the Read tool to scan the Python code for variable definitions and map them to their mathematical symbols, ensuring consistency between the algorithm's implementation and its theoretical description.21
6. The Review System: Adversarial Compliance
The final phase is the "Reviewer" skill (review-manuscript). This skill adopts an adversarial persona to simulate the peer review process, focusing on compliance and logical rigor.30
6.1 Journal-Specific Compliance Checklists
The Reviewer Skill loads a checklist specific to the target journal defined in CLAUDE.md.
PLOS Computational Biology: Checks for the presence of a "Data Availability Statement" and ensures that code repositories are linked. It also verifies that the "Author Summary" is distinct from the Abstract.26
Nature Methods: Checks the length of the Methods section. If it exceeds the limit, it suggests moving technical details to "Supplementary Information".24
Bioinformatics: Verifies that the Abstract follows the structured format (Motivation, Results, Availability).27
6.2 Automated Stylistic Linting
Beyond semantic review, the skill employs "Linting Scripts" to enforce stylistic norms.
Passive Voice Detection: A script checks for overuse of passive voice (e.g., "It was shown that...").
Acronym Consistency: A script scans the text to ensure that every acronym (e.g., "SOTA") is defined in parentheses upon its first occurrence.34
Figure Reference Check: A script uses regex to ensure that every figure file in the directory (e.g., Fig1.png) is referenced in the text (e.g., "Figure 1 shows...").21
7. Implementation Specifications: The Skill Files
The following section provides the concrete implementation details for the core skills. These files should be placed in the .claude/skills/ directory of the repository.
7.1 The Planner Skill (.claude/skills/plan-manuscript/SKILL.md)

YAML


---
name: plan-manuscript
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
3.  **Read Context:** Read `README.md` and `CLAUDE.md` to understand the project goals.

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


7.2 The Writer Skill (.claude/skills/draft-section/SKILL.md)

YAML


---
name: draft-section
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
*   **Command:** `python scripts/verify_stats.py --file <PATH> --col [NAME] --op [mean/max/min]`

## Figure referencing
*   Ensure every Figure mentioned is referenced as "Figure X" (capitalized).
*   Describe the figure content based on the generating script's logic (e.g., "Figure 1 visualizes the t-SNE projection...").

## Output
Append the drafted text to `drafts/section_name.md`.


7.3 The Reviewer Skill (.claude/skills/review-manuscript/SKILL.md)

YAML


---
name: review-manuscript
description: adversarial review of the draft against journal checklists and data integrity checks.
allowed-tools:
---
# Peer Review Simulation

## Persona
You are "Reviewer #2"—critical, demanding, and focused on reproducibility.

## Compliance Checks
1.  **Journal Specifics:**
    *   *Nature:* Check word count of the Abstract (max 150 words).
    *   *PLOS:* Verify presence of "Data Availability Statement" and "Ethics Statement".
    *   *Bioinformatics:* Check that the "Abstract" has structured headers.
2.  **Citation Integrity:**
    *   Scan text for citation keys (e.g., `[smith2020]`).
    *   Verify they exist in `bib_index.md`.
    *   Flag any missing keys as "HALLUCINATION RISK".
3.  **Figure Callouts:**
    *   Ensure logical ordering (Figure 1 appears before Figure 2).
    *   Flag any figures in the `figures/` folder that are not referenced in the text.

## Prose Linting
Run the prose linter:
`python scripts/lint_manuscript.py drafts/full_manuscript.md`

## Output
Generate a review report `critique_round_1.md` with:
*   **Major Revisions:** (Scientific gaps, missing data).
*   **Minor Revisions:** (Formatting, typos).
*   **Action Items:** Specific instructions for the `draft-section` skill to fix errors.


8. Operational Workflows and Orchestration
Operating this system requires a defined workflow that guides the user from repository initialization to final PDF generation.
8.1 The "Bootstrap" Command
The user begins by initializing the environment. A /init-paper command (defined in .claude/commands/init-paper.md) scaffolds the necessary directory structure:

Bash


mkdir -p .claude/skills drafts figures data scripts
touch .claude/CLAUDE.md
# Downloads the standard Python scripts (verify_stats.py, etc.)


This command ensures that the "Agent Skills" have the necessary runtime environment to execute.10
8.2 The Execution Loop
Ingest: User runs /ingest-repo. The system maps the file tree and indexes BibTeX.
Plan: User runs /plan-manuscript. The agent asks for the target journal and generates manuscript_plan.md.
Iterative Drafting:
User: "Draft the Methods section."
Agent (Skill: draft-section): Reads the plan, identifies src/processing.py, reads it, drafts the text, runs verify_stats.py to check sample sizes, and saves to drafts/methods.md.
Review: User runs /review-manuscript. The agent critiques the draft.
Refine: User asks the agent to apply the fixes.
Compile: A final skill, compile-pdf, uses pandoc with the appropriate journal .csl style file to generate the final PDF.21
8.3 Handling Complex Data Dependencies
For manuscripts involving heavy data analysis, the system supports a "Re-run" workflow. If the underlying data changes (e.g., data/results.csv is updated with new experiments), the user can trigger a "Consistency Check." The review-manuscript skill iterates through all verifiable claims in the text and re-runs verify_stats.py. If the new data contradicts the old text (e.g., accuracy dropped from 96% to 94%), the agent flags the section for redrafting. This capability essentially provides Continuous Integration (CI) for Scientific Manuscripts.36
9. Data & Visualization Integrity: The Visualizer Skill
A manuscript is not just text; it is a synthesis of text and visual evidence. The "Visualizer" skill is designed to ensure semantic consistency between the figures and their captions.
9.1 Figure Introspection
Since the LLM cannot "see" the PNG files directly (or sees them only at a high token cost), the Visualizer skill relies on "Introspection of the Generating Code."
Logic: To describe Figure 1, the agent reads scripts/plot_fig1.py.
Extraction: It identifies the variables plotted (x-axis: time, y-axis: error_rate), the title, and the legend labels.
Caption Generation: Using this code-derived understanding, it generates a caption: "Figure 1: Error rate over time. The error rate decreases exponentially, reaching convergence at t=100, as calculated by the calc_error function in src/metrics.py."
This method ensures that the caption accurately reflects the data processing pipeline, even if the agent cannot visually inspect the pixel data.21
9.2 Table Generation from Dataframes
For tabular data, the system avoids manual formatting. The draft-section skill uses a Python tool to convert Pandas DataFrames directly into Markdown or LaTeX tables.
Command: python scripts/df_to_latex.py data/summary_stats.csv --caption "Summary Statistics"
Result: A perfectly formatted LaTeX table snippet that is injected into the manuscript draft. This eliminates transcription errors where rows/columns might be transposed during manual entry.37
10. Conclusion
The architecture presented in this report transforms the scientific writing process from a manual art into a rigorous, verifiable engineering discipline. By leveraging the "Agent Skills" framework within Claude Code, we can construct a system that is:
Context-Aware: Deeply integrated with the repository's code and data structures.
Journal-Compliant: adaptable to the rigid constraints of Nature, PLOS, and Bioinformatics.
Factually Robust: Protected against hallucination through deterministic Python verification loops.
Scalable: Capable of handling massive repositories through progressive disclosure and subagent delegation.
This "Repository-to-Manuscript" pipeline represents the future of reproducible research, where the manuscript is treated as a dynamic, compiled artifact of the scientific codebase rather than a static, detached document. The detailed skill specifications and Python toolchains provided herein serve as a blueprint for implementing this next-generation workflow.
References


"Claude skill" markdown file format.
9 - "Claude skill" markdown file format (Configuration Definitions).
2 - "Claude code" skills feature (Overview).
3 - "Claude code" skills feature (Progressive Disclosure).
4 - "Claude code" skills feature (Intro to Skills).
10 - "Claude code" explained: CLAUDE.md, commands, skills.
13 - mapping github repository to scientific manuscript workflow (GitIngest).
14 - mapping github repository to scientific manuscript workflow (LLM formatting).
23 - journal guidelines PLOS Computational Biology.
35 - python tools for scientific manuscript drafting (Pandoc).
21 - python tools for scientific manuscript drafting (Pandoc Research Paper).
20 - python tools for scientific manuscript drafting (BibTeX).
3 - "Claude Code" interlinked skills example architecture.
29 - "Claude Code" subagent execution skill pattern.
3 - "Claude Code" subagent execution skill pattern (Deep Dive).
17 - python script to extract bibtex from paper text.
18 - python script to extract bibtex (Biblib).
24 - Nature Methods manuscript structure requirements.
25 - Bioinformatics journal guidelines.
27 - Bioinformatics journal author guidelines.
26 - PLOS Computational Biology manuscript formatting requirements.
15 - python script to convert jupyter notebooks (IPYNB cleaning).
7 - Claude scientific writer plugin.
8 - K-Dense-AI scientific writer SKILL.md content.
30 - prompt for LLM to identify "key findings" (Persona).
5 - python function to verify manuscript numbers against csv.
11 - multi-agent orchestration for scientific writing.
6 - python script to cross-reference manuscript values.
33 - "Nature Methods" style guide.
Detailed Technical Analysis and Implementation Guide
Section A: Advanced Repository Ingestion Strategies
A.1 The GitIngest Integration
The efficacy of the "Planner" skill is directly proportional to the quality of the repository map it receives. As highlighted in snippet 13, tools like gitingest are essential for converting a directory tree into a single, token-optimized text stream. The ingest-repo skill should define a Bash command that runs a local version of this logic.
Token Optimization: The script must exclude files listed in .gitignore but also apply "Scientific Filters." For example, it should exclude data/raw/* (too large) but include data/processed/summary.csv (high information density).
Implementation: The Python script scripts/summarize_repo.py uses the os.walk method to build a text representation. Crucially, it should use the ast (Abstract Syntax Tree) module to parse Python files. Instead of including the full code, it extracts:
Class names and docstrings.
Function signatures.
Global variable definitions. This creates a "Semantic Skeleton" that fits within the context window while providing enough information for the Planner to understand the code's capability.38
A.2 The Jupyter Notebook "De-Noising" Protocol
As identified in 15, Jupyter notebooks are often 90% JSON overhead and base64 image strings. A dedicated Python script scripts/clean_ipynb.py is required.

Python


import json
import sys

def clean_notebook(filepath):
    with open(filepath, 'r') as f:
        nb = json.load(f)

    clean_cells = []
    for cell in nb['cells']:
        if cell['cell_type'] == 'markdown':
            clean_cells.append("".join(cell['source']))
        elif cell['cell_type'] == 'code':
            source = "".join(cell['source'])
            # Exclude plotting commands if they don't contain logic
            if "plt.show()" not in source:
                clean_cells.append(f"```python\n{source}\n```")

    return "\n".join(clean_cells)


The ingestion skill executes this script on all .ipynb files, saving the output to a temporary context/notebooks/ directory. The Planner then reads these cleaned text files, gaining access to the scientist's exploratory logic without the token cost of the UI overhead.15
Section B: Deep Dive into Verification Logic
B.1 The verify_stats.py Architecture
This tool is the "Source of Truth" for the manuscript. Its design must be robust enough to handle various data formats and statistical queries.5
Arguments:
--file: Path to the CSV/Excel file.
--filter: A SQL-like string to filter rows (e.g., age > 30).
--column: The column to analyze.
--metric: The statistic to compute (mean, std, count, p_value).
Logic: The script loads the data into a Pandas DataFrame, applies the filter, computes the metric, and prints the result.
Integration: The draft-section skill explicitly instructs the agent: "If you want to say 'The average age was 45', you must first run verify_stats.py --file demographics.csv --column age --metric mean and use the output value."
B.2 Handling Qualitative Data Verification
Not all facts are numbers. Some are boolean or categorical (e.g., "The gene BRCA1 was upregulated").
Text Search: The system uses grep to verify these claims in the result logs.
Skill Instruction: "To claim 'X is upregulated', find the line in results/gene_expression.txt that contains 'X' and 'upregulated'.".6
Section C: Journal-Specific Style Logic
C.1 Nature Methods Template Logic
For Nature Methods, the "Planner" skill constructs an outline that emphasizes methodological innovation over biological results.
Abstract: Must be "unstructured" and under 150 words. The skill loads a specific prompt: "Summarize the method first, then the application. Do not use headers.".33
Methods Section: The skill places a hard constraint: "The main text Methods is a summary. All technical details (hyperparameters, exact buffer compositions) must be written to supplementary_methods.md."
C.2 PLOS Computational Biology Logic
Author Summary: The Planner creates a dedicated section author_summary.md. The prompt for this section instructs the agent: "Rewrite the Abstract for a non-specialist audience. Avoid jargon like 'heteroscedasticity' or 'backpropagation'. Focus on the 'Why' and 'So What'.".26
Code Availability: The Reviewer skill scans the draft for a GitHub link. If missing, it halts the review and demands the user provide the URL.32
C.3 Bioinformatics Logic
Implementation Section: This journal specifically requests an "Implementation" section detailing the software stack. The Planner ensures this is distinct from the theoretical "Algorithm" section. The Drafting skill is instructed to list library versions (e.g., "PyTorch v1.9") in this section, extracting them from requirements.txt.27
Section D: Multi-Agent Orchestration with context: fork
The complexity of a 15,000-word report necessitates parallel processing. The "K-Dense" architecture 7 suggests using subagents to handle distinct components.
D.1 The "Editor-in-Chief" Pattern
The main session acts as the Editor. It holds the outline.md and the CLAUDE.md.
It spawns subagents (Workers) for specific tasks.
Worker 1 (Literature): "Read the bib_index.md and intro_notes.md. Write the Introduction."
Worker 2 (Statistician): "Read data/results.csv. Write the Results section. Run verify_stats.py for every number."
Worker 3 (Technician): "Read src/. Write the Methods section."
D.2 State Re-integration
When a subagent finishes, it writes its output to a file (e.g., drafts/intro.md). It does not return the full text to the Editor's context window (saving tokens). instead, it returns a summary: "Introduction drafted. Length: 1200 words. Key citations: [smith2020, doe2021]. Saved to drafts/intro.md." The Editor then updates CLAUDE.md with this status, marking the section as "Ready for Review".29
Section E: The Final Compilation
The final step is converting the Markdown drafts into a submission-ready PDF.
The compile-pdf skill wraps pandoc.
Template Injection: It selects the correct .csl (Citation Style Language) file based on the target journal (e.g., nature.csl or plos.csl).35
Cross-Referencing: It uses pandoc-crossref to resolve @fig:label citations to "Figure 1".
Command: pandoc drafts/*.md -o manuscript.pdf --bibliography references.bib --csl styles/nature.csl --filter pandoc-crossref. This ensures that the final styling (superscripts, bold vs italic, reference formatting) is handled by a robust engine, not by the LLM trying to "guess" the visual layout.21
Works cited
How to Actually Upload Claude Skills (Without Breaking Everything) - Medium, accessed February 3, 2026, https://medium.com/@creativeaininja/how-to-actually-upload-claude-skills-without-breaking-everything-1e8c436df2f2
What are Skills? | Claude Help Center, accessed February 3, 2026, https://support.claude.com/en/articles/12512176-what-are-skills
Equipping agents for the real world with Agent Skills - Anthropic, accessed February 3, 2026, https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
The Busy Person's Intro to Claude Skills (a feature that might be bigger than MCP) - Reddit, accessed February 3, 2026, https://www.reddit.com/r/ClaudeAI/comments/1pq0ui4/the_busy_persons_intro_to_claude_skills_a_feature/
PCAViz: An Open-Source Python/JavaScript Toolkit for Visualizing Molecular Dynamics Simulations in the Web Browser | Journal of Chemical Information and Modeling, accessed February 3, 2026, https://pubs.acs.org/doi/10.1021/acs.jcim.9b00703
COVID-19 Misinformation Detection: Machine-Learned Solutions to the Infodemic - NIH, accessed February 3, 2026, https://pmc.ncbi.nlm.nih.gov/articles/PMC9987189/
K-Dense-AI/claude-scientific-writer - GitHub, accessed February 3, 2026, https://github.com/K-Dense-AI/claude-scientific-writer
K-Dense-AI/claude-scientific-skills - GitHub, accessed February 3, 2026, https://github.com/K-Dense-AI/claude-scientific-skills
CLAUDE.md and Skills Experiment: What's the Best Way to Organize Instructions for Claude? : r/ClaudeAI - Reddit, accessed February 3, 2026, https://www.reddit.com/r/ClaudeAI/comments/1pe37e3/claudemd_and_skills_experiment_whats_the_best_way/
Claude Code Explained: CLAUDE.md, /command, SKILL.md, hooks, subagents, accessed February 3, 2026, https://avinashselvam.medium.com/claude-code-explained-claude-md-command-skill-md-hooks-subagents-e38e0815b59b
How we built our multi-agent research system - Anthropic, accessed February 3, 2026, https://www.anthropic.com/engineering/multi-agent-research-system
Prompting best practices - Claude API Docs, accessed February 3, 2026, https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-4-best-practices
GitIngest: Make GitHub repo ready for LLM - YouTube, accessed February 3, 2026, https://www.youtube.com/watch?v=wnpbZPhlbO8
Turn any git repo into llm readable format - DEV Community, accessed February 3, 2026, https://dev.to/tzgyn/turn-any-git-repo-into-llm-readable-format-5e
Optimizing Jupyter Notebooks for LLMs - Alex Molas, accessed February 3, 2026, https://www.alexmolas.com/2025/01/15/ipynb-for-llm.html
Using jupyter notebooks for reproducible publication figures | by Diogo Aguiam | Medium, accessed February 3, 2026, https://medium.com/@diogoaguiam/using-jupyter-notebooks-for-reproducible-publication-figures-9a195f8c6f1d
danduk82/extract_bib: A simple script to extract all the Bibtex bibliographic references that are cited in a given Latex text file - GitHub, accessed February 3, 2026, https://github.com/danduk82/extract_bib
Working with BibTeX in Python - Biblib - Gerard Martí, accessed February 3, 2026, https://gerardmjuan.github.io/2019/08/06/working-with-bibtex-python/
Academic Markdown. A workflow with Pandoc, BibTEX, and the… | by Chris Krycho | Medium, accessed February 3, 2026, https://medium.com/@chriskrycho/academic-markdown-and-citations-fe562ff443df
Turning BibTeX into bibliographies with Python (is a nightmare) - Marcel Bollmann, accessed February 3, 2026, https://marcel.bollmann.me/blog/turning-bibtex-into-bibliographies-with-python/
How to use Pandoc to produce a research paper | Opensource.com, accessed February 3, 2026, https://opensource.com/article/18/9/pandoc-research-paper
skills_collection — Explorer - GitHub Pages, accessed February 3, 2026, https://mattnigh.github.io/skills_collection/
Journal Information | PLOS Computational Biology, accessed February 3, 2026, https://journals.plos.org/ploscompbiol/s/journal-information
Submission Guidelines | PLOS One, accessed February 3, 2026, https://journals.plos.org/plosone/s/submission-guidelines
Article types - Frontiers in Bioinformatics | About, accessed February 3, 2026, https://www.frontiersin.org/journals/bioinformatics/for-authors/article-types
Submission Guidelines | PLOS Computational Biology, accessed February 3, 2026, https://journals.plos.org/ploscompbiol/s/submission-guidelines
Author guidelines | Bioinformatics - Oxford Academic, accessed February 3, 2026, https://academic.oup.com/bioinformatics/pages/author-guidelines
anarojoecheburua/Prompt-Chaining-For-LLMs: A Step-by-Step Guide to Enhancing LLM Performance and Accuracy - GitHub, accessed February 3, 2026, https://github.com/anarojoecheburua/Prompt-Chaining-For-LLMs
Create custom subagents - Claude Code Docs, accessed February 3, 2026, https://code.claude.com/docs/en/sub-agents
How to Prompt LLMs for Better, Faster Security Reviews - Crash Override, accessed February 3, 2026, https://crashoverride.com/blog/prompting-llm-security-reviews
claude-code-templates/cli-tool/components/skills/scientific/peer-review/SKILL.md at main, accessed February 3, 2026, https://github.com/davila7/claude-code-templates/blob/main/cli-tool/components/skills/scientific/peer-review/SKILL.md?plain=1
Ten simple rules for writing a PLOS Computational Biology quick tips article - PMC - NIH, accessed February 3, 2026, https://pmc.ncbi.nlm.nih.gov/articles/PMC10734976/
Martin Krzywinski - Data Visualization, Design, Science and Art, accessed February 3, 2026, https://mk.bcgsc.ca/pointsofsignificance/figures.mhtml
APA Formatting and Citation (7th Ed.) | Generator, Template, Examples - Scribbr, accessed February 3, 2026, https://www.scribbr.com/apa-style/format/
Awesome Scientific Writing - GitHub Pages, accessed February 3, 2026, https://writing-resources.github.io/awesome-scientific-writing/
How to Use Skills in Claude Code: Install Path, Project Scoping & Testing - Skywork.ai, accessed February 3, 2026, https://skywork.ai/blog/how-to-use-skills-in-claude-code-install-path-project-scoping-testing/
How to Convert a Jupyter Notebook to an Academic Paper Format? - Stack Overflow, accessed February 3, 2026, https://stackoverflow.com/questions/49371469/how-to-convert-a-jupyter-notebook-to-an-academic-paper-format
Weixin-Liang/Mapping-the-Increasing-Use-of-LLMs-in-Scientific-Papers - GitHub, accessed February 3, 2026, https://github.com/Weixin-Liang/Mapping-the-Increasing-Use-of-LLMs-in-Scientific-Papers
