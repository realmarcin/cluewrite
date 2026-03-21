# Citation Gap Analysis Workflow Diagram

## High-Level Overview

```
┌─────────────────────┐
│   Google Docs       │
│   Manuscript        │
│  (Your Document)    │
└──────────┬──────────┘
           │
           │ Document ID
           ▼
┌─────────────────────┐
│  Phase 1: Download  │
│  (rrwrite-download- │
│   gdoc.py)          │
└──────────┬──────────┘
           │
           │ manuscript.docx
           ▼
┌─────────────────────┐
│ Phase 2: Extract    │
│ Citations           │
│ (rrwrite-extract-   │
│  gdoc-citations.py) │
└──────────┬──────────┘
           │
           │ extracted_citations.json
           │ (42 citations found)
           ▼
┌─────────────────────────────────────────┐
│ Phase 3: Multi-Tier Literature Search   │
├─────────────────────────────────────────┤
│ Tier 1: Direct Method Match             │
│   • automated manuscript generation     │
│   • computational notebook publishing   │
│   → 20 papers (highly-cited)            │
├─────────────────────────────────────────┤
│ Tier 2: Overlapping Approaches          │
│   • Jupyter notebook publishing         │
│   • repository analysis documentation   │
│   • claim verification                  │
│   → 45 papers (recent + specialized)    │
├─────────────────────────────────────────┤
│ Tier 3: Related Infrastructure          │
│   • FAIR principles software            │
│   • provenance tracking                 │
│   → 30 papers (foundational)            │
└──────────┬──────────────────────────────┘
           │
           │ tier1_merged.json (20 papers)
           │ tier2_merged.json (45 papers)
           │ tier3_merged.json (30 papers)
           │ TOTAL: 95 papers
           ▼
┌─────────────────────────────────────────┐
│ Phase 4: Gap Analysis (4 Layers)        │
├─────────────────────────────────────────┤
│ Layer 1: Exact Matching                 │
│   • DOI comparison                      │
│   • Title comparison                    │
│   → 23 gaps found                       │
├─────────────────────────────────────────┤
│ Layer 2: Semantic Overlap (TF-IDF)      │
│   • Abstract vectorization              │
│   • Cosine similarity (>70%)            │
│   → 8 papers with high overlap          │
├─────────────────────────────────────────┤
│ Layer 3: Citation Type Categorization   │
│   • tool, method, review, benchmark     │
│   • Section recommendations             │
│   → 5 tool, 12 method, 6 review         │
├─────────────────────────────────────────┤
│ Layer 4: Citation Network Analysis      │
│   • Priority score (0-10)               │
│   • critical/important/optional         │
│   → 5 critical, 12 important, 6 optional│
└──────────┬──────────────────────────────┘
           │
           │ gap_analysis.json
           │ (23 gaps with priorities)
           ▼
┌─────────────────────────────────────────┐
│ Phase 5: Report Generation              │
├─────────────────────────────────────────┤
│ Markdown Report:                        │
│   • Executive Summary                   │
│   • Current Citation Profile            │
│   • Critical Gaps (Must-Cite)           │
│   • Recommended Additions (Should-Cite) │
│   • Optional Citations                  │
│   • Actionable Recommendations          │
├─────────────────────────────────────────┤
│ JSON Report:                            │
│   • gaps_by_priority                    │
│   • gaps_by_type                        │
│   • all_gaps with metadata              │
└──────────┬──────────────────────────────┘
           │
           │ citation_gap_report.md
           │ citation_gap_report.json
           ▼
┌─────────────────────┐
│  User Review        │
│  & Citation Updates │
└─────────────────────┘
```

## Detailed Workflow: End-to-End

