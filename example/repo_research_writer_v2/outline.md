# Manuscript Outline: RRWrite

**Target Journal:** PLOS Computational Biology

**Manuscript Type:** Software/Methods Article

**Total Word Count Target:** ~6,000-8,000 words

---

## Abstract (200-300 words)

**Target:** 250 words | **Min:** 200 | **Max:** 300

**Purpose:** Concise summary of RRWrite's functionality, validation results, and availability.

**Key Points:**
- Scientific software development increasingly relies on complex computational pipelines
- Challenge: Translating code repositories into publication-ready manuscripts
- RRWrite: AI-powered tool automating manuscript generation from research repositories
- Core features: repository analysis, literature integration, evidence-based writing, journal-specific formatting
- Validation: Self-referential manuscript generation demonstrating full workflow
- Results: Complete manuscript in 40-80 minutes with proper citations and structure
- Availability: Open-source Python package with Claude Code integration

**Evidence Files:**
- `README.md` - Tool description and features
- `example/repo_research_writer_v2/` - Self-referential manuscript output
- `repository_analysis.md` - Tool architecture overview

---

## Author Summary (100-200 words)

**Target:** 150 words | **Min:** 100 | **Max:** 200

**Purpose:** Non-technical explanation for broad audience (required by PLOS Comp Bio).

**Key Points:**
- Writing scientific papers about software is time-consuming and error-prone
- Researchers must manually extract information from code, find relevant literature, and format for journals
- RRWrite automates this process: analyzes code → searches literature → generates structured manuscript
- Like having an AI research assistant that understands both code and scientific writing
- Saves 20-40 hours per manuscript while ensuring accuracy and proper citations
- Makes computational methods more accessible by lowering publication barriers

**Note:** Use plain language, avoid jargon, explain "why this matters" to non-specialists.

**Evidence Files:**
- `README.md` - Feature overview in accessible language
- `docs/power-user-workflow.md` - Workflow examples

---

## Introduction (800-1,500 words)

**Target:** 1,200 words | **Min:** 800 | **Max:** 1,500

**Purpose:** Establish motivation, review existing tools, identify gaps, introduce RRWrite as solution.

### Subsections:

#### 1.1 The Challenge of Software Documentation (300 words)
**Key Points:**
- Scientific software development accelerating (GitHub growth statistics)
- Documentation lags behind code (technical debt problem)
- Publishing software methods requires narrative synthesis, not just README files
- Manual manuscript writing: 20-40 hours per paper, high error rate

**Evidence Files:**
- Literature citations on scientific software crisis
- `README.md` - RRWrite motivation section

#### 1.2 Existing Approaches and Limitations (400 words)
**Key Points:**
- Manual documentation: Time-intensive, inconsistent, often outdated
- Template-based tools: Rigid, limited to specific domains
- Code-to-text generators: Lack narrative flow, no literature integration
- AI writing assistants: Generic, not repository-aware, no evidence tracking

**Evidence Files:**
- Literature review (to be generated in Phase 4)
- Comparison table with existing tools

#### 1.3 RRWrite: An Integrated Solution (500 words)
**Key Points:**
- Evidence-based manuscript generation from repository analysis
- Multi-stage pipeline: analyze → plan → research → draft → critique → revise
- Journal-specific formatting and structure
- Defense-in-depth citation validation (4 layers)
- Dual git repository system (tool separate from manuscripts)
- Claude Code integration for interactive workflow

**Evidence Files:**
- `repository_analysis.md` - Architecture overview
- `scripts/` - Core pipeline components
- `.claude/skills/` - Workflow skills
- `docs/GIT_ARCHITECTURE.md` - Safety design
- `IMPLEMENTATION_SUMMARY.md` - System overview

---

## Results (1,000-3,000 words)

**Target:** 2,000 words | **Min:** 1,000 | **Max:** 3,000

**Purpose:** Demonstrate RRWrite capabilities through self-referential example and validation.

### Subsections:

#### 2.1 Repository Analysis Capabilities (400 words)
**Key Points:**
- Automated code structure extraction (tree depth, file types, dependencies)
- Documentation parsing (README, docstrings, comments)
- Research indicator detection (figures, data tables, notebooks)
- Evidence database generation for fact-checking

**Evidence Files:**
- `example/repo_research_writer_v2/repository_analysis.md` - Analysis output
- `example/repo_research_writer_v2/data_tables/*.tsv` - Structured data extraction
- `scripts/rrwrite-analyze-repo.py` - Analysis implementation

