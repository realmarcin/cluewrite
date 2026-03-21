# Paperpile-to-RRWrite Citation Workflow

## Overview

This document describes the workflow for managing citations in manuscripts authored in **Google Docs with Paperpile**, then exported to DOCX/Markdown for editing in the RRWrite repository.

## Problem Statement

Manuscripts authored in Google Docs with Paperpile use a proprietary citation format:
```
[(Author et al. YEAR)](https://paperpile.com/c/PROJECT/CODE)
```

This format creates challenges for RRWrite integration:
- Paperpile links work for viewing but aren't compatible with RRWrite's citation validation system
- RRWrite expects BibTeX `.bib` files and `[authorYEAR]` citation keys
- Cannot use RRWrite's citation validation/assembly tools without proper bibliography infrastructure

## Solution: Three-Script Workflow

The Paperpile-to-RRWrite workflow consists of three Python scripts that extract citations, fetch bibliographic metadata, and generate RRWrite-compatible evidence files.

### Script 1: Extract Paperpile Citations

**Script:** `scripts/rrwrite-extract-paperpile-citations.py`

**Purpose:** Parse manuscript to extract all Paperpile citations and extract metadata from display text.

**Usage:**
```bash
python scripts/rrwrite-extract-paperpile-citations.py \
  --manuscript manuscript/kbaseeco_v2/manuscript_v2.md \
  --output manuscript/kbaseeco_v2/paperpile_citations_raw.json \
  --stats
```

**Output:** `paperpile_citations_raw.json`
```json
{
  "citations": [
    {
      "display_text": "(Park et al. 2023)",
      "project_code": "aBwggu",
      "paperpile_code": "opIz",
      "author": "Park",
      "year": "2023"
    }
  ]
}
```

**What it does:**
- Regex pattern: `\[(.*?)\]\(https://paperpile\.com/c/([^/]+)/([^\)]+)\)`
- Extracts author surname and year from display text
- Handles multi-citation codes (separated by `+`)
- Generates statistics (year range, top authors, parse failures)

**Known limitations:**
- Cannot parse citations split across lines (requires text preprocessing)
- Fails on malformed citations like `("Shap," n.d.)`
- Only captures in-text citations (`/c/` format), not bibliography links (`/b/` format)

---

### Script 2: Build BibTeX from Paperpile

**Script:** `scripts/rrwrite-build-bib-from-paperpile.py`

**Purpose:** Query CrossRef API with author+year, fetch BibTeX via DOI content negotiation, generate Paperpile→BibTeX mapping.

**Usage:**
```bash
python scripts/rrwrite-build-bib-from-paperpile.py \
  --citations manuscript/kbaseeco_v2/paperpile_citations_raw.json \
  --output-bib manuscript/kbaseeco_v2/literature_citations.bib \
  --output-mapping manuscript/kbaseeco_v2/paperpile_mapping.json \
  --email your.email@example.com \
  --confidence-threshold 0.5
```

**Outputs:**
1. **`literature_citations.bib`** - BibTeX bibliography
2. **`paperpile_mapping.json`** - Paperpile code → BibTeX key mapping
3. **`citation_extraction_report.md`** - Quality report with success/failure stats
4. **`citations_failed.json`** - Failed lookups requiring manual review

**What it does:**
1. For each citation:
   - Query CrossRef API: `https://api.crossref.org/works?query.author={author}&query.bibliographic={year}`
   - Rank results by relevance (author match + year match)
   - Fetch BibTeX via DOI content negotiation: `https://doi.org/{DOI}` with `Accept: application/x-bibtex`
2. Generate citation keys following RRWrite convention: `{author}{year}` (e.g., `park2023`)
3. Handle key collisions with suffixes: `park2023a`, `park2023b`
4. Create Paperpile mapping: `{"opIz": "park2023", "Omae": "zhang2024"}`

**Ranking algorithm:**
- **First author match**: +0.5
- **Year exact match**: +0.3
- **Year ±1**: +0.2
- **Auto-accept threshold**: 0.5 (configurable)

**Known limitations:**
- **⚠️ CRITICAL**: Author+year search is not specific enough
  - Common surnames (Park, Zhang, Wang) return many false positives
  - CrossRef may return wrong papers with same author/year
  - **Example**: Searching "Park 2023" returns drone classification paper instead of metagenome classification
- **Manual review required** for all auto-matched papers
- Rate limit: 10 requests/second (polite API usage)

