---
name: rrwrite-research-literature
description: Performs deep literature research on manuscript topics and generates a comprehensive one-page summary of background and related work with citations.
arguments:
  - name: target_dir
    description: Output directory for manuscript files (e.g., manuscript/repo_v1)
    default: manuscript
allowed-tools:
context: fork
---
# Literature Research Protocol

## Purpose
Conduct comprehensive literature research on the manuscript topic and generate a structured summary of:
- Background context and foundations
- Related work and competing approaches
- Recent advances and state-of-the-art
- Gaps that the manuscript addresses

## Prerequisites
**Best if you have:**
- `manuscript_plan.md` (outline with research questions)
- Draft manuscript sections (especially Introduction/Methods)
- `references.bib` (existing citations to build upon)

**Minimum requirement:**
- PROJECT.md with clear research topic and key findings

## Workflow

### Phase 0: Version Reuse Detection (Automatic)

**Purpose:** Detect if a previous manuscript version exists with completed literature research and offer to reuse it as a starting point.

1. **Auto-Detect Previous Version:**
   ```bash
   python scripts/rrwrite_import_evidence_tool.py \
     --detect-only \
     --target-dir {target_dir}
   ```

2. **If Previous Version Found:**
   Display information about the detected version and ask user if they want to reuse the literature:

   ```
   ✓ Detected previous version: manuscript/project_v1
   - Created: 2026-02-05
   - Papers: 23
   - Status: Research completed

   Reuse literature from previous version as starting point?
   This will:
   - Import literature review and citations
   - Validate all DOIs (check if still accessible)
   - Allow you to expand with new recent papers

   Reuse previous literature? [Y/n]:
   ```

3. **If User Accepts (Y or blank):**

   **Step A: Import and Validate Evidence**
   ```bash
   python scripts/rrwrite_import_evidence_tool.py \
     --target-dir {target_dir} \
     --validate
   ```

   This imports:
   - `literature.md` (copied as base for expansion)
   - `literature_citations.bib` (validated subset only)
   - `literature_evidence.csv` (validated subset only)
   - `literature_evidence_metadata.json` (provenance tracking)

   Display results:
   ```
   VALIDATION RESULTS:
   ✓ Imported 20 of 23 papers from project_v1

   Papers imported:
     • 18 papers - Valid (DOI resolves, <5 years old)
     • 2 papers - Flagged for review (>5 years old, may need update)

   Papers excluded:
     • 3 papers - DOI does not resolve (404 error)
       → Check validation report for details: literature_evidence_validation.csv

   Next step: Review flagged papers and decide whether to:
     - Keep (foundational/seminal work)
     - Replace with newer reference
     - Remove if not appropriate
       → See details in: literature_evidence_validation.csv

   ============================================================
   IMPORT COMPLETE - Proceeding to NEW Literature Search
   ============================================================
   ```

   **Step B: Save imported files as backups**
   ```bash
   cp {target_dir}/literature_evidence.csv {target_dir}/literature_evidence_imported.csv
   cp {target_dir}/literature.md {target_dir}/literature_imported.md
   ```

   **Step C: CONTINUE AUTOMATICALLY to Phases 1-3**

   **IMPORTANT:** After import, the skill MUST continue to Phases 1-3 to conduct NEW literature search. This is not optional - it's the "review, extend, and refine" part of the workflow.

   **Adjusted search strategy for Phases 1-3:**
   - **Focus:** Papers from **last 2 years only** (2024-2026)
   - **Target:** 10-15 new papers (not 20-25)
   - **Avoid duplicates:** Check against `literature_evidence_imported.csv`
   - **Context:** Use imported `literature.md` to identify gaps and extensions
   - **Goal:** Update "Recent Advances" section with latest research

   **After Phase 3 (new search complete), merge automatically:**
   ```bash
   python scripts/rrwrite_import_evidence_tool.py \
     --merge \
     --old {target_dir}/literature_evidence_imported.csv \
     --new {target_dir}/literature_evidence_new.csv \
     --output {target_dir}/literature_evidence.csv
   ```

   **Final output:**
   - Updated `literature.md` with new papers integrated
   - Updated `literature_citations.bib` with all citations
   - Merged `literature_evidence.csv` (deduplicated by DOI)
   - Total: ~30 papers (20 from v1 + 10 new)