**Figures:**
- Figure 1: Repository structure visualization
- Figure 2: File type distribution

#### 2.2 Literature Integration (400 words)
**Key Points:**
- Cascading year search strategy (recent → foundational)
- Dual-source search (PubMed + Semantic Scholar)
- DOI verification and citation formatting
- Evidence extraction into structured database

**Evidence Files:**
- `scripts/rrwrite-search-literature.py` - Literature search implementation
- `example/repo_research_writer_v2/literature_evidence.csv` - Citation database format
- `example/repo_research_writer_v2/literature_citations.bib` - BibTeX output
- `docs/cascading-literature-search.md` - Search strategy documentation

**Tables:**
- Table 1: Literature search performance metrics

#### 2.3 Manuscript Drafting with Verification Gates (600 words)
**Key Points:**
- Section-specific drafting strategies (abstract, intro, methods, results, discussion, availability)
- Mandatory verification before progression (word count, citations, evidence)
- Section-appropriate citation rules (no methods papers in Results, etc.)
- Task decomposition into 2-5 minute checkpoints

**Evidence Files:**
- `scripts/rrwrite-draft-section.py` - Section drafting
- `scripts/rrwrite-validate-manuscript.py` - Validation gates
- `docs/citation-rules-by-section.md` - Section-specific rules
- `docs/2-5-minute-rule.md` - Task decomposition

**Figures:**
- Figure 3: Verification gate workflow diagram

#### 2.4 Automated Critique and Revision (400 words)
**Key Points:**
- Two-stage review: content validation → format compliance
- Issue detection with severity classification (major, minor, warning)
- Automated revision with convergence detection
- Iterative improvement loop (max iterations configurable)

**Evidence Files:**
- `scripts/rrwrite-critique-manuscript.py` - Critique implementation
- `scripts/rrwrite-revise-manuscript.py` - Automated revision
- `example/repo_research_writer_v2/critique_manuscript_v1.md` - Example critique
- `docs/rationalization-table.md` - Common error patterns

**Tables:**
- Table 2: Critique issue categories and resolution rates

#### 2.5 Self-Referential Validation (200 words)
**Key Points:**
- RRWrite generates manuscript about itself
- Full workflow completion: 63 minutes (repository_research_writer_v2 example)
- 5,307 words, 40 citations, 6 sections
- All verification gates passed
- Critique identified 5 major + 8 minor issues (addressed in revision)

**Evidence Files:**
- `example/repo_research_writer_v2/README.md` - Self-referential example summary
- `example/repo_research_writer_v2/results.md` - Results from previous run
- `.rrwrite/state.json` - Workflow state tracking

---

## Discussion (600-1,500 words)

**Target:** 1,000 words | **Min:** 600 | **Max:** 1,500

**Purpose:** Interpret results, discuss implications, acknowledge limitations, propose future work.

### Subsections:

#### 3.1 Impact on Scientific Software Documentation (300 words)
**Key Points:**
- Reduces manuscript writing time by 75% (20-40 hours → 5-10 hours supervision)
- Lowers barrier to publication for computational method developers
- Standardizes documentation quality across projects
- Enables "documentation-as-code" workflows

**Evidence Files:**
- Timing data from self-referential example
- Literature on documentation challenges

#### 3.2 Evidence-Based Writing as Quality Control (300 words)
**Key Points:**
- Defense-in-depth validation prevents citation errors
- Verification gates enforce completeness before progression
- Evidence tracking enables reproducibility
- Reduces plagiarism risk through explicit source attribution

**Evidence Files:**
- `docs/EVIDENCE_TRACKING.md` - Evidence system design
- `.rrwrite/citation_audit.jsonl` - Audit trail example

#### 3.3 Limitations and Future Directions (400 words)
**Key Points:**
- **Current limitations:**
  - Requires internet for literature search APIs
  - Claude API dependency for LLM-based drafting
  - Limited to repositories with documentation (README, code comments)
  - Manual journal selection still needed
- **Future work:**
  - Local LLM support for offline operation
  - Automatic journal recommendation based on content analysis
  - Multi-language support (currently English-only)
  - Integration with manuscript submission platforms
  - Collaborative editing features

**Evidence Files:**
- `docs/remaining-implementation-notes.md` - Known limitations
- GitHub issues tracker (future enhancements)

