#!/bin/bash
# Custom literature search for KBase Ecosystem Classification manuscript
# Searches for domain-relevant papers in microbial ecology, metagenomics, and ML

set -e

OUTPUT_DIR="manuscript/citation_gaps"
mkdir -p "$OUTPUT_DIR"

echo "################################################"
echo "# KBase Ecosystem Classification Literature Search"
echo "################################################"
echo ""

# Tier 1: Core Domain (Microbial Ecosystem Classification)
echo "=== Tier 1: Core Domain (Ecosystem Classification) ==="
echo ""

echo "Query 1/4: Microbial ecosystem classification machine learning"
uv run python scripts/rrwrite-search-literature.py \
  "microbial ecosystem classification machine learning" \
  --max-results 20 \
  --output "$OUTPUT_DIR/tier1_custom_query1.json"

echo ""
echo "Query 2/4: Metagenome feature importance analysis"
uv run python scripts/rrwrite-search-literature.py \
  "metagenome feature importance analysis" \
  --max-results 20 \
  --output "$OUTPUT_DIR/tier1_custom_query2.json"

echo ""
echo "Query 3/4: 16S rRNA taxonomic classification"
uv run python scripts/rrwrite-search-literature.py \
  "16S rRNA taxonomic classification database" \
  --max-results 20 \
  --output "$OUTPUT_DIR/tier1_custom_query3.json"

echo ""
echo "Query 4/4: Microbiome machine learning interpretability"
uv run python scripts/rrwrite-search-literature.py \
  "microbiome machine learning interpretability SHAP" \
  --max-results 20 \
  --output "$OUTPUT_DIR/tier1_custom_query4.json"

# Tier 2: Methods & Tools
echo ""
echo "=== Tier 2: Methods & Tools ==="
echo ""

echo "Query 1/5: KBase metagenome analysis"
uv run python scripts/rrwrite-search-literature.py \
  "KBase metagenome analysis workflow" \
  --max-results 15 \
  --output "$OUTPUT_DIR/tier2_custom_query1.json"

echo ""
echo "Query 2/5: CatBoost gradient boosting microbiome"
uv run python scripts/rrwrite-search-literature.py \
  "CatBoost gradient boosting microbiome classification" \
  --max-results 15 \
  --output "$OUTPUT_DIR/tier2_custom_query2.json"

echo ""
echo "Query 3/5: SHAP feature importance biological data"
uv run python scripts/rrwrite-search-literature.py \
  "SHAP feature importance biological data interpretation" \
  --max-results 15 \
  --output "$OUTPUT_DIR/tier2_custom_query3.json"

echo ""
echo "Query 4/5: Metagenomic taxonomic profiling tools"
uv run python scripts/rrwrite-search-literature.py \
  "metagenomic taxonomic profiling tools comparison" \
  --max-results 15 \
  --output "$OUTPUT_DIR/tier2_custom_query4.json"

echo ""
echo "Query 5/5: Environmental microbiome characterization"
uv run python scripts/rrwrite-search-literature.py \
  "environmental microbiome characterization sequencing" \
  --max-results 15 \
  --output "$OUTPUT_DIR/tier2_custom_query5.json"

# Tier 3: Related Infrastructure & Databases
echo ""
echo "=== Tier 3: Infrastructure & Databases ==="
echo ""

echo "Query 1/4: SILVA ribosomal RNA database"
uv run python scripts/rrwrite-search-literature.py \
  "SILVA ribosomal RNA database taxonomy" \
  --max-results 10 \
  --output "$OUTPUT_DIR/tier3_custom_query1.json"

echo ""
echo "Query 2/4: Rfam RNA families database"
uv run python scripts/rrwrite-search-literature.py \
  "Rfam RNA families database" \
  --max-results 10 \
  --output "$OUTPUT_DIR/tier3_custom_query2.json"

echo ""
echo "Query 3/4: IMG/M integrated microbial genomes"
uv run python scripts/rrwrite-search-literature.py \
  "IMG/M integrated microbial genomes metagenomes database" \
  --max-results 10 \
  --output "$OUTPUT_DIR/tier3_custom_query3.json"

echo ""
echo "Query 4/4: Metagenome metadata standards"
uv run python scripts/rrwrite-search-literature.py \
  "metagenome metadata standards MIxS GSC" \
  --max-results 10 \
  --output "$OUTPUT_DIR/tier3_custom_query4.json"

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
        file_path = Path('$OUTPUT_DIR/tier{tier_num}_custom_query{i}.json'.format(tier_num=tier_num, i=i))
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
                # No DOI - check title
                title = paper.get('title', '').lower()
                if title not in [p.get('title', '').lower() for p in all_papers]:
                    all_papers.append(paper)

    output_file = Path('$OUTPUT_DIR/tier{tier_num}_custom_merged.json'.format(tier_num=tier_num))
    with open(output_file, 'w') as f:
        json.dump({'papers': all_papers, 'total': len(all_papers)}, f, indent=2)

    print(f'Tier {tier_num}: {len(all_papers)} unique papers → {output_file}')
    return len(all_papers)

tier1_count = merge_tier(1, 4)
tier2_count = merge_tier(2, 5)
tier3_count = merge_tier(3, 4)

print(f'\\nTotal papers: {tier1_count + tier2_count + tier3_count}')
"

echo ""
echo "################################################"
echo "# Literature Search Complete!"
echo "################################################"
echo ""
echo "Next steps:"
echo "  1. Run gap analysis: ./scripts/run-gap-analysis-custom.sh"
echo "  2. View report: manuscript/citation_gaps/citation_gap_report.md"
echo ""