**Mitigation strategies:**
1. **Use title keywords** (requires extracting from Paperpile export)
2. **Use DOIs directly** (requires Paperpile BibTeX export)
3. **Manual verification** of all matches via `citation_extraction_report.md`

---

### Script 3: Generate Evidence CSV

**Script:** `scripts/rrwrite-bib-to-evidence.py`

**Purpose:** Parse BibTeX file and generate `literature_evidence.csv` for RRWrite citation validation.

**Usage:**
```bash
python scripts/rrwrite-bib-to-evidence.py \
  --bib manuscript/kbaseeco_v2/literature_citations.bib \
  --output manuscript/kbaseeco_v2/literature_evidence.csv \
  --fetch-abstracts \
  --stats
```

**Output:** `literature_evidence.csv`
```csv
citation_key,doi,title,authors,year,journal,abstract,citation_type
park2023,10.46620/ursigass.2023.2947.nvsv8362,Drone Classification Model Using AI Algorithm,"Park J., Park S.",2023,Proceedings of the XXXVth URSI General Assembly,,conference
```

**What it does:**
- Parses BibTeX entries using `bibtexparser` library
- Extracts metadata: DOI, title, authors, year, journal
- Infers citation type (research_article, review, method, dataset, conference, preprint)
- Optionally fetches abstracts via CrossRef API (slower)

**Citation type inference:**
- **Preprint**: arXiv, bioRxiv, medRxiv journals
- **Conference**: `@inproceedings` or `@conference` entry type
- **Book**: `@book`, `@incollection` entry type
- **Review**: Title contains "review", "survey", "meta-analysis"
- **Method/Tool**: Title contains "method", "tool", "software", "algorithm"
- **Dataset**: Title contains "database", "dataset", "resource"
- **Default**: research_article

---

## Complete Workflow Example

### Step 1: Extract Citations

```bash
python scripts/rrwrite-extract-paperpile-citations.py \
  --manuscript manuscript/kbaseeco_v2/manuscript_v2.md \
  --output manuscript/kbaseeco_v2/paperpile_citations_raw.json \
  --stats
```

**Expected output:**
```
✓ Extracted 6 unique Paperpile citations
Year range: 2005 - 2024
⚠️  Parse failures: 1 (malformed citations)
```

---

### Step 2: Build BibTeX Bibliography

```bash
python scripts/rrwrite-build-bib-from-paperpile.py \
  --citations manuscript/kbaseeco_v2/paperpile_citations_raw.json \
  --output-bib manuscript/kbaseeco_v2/literature_citations.bib \
  --output-mapping manuscript/kbaseeco_v2/paperpile_mapping.json \
  --email your.email@example.com
```

**Expected output:**
```
Processing 1/6: (Park et al. 2023)... ✓ park2023 (score: 0.80)
Processing 2/6: (Zhang et al. 2024)... ✓ zhang2024 (score: 0.80)
...
✓ Successful: 5
❌ Failed: 1
Success rate: 83.3%
```

---

### Step 3: Manual Review (CRITICAL)

**Review `citation_extraction_report.md`:**
```markdown
## Successfully Matched Citations

- `park2023`: (Park et al. 2023)
  - DOI: 10.46620/ursigass.2023.2947.nvsv8362
  - Confidence: 0.80
```

**⚠️ Verify each match:**
1. Check DOI matches expected paper
2. Compare title with manuscript context
3. If wrong match:
   - Manually look up correct DOI
   - Update `literature_citations.bib`
   - Update `paperpile_mapping.json`

**Review `citations_failed.json`:**
```json
[
  {
    "citation": {"display_text": "(\"Shap,\" n.d.)"},
    "reason": "Failed to parse author or year",
    "top_candidate": null
  }
]
```

**Fix failures:**
1. Manually look up correct citation
2. Add BibTeX entry to `literature_citations.bib`
3. Add mapping to `paperpile_mapping.json`

---

### Step 4: Generate Evidence CSV

```bash
python scripts/rrwrite-bib-to-evidence.py \
  --bib manuscript/kbaseeco_v2/literature_citations.bib \
  --output manuscript/kbaseeco_v2/literature_evidence.csv \
  --stats
```

**Expected output:**
```
✓ Evidence CSV written to: manuscript/kbaseeco_v2/literature_evidence.csv
  5 entries
Citation type distribution:
  research_article: 4
  conference: 1
```

---

### Step 5: Validate Citations (RRWrite Integration)

Now you can use RRWrite's citation validation tools:

