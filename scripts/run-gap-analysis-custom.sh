#!/bin/bash
# Run citation gap analysis with custom KBase-relevant literature search results
# Usage: ./scripts/run-gap-analysis-custom.sh

set -e

echo "Running citation gap analysis with domain-specific literature..."

uv run python scripts/rrwrite-citation-gap-analyzer.py \
  --manuscript-citations manuscript/citation_gaps/all_citations.json \
  --search-results \
    manuscript/citation_gaps/tier1_custom_merged.json \
    manuscript/citation_gaps/tier2_custom_merged.json \
    manuscript/citation_gaps/tier3_custom_merged.json \
  --output manuscript/citation_gaps/gap_analysis_kbase.json \
  --similarity-threshold 0.70 \
  --verbose

echo ""
echo "Generating gap analysis report..."

uv run python scripts/rrwrite-generate-gap-report.py \
  --gap-analysis manuscript/citation_gaps/gap_analysis_kbase.json \
  --output-dir manuscript/citation_gaps \
  --verbose

echo ""
echo "✅ Complete! View domain-specific report at:"
echo "   manuscript/citation_gaps/citation_gap_report.md"
echo ""
echo "This report is based on:"
echo "  - 27 citations from your manuscript"
echo "  - Literature search in microbial ecology, metagenomics, and ML"
echo "  - Domain-specific queries (ecosystem classification, SHAP, KBase, etc.)"
