# RRWrite Example Manuscript - Version 1

This directory contains a **reference implementation** of a complete manuscript generated using RRWrite on the repo-research-writer repository itself.

## Purpose

This serves as:
- **Documentation**: Demonstrates the complete workflow output
- **Template**: Shows the structure and quality of generated manuscripts
- **Reference**: Example for users learning RRWrite

## Contents

This v1 manuscript includes:
- ✅ `outline.md` - Detailed manuscript structure
- ✅ `abstract.md` - Abstract section
- ✅ `introduction.md` - Introduction section
- ✅ `methods.md` - Methods section
- ✅ `results.md` - Results section
- ✅ `discussion.md` - Discussion section
- ✅ `availability.md` - Data availability statement
- ✅ `literature.md` - Literature review summary
- ✅ `literature_citations.bib` - BibTeX citations (20+ papers)
- ✅ `literature_evidence.csv` - Citation evidence tracker
- ✅ `critique_manuscript_v1.md` - Quality review and recommendations
- ✅ `.rrwrite/state.json` - Workflow state tracking

## Target Journal

**Bioinformatics** (Oxford Academic)
- Total word limit: 6000 words
- Focus: Software utility, performance, reproducibility

## Generation Details

- **Generated**: February 2026
- **Repository**: repo-research-writer (RRWrite itself)
- **Word Count**: ~6000 words (within limits)
- **Citations**: 20+ papers with DOIs
- **Status**: Completed through critique phase

## How This Was Created

This manuscript was generated using the RRWrite workflow:

```bash
# 1. Planning phase
/rrwrite-plan-manuscript --target-dir examples/repo-research-writer_v1

# 2. Literature research
/rrwrite-research-literature --target-dir examples/repo-research-writer_v1

# 3. Drafting sections
/rrwrite-draft-section abstract --target-dir examples/repo-research-writer_v1
/rrwrite-draft-section introduction --target-dir examples/repo-research-writer_v1
/rrwrite-draft-section methods --target-dir examples/repo-research-writer_v1
/rrwrite-draft-section results --target-dir examples/repo-research-writer_v1
/rrwrite-draft-section discussion --target-dir examples/repo-research-writer_v1

# 4. Quality critique
/rrwrite-critique-manuscript --target-dir examples/repo-research-writer_v1
```

## Notes for Users

- This is a **frozen reference** - it won't be updated
- Self-generated manuscripts (running `/rrwrite .`) go to `manuscript/repo-research-writer_vN/`
- The example demonstrates the workflow but isn't necessarily publication-ready
- Review `critique_manuscript_v1.md` to see the quality assessment

## Future Examples

We may add:
- `repo-research-writer_v2/` - Showing revision workflow after addressing critique
- Other journal formats (Nature, PLOS)
- Multi-version comparison examples
