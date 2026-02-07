# Repo Research Writer (RRWrite) Workflow Guide

Complete step-by-step workflow for generating a scientific manuscript from your research repository.

## 🎯 Overview

```
Research Repository → Manuscript Outline → Literature Review → Draft Sections → Review & Revise → Publication
```

## 📋 Complete Workflow

### Phase 1: Project Initialization

**Goal**: Set up your project structure and document your findings.

#### Step 1.1: Install RRWrite (One-time)
```bash
cd /path/to/repo-research-writer
./install.sh global
```

#### Step 1.2: Setup Your Research Project
```bash
cd /path/to/your/research/project
/path/to/repo-research-writer/install.sh setup-project
```

**Creates:**
- `PROJECT.md` (template)
- `rrwrite-drafts/`, `scripts/`, `figures/`, `data/` directories
- Verification scripts

#### Step 1.3: Document Your Findings
Edit `PROJECT.md` with:
- Project overview and goals
- Target journal
- Key findings with evidence links (data files, scripts, figures)
- Methodology notes

**Example:**
```markdown
# My Research Project

## Key Findings
1. Our model achieves 87% accuracy
   - Evidence: data/results.csv (column: accuracy)
   - Figure: figures/accuracy_plot.png
   - Script: scripts/evaluate.py (lines 45-67)
```

---

### Phase 2: Manuscript Planning

**Goal**: Create a detailed outline mapping repository contents to manuscript structure.

#### Step 2.1: Generate Outline
```
Use /rrwrite-plan-manuscript to create an outline for [Target Journal]
```

**Example:**
```
"Use /rrwrite-plan-manuscript to create an outline for Bioinformatics journal"
```

**Output**: `manuscript_plan.md`
- Section-by-section breakdown
- File mappings for each claim
- Word count guidance
- Journal-specific structure

#### Step 2.2: Critique Outline (Optional but Recommended)
```
Use /rrwrite-critique-manuscript to critique the outline in manuscript_plan.md
```

**Checks:**
- Logical flow
- Evidence mapping
- Missing sections
- Journal compliance

**Output**: `critique_outline.md`

#### Step 2.3: Refine Outline
- Address critique feedback
- Adjust section organization
- Verify file mappings

---

### Phase 3: Literature Research

**Goal**: Conduct comprehensive literature research and document evidence.

#### Step 3.1: Research Background and Related Work
```
Use /rrwrite-research-literature to find relevant papers for my [topic] manuscript
```

**Example:**
```
"Use /rrwrite-research-literature for transformer-based protein structure prediction"
```

**What happens:**
1. Extracts topics from PROJECT.md and manuscript_plan.md
2. Web search for foundational papers (pre-2020)
3. Web search for recent advances (2024-2026)
4. Web search for competing methods
5. Collects DOIs for all papers
6. Extracts direct quotes from each paper

**Outputs:**
- `rrwrite-drafts/literature_review.md` (structured summary, ~1000 words)
- `bib_additions.bib` (BibTeX entries with DOIs)
- `literature_evidence.csv` (DOIs + direct quotes)
- `literature_integration_notes.md` (where to cite)

#### Step 3.2: Critique Literature Coverage
```
Use /rrwrite-critique-manuscript to critique the literature review in rrwrite-drafts/literature_review.md
```

**Checks:**
- Coverage completeness (foundational, related, recent)
- Citation accuracy
- Balance across approaches
- Integration guidance quality

**Output**: `critique_literature.md`

#### Step 3.3: Integrate Citations
- Append `bib_additions.bib` to `references.bib`
- Note key citations for each section
- Keep `literature_evidence.csv` for verification

---

### Phase 4: Manuscript Drafting

**Goal**: Write manuscript sections with verified facts and proper citations.

#### Step 4.1: Draft Individual Sections

**Order suggestion:**
1. Methods (most straightforward, based on code)
2. Results (based on data files)
3. Introduction (now informed by literature review)
4. Discussion (synthesizes everything)
5. Abstract (last, summarizes complete manuscript)

**For each section:**
```
Use /rrwrite-draft-section to write the [Section Name] section
```

**Examples:**
```
"Use /rrwrite-draft-section to write the Methods section"
"Use /rrwrite-draft-section to write the Results section"
"Use /rrwrite-draft-section to write the Introduction section"
"Use /rrwrite-draft-section to write the Discussion section"
"Use /rrwrite-draft-section to write the Abstract"
"Use /rrwrite-draft-section to write the Availability section"
```

