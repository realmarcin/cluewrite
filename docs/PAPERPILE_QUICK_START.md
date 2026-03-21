# Paperpile Citation Workflow - Quick Start

## 5-Step Complete Workflow

### Step 1: Extract Citations
```bash
python scripts/rrwrite-extract-paperpile-citations.py \
  --manuscript manuscript/kbaseeco_v2/manuscript_v2.md \
  --output manuscript/kbaseeco_v2/paperpile_citations_raw.json \
  --stats
```

**Output:** `paperpile_citations_raw.json` with parsed citations

---

### Step 2: Build BibTeX Bibliography
```bash
python scripts/rrwrite-build-bib-from-paperpile.py \
  --citations manuscript/kbaseeco_v2/paperpile_citations_raw.json \
  --output-bib manuscript/kbaseeco_v2/literature_citations.bib \
  --output-mapping manuscript/kbaseeco_v2/paperpile_mapping.json \
  --email your.email@example.com
```

**Outputs:**
- `literature_citations.bib` - BibTeX bibliography
- `paperpile_mapping.json` - Paperpile code → BibTeX key mapping
- `citation_extraction_report.md` - Quality report
- `citations_failed.json` - Failed matches (if any)

**⚠️ CRITICAL:** Review `citation_extraction_report.md` and verify DOIs match expected papers!

---

### Step 3: Generate Evidence CSV
```bash
python scripts/rrwrite-bib-to-evidence.py \
  --bib manuscript/kbaseeco_v2/literature_citations.bib \
  --output manuscript/kbaseeco_v2/literature_evidence.csv \
  --stats
```

**Output:** `literature_evidence.csv` for RRWrite validation

---

### Step 4: Validate Citations (NEW - Phase 2)
```bash
python scripts/rrwrite_citation_validator.py \
  --manuscript manuscript/kbaseeco_v2/manuscript_v2.md \
  --evidence manuscript/kbaseeco_v2/literature_evidence.csv \
  --bib manuscript/kbaseeco_v2/literature_citations.bib \
  --format paperpile \
  --paperpile-mapping manuscript/kbaseeco_v2/paperpile_mapping.json
```

**What it does:**
- Extracts Paperpile citations from manuscript
- Maps to BibTeX keys using mapping file
- Validates against evidence CSV
- Checks citation completeness

---

### Step 5: Assemble with Bibliography (NEW - Phase 2)
```bash
python scripts/rrwrite-assemble-manuscript.py \
  --output-dir manuscript/kbaseeco_v2
```

**What it does:**
- Auto-detects Paperpile citations
- Converts to BibTeX format (using mapping)
- Generates DOCX with formatted bibliography
- Creates PDF if pdflatex available

**Outputs:**
- `full_manuscript.md` - Markdown with BibTeX citations
- `full_manuscript.docx` - Word doc with bibliography
- `full_manuscript.pdf` - PDF (if available)

---

## Manual Review (REQUIRED)

After Step 2, **always check** `citation_extraction_report.md`:

```markdown
## Successfully Matched Citations

- `park2023`: (Park et al. 2023)
  - DOI: 10.46620/ursigass.2023.2947.nvsv8362  ← Verify this!
  - Confidence: 0.80
```

**If DOI is wrong:**
1. Look up correct DOI manually
2. Update `literature_citations.bib` with correct BibTeX entry
3. Update `paperpile_mapping.json` if citation key changed
4. Re-run Step 3

---

## Optional: Format Conversion

### Convert to BibTeX for RRWrite Editing
```bash
python scripts/rrwrite-convert-paperpile-citations.py \
  --manuscript manuscript_v2.md \
  --mapping paperpile_mapping.json \
  --output manuscript_v2_bibtex.md
```

**Use case:** Edit manuscript using native RRWrite tools (cleaner citations)

### Convert Back to Paperpile for Google Docs
```bash
python scripts/rrwrite-convert-bibtex-to-paperpile.py \
  --manuscript manuscript_v2_bibtex.md \
  --mapping paperpile_mapping.json \
  --output manuscript_v2_paperpile.md \
  --project-code aBwggu
```

**Use case:** Sync changes back to Google Docs with Paperpile

---

## Example: KBase Manuscript

```bash
cd /Users/marcin/Documents/VIMSS/ontology/repo-research-writer

# Step 1: Extract
python scripts/rrwrite-extract-paperpile-citations.py \
  --manuscript manuscript/kbaseeco_v2/manuscript_v2.md \
  --output manuscript/kbaseeco_v2/paperpile_citations_raw.json \
  --stats

# Step 2: Build BibTeX
python scripts/rrwrite-build-bib-from-paperpile.py \
  --citations manuscript/kbaseeco_v2/paperpile_citations_raw.json \
  --output-bib manuscript/kbaseeco_v2/literature_citations.bib \
  --output-mapping manuscript/kbaseeco_v2/paperpile_mapping.json \
  --email marcin@example.com

# Step 3: Generate evidence
python scripts/rrwrite-bib-to-evidence.py \
  --bib manuscript/kbaseeco_v2/literature_citations.bib \
  --output manuscript/kbaseeco_v2/literature_evidence.csv \
  --stats

# Step 4: Validate citations (NEW)
python scripts/rrwrite_citation_validator.py \
  --manuscript manuscript/kbaseeco_v2/manuscript_v2.md \
  --evidence manuscript/kbaseeco_v2/literature_evidence.csv \
  --bib manuscript/kbaseeco_v2/literature_citations.bib \
  --format paperpile \
  --paperpile-mapping manuscript/kbaseeco_v2/paperpile_mapping.json

# Step 5: Assemble with bibliography (NEW)
python scripts/rrwrite-assemble-manuscript.py \
  --output-dir manuscript/kbaseeco_v2

# Review outputs
ls -lh manuscript/kbaseeco_v2/full_manuscript.*
```

**Results:**
- ✓ Extracted 6 citations
- ✓ Matched 5 via CrossRef API (83.3% success)
- ⚠️ 1 failed (malformed citation)
- ⚠️ Manual review required for accuracy

---

## Files Generated

```
manuscript/kbaseeco_v2/
├── paperpile_citations_raw.json         # Extracted citations
├── literature_citations.bib             # BibTeX bibliography
├── paperpile_mapping.json               # Paperpile → BibTeX mapping
├── literature_evidence.csv              # RRWrite evidence database
├── citation_extraction_report.md        # Quality report (READ THIS!)
└── citations_failed.json                # Failed lookups
```

---

## Dependencies

```bash
pip install bibtexparser
```

---

## Full Documentation

See `docs/PAPERPILE_WORKFLOW.md` for:
- Detailed explanation of each script
- Alternative workflows (Paperpile export)
- Troubleshooting guide
- Future enhancements
- Best practices

---

## Implementation Status

See `PAPERPILE_IMPLEMENTATION_SUMMARY.md` for:
- What was implemented ✅
- What still needs work ⏳
- Known limitations ⚠️
- Test results 📊