```
START
  │
  ├─► Input: Google Doc ID + Credentials
  │
  ▼
┌────────────────────────────────────────────────────────┐
│ STEP 1: Download Google Doc as DOCX                    │
│ ────────────────────────────────────────────────────── │
│ Script: rrwrite-download-gdoc.py                       │
│ Input:  Document ID, credentials.json                  │
│ Output: manuscript.docx, manuscript.metadata.json      │
│ Time:   5-10 seconds                                   │
└────────────────────────────────────────────────────────┘
  │
  ▼
┌────────────────────────────────────────────────────────┐
│ STEP 2: Extract Citations from DOCX                    │
│ ────────────────────────────────────────────────────── │
│ Script: rrwrite-extract-gdoc-citations.py              │
│ Input:  manuscript.docx                                │
│ Output: extracted_citations.json                       │
│ Formats: Paperpile, bracketed, numbered                │
│ Time:   2-5 seconds                                    │
│ Example Output:                                        │
│   {                                                    │
│     "statistics": {                                    │
│       "total_citations": 42,                           │
│       "by_type": {"paperpile": 40, "bracketed": 2},    │
│       "year_range": {"earliest": "2019", ...}          │
│     }                                                  │
│   }                                                    │
└────────────────────────────────────────────────────────┘
  │
  ▼
┌────────────────────────────────────────────────────────┐
│ STEP 3: Multi-Tier Literature Search                   │
│ ────────────────────────────────────────────────────── │
│ Script: rrwrite-search-literature.py (multiple calls)  │
│                                                        │
│ ┌──────────────────────────────────────────────────┐  │
│ │ Tier 1: Direct Method Match                      │  │
│ │ ─────────────────────────────────────────────    │  │
│ │ Queries (3):                                     │  │
│ │   • "automated manuscript generation..."        │  │
│ │   • "computational notebook publishing"         │  │
│ │   • "research code to documentation"            │  │
│ │ Filters: year≥2019, citations≥50                │  │
│ │ Results: ~20 papers                              │  │
│ │ Time: 1-2 minutes (uncached)                     │  │
│ └──────────────────────────────────────────────────┘  │
│                                                        │
│ ┌──────────────────────────────────────────────────┐  │
│ │ Tier 2: Overlapping Approaches                   │  │
│ │ ─────────────────────────────────────────────    │  │
│ │ Queries (5):                                     │  │
│ │   • "Jupyter notebook academic publishing"      │  │
│ │   • "repository analysis automation"            │  │
│ │   • "claim verification scientific literature"  │  │
│ │   • "Quarto scientific publishing"              │  │
│ │   • "literate programming research"             │  │
│ │ Filters: year≥2022                               │  │
│ │ Results: ~45 papers                              │  │
│ │ Time: 2-4 minutes (uncached)                     │  │
│ └──────────────────────────────────────────────────┘  │
│                                                        │
│ ┌──────────────────────────────────────────────────┐  │
│ │ Tier 3: Related Infrastructure                   │  │
│ │ ─────────────────────────────────────────────    │  │
│ │ Queries (4):                                     │  │
│ │   • "provenance tracking research data"         │  │
│ │   • "FAIR principles software"                  │  │
│ │   • "reproducibility computational science"     │  │
│ │   • "software citation academic research"       │  │
│ │ Filters: year≥2020, citations≥100                │  │
│ │ Results: ~30 papers                              │  │
│ │ Time: 1-2 minutes (uncached)                     │  │
│ └──────────────────────────────────────────────────┘  │
│                                                        │
│ Output: tier1_merged.json, tier2_merged.json,          │
│         tier3_merged.json                              │
│ Total Papers: 95 (deduplicated)                        │
│ Total Time: 3-8 minutes (first run), 10-30s (cached)   │
└────────────────────────────────────────────────────────┘
  │
  ▼
┌────────────────────────────────────────────────────────┐
│ STEP 4: Gap Analysis (4 Layers)                        │
│ ────────────────────────────────────────────────────── │
│ Script: rrwrite-citation-gap-analyzer.py               │
│                                                        │
│ ┌──────────────────────────────────────────────────┐  │
│ │ Layer 1: Exact Matching                          │  │
│ │ ──────────────────────                           │  │
│ │ • Compare DOIs from manuscript vs search         │  │
│ │ • Compare titles (normalized)                    │  │
│ │ • Identify papers NOT in manuscript              │  │
│ │ Result: 23 missing papers found                  │  │
│ └──────────────────────────────────────────────────┘  │
│           │                                            │
│           ▼                                            │
│ ┌──────────────────────────────────────────────────┐  │
│ │ Layer 2: Semantic Overlap Detection              │  │
│ │ ──────────────────────────────                   │  │
│ │ • TF-IDF vectorization (500 features)            │  │
│ │ • Cosine similarity calculation                  │  │
│ │ • Threshold: 70% (configurable)                  │  │
│ │ Result: 8 papers with >70% overlap               │  │
│ └──────────────────────────────────────────────────┘  │
│           │                                            │
│           ▼                                            │
│ ┌──────────────────────────────────────────────────┐  │
│ │ Layer 3: Citation Type Categorization            │  │
│ │ ──────────────────────────────────               │  │
│ │ Inferred from title/abstract keywords:           │  │
│ │   • tool (5 papers)                              │  │
│ │   • method (12 papers)                           │  │
│ │   • review (3 papers)                            │  │
│ │   • benchmark (2 papers)                         │  │
│ │   • recent (1 paper)                             │  │
│ │ + Section recommendations                        │  │
│ └──────────────────────────────────────────────────┘  │
│           │                                            │
│           ▼                                            │
│ ┌──────────────────────────────────────────────────┐  │
│ │ Layer 4: Citation Network Analysis               │  │
│ │ ──────────────────────────────────               │  │
│ │ Priority Score Calculation:                      │  │
│ │   score = 0                                      │  │
│ │   if citations > 100:  score += 3                │  │
│ │   if year >= 2024-2:   score += 2                │  │
│ │   if similarity > 0.8: score += 3                │  │
│ │   if type in [method, tool]: score += 2          │  │
│ │                                                  │  │
│ │ Priority Classification:                         │  │
│ │   • critical (score ≥7): 5 papers ← MUST CITE    │  │
│ │   • important (score ≥4): 12 papers ← SHOULD     │  │
│ │   • optional (score <4): 6 papers ← MAYBE        │  │
│ └──────────────────────────────────────────────────┘  │
│                                                        │
│ Output: gap_analysis.json                              │
│ Time: 10-30 seconds                                    │
└────────────────────────────────────────────────────────┘
  │
  ▼
┌────────────────────────────────────────────────────────┐
│ STEP 5: Report Generation                              │
│ ────────────────────────────────────────────────────── │
│ Script: rrwrite-generate-gap-report.py                 │
│                                                        │
│ Markdown Report Structure:                             │
│ ┌────────────────────────────────────────────────┐    │
│ │ ## Executive Summary                           │    │
│ │ Current: 42 citations                          │    │
│ │ Missing: 23 citations                          │    │
│ │ Critical: 5 (must-cite before submission)      │    │
│ │ Important: 12 (strengthen manuscript)          │    │
│ │ Optional: 6 (emerging work)                    │    │
│ └────────────────────────────────────────────────┘    │
│           │                                            │
│           ▼                                            │
│ ┌────────────────────────────────────────────────┐    │
│ │ ## Section 2: Critical Gaps                    │    │
│ │ ───────────────────────────────────────        │    │
│ │ For each of 5 papers:                          │    │
│ │   • Full metadata (title, authors, DOI)        │    │
│ │   • Why missing (overlap %, citations)         │    │
│ │   • Relevance (abstract excerpt)               │    │
│ │   • Recommended section                        │    │
│ │   • Suggested citation context                 │    │
│ └────────────────────────────────────────────────┘    │
│           │                                            │
│           ▼                                            │
│ ┌────────────────────────────────────────────────┐    │
│ │ ## Section 3: Recommended Additions            │    │
│ │ Grouped by type:                               │    │
│ │   • Method papers (7)                          │    │
│ │   • Tool papers (3)                            │    │
│ │   • Review papers (2)                          │    │
│ └────────────────────────────────────────────────┘    │
│           │                                            │
│           ▼                                            │
│ ┌────────────────────────────────────────────────┐    │
│ │ ## Section 5: Actionable Recommendations       │    │
│ │ ───────────────────────────────────────        │    │
│ │ Immediate Actions (Next Draft):                │    │
│ │   1. Add 5 critical citations (Section 2)      │    │
│ │   2. Consider 12 important citations           │    │
│ │                                                │    │
│ │ Medium Priority (Post-Review):                 │    │
│ │   3. Review remaining important citations      │    │
│ │                                                │    │
│ │ Next Steps:                                    │    │
│ │   • Download PDFs                              │    │
│ │   • Add to literature_citations.bib            │    │
│ │   • Extract evidence to CSV                    │    │
│ │   • Update manuscript                          │    │
│ └────────────────────────────────────────────────┘    │
│                                                        │
│ Output: citation_gap_report.md (human-readable)        │
│         citation_gap_report.json (machine-readable)    │
│ Time: 2-5 seconds                                      │
└────────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────┐
│  User Actions       │
│  ─────────────────  │
│  1. Review report   │
│  2. Add citations   │
│  3. Update manuscript│
│  4. Re-run analysis │
└─────────────────────┘
  │
  ▼
 END
```

