# Manuscript Outline: RRWrite - Automated Manuscript Generation from Research Repositories

**Target Journal:** Bioinformatics (Oxford University Press)

**Generated:** 2026-02-05

**Based on:** RR-WRITE-PROJECT.md, README.md, repository analysis

---

## 1. Abstract (150-200 words)

### Purpose
Concise summary of motivation, methodology, implementation, and availability.

### Key Points to Cover
- Problem: Manual manuscript writing from computational research is error-prone and time-consuming
- Solution: RRWrite - AI-powered system for automatic manuscript generation
- Key features: Fact verification, evidence provenance, multi-journal formatting
- Implementation: 4 Claude Code skills + Python verification tools + LinkML schema
- Availability: Open source on GitHub, MIT license

### Evidence Files
- `RR-WRITE-PROJECT.md` (lines 1-15: project overview, research question)
- `README.md` (lines 1-30: system description)
- `.claude/skills/` (4 skill implementations)
- `scripts/` (8 Python tools)

### Word Count Target
**180 words**

---

## 2. Introduction (400-500 words)

### Subsection 2.1: Background and Motivation (200 words)

**Purpose:** Establish the problem of manuscript writing in computational research

**Key Points:**
- Computational researchers spend significant time translating code/data into text
- Common issues: transcription errors, broken provenance, inconsistent descriptions
- Need for automation while maintaining scientific accuracy

**Evidence Files:**
- `RR-WRITE-PROJECT.md` (lines 16-25: key innovation)
- `RR-WRITE-PROJECT.md` (lines 278-294: problem statement)

### Subsection 2.2: Existing Approaches (150 words)

**Purpose:** Review related tools and their limitations

**Key Points:**
- Literature review tools (e.g., Google Scholar, Semantic Scholar)
- Citation managers (e.g., Zotero, Mendeley)
- Jupyter notebooks for reproducible research
- Gap: No end-to-end manuscript generation with fact verification

**Evidence Files:**
- `data/gemini_deepresearch_cluewrite_concept.md` (background research)
- External literature (to be added in research phase)

### Subsection 2.3: RRWrite Contribution (150 words)

**Purpose:** State what RRWrite adds beyond existing tools

**Key Points:**
- Complete workflow: plan → research → draft → critique → assemble
- Mandatory fact-checking at every step
- Multi-journal format support
- Git-integrated version control
- Schema-based validation

**Evidence Files:**
- `RR-WRITE-PROJECT.md` (lines 27-37: system architecture)
- `.claude/skills/` (skill implementations)

### Word Count Target
**500 words total**

---

## 3. Algorithm/System Design (600-700 words)

### Subsection 3.1: Overall Architecture (200 words)

**Purpose:** Describe the skill-based architecture

**Key Points:**
- 4 core AI skills using Claude Code framework
- Each skill is self-contained with YAML configuration
- Skills communicate via file system (manuscript/ directory)
- State tracking coordinates workflow
- Schema validation ensures output quality

**Evidence Files:**
- `.claude/skills/rrwrite-plan-manuscript/SKILL.md` (lines 1-62)
- `.claude/skills/rrwrite-draft-section/SKILL.md` (lines 1-50)
- `.claude/skills/rrwrite-research-literature/SKILL.md` (lines 1-30)
- `.claude/skills/rrwrite-critique-manuscript/SKILL.md` (lines 1-30)
- `schemas/manuscript.yaml` (complete schema)

### Subsection 3.2: Verification System (150 words)

**Purpose:** Explain automatic fact-checking mechanism

**Key Points:**
- rrwrite-verify-stats.py: validates numerical claims against CSV/Excel
- rrwrite-validate-manuscript.py: LinkML schema validation
- Mandatory verification before section finalization
- Complete provenance from data files to claims

**Evidence Files:**
- `scripts/rrwrite-verify-stats.py` (entire file)
- `scripts/rrwrite-validate-manuscript.py` (entire file - 450 lines)
- `RR-WRITE-PROJECT.md` (lines 40-48: verification system)

