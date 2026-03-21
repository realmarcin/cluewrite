# Citation Gap Analysis for Google Docs Manuscripts

**RRWrite Citation Gap Analyzer** identifies missing citations in Google Docs manuscripts by comparing current citations against targeted literature searches with semantic similarity analysis.

## Overview

This tool performs **read-only analysis** of Google Docs manuscripts to identify citation gaps. It does NOT modify your manuscript - only generates analysis reports.

### What It Does

1. **Downloads** Google Doc as DOCX (local copy for analysis)
2. **Extracts** citations from manuscript (Paperpile, bracketed, or numbered formats)
3. **Searches** literature with multi-tier queries (foundational + emerging + overlapping methods)
4. **Analyzes** gaps using 4-layer analysis:
   - Layer 1: Exact DOI/title matching
   - Layer 2: Semantic overlap detection (TF-IDF similarity)
   - Layer 3: Citation type categorization (tool, method, review, etc.)
   - Layer 4: Citation network analysis (impact-based prioritization)
5. **Generates** actionable reports (Markdown + JSON)

### What It Doesn't Do

- ❌ Modify your Google Doc
- ❌ Auto-add citations to manuscript
- ❌ Upload changes to Google Drive

This is a **gap identification tool**, not an auto-citation tool.

## Prerequisites

### 1. Google Cloud Setup

Enable Google Docs API + Google Drive API:

