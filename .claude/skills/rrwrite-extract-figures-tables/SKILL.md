---
name: rrwrite-extract-figures-tables
description: Extract figures and tables from analyzed repository and generate supplementary visualizations
allowed_tools:
  - Read
  - Write
  - Bash
  - Glob
  - Grep
fork_mode: fork
---

# RRWrite: Figure and Table Extraction

Extract existing figures/tables from the analyzed repository and generate supplementary analysis visualizations. Creates manifests with priority metadata.

## Overview

This skill performs two extraction tasks:

1. **Repository Extraction** (Priority 1): Copy existing figures/tables from the analyzed code repository
2. **Supplementary Generation** (Priority 2): Generate analysis visualizations from repository data

## Prerequisites

Before running this skill, ensure:
- ✓ Repository analysis completed (`/rrwrite-analyze-repository`)
- ✓ `data_tables/` directory exists with analysis outputs
- ✓ Repository path is known

## Inputs

**Required arguments:**
- `--target_dir`: Manuscript output directory (e.g., `manuscript/project_v1`)
- `--repo_path`: Path to analyzed repository

**Optional arguments:**
- `--extract`: What to extract: `figures`, `tables`, or `figures,tables` (default: both)
- `--generate`: What to generate: `figures`, `tables`, or `figures,tables` (default: both)

## Execution

```bash
# Run extraction
python scripts/rrwrite-extract-figures-tables.py \
    --repo-path {repo_path} \
    --manuscript-dir {target_dir} \
    --extract figures,tables \
    --generate figures \
    --verbose
```

## Output Structure

Creates the following directory structure:

```
{target_dir}/
├── figures/
│   ├── from_repo/              # Priority 1: Original repository figures
│   │   ├── workflow_diagram.pdf
│   │   ├── results_plot.png
│   │   └── README.md           # Auto-generated index
│   ├── generated/              # Priority 2: Analysis visualizations
│   │   ├── repository_composition.png
│   │   ├── repository_composition.pdf
│   │   ├── file_size_distribution.png
│   │   └── research_topics.png
│   └── figure_manifest.json    # Metadata with priorities
├── tables/
│   ├── from_repo/              # Priority 1: Original data tables
│   │   ├── experimental_data.csv
│   │   └── benchmark_results.tsv
│   ├── generated/              # Priority 2: Analysis tables
│   │   ├── repository_statistics.tsv
│   │   └── file_inventory.tsv
│   └── table_manifest.json
```

## Manifest Format

### Figure Manifest (`figures/figure_manifest.json`)

```json
{
  "version": "1.0",
  "created_at": "2025-01-15T10:30:00",
  "total_figures": 8,
  "figures_from_repo": 5,
  "figures_generated": 3,
  "figures": [
    {
      "id": "fig_repo_001",
      "path": "figures/from_repo/workflow_diagram.pdf",
      "source": "from_repo",
      "priority": 1,
      "original_path": "docs/figures/workflow.pdf",
      "recommended_sections": ["methods", "introduction"],
      "default_caption": "Workflow diagram showing analysis pipeline",
      "generating_script": "scripts/create_workflow.py"
    },
    {
      "id": "fig_gen_001",
      "path": "figures/generated/repository_composition.png",
      "source": "generated",
      "priority": 2,
      "recommended_sections": ["methods", "results"],
      "default_caption": "Repository composition by file category"
    }
  ]
}
```

## State Tracking

Updates StateManager with extraction results:

```python
from pathlib import Path
import sys
sys.path.insert(0, 'scripts')
from rrwrite_state_manager import StateManager

state = StateManager(output_dir="{target_dir}")

# Mark stage as in-progress
state.update_stage("figure_table_extraction", "in_progress")

# After extraction, mark as completed
state.update_figure_table_extraction(
    figures_from_repo=5,
    figures_generated=3,
    tables_from_repo=2,
    tables_generated=4,
    figure_manifest_path="figures/figure_manifest.json",
    table_manifest_path="tables/table_manifest.json",
    scripts_parsed=12
)
```

## Validation

After extraction, validate manifests:

```bash
# Validate against schema
python scripts/rrwrite_manifest_generator.py \
    --manuscript-dir {target_dir} \
    --validate \
    --schemas-dir schemas
```

## Using Extracted Figures in Sections

When drafting sections, query manifests for available figures:

```python
from pathlib import Path
from rrwrite_manifest_generator import ManifestGenerator

generator = ManifestGenerator(Path("{target_dir}"))

# Get figures for specific section (prioritizes repo figures)
results_figures = generator.get_figures_for_section("results")

for fig in results_figures:
    print(f"Priority {fig['priority']}: {fig['path']}")
    print(f"Caption: {fig['default_caption']}")
```

## Exclusion Rules

The extractor **automatically excludes**:
- Thumbnails and icons (patterns: `*thumb*`, `*icon*`, `*logo*`, `*badge*`)
- Build artifacts (`build/`, `dist/`, `node_modules/`, `__pycache__/`)
- Version control (`.git/`, `.ipynb_checkpoints/`)
- Oversized files (>10MB for figures, >5MB for tables)

## Troubleshooting

### No figures/tables found

**Cause**: Repository may not contain figure files or extraction patterns don't match

**Solution**: Check repository for figure files manually:
```bash
find {repo_path} -name "*.png" -o -name "*.pdf" -o -name "*.svg"
```

### Missing generated figures

**Cause**: Repository analysis didn't create `data_tables/` directory

**Solution**: Re-run repository analysis:
```bash
/rrwrite-analyze-repository --repo_path {repo_path} --output_dir {target_dir}
```

### Manifest validation fails

**Cause**: Schema files missing or malformed manifest

**Solution**: Check schemas exist in `schemas/` directory:
```bash
ls schemas/figure_manifest_schema.json
ls schemas/table_manifest_schema.json
```

## Integration with Workflow

This stage runs **after research** and **before drafting**:

1. Repository Analysis → generates `data_tables/`
2. Planning → creates outline
3. Assessment → selects journal
4. Literature Research → finds citations
5. **Figure/Table Extraction** ← THIS STAGE
6. Section Drafting → uses manifests to include figures/tables
7. Assembly → embeds all figures/tables in final manuscript
8. Critique

## Next Steps

After successful extraction:
1. Review `figures/from_repo/README.md` to verify detected figures
2. Check manifest files for correct priority assignments
3. Proceed to section drafting: `/rrwrite-draft-section --section introduction`

## Expected Duration

- Small repositories (<50 figures): 30-60 seconds
- Medium repositories (50-200 figures): 1-2 minutes
- Large repositories (>200 figures): 2-4 minutes

## Success Criteria

✓ Figures extracted and copied to `figures/from_repo/`
✓ Generated figures created in `figures/generated/`
✓ Tables extracted to `tables/from_repo/`
✓ Manifests created with valid JSON schema
✓ StateManager updated with extraction counts
✓ Priority metadata correctly assigned (1=repo, 2=generated)
