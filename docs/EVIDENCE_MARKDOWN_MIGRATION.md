# Evidence Format Migration: CSV → Markdown

**Date**: 2026-02-07
**Status**: ✅ COMPLETE

---

## Summary

Successfully migrated evidence tracking from CSV format to markdown format per user request:
> "make sure that evidence for literature citations is stored in a literature_evidence .md output file. and same for data or content referenced from the github repository in the manuscript, output a separate repo_evidence .md file."

---

## Files Created

### 1. Literature Evidence (20 citations)

**File**: `manuscript/data_sheets_schema_v1/literature_evidence.md`

**Format**:
```markdown
## [citation_key]: [Paper Title]

**Authors**: [Author list]
**Venue**: [Journal/Conference, Year]
**DOI**: [DOI]
**URL**: [Direct link]

**Evidence Quote**:
> "[Verbatim quote from paper]"

**Key Findings**:
- (Extract from full paper if needed)
```

**Content**: 20 literature citations with verbatim quotes from:
- Gebru 2021 (Datasheets for Datasets)
- Wilkinson 2016 (FAIR Principles)
- Pushkarna 2022 (Data Cards)
- Holland 2018 (Dataset Nutrition Label)
- Mitchell 2019 (Model Cards)
- Moxon 2025 (LinkML)
- Unni 2022 (Biolink Model)
- DCAT 2024, STANDING Together 2024
- Bridge2AI standards, JSON-LD, Healthcare AI
- And 9 more citations

### 2. Repository Evidence (18 claims)

**File**: `manuscript/data_sheets_schema_v1/repo_evidence.md`

**Format**:
```markdown
## Claim: "[Exact claim from manuscript]"

**Section**: [Section name]
**Evidence Source**: [Source type]

**Verification**:
```bash
[Command to verify]
```

**Output**:
```
[Command output]
```

**Status**: ✅ Verified | ⚠ Approximate | ❌ Unverified
```

**Content**: 18 claims extracted from manuscript:
- ✅ Verified: 0 (exact matches)
- ⚠ Approximate: 13 (close matches, manual review needed)
- ❌ Unverified: 5 (need manual identification)

**Claims tracked**:
- Git metadata: 372 commits (now 464), 12 contributors (now 11)
- Line counts: 254,000, 810,418, 4,365, 2,244, 449 lines
- Schema stats: 57 classes
- Version info: Python 3.9+, version 6
- Validation: 100% validation success

---

## Scripts Created

### 1. Repository Evidence Extractor

**File**: `scripts/rrwrite-extract-repo-evidence.py` (369 lines)

**Purpose**: Automatically extract factual claims from manuscript and generate verification commands

**Features**:
- Pattern matching for numerical claims (commits, files, lines, etc.)
- Git metadata verification (commits, contributors)
- File count verification with glob patterns
- Line count verification
- Version number detection
- Percentage detection
- Markdown output with verification status

**Usage**:
```bash
python3 scripts/rrwrite-extract-repo-evidence.py \
  --repo-path /path/to/repo \
  --manuscript manuscript/repo_v1/manuscript.md \
  --output manuscript/repo_v1/repo_evidence.md
```

**Output**: Markdown file with verification commands for each claim

### 2. CSV to Markdown Converter

**File**: `scripts/rrwrite-convert-evidence-to-md.py` (180 lines)

**Purpose**: One-time conversion of existing CSV evidence to markdown format

**Features**:
- Reads literature_evidence.csv
- Parses BibTeX for citation metadata
- Generates markdown with proper formatting
- Preserves verbatim quotes

**Usage**:
```bash
python3 scripts/rrwrite-convert-evidence-to-md.py \
  --csv manuscript/repo_v1/literature_evidence.csv \
  --bib manuscript/repo_v1/literature_citations.bib \
  --output manuscript/repo_v1/literature_evidence.md
```

**Status**: Used for migration, can be used for future conversions if needed

---

## Updated Documentation

### 1. Evidence Tracking Protocol

**File**: `docs/EVIDENCE_TRACKING.md` (402 lines)

**Updates**:
- Changed literature evidence format from CSV to markdown
- Added comprehensive examples for both formats
- Documented repository evidence extraction process
- Added verification workflow
- Integration with critique skill

**Key sections**:
- Literature Evidence format and examples
- Repository Evidence format and examples
- Verification workflow (during drafting, critique, submission)
- Automation support (extract, verify scripts)
- Integration with critique checklist

### 2. Literature Research Skill

**File**: `.claude/skills/rrwrite-research-literature/SKILL.md`

**Updates** (Phase 5):
- Changed output from `literature_evidence.csv` to `literature_evidence.md`
- Updated format specification to markdown
- Added examples with proper markdown structure
- Maintained requirement for verbatim quotes

**Output files**:
1. `literature.md` - Comprehensive review (unchanged)
2. `literature_citations.bib` - BibTeX entries (unchanged)
3. `literature_evidence.md` - Evidence quotes (NEW FORMAT)

---

## Testing Results

### Data Sheets Schema Manuscript