## Priority Score Calculation Details

```
Input: Paper metadata
  │
  ├─► Citation Count
  │   ├─► >100 citations: +3 points
  │   ├─► >50 citations:  +2 points
  │   └─► >10 citations:  +1 point
  │
  ├─► Recency
  │   └─► Published within 2 years: +2 points
  │
  ├─► Semantic Overlap (TF-IDF)
  │   ├─► Similarity ≥80%: +3 points
  │   └─► Similarity ≥70%: +2 points
  │
  └─► Citation Type Relevance
      ├─► method, tool, benchmark: +2 points
      └─► review, seminal: +1 point
  │
  ▼
Total Score (0-10)
  │
  ├─► Score ≥7: CRITICAL (must-cite)
  ├─► Score ≥4: IMPORTANT (should-cite)
  └─► Score <4: OPTIONAL (nice-to-have)
```

## Data Flow Summary

```
Google Doc
    │
    │ Document ID
    ▼
manuscript.docx (5-10 KB)
    │
    │ DOCX parsing
    ▼
extracted_citations.json (2-5 KB)
    │                               ┌─────────────────────┐
    │                               │ Literature Search   │
    │                               │ (Semantic Scholar + │
    │                               │  PubMed APIs)       │
    │                               └──────┬──────────────┘
    │                                      │
    │                                      │ 3 tiers × queries
    │                                      ▼
    │                               tier*_merged.json (50-100 KB)
    │                                      │
    │                                      │ 95 papers
    │                                      │
    ├──────────────────────────────────────┘
    │ 42 citations
    │
    ▼
gap_analysis.json (20-40 KB)
    │ 23 gaps with priorities
    │
    ▼
citation_gap_report.md (15-30 KB)
citation_gap_report.json (10-20 KB)
    │
    ▼
User reads report → Updates manuscript → Re-run analysis
```

