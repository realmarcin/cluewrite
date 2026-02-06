---
name: cluewrite-workflow
description: Guide through the complete ClueWrite manuscript generation workflow
---

# ClueWrite Workflow Assistant

I'll guide you through the complete manuscript generation workflow. Let me first check what stage you're at.

## Current Project Status

Let me check your project structure:

**Files to check:**
- `CLUEWRITE.md` - Your documented findings
- `manuscript_plan.md` - Manuscript outline
- `cluewrite-drafts/literature_review.md` - Literature research
- `cluewrite-drafts/*.md` - Drafted sections
- `references.bib` - Citations

## Complete Workflow

### Stage 1: Project Setup ✓/✗
**Prerequisites:**
- [ ] ClueWrite installed globally
- [ ] Project directory initialized
- [ ] CLUEWRITE.md created and filled out

**If not done:**
```bash
# Install ClueWrite (one time)
cd /path/to/cluewrite && ./install.sh global

# Setup this project
cd /your/research/project
/path/to/cluewrite/install.sh setup-project

# Edit CLUEWRITE.md with your findings
```

---

### Stage 2: Manuscript Planning ✓/✗
**Goal:** Create detailed outline

**Run:**
```
Use cluewrite-plan-manuscript to create an outline for [Your Target Journal]
```

**Examples:**
- "Use cluewrite-plan-manuscript for Nature Methods"
- "Use cluewrite-plan-manuscript for PLOS Computational Biology"
- "Use cluewrite-plan-manuscript for Bioinformatics"

**Output:** `manuscript_plan.md`

**Then review:**
```
Use cluewrite-review-manuscript to review manuscript_plan.md
```

---

### Stage 3: Literature Research ✓/✗
**Goal:** Find and document relevant papers

**Run:**
```
Use cluewrite-research-literature to research background for [your topic]
```

**Example:**
```
Use cluewrite-research-literature for transformer-based protein structure prediction
```

**Outputs:**
- `cluewrite-drafts/literature_review.md` (summary)
- `bib_additions.bib` (new citations with DOIs)
- `literature_evidence.csv` (quotes for verification)

**Then review:**
```
Use cluewrite-review-manuscript to review cluewrite-drafts/literature_review.md
```

**Manual step:**
```bash
# Append new citations to your bibliography
cat bib_additions.bib >> references.bib
```

---

### Stage 4: Section Drafting ✓/✗
**Goal:** Write manuscript sections with verified facts

**Draft in this order:**

1. **Methods** (most straightforward)
   ```
   Use cluewrite-draft-section to write the Methods section
   ```

2. **Results** (based on data)
   ```
   Use cluewrite-draft-section to write the Results section
   ```

3. **Introduction** (with literature context)
   ```
   Use cluewrite-draft-section to write the Introduction section
   ```

4. **Discussion** (synthesize everything)
   ```
   Use cluewrite-draft-section to write the Discussion section
   ```

5. **Abstract** (summarize complete work)
   ```
   Use cluewrite-draft-section to write the Abstract
   ```

**After each section, verify numbers:**
```bash
# Example: Check accuracy claim
python scripts/cluewrite-verify-stats.py \
  --file data/results.csv \
  --col accuracy \
  --op mean
```

---

### Stage 5: Manuscript Review ✓/✗
**Goal:** Ensure quality and compliance

**Run:**
```
Use cluewrite-review-manuscript to review the complete manuscript
```

**Specify file:**
```
Use cluewrite-review-manuscript to review cluewrite-drafts/full_manuscript.md
```

**Output:** `review_manuscript_round_1.md`

**Address feedback and iterate:**
1. Fix major issues (scientific gaps, missing data)
2. Fix minor issues (formatting, typos)
3. Re-review until "accept with minor revisions"

---

### Stage 6: Final Assembly ✓/✗
**Goal:** Compile and prepare for submission

**Combine sections:**
```bash
cat cluewrite-drafts/abstract.md \
    cluewrite-drafts/introduction.md \
    cluewrite-drafts/methods.md \
    cluewrite-drafts/results.md \
    cluewrite-drafts/discussion.md \
    > cluewrite-drafts/full_manuscript.md
```

**Compile to PDF (if pandoc installed):**
```bash
pandoc cluewrite-drafts/full_manuscript.md \
  -o manuscript.pdf \
  --bibliography references.bib \
  --csl styles/nature.csl
```

**Final checklist:**
- [ ] All figures referenced
- [ ] All citations in references.bib
- [ ] Data availability statement
- [ ] Acknowledgments
- [ ] Supplementary materials (if needed)

---

## Quick Commands Reference

```bash
# Planning
"Use cluewrite-plan-manuscript for [Journal]"

# Literature
"Use cluewrite-research-literature for [topic]"

# Drafting (one at a time)
"Use cluewrite-draft-section to write the Methods section"
"Use cluewrite-draft-section to write the Results section"
"Use cluewrite-draft-section to write the Introduction section"
"Use cluewrite-draft-section to write the Discussion section"
"Use cluewrite-draft-section to write the Abstract"

# Reviewing
"Use cluewrite-review-manuscript to review [file]"
```

---

## Need Help?

- **Detailed workflow:** See `WORKFLOW.md` in ClueWrite repository
- **Example project:** See `example/` directory
- **Installation issues:** See `INSTALL.md`
- **Usage scenarios:** See `USAGE_GUIDE.md`

---

## What stage are you at?

Please let me know:
1. What stage you're currently at (1-6)
2. Any issues you're encountering
3. What you'd like to do next

I'll provide specific guidance for your situation!