### Subsection 3.3: Versioning and State Tracking (200 words)

**Purpose:** Detail the novel hybrid versioning approach

**Key Points:**
- Git for collaboration and history
- JSON state file (`.rrwrite/state.json`) for workflow progress
- Timestamped runs for manuscript archiving
- Semantic versioning for critique iterations

**Evidence Files:**
- `scripts/rrwrite-state-manager.py` (600+ lines)
- `scripts/rrwrite-status.py` (350+ lines)
- `scripts/rrwrite-archive-run.py` (250+ lines)
- `scripts/rrwrite-compare-runs.py` (350+ lines)
- `RR-WRITE-PROJECT.md` (lines 50-63: versioning system)

### Subsection 3.4: Workflow Stages (150 words)

**Purpose:** Describe the 5-stage workflow

**Key Points:**
1. Plan: Analyze repository, create journal-specific outline
2. Research: Deep literature search with citation management
3. Draft: Section-by-section writing with fact-checking
4. Critique: Adversarial review against journal standards
5. Assemble: Combine sections, validate, finalize

**Evidence Files:**
- `WORKFLOW.md` (complete workflow description)
- `RR-WRITE-PROJECT.md` (lines 72-75: workflow coverage)
- Each skill's SKILL.md file

### Word Count Target
**700 words total**

---

## 4. Implementation (500-600 words)

### Subsection 4.1: Technology Stack (150 words)

**Purpose:** Describe implementation technologies

**Key Points:**
- Python 3.x for verification tools and state management
- Bash for installation automation
- Claude Code framework for skill execution
- LinkML for schema definition
- Git for version control
- JSON for state serialization
- YAML for configuration
- Markdown for all outputs

**Evidence Files:**
- `scripts/*.py` (Python implementation)
- `install.sh` (Bash installation script)
- `schemas/manuscript.yaml` (LinkML schema)
- `RR-WRITE-PROJECT.md` (lines 231-242: methodology)

### Subsection 4.2: Skill System Details (200 words)

**Purpose:** Explain skill implementation

**Key Points:**
- YAML frontmatter configuration (name, description, tools, context)
- Context isolation via fork mode
- Tool access control
- State updates after completion
- Integration with verification scripts

**Evidence Files:**
- `.claude/skills/rrwrite-plan-manuscript/SKILL.md` (lines 1-5: YAML frontmatter)
- `.claude/skills/rrwrite-draft-section/SKILL.md` (lines 1-7: configuration)
- Updated skills with state tracking (lines 44-60 in each)

### Subsection 4.3: Installation System (150 words)

**Purpose:** Describe installation and setup process

**Key Points:**
- Global installation using symbolic links
- One-time setup, multi-project usage
- Automatic state initialization
- Template copying (PROJECT.md, scripts, schema)
- Directory structure creation

**Evidence Files:**
- `install.sh` (160 lines total)
- `INSTALL.md` (installation instructions)
- `USAGE_GUIDE.md` (setup scenarios)
- `RR-WRITE-PROJECT.md` (lines 67-71: installation model)

### Word Count Target
**500 words total**

---

## 5. Results/Features (400-500 words)

### Subsection 5.1: Core Capabilities (200 words)

**Purpose:** Demonstrate what the system can do

**Key Points:**
- Multi-journal support: Nature Methods, PLOS Comp Bio, Bioinformatics
- Complete workflow automation (5 stages)
- Fact verification for all numerical claims
- Citation management (BibTeX integration)
- Evidence provenance tracking
- Git integration with checkpoints

**Evidence Files:**
- Example project in `example/` directory
- `example/PROJECT.md` (protein structure prediction example)
- `example/manuscript_plan.md` (generated outline)
- `RR-WRITE-PROJECT.md` (lines 72-86: performance characteristics)

### Subsection 5.2: Example Output (150 words)

