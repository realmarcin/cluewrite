# Methods

## System Architecture

RRWrite is implemented as a modular Python-based pipeline integrating repository analysis, literature search, and manuscript generation workflows. The system architecture comprises four core components: state management, Git version control, manuscript assembly, and validation frameworks.

**State Management System**: Workflow progress is tracked using a JSON-based state management system (`StateManager` class in `rrwrite_state_manager.py`). Each manuscript maintains an independent state file at `{manuscript_dir}/.rrwrite/state.json`, recording completion status for eight sequential stages: repository analysis, planning, assessment, research, figure/table extraction, drafting (six sub-stages), assembly, and critique. The state manager enforces progression gates, preventing advancement until prior stages complete successfully. This design enables workflow interruption and resumption without data loss.

**Dual Git Repository Architecture**: RRWrite employs a clean separation model to isolate tool development from manuscript version control [Barker2022]. The tool repository (`rrwrite/.git/`) contains scripts, templates, and documentation, while each manuscript receives an independent Git repository (`manuscript/{project}/.git/`). Four safety layers prevent repository pollution: (1) the tool repository's `.gitignore` excludes `manuscript/` directories, (2) pre-commit hooks reject manuscript file commits to the tool repository, (3) the `GitManager` class validates remote URLs before commits, and (4) the `StateManager` verifies the presence of `.rrwrite/` markers before initializing Git repositories. This architecture allows users to version control manuscripts independently while pulling tool updates from the upstream repository.

**Claude Code Integration**: The system integrates with Claude Code via skill-based workflow automation. Each workflow stage (analysis, planning, research, drafting, critique) corresponds to a dedicated skill in `.claude/skills/`, enabling interactive execution with natural language commands (e.g., `/rrwrite-draft-section --section methods`). Skills fork separate execution contexts to prevent token overflow during long-running operations.

**Schema Validation**: All intermediate outputs conform to LinkML schemas [LinkML2024] defined in `schemas/manuscript.yaml`. The `ManuscriptValidator` class performs structural validation, word count enforcement (±20% tolerance), citation format verification, and figure/table reference checks before allowing workflow progression.

## Repository Analysis Pipeline

Repository analysis extracts structured metadata from research code repositories to populate manuscript sections with verifiable evidence.

**File Classification**: The analysis pipeline (`rrwrite-analyze-repo.py`) traverses repository trees to configurable depths (default: 3 levels to avoid excessive recursion in deep hierarchies). Files are classified into categories (code, documentation, data, figures, notebooks) using extension-based heuristics. Python files (`.py`) are parsed for docstrings using AST traversal, Markdown files are indexed for section headers, and Jupyter notebooks [Kluyver2016] are scanned for research indicators (plots, statistical analyses, data tables).

**Research Indicator Detection**: The system identifies publication-ready artifacts including figures (`.png`, `.pdf`, `.svg` >5KB and <50MB), data tables (`.tsv`, `.csv` with >3 rows), and computational notebooks (`.ipynb` with execution outputs). Detected artifacts are cataloged with metadata: file path, size, modification timestamp, and generating script (inferred from naming conventions). This catalog populates `data_tables/` for tabular data and `figures/` for visualizations.

**Git History Mining**: Commit patterns are analyzed to extract contributor information, development timeline, and code churn metrics. The `git log --stat` command quantifies file modification frequencies, identifying core implementation files versus peripheral documentation.

**Output Structure**: Analysis results are serialized to `repository_analysis.md` (human-readable summary), `data_tables/file_inventory.tsv` (complete file listing with metadata), and `data_tables/repository_statistics.tsv` (aggregate metrics: total file counts, size distributions, category breakdowns).

## Literature Search and Citation Management

Literature search employs a dual-source strategy combining PubMed (biomedical focus) and Semantic Scholar (broad coverage) APIs with cascading year prioritization.

**Cascading Year Search**: The search strategy prioritizes recent publications through three sequential tiers: Tier 1 (last 2-3 years: 2024-2026) targets 15-20 papers from high-impact venues; if insufficient, Tier 2 (4-6 years: 2020-2023) supplements with foundational methodology papers; Tier 3 (7-10 years: 2016-2019) adds seminal highly-cited work (>500 citations). This approach balances recency (demonstrating awareness of current literature) with comprehensiveness (capturing foundational concepts). The search terminates when ≥15 relevant papers are found or all tiers are exhausted (minimum 8-10 papers acceptable for niche topics).

**API Integration**: PubMed queries use the Entrez E-utilities API (`rrwrite-api-pubmed.py`) with Medical Subject Headings (MeSH) term expansion and result ranking by relevance score. Semantic Scholar queries (`rrwrite-api-semanticscholar.py`) access the REST API with citation count prioritization and recency weighting. Both implementations include request caching (24-hour SQLite cache via `requests-cache`) to reduce API load during iterative searches.