**Repository**: `/Users/marcin/Documents/VIMSS/ontology/bridge2ai/data-sheets-schema`
**Manuscript**: `manuscript/data_sheets_schema_v1/manuscript.md`

**Literature Evidence**:
- ✅ Successfully converted 20 citations from CSV to markdown
- ✅ All DOIs preserved
- ✅ Verbatim quotes intact
- ✅ Metadata extracted from BibTeX

**Repository Evidence**:
- ✅ Extracted 18 claims from manuscript
- ⚠ 13 require manual verification (specific files)
- ⚠ 2 claims outdated (commits: 372→464, contributors: 12→11)
- ❌ 5 claims need manual evidence (Python version, validation %)

**Recommendations**:
1. Update manuscript claims that are outdated (commits, contributors)
2. Identify specific files for line count claims
3. Add evidence for version requirements and validation percentages
4. Re-run extraction after manuscript updates

---

## Benefits of Markdown Format

### Readability
- ✅ Human-readable without parsing
- ✅ Proper formatting with headers and sections
- ✅ Easy to review in text editors or GitHub
- ✅ Better git diffs for tracking changes

### Maintainability
- ✅ Can be edited directly without CSV escaping issues
- ✅ Supports rich formatting (code blocks, quotes, lists)
- ✅ Each evidence entry is clearly separated
- ✅ Easy to add notes or key findings

### Integration
- ✅ Can be included in manuscript appendix
- ✅ Compatible with markdown-based workflows
- ✅ Easy to convert to other formats (HTML, PDF)
- ✅ Better integration with documentation systems

### Verification
- ✅ Code blocks for verification commands
- ✅ Clear status indicators (✅ ⚠ ❌)
- ✅ Separate output sections for results
- ✅ Easy to spot missing or outdated evidence

---

## Next Steps

### Immediate
1. ✅ Repository evidence extraction script created
2. ✅ CSV to markdown conversion script created
3. ✅ Data sheets schema evidence migrated
4. ✅ Documentation updated

### Future Work
1. **Update drafting skills** to automatically generate evidence entries as sections are written
   - Modify `rrwrite-draft-section` to track claims made
   - Auto-generate evidence stubs for numerical claims
   - Flag when repository verification is needed

2. **Create verification script** (`scripts/rrwrite-verify-evidence.py`)
   - Parse all verification commands from evidence files
   - Execute commands automatically
   - Compare outputs to recorded outputs
   - Flag discrepancies for manual review

3. **Update critique skill** to check evidence completeness
   - Verify all numerical claims have evidence entries
   - Check verification status (no ❌ unverified)
   - Ensure commit hash is current
   - Validate all literature citations have evidence quotes

4. **Add to workflow checklist**
   - Evidence tracking during drafting phase
   - Evidence verification before critique
   - Evidence freshness check before submission

---

## File Inventory

### Evidence Files (per manuscript)
- `manuscript/{repo}_v{N}/literature_evidence.md` - Literature citation evidence
- `manuscript/{repo}_v{N}/repo_evidence.md` - Repository content evidence
- `manuscript/{repo}_v{N}/literature_citations.bib` - BibTeX references (existing)

### Legacy Files (deprecated)
- `manuscript/{repo}_v{N}/literature_evidence.csv` - OLD FORMAT (can be deleted)

### Scripts
- `scripts/rrwrite-extract-repo-evidence.py` - Extract claims from manuscript
- `scripts/rrwrite-convert-evidence-to-md.py` - Convert CSV to markdown (one-time)

### Documentation
- `docs/EVIDENCE_TRACKING.md` - Comprehensive protocol
- `docs/EVIDENCE_MARKDOWN_MIGRATION.md` - This file

---

## Status

✅ **Migration complete**
✅ **Scripts implemented and tested**
✅ **Documentation updated**
✅ **Data sheets schema evidence generated**

**Ready for**: Next manuscript generation will use markdown evidence format automatically (once skills are updated)

---

## Impact on RRWrite Pipeline

### Modified Steps

**Step 4: Literature Research** (`/rrwrite-research-literature`)
- ✅ Now generates `literature_evidence.md` instead of CSV
- ✅ Markdown format with full citation metadata
- ✅ Verbatim quotes preserved

**Step 5-6: Section Drafting** (`/rrwrite-draft-section`)
- ⏳ Future: Auto-generate evidence stubs for claims made
- ⏳ Future: Track numerical claims during drafting

**Step 7: Critique** (`/rrwrite-critique-manuscript`)
- ⏳ Future: Check evidence file completeness
- ⏳ Future: Verify all claims have evidence
- ⏳ Future: Flag outdated or unverified claims

### New Capabilities

**Evidence Extraction**:
- Can extract claims from any existing manuscript
- Generates verification commands automatically
- Identifies claims needing manual review

**Evidence Verification**:
- Clear verification status for each claim
- Executable commands for reproducibility
- Tracks evidence source (git, files, etc.)

---

**Completed**: 2026-02-07
**Time**: ~30 minutes
**Files Created**: 4 (2 scripts, 2 evidence files, 1 doc)
**Documentation**: Updated 2 files, created 1 migration doc