**Purpose:** Show representative generated content

**Key Points:**
- Example outline structure (from example/)
- Section word counts and structure
- Evidence file linkages
- Citation formatting

**Evidence Files:**
- `example/manuscript_plan.md` (complete example outline)
- `example/README.md` (walkthrough)

### Subsection 5.3: Validation and Quality Assurance (100 words)

**Purpose:** Explain quality control mechanisms

**Key Points:**
- Schema-based validation (LinkML)
- Mandatory verification before finalization
- Critique iteration tracking
- Git history for auditability

**Evidence Files:**
- `schemas/manuscript.yaml` (500+ lines)
- `scripts/rrwrite-validate-manuscript.py` (validation logic)

### Word Count Target
**450 words total**

---

## 6. Discussion (400-500 words)

### Subsection 6.1: Advantages Over Manual Writing (150 words)

**Purpose:** Highlight benefits of automated approach

**Key Points:**
- Reduces transcription errors
- Maintains complete provenance
- Enables rapid journal reformatting
- Supports iterative revisions
- Improves reproducibility

**Evidence Files:**
- `RR-WRITE-PROJECT.md` (lines 278-305: significance)

### Subsection 6.2: Limitations (100 words)

**Purpose:** Acknowledge current constraints

**Key Points:**
- Requires structured project organization
- Python-centric verification tools
- English-language focused
- Dependent on AI model quality
- Manual PROJECT.md creation required

**Evidence Files:**
- `.claude/skills/rrwrite-research-literature/SKILL.md` (lines 369-379: limitations)
- `RR-WRITE-PROJECT.md` (lines 340-347: future work)

### Subsection 6.3: Future Directions (150 words)

**Purpose:** Suggest potential enhancements

**Key Points:**
- Web dashboard for progress visualization
- Automatic figure caption generation
- Zotero/Mendeley integration
- Export to Overleaf
- Support for more journals
- Multi-language support
- Automatic table extraction

**Evidence Files:**
- `RR-WRITE-PROJECT.md` (lines 340-347: future work)
- `REFACTORING_SUMMARY.md` (planned enhancements)

### Word Count Target
**400 words total**

---

## 7. Availability and Requirements (150-200 words)

### Software Availability

**Purpose:** Provide access information

**Key Points:**
- GitHub repository: https://github.com/realmarcin/repo-research-writer
- License: MIT (open source)
- Language: Python 3.7+, Bash
- Dependencies: Claude Code CLI, Git, optional pandas/openpyxl
- Installation: Single command (`./install.sh global`)
- Documentation: Complete guides (WORKFLOW.md, VERSIONING.md, INSTALL.md)

**Evidence Files:**
- `README.md` (installation instructions)
- `INSTALL.md` (detailed setup)
- `install.sh` (installation script)
- `RR-WRITE-PROJECT.md` (lines 318-325: installation requirements)

### Word Count Target
**180 words**

---

## Summary

**Total Estimated Word Count:** ~3,000 words

**Journal Format:** Bioinformatics (Software/Algorithm Application Note)

**Structure:**
1. Abstract (180 words)
2. Introduction (500 words)
3. Algorithm/System Design (700 words)
4. Implementation (500 words)
5. Results/Features (450 words)
6. Discussion (400 words)
7. Availability (180 words)

**Primary Evidence Sources:**
- RR-WRITE-PROJECT.md: Project context and findings
- README.md: System overview
- Scripts (11 Python files, 1 Bash file): Implementation
- Skills (4 SKILL.md files): Core functionality
- Documentation (7 guide files): Usage and setup
- Schema (manuscript.yaml): Validation rules
- Example project: Demonstration

**Key Strengths:**
- Complete provenance from code to publication
- Automated fact-checking
- Multi-journal support
- Open source and extensible
- Comprehensive documentation

**Target Audience:**
- Computational biologists
- Bioinformatics researchers
- Data scientists publishing algorithmic work
- Research software engineers