4. **If User Declines (n):**
   Skip to Phase 1 (fresh research from scratch)
   - Do not import any previous evidence
   - Follow standard workflow (20-25 papers total)

5. **If No Previous Version Found:**
   Skip to Phase 1 (fresh research from scratch)
   - No user prompt shown
   - Continue with normal workflow (20-25 papers total)

**Note:** Version reuse applies **only to literature evidence** (not repository evidence, as repos change).

### Phase 1: Topic Extraction
1. **Read Context Documents:**
   - Read `PROJECT.md` to understand the research domain
   - Read `manuscript_plan.md` if available (for detailed topics)
   - Read `{target_dir}/introduction.md` or `{target_dir}/abstract.md` if available
   - Read `references.bib` to see what's already cited
   - **If evidence was imported:** Read `{target_dir}/literature.md` and `{target_dir}/literature_evidence_imported.csv` to understand existing coverage

2. **Extract Key Research Topics:**
   - Primary methodology (e.g., "transformer-based protein structure prediction")
   - Domain area (e.g., "computational biology", "deep learning")
   - Specific techniques (e.g., "attention mechanisms", "MSA features")
   - Comparison methods (e.g., "AlphaFold2", "RoseTTAFold")
   - **If building on previous version:** Note topics already covered and identify gaps to fill

3. **Formulate Search Queries:**
   Create 3-5 targeted search queries combining:
   - Core method + domain
   - Technique + application
   - "Recent advances in [topic]"
   - "State of the art [domain]"
   - Each competing method mentioned

### Phase 2: Literature Search

**Search Strategy:**

**If building on previous version (evidence was imported in Phase 0):**
- **Focus exclusively on recent papers (2024-2026)**
- Target 10-15 new papers to add
- Check against `literature_evidence_imported.csv` to avoid duplicates
- Prioritize: NeurIPS 2024/2025, ICLR 2025, Nature/Science 2024+
- Query format: "[method] 2024", "[method] 2025", "[method] recent"

**If starting fresh (no previous version):**

**Use WebSearch tool to find:**
1. **Foundational Papers** (highly cited, >1000 citations)
   - Query: "[core method] review" OR "[domain] survey"
   - Focus on papers from last 5 years for reviews, last 10 for foundations

2. **Recent Advances** (last 2 years, 2024-2026)
   - Query: "[method] 2024" OR "[method] 2025" OR "[method] 2026"
   - Look for: NeurIPS, ICLR, ICML, Nature, Science papers

