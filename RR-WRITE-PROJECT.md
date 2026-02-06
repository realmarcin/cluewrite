# Repo Research Writer (RRWrite): AI-Powered Manuscript Generation System

## Project Overview

**Title:** Automated Manuscript Generation from Research Code Repositories Using Large Language Models

**Project Type:** Research Software Tool

**Status:** Production-ready v1.0

**Repository:** https://github.com/realmarcin/repo-research-writer

## Research Question

Can an AI-powered system automatically generate scientifically accurate, journal-compliant manuscripts directly from research code repositories while maintaining complete provenance from data to publication?

## Key Innovation

RRWrite is a comprehensive system that transforms computational research repositories (code, data, notebooks) into publication-ready manuscripts through:

1. **Automatic fact verification** - Every numerical claim verified against source data files
2. **Evidence provenance** - Complete traceability from data files to manuscript claims
3. **Multi-journal formatting** - Automatic adaptation to Nature, PLOS, Bioinformatics guidelines
4. **Iterative critique system** - Adversarial review and revision cycles
5. **Version control integration** - Git-based workflow with state tracking

## Key Findings

### 1. System Architecture

RRWrite consists of 4 core AI skills implemented as Claude Code skills:

- **rrwrite-plan-manuscript**: Analyzes repository structure and generates journal-specific outlines
- **rrwrite-draft-section**: Drafts individual sections with automatic fact-checking
- **rrwrite-research-literature**: Performs deep literature research with citation management
- **rrwrite-critique-manuscript**: Provides adversarial critique against journal standards

**Evidence:** `.claude/skills/` directory contains 4 skill implementations (400+ lines each)

### 2. Verification System

The system enforces fact-checking through Python verification tools:

- **rrwrite-verify-stats.py**: Validates numerical claims against CSV/Excel data
- **rrwrite-validate-manuscript.py**: Schema-based validation using LinkML
- **rrwrite-clean-ipynb.py**: Processes Jupyter notebooks for reproducibility

**Evidence:** `scripts/` directory contains verification tools, `schemas/manuscript.yaml` defines validation rules

### 3. Versioning and Progress Tracking

Novel hybrid versioning approach combining:

- Git versioning for collaboration and history
- State tracking (`.rrwrite/state.json`) for workflow progress
- Timestamped workflow runs for manuscript archiving
- Semantic versioning for critique iterations (v1, v2, v3...)

**Evidence:**
- `scripts/rrwrite-state-manager.py` (600+ lines) - State management
- `scripts/rrwrite-status.py` (350+ lines) - Progress display
- `scripts/rrwrite-archive-run.py` (250+ lines) - Run archiving
- `scripts/rrwrite-compare-runs.py` (350+ lines) - Run comparison

### 4. Performance Characteristics

**Installation:**
- Global installation model using symbolic links
- Enables one-time setup, multi-project usage
- Automatic updates via `git pull`

**Workflow Coverage:**
- 5 workflow stages tracked automatically
- Supports 3 major journal formats (Nature Methods, PLOS Comp Bio, Bioinformatics)
- Handles complete manuscript lifecycle: plan → research → draft → critique → revise → assemble

**Documentation:**
- 2,500+ lines of comprehensive documentation
- Complete workflow guide (WORKFLOW.md)
- Versioning guide (VERSIONING.md) with examples
- Installation instructions for multiple scenarios

**Evidence:**
- `install.sh` (160 lines) - Installation automation
- `WORKFLOW.md`, `VERSIONING.md`, `README.md` - Documentation
- Example project in `example/` directory

### 5. Schema-Based Validation

Uses LinkML schema for structured validation:

```yaml
ManuscriptProject:
  - outline (ManuscriptOutline)
  - literature_review (LiteratureReview)
  - sections (ManuscriptSection)
  - critiques (Critique)
  - full_manuscript (FullManuscript)
```

**Evidence:** `schemas/manuscript.yaml` (500+ lines) defines complete schema

### 6. Integration and Extensibility

**Git Integration:**
- Automatic checkpoint warnings before overwrites
- Git commit tracking for provenance
- File history tracking
- Automatic tagging for archived runs

**Skill System:**
- Modular skill architecture
- Context isolation via fork mode
- YAML-based configuration
- Tool access control

