---
name: rrwrite-workflow
description: Use for complete end-to-end manuscript generation. Orchestrates all steps from repository analysis to final manuscript with validation gates, two-stage review, and citation verification. Equivalent to individual commands but fully automated.
arguments:
  - name: repo_path
    description: Path to research repository (local or GitHub URL)
    required: true
  - name: target_dir
    description: Output directory for manuscript (default: manuscript/reponame_v1)
    default: manuscript
allowed-tools:
context: fork
---

# RRWrite: Complete Manuscript Generation Workflow

Comprehensive, guided workflow incorporating all reliability improvements:
- ✅ Defense-in-depth citation validation (4 layers)
- ✅ Verification gates (no incomplete sections)
- ✅ Two-stage review (content + format)
- ✅ Rationalization counters (evidence-based error messages)
- ✅ Task decomposition (2-5 minute checkpoints)
- ✅ Root cause tracing (automated debugging)

## Quick Reference

| Phase | Time | Output | Validation |
|-------|------|--------|------------|
| 1. Analyze Repository | 2-5 min | repository_analysis.md, data tables | Auto |
| 2. Plan Manuscript | 3-5 min | outline.md | Word count, structure |
| 3. Assess Journal | 2-3 min | journal_assessment.md | User selection |
| 4. Research Literature | 5-10 min | literature.md, evidence.csv, citations.bib | DOI verification |
| 5. Draft Sections | 20-40 min | abstract.md, intro.md, etc. | **Verification gates** |
| 6. Assemble Manuscript | 1-2 min | manuscript.md | Citation sync, completeness |
| 7. Two-Stage Review | 10-15 min | critique_content.md, critique_format.md | Content → Format |

**Total:** 40-80 minutes | **Validation:** Continuous at every phase

---

## Phase 1: Repository Analysis

### Step 1.1: Analyze Repository Structure

```bash
python scripts/rrwrite-analyze-repository.py \
  --repo {repo_path} \
  --output {target_dir}
```

**Generates:**
- `repository_analysis.md` - Structure, files, dependencies
- `data_tables/` - File inventory, statistics, research indicators
- `repo_evidence.md` - Evidence database for claims

**Validation (automatic):**
- File count > 0
- README or documentation found
- At least one code file detected

**If validation fails:** Cannot proceed. Check repo path is correct.

---

## Phase 2: Manuscript Planning

### Step 2.1: Generate Outline

```bash
python scripts/rrwrite-plan-manuscript.py \
  --repo-analysis {target_dir}/repository_analysis.md \
  --output {target_dir}/outline.md
```

**Generates:**
- `outline.md` - Section structure, word targets, evidence mapping

**Validation:**
```bash
python scripts/rrwrite-validate-manuscript.py \
  --file {target_dir}/outline.md \
  --type outline
```

**Requirements:**
- [ ] All required sections present (Abstract, Intro, Methods, Results, Discussion)
- [ ] Word count ≥ 500 (detailed outline)
- [ ] Evidence files mapped

**If validation fails:** Review outline, add missing sections, ensure detail sufficient.

---

## Phase 3: Journal Assessment

### Step 3.1: Assess Target Journals

```bash
python scripts/rrwrite-assess-journal.py \
  --outline {target_dir}/outline.md \
  --output {target_dir}/journal_assessment.md
```

**Generates:**
- `journal_assessment.md` - 3-5 recommended journals with fit scores

### Step 3.2: Select Journal

**User decision required:** Review recommendations, select target journal.

**Options:**
1. Nature Methods (high impact, strict requirements)
2. PLOS Computational Biology (open access, broader scope)
3. Bioinformatics (specialized, faster review)

### Step 3.3: Fetch Guidelines

```bash
python scripts/rrwrite-fetch-guidelines.py \
  --journal {selected_journal} \
  --output {target_dir}/journal_guidelines.md
```

**Generates:**
- `journal_guidelines.md` - Author instructions, word limits, format requirements

---

## Phase 4: Literature Research

### Step 4.1: Detect Previous Version (Optional)

```bash
python scripts/rrwrite_import_evidence_tool.py \
  --detect-only \
  --target-dir {target_dir}
```

**If previous version found:** Prompt to reuse literature as base (DOIs validated, broken links excluded).

**Decision:** [Y]es to import + expand | [N]o to start fresh

### Step 4.2: Research Literature

```bash
python scripts/rrwrite-research-literature.py \
  --outline {target_dir}/outline.md \
  --target-dir {target_dir}
```

**Generates:**
- `literature.md` - 1-page summary (background, related work, gaps)
- `literature_evidence.csv` - Citation database (DOI, title, year, quote)
- `literature_citations.bib` - Bibliography (BibTeX format)

**Defense-in-Depth Layer 1 activated:** All citations validated on entry.

