#!/bin/bash
# Run gap analysis with TARGETED manuscript-specific search results

set -e

echo "Running TARGETED citation gap analysis..."
echo "(Using queries derived from YOUR manuscript content)"
echo ""

uv run python scripts/rrwrite-citation-gap-analyzer.py \
--manuscript-citations manuscript/citation_gaps/all_citations_complete.json \
--search-results \
manuscript/citation_gaps/tier1_targeted_merged.json \
manuscript/citation_gaps/tier2_targeted_merged.json \
manuscript/citation_gaps/tier3_targeted_merged.json \
--output manuscript/citation_gaps/gap_analysis_targeted.json \
--manuscript-keywords manuscript/citation_gaps/manuscript_keywords_curated.json \
--similarity-threshold 0.70 \
--verbose

echo ""
echo "Generating targeted gap report..."

uv run python scripts/rrwrite-generate-gap-report.py \
--gap-analysis manuscript/citation_gaps/gap_analysis_targeted.json \
--output-dir manuscript/citation_gaps \
--verbose

echo ""
echo "✅ TARGETED analysis complete!"
echo ""
echo "This analysis used queries based on:"
echo "  ✓ Tools YOU actually use (MGnify, SILVA, KBase, etc.)"
echo "  ✓ Methods YOU applied (SHAP, gradient boosting, Mann-Whitney)"
echo "  ✓ Concepts from YOUR manuscript (ecosystem-discriminative features)"
echo ""
echo "Report: manuscript/citation_gaps/citation_gap_report.md"
