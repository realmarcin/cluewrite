# Repo Research Writer (RRWrite) 📝

**Transform your research code into publication-ready manuscripts automatically.**

Repo Research Writer (RRWrite) is an AI-powered system that reads your research repository—code, data, and notebooks—and generates scientifically accurate manuscripts with verified facts, proper citations, and journal-specific formatting.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎯 What RRWrite Does

Instead of manually translating your computational research into text:

```
Your Research Repo            RRWrite              Publication
├── data/results.csv    ──────────────────>    ┌─────────────────┐
├── scripts/analyze.py  ──────────────────>    │ Abstract        │
├── figures/fig1.png    ──────────────────>    │ Introduction    │
└── notebooks/          ──────────────────>    │ Methods         │
                                                │ Results         │
                                                │ Discussion      │
                                                └─────────────────┘
```

RRWrite:
- ✅ **Extracts findings** from your data files
- ✅ **Verifies all numbers** against source CSVs
- ✅ **Describes methods** by reading your code
- ✅ **Formats for journals** (Nature, PLOS, Bioinformatics)
- ✅ **Maintains evidence chains** from data to claims

## 🚀 Quick Example

See a real example: [manuscript/repo_research_writer_v2/](manuscript/repo_research_writer_v2/) - RRWrite documenting itself!

```bash
# In your research project directory
cd my-research-project

# Step 1: Use RRWrite to analyze your repository
# No PROJECT.md needed - analyzes repo automatically!

# Step 2: Plan the manuscript
"Use /rrwrite-plan-manuscript to create an outline for Bioinformatics journal"

# Step 3: Research the literature
"Use /rrwrite-research-literature to find relevant background papers and related work"

# Step 3: Draft sections
"Use /rrwrite-draft-section to write the Methods section"
"Use /rrwrite-draft-section to write the Results section"

# Step 4: Critique for compliance
"Use /rrwrite-critique-manuscript to check the draft"
```

**Result**: A complete manuscript draft where every claim is traced back to your source data.

## 📊 Real-World Example

The `manuscript/repo_research_writer_v2/` directory contains a complete self-documentation demonstration:

**Input**: RRWrite's own repository with:
- Python scripts: Multi-agent framework code
- Documentation: README, skill protocols, schemas
- Templates: Journal configurations, repo analysis
- State tracking: Workflow management system

**RRWrite Output**:
- Complete manuscript for Bioinformatics journal (3,788 words)
- 23 DOI-verified citations with evidence tracking
- 6 sections: Abstract, Introduction, Methods, Results, Discussion, Availability
- Literature review from 20 papers
- Comprehensive critique identifying 6 major + 8 minor issues
- Complete provenance: outline → literature → drafts → critique

[→ View Full Example](manuscript/repo_research_writer_v2/)

## 🔧 Installation

```bash
# 1. Clone RRWrite to a permanent location
git clone https://github.com/realmarcin/repo-research-writer.git ~/repo-research-writer

# 2. Install globally
cd ~/repo-research-writer
./install.sh

# That's it! RRWrite is now available globally.
```

### What install.sh Does

- Creates `~/.claude/skills/` directory
- Creates **symbolic links** pointing to RRWrite skills:
  ```
  ~/.claude/skills/rrwrite-plan-manuscript
  ~/.claude/skills/rrwrite-draft-section
  ~/.claude/skills/rrwrite-research-literature
  ~/.claude/skills/rrwrite-critique-manuscript
  ```
- **Benefit**: Update RRWrite once (`git pull`), all projects get updates automatically

### New Architecture: External Repository Model

RRWrite now works with **external repositories** - you don't install it into your research projects!

```bash
# Analyze any repository (GitHub URL or local path)
/rrwrite https://github.com/user/research-project --journal bioinformatics

# Or analyze a local directory
/rrwrite /path/to/my-research --journal nature

# Or the current directory
/rrwrite . --journal plos
```

All manuscripts are generated in versioned directories within RRWrite:
```
~/repo-research-writer/
├── manuscript/
│   ├── my-research_v1/    # First iteration
│   ├── my-research_v2/    # After critique
│   └── my-research_v3/    # Final version
└── examples/
    └── repo-research-writer_v1/  # Reference example
```

## 📖 How It Works

### 1. Repository Ingestion

RRWrite reads your project structure:
```
your-project/
├── data/processed/results.csv    → Numerical evidence
├── scripts/analyze.py             → Methodology
├── figures/fig1.png              → Visual results
└── PROJECT.md                      → Key findings summary
```

### 2. Planning

The `/rrwrite-plan-manuscript` skill creates a detailed outline:
- Maps each section to specific files
- Links claims to data sources
- Applies journal-specific structure

### 3. Drafting with Verification