**What happens:**
1. Reads relevant files from manuscript_plan.md
2. Reads citations from bib_index.md or references.bib
3. Generates text with proper formatting
4. **Verifies numerical claims** using rrwrite-verify-stats.py
5. Saves to `rrwrite-drafts/[section_name].md`

**Special Note: Data and Code Availability Section**

When drafting the Availability section, include ONLY factual access information:

✅ **Should include:**
- Repository URL (GitHub, GitLab, Zenodo, etc.)
- License type (MIT, Apache 2.0, GPL-3.0, etc.)
- Installation method or documentation reference
- Data repository DOIs (Zenodo, Figshare, Dryad)
- Software version or release DOI
- System requirements (Python 3.10+, dependencies)

❌ **Should NOT include:**
- General methodology citations (FAIR principles, reproducibility frameworks)
- Research background or justification
- Citations unless specifically about tools/platforms
- Analysis methodology discussions

**Example (correct):**
```markdown
Source code available at https://github.com/user/project (MIT license).
Installation via `pip install project` requires Python 3.10+.
Documentation: https://project.readthedocs.io.
Data deposited in Zenodo: DOI 10.5281/zenodo.1234567.
```

#### Step 4.2: Verify Numerical Claims (Critical!)

After drafting, manually verify key claims:
```bash
# Check a specific statistic
python scripts/rrwrite-verify-stats.py \
  --file data/results.csv \
  --col accuracy \
  --op mean

# Expected output matches manuscript claim
```

#### Step 4.3: Cross-Reference with Evidence File

Check interpretations of prior work:
```bash
# Compare your description of AlphaFold2 with evidence
grep "alphafold2021" literature_evidence.csv

# Ensure your manuscript accurately represents the quote
```

---

### Phase 5: Manuscript Critique

**Goal**: Identify issues and ensure journal compliance.

#### Step 5.1: Critique Complete Draft
```
Use /rrwrite-critique-manuscript to critique the complete manuscript draft
```

**Point to main manuscript file or specify sections:**
```
"Use /rrwrite-critique-manuscript to critique rrwrite-drafts/full_manuscript.md"
```

**Checks:**
- Technical accuracy
- Journal-specific requirements
- Citation integrity
- Figure references
- Data availability statements
- Word counts

**Output**: `critique_manuscript_round_1.md`

#### Step 5.2: Address Critique Feedback

Work through critique report systematically:
- **Major Issues**: Address first (scientific gaps, missing data)
- **Minor Issues**: Fix formatting, typos, style
- **Action Items**: Specific fixes for each section

**Revise sections:**
```
"Use /rrwrite-draft-section to revise the Methods section addressing [specific issue]"
```

#### Step 5.3: Iterate
- Critique → Revise → Critique again
- Continue until "Accept with minor revisions"

---

### Phase 6: Final Assembly

**Goal**: Compile manuscript and prepare for submission.

#### Step 6.1: Combine Sections
```bash
# Manually combine all sections
cat rrwrite-drafts/abstract.md \
    rrwrite-drafts/introduction.md \
    rrwrite-drafts/methods.md \
    rrwrite-drafts/results.md \
    rrwrite-drafts/discussion.md \
    > rrwrite-drafts/full_manuscript.md
```

#### Step 6.2: Compile to PDF (Optional)

Using Pandoc (if installed):
```bash
pandoc rrwrite-drafts/full_manuscript.md \
  -o manuscript.pdf \
  --bibliography references.bib \
  --csl styles/[journal].csl \
  --filter pandoc-crossref
```

**Journal CSL files:**
- Nature Methods: `nature.csl`
- PLOS Computational Biology: `plos-computational-biology.csl`
- Bioinformatics: `bioinformatics.csl`

#### Step 6.3: Final Checks
- [ ] All figures referenced
- [ ] All citations in references.bib
- [ ] Data availability statement included
- [ ] Author contributions listed
- [ ] Acknowledgments added
- [ ] Supplementary materials prepared (if needed)

---

## 🔄 Quick Reference Workflow