3. **Direct Competitors** (methods you're comparing against)
   - Query: exact names of competing methods
   - Find their original papers and recent improvements

4. **Application Domain** (specific to your problem)
   - Query: "[your application] + [your method type]"
   - Example: "protein structure prediction transformers"

**For each relevant paper found:**
- Extract: Authors, Title, Venue, Year, **DOI** (critical!)
- Note: Key contribution, methodology, results
- Record: Citation key format (e.g., author2024)
- **Capture direct quote**: Extract 1-2 sentences that best represent the key finding or contribution

### Phase 3: Synthesis

**If building on previous version:**
1. Read imported `{target_dir}/literature.md`
2. Integrate new papers into existing sections
3. Update "Recent Advances" section with 2024-2026 papers
4. Preserve existing foundational and related work sections
5. Mark additions with comment: `<!-- Added from v2 research 2026-02-08 -->`

**If starting fresh:**

Generate a structured summary in `{target_dir}/literature.md`:

```markdown
# Literature Review: [Manuscript Topic]

**Generated:** [Date]
**Based on:** [manuscript_plan.md / PROJECT.md]

## 1. Background & Foundations (200-300 words)

### Core Concepts
- [Topic 1]: Foundational work by [Author et al., Year]. Key insight: ...
- [Topic 2]: Established by [Author et al., Year]. Approach: ...

### Historical Context
- Evolution from [old method] to [current method]
- Major breakthrough: [cite landmark paper]

## 2. Related Work (300-400 words)

### Approach A: [Method Name]
- **Key Papers**: [Author1, Year], [Author2, Year]
- **Methodology**: [Brief description]
- **Strengths**: ...
- **Limitations**: ...

### Approach B: [Method Name]
- **Key Papers**: [Author3, Year], [Author4, Year]
- **Methodology**: [Brief description]
- **Strengths**: ...
- **Limitations**: ...

### Approach C: [Method Name]
- **Key Papers**: [Author5, Year]
- **Methodology**: [Brief description]
- **Strengths**: ...
- **Limitations**: ...

## 3. Recent Advances (200-300 words)

### State-of-the-Art
- [Recent Paper 1, 2024/2025]: Achieved [result]. Method: ...
- [Recent Paper 2, 2024/2025]: Novel approach using ...

### Current Trends
- Trend 1: [Description]
- Trend 2: [Description]

## 4. Research Gaps (100-150 words)

**Identified Gaps:**
1. [Gap 1 that your work addresses]
2. [Gap 2 that your work addresses]
3. [Gap 3 that your work addresses]

**How Our Work Fits:**
[Brief statement of how your manuscript fills these gaps]

## 5. Key Citations to Add

**Essential references to cite in manuscript:**

### Background (Introduction)
- [author2020]: Foundational work on [topic]
- [author2021]: Comprehensive review of [domain]

### Related Work (Methods/Discussion)
- [author2023]: Competing approach [Method A]
- [author2024]: Recent improvement to [Method B]
- [author2025]: State-of-the-art baseline

### Recent Comparisons (Results/Discussion)
- [author2024a]: Benchmark dataset
- [author2024b]: Performance comparison

## 6. Citation Integration Guide

**Where to cite what:**

**Introduction:**
- Cite [author2020, author2021] when introducing the problem
- Cite [author2023] when discussing prior approaches

**Methods:**
- Cite [author2022] when describing your architecture basis
- Cite [author2023] when contrasting with existing methods

**Results:**
- Cite [author2024a, author2024b] when presenting comparisons

**Discussion:**
- Cite [author2025] when positioning your work

---

## References to Add to references.bib

[Provide properly formatted BibTeX entries for all cited works]

```

### Phase 4: Citation File Generation

**If building on previous version:**
- Merge imported `{target_dir}/literature_citations.bib` with newly found papers
- Use merge script to avoid duplicates:
  ```bash
  python scripts/rrwrite_import_evidence_tool.py \
    --merge \
    --old {target_dir}/literature_evidence_imported.csv \
    --new {target_dir}/literature_evidence_new.csv \
    --output {target_dir}/literature_evidence.csv
  ```
- Update `literature_citations.bib` to include only papers in final merged evidence

**If starting fresh:**

Create or update `bib_additions.bib` with BibTeX entries for all newly found papers:

```bibtex
@article{author2024,
  title={Title of Paper},
  author={Author, First and Author, Second},
  journal={Journal/Conference},
  year={2024},
  doi={10.1234/journal.2024.12345},
  url={https://doi.org/10.1234/journal.2024.12345}
}
```

**CRITICAL**: Always include DOI when available. DOIs are permanent identifiers and essential for verification.

### Phase 5: Evidence Documentation

Create `literature_evidence.csv` with columns:

```csv
doi,citation_key,evidence
10.1038/s41586-021-03819-2,jumper2021,"We developed AlphaFold, a deep learning system that predicts protein structures with atomic accuracy even in cases in which no similar structure is known."
10.1126/science.abj8754,baek2021,"RoseTTAFold can generate accurate models of protein structures and complexes using as input only a protein sequence."
10.1093/bioinformatics/bty1057,author2024,"Our approach achieves 15% improvement over existing methods while reducing computational cost by 3-fold."
```

**Requirements for evidence quotes:**
- Extract 1-2 sentences that capture the KEY finding or contribution
- Use direct quotes (verbatim from the paper)
- Focus on quantitative results or novel methodological claims
- Ensure quote is self-contained and understandable
- Include page number in comment if possible

## Output Files

Generate **three files** in the `{target_dir}/` directory (per schema: schemas/manuscript.yaml):

1. **`{target_dir}/literature.md`**
   - One-page structured summary (800-1000 words)
   - Organized by themes, not chronologically
   - Includes citation keys in [author2024] format
   - **Each citation includes DOI**: e.g., [jumper2021, DOI:10.1038/...]
   - Required sections: Background, Related Work, Recent Advances, Research Gaps

2. **`{target_dir}/literature_citations.bib`**
   - BibTeX entries for all newly found references
   - **Must include DOI field** for each entry
   - Ready to append to existing references.bib

3. **`{target_dir}/literature_evidence.csv`**
   - **Three columns**: doi, citation_key, evidence
   - Direct quotes from each cited paper
   - Enables verification and evidence chains
   - Can be used to check claims against original sources

## Validation

After generating files, validate the literature review:
```bash
python scripts/rrwrite-validate-manuscript.py --file {target_dir}/literature.md --type literature
```

## State Update

After successful validation, update workflow state:

**If evidence was imported (building on previous version):**
```python
import sys
import json
from pathlib import Path
sys.path.insert(0, str(Path('scripts').resolve()))
from rrwrite_state_manager import StateManager

manager = StateManager(output_dir="{target_dir}")

# Load provenance metadata
with open('{target_dir}/literature_evidence_metadata.json', 'r') as f:
    metadata = json.load(f)

# Count papers
papers_imported = metadata['validation_summary']['papers_imported']
papers_new = len(pd.read_csv('{target_dir}/literature_evidence_new.csv'))

# Update state with import info
manager.update_research_with_import(
    source_version=metadata['source_version'],
    papers_imported=papers_imported,
    papers_new=papers_new,
    validation_summary=metadata['validation_summary']
)
```

**If starting fresh (no import):**
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path('scripts').resolve()))
from rrwrite_state_manager import StateManager

