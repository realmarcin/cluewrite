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

See a real example: [example/](example/) - A complete protein structure prediction project

```bash
# In your research project directory
cd my-research-project

# Step 1: Tell ClueWrite about your project
# Edit PROJECT.md with your findings and data sources

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

The `example/` directory contains a complete demonstration:

**Input**: Protein prediction project with:
- CSV data: `benchmark_results.csv` (model accuracies)
- Python scripts: `train_model.py`, `evaluate.py`
- Figures: `accuracy_comparison.png`
- BibTeX: `references.bib`

**RRWrite Output**:
- Detailed manuscript plan mapping data→sections
- Methods section describing the code implementation
- Results section with verified statistics
- Proper figure captions derived from plotting code
- Journal-compliant formatting for Bioinformatics

[→ View Full Example](example/)

## 🔧 Installation

### Global Installation (Recommended - Use Across All Projects)

```bash
# 1. Clone RRWrite to a permanent location
git clone https://github.com/realmarcin/repo-research-writer.git ~/repo-research-writer
# Note: You can clone anywhere, just remember the path!

# 2. Install globally
cd ~/repo-research-writer
./install.sh global

# 3. Setup any research project
cd /path/to/your/research/project
~/repo-research-writer/install.sh setup-project
```

**If you cloned to a different location:**
```bash
# Replace ~/repo-research-writer with your actual path
cd /your/actual/path/to/repo-research-writer
./install.sh global

# Then use the full path when setting up projects
cd /path/to/your/research/project
/your/actual/path/to/repo-research-writer/install.sh setup-project
```

### What install.sh Does

#### `./install.sh global`
- Creates `~/.claude/skills/` directory
- Creates **symbolic links** (not copies) pointing to RRWrite skills:
  ```
  ~/.claude/skills/rrwrite-plan-manuscript → /path/to/repo-research-writer/.claude/skills/rrwrite-plan-manuscript
  ~/.claude/skills/rrwrite-draft-section → /path/to/repo-research-writer/.claude/skills/rrwrite-draft-section
  ~/.claude/skills/rrwrite-critique-manuscript → /path/to/repo-research-writer/.claude/skills/rrwrite-critique-manuscript
  ```
- **Benefit**: Update RRWrite once (`git pull`), all projects get updates automatically

#### `./install.sh setup-project`
Prepares your research project by:
1. Creating directory structure (`rrwrite-drafts/`, `scripts/`, `figures/`, `data/`)
2. Copying `PROJECT.md` template for documenting findings
3. Copying verification tools (`rrwrite-verify-stats.py`, `rrwrite-clean-ipynb.py`)
4. Creating `.gitignore` for manuscript drafts

#### `./install.sh local`
- Copies (not symlinks) skills directly to current project's `.claude/skills/`
- Use when you want project-specific skill customization
- Updates require re-copying to each project

## 📖 How It Works

### 1. Repository Ingestion

ClueWrite reads your project structure:
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

The `/rrwrite-critique-manuscript` skill acts as "Reviewer #2":
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
Critiques drafts for compliance and accuracy.

**Checks**:
- Word counts
- Citation integrity
- Figure references
- Data availability statements

## 📁 Project Structure

Your research project should have:

```
your-research-project/
├── .claude/skills/        # RRWrite skills (symlinked)
├── PROJECT.md              # Your project context
├── manuscript/            # All manuscript outputs (schema-validated)
│   ├── outline.md        # Manuscript plan
│   ├── literature.md     # Literature review
│   ├── abstract.md       # Section files
│   ├── introduction.md
│   ├── methods.md
│   ├── results.md
│   ├── discussion.md
│   └── full_manuscript.md
├── schemas/
│   └── manuscript.yaml   # LinkML schema definition
├── scripts/              # Verification and validation tools
├── data/
│   └── processed/        # Data files with results
├── figures/              # Generated plots
└── references.bib        # Citations
```

See [MANUSCRIPT_SCHEMA.md](MANUSCRIPT_SCHEMA.md) for detailed naming conventions and validation.

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
    A[Research Code] --> B[/rrwrite-plan-manuscript]
    B --> C[manuscript/outline.md]
    C --> D[/rrwrite-draft-section]
    D --> E[manuscript/*.md sections]
    E --> F[Assemble]
    F --> G[manuscript/full_manuscript.md]
    G --> H[/rrwrite-critique-manuscript]
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

### From PROJECT.md:
```markdown
## Key Finding
Our model achieves 87% accuracy on the benchmark.

Evidence: data/results.csv (line 45), figures/accuracy.png
```

### Generated Methods Section:
```markdown
## Methods

The model was trained using AdamW optimizer (learning rate 1e-4,
weight decay 0.01) for 100 epochs on 4× NVIDIA A100 GPUs. The loss
function combined RMSD and TM-score as implemented in
`scripts/train_model.py:87-89`.
```

### With Verification:
```python
# The agent reads train_model.py and finds:
optimizer = torch.optim.AdamW(
    model.parameters(),
    lr=1e-4,          # ← Extracted
    weight_decay=0.01  # ← Extracted
)
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
- **[Full Example](example/)**: Complete protein prediction project
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

1. **Read the workflow**: See [WORKFLOW.md](WORKFLOW.md) for complete guide
2. **Try the example**: `cd example/` and explore
3. **Install globally**:
   ```bash
   cd /path/where/you/cloned/repo-research-writer
   ./install.sh global
   ```
4. **Setup your project**:
   ```bash
   cd /your/research/project
   /path/to/repo-research-writer/install.sh setup-project
   ```
5. **Start writing**: In your AI agent, type `/rrwrite-workflow` for guided assistance

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
