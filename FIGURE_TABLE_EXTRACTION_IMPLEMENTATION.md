# Figure/Table Extraction Implementation Summary

**Date:** 2026-03-05
**Status:** Phase 1-3 COMPLETE ✓

## Overview

Successfully implemented a new workflow stage for extracting figures and tables from analyzed repositories and generating supplementary visualizations. The system now prioritizes **actual research outputs** (Priority 1) over **analysis-generated visualizations** (Priority 2).

## What Was Implemented

### Phase 1: Core Infrastructure ✓

#### 1. Extraction Script (`scripts/rrwrite-extract-figures-tables.py`)
- **Lines:** ~500
- **Features:**
  - Scans repository for existing figures (PNG, JPG, PDF, SVG, EPS)
  - Scans repository for data tables (CSV, TSV, XLSX)
  - Filters out thumbnails, icons, build artifacts
  - Enforces size limits (10MB figures, 5MB tables)
  - Copies to `figures/from_repo/` and `tables/from_repo/`
  - Generates supplementary figures via `FigureGenerator`
  - Creates metadata manifests with priority levels
  - Attempts to identify generating scripts
  - Auto-generates README index for repository figures

**Usage:**
```bash
python scripts/rrwrite-extract-figures-tables.py \
    --repo-path /path/to/repo \
    --manuscript-dir manuscript/project_v1 \
    --extract figures,tables \
    --generate figures \
    --verbose
```

#### 2. Manifest Generator (`scripts/rrwrite_manifest_generator.py`)
- **Lines:** ~200
- **Features:**
  - `ManifestGenerator` class for creating/loading manifests
  - `ManifestValidator` class for JSON schema validation
  - Methods to query figures/tables by section
  - Priority-based sorting (repo figures first)
  - CLI utilities for validation and querying

#### 3. JSON Schemas
- **`schemas/figure_manifest_schema.json`**: Validates figure manifests
- **`schemas/table_manifest_schema.json`**: Validates table manifests
- Both use JSON Schema Draft 2020-12

### Phase 2: State Management ✓

#### Modified `scripts/rrwrite_state_manager.py`

**Changes:**
1. Added `figure_table_extraction` stage (after `research`, before `drafting`)
2. Updated `stages_order` list
3. Added `update_figure_table_extraction()` method
4. Progress tracking automatically includes new stage

### Phase 3: Workflow Integration ✓

#### 1. Enhanced Figure Selector
Added `get_figures_from_manifest()` to `scripts/rrwrite_figure_generator.py`

#### 2. Updated Draft Section Skill
Added "Figure discovery and inclusion" section with priority system instructions

#### 3. Updated Assembly Script
Enhanced Pandoc resource paths to search multiple figure directories

#### 4. Updated Workflow Skill
Added Phase 5: Figure/Table Extraction, renumbered subsequent phases

#### 5. Created Extraction Skill
New skill: `.claude/skills/rrwrite-extract-figures-tables/SKILL.md`

## Files Created

1. `scripts/rrwrite-extract-figures-tables.py` (500 lines)
2. `scripts/rrwrite_manifest_generator.py` (200 lines)
3. `schemas/figure_manifest_schema.json`
4. `schemas/table_manifest_schema.json`
5. `.claude/skills/rrwrite-extract-figures-tables/SKILL.md`

## Files Modified

1. `scripts/rrwrite_state_manager.py` (+30 lines)
2. `scripts/rrwrite_figure_generator.py` (+40 lines)
3. `scripts/rrwrite-assemble-manuscript.py` (+15 lines)
4. `.claude/skills/rrwrite-draft-section/SKILL.md` (+60 lines)
5. `.claude/skills/rrwrite-workflow/SKILL.md` (+50 lines)

## Total Impact

- **New files:** 5
- **Modified files:** 5
- **Total lines added:** ~900
- **New workflow stage:** 1
- **Skills created:** 1
- **Skills enhanced:** 2

## Testing Results

### ✅ Phase 4: Testing & Validation (COMPLETE)

**Test 1: Module Import and Basic Functionality**
- ✓ `ManifestGenerator` imports successfully
- ✓ `FigureSelector` enhanced methods work
- ✓ Manifest creation validated

**Test 2: Extraction Script**
- ✓ Scanned rrwrite repository: 959 figures found
- ✓ Created valid JSON manifest
- ✓ Generated README index
- ✓ Applied filtering rules correctly

**Test 3: StateManager Integration**
- ✓ New `figure_table_extraction` stage exists
- ✓ `update_figure_table_extraction()` method works
- ✓ Metadata updated correctly (figures_count)
- ✓ Progress tracking includes new stage

**Test Results:**
```
Extraction test: /tmp/test_extraction_rrwrite/
  - Figures from repository: 959
  - Manifests generated: ✓
  - README index created: ✓
  - State tracking: ✓
```

### ✅ Phase 5: Documentation (COMPLETE)

**Updated Files:**
1. `CLAUDE.md` - Added figure/table extraction to:
   - Workflow stages list
   - Common commands section
   - Step-by-step workflow
   - Python script commands

2. `docs/FIGURE_TABLE_WORKFLOW.md` (NEW - 500+ lines)
   - Complete workflow guide
   - Priority system explanation
   - Usage examples
   - Troubleshooting guide
   - Best practices
   - Advanced queries

**Documentation Coverage:**
- ✓ Architecture overview
- ✓ Priority system (1=repo, 2=generated)
- ✓ Usage instructions (3 methods)
- ✓ Output structure
- ✓ Manifest format
- ✓ Integration with drafting
- ✓ Validation procedures
- ✓ Troubleshooting
- ✓ Best practices

---

**Status:** ✅ IMPLEMENTATION COMPLETE

**All Phases Delivered:**
- ✅ Phase 1: Core Infrastructure
- ✅ Phase 2: State Management
- ✅ Phase 3: Workflow Integration
- ✅ Phase 4: Testing & Validation
- ✅ Phase 5: Documentation

**Ready for:** Production use in RRWrite workflow
