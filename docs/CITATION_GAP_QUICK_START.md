# Citation Gap Analysis - Quick Start Guide

**Goal:** Identify missing citations in your Google Docs manuscript in 5 minutes.

## Prerequisites (One-Time Setup)

### 1. Install Dependencies

```bash
pip install -r requirements-gdocs.txt
pip install -r requirements.txt
```

### 2. Get Google API Credentials

**Option A - OAuth2 (Recommended for personal use):**

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create project → Enable "Google Docs API" + "Google Drive API"
3. Create OAuth 2.0 Client ID → Download `credentials.json`
4. Place in repo root: `repo-research-writer/credentials.json`

**Option B - Service Account (For automation):**

1. Create Service Account → Download JSON key
2. Rename to `credentials.json`
3. **Important:** Share your Google Doc with service account email

See: `docs/GDOC_API_SETUP.md` for detailed setup

## Run Analysis (3 Commands)

### Step 1: Get Your Document ID

Open your Google Doc, copy the ID from URL:

```
https://docs.google.com/document/d/1ABC_XYZ_DOCUMENT_ID_HERE/edit
                                  ^^^^^^^^^^^^^^^^^^^^^^^^
```

### Step 2: Run Workflow

```bash
python scripts/rrwrite-gdoc-citation-gap-workflow.py \
    --document-id YOUR_DOCUMENT_ID_HERE \
    --output-dir manuscript/citation_gaps
```

**Runtime:** 5-15 minutes (first run), 30-60 seconds (cached)

### Step 3: Read Report

```bash
open manuscript/citation_gaps/citation_gap_report.md
```

Or view JSON for programmatic access:

```bash
cat manuscript/citation_gaps/citation_gap_report.json | jq '.summary'
```

## What You Get

```
manuscript/citation_gaps/
├── citation_gap_report.md     ← READ THIS FIRST
├── citation_gap_report.json   ← Machine-readable data
├── manuscript.docx            ← Downloaded copy
├── extracted_citations.json   ← Current citations (42 found)
├── gap_analysis.json          ← Complete analysis results
└── tier*.json                 ← Search results (cached)
```

## Understanding the Report

### Section 2: Critical Gaps (Must-Cite)

Papers with:
- **>100 citations** (high impact)
- **>70% semantic overlap** with your manuscript
- **Direct methodological relevance**

**Action:** Add these before submission to avoid reviewer criticism

### Section 3: Recommended Additions (Should-Cite)

Papers that strengthen your manuscript:
- **50-100 citations** (medium impact)
- **Relevant to your methods/results**

**Action:** Add to broaden literature coverage

### Section 4: Optional Citations

Recent or niche papers:
- **<50 citations** or very recent (<1 year)
- **Emerging work or specialized topics**

**Action:** Consider for discussion section

## Common Issues

### "Credentials file not found"

**Fix:** Place `credentials.json` in repo root

```bash
ls credentials.json  # Should exist
```

### "Permission denied for document"

**Fix (OAuth2):** Browser will open for sign-in
**Fix (Service Account):** Share doc with service account email

### "No citations found"

**Possible causes:**
- Manuscript uses images/screenshots for citations
- Citations in footnotes (not main text)
- Unsupported format

**Fix:** Check `extracted_citations.json` statistics

### "scikit-learn not installed"

**Impact:** Semantic similarity disabled (still works, but less accurate)

**Fix:**
```bash
pip install scikit-learn
```

## Next Steps

1. **Review critical gaps** in Section 2 of report
2. **Download PDFs** for papers you want to add
3. **Add to BibTeX:** `literature_citations.bib`
4. **Add evidence:** `literature_evidence.csv`
5. **Update manuscript** with new citations
6. **Re-run analysis** to verify gaps addressed

## Customization

### Run Only Tier 1 (Fast Mode - 2 minutes)

```bash
python scripts/rrwrite-gdoc-citation-gap-workflow.py \
    --document-id YOUR_ID \
    --output-dir manuscript/citation_gaps \
    --search-tiers 1
```

### Run All Tiers (Comprehensive - 15 minutes)

```bash
python scripts/rrwrite-gdoc-citation-gap-workflow.py \
    --document-id YOUR_ID \
    --output-dir manuscript/citation_gaps \
    --search-tiers 1,2,3
```

### Adjust Sensitivity

**More gaps** (may include false positives):

```bash
python scripts/rrwrite-citation-gap-analyzer.py \
    --manuscript-citations extracted_citations.json \
    --search-results tier*.json \
    --output gap_analysis.json \
    --similarity-threshold 0.60
```

**Fewer gaps** (only very similar papers):

```bash
--similarity-threshold 0.80
```

## Integration with Existing Workflow

### After RRWrite Generation

```bash
# 1. Generate manuscript
/rrwrite --repo /path/to/repo

# 2. Export to Google Docs (manual)
# Copy manuscript/project_v1/manuscript.md to Google Docs

# 3. Run gap analysis
python scripts/rrwrite-gdoc-citation-gap-workflow.py \
    --document-id YOUR_ID \
    --output-dir manuscript/project_v1/citation_gaps

# 4. Add missing citations
# (Update literature_evidence.csv based on report)

# 5. Re-generate sections
/rrwrite-draft-section --section introduction
/rrwrite-assemble
```

## Performance Tips

- **Use cache:** 24-hour cache speeds up repeated runs
- **Run tier 1 first:** Get quick results, then run tiers 2-3 if needed
- **Run overnight:** Comprehensive 3-tier search takes 10-15 min
- **Re-use search results:** `tier*.json` files can be reused for different manuscripts

## Example Output

```
=== Citation Statistics ===
Total citations: 42
By type:
  paperpile: 40
  bracketed: 2

Year range: 2019 - 2024

Top years:
  2024: 15
  2023: 12
  2022: 8

✅ Gap analysis complete!
  Total gaps: 23
  Critical: 5    ← ADD THESE
  Important: 12  ← CONSIDER THESE
  Optional: 6    ← OPTIONAL
```

## Help & Support

**Full documentation:** `docs/CITATION_GAP_ANALYSIS.md`
**Google API setup:** `docs/GDOC_API_SETUP.md`
**Issues:** https://github.com/your-repo/rrwrite/issues

---

**Ready to start?** Run the workflow command above with your document ID!