```bash
# 1. Plan
"Use /rrwrite-plan-manuscript for [Journal]"

# 2. Research
"Use /rrwrite-research-literature for background"

# 3. Critique outline and literature
"Use /rrwrite-critique-manuscript to critique manuscript_plan.md"
"Use /rrwrite-critique-manuscript to critique literature_review.md"

# 4. Draft sections (in order)
"Use /rrwrite-draft-section to write Methods"
"Use /rrwrite-draft-section to write Results"
"Use /rrwrite-draft-section to write Introduction"
"Use /rrwrite-draft-section to write Discussion"
"Use /rrwrite-draft-section to write Abstract"

# 5. Critique and revise
"Use /rrwrite-critique-manuscript to critique the complete draft"
# Address feedback, iterate

# 6. Compile
cat rrwrite-drafts/*.md > rrwrite-drafts/full_manuscript.md
```

---

## 📊 File Structure Reference

**After complete workflow:**
```
your-research-project/
├── PROJECT.md                          # Your documented findings
├── manuscript_plan.md                   # Generated outline
├── rrwrite-drafts/
│   ├── literature_review.md            # Literature summary
│   ├── abstract.md                     # Drafted sections
│   ├── introduction.md
│   ├── methods.md
│   ├── results.md
│   ├── discussion.md
│   └── full_manuscript.md              # Combined
├── literature_evidence.csv              # DOIs + quotes
├── bib_additions.bib                   # New citations
├── references.bib                      # All citations
├── critique_outline.md                   # Critique reports
├── critique_literature.md
├── critique_manuscript_round_1.md
├── data/
│   └── *.csv                           # Your research data
├── scripts/
│   ├── rrwrite-verify-stats.py       # Verification tools
│   └── *.py                            # Your analysis scripts
└── figures/
    └── *.png                           # Your figures
```

---

## 💡 Tips for Success

### Before You Start
- ✅ Organize your data files with clear column names
- ✅ Document your scripts with comments
- ✅ Name figures descriptively
- ✅ Keep a references.bib file updated

### During Planning
- ✅ Be specific in PROJECT.md about key findings
- ✅ Link every claim to a data file
- ✅ Critique outline before drafting

### During Literature Research
- ✅ Verify all DOIs resolve
- ✅ Check evidence quotes are accurate
- ✅ Note gaps your work addresses

### During Drafting
- ✅ Draft one section at a time
- ✅ Verify every number with rrwrite-verify-stats.py
- ✅ Use exact citation keys from references.bib

### During Critique
- ✅ Address major issues before minor ones
- ✅ Iterate until critique says "accept with minor revisions"
- ✅ Keep evidence.csv handy for verification

### Common Pitfalls to Avoid
- ❌ Drafting before planning (leads to poor structure)
- ❌ Skipping literature research (weak positioning)
- ❌ Not verifying numbers (risk of errors)
- ❌ Ignoring critique feedback (quality suffers)
- ❌ Combining sections too early (harder to revise)

---

## 🆘 Troubleshooting

### "Skills not found"
```bash
# Check global installation
ls -la ~/.claude/skills/

# Re-install if needed
cd /path/to/repo-research-writer
./install.sh global
```

### "Verification script fails"
```bash
# Check data file exists
ls data/results.csv

# Check column name
head -1 data/results.csv

# Install pandas if missing
pip install pandas openpyxl
```

### "Citations not found"
```bash
# Check references.bib exists
ls references.bib

# Check citation key format
grep "alphafold2021" references.bib
```

### "Critique finds many issues"
- Critique the outline first (catch structure issues early)
- Verify data → claim links in PROJECT.md
- Check evidence.csv quotes match your interpretations

---

## 📚 Additional Resources

- **[README.md](README.md)** - Installation and overview
- **[INSTALL.md](INSTALL.md)** - Detailed installation guide
- **[USAGE_GUIDE.md](USAGE_GUIDE.md)** - Integration scenarios
- **[example/](example/)** - Complete working example

---

## 🎓 Learning Path

**First time using RRWrite?** Follow this progression:

1. **Explore the example** (`cd example/`)
   - Read PROJECT.md to see how findings are documented
   - Check manuscript_plan.md to see outline structure
   - Read literature_evidence.csv to see evidence format

2. **Try with a small project**
   - Start with 1-2 key findings
   - Draft just Methods and Results
   - Practice the verification workflow

3. **Scale to full manuscript**
   - Complete PROJECT.md documentation
   - Full literature research
   - All sections drafted
   - Multiple critique rounds

---

**Ready to start?** Run: `/rrwrite-workflow` in your research project to begin!
