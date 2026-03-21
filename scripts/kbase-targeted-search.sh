#!/bin/bash
# TARGETED literature search based on manuscript keyword extraction
# Uses ACTUAL tools, methods, and terms from the manuscript

set -e

OUTPUT_DIR="manuscript/citation_gaps"
mkdir -p "$OUTPUT_DIR"

echo "################################################"
echo "# TARGETED KBase Literature Search"
echo "# (Based on manuscript keyword extraction)"
echo "################################################"
echo ""

# Tier 1: Core Tools & Databases YOU ACTUALLY USE
echo "=== Tier 1: Tools & Databases (From Your Manuscript) ==="
echo ""

echo "Query 1/6: MGnify metagenome analysis pipeline"
uv run python scripts/rrwrite-search-literature.py \
"MGnify metagenome analysis pipeline" \
--max-results 15 \
--output "$OUTPUT_DIR/tier1_targeted_q1.json"

echo ""
echo "Query 2/6: SILVA 16S rRNA database taxonomy"
uv run python scripts/rrwrite-search-literature.py \
"SILVA 16S rRNA database taxonomy" \
--max-results 15 \
--output "$OUTPUT_DIR/tier1_targeted_q2.json"

echo ""
echo "Query 3/6: Infernal RNA structure alignment"
uv run python scripts/rrwrite-search-literature.py \
"Infernal RNA structure alignment" \
--max-results 10 \
--output "$OUTPUT_DIR/tier1_targeted_q3.json"

echo ""
echo "Query 4/6: KBase ecosystem microbiome analysis"
uv run python scripts/rrwrite-search-literature.py \
"KBase ecosystem microbiome analysis" \
--max-results 10 \
--output "$OUTPUT_DIR/tier1_targeted_q4.json"

echo ""
echo "Query 5/6: GOLD database microbial genomes metadata"
uv run python scripts/rrwrite-search-literature.py \
"GOLD database microbial genomes metadata" \
--max-results 10 \
--output "$OUTPUT_DIR/tier1_targeted_q5.json"

echo ""
echo "Query 6/6: CatBoost gradient boosting microbiome"
uv run python scripts/rrwrite-search-literature.py \
"CatBoost gradient boosting microbiome classification" \
--max-results 10 \
--output "$OUTPUT_DIR/tier1_targeted_q6.json"

# Tier 2: YOUR SPECIFIC METHODS
echo ""
echo "=== Tier 2: Methods YOU Applied ==="
echo ""

echo "Query 1/5: SHAP feature importance microbiome"
uv run python scripts/rrwrite-search-literature.py \
"SHAP feature importance microbiome interpretation" \
--max-results 12 \
--output "$OUTPUT_DIR/tier2_targeted_q1.json"

echo ""
echo "Query 2/5: Ecosystem discriminative features metagenomics"
uv run python scripts/rrwrite-search-literature.py \
"ecosystem discriminative features metagenomics machine learning" \
--max-results 12 \
--output "$OUTPUT_DIR/tier2_targeted_q2.json"

echo ""
echo "Query 3/5: Characteristic features ecosystem classification"
uv run python scripts/rrwrite-search-literature.py \
"characteristic features ecosystem classification metagenome" \
--max-results 12 \
--output "$OUTPUT_DIR/tier2_targeted_q3.json"

echo ""
echo "Query 4/5: Mann-Whitney feature selection metagenome"
uv run python scripts/rrwrite-search-literature.py \
"Mann-Whitney test feature selection metagenome" \
--max-results 10 \
--output "$OUTPUT_DIR/tier2_targeted_q4.json"

echo ""
echo "Query 5/5: Permutation importance gradient boosting ecology"
uv run python scripts/rrwrite-search-literature.py \
"permutation importance gradient boosting microbial ecology" \
--max-results 10 \
--output "$OUTPUT_DIR/tier2_targeted_q5.json"

# Tier 3: Domain-Specific Methods
echo ""
echo "=== Tier 3: Domain-Specific Approaches ==="
echo ""

echo "Query 1/4: Metagenomic functional annotation pipelines"
uv run python scripts/rrwrite-search-literature.py \
"metagenomic functional annotation InterPro Pfam" \
--max-results 10 \
--output "$OUTPUT_DIR/tier3_targeted_q1.json"

echo ""
echo "Query 2/4: Taxonomic profiling metagenomes comparison"
uv run python scripts/rrwrite-search-literature.py \
"taxonomic profiling metagenomes comparison methods" \
--max-results 10 \
--output "$OUTPUT_DIR/tier3_targeted_q2.json"

echo ""
echo "Query 3/4: Microbial community ecosystem type classification"
uv run python scripts/rrwrite-search-literature.py \
"microbial community ecosystem type classification" \
--max-results 10 \
--output "$OUTPUT_DIR/tier3_targeted_q3.json"

echo ""
echo "Query 4/4: Metagenome sample metadata standards"
uv run python scripts/rrwrite-search-literature.py \
"metagenome sample metadata GOLD ecosystem classification" \
--max-results 8 \
--output "$OUTPUT_DIR/tier3_targeted_q4.json"

echo ""
echo "=== Merging Results ==="
echo ""

# Merge tier files
python3 -c "
import json
from pathlib import Path

def merge_tier(tier_num, query_count):
    all_papers = []
    seen_dois = set()

    for i in range(1, query_count + 1):
        file_path = Path('$OUTPUT_DIR/tier{tier_num}_targeted_q{i}.json'.format(tier_num=tier_num, i=i))
        if not file_path.exists():
            continue

        with open(file_path) as f:
            data = json.load(f)

        for paper in data.get('papers', []):
            doi = paper.get('doi', '').lower()
            if doi and doi not in seen_dois:
                all_papers.append(paper)
                seen_dois.add(doi)
            elif not doi:
                title = paper.get('title', '').lower()
                if title not in [p.get('title', '').lower() for p in all_papers]:
                    all_papers.append(paper)

    output_file = Path('$OUTPUT_DIR/tier{tier_num}_targeted_merged.json'.format(tier_num=tier_num))
    with open(output_file, 'w') as f:
        json.dump({'papers': all_papers, 'total': len(all_papers)}, f, indent=2)

    print(f'Tier {tier_num}: {len(all_papers)} unique papers → {output_file}')
    return len(all_papers)

tier1_count = merge_tier(1, 6)
tier2_count = merge_tier(2, 5)
tier3_count = merge_tier(3, 4)

print(f'\\nTotal papers: {tier1_count + tier2_count + tier3_count}')
"

echo ""
echo "################################################"
echo "# TARGETED Search Complete!"
echo "################################################"
echo ""
echo "Queries were based on YOUR manuscript content:"
echo "  - Tools: MGnify, SILVA, Infernal, KBase, GOLD, CatBoost"
echo "  - Methods: SHAP, gradient boosting, Mann-Whitney, permutation"
echo "  - Concepts: ecosystem-discriminative features, characteristic features"
echo ""
echo "Next: Run gap analysis"
echo "  ./scripts/run-gap-analysis-targeted.sh"
echo ""
