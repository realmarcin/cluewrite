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
python3 scripts/rrwrite_state_manager.py --install-tool-protection
```

**Expected result:**
```
✓ Installed tool repository protection hook: /path/to/rrwrite/.git/hooks/pre-commit
✓ Tool repository protection installed
```

This hook prevents you from accidentally committing manuscript files to the tool repository.

### Step 3: Verify Installation

```bash
# Check that scripts are executable
ls -l scripts/rrwrite*.py | head -5

# Test Python syntax
python3 -m py_compile scripts/rrwrite_git.py
python3 -m py_compile scripts/rrwrite_state_manager.py

# Verify Git ignores manuscript directory
cat .gitignore | grep manuscript
```

**Expected result:**
```
# From .gitignore
manuscript/
```

### Step 4: Install Python Dependencies (Optional)

If you need additional Python packages:

```bash
# Create virtual environment (optional but recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies (when requirements.txt is created)
# pip install -r requirements.txt
```

**Current status:** RRWrite uses only Python standard library, so no dependencies needed yet.

---

## Generating Your First Manuscript

### Prerequisites

Before generating a manuscript, you need:
- A research code repository (local path or Git URL)
- The repository should have:
  - README or documentation
  - Source code files
  - Git history (optional but helpful)

### Option A: Full Automated Workflow (Claude Code)

**Best for:** End-to-end manuscript generation with minimal manual intervention.

```bash
# Start from rrwrite directory
cd /path/to/rrwrite

