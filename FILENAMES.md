# ClueWrite File Naming Conventions

All ClueWrite files use `cluewrite-` prefix or `CLUEWRITE` name to avoid conflicts.

## Core Files

- **`CLUEWRITE.md`** - Project context (replaces PROJECT.md)
- **`cluewrite-drafts/`** - Generated sections directory
- **`scripts/cluewrite-*.py`** - Verification tools

## Generated Files

- `cluewrite-manuscript-plan.md`
- `cluewrite-literature-review.md`
- `cluewrite-literature-evidence.csv`
- `cluewrite-bib-additions.bib`
- `cluewrite-review-*.md`

## Why?

**Prevents conflicts** with existing project files like PROJECT.md, drafts/, README.md

**Clear ownership:** `ls cluewrite-*` shows all ClueWrite files

**Safe removal:** `rm -rf cluewrite-*` won't touch your research files
