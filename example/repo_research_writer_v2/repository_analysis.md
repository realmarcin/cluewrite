# Research Repository Analysis for Manuscript Generation

**Repository**: /Users/marcin/Documents/VIMSS/ontology/repo-research-writer
**Name**: repo-research-writer
**Analysis Date**: 2026-03-05 23:45:06

---

## Repository Structure

```
repo-research-writer/
├── .claude
│   ├── commands
│   │   ├── rrwrite-workflow.md
│   │   └── rrwrite.md
│   ├── skills
│   │   ├── rrwrite-analyze-repository
│   │   │   └── SKILL.md
│   │   ├── rrwrite-assemble
│   │   │   └── SKILL.md
│   │   ├── rrwrite-assemble-manuscript
│   │   │   └── SKILL.md
│   │   ├── rrwrite-assess-journal
│   │   │   └── SKILL.md
│   │   ├── rrwrite-critique-manuscript
│   │   │   └── SKILL.md
│   │   ├── rrwrite-draft-section
│   │   │   └── SKILL.md
│   │   ├── rrwrite-extract-figures-tables
│   │   │   └── SKILL.md
│   │   ├── rrwrite-plan-manuscript
│   │   │   └── SKILL.md
│   │   ├── rrwrite-research-literature
│   │   │   └── SKILL.md
│   │   ├── rrwrite-revise-manuscript
│   │   │   └── SKILL.md
│   │   └── rrwrite-workflow
│   │       └── SKILL.md
│   └── settings.local.json
├── data
│   └── gemini_deepresearch_cluewrite_concept.md
├── docs
│   ├── git-hooks
│   │   └── pre-commit-manuscript
│   ├── 2-5-minute-rule.md
│   ├── API_IMPLEMENTATION_SUMMARY.md
│   ├── API_LITERATURE_SEARCH.md
│   ├── ASSEMBLY_SUMMARY.md
│   ├── ASSESSMENT_QUICKSTART.md
│   ├── CRITIQUE_COMMENTS.md
│   ├── EVIDENCE_ENHANCEMENTS_COMPLETE.md
│   ├── EVIDENCE_MARKDOWN_MIGRATION.md
│   ├── EVIDENCE_TRACKING.md
│   ├── FIGURES_AND_DOCX.md
│   ├── FIGURES_AND_TABLES_GUIDE.md
│   ├── FIGURE_TABLE_WORKFLOW.md
│   ├── GIT_ARCHITECTURE.md
│   ├── GUIDELINES_INTEGRATION.md
│   ├── IMPLEMENTATION_SUMMARY.md
│   ├── LITERATURE_AGENT_COMPARISON.md
│   ├── TABLE_GENERATION.md
│   ├── VERSIONING_IMPLEMENTATION_PLAN.md
│   ├── VERSION_REUSE.md
│   ├── cascading-literature-search.md
│   ├── citation-rules-by-section.md
│   ├── power-user-workflow.md
│   ├── rationalization-table.md
│   ├── remaining-implementation-notes.md
│   └── skill-optimization-guide.md
├── example
│   ├── data
│   │   └── benchmark_results.csv
│   ├── drafts
│   ├── figures
│   ├── notebooks
│   ├── repo_research_writer_v2
│   │   ├── data_tables
│   │   │   ├── file_inventory.tsv
│   │   │   ├── repository_statistics.tsv
│   │   │   ├── research_indicators.tsv
│   │   │   └── size_distribution.tsv
│   │   ├── README.md
│   │   ├── abstract.md
│   │   ├── availability.md
│   │   ├── critique_manuscript_v1.md
│   │   ├── discussion.md
│   │   ├── introduction.md
│   │   ├── literature.md
│   │   ├── literature_citations.bib
│   │   ├── literature_evidence.csv
│   │   ├── methods.md
│   │   ├── outline.md
│   │   ├── repository_analysis.md
│   │   └── results.md
│   ├── rrwrite_v1
│   │   ├── .rrwrite
│   │   │   └── state.json
│   │   ├── data_tables
│   │   │   ├── file_inventory.tsv
│   │   │   ├── repository_statistics.tsv
│   │   │   ├── research_indicators.tsv
│   │   │   └── size_distribution.tsv
│   │   ├── .gitignore
│   │   ├── EVIDENCE_REPORT.md
│   │   ├── abstract.md
│   │   ├── availability.md
│   │   ├── discussion.md
│   │   ├── full_manuscript.docx
│   │   ├── full_manuscript.md
│   │   ├── introduction.md
... (truncated)
```