**Validation:**
```bash
python scripts/rrwrite-validate-manuscript.py \
  --file {target_dir}/literature.md \
  --type literature
```

**Requirements:**
- [ ] ≥ 10 citations (adequate coverage)
- [ ] All DOIs verified (resolve correctly)
- [ ] All required sections present (Background, Related Work, Gaps)
- [ ] Word count 800-1500

**If validation fails:** Run tracer to identify broken DOIs:
```bash
python scripts/rrwrite_citation_tracer.py {citation_key} literature {target_dir}
```

---

## Phase 5: Draft Sections (WITH VERIFICATION GATES)

### **CRITICAL: Iron Law of Academic Drafting**

**NO SECTION MARKED COMPLETE WITHOUT PASSING VERIFICATION GATE**

For each section:

### Step 5.1: Draft Section

```bash
python scripts/rrwrite-draft-section.py \
  --section {section_name} \
  --target-dir {target_dir}
```

**Task decomposition (2-5 minute chunks):**
- Task 1: First paragraph (2 min, verify word count + citations)
- Task 2: Second paragraph (3 min, verify appropriateness)
- Task 3: Third paragraph (2 min, verify no orphaned refs)
- Task 4: Final assembly (1 min, verify total word count ±20%)

**Defense-in-Depth Layers 1-2 activated:**
- Layer 1: Entry validation (citations in evidence file)
- Layer 2: Business logic (section appropriateness)

See `docs/citation-rules-by-section.md` for appropriate citation types.

### Step 5.2: VERIFICATION GATE (MANDATORY)

**Before proceeding to state update:**

```bash
python scripts/rrwrite-validate-manuscript.py \
  --file {target_dir}/{section_name}.md \
  --type section
```

**Checklist (ALL must pass):**
- [ ] Word count within ±20% of target
- [ ] All citations in literature_evidence.csv
- [ ] No orphaned figure/table references
- [ ] Required subsections present (if applicable)
- [ ] **Exit code = 0**

**If exit code ≠ 0:** DO NOT PROCEED. Fix errors, re-validate.

**Common rationalizations countered:**
| Thought | Reality |
|---------|---------|
| "I'll fix citations later" | 40% of citations forgotten → plagiarism risk |
| "Word count is close enough" | Journals auto-reject at limit violations |
| "This is just a draft" | First drafts with errors become habits |

See `docs/rationalization-table.md` for full list.

**If validation fails:** Use root cause tracer:
```bash
python scripts/rrwrite_citation_tracer.py {failing_citation} {section_name} {target_dir}
```

### Step 5.3: Update State (ONLY AFTER GATE PASSES)

```python
from rrwrite_state_manager import StateManager
manager = StateManager(output_dir="{target_dir}")
manager.add_section_completed("{section_name}")
```

### Step 5.4: Check Progress

```bash
python scripts/rrwrite-status.py --output-dir {target_dir}
```

**Repeat Steps 5.1-5.4 for all sections:**
1. abstract
2. introduction
3. methods
4. results
5. discussion
6. availability

**Section-specific citation rules enforced:**
- **Abstract:** 0-2 citations max
- **Introduction:** All types appropriate
- **Methods:** Tools/datasets only (NO abstract principles)
- **Results:** Observations only (NO explanations)
- **Discussion:** All types appropriate
- **Availability:** Platform-specific only (NO methodology papers)

---

## Phase 6: Assemble Manuscript

### Step 6.1: Assemble Sections

```bash
python scripts/rrwrite-assemble-manuscript.py \
  --target-dir {target_dir} \
  --journal {selected_journal}
```

**Generates:**
- `manuscript.md` - Complete assembled manuscript

**Defense-in-Depth Layer 3 activated:** Assembly validation
- All citations synchronized between text and bibliography
- No orphaned references
- Section order correct for journal
- Metadata complete

### Step 6.2: Validate Assembly

```bash
python scripts/rrwrite-validate-manuscript.py \
  --file {target_dir}/manuscript.md \
  --type manuscript
```

**Requirements:**
- [ ] All required sections present
- [ ] Total word count 1000-15000
- [ ] Citations synchronized (text ↔ bibliography)
- [ ] No orphaned tables/figures
- [ ] Journal limits respected (tables, figures)

**If validation fails:** Most commonly citation sync issues. Tracer identifies:
```bash
python scripts/rrwrite_citation_tracer.py {failing_citation} manuscript {target_dir}
```

---

## Phase 7: Two-Stage Review

### Stage 1: Content Review (PRIORITY ISSUES)

**Mindset:** Skeptical scientist - assume claims wrong until proven

```bash
python scripts/rrwrite-critique-content.py \
  --file {target_dir}/manuscript.md \
  --output {target_dir}/critique_content_v1.md
```

**Checks (6 validations):**
1. Research question clearly stated?
2. All claims supported by evidence?
3. Logical flow coherent?
4. Methods reproducible?
5. Results interpretations valid?
6. Narrative coherent?