**Evidence:**
- Each skill has `SKILL.md` with YAML frontmatter
- State manager includes Git integration methods
- Skills use `context: fork` for isolation

## Data Sources

### Primary Code Assets

1. **Skill Implementations** (`.claude/skills/`)
   - rrwrite-plan-manuscript/SKILL.md
   - rrwrite-draft-section/SKILL.md
   - rrwrite-research-literature/SKILL.md
   - rrwrite-critique-manuscript/SKILL.md

2. **Verification Scripts** (`scripts/`)
   - rrwrite-verify-stats.py
   - rrwrite-validate-manuscript.py
   - rrwrite-assemble-manuscript.py
   - rrwrite-state-manager.py
   - rrwrite-status.py
   - rrwrite-archive-run.py
   - rrwrite-compare-runs.py
   - rrwrite-migrate-v1.py

3. **Schema Definition** (`schemas/`)
   - manuscript.yaml (LinkML schema)

4. **Documentation** (root directory)
   - README.md
   - WORKFLOW.md
   - VERSIONING.md
   - INSTALL.md
   - USAGE_GUIDE.md
   - FILENAMES.md
   - MANUSCRIPT_SCHEMA.md

5. **Installation System**
   - install.sh (bash script for setup)
   - PROJECT.md.template (project context template)

### Example Project

Complete demonstration in `example/` directory:
- PROJECT.md: Protein structure prediction example
- README.md: Example walkthrough
- manuscript_plan.md: Generated outline

## Target Audience

1. **Computational researchers** who want to automate manuscript writing
2. **Bioinformatics researchers** with code-heavy projects
3. **Data scientists** publishing algorithmic research
4. **Academic labs** producing multiple papers from code repositories

## Significance

This work addresses a critical gap in research automation:

**Problem:** Researchers spend significant time manually translating computational work into manuscripts, leading to:
- Transcription errors in numerical results
- Broken provenance chains from data to claims
- Inconsistent methodology descriptions
- Time-consuming revisions for different journals

**Solution:** RRWrite automates this process while:
- Maintaining complete verifiability
- Enforcing fact-checking at every step
- Enabling rapid journal-specific reformatting
- Preserving full provenance

**Impact:**
- Reduces manuscript writing time by automating repetitive tasks
- Improves accuracy through mandatory verification
- Enables reproducible manuscript generation
- Facilitates multi-journal submissions

## Methodology

### System Design

**Architecture:** Skill-based AI system using Claude Code framework
- Each skill is a self-contained AI task
- Skills communicate via file system (manuscript/ directory)
- State tracking provides workflow coordination
- Schema validation ensures output quality

**Verification Strategy:**
- Python-based verification tools
- CSV/Excel data parsing
- Statistical computation validation
- Automatic number checking before finalization

**Version Control:**
- Git as primary collaboration mechanism
- JSON state file for progress tracking
- Timestamped run directories for archiving
- Semantic versioning for critique iterations

### Implementation

**Language:** Python 3.x + Bash
**AI Framework:** Claude Code skills system
**Schema:** LinkML for structured validation
**Version Control:** Git
**Documentation:** Markdown

**Key Technologies:**
- Python subprocess for Git integration
- JSON for state serialization
- YAML for schemas and skill configuration
- Markdown for all outputs

## Installation Requirements

- Python 3.7+
- Git
- Claude Code CLI (for skill execution)
- Optional: pandas, openpyxl (for verification tools)

## Reproducibility

All code is open source and version controlled:

```bash
git clone https://github.com/realmarcin/repo-research-writer.git
cd repo-research-writer
./install.sh global
```

Complete workflow reproducible via:
```bash
cd /research/project
~/repo-research-writer/install.sh setup-project
# Edit PROJECT.md
# Run skills in order
```

## Future Work

Potential enhancements:
1. Web dashboard for progress visualization
2. Automatic figure caption generation from plotting code
3. Integration with Zotero/Mendeley for citation management
4. Export to journal submission systems (e.g., Overleaf)
5. Support for more journal formats
6. Automatic table extraction from data files
7. Multi-language support (currently English-focused)

## References

- Claude Code documentation: https://docs.anthropic.com/
- LinkML schema language: https://linkml.io/
- Example journal guidelines: Nature Methods, PLOS Computational Biology, Bioinformatics

## Contact

Project maintained at: https://github.com/realmarcin/repo-research-writer
