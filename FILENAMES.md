# RRWrite File Naming Conventions

All RRWrite files use `rrwrite-` prefix or `PROJECT` name to avoid conflicts.

## Core Files

- **`PROJECT.md`** - Project context (replaces PROJECT.md)
- **`rrwrite-drafts/`** - Generated sections directory (deprecated, use `manuscript/` instead)
- **`manuscript/`** - All manuscript outputs (schema-validated)
- **`scripts/rrwrite-*.py`** - Verification tools

## Generated Files (Legacy - deprecated)

- `rrwrite-manuscript-plan.md`
- `rrwrite-literature-review.md`
- `rrwrite-literature-evidence.csv`
- `rrwrite-bib-additions.bib`
- `rrwrite-critique-*.md`

## New Schema-Based Structure

All new manuscript outputs go in `manuscript/` directory:
- `manuscript/outline.md`
- `manuscript/literature.md`
- `manuscript/literature_citations.bib`
- `manuscript/literature_evidence.csv`
- `manuscript/abstract.md`, `manuscript/introduction.md`, etc.
- `manuscript/critique_TYPE_vN.md`

## Why?

**Prevents conflicts** with existing project files like PROJECT.md, drafts/, README.md

**Clear ownership:** `ls rrwrite-*` shows all RRWrite files

**Safe removal:** `rm -rf rrwrite-*` won't touch your research files

**Schema validation:** `manuscript/` directory follows LinkML schema for consistency