**Output:** Major issues (content validity)

**Action:** Fix all major issues before format review.

### Stage 2: Format Review (SECONDARY ISSUES)

**Mindset:** Copy editor - trust content, verify presentation

```bash
python scripts/rrwrite-critique-format.py \
  --file {target_dir}/manuscript.md \
  --journal {selected_journal} \
  --output {target_dir}/critique_format_v1.md
```

**Checks (6 validations):**
1. Citations formatted correctly?
2. Tables numbered and captioned?
3. Figures referenced sequentially?
4. No orphaned references?
5. Word counts within journal limits?
6. Required sections present per journal?

**Output:** Minor issues (formatting)

**Action:** Fix formatting issues for polish.

### Why Two Stages?

- **Different mindsets:** Content = domain expertise + skepticism | Format = attention to detail
- **Clear priorities:** Major (content) before Minor (format)
- **Can parallelize:** Run both simultaneously, prioritize content fixes
- **Reduced cognitive load:** Focus on one concern type

---

## Final Output Structure

```
{target_dir}/
├── .git/                               # Version control
├── .rrwrite/
│   ├── state.json                      # Workflow state
│   └── citation_audit.jsonl            # Citation usage audit trail
├── repository_analysis.md              # Phase 1 output
├── outline.md                          # Phase 2 output (VALIDATED)
├── journal_assessment.md               # Phase 3 output
├── journal_guidelines.md               # Phase 3 output
├── literature.md                       # Phase 4 output (VALIDATED)
├── literature_evidence.csv             # Citation database (DOI verified)
├── literature_citations.bib            # Bibliography
├── repo_evidence.md                    # Evidence database
├── data_tables/                        # Repository tables
│   ├── file_inventory.tsv
│   ├── repository_statistics.tsv
│   └── research_indicators.tsv
├── sections/                           # Phase 5 outputs (ALL VALIDATED)
│   ├── abstract.md                     # ✅ Passed verification gate
│   ├── introduction.md                 # ✅ Passed verification gate
│   ├── methods.md                      # ✅ Passed verification gate
│   ├── results.md                      # ✅ Passed verification gate
│   ├── discussion.md                   # ✅ Passed verification gate
│   └── availability.md                 # ✅ Passed verification gate
├── manuscript.md                       # Phase 6 output (VALIDATED)
├── critique_content_v1.md              # Phase 7 Stage 1 output
└── critique_format_v1.md               # Phase 7 Stage 2 output
```

---

## Validation Summary

### Continuous Validation Throughout Workflow

| Phase | Validation Type | Tool | Enforcement |
|-------|----------------|------|-------------|
| 1. Analysis | Auto | Built-in checks | Soft (warnings) |
| 2. Outline | Manual | `rrwrite-validate-manuscript.py --type outline` | Required before proceeding |
| 4. Literature | Manual + Layer 1 | `rrwrite-validate-manuscript.py --type literature` | Required + DOI verification |
| 5. Each Section | **VERIFICATION GATE** | `rrwrite-validate-manuscript.py --type section` | **MANDATORY, exit code 0** |
| 6. Assembly | Layer 3 | `rrwrite-validate-manuscript.py --type manuscript` | Required + citation sync |
| 7. Content Review | Stage 1 | `rrwrite-critique-content.py` | Major issues must be fixed |
| 7. Format Review | Stage 2 | `rrwrite-critique-format.py` | Minor issues recommended fixes |

### Defense-in-Depth Citation Validation (Active Throughout)

**Layer 1: Entry Validation (Phase 4-5)**
- Fast-fail: Citation must be in evidence file before use

**Layer 2: Business Logic (Phase 5)**
- Section-specific appropriateness (Methods = tools, Results = observations)

**Layer 3: Assembly Validation (Phase 6)**
- Manuscript-wide completeness, bibliography synchronization

**Layer 4: Audit Trail (Continuous)**
- Citation usage logged for forensics and debugging

---

## Error Handling

### Common Errors and Solutions

| Error | Phase | Solution | Tool |
|-------|-------|----------|------|
| Citation not found | 5 (Draft) | Add to literature_evidence.csv | Root cause tracer |
| Word count violation | 5 (Draft) | Expand/condense section | Task decomposition |
| Broken DOI | 4 (Literature) | Find alternative source or remove | DOI validator |
| Citation sync failure | 6 (Assembly) | Fix bib entry or text citation | Citation tracer |
| Orphaned reference | 5-6 | Add figure/table or remove reference | Format validator |
| Incomplete section | 5 (Draft) | Cannot proceed, fix errors first | **Verification gate** |

### Root Cause Tracing (When Validation Fails)

```bash
python scripts/rrwrite_citation_tracer.py {citation_key} {section} {target_dir}
```