```bash
# Validate citations exist in bibliography
python scripts/rrwrite_citation_validator.py \
  --manuscript manuscript/kbaseeco_v2/manuscript_v2.md \
  --evidence manuscript/kbaseeco_v2/literature_evidence.csv \
  --paperpile-mapping manuscript/kbaseeco_v2/paperpile_mapping.json \
  --format paperpile
```

**Note:** This requires extending `rrwrite_citation_validator.py` to support Paperpile format (see Future Enhancements below).

---

## File Structure

After running the workflow:

```
manuscript/kbaseeco_v2/
├── manuscript_v2.md                     # Original manuscript with Paperpile links
├── paperpile_citations_raw.json         # Extracted citations (intermediate)
├── literature_citations.bib             # BibTeX bibliography
├── paperpile_mapping.json               # Paperpile code → BibTeX key mapping
├── literature_evidence.csv              # RRWrite evidence database
├── citation_extraction_report.md        # Quality report
└── citations_failed.json                # Failed lookups (if any)
```

---

## Alternative Workflows

### Option A: Paperpile BibTeX Export (Recommended)

If you have access to Paperpile:

1. **Export bibliography from Paperpile:**
   - Paperpile → File → Export → BibTeX
   - Save as `literature_citations.bib`

2. **Create mapping manually:**
   - Open manuscript in Google Docs
   - For each citation, note Paperpile code and author+year
   - Create `paperpile_mapping.json`:
     ```json
     {
       "opIz": "park2023",
       "Omae": "zhang2024"
     }
     ```

3. **Generate evidence CSV:**
   ```bash
   python scripts/rrwrite-bib-to-evidence.py \
     --bib literature_citations.bib \
     --output literature_evidence.csv
   ```

**Advantages:**
- Accurate BibTeX entries (no CrossRef matching needed)
- Abstracts included (if Paperpile has them)
- Faster (no API queries)

**Disadvantages:**
- Requires Paperpile access
- Manual mapping creation (unless automated)

---

### Option B: Convert to Native RRWrite Format

For manuscripts that will be heavily edited in the repository:

1. **Export Paperpile bibliography** (as above)

2. **Convert all Paperpile links to BibTeX keys:**
   ```bash
   python scripts/rrwrite-convert-paperpile-citations.py \
     --manuscript manuscript_v2.md \
     --mapping paperpile_mapping.json \
     --output manuscript_v2_bibtex.md
   ```
   **Result:** `[(Park et al. 2023)](link)` → `[park2023]`

3. **Use RRWrite tools natively** on `manuscript_v2_bibtex.md`

4. **When syncing back to Google Docs:**
   ```bash
   python scripts/rrwrite-convert-bibtex-to-paperpile.py \
     --manuscript manuscript_v2_bibtex.md \
     --mapping paperpile_mapping.json \
     --output manuscript_v2_paperpile.md
   ```

**Advantages:**
- Full RRWrite tool support
- Cleaner markdown (no long URLs)
- Better citation validation

**Disadvantages:**
- Requires conversion step
- Need reverse conversion for Google Docs sync

---

## Future Enhancements

### 1. Extend RRWrite Citation Validator

Add Paperpile format support to `scripts/rrwrite_citation_validator.py`:

```python
def extract_paperpile_citations(text):
    """Extract Paperpile citation codes from manuscript."""
    pattern = r'\[.*?\]\(https://paperpile\.com/c/[^/]+/([^\)]+)\)'
    return re.findall(pattern, text)

def map_to_bibtex_keys(paperpile_codes, mapping_file):
    """Convert Paperpile codes to BibTeX keys using mapping."""
    with open(mapping_file) as f:
        mapping = json.load(f)
    return [mapping.get(code) for code in paperpile_codes]
```

**Usage:**
```bash
python scripts/rrwrite_citation_validator.py \
  --manuscript manuscript_v2.md \
  --evidence literature_evidence.csv \
  --format paperpile \
  --paperpile-mapping paperpile_mapping.json
```

---

### 2. Extend Assembly for Paperpile

Modify `scripts/rrwrite-assemble-manuscript.py` to auto-convert Paperpile → BibTeX during assembly:

```python
# Detect Paperpile citations
if has_paperpile_citations(manuscript_text):
    # Convert to BibTeX keys
    manuscript_text = convert_paperpile_to_bibtex(
        manuscript_text,
        mapping_file='paperpile_mapping.json'
    )

# Run Pandoc with bibliography
subprocess.run([
    'pandoc', manuscript_text,
    '--bibliography=literature_citations.bib',
    '--citeproc',
    '--csl=nature.csl',
    '-o', 'manuscript_full.docx'
])
```