manager = StateManager(output_dir="{target_dir}")
# Count papers from literature_citations.bib
import re
with open('{target_dir}/literature_citations.bib', 'r') as f:
    papers_found = len(re.findall(r'^@\w+{', f.read(), re.MULTILINE))

manager.update_workflow_stage("research", status="completed",
                              file_path="{target_dir}/literature.md",
                              papers_found=papers_found)
```

Display updated progress:
```bash
python scripts/rrwrite-status.py --output-dir {target_dir}
```

If validation passes, confirm completion and show progress. If it fails, fix issues and re-validate.

## Quality Criteria

**Ensure the literature review:**
- ✅ Covers foundational work (pre-2020)
- ✅ Includes recent advances (2024-2026)
- ✅ Identifies all major competing approaches
- ✅ Explains relationships between methods
- ✅ Highlights gaps your work addresses
- ✅ Provides actionable integration guidance
- ✅ All citations are real and verifiable
- ✅ BibTeX entries are properly formatted
- ✅ **DOIs included for all papers** (when available)
- ✅ **Evidence quotes captured** for verification
- ✅ **literature_evidence.csv created** with direct quotes

## Search Strategy Notes

**Coverage targets:**
- 15-25 papers total
- 3-5 foundational/review papers
- 5-8 directly related work papers
- 4-6 recent advances (last 2 years)
- 2-4 competing method papers

**Quality indicators for papers:**
- Published in top-tier venues (Nature, Science, NeurIPS, ICML, ICLR)
- High citation count (>50 for recent, >500 for foundational)
- Relevant to your specific approach and domain
- Provides reproducible benchmarks or datasets

**Verification:**
- Cross-check papers exist via multiple sources
- **Prioritize papers with DOIs** (permanent identifiers)
- Accept arXiv IDs for preprints (format: arXiv:YYMM.NNNNN)
- Verify author names and publication years
- Confirm venue/journal names are correct
- **Extract direct quote from abstract or key results section**
- Record quote in evidence file for later verification

## Integration with Drafting

After generating the literature review:

1. **Update Introduction:**
   - Integrate background citations from Section 1
   - Add related work references from Section 2

2. **Update Methods:**
   - Add citations justifying methodological choices
   - Reference papers you're building upon or modifying

3. **Update Discussion:**
   - Compare your results to recent state-of-the-art
   - Position your work in context of current trends

4. **Inform Future Work:**
   - Cite papers suggesting future directions
   - Reference emerging techniques to try

## Example Usage

```
User: "Use /rrwrite-research-literature to research the background for my protein structure prediction paper"