**Deduplication and DOI Resolution**: Results from both sources are merged and deduplicated based on DOI matching or title similarity (Levenshtein distance <0.15 threshold). Missing DOIs are resolved via CrossRef API lookups using title and author metadata. Papers lacking DOIs after resolution are flagged but retained if from reputable venues.

**Citation Database Generation**: Retrieved papers are stored in two formats: (1) `literature_citations.bib` containing BibTeX entries with standardized keys (`authorYEAR` format, e.g., `Wilkinson2016`), and (2) `literature_evidence.csv` containing structured metadata (title, authors, year, DOI, abstract, venue, citation count). This dual format supports both citation insertion during drafting (BibTeX) and evidence-based claim verification (CSV with searchable abstracts).

**Evidence Extraction**: Paper abstracts and key sentences are indexed with citation keys to enable claim-to-source tracing during validation. The `rrwrite-verify-evidence.py` script cross-references manuscript citations against this database, flagging unsupported claims.

## Drafting and Validation System

Manuscript drafting employs section-specific strategies with verification gates enforcing completeness before progression.

**Section-Specific Drafting**: Each manuscript section (abstract, introduction, methods, results, discussion, availability) uses tailored prompting strategies implemented in `rrwrite-draft-section.py`. Methods sections receive prompts emphasizing passive voice, technical detail, and tool citations. Results sections receive prompts prioritizing active voice, quantitative reporting, and observation-focused language. The drafter loads section-appropriate context: code files for Methods, data tables for Results, literature citations for Introduction and Discussion.

**Word Limit Enforcement**: The `rrwrite-config-manager.py` script maintains section-specific word count targets with ±20% variance tolerance (e.g., Methods target: 1200 words, acceptable range: 960-1440). Drafts exceeding limits trigger automated summarization passes; drafts under limits receive expansion prompts.

**Citation Appropriateness Rules**: An evidence-based citation filtering system prevents inappropriate references by section. Methods sections allow only tool citations (software packages, datasets, specific algorithms actually used) and prohibit abstract principle papers (e.g., FAIR principles, reproducibility frameworks). Results sections allow only citations reporting observations (papers analyzed, datasets benchmarked) and prohibit explanatory or justification citations. These rules are enforced via regex pattern matching in `rrwrite-validate-manuscript.py`, which scans citation context (±50 words) for prohibited keywords.

**Verification Gates**: Before section completion, five validation checks execute: (1) structural compliance (required headings present), (2) word count within tolerance, (3) citation format correctness (`[authorYEAR]` pattern), (4) figure/table references sequential and complete, and (5) evidence linkage (all quantitative claims traced to source files). Failed checks block progression and return actionable error messages (e.g., "Missing citation for claim in line 45: '85% accuracy'").

**Figure and Table Integration**: The system extracts figures from two sources with priority-based selection: Priority 1 figures (`figures/from_repo/`) are actual research outputs from the analyzed repository, extracted during the figure/table extraction stage and linked to generating scripts via filename pattern matching; Priority 2 figures (`figures/generated/`) are supplementary visualizations created from repository analysis data (file type distributions, size histograms). Section drafters query the figure manifest (`figure_manifest.json`) to retrieve recommended figures with captions and section placement suggestions, prioritizing repository figures over generated visualizations.

## Assembly and Quality Control

Manuscript assembly combines validated sections into a unified document with citation consolidation and format conversion.

**Section Integration**: The `rrwrite-assemble-manuscript.py` script concatenates section files in canonical order (abstract, introduction, methods, results, discussion, availability), inserting section delimiters and adjusting heading levels for consistency. Cross-references (figure numbers, table numbers, section references) are renumbered globally to ensure sequential ordering.

**Citation Consolidation**: BibTeX entries from `literature_citations.bib` are merged with repository evidence citations, sorted alphabetically, and formatted according to target journal style (PLOS Computational Biology uses numbered citations in order of appearance). Duplicate entries are detected via DOI matching and removed.

**Multi-Format Export**: Assembled manuscripts are generated in three formats: (1) Markdown source (`manuscript_full.md`), (2) DOCX via Pandoc with embedded figures and preserved table formatting, and (3) PDF via LaTeX compilation when `pdflatex` is available. The Pandoc conversion uses `--resource-path` to locate figures, `--extract-media` to embed images, and `--wrap=preserve` to maintain table structure.

**Evidence Report Generation**: The `rrwrite-generate-evidence-report.py` script produces a supplementary evidence report (`EVIDENCE_REPORT.md`) documenting all repository-to-manuscript evidence linkages. This report lists: (1) total claims made with evidence, (2) claims lacking evidence (flagged for manual verification), (3) citation usage by section, and (4) repository files referenced per section. This transparency supports reproducibility and facilitates peer review.


## Code Availability

All analysis code is available at: /Users/marcin/Documents/VIMSS/ontology/repo-research-writer