The `/rrwrite-draft-section` skill:
- Reads relevant code/data files
- Generates academic prose
- **Verifies every number** using `rrwrite-verify-stats.py`
- Cites from your `references.bib`

Example fact-checking:
```bash
# Agent writes: "The model achieved 87% accuracy"
# Behind the scenes:
python scripts/rrwrite-verify-stats.py --file data/results.csv --col accuracy --op mean
# Returns: 0.87 ✓
```

### 4. Critique

The `/rrwrite-critique-manuscript` skill applies critical, demanding critique style:
- Checks journal-specific requirements
- Verifies citation integrity
- Flags missing figures or data availability statements

## 🎓 Skills Included

### `/rrwrite-plan-manuscript`
Maps your repository to a manuscript outline for your target journal.

**Supports**:
- Nature Methods
- PLOS Computational Biology
- Bioinformatics

### `/rrwrite-draft-section`
Writes individual sections with fact-checking.

**Features**:
- Reads code to describe methods
- Verifies numbers against data files
- Generates LaTeX equations from code
- Maintains variable name consistency

### `/rrwrite-critique-manuscript`
Critiques drafts for compliance and accuracy using critical, demanding style.

**Checks**:
- Word counts
- Citation integrity
- Figure references
- Data availability statements

## 📁 Output Structure

RRWrite generates manuscripts in versioned directories:

```
manuscript/
└── <your-repo>_v1/       # First version
    ├── outline.md        # Manuscript plan
    ├── literature.md     # Literature review
    ├── abstract.md       # Section files
    ├── introduction.md
    ├── methods.md
    ├── results.md
    ├── discussion.md
    ├── literature_citations.bib  # BibTeX citations
    ├── literature_evidence.csv   # Citation evidence
    ├── critique_manuscript_v1.md # Quality review
    └── .rrwrite/
        └── state.json    # Progress tracking
```

After addressing critique feedback, create v2:
```bash
/rrwrite . --version v2  # Creates manuscript/<your-repo>_v2/
```

See [MANUSCRIPT_SCHEMA.md](MANUSCRIPT_SCHEMA.md) for detailed naming conventions.

## 🛠️ Verification Tools

RRWrite includes Python tools to ensure accuracy:

### `rrwrite-verify-stats.py`
Verifies numerical claims against source data:
```bash
python scripts/rrwrite-verify-stats.py \
  --file data/results.csv \
  --col accuracy \
  --op mean
# Output: 0.8734
```

### `rrwrite-clean-ipynb.py`
Converts Jupyter notebooks to clean markdown:
```bash
python scripts/rrwrite-clean-ipynb.py notebook.ipynb -o clean.md
# Removes base64 images, keeps code and markdown
```

### `rrwrite-validate-manuscript.py`
Validates manuscript outputs against LinkML schema:
```bash
# Validate outline
python scripts/rrwrite-validate-manuscript.py \
  --file manuscript/outline.md \
  --type outline

# Validate section
python scripts/rrwrite-validate-manuscript.py \
  --file manuscript/methods.md \
  --type section

# Validate full manuscript
python scripts/rrwrite-validate-manuscript.py \
  --file manuscript/full_manuscript.md \
  --type manuscript
```

### `rrwrite-assemble-manuscript.py`
Assembles individual sections into full manuscript:
```bash
python scripts/rrwrite-assemble-manuscript.py
# Creates manuscript/full_manuscript.md from sections
```

## 📋 Schema-Based Validation

All manuscript outputs follow a LinkML schema (`schemas/manuscript.yaml`) that ensures:

- ✅ **Correct filenames**: `outline.md`, `literature.md`, `abstract.md`, etc.
- ✅ **Required sections**: All necessary parts included
- ✅ **Word count targets**: Sections meet minimum lengths
- ✅ **Citation integrity**: Proper citation format
- ✅ **Critique versioning**: `critique_TYPE_v1.md`, `critique_TYPE_v2.md`, etc.

Skills automatically validate outputs after generation. See [MANUSCRIPT_SCHEMA.md](MANUSCRIPT_SCHEMA.md) for details.

## 🔄 Workflow

```mermaid
graph LR
    A[Research Code] --> B[Plan Manuscript]
    B --> C[manuscript/outline.md]
    C --> D[Draft Sections]
    D --> E[manuscript/*.md sections]
    E --> F[Assemble]
    F --> G[manuscript/full_manuscript.md]
    G --> H[Critique]
    H --> I[manuscript/critique_manuscript_v1.md]
    I --> J[Revise & Finalize]
```

## 💡 Key Features

### ✅ Fact-Checking
Every numerical claim is verified against source data files.

### ✅ Code→Text Consistency
Variable names in the code match those in the manuscript.

### ✅ Evidence Chains
Each claim links to specific files/line numbers.