Agent:
1. Reads PROJECT.md and manuscript_plan.md
2. Extracts topics: "transformer architecture", "protein folding", "AlphaFold2", "attention mechanisms"
3. Searches for:
   - "protein structure prediction review 2024"
   - "transformer protein folding"
   - "AlphaFold2 improvements 2024"
   - "attention mechanisms structural biology"
4. Finds 20 relevant papers with DOIs
5. Extracts direct quotes from each paper
6. Generates:
   - literature_review.md (structured summary, 950 words)
   - bib_additions.bib (20 BibTeX entries with DOIs)
   - literature_evidence.csv (20 rows with DOIs and quotes)
   - literature_integration_notes.md
7. Provides integration guidance

Output: "✓ Literature review complete. Found 20 relevant papers (5 foundational, 8 related work, 7 recent). Generated manuscript/literature.md (950 words), manuscript/literature_citations.bib (20 entries with DOIs), and manuscript/literature_evidence.csv (20 evidence quotes)."
```

## Evidence File Example

`literature_evidence.csv`:
```csv
doi,citation_key,evidence
10.1038/s41586-021-03819-2,jumper2021,"We developed AlphaFold, a deep learning system that predicts protein structures with atomic accuracy even in cases in which no similar structure is known. AlphaFold achieved a median accuracy of 92.4 GDT on CASP14 targets."
10.1126/science.abj8754,baek2021,"RoseTTAFold can generate accurate models of protein structures and complexes using as input only a protein sequence. The method achieves accuracy comparable to AlphaFold while being more computationally efficient."
10.1038/s41467-024-12345-6,yang2024,"We demonstrate that pre-trained protein language models can reduce MSA requirements by 80% while maintaining prediction accuracy above 85% on CASP15 targets."
arXiv:2401.12345,zhang2025,"Our efficient transformer architecture achieves real-time protein structure prediction (< 1 second per protein) with only 5% accuracy loss compared to AlphaFold2."
```

**Using the evidence file:**
- Cross-reference claims in your manuscript with direct quotes
- Verify that your interpretation aligns with original sources
- Provide evidence for peer reviewers if challenged
- Enable reproducible claim verification

## Limitations & Handling

**If no manuscript outline exists:**
- Use PROJECT.md "Key Findings" to infer topics
- Focus on broader domain literature
- Request user clarification on specific sub-topics

**If references.bib already extensive:**
- Compare found papers with existing citations
- Flag papers that should be added
- Suggest papers that might be outdated or less relevant

**If topic is very niche:**
- Expand search to broader domain
- Include methodological foundations even if not domain-specific
- Flag if insufficient literature found (suggest broadening)

## Notes

- **DO NOT hallucinate papers** - Only cite papers found via WebSearch or in references.bib
- **Verify all citations** - Double-check author names, years, venues
- **Always capture DOIs** - Essential for permanent identification and verification
- **Extract exact quotes** - Copy verbatim from paper abstract or results, no paraphrasing
- **Be selective** - Quality over quantity; cite only the most relevant papers
- **Stay current** - Prioritize papers from last 2-3 years for "Recent Advances"
- **Cross-reference** - If a paper cites another relevant paper, follow the trail
- **Use WebFetch if needed** - To read paper abstracts and extract accurate quotes
- **Format evidence properly** - Ensure CSV is properly escaped (quotes within quotes)
