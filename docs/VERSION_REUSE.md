# Version Reuse: Literature Evidence Import

## Overview

RRWrite supports reusing literature evidence from previous manuscript versions as a starting point for new versions. This feature:

- **Saves time** by avoiding redundant literature searches
- **Maintains continuity** across manuscript iterations
- **Validates evidence** to ensure DOIs still resolve and papers are current
- **Tracks provenance** with metadata about source versions and validation
- **Focuses new research** on recent papers (2024-2026)

## Benefits

### Time Savings
Instead of searching for 20-25 papers from scratch, you can:
1. Import 18-20 validated papers from v1
2. Search for 10-15 new recent papers
3. Merge to get 28-35 total papers

**Estimated time saved:** 30-45 minutes per version

### Quality Improvements
- Builds on previously vetted papers
- Ensures foundational citations are consistent
- Focuses effort on discovering recent advances
- Maintains citation continuity across versions

### Traceability
- Know which papers came from which version
- Track validation status and DOI health
- See when papers become stale (>5 years old)
- Review removed papers and reasons

## How It Works

### Automatic Detection

When you start literature research in a new version (e.g., `manuscript/project_v2`), RRWrite automatically:

1. Scans sibling directories (e.g., `manuscript/project_v1`)
2. Looks for versions with completed research (`.rrwrite/state.json`)
3. Identifies the most recent version with papers
4. Prompts you to reuse the literature

### User Workflow

```bash
# Start literature research in new version
cd manuscript/project_v2
python scripts/rrwrite-research-literature.py --target-dir .
```

**Phase 0: Auto-Detection**

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

**If you press Y (or Enter):**

The system executes a **three-step workflow**:

### Step 1: Import and Validate (Phase 0)
1. Copies `literature.md`, `literature_citations.bib`, `literature_evidence.csv` from v1
2. Validates each DOI via HTTP HEAD request
3. Checks paper freshness (flags papers >5 years old)
4. Removes papers with invalid DOIs
5. Saves validated evidence to v2
6. Creates backup files (`literature_evidence_imported.csv`)

**Validation Results:**

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

### Step 2: NEW Literature Search (Phases 1-3)

**IMPORTANT:** The workflow automatically continues to conduct a NEW literature search. This is the "review, extend, and refine" step:

**Search Strategy:**
- **Focus:** Papers from **2024-2026 only** (last 2 years)
- **Target:** 10-15 new papers
- **Topics:** Identified from imported literature + repository context
- **Queries:**
  - "AI-driven cultivation systems 2024"
  - "Multi-agent systems for science 2025"
  - "Knowledge graph applications biology 2024"
  - "High-throughput screening 2025"
- **Deduplication:** Check against imported papers to avoid duplicates

**Output:** `literature_evidence_new.csv` (10-15 recent papers)

### Step 3: Merge Evidence

Automatically merge imported + new papers:

```bash
python scripts/rrwrite_import_evidence_tool.py \
  --merge \
  --old literature_evidence_imported.csv \
  --new literature_evidence_new.csv \
  --output literature_evidence.csv
```

**Merge Results:**
```
Papers from previous version: 20
Papers from new search: 12
Duplicates removed: 2
Total merged papers: 30
```

**Final Outputs:**
- `literature.md` - Updated with new papers in "Recent Advances" section
- `literature_citations.bib` - All 30 citations
- `literature_evidence.csv` - Merged and deduplicated
- `literature_evidence_metadata.json` - Complete provenance tracking

### Why This Workflow?

**Review:** Validate that v1 papers are still current and accessible
**Extend:** Add 10-15 new papers from 2024-2026
**Refine:** Merge both sources, remove duplicates, update literature review

