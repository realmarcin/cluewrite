---
name: rrwrite-critique-manuscript
description: Use when manuscript draft exists and needs review. Runs two-stage review (content validity, then format compliance). Do NOT use before draft exists or for planning. Outputs separate content and format reports.
arguments:
  - name: target_dir
    description: Output directory for manuscript files (e.g., manuscript/repo_v1)
    default: manuscript
allowed-tools:
---
# Academic Critique Protocol

## Two-Stage Review Process

### Why Separate Stages?

1. **Different mindsets:** Content requires domain expertise and skepticism; format requires attention to detail
2. **Parallel execution:** Can run simultaneously with different agents
3. **Clear priorities:** Content issues are Major, format issues are Minor
4. **Reduced cognitive load:** Reviewer focuses on one concern type

### Stage 1: Content Review (Priority Issues)
**Focus:** Scientific validity, argument strength, evidence quality
**Mindset:** Skeptical scientist - assume claims are wrong until proven

```bash
python scripts/rrwrite-critique-content.py \
  --file {target_dir}/manuscript.md \
  --output {target_dir}/critique_content_v{N}.md
```

**Checks:**
- [ ] Does it answer the stated research question?
- [ ] Are all claims supported by evidence?
- [ ] Are there logical gaps in arguments?
- [ ] Is the narrative coherent?
- [ ] Are methods reproducible?
- [ ] Are results interpretations valid?

### Stage 2: Format Review (Secondary Issues)
**Focus:** Citation formatting, structure compliance, journal requirements
**Mindset:** Copy editor - trust content, verify presentation

```bash
python scripts/rrwrite-critique-format.py \
  --file {target_dir}/manuscript.md \
  --journal {journal} \
  --output {target_dir}/critique_format_v{N}.md
```

**Checks:**
- [ ] Citations complete and formatted correctly?
- [ ] Tables have captions and are numbered?
- [ ] Figures numbered correctly?
- [ ] No orphaned references?
- [ ] Word counts within limits?
- [ ] Required sections present?
- [ ] Journal-specific requirements met?

---

# Legacy Single-Stage Critique (Optional)

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
4.  **Availability Section Citations:**
    *   Check Data and Code Availability (or similar) sections for inappropriate citations.
    *   **ACCEPTABLE citations:** Specific tools/platforms (Zenodo DOI, Docker, GitHub, data repositories).
    *   **UNACCEPTABLE citations:** General methodology papers (FAIR principles, reproducibility frameworks, workflow standards).
    *   **Rationale:** Availability sections should contain factual access information, not methodology justifications.
    *   **Action if violated:** Flag as minor issue, recommend removing general citations and keeping only tool-specific ones.

5.  **Methods Section Citations:**
    *   Check Methods sections for abstract concept citations vs. specific tool citations.
    *   **ACCEPTABLE citations:**
        - Specific software tools actually used (e.g., LinkML for schema validation, pandas for data processing)
        - Datasets accessed (e.g., GTDB for taxonomic data, MediaDive for media formulations)
        - Published algorithms implemented (e.g., MaxPro for experimental design)
        - Computational methods applied (e.g., graph embeddings, flux balance analysis)
    *   **UNACCEPTABLE citations:**
        - Abstract principles (FAIR data sharing [Wilkinson2016], reproducibility frameworks)
        - General best practices papers (workflow standards, documentation guidelines)
        - Related tools NOT used (e.g., citing Manubot when not using it)
        - Methodological reviews unless specific method was implemented
    *   **Rationale:** Methods describes what was done in THIS work, not general field principles. Abstract concepts belong in Introduction or Discussion.
    *   **Action if violated:** Flag as minor issue. Recommend moving abstract principle citations to Introduction (for motivation) or Discussion (for broader context), keeping only tool-specific citations in Methods.

6.  **Results Section Citations:**
    *   Check Results sections for explanatory/justification citations vs. observational citations.
    *   **ACCEPTABLE citations:**
        - Papers/datasets analyzed or benchmarked (e.g., compared performance against [Smith2020])
        - Examples of findings (e.g., "identified papers including [Example2024, Example2025]")
        - Data sources processed (e.g., sequences from [GTDB2024])
        - Tools whose performance was measured
    *   **UNACCEPTABLE citations:**
        - Explaining concepts (e.g., "establishing provenance chains [citations]")
        - Justifying methodology (e.g., "addressing concerns about hallucination [citations]")
        - Future possibilities (e.g., "for future integration with standards [citations]")
        - Background context or motivation
    *   **Rationale:** Results reports OBSERVATIONS and MEASUREMENTS. Explanations belong in Introduction; justifications and future directions belong in Discussion.
    *   **Action if violated:** Flag as minor issue. Remove explanatory citations or move content to Discussion if it describes future directions or broader implications.

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