## Performance Metrics

```
┌────────────────────────────────────────────────────────┐
│ Component                 │ Time      │ Cache Impact  │
├────────────────────────────────────────────────────────┤
│ Download DOCX             │ 5-10 sec  │ N/A           │
│ Extract citations         │ 2-5 sec   │ N/A           │
│ Literature search (T1)    │ 1-2 min   │ 10-30 sec     │
│ Literature search (T2)    │ 2-4 min   │ 10-30 sec     │
│ Literature search (T3)    │ 1-2 min   │ 5-15 sec      │
│ Gap analysis              │ 10-30 sec │ N/A           │
│ Report generation         │ 2-5 sec   │ N/A           │
├────────────────────────────────────────────────────────┤
│ TOTAL (first run)         │ 5-15 min  │ -             │
│ TOTAL (cached)            │ 30-60 sec │ 95% faster    │
└────────────────────────────────────────────────────────┘

Cache Details:
• Type: SQLite (24-hour expiry)
• Location: manuscript/.cache/
• Deduplication rate: 90%+
• API call reduction: 95%+
```

## Error Handling Flow

```
START
  │
  ├─► Check credentials.json exists
  │   └─► NO → Error: "Credentials file not found"
  │
  ├─► Authenticate with Google API
  │   ├─► OAuth2: Browser flow
  │   └─► Service Account: Direct auth
  │   └─► FAIL → Error: "Authentication failed"
  │
  ├─► Download Google Doc
  │   └─► FAIL → Error: "Permission denied for document"
  │
  ├─► Extract citations
  │   └─► NO CITATIONS → Warning: "No citations found"
  │
  ├─► Literature search
  │   └─► API ERROR → Continue with partial results
  │
  ├─► Gap analysis
  │   ├─► scikit-learn missing → Fallback to keyword matching
  │   └─► NO GAPS → Report: "Citation coverage adequate"
  │
  └─► Generate report
      └─► Success → citation_gap_report.md
```

## Integration Points

```
┌─────────────────────────────────────────────────────────┐
│ RRWrite Manuscript Generation Workflow                  │
└─────────────────────────────────────────────────────────┘
           │
           ▼
    /rrwrite --repo /path/to/repo
           │
           ▼
    manuscript/project_v1/manuscript.md
           │
           │ (Manual: Copy to Google Docs)
           ▼
    Google Docs (collaborative editing)
           │
           │ Document ID
           ▼
┌─────────────────────────────────────────────────────────┐
│ Citation Gap Analysis (THIS TOOL)                       │
└─────────────────────────────────────────────────────────┘
           │
           ▼
    citation_gap_report.md
           │ Recommendations
           ▼
    Update literature_evidence.csv
           │
           ▼
    /rrwrite-draft-section --section introduction
           │
           ▼
    Updated manuscript with new citations
```

---

**Visual Guides:**
- See `CITATION_GAP_QUICK_START.md` for 5-minute setup
- See `docs/CITATION_GAP_ANALYSIS.md` for comprehensive docs