---

## Key Files Identified

### Documentation Files
**File**: `README.md`

# RRWrite: Research Repository to Manuscript

**Transform your research code repository into a publication-ready scientific manuscript.**

RRWrite is an AI-powered tool that analyzes software repositories, extracts evidence, conducts literature review, and generates structured academic manuscripts tailored to specific journal requirements.

---

## Features

- 🔍 **Repository Analysis**: Deep analysis of code structure, documentation, and git history
- 📚 **Literature Research**: Automated literature search via PubMed and Semantic Scholar
- ✍️ **Manuscript Drafting**: Generate publication-ready sections with citations
- 🎯 **Journal Targeting**: Match manuscripts to appropriate journals and fetch author guidelines
- 🔬 **Evidence-Based**: All claims verified against repository evidence
- 📝 **Citation Management**: Automatic citation formatting and bibliography generation
- 🔄 **Version Control**: Safe Git integration for manuscript tracking (separate from tool repo)
- ⚡ **Iterative Refinement**: Adversarial critique and revision workflow

---

## Installation

### Prerequisites

- **Python 3.8+** (check with `python3 --version`)
- **Git** (check with `git --version`)
- **Claude Code CLI** (optional, for `/rrwrite` skills) - [Install here](https://claude.com/code)
- **Internet connection** (for PubMed and Semantic Scholar API access)

### Step 1: Clone RRWrite Repository

```bash
# Clone from GitHub (replace YOUR_USERNAME with actual repository location)
git clone https://github.com/YOUR_USERNAME/rrwrite.git

# Navigate into the repository
cd rrwrite

# Verify you're in the correct directory
pwd
# Should show: /path/to/rrwrite
```

**Expected result:**
```
Cloning into 'rrwrite'...
remote: Enumerating objects: 60, done.
remote: Counting objects: 100% (60/60), done.
Receiving objects: 100% (60/60), done.
```

### Step 2: Install Git Safety Hooks (Recommended)

```bash
# Install pre-commit hook to protect tool repository
python3 scripts/rrwrite_state_manager.py --install-to

... (truncated)

### Data Files
- `.claude/settings.local.json` (1.0 KB)
- `example/data/benchmark_results.csv` (559.0 B)
- `example/literature_evidence.csv` (1.2 KB)
- `example/repo_research_writer_v2/data_tables/file_inventory.tsv` (122.1 KB)
- `example/repo_research_writer_v2/data_tables/repository_statistics.tsv` (210.0 B)
- `example/repo_research_writer_v2/data_tables/research_indicators.tsv` (916.0 B)
- `example/repo_research_writer_v2/data_tables/size_distribution.tsv` (259.0 B)
- `example/repo_research_writer_v2/literature_evidence.csv` (6.1 KB)
- `example/rrwrite_v1/.rrwrite/state.json` (4.1 KB)
- `example/rrwrite_v1/data_tables/file_inventory.tsv` (11.8 KB)
- `example/rrwrite_v1/data_tables/repository_statistics.tsv` (247.0 B)
- `example/rrwrite_v1/data_tables/research_indicators.tsv` (581.0 B)
- `example/rrwrite_v1/data_tables/size_distribution.tsv` (298.0 B)
- `example/rrwrite_v1/literature_evidence.csv` (204.0 B)
- `example/rrwrite_v1/manifest.json` (966.0 B)
- `manuscript/MicroGrowAgents_v4/.rrwrite/state.json` (8.0 KB)
- `manuscript/MicroGrowAgents_v4/data_tables/file_inventory.tsv` (103.5 KB)
- `manuscript/MicroGrowAgents_v4/data_tables/repository_statistics.tsv` (268.0 B)
- `manuscript/MicroGrowAgents_v4/data_tables/research_indicators.tsv` (996.0 B)
- `manuscript/MicroGrowAgents_v4/data_tables/size_distribution.tsv` (330.0 B)
- ... and 109 more files

### Analysis Scripts
- `example/scripts/evaluate.py` (4.2 KB)
- `example/scripts/train_model.py` (3.6 KB)
- `install.sh` (2.8 KB)
- `manuscript/MicroGrowLink_v1/figures/generate_figure1.py` (4.2 KB)
- `manuscript/MicroGrowLink_v1/figures/generate_figure2.py` (7.3 KB)
- `manuscript/MicroGrowLink_v1/figures/generate_table1.py` (4.7 KB)
- `scripts/__init__.py` (61.0 B)
- `scripts/extract_docx_comments.py` (5.2 KB)
- `scripts/extract_word_comments.py` (5.0 KB)
- `scripts/rrwrite-analyze-repo.py` (18.5 KB)
- `scripts/rrwrite-api-pubmed.py` (8.6 KB)
- `scripts/rrwrite-api-semanticscholar.py` (7.3 KB)
- `scripts/rrwrite-apply-edits.py` (10.3 KB)
- `scripts/rrwrite-archive-run.py` (7.0 KB)
- `scripts/rrwrite-assemble-manuscript.py` (9.7 KB)
- `scripts/rrwrite-check-consistency.py` (3.5 KB)
- `scripts/rrwrite-clean-ipynb.py` (2.7 KB)
- `scripts/rrwrite-compare-runs.py` (8.1 KB)
- `scripts/rrwrite-config-manager.py` (9.4 KB)
- `scripts/rrwrite-convert-evidence-to-md.py` (4.4 KB)
- ... and 53 more files

### Figures and Visualizations
- `manuscript/MicroGrowAgents_v4/figures/10.1002_bit.26785.pdf` (748.2 KB)
- `manuscript/MicroGrowAgents_v4/figures/10.1007_0-306-46828-X_3.pdf` (3.4 MB)
- `manuscript/MicroGrowAgents_v4/figures/10.1007_BF00125087.pdf` (868.8 KB)
- `manuscript/MicroGrowAgents_v4/figures/10.1007_s002030050555.pdf` (96.0 KB)
- `manuscript/MicroGrowAgents_v4/figures/10.1007_s002030050747.pdf` (103.3 KB)
- `manuscript/MicroGrowAgents_v4/figures/10.1007_s00240-004-0458-y.pdf` (286.1 KB)
- `manuscript/MicroGrowAgents_v4/figures/10.1007_s00284-005-0370-x.pdf` (178.8 KB)
- `manuscript/MicroGrowAgents_v4/figures/10.1007_s10534-004-5769-5.pdf` (280.6 KB)
- `manuscript/MicroGrowAgents_v4/figures/10.1007_s10534-009-9224-5.pdf` (281.8 KB)
- `manuscript/MicroGrowAgents_v4/figures/10.1007_s10534-010-9400-7.pdf` (1.2 MB)
- `manuscript/MicroGrowAgents_v4/figures/10.1007_s10534-011-9421-x.pdf` (2.5 MB)
- `manuscript/MicroGrowAgents_v4/figures/10.1007_s10858-018-00222-4.pdf` (687.9 KB)
- `manuscript/MicroGrowAgents_v4/figures/10.1007_s10858-018-0218-x.pdf` (3.4 MB)
- `manuscript/MicroGrowAgents_v4/figures/10.1016_0891-5849(95)02016-0.pdf` (648.2 KB)
- `manuscript/MicroGrowAgents_v4/figures/10.1016_S0168-6445(03)00052-4.pdf` (567.8 KB)
- `manuscript/MicroGrowAgents_v4/figures/10.1016_S0969-2126(96)00095-0.pdf` (301.5 KB)
- `manuscript/MicroGrowAgents_v4/figures/10.1016_j.colsurfb.2006.04.014.pdf` (175.8 KB)
- `manuscript/MicroGrowAgents_v4/figures/10.1016_j.jphotobiol.2013.03.001.pdf` (515.8 KB)
- `manuscript/MicroGrowAgents_v4/figures/10.1021_es070174h.pdf` (175.1 KB)
- `manuscript/MicroGrowAgents_v4/figures/10.1021_ja00485a018.pdf` (1.0 MB)
- ... and 984 more files

### Configuration and Dependencies
- `requirements.txt` (218.0 B)

---

## Inferred Research Context

**Detected Topics**:
- Bioinformatics
- Data
- Data Analysis
- Data Sheets Schema V1
- Data Tables
- Data Visualization
- Figures
- Machine Learning
- Rrwrite-Extract-Figures-Tables
- Visualization
- Workflow

---

## Suggested Manuscript Sections

Based on the repository contents, the following sections are recommended:

1. **Data Description**: Repository contains data files that should be described in Methods
2. **Analysis Methods**: Repository contains analysis scripts/notebooks
3. **Results**: Repository contains figure files suggesting visualized results

---

## Additional Notes

- Total files analyzed: 1580
- Contains 6 test file(s)
- Contains 306 documentation file(s)