---

## Methods (800-2,500 words)

**Target:** 1,800 words | **Min:** 800 | **Max:** 2,500

**Purpose:** Detailed description of implementation enabling reproducibility.

### Subsections:

#### 4.1 System Architecture (400 words)
**Key Points:**
- Python-based modular pipeline
- State management system (StateManager class)
- Dual git repository architecture (tool vs. manuscripts)
- Claude Code skill system for interactive workflow
- JSON schema validation throughout

**Evidence Files:**
- `scripts/rrwrite_state_manager.py` - State management
- `scripts/rrwrite_git.py` - Git safety layer
- `docs/GIT_ARCHITECTURE.md` - Repository separation design
- `schemas/*.json` - Validation schemas

**Figures:**
- Figure 4: System architecture diagram

#### 4.2 Repository Analysis Pipeline (400 words)
**Key Points:**
- Tree traversal algorithm (configurable depth)
- File classification heuristics (code, docs, data, figures)
- Documentation parser (Markdown, reStructuredText, code comments)
- Git history analysis (commit patterns, contributors)

**Evidence Files:**
- `scripts/rrwrite-analyze-repo.py` - Main analysis script
- Code snippets demonstrating parsing logic

#### 4.3 Literature Search and Citation Management (500 words)
**Key Points:**
- PubMed API integration (Entrez toolkit)
- Semantic Scholar API integration (REST API)
- Cascading search strategy algorithm
- BibTeX generation and DOI resolution
- Citation evidence database schema

**Evidence Files:**
- `scripts/rrwrite-search-literature.py` - Search implementation
- `scripts/rrwrite_citation_validator.py` - DOI verification
- `docs/cascading-literature-search.md` - Algorithm description

**Tables:**
- Table 3: API endpoints and rate limits

#### 4.4 Drafting and Validation System (500 words)
**Key Points:**
- LLM prompting strategies (section-specific templates)
- Verification gate implementation (regex + schema validation)
- Citation appropriateness rules engine
- Word count enforcement algorithm

**Evidence Files:**
- `scripts/rrwrite-draft-section.py` - Section drafter
- `scripts/rrwrite-validate-manuscript.py` - Validator
- Prompt templates for each section type

---

## Supporting Information

### S1 File. Complete Self-Referential Example
- Full manuscript generated by RRWrite analyzing itself
- Demonstrates all workflow stages
- Available at: `example/repo_research_writer_v2/`

### S2 File. Workflow State JSON Schema
- Schema definition for `.rrwrite/state.json`
- Enables workflow tracking and resumption

### S3 File. Citation Evidence Database Schema
- Schema for `literature_evidence.csv`
- Enables evidence-based writing verification

### S1 Table. Comparison with Existing Documentation Tools
- Feature matrix: RRWrite vs. alternatives
- Metrics: automation level, citation support, journal formatting

---

## Data Availability

**Code and Data:**
- RRWrite source code: GitHub repository (to be specified)
- Example manuscripts: `example/` directory in repository
- Test datasets: Included in `data/` directory

**Third-Party Resources:**
- PubMed API: https://www.ncbi.nlm.nih.gov/home/develop/api/
- Semantic Scholar API: https://www.semanticscholar.org/product/api

---

## Acknowledgments

- Claude Code team for LLM integration platform
- VIMSS project for motivating use case
- PubMed and Semantic Scholar for literature APIs

---

## References

*To be populated during literature research phase (Phase 4)*

Target: 40-60 references spanning:
- Scientific software development challenges (10-15 refs)
- Automated documentation tools (10-15 refs)
- AI-assisted writing systems (10-15 refs)
- Citation management and validation (5-10 refs)
- Example applications and case studies (5-10 refs)

---

## Estimated Total Word Count Breakdown

| Section | Min | Target | Max | Actual (TBD) |
|---------|-----|--------|-----|--------------|
| Abstract | 200 | 250 | 300 | - |
| Author Summary | 100 | 150 | 200 | - |
| Introduction | 800 | 1,200 | 1,500 | - |
| Results | 1,000 | 2,000 | 3,000 | - |
| Discussion | 600 | 1,000 | 1,500 | - |
| Methods | 800 | 1,800 | 2,500 | - |
| **TOTAL** | **3,500** | **6,400** | **9,000** | - |

**Note:** PLOS Computational Biology has no strict total word limit, allowing detailed methods and results sections.
