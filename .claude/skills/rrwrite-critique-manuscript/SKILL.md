---
name: rrwrite-critique-manuscript
description: Performs adversarial critique of manuscripts, outlines, literature reviews, or other academic content against journal requirements and quality standards.
arguments:
  - name: target_dir
    description: Output directory for manuscript files (e.g., manuscript/repo_v1)
    default: manuscript
allowed-tools:
---
# Academic Critique Protocol

## Scope
This skill can critique multiple types of academic content:
1. **Manuscript Drafts** - Full or partial manuscript sections
2. **Manuscript Outlines** - Structure and logical flow (manuscript_plan.md)
3. **Literature Reviews** - Background research summaries
4. **Critique Documents** - Meta-critique of other critiques

## Critique Style
Apply critical, demanding critique style focused on reproducibility, clarity, and rigor.

## Critique Mode Selection

**Automatically detect what is being critiqued:**

### If critiquing `manuscript_plan.md` (Outline):
Focus on:
- Logical flow and narrative arc
- Section ordering and dependencies
- Evidence-to-claim mapping
- Missing sections or components
- Target journal structure compliance

### If critiquing `{target_dir}/literature.md`:
Focus on:
- Coverage completeness (foundational, related, recent)
- Citation accuracy and verifiability
- Gap analysis clarity
- Integration guidance quality
- Balance between domains/approaches

### If critiquing manuscript drafts (`{target_dir}/*.md`):
Focus on:
- Technical accuracy and reproducibility
- Journal-specific compliance
- Citation integrity
- Data availability
- Writing quality

### If critiquing another critique document:
Focus on:
- Constructiveness of feedback
- Actionability of suggestions
- Coverage of critical issues
- Balance of criticism

---

## Compliance Checks (For Manuscript Drafts)

1.  **Journal Specifics:**
    *   *Nature Methods:* Check word count of the Abstract (max 150 words).
    *   *PLOS Computational Biology:* Verify presence of "Data Availability Statement" and "Ethics Statement".
    *   *Bioinformatics:* Check that the "Abstract" has structured headers.
2.  **Citation Integrity:**
    *   Scan text for citation keys (e.g., `[smith2020]`).
    *   Verify they exist in `bib_index.md` or `references.bib`.
    *   Flag any missing keys as "HALLUCINATION RISK".
3.  **Figure Callouts:**
    *   Ensure logical ordering (Figure 1 appears before Figure 2).
    *   Flag any figures in the `figures/` folder that are not referenced in the text.

## Additional Critique Criteria

### For Outlines (manuscript_plan.md):
1. **Structure:**
   - Does outline follow target journal format?
   - Are sections in logical order?
   - Is there clear progression from introduction to conclusion?

2. **Evidence Mapping:**
   - Is every claim linked to a specific data file?
   - Are figure references appropriate for each section?
   - Are code/script citations accurate?

3. **Completeness:**
   - Are all required sections present?
   - Is word count guidance realistic?
   - Are dependencies between sections clear?

### For Literature Reviews:
1. **Coverage:**
   - Are foundational papers included?
   - Are recent advances (last 2 years) covered?
   - Are all major competing methods discussed?

2. **Balance:**
   - Is there appropriate coverage across different approaches?
   - Are strengths AND limitations discussed?
   - Is the positioning of the manuscript work clear?

3. **Accuracy:**
   - Can all citations be verified?
   - Are author names, years, venues correct?
   - Are paper summaries accurate (not hallucinated)?

4. **Integration:**
   - Are there clear suggestions for where to cite papers?
   - Does it identify gaps the manuscript addresses?
   - Is there guidance for updating existing sections?

## Prose Linting (For Manuscript Drafts)

Run the prose linter:
`python scripts/rrwrite-lint-manuscript.py {target_dir}/full_manuscript.md`

## Output Format (per schema: schemas/manuscript.yaml)

Generate a critique report in `{target_dir}/` directory with naming convention:
- Manuscript: `{target_dir}/critique_manuscript_v1.md` (increment version number for subsequent critiques)
- Outline: `{target_dir}/critique_outline_v1.md`
- Literature: `{target_dir}/critique_literature_v1.md`
- Section: `{target_dir}/critique_section_v1.md`

**Filename pattern:** `critique_TYPE_vN.md` where TYPE is (outline|literature|section|manuscript) and N is version number

**Structure:**
```markdown
# Critique: [Document Type]

**Critiqued:** [Date]
**Document:** [File path]
**Target Journal:** [If applicable]

## Summary Assessment
[2-3 sentence overall evaluation]

## Strengths
1. [Positive aspect 1]
2. [Positive aspect 2]
3. [Positive aspect 3]

## Major Issues
1. **[Issue Category]:** [Description]
   - **Impact:** [Why this matters]
   - **Action:** [Specific fix required]

2. **[Issue Category]:** [Description]
   - **Impact:** [Why this matters]
   - **Action:** [Specific fix required]

## Minor Issues
1. **[Issue Category]:** [Description]
   - **Action:** [Quick fix]

2. **[Issue Category]:** [Description]
   - **Action:** [Quick fix]

## Compliance Checklist
[For manuscripts only]
- [ ] Abstract word count (if applicable)
- [ ] Citations verified
- [ ] Figures referenced
- [ ] Data availability statement
- [ ] Ethics statement (if needed)

## Actionable Next Steps
1. [Specific instruction for fixing issue 1]
2. [Specific instruction for fixing issue 2]
3. [Specific instruction for fixing issue 3]

## Recommendation
[ ] Accept with minor revisions
[ ] Major revisions required
[ ] Reject - fundamental issues
```

## Validation

After generating the critique, validate it:
```bash
python scripts/rrwrite-validate-manuscript.py --file {target_dir}/critique_TYPE_vN.md --type critique
```

## State Update

After successful validation, update workflow state with critique iteration:
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path('scripts').resolve()))
from rrwrite_state_manager import StateManager

manager = StateManager(output_dir="{target_dir}")

# Get version number from filename or use manager method
critique_type = "manuscript"  # or "outline", "literature", "section"
version = manager.get_next_critique_version(critique_type)

# Count issues from the critique file
major_issues = 0  # Count from "MAJOR:" sections in critique
minor_issues = 0  # Count from "MINOR:" sections in critique
recommendation = "MAJOR_REVISIONS"  # Extract from recommendation section

manager.add_critique_iteration(
    critique_type=critique_type,
    version=version,
    file_path=f"{target_dir}/critique_{critique_type}_v{version}.md",
    recommendation=recommendation,
    major_issues=major_issues,
    minor_issues=minor_issues
)
```

Display updated progress:
```bash
python scripts/rrwrite-status.py --output-dir {target_dir}
```

Report validation status, critique iteration, and updated workflow progress. If validation passes, confirm critique completion.