---

### 3. Improve CrossRef Matching

**Use title keywords from manuscript context:**

```python
# Extract surrounding sentence for title hints
context = extract_citation_context(manuscript_text, citation_position)
title_keywords = extract_keywords(context)

# Enhanced CrossRef search
results = api.search_by_author_year_title(
    author="Park",
    year="2023",
    title_keywords=["metagenome", "classification", "histidine kinase"]
)
```

**Use PubMed API as fallback:**

```python
# If CrossRef fails or low confidence
pubmed_results = search_pubmed(author, year, title_keywords)
ranked_results = merge_and_rank(crossref_results, pubmed_results)
```

---

### 4. Create Citation Format Converters

**Script:** `scripts/rrwrite-convert-paperpile-citations.py`
```bash
# Convert Paperpile links → BibTeX keys
python scripts/rrwrite-convert-paperpile-citations.py \
  --manuscript manuscript_v2.md \
  --mapping paperpile_mapping.json \
  --output manuscript_v2_bibtex.md
```

**Script:** `scripts/rrwrite-convert-bibtex-to-paperpile.py`
```bash
# Reverse: BibTeX keys → Paperpile links
python scripts/rrwrite-convert-bibtex-to-paperpile.py \
  --manuscript manuscript_v2_bibtex.md \
  --mapping paperpile_mapping.json \
  --output manuscript_v2_paperpile.md
```

---

## Troubleshooting

### Issue: Wrong papers matched by CrossRef

**Symptom:** `citation_extraction_report.md` shows incorrect titles/DOIs

**Cause:** Author+year search is too broad (common surnames)

**Solution:**
1. Review `citation_extraction_report.md`
2. Manually look up correct DOI for each citation
3. Edit `literature_citations.bib` with correct BibTeX entries
4. Update `paperpile_mapping.json` if citation keys changed
5. Re-run `rrwrite-bib-to-evidence.py`

---

### Issue: Citations split across lines not extracted

**Symptom:** Fewer citations extracted than expected

**Example:**
```
[(Author et al.
2023)](https://paperpile.com/c/PROJECT/CODE)
```

**Cause:** Regex doesn't match across newlines

**Solution:**
1. Preprocess manuscript to remove line breaks within citations:
   ```bash
   sed ':a;N;$!ba;s/\n/ /g' manuscript.md > manuscript_preprocessed.md
   ```
2. Run extraction on preprocessed file
3. **Or** manually add missing citations to `paperpile_citations_raw.json`

---

### Issue: Parse failures for malformed citations

**Symptom:** `⚠️ Parse failures: N` in extraction report

**Examples:**
- `("Shap," n.d.)` - no year
- `(Author)` - no year
- `(2023)` - no author

**Solution:**
1. Check `parse_failure_examples` in extraction report
2. Manually look up correct citation
3. Add to `paperpile_citations_raw.json` with correct author/year
4. Re-run BibTeX builder

---

## Best Practices

1. **Always run manual review** after Step 2 (BibTeX building)
   - CrossRef matching is not 100% accurate
   - Verify DOIs match expected papers

2. **Use Paperpile BibTeX export when possible**
   - More accurate than CrossRef API matching
   - Includes abstracts and complete metadata

3. **Maintain dual formats** during active editing
   - Keep `manuscript_v2.md` with Paperpile links (master)
   - Generate `manuscript_v2_bibtex.md` for RRWrite tools
   - Sync back to Google Docs using reverse converter

4. **Version control bibliography files**
   - Commit `literature_citations.bib` and `paperpile_mapping.json`
   - Track manual corrections in git history

5. **Document manual corrections**
   - Add comments to `citation_extraction_report.md`
   - Note which citations were manually verified

---

## Dependencies

- **Python 3.8+**
- **bibtexparser**: `pip install bibtexparser`
- **requests**: `pip install requests` (usually pre-installed)

Optional:
- **requests-cache**: `pip install requests-cache` (for API caching)

---

## References

- **CrossRef API**: https://www.crossref.org/documentation/retrieve-metadata/rest-api/
- **DOI Content Negotiation**: https://citation.crosscite.org/docs.html
- **BibTeX Format**: http://www.bibtex.org/Format/
- **Paperpile**: https://paperpile.com/
- **RRWrite Citation Validation**: `docs/citation-rules-by-section.md`

---

## License

Same as RRWrite project license.