**Provides:**
- Level 1: Symptom observation
- Level 2: Immediate cause (where failing)
- Level 3: Usage trace (how got there)
- Level 4: Data origin (where added)
- Level 5: Trigger (when/why started)
- **Suggested fix:** Actionable commands
- **Prevention:** How to avoid recurrence

---

## Workflow State Management

### Check Current Status

```bash
python scripts/rrwrite-status.py --output-dir {target_dir}
```

**Shows:**
- Phase completion (which steps done)
- Section status (pending, in_progress, completed)
- Validation results (passed/failed per section)
- Next recommended action

### Resume Interrupted Workflow

State persists in `{target_dir}/.rrwrite/state.json`

**To resume:**
1. Check status: `python scripts/rrwrite-status.py --output-dir {target_dir}`
2. Identify incomplete phase
3. Re-run that phase's command
4. Continue from there

---

## Comparison: Comprehensive vs. Power User Workflow

### This Workflow (Comprehensive, Guided)

**Pros:**
- Fully automated orchestration
- Built-in validation at every step
- Verification gates prevent incomplete work
- Guided decisions (journal selection, etc.)
- Error messages explain why and what to do
- Task decomposition provides checkpoints

**Cons:**
- More verbose output
- Less granular control
- Must follow phase order

**Best for:** First-time users, complex manuscripts, wanting validation safety

### Power User Workflow (Individual Commands)

**Pros:**
- Granular control over each step
- Can skip/reorder phases as needed
- Parallel execution possible
- Expert mode (minimal output)
- JSON output for automation
- Shell aliases for speed

**Cons:**
- Must manage phase dependencies manually
- Must remember to validate
- More responsibility for correctness

**Best for:** Experienced users, iterative refinement, automation integration

**See:** `docs/power-user-workflow.md` for individual commands

---

## Success Metrics

### Expected Outcomes

After completing this workflow, you should have:

**Quality:**
- ✅ Zero incomplete sections (verification gates)
- ✅ Zero citation errors (defense-in-depth)
- ✅ All claims evidence-backed (audit trail)
- ✅ Reproducible methods (validation checks)
- ✅ Journal-compliant format (two-stage review)

**Files:**
- ✅ 15-20 markdown files (analysis, outline, sections, manuscript, reviews)
- ✅ 1 CSV (citation database)
- ✅ 1 BIB (bibliography)
- ✅ Data tables (repository statistics)
- ✅ Complete git history (version control)

**Validation:**
- ✅ All sections passed verification gates
- ✅ Manuscript passed assembly validation
- ✅ Content review completed (major issues addressed)
- ✅ Format review completed (minor issues noted)

**Time:**
- 40-80 minutes total (varies by repository size)
- ~2 hours if including revisions from critique

---

## Next Steps After Workflow Completion

### 1. Address Critique Issues

Review both critique reports:
```bash
cat {target_dir}/critique_content_v1.md
cat {target_dir}/critique_format_v1.md
```

**Fix major issues first** (content), then minor (format).

### 2. Iterate if Needed

For major revisions:
1. Edit affected sections directly: `{target_dir}/sections/{section}.md`
2. Re-validate each edited section: `python scripts/rrwrite-validate-manuscript.py --file ... --type section`
3. Re-assemble: `python scripts/rrwrite-assemble-manuscript.py --target-dir {target_dir}`
4. Re-critique: `python scripts/rrwrite-critique-content.py ...`

### 3. Export for Submission

```bash
# Convert to journal-specific format (if needed)
pandoc {target_dir}/manuscript.md -o {target_dir}/manuscript.docx
pandoc {target_dir}/manuscript.md -o {target_dir}/manuscript.pdf
```

### 4. Version Control

```bash
cd {target_dir}
git add .
git commit -m "Final manuscript draft v1

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
git tag v1.0
```

---

## Troubleshooting

### Workflow Stuck?

1. Check state: `python scripts/rrwrite-status.py --output-dir {target_dir}`
2. Identify failing phase
3. Run validation for that phase
4. If validation fails, use root cause tracer
5. Fix identified issue
6. Re-run phase command
7. Continue

### Need Help?

- **Validation errors:** See `docs/rationalization-table.md`
- **Citation issues:** Run `python scripts/rrwrite_citation_tracer.py ...`
- **Word count issues:** See `docs/2-5-minute-rule.md` for task decomposition
- **Section rules:** See `docs/citation-rules-by-section.md`

---

## Related Documentation

- `docs/citation-rules-by-section.md` - Citation appropriateness by section
- `docs/2-5-minute-rule.md` - Task decomposition pattern
- `docs/rationalization-table.md` - Common excuses and reality checks
- `docs/power-user-workflow.md` - Individual commands for granular control
- `IMPLEMENTATION_COMPLETE.md` - Technical details of improvements