### ✅ Journal Compliance
Automatic formatting for target journals.

### ✅ Reproducibility
Complete provenance from data to publication.

### ✅ Progress Tracking
Automatic workflow state tracking shows what's done and what's next:
```bash
python scripts/rrwrite-status.py

# Output:
# Workflow Progress:
#   ✓ Planning (outline.md)
#   ✓ Literature Research (23 papers)
#   ⚠ Drafting (4/5 sections)
#   ○ Critique
#   ○ Final Assembly
```

### ✅ Versioning & Archiving
- **Git integration**: Full history and collaboration
- **Workflow runs**: Archive complete manuscripts for different journals
- **Critique iterations**: Track review cycles (v1, v2, v3...)
- **Run comparison**: Compare different approaches side-by-side

See [VERSIONING.md](VERSIONING.md) for details.

## 📚 Example Outputs

### From Repository Analysis:
```markdown
## Key Features
[REMOVED] integrates 864,363 validated species from KG-Microbe,
57 Bakta-annotated genomes (667K features), and 245+ publications.

Evidence: README.md (lines 13-20), data/designs/MP_plus/MP_plus_v10/
```

### Generated Methods Section:
```markdown
## Methods

The multi-agent framework comprised four specialized agents operating on
shared data infrastructure: LiteratureAgent, AnalogyReasoningAgent,
GenomeFunctionAgent, and MediaFormulationAgent. All agents interfaced
with a DuckDB backend containing KG-Microbe (864,363 validated species
across 1.5M nodes and 5.1M edges) as implemented in
`src/[REMOVED]/agents/`.
```

### With Verification:
```python
# The agent reads README.md and finds:
# - 864,363 validated species across bacteria, archaea, fungi, and protozoa
# - 57 Bakta-annotated genomes (667K features)
# - 245+ publications
# All statistics verified against source documentation
```

## 🤝 Contributing

We welcome contributions! To add:
- **New journal templates**: Add to skills/rrwrite-plan-manuscript
- **New verification tools**: Add to scripts/
- **Documentation improvements**: Update README or USAGE_GUIDE

1. Fork this repository
2. Create your feature branch
3. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE)

## 🙏 Citation

If RRWrite helps your research, please cite:

```bibtex
@software{rrwrite2026,
  title={Repo Research Writer (RRWrite): Repository-Driven Scientific Manuscript Generation},
  author={RRWrite Contributors},
  year={2026},
  url={https://github.com/realmarcin/repo-research-writer}
}
```

## 🔗 Resources

- **[Complete Workflow](WORKFLOW.md)**: Step-by-step manuscript generation guide
- **[Full Example](manuscript/repo_research_writer_v2/)**: RRWrite self-documentation
- **[Usage Guide](USAGE_GUIDE.md)**: Detailed integration instructions
- **[Installation Guide](INSTALL.md)**: Comprehensive setup instructions
- **[Technical Spec](data/gemini_deepresearch_cluewrite_concept.md)**: Architecture details

## ❓ FAQ

**Q: Does this work with non-Python projects?**
A: Yes! The skills read any text files. Verification tools are Python, but you can write your own for other languages.

**Q: Can I customize for my specific journal?**
A: Yes! Edit the skill files to add new journal templates.

**Q: How does it handle figures?**
A: RRWrite reads the scripts that generate figures to write accurate captions.

**Q: Does it hallucinate numbers?**
A: No! The verification loop ensures every number comes from your data files.

## 🎯 Next Steps

1. **Install RRWrite**:
   ```bash
   git clone https://github.com/realmarcin/repo-research-writer.git ~/repo-research-writer
   cd ~/repo-research-writer
   ./install.sh
   ```

2. **View the example**:
   ```bash
   cat ~/repo-research-writer/manuscript/repo_research_writer_v2/README.md
   ```

3. **Generate your first manuscript**:
   ```bash
   /rrwrite /path/to/your/research --journal bioinformatics
   ```

4. **Get help**: Type `/rrwrite-workflow` in your AI agent for guided assistance

## 🔍 Installation Troubleshooting

**"Skills not found"?**
- Check if skills are linked: `ls -la ~/.claude/skills/`
- Verify symlinks point to correct location: `readlink ~/.claude/skills/rrwrite-plan-manuscript`
- If path is wrong, re-run: `./install.sh global` from the correct RRWrite directory

**"Can't find install.sh"?**
- Make sure you're in the RRWrite repository directory
- Check: `pwd` should show the path where you cloned RRWrite
- The directory should contain: `.claude/`, `scripts/`, `README.md`, `install.sh`

**Want to move RRWrite?**
```bash
# If you move the repo, re-run global install
cd /new/location/of/repo-research-writer
./install.sh global
# This will update the symlinks
```

---

**Made with ❤️ for researchers who use repos**
