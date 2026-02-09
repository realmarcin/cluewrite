# RRWrite Example Manuscripts

This directory contains reference example manuscripts demonstrating RRWrite's capabilities.

## Available Examples

### repo_research_writer_v2

A complete self-referential manuscript documenting the RRWrite tool itself.

**Contents:**
- `abstract.md`, `introduction.md`, `methods.md`, `results.md`, `discussion.md`, `availability.md`
- `literature.md` - One-page literature review
- `literature_citations.bib` - BibTeX bibliography
- `literature_evidence.csv` - Citation database
- `outline.md` - Manuscript outline
- `critique_manuscript_v1.md` - Adversarial critique report
- `.rrwrite/state.json` - Workflow state

**Use this example to:**
- See complete RRWrite output format
- Understand section structure and content
- Learn citation and evidence tracking
- Reference when drafting your own manuscripts

## Generating Additional Examples

To create another example manuscript:

```bash
# From the rrwrite directory
/rrwrite --repo /path/to/another-repo --output-dir example/example_name_v1
```

## Purpose

Examples in this directory:
- **Are tracked in git** (part of the tool repository)
- Serve as reference implementations
- Demonstrate RRWrite's output format
- Help new users understand the workflow

## User Manuscripts

User-generated manuscripts should go in `manuscript/` directory (gitignored) where each will have its own separate git repository.

See [Git Architecture](../docs/GIT_ARCHITECTURE.md) for details on the separation between tool and manuscript repositories.