# Run the full workflow skill
/rrwrite --repo /path/to/your/research-repository
```

**What this does (automatically):**

1. **Repository Analysis** (~2-5 min)
   - Analyzes code structure, dependencies, documentation
   - Extracts evidence from README, docstrings, comments
   - Creates: `manuscript/yourrepo_v1/repository_analysis.md`

2. **Manuscript Planning** (~3-5 min)
   - Generates outline based on repository analysis
   - Determines manuscript type (methods, application, tool)
   - Creates: `manuscript/yourrepo_v1/outline.md`

3. **Journal Assessment** (~2-3 min)
   - Recommends 3-5 suitable journals
   - Prompts you to select target journal
   - Fetches author guidelines for selected journal
   - Creates: `manuscript/yourrepo_v1/journal_assessment.md`, `journal_guidelines.md`

4. **Literature Research** (~5-10 min)
   - Searches PubMed and Semantic Scholar
   - Identifies 20-50 relevant papers
   - Creates citation database
   - Creates: `manuscript/yourrepo_v1/literature.md`, `literature_evidence.csv`, `literature_citations.bib`

5. **Section Drafting** (~20-40 min total)
   - Drafts each section individually:
     - Abstract (150-250 words)
     - Introduction (~800-1200 words)
     - Methods (~1000-1500 words)
     - Results (~1000-1500 words)
     - Discussion (~800-1200 words)
     - Data & Code Availability (~200-400 words)
   - Each section includes citations and evidence links
   - Creates: `manuscript/yourrepo_v1/sections/*.md`

6. **Assembly** (~1-2 min)
   - Combines sections in journal-specified order
   - Formats citations
   - Generates metadata
   - Creates: `manuscript/yourrepo_v1/manuscript.md`

7. **Critique** (~5-10 min)
   - Adversarial review of complete manuscript
   - Identifies issues (major and minor)
   - Suggests improvements
   - Creates: `manuscript/yourrepo_v1/critique_manuscript_v1.md`

**Total time:** 40-80 minutes

**Expected final output:**

```
manuscript/yourrepo_v1/
├── .git/                          # Git repository for version control
├── .rrwrite/
│   └── state.json                 # Workflow state
├── repository_analysis.md         # Repository analysis report
├── outline.md                     # Manuscript outline
├── journal_assessment.md          # Journal recommendation
├── journal_guidelines.md          # Author guidelines
├── literature.md                  # Literature review summary
├── literature_evidence.csv        # Citation database (CSV)
├── literature_citations.bib       # Bibliography (BibTeX)
├── repo_evidence.md               # Repository evidence database
├── sections/
│   ├── abstract.md
│   ├── introduction.md
│   ├── methods.md
│   ├── results.md
│   ├── discussion.md
│   └── availability.md
├── manuscript.md                  # Complete assembled manuscript
├── assembly_manifest.json         # Assembly metadata
└── critique_manuscript_v1.md      # Critique report
```

### Option B: Step-by-Step Manual Workflow

**Best for:** Fine-grained control over each stage.

#### Step 1: Analyze Repository

```bash
# Navigate to rrwrite directory
cd /path/to/rrwrite

# Run repository analysis
python3 scripts/rrwrite-analyze-repo.py \
    --repo-path /path/to/your/research-repo \
    --output-dir manuscript/myproject_v1
```

**Expected output:**
```
Analyzing repository: /path/to/your/research-repo
✓ Analyzed directory structure (45 files, 12 directories)
✓ Extracted README documentation
✓ Analyzed 234 commits from Git history
✓ Identified 15 contributors
✓ Detected technologies: Python, JavaScript, Docker

Repository analysis saved to: manuscript/myproject_v1/repository_analysis.md
```

**Verify:**
```bash
cat manuscript/myproject_v1/repository_analysis.md | head -50
```

#### Step 2: Generate Manuscript Outline

```bash
# Use Claude Code skill (interactive)
/rrwrite-plan-manuscript
```

When prompted:
1. Specify manuscript directory: `manuscript/myproject_v1`
2. Review generated outline
3. Confirm or request revisions

**Expected output:**
```
✓ Loaded repository analysis
✓ Generated manuscript outline
✓ Identified manuscript type: Methods paper
✓ Outline includes 6 sections

Outline saved to: manuscript/myproject_v1/outline.md
```

**Verify:**
```bash
cat manuscript/myproject_v1/outline.md
```

#### Step 3: Assess Journal Fit

```bash
# Use Claude Code skill (interactive)
/rrwrite-assess-journal
```

When prompted:
1. Review recommended journals (e.g., Nature Methods, Bioinformatics, PLOS Computational Biology)
2. Select target journal
3. RRWrite fetches author guidelines

**Expected output:**
```
✓ Analyzed outline for journal matching
✓ Recommended 4 suitable journals
✓ User selected: Nature Methods
✓ Fetched author guidelines for Nature Methods
✓ Compatibility score: 0.87/1.00

Files created:
- journal_assessment.md
- journal_guidelines.md
```

**Verify:**
```bash
cat manuscript/myproject_v1/journal_assessment.md
cat manuscript/myproject_v1/journal_guidelines.md
```

#### Step 4: Conduct Literature Research

```bash
# Use Claude Code skill (interactive)
/rrwrite-research-literature
```

Or use Python script directly:

```bash
python3 scripts/rrwrite-search-literature.py \
    --output-dir manuscript/myproject_v1 \
    --topics "machine learning,data analysis,visualization" \
    --max-papers 30
```

**Expected output:**
```
Searching PubMed for: machine learning...
✓ Found 145 papers, selected top 10

Searching Semantic Scholar for: data analysis...
✓ Found 234 papers, selected top 10

Searching Semantic Scholar for: visualization...
✓ Found 89 papers, selected top 10

✓ Total papers retrieved: 30
✓ Generated citation database
✓ Created bibliography file

Files created:
- literature.md (one-page summary)
- literature_evidence.csv (citation database)
- literature_citations.bib (BibTeX)
```

**Verify:**
```bash
wc -l manuscript/myproject_v1/literature_evidence.csv
# Should show: 31 (30 papers + header)

cat manuscript/myproject_v1/literature.md | head -100
```

#### Step 5: Draft Individual Sections

```bash
# Draft each section separately
/rrwrite-draft-section --section abstract
/rrwrite-draft-section --section introduction
/rrwrite-draft-section --section methods
/rrwrite-draft-section --section results
/rrwrite-draft-section --section discussion
/rrwrite-draft-section --section availability
```

**Expected output (per section):**
```
Drafting section: introduction
✓ Loaded repository evidence
✓ Loaded literature citations (30 papers)
✓ Loaded journal guidelines
✓ Generated introduction section (1,234 words)
✓ Included 8 citations
✓ Verified 12 claims against evidence

Section saved to: manuscript/myproject_v1/sections/introduction.md
```

**Verify:**
```bash
# Check word count for each section
for section in abstract introduction methods results discussion availability; do
    echo "=== $section ==="
    wc -w manuscript/myproject_v1/sections/$section.md
done
```

#### Step 6: Assemble Complete Manuscript

```bash
python3 scripts/rrwrite-assemble-manuscript.py \
    --manuscript-dir manuscript/myproject_v1
```

**Expected output:**
```
Assembling manuscript from sections...
✓ Loaded journal guidelines (Nature Methods)
✓ Section order: abstract, introduction, results, discussion, methods, availability
✓ Merged 6 sections
✓ Formatted 45 citations
✓ Total word count: 4,567 words
✓ Validation: All sections present

Files created:
- manuscript.md
- assembly_manifest.json
```

**Verify:**
```bash
wc -w manuscript/myproject_v1/manuscript.md
# Should show: ~4500-5000 words

head -100 manuscript/myproject_v1/manuscript.md
```

#### Step 7: Critique Manuscript

```bash
# Use Claude Code skill (interactive)
/rrwrite-critique-manuscript
```

When prompted, specify manuscript directory: `manuscript/myproject_v1`

**Expected output:**
```
Performing adversarial critique...
✓ Reviewed abstract (2 minor issues)
✓ Reviewed introduction (1 major issue, 3 minor)
✓ Reviewed methods (4 minor issues)
✓ Reviewed results (2 major issues, 5 minor)
✓ Reviewed discussion (3 minor issues)
✓ Checked citation formatting (2 issues)

Total issues found: 3 major, 19 minor

Critique saved to: manuscript/myproject_v1/critique_manuscript_v1.md
```

**Verify:**
```bash
cat manuscript/myproject_v1/critique_manuscript_v1.md
```

### Option C: Custom Output Location

Generate manuscript outside the rrwrite directory:

```bash
# Create output directory
mkdir -p ~/my-manuscripts/project-2025

# Run workflow with custom output
/rrwrite --repo /path/to/research --output-dir ~/my-manuscripts/project-2025
```

**Result:** Manuscript generated in `~/my-manuscripts/project-2025/` with its own git repository.

---

## Post-Generation Tasks

### View Workflow Status

```bash
# Check completion status
python3 scripts/rrwrite-status.py --output-dir manuscript/myproject_v1
```

**Expected output:**
```
═══════════════════════════════════════════════════════════════
RRWrite Workflow Status
═══════════════════════════════════════════════════════════════

Manuscript Directory: /path/to/rrwrite/manuscript/myproject_v1
Target Journal: Nature Methods
Overall Progress: 100.0%

Workflow Stages:
  ✓ repository_analysis: completed
  ✓ plan: completed
  ✓ assessment: completed
  ✓ research: completed
  ✓ drafting: completed (6/6 sections)
  ✓ assembly: completed
  ✓ critique: completed

Journal Compatibility: 0.87/1.00
Total Word Count: 4,567
Citations: 45
```

### Version Control Your Manuscript

Each manuscript has its own Git repository:

```bash
# Navigate to manuscript directory
cd manuscript/myproject_v1

# Check Git history (auto-commits from each stage)
git log --oneline

# Expected output:
# a3f8b21 [RRWrite] Complete critique: Adversarial critique completed
# 9d2c4e1 [RRWrite] Complete assembly: Assembled complete manuscript
# 7b1a5c3 [RRWrite] Complete drafting: All sections completed
# ...

# Push to your own repository
git remote add origin https://github.com/YOUR_USERNAME/my-manuscript.git
git branch -M main
git push -u origin main
```

### Iterate and Revise

```bash
# Make manual edits to sections
vim sections/introduction.md

# Re-assemble manuscript
python3 ../../scripts/rrwrite-assemble-manuscript.py --manuscript-dir .

# Commit changes
git add sections/introduction.md manuscript.md
git commit -m "Revise introduction based on critique feedback"

# Run critique again
/rrwrite-critique-manuscript
```

---

## Directory Structure

```
rrwrite/                          # Tool repository (clone this)
├── .git/                         # Tool's git repository
├── .gitignore                    # Ignores manuscript/ workspace
├── .claude/                      # Claude Code skills
│   └── skills/
│       ├── rrwrite.md
│       ├── rrwrite-plan-manuscript.md
│       ├── rrwrite-draft-section.md
│       └── ...
├── scripts/                      # Python tools
│   ├── rrwrite_state_manager.py  # Workflow state management
│   ├── rrwrite_git.py            # Git version control manager
│   ├── rrwrite-analyze-repo.py
│   ├── rrwrite-search-literature.py
│   └── ...
├── templates/                    # Configuration templates
│   └── journal_guidelines.yaml
├── docs/                         # Documentation
│   └── GIT_ARCHITECTURE.md       # Git architecture explained
├── example/                      # Example manuscripts (for reference)
│   ├── README.md                 # Example documentation
│   └── repo_research_writer_v2/  # Self-referential manuscript example
│       ├── abstract.md
│       ├── introduction.md
│       ├── methods.md
│       ├── results.md
│       ├── discussion.md
│       ├── availability.md
│       ├── literature.md
│       ├── literature_citations.bib
│       └── ...
└── manuscript/                   # Your workspace (auto-created, gitignored)
    └── yourrepo_v1/              # Your manuscript project
        ├── .git/                 # Separate git repo for your manuscript
        ├── .rrwrite/
        │   └── state.json        # Workflow state
        ├── sections/
        │   ├── abstract.md
        │   ├── introduction.md
        │   └── ...
        └── manuscript.md         # Final assembled manuscript
```

---

## Git Architecture

RRWrite uses **separate Git repositories** for tool and manuscripts to prevent pollution.

### Key Concepts

- **Tool Repository** (`rrwrite/.git/`): The RRWrite tool itself (this repo)
- **Manuscript Repositories** (`manuscript/project_v1/.git/`): Your manuscripts (separate repos)
- **Safety:** Four layers of protection prevent accidental commits to tool repo

### Workflow

```bash
# 1. Clone rrwrite tool (once)
git clone https://github.com/user/rrwrite.git
cd rrwrite

# 2. Run rrwrite (creates manuscript with own .git/)
python scripts/rrwrite.py --repo /path/to/research

# 3. Manuscript has independent git history
cd manuscript/research_v1
git log  # Shows only manuscript commits

# 4. Push manuscript to your own repo
git remote add origin https://github.com/you/my-manuscript.git
git push -u origin main

# 5. Update tool without affecting manuscripts
cd ../..
git pull  # Updates rrwrite tool only
```

**See [docs/GIT_ARCHITECTURE.md](docs/GIT_ARCHITECTURE.md) for detailed explanation.**

### Safety Features

1. ✅ **Remote URL validation** - Prevents commits to tool repo
2. ✅ **Pre-commit hooks** - Rejects manuscript files in tool commits
3. ✅ **Explicit --git-dir** - All git commands specify exact repository
4. ✅ **Warning messages** - Loud alerts when safety checks fail

---

## Workflow Stages

### 1. Repository Analysis

```bash
python scripts/rrwrite-analyze-repo.py --repo-path /path/to/repo
```

Analyzes:
- Code structure and architecture
- Documentation (README, docstrings, comments)
- Git history (commits, contributors)
- Dependencies and technologies
- Test coverage and examples

**Output:** `repository_analysis.md`

### 2. Manuscript Planning

```bash
/rrwrite-plan-manuscript
```

Generates structured outline:
- Title and abstract outline
- Section structure tailored to research type
- Key points for each section
- Suggested figures and tables

**Output:** `outline.md`

### 3. Journal Assessment

```bash
/rrwrite-assess-journal
```

Recommends target journals based on:
- Research scope and methodology
- Manuscript outline content
- Journal impact and fit

Fetches author guidelines for selected journal.

**Output:** `journal_assessment.md`, `journal_guidelines.md`

### 4. Literature Research

```bash
python scripts/rrwrite-search-literature.py --topics "topic1,topic2,topic3"
```

Conducts literature review:
- Searches PubMed and Semantic Scholar
- Ranks papers by relevance
- Generates citation indices
- Creates evidence database

**Output:** `literature.md`, `literature_evidence.csv`, `literature_citations.bib`

### 5. Section Drafting

```bash
/rrwrite-draft-section --section introduction
```

Writes individual sections:
- Uses repository evidence
- Incorporates citations from literature
- Follows journal guidelines
- Fact-checks claims against evidence

**Output:** `sections/introduction.md`, `sections/methods.md`, etc.

### 6. Manuscript Assembly

```bash
python scripts/rrwrite-assemble-manuscript.py
```

Combines sections in journal-specified order:
- Merges section files
- Formats citations
- Validates completeness
- Generates metadata

**Output:** `manuscript.md`, `assembly_manifest.json`

### 7. Manuscript Critique

```bash
/rrwrite-critique-manuscript
```

Adversarial review:
- Checks clarity and coherence
- Validates citations
- Identifies weak arguments
- Suggests improvements

**Output:** `critique_manuscript_v1.md`

---

## Command Reference

### Core Scripts

| Script | Purpose |
|--------|---------|
| `rrwrite-analyze-repo.py` | Analyze repository structure and content |
| `rrwrite-search-literature.py` | Search PubMed and Semantic Scholar |
| `rrwrite-extract-repo-evidence.py` | Extract evidence from repository |
| `rrwrite-verify-evidence.py` | Verify manuscript claims against evidence |
| `rrwrite-assemble-manuscript.py` | Assemble final manuscript from sections |
| `rrwrite-match-journal-scope.py` | Match manuscript to journal scopes |
| `rrwrite-recommend-journal.py` | Recommend suitable journals |
| `rrwrite-fetch-guidelines.py` | Fetch author guidelines for journal |

### Claude Code Skills

| Skill | Purpose |
|-------|---------|
| `/rrwrite` | Full end-to-end manuscript generation |
| `/rrwrite-plan-manuscript` | Generate manuscript outline |
| `/rrwrite-assess-journal` | Journal recommendation and guidelines |
| `/rrwrite-research-literature` | Deep literature research |
| `/rrwrite-draft-section` | Draft individual manuscript section |
| `/rrwrite-critique-manuscript` | Adversarial critique of manuscript |

### State Management

```bash
# View workflow status
python scripts/rrwrite-status.py --output-dir manuscript/yourrepo_v1

# View state summary
python scripts/rrwrite_state_manager.py --output-dir manuscript/yourrepo_v1 --summary

# Export state as JSON
python scripts/rrwrite_state_manager.py --output-dir manuscript/yourrepo_v1 --export
```

---

## Configuration

### Journal Guidelines Template

Edit `templates/journal_guidelines.yaml` to customize journal-specific formatting:

```yaml
journal: "Nature Methods"
sections_order:
  - abstract
  - introduction
  - results
  - discussion
  - methods
  - availability
citation_style: "nature"
word_limits:
  abstract: 200
  main_text: 3000
```

### Custom Output Location

```bash
# Output to directory outside rrwrite/
python scripts/rrwrite.py \
    --repo /path/to/research \
    --output-dir ~/my-manuscripts/project_v1
```

### Disable Git Version Control

```bash
python scripts/rrwrite.py --repo /path/to/research --no-git
```

---

## Examples

### Included Example: repo_research_writer_v2

See `example/repo_research_writer_v2/` for a complete self-referential manuscript documenting the RRWrite tool itself.

This example includes:
- All manuscript sections (abstract through availability)
- Literature review and citations
- Evidence tracking database
- Critique report
- Complete workflow state

**Explore the example:**
```bash
cd example/repo_research_writer_v2/
ls -la  # See all generated files
cat README.md  # Overview of the manuscript
```

### Generate Your Own Example

To create a manuscript for your repository:

```bash
# Generate manuscript for your project
/rrwrite --repo /path/to/your-repo --output-dir manuscript/yourproject_v1
```

---

## Troubleshooting

### "SAFETY VIOLATION: RRWRITE TOOL REPOSITORY DETECTED"

**Cause:** Trying to initialize git in tool directory
**Fix:** Use `manuscript/` subdirectory or `--output-dir`

```bash
# Correct:
python scripts/rrwrite.py --repo /path/to/research --output-dir manuscript/myproject

# Wrong:
python scripts/rrwrite.py --repo /path/to/research --output-dir .
```

### "Commit rejected: manuscript/ files detected"

**Cause:** Pre-commit hook detected manuscript files in tool repo
**Fix:** Commit from manuscript directory instead

```bash
git reset HEAD manuscript/
cd manuscript/myproject
git commit -m "Your manuscript changes"
```

### "Git repository not initialized"

**Cause:** Git initialization failed or disabled
**Fix:** Manually initialize

```bash
cd manuscript/yourproject
python ../../scripts/rrwrite_git.py --manuscript-dir . --initialize
```

### API Rate Limits

**PubMed:** No authentication required, but rate limited to 3 requests/second
**Semantic Scholar:** Rate limited to 100 requests/5 minutes

**Fix:** If you hit limits, wait and retry, or register for API keys

---

## Development

### Adding New Skills

1. Create skill file in `.claude/skills/`
2. Define metadata, prompts, and tools
3. Test with `/skill-name`

### Adding New Scripts

1. Create Python script in `scripts/`
2. Follow naming convention: `rrwrite-action-name.py`
3. Add CLI argparse interface
4. Document in README

### Running Tests

```bash
# Verify safety features
python scripts/rrwrite_git.py --install-tool-hook
git add manuscript/  # Should fail with hook

# Test manuscript creation
python scripts/rrwrite.py --repo /path/to/test-repo --output-dir /tmp/test-manuscript
```

---

## Architecture

### Workflow State Machine

```
not_started → in_progress → completed
```

Stages tracked:
1. repository_analysis
2. plan
3. assessment
4. research
5. drafting (with sub-stages for each section)
6. assembly
7. critique

State stored in: `{manuscript_dir}/.rrwrite/state.json`

### Evidence Chain

```
Repository → Evidence Extraction → Citation Index → Manuscript → Verification
```

1. Extract facts from repo (code, docs, commits)
2. Create evidence database (CSV)
3. Draft manuscript sections referencing evidence
4. Verify all claims link back to evidence

### Git Integration

```
StateManager → GitManager → Manuscript .git/
```

- `StateManager`: Initializes git for new manuscripts
- `GitManager`: Handles all git operations with safety checks
- Each manuscript gets independent `.git/` repository

---

## Contributing

Contributions welcome! Please:

1. Fork this repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

**Note:** Reference examples should go in `example/` (tracked in git), user manuscripts go in `manuscript/` (gitignored with separate repos)

---

## License

[Specify your license here]

---

## Citation

If you use RRWrite in your research, please cite:

```bibtex
@software{rrwrite2025,
  title={RRWrite: Research Repository to Manuscript Generator},
  author={Your Name},
  year={2025},
  url={https://github.com/YOUR_USERNAME/rrwrite}
}
```

---

## Support

- **Documentation:** See `docs/` directory
- **Issues:** Report bugs on GitHub Issues
- **Questions:** Open a GitHub Discussion

---

## Acknowledgments

Built with [Claude Code](https://claude.com/code) using Claude AI models.

---

## Quick Reference

### Installation Commands

```bash
# Clone and setup
git clone https://github.com/YOUR_USERNAME/rrwrite.git
cd rrwrite
python3 scripts/rrwrite_state_manager.py --install-tool-protection
```

### Full Automated Workflow

```bash
# Single command to generate complete manuscript
/rrwrite --repo /path/to/research-repo
```

### Manual Step-by-Step Workflow

```bash
# 1. Analyze repository
python3 scripts/rrwrite-analyze-repo.py --repo-path /path/to/repo --output-dir manuscript/project_v1

# 2. Plan manuscript
/rrwrite-plan-manuscript

# 3. Assess journal fit
/rrwrite-assess-journal

# 4. Research literature
/rrwrite-research-literature

# 5. Draft sections
/rrwrite-draft-section --section abstract
/rrwrite-draft-section --section introduction
/rrwrite-draft-section --section methods
/rrwrite-draft-section --section results
/rrwrite-draft-section --section discussion
/rrwrite-draft-section --section availability

# 6. Assemble manuscript
python3 scripts/rrwrite-assemble-manuscript.py --manuscript-dir manuscript/project_v1

# 7. Critique
/rrwrite-critique-manuscript
```

### Common Commands

```bash
# Check workflow status
python3 scripts/rrwrite-status.py --output-dir manuscript/project_v1

# View state summary
python3 scripts/rrwrite_state_manager.py --output-dir manuscript/project_v1 --summary

# Check manuscript git history
cd manuscript/project_v1 && git log --oneline

# Push manuscript to GitHub
cd manuscript/project_v1
git remote add origin https://github.com/YOU/manuscript.git
git push -u origin main

# Update RRWrite tool
cd /path/to/rrwrite
git pull
```

### Directory Paths

- **Tool repository:** `/path/to/rrwrite/`
- **Manuscript workspace:** `/path/to/rrwrite/manuscript/`
- **Example directory:** `/path/to/rrwrite/example/`
- **Scripts:** `/path/to/rrwrite/scripts/`
- **Documentation:** `/path/to/rrwrite/docs/`

### File Locations (in manuscript directory)

- **Repository analysis:** `repository_analysis.md`
- **Outline:** `outline.md`
- **Journal assessment:** `journal_assessment.md`
- **Literature review:** `literature.md`
- **Citation database:** `literature_evidence.csv`
- **Bibliography:** `literature_citations.bib`
- **Section files:** `sections/*.md`
- **Final manuscript:** `manuscript.md`
- **Critique:** `critique_manuscript_v1.md`
- **Workflow state:** `.rrwrite/state.json`
- **Git repository:** `.git/`

---

## Learn More

- [Git Architecture](docs/GIT_ARCHITECTURE.md) - Detailed explanation of version control system
- [Evidence Tracking](docs/EVIDENCE_TRACKING.md) - How RRWrite tracks and verifies claims
- [Journal Guidelines](templates/journal_guidelines.yaml) - Customize formatting

---

**RRWrite**: From code to publication, powered by AI.