1. Visit [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project or select existing
3. Enable APIs:
   - Google Docs API
   - Google Drive API
4. Create credentials:
   - **Option A (OAuth2):** Create OAuth2 Client ID → Download `credentials.json`
   - **Option B (Service Account):** Create Service Account → Download JSON key
5. Grant permissions:
   - OAuth2: Browser-based auth flow (one-time)
   - Service Account: Share doc with service account email

See: `docs/GDOC_API_SETUP.md` for detailed instructions

### 2. Python Dependencies

Install required packages:

```bash
# Google Docs API dependencies
pip install -r requirements-gdocs.txt

# Analysis dependencies
pip install -r requirements.txt
```

**Key packages:**
- `google-api-python-client` - Google Docs/Drive API client
- `python-docx` - DOCX parsing for citation extraction
- `scikit-learn` - TF-IDF semantic similarity (optional but recommended)

## Usage

### Quick Start (End-to-End Workflow)

Run complete workflow with single command:

```bash
python scripts/rrwrite-gdoc-citation-gap-workflow.py \
    --document-id 1ABC...XYZ \
    --output-dir manuscript/citation_gap_analysis \
    --search-tiers 1,2,3 \
    --credentials credentials.json
```

**Arguments:**
- `--document-id`: Google Doc ID (from URL: `docs.google.com/document/d/{DOCUMENT_ID}/edit`)
- `--output-dir`: Output directory for all results
- `--search-tiers`: Comma-separated tiers to execute (1=foundational, 2=overlapping, 3=infrastructure)
- `--credentials`: Path to `credentials.json` (OAuth2 or Service Account)

**Output:**
```
manuscript/citation_gap_analysis/
├── manuscript.docx                  # Downloaded Google Doc
├── manuscript.metadata.json         # Document metadata
├── extracted_citations.json         # Extracted citations with stats
├── tier1_merged.json                # Tier 1 search results
├── tier2_merged.json                # Tier 2 search results
├── tier3_merged.json                # Tier 3 search results
├── gap_analysis.json                # Complete gap analysis results
├── citation_gap_report.md           # Human-readable report
└── citation_gap_report.json         # Machine-readable report
```

**Runtime:** 5-15 minutes (depends on search tier count and API latency)

### Step-by-Step Workflow

For more control, run individual steps:

#### Step 1: Download Google Doc

```bash
python scripts/rrwrite-download-gdoc.py \
    --document-id 1ABC...XYZ \
    --output manuscript.docx \
    --credentials credentials.json \
    --save-metadata \
    --verbose
```

**Output:**
- `manuscript.docx` - Downloaded document
- `manuscript.metadata.json` - Title, revision ID, timestamp

#### Step 2: Extract Citations

```bash
python scripts/rrwrite-extract-gdoc-citations.py \
    --docx manuscript.docx \
    --output extracted_citations.json \
    --stats
```

**Supported formats:**
- **Paperpile:** `[(Author et al. 2024)](https://paperpile.com/c/PROJECT/CODE)`
- **Bracketed:** `[Author2024]`, `[Author2024a]`
- **Numbered:** `[1]`, `[2]`, `[3-5]`

**Output:**
```json
{
  "statistics": {
    "total_citations": 42,
    "by_type": {"paperpile": 40, "bracketed": 2},
    "year_range": {"earliest": "2019", "latest": "2024"}
  },
  "citations": [...]
}
```

#### Step 3: Literature Search (Multi-Tier)

**Tier 1 - Direct Method Match** (foundational, highly-cited):

```bash
python scripts/rrwrite-search-literature.py \
    "automated manuscript generation from code repositories" \
    --max-results 20 \
    --output tier1_results.json
```

**Tier 2 - Overlapping Approaches** (recent, specialized):

```bash
python scripts/rrwrite-search-literature.py \
    "computational notebook scientific publishing" \
    --max-results 15 \
    --output tier2_query1.json

python scripts/rrwrite-search-literature.py \
    "repository analysis automated documentation" \
    --max-results 15 \
    --output tier2_query2.json
```

**Tier 3 - Related Infrastructure** (foundational):

```bash
python scripts/rrwrite-search-literature.py \
    "FAIR principles software research" \
    --max-results 10 \
    --output tier3_results.json
```

**Notes:**
- Uses 24-hour SQLite cache to avoid redundant API calls
- Searches Semantic Scholar + PubMed in parallel
- Automatically deduplicates by DOI

#### Step 4: Gap Analysis

```bash
python scripts/rrwrite-citation-gap-analyzer.py \
    --manuscript-citations extracted_citations.json \
    --search-results tier1_results.json tier2_query1.json tier2_query2.json \
    --output gap_analysis.json \
    --similarity-threshold 0.70
```

**Arguments:**
- `--similarity-threshold`: TF-IDF cosine similarity threshold (0-1, default: 0.70)

**Output:**
```json
{
  "summary": {
    "total_gaps": 23,
    "by_priority": {
      "critical": 5,
      "important": 12,
      "optional": 6
    },
    "semantic_overlap_count": 8
  },
  "gaps": [...]
}
```

#### Step 5: Generate Reports

```bash
python scripts/rrwrite-generate-gap-report.py \
    --gap-analysis gap_analysis.json \
    --output-dir manuscript/citation_gap_analysis
```

**Output:**
- `citation_gap_report.md` - Human-readable report with actionable recommendations
- `citation_gap_report.json` - Machine-readable structured data

## Report Structure

### Markdown Report Sections

**1. Executive Summary**
- Current citation count
- Missing citation count
- Critical vs. important gaps
- Overall recommendation

**2. Current Citation Profile**
- Citation count by type
- Citation count by year
- Citation distribution

**3. Critical Gaps (Must-Cite)**
- Highly-cited papers (>100 citations) with direct overlap
- Recommended for: avoiding reviewer criticism

**For each gap:**
```
### 1. [Paper Title]

**Authors:** First Author et al.
**Year:** 2024
**DOI:** 10.1234/example
**Citations:** 523
**Type:** method

**Why Missing:**
- Semantic overlap: 85%
- Citation impact: 523 citations
- Priority score: 8/10

**Relevance:**
[Abstract excerpt]

**Recommended Section:** Methods

**Suggested Context:**
"For this analysis, we used [Paper Title] [Author et al. 2024]."
```

**4. Recommended Additions (Should-Cite)**
- Medium-cited papers with relevance
- Grouped by citation type (method, tool, review, etc.)

**5. Optional Citations (Emerging Work)**
- Recent papers (<2 years) or niche topics
- Top 10 by year + citations

**6. Actionable Recommendations**
- Immediate actions (next draft)
- Medium priority (post-review)
- Low priority (optional)
- Next steps (automated workflow)

### JSON Report Structure

```json
{
  "report_metadata": {...},
  "summary": {...},
  "gaps_by_priority": {
    "critical": [...],
    "important": [...],
    "optional": [...]
  },
  "gaps_by_type": {
    "method": [...],
    "tool": [...],
    "review": [...]
  },
  "all_gaps": [...]
}
```

## Search Tier Definitions

### Tier 1: Direct Method Match

**Focus:** Foundational papers with direct methodological overlap

**Filters:**
- Year: 2019+
- Min citations: 50
- Prioritize: highly-cited + recent

**Example queries:**
- "automated manuscript generation from code repositories"
- "computational notebook scientific publishing"

**Expected papers:**
- Manubot
- Curvenote
- Quarto
- PaperCoder

### Tier 2: Overlapping Approaches

**Focus:** Recent specialized papers with partial overlap

**Filters:**
- Year: 2022+
- Prioritize: recent + specialized

**Example queries:**
- "Jupyter notebook academic publishing"
- "repository analysis automated documentation"
- "claim verification scientific literature"
- "literate programming research"

**Expected papers:**
- Jupyter Book
- CliVER (claim verification)
- Code-to-docs tools

### Tier 3: Related Infrastructure

**Focus:** Foundational infrastructure and principles

**Filters:**
- Year: 2020+
- Min citations: 100
- Prioritize: foundational

**Example queries:**
- "provenance tracking research data"
- "FAIR principles software research"
- "reproducibility computational science"
- "software citation academic research"

**Expected papers:**
- FAIR4RS Principles
- Software Citation Principles
- Provenance frameworks

## Prioritization Logic

### Priority Score Calculation

```python
score = 0

# Citation count (normalized)
if citations > 100: score += 3
elif citations > 50: score += 2
elif citations > 10: score += 1

# Recency (within 2 years)
if year >= current_year - 2: score += 2

# Semantic overlap (TF-IDF)
if similarity >= 0.80: score += 3
elif similarity >= 0.70: score += 2

# Citation type relevance
if type in ['method', 'tool', 'benchmark']: score += 2
elif type in ['review', 'seminal']: score += 1
```

### Priority Classification

- **Critical** (score ≥ 7): Must-cite before submission
- **Important** (score ≥ 4): Should-cite to strengthen manuscript
- **Optional** (score < 4): Consider for specific contexts

## Citation Type Inference

Automatic categorization based on title/abstract keywords:

| Type | Keywords | Section Recommendation |
|------|----------|------------------------|
| **tool** | software, tool, pipeline, package, algorithm | Methods |
| **review** | review, survey, overview, perspectives | Introduction/Discussion |
| **method** | protocol, method, procedure, workflow | Methods |
| **benchmark** | benchmark, comparison, evaluation | Results/Discussion |
| **dataset** | database, dataset, repository, collection | Methods |
| **recent** | Published within 3 years | Introduction/Discussion |
| **seminal** | >10 years old + >500 citations | Introduction |

## Troubleshooting

### Error: "Credentials file not found"

**Solution:**
1. Download `credentials.json` from Google Cloud Console
2. Place in project root or specify path with `--credentials`

### Error: "Permission denied for document"

**OAuth2 Solution:**
- Run script - browser auth flow will open
- Sign in with account that has access to document

**Service Account Solution:**
- Share Google Doc with service account email (`xyz@project.iam.gserviceaccount.com`)
- Grant "Viewer" access

### Warning: "scikit-learn not installed"

**Impact:** Semantic similarity analysis disabled (falls back to exact matching)

**Solution:**
```bash
pip install scikit-learn>=1.0.0
```

### Error: "python-docx not installed"

**Solution:**
```bash
pip install python-docx>=0.8.11
```

### No citations extracted

**Possible causes:**
1. Manuscript uses unsupported citation format
2. Citations are images/screenshots (not text)
3. Citations in footnotes/comments (not main text)

**Solution:**
- Verify citation format in DOCX
- Check `extracted_citations.json` statistics
- Manually add citations to JSON if needed

## Advanced Usage

### Custom Search Queries

Modify search queries in `rrwrite-gdoc-citation-gap-workflow.py`:

```python
tier_queries = {
    1: [
        "your custom query here",
        "another foundational query"
    ],
    2: [
        "specialized query 1",
        "specialized query 2"
    ]
}
```

### Adjust Similarity Threshold

Lower threshold = more gaps detected (may include false positives):

```bash
python scripts/rrwrite-citation-gap-analyzer.py \
    --similarity-threshold 0.60
```

Higher threshold = fewer gaps (may miss relevant papers):

```bash
python scripts/rrwrite-citation-gap-analyzer.py \
    --similarity-threshold 0.80
```

**Recommended:** 0.70 (default) balances precision and recall

### Filter by Citation Type

Extract specific types from JSON report:

```bash
# Extract only method papers
jq '.gaps_by_type.method' citation_gap_report.json

# Extract critical gaps with >100 citations
jq '.gaps_by_priority.critical[] | select(.citations > 100)' citation_gap_report.json
```

## Integration with RRWrite Workflow

### Step 1: Generate Manuscript

```bash
/rrwrite --repo /path/to/research-repo
```

### Step 2: Export to Google Docs

(Manual: Copy `manuscript/project_v1/manuscript.md` to Google Docs)

### Step 3: Run Gap Analysis

```bash
python scripts/rrwrite-gdoc-citation-gap-workflow.py \
    --document-id [YOUR_GDOC_ID] \
    --output-dir manuscript/project_v1/citation_gaps
```

### Step 4: Update Literature Database

Based on gap analysis report, add missing citations:

```bash
# Search for specific papers
python scripts/rrwrite-search-literature.py \
    "specific paper title or topic" \
    --max-results 10 \
    --output new_citations.json

# Add to literature_evidence.csv manually
```

### Step 5: Re-run Manuscript Generation

```bash
/rrwrite-draft-section --section introduction
/rrwrite-assemble
```

## Best Practices

### 1. Run Early and Often

- ✅ Run after initial draft
- ✅ Run after major revisions
- ✅ Run before submission
- ❌ Don't wait until final review stage

### 2. Prioritize Critical Gaps First

Focus on papers with:
- High citation count (>100)
- High semantic overlap (>80%)
- Direct methodological relevance

### 3. Verify Relevance Manually

- Read abstracts of critical gaps
- Confirm relevance before adding
- Don't blindly add all suggested citations

### 4. Document Decisions

Track why papers were:
- Added (accepted gap)
- Rejected (not relevant)
- Deferred (post-review)

### 5. Re-run After Updates

After adding citations:
- Re-export Google Doc
- Re-run gap analysis
- Verify gaps addressed

## Performance

**Typical runtime** (end-to-end workflow):

| Component | Time | Notes |
|-----------|------|-------|
| Download DOCX | 5-10 sec | Depends on doc size |
| Extract citations | 2-5 sec | ~100 citations |
| Literature search (3 tiers, 8 queries) | 3-8 min | Cached: 10-30 sec |
| Gap analysis | 10-30 sec | With scikit-learn |
| Report generation | 2-5 sec | 50 gaps |
| **Total** | **5-15 min** | **First run** |
| **Total** | **30-60 sec** | **Cached** |

**Optimization tips:**
- Use `--search-tiers 1` for quick analysis
- 24-hour cache speeds up repeated runs
- Run overnight for comprehensive 3-tier search

## Citation

If you use this tool in your research, please cite:

```bibtex
@software{rrwrite_citation_gap,
  title = {RRWrite Citation Gap Analyzer},
  author = {RRWrite Development Team},
  year = {2024},
  url = {https://github.com/your-repo/rrwrite}
}
```

## Support

**Issues:** https://github.com/your-repo/rrwrite/issues
**Documentation:** `docs/`
**Examples:** `example/citation_gap_analysis/`

## See Also

- `docs/GDOC_API_SETUP.md` - Google API setup guide
- `docs/PAPERPILE_WORKFLOW.md` - Paperpile citation workflow
- `CLAUDE.md` - Complete RRWrite architecture
