---
name: rrwrite-workflow
description: Guide through the complete RRWrite manuscript generation workflow
---

# RRWrite Workflow Assistant

I'll guide you through the complete manuscript generation workflow. Let me first check what stage you're at.

## Current Project Status

Let me check your project structure:

**Files to check:**
- `PROJECT.md` - Your documented findings
- `manuscript_plan.md` - Manuscript outline
- `rrwrite-drafts/literature_review.md` - Literature research
- `rrwrite-drafts/*.md` - Drafted sections
- `references.bib` - Citations

## Complete Workflow

### Stage 1: Project Setup ✓/✗
**Prerequisites:**
- [ ] RRWrite installed globally
- [ ] Project directory initialized
- [ ] PROJECT.md created and filled out

**If not done:**
```bash
# Install RRWrite (one time)
cd /path/to/repo-research-writer && ./install.sh global

# Setup this project
cd /your/research/project
/path/to/repo-research-writer/install.sh setup-project

# Edit PROJECT.md with your findings
```

---

### Stage 2: Manuscript Planning ✓/✗
**Goal:** Create detailed outline

**Run:**
```
Use /rrwrite-plan-manuscript to create an outline for [Your Target Journal]
```

**Examples:**
- "Use /rrwrite-plan-manuscript for Nature Methods"
- "Use /rrwrite-plan-manuscript for PLOS Computational Biology"
- "Use /rrwrite-plan-manuscript for Bioinformatics"

**Output:** `manuscript_plan.md`

**Then critique:**
```
Use /rrwrite-critique-manuscript to critique manuscript_plan.md
```

---

### Stage 3: Literature Research ✓/✗
**Goal:** Find and document relevant papers

**Run:**
```
Use /rrwrite-research-literature to research background for [your topic]
```

**Example:**
```
Use /rrwrite-research-literature for transformer-based protein structure prediction
```

**Outputs:**
- `rrwrite-drafts/literature_review.md` (summary)
- `bib_additions.bib` (new citations with DOIs)
- `literature_evidence.csv` (quotes for verification)

**Then critique:**
```
Use /rrwrite-critique-manuscript to critique rrwrite-drafts/literature_review.md
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
   Use /rrwrite-draft-section to write the Methods section
   ```

2. **Results** (based on data)
   ```
   Use /rrwrite-draft-section to write the Results section
   ```

3. **Introduction** (with literature context)
   ```
   Use /rrwrite-draft-section to write the Introduction section
   ```

4. **Discussion** (synthesize everything)
   ```
   Use /rrwrite-draft-section to write the Discussion section
   ```

5. **Abstract** (summarize complete work)
   ```
   Use /rrwrite-draft-section to write the Abstract
   ```

**After each section, verify numbers:**
```bash
# Example: Check accuracy claim
python scripts/rrwrite-verify-stats.py \
  --file data/results.csv \
  --col accuracy \
  --op mean
```

---

### Stage 5: Manuscript Critique ✓/✗
**Goal:** Ensure quality and compliance

**Run:**
```
Use /rrwrite-critique-manuscript to critique the complete manuscript
```

**Specify file:**
```
Use /rrwrite-critique-manuscript to critique rrwrite-drafts/full_manuscript.md
```

**Output:** `critique_manuscript_round_1.md`

**Address feedback and iterate:**
1. Fix major issues (scientific gaps, missing data)
2. Fix minor issues (formatting, typos)
3. Re-critique until "accept with minor revisions"

---

### Stage 6: Final Assembly ✓/✗
**Goal:** Compile and prepare for submission

**Combine sections:**
```bash
cat rrwrite-drafts/abstract.md \
    rrwrite-drafts/introduction.md \
    rrwrite-drafts/methods.md \
    rrwrite-drafts/results.md \
    rrwrite-drafts/discussion.md \
    > rrwrite-drafts/full_manuscript.md
```

**Compile to PDF (if pandoc installed):**
```bash
pandoc rrwrite-drafts/full_manuscript.md \
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
"Use /rrwrite-plan-manuscript for [Journal]"

# Literature
"Use /rrwrite-research-literature for [topic]"

# Drafting (one at a time)
"Use /rrwrite-draft-section to write the Methods section"
"Use /rrwrite-draft-section to write the Results section"
"Use /rrwrite-draft-section to write the Introduction section"
"Use /rrwrite-draft-section to write the Discussion section"
"Use /rrwrite-draft-section to write the Abstract"

# Critiquing
"Use /rrwrite-critique-manuscript to critique [file]"
```

---

## Need Help?

- **Detailed workflow:** See `WORKFLOW.md` in RRWrite repository
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
