#!/bin/bash
# Run citation gap analysis with complete citation extraction
# Usage: ./scripts/run-gap-analysis.sh

set -e  # Exit on error

echo "Running citation gap analysis with all citations..."

uv run python scripts/rrwrite-citation-gap-analyzer.py \
  --manuscript-citations manuscript/citation_gaps/all_citations.json \
  --search-results \
    manuscript/citation_gaps/tier1_merged.json \
    manuscript/citation_gaps/tier2_merged.json \
    manuscript/citation_gaps/tier3_merged.json \
  --output manuscript/citation_gaps/gap_analysis_complete.json \
  --similarity-threshold 0.70 \
  --verbose

echo ""
echo "Generating gap analysis report..."

uv run python scripts/rrwrite-generate-gap-report.py \
  --gap-analysis manuscript/citation_gaps/gap_analysis_complete.json \
  --output-dir manuscript/citation_gaps \
  --verbose

echo ""
echo "✅ Complete! View report at:"
echo "   manuscript/citation_gaps/citation_gap_report.md"