This approach:
- ✅ Saves time (don't re-search for foundational papers)
- ✅ Ensures currency (add latest 2024-2026 papers)
- ✅ Maintains quality (validate all DOIs, check freshness)
- ✅ Full traceability (provenance metadata tracks everything)

## Validation Process

### DOI Validation

For each paper in the previous version, the system:

1. **Checks if DOI resolves:**
   - HTTP HEAD request to `https://doi.org/{doi}`
   - 5 second timeout
   - Returns: `valid`, `invalid`, or `unknown`

2. **Actions based on status:**
   - `valid`: **Import** - Keep the paper (DOI resolves successfully)
   - `invalid` (404): **Exclude** - Remove the paper (DOI no longer resolves)
   - `unknown` (timeout/error): **Import with warning** - Keep but flag for manual check

### Freshness Check

Papers are categorized by age:

- **Fresh** (<5 years old): **Import** - No warning, automatically included
- **Stale** (5-10 years old): **Import with flag** - Flagged for manual review
- **Old** (>10 years old): **Import with flag** - Flagged for manual review

**IMPORTANT:** Stale/old papers are **ALWAYS imported** - they're never automatically removed. Age alone is not a reason to exclude a paper. The system only flags them for your manual review so you can decide:

- **Keep** - Foundational work, seminal papers, classic references
- **Replace** - Newer reference available that supersedes it
- **Remove** - Citation not appropriate or work has been superseded

Only papers with **invalid DOIs** (404 errors) are automatically excluded from import.

### Validation Report

A detailed validation report is saved to `{target_dir}/literature_evidence_validation.csv`:

```csv
doi,citation_key,citation,evidence_quote,doi_status,freshness,action,reason
10.1038/s41586-021-03819-2,jumper2021,"Jumper et al. (2021)","We developed AlphaFold...",valid,stale,review,Paper is 5 years old
10.1038/s41467-024-12345-6,yang2024,"Yang et al. (2024)","Novel approach...",valid,fresh,keep,Valid
10.9999/invalid.doi.12345,removed2020,"Removed et al. (2020)","Fake quote",invalid,fresh,remove,DOI does not resolve
```

**Understanding the columns:**

- `doi_status`: Result of DOI validation
  - `valid` = DOI resolves (HTTP 200)
  - `invalid` = DOI not found (HTTP 404)
  - `unknown` = Network error or timeout

- `freshness`: Age category
  - `fresh` = <5 years old
  - `stale` = 5-10 years old
  - `old` = >10 years old

- `action`: What happens to this paper
  - `keep` = Automatically imported (valid + fresh)
  - `review` = Imported but flagged for manual review (valid + stale/old)
  - `remove` = Excluded from import (invalid DOI only)

- `reason`: Explanation of the action

## Provenance Tracking

### Metadata File

The system generates `literature_evidence_metadata.json`:

```json
{
  "version": "1.0",
  "created": "2026-02-08T10:15:00",
  "source_version": "manuscript/project_v1",
  "source_git_commit": "a1b2c3d",
  "target_git_commit": "e4f5g6h",
  "validation_summary": {
    "papers_total_in_source": 23,
    "papers_imported": 20,
    "papers_removed": 3,
    "papers_need_review": 2,
    "validation_timestamp": "2026-02-08T10:15:00"
  },
  "files_imported": [
    "literature.md",
    "literature_evidence.csv",
    "literature_citations.bib"
  ]
}
```

### State Tracking

RRWrite updates `.rrwrite/state.json` to track the import:

```json
{
  "workflow_status": {
    "research": {
      "status": "completed",
      "papers_found": 30,
      "papers_from_previous": 20,
      "papers_new": 10,
      "source_version": "manuscript/project_v1",
      "validation_summary": {
        "papers_imported": 20,
        "papers_removed": 3,
        "papers_need_review": 2
      }
    }
  }
}
```

## Example Workflow

### Scenario: Creating v2 from v1 (Complete Workflow)

**v1 (completed):**
- 23 papers total
- Literature research completed on 2026-02-05
- Includes foundational work (2018-2022) and recent work (2023-2024)

**v2 (new version) - Three-Step Workflow:**

#### Step 1: Import and Validate (Phase 0)
```
✓ Detected previous version: manuscript/project_v1
Reuse previous literature? [Y/n]: Y

Validating evidence DOIs...

VALIDATION RESULTS:
✓ Imported 20 of 23 papers from project_v1

Papers imported:
  • 18 papers - Valid (DOI resolves, <5 years old)
  • 2 papers - Flagged for review (>5 years old, may need update)

Papers excluded:
  • 3 papers - DOI does not resolve (404 error)

IMPORT COMPLETE - Proceeding to NEW Literature Search
```

#### Step 2: NEW Literature Search (Phases 1-3)
```
Phase 1: Topic Extraction
✓ Extracted 8 topics from imported literature + repository
  - AI-driven cultivation systems
  - Multi-agent frameworks
  - Knowledge graph applications
  - High-throughput screening methods

Phase 2: Literature Search (2024-2026 only)
Searching: "AI cultivation systems 2024"
Searching: "multi-agent science 2025"
Searching: "knowledge graphs biology 2024"

✓ Found 12 new papers (2024-2026)

Phase 3: Evidence Extraction
✓ Extracted quotes from 12 papers
✓ Generated BibTeX entries with DOIs
```

#### Step 3: Merge Results
```
Merging evidence...

Papers from previous version: 20
Papers from new search: 12
Duplicates removed: 2
Total merged papers: 30

✓ Updated literature.md with new "Recent Advances" section
✓ Merged literature_citations.bib (30 entries)
✓ Merged literature_evidence.csv (30 rows)
✓ Updated provenance metadata
```

#### Final Result:
```
manuscript/project_v2/
├── literature.md                       # Updated with 12 new papers
├── literature_citations.bib            # 30 citations total
├── literature_evidence.csv             # 30 papers (merged)
├── literature_evidence_imported.csv    # 20 papers from v1 (backup)
├── literature_evidence_new.csv         # 12 papers from 2024-2026 (backup)
├── literature_evidence_validation.csv  # DOI validation report
└── literature_evidence_metadata.json   # Complete provenance

Total papers: 30 (20 from v1 + 10 new, 2 duplicates removed)
Time saved: ~45 minutes vs. searching 30 papers from scratch
```

### Scenario: Creating v3 from v2

RRWrite automatically detects v2 (most recent) and offers to import from it:

```
✓ Detected previous version: manuscript/project_v2
- Created: 2026-02-08
- Papers: 30
- Status: Research completed
(This version already imported from: manuscript/project_v1)

Reuse previous literature? [Y/n]:
```

**Chain builds:** v1 → v2 → v3

Each version builds on the previous, always using the most recent.

## Command-Line Tools

### Detect Previous Versions

```bash
python scripts/rrwrite_import_evidence_tool.py \
  --detect-only \
  --target-dir manuscript/project_v2
```

Shows what version would be detected without importing.

### Manual Import

```bash
python scripts/rrwrite_import_evidence_tool.py \
  --source manuscript/project_v1 \
  --target manuscript/project_v2 \
  --validate
```

Manually specify source version and import.

### Validation Only

```bash
python scripts/rrwrite_validate_evidence_tool.py \
  --csv manuscript/project_v1/literature_evidence.csv \
  --output validation_report.csv
```

Validate evidence without importing.

### Merge Evidence

```bash
python scripts/rrwrite_import_evidence_tool.py \
  --merge \
  --old manuscript/v2/literature_evidence_imported.csv \
  --new manuscript/v2/literature_evidence_new.csv \
  --output manuscript/v2/literature_evidence.csv
```

Merge imported and new evidence, deduplicating by DOI.

## Best Practices

### When to Reuse

✅ **Reuse when:**
- Creating a revised version of the same manuscript
- Updating a manuscript with new results
- Submitting to a different journal (same topic)
- Adding a new analysis to existing work

❌ **Don't reuse when:**
- Starting a completely different project
- Topic has significantly changed
- >2 years since v1 (papers may be too stale)

### Review Stale Papers

After import, review papers flagged as "stale":

```bash
# View validation report
cat manuscript/v2/literature_evidence_validation.csv | grep stale
```

**Consider:**
- Is the paper still relevant?
- Has it been superseded by newer work?
- Should I cite the original foundational paper or a more recent update?

### Focus New Research

When building on previous version:

- Search for papers from **last 2 years only** (2024-2026)
- Target **10-15 new papers** (not 20-25)
- Prioritize top-tier venues (Nature, Science, NeurIPS, ICLR)
- Update "Recent Advances" section with new findings

### Check for Duplicates

The merge process automatically deduplicates by DOI, keeping the most recent evidence quote if a DOI appears in both old and new searches.

## Troubleshooting

### No Previous Version Detected

**Problem:** System says "No previous version found"

**Causes:**
- No sibling directories with `.rrwrite/state.json`
- Previous version research status is not "completed"
- Previous version has 0 papers

**Solution:**
- Check if previous version exists in parent directory
- Verify `{prev_version}/.rrwrite/state.json` has research completed
- Use `--source` to manually specify version

### All Papers Marked Invalid

**Problem:** Validation removes all papers

**Causes:**
- Network connectivity issues
- DOI service temporarily down
- Source evidence used test/fake DOIs

**Solution:**
- Re-run validation later
- Use `--no-validate` to skip DOI checks
- Check `literature_evidence_validation.csv` for details

### Import Takes Too Long

**Problem:** Validation is very slow (DOI checks)

**Causes:**
- Validating 50+ papers
- Slow network connection
- DOI.org service latency

**Solution:**
- Use `--timeout` to reduce wait time per DOI
- Use `--no-validate` for initial import, validate later
- Run validation in background

### Duplicate Papers After Merge

**Problem:** Same paper appears twice in final evidence

**Causes:**
- Different DOIs for same paper (e.g., arXiv + journal)
- Typos in DOI

**Solution:**
- Manually review and remove duplicates
- Use citation key as secondary deduplication criterion

## Limitations

### Literature Evidence Only

Version reuse applies **only to literature evidence**, not repository evidence:

- ✅ Reused: `literature.md`, `literature_citations.bib`, `literature_evidence.csv`
- ❌ Not reused: Repository analysis, code evidence, data files

**Reason:** Repositories change between versions, so code evidence must be regenerated.

### Network Dependency

DOI validation requires internet access. If offline:
- Use `--no-validate` to skip validation
- Import without checks, validate later

### False Positives/Negatives

- Some valid DOIs may timeout (marked "unknown")
- Some invalid DOIs may return 200 (false positive)
- Freshness is based on year extraction (may be inaccurate)

**Best practice:** Review validation report manually, especially for "unknown" status.

## Implementation Details

### Files Created

1. **`literature_evidence_metadata.json`** - Provenance tracking
2. **`literature_evidence_validation.csv`** - Detailed validation report
3. **`literature_evidence_imported.csv`** - Backup of imported evidence (before merge)

### State Schema

Added to `.rrwrite/state.json`:

```json
"research": {
  "papers_from_previous": 20,
  "papers_new": 10,
  "source_version": "manuscript/project_v1",
  "validation_summary": {
    "papers_imported": 20,
    "papers_removed": 3,
    "papers_need_review": 2
  }
}
```

## Future Enhancements

Potential improvements:

- **Incremental validation:** Only re-validate papers older than N days
- **Citation update suggestions:** Flag papers with newer versions
- **Impact tracking:** Highlight highly-cited papers vs low-impact
- **Semantic deduplication:** Use embeddings to detect similar papers with different DOIs

## See Also

- [RRWrite Workflow Guide](WORKFLOW.md)
- [Literature Research Skill](../.claude/skills/rrwrite-research-literature/SKILL.md)
- [State Management](STATE_MANAGEMENT.md)
