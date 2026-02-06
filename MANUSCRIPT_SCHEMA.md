# Manuscript Schema and Conventions

This document explains the LinkML schema (`schemas/manuscript.yaml`) and file naming conventions used by Repo Research Writer (RRWrite).

## Overview

All manuscript-related outputs are stored in the `manuscript/` directory with standardized names and structures validated against a LinkML schema.

## Directory Structure

```
your-project/
├── PROJECT.md              # Project context
├── manuscript/               # All manuscript outputs
│   ├── outline.md           # Manuscript outline/plan
│   ├── literature.md        # Literature review
│   ├── literature_citations.bib  # BibTeX citations
│   ├── literature_evidence.csv   # Evidence quotes
│   ├── abstract.md          # Abstract section
│   ├── introduction.md      # Introduction section
│   ├── methods.md           # Methods section
│   ├── results.md           # Results section
│   ├── discussion.md        # Discussion section
│   ├── conclusion.md        # Conclusion section (optional)
│   ├── full_manuscript.md   # Assembled manuscript
│   ├── critique_outline_v1.md      # Outline critique
│   ├── critique_literature_v1.md   # Literature critique
│   ├── critique_manuscript_v1.md   # Manuscript critique
│   └── critique_manuscript_v2.md   # Subsequent critique
├── schemas/
│   └── manuscript.yaml      # LinkML schema definition
├── scripts/
│   └── rrwrite-validate-manuscript.py  # Validator
└── data/                    # Your research data
```

## File Naming Conventions

### Outline
- **Filename:** `manuscript/outline.md`
- **Purpose:** Detailed manuscript plan mapping repository to sections
- **Required sections:**
  - Target Journal
  - Section descriptions
  - Evidence file mappings
  - Word count targets

### Literature Research
- **Filename:** `manuscript/literature.md`
- **Purpose:** Comprehensive literature review with citations
- **Required sections:**
  - Background & Foundations
  - Related Work
  - Recent Advances
  - Research Gaps
- **Accompanying files:**
  - `manuscript/literature_citations.bib` - BibTeX entries
  - `manuscript/literature_evidence.csv` - Evidence quotes with DOIs

### Manuscript Sections
- **Filenames:** `manuscript/SECTIONNAME.md`
  - `abstract.md` - Abstract/Summary
  - `introduction.md` - Introduction/Background
  - `methods.md` - Methods/Materials and Methods
  - `results.md` - Results
  - `discussion.md` - Discussion
  - `conclusion.md` - Conclusion (optional)

### Full Manuscript
- **Filename:** `manuscript/full_manuscript.md`
- **Purpose:** Complete assembled manuscript ready for critique/submission
- **Contents:** All sections combined in order

### Critiques
- **Filename pattern:** `manuscript/critique_TYPE_vN.md`
  - `TYPE`: one of `outline`, `literature`, `section`, `manuscript`
  - `N`: version number (1, 2, 3, ...)
- **Examples:**
  - `critique_outline_v1.md`
  - `critique_manuscript_v1.md`
  - `critique_manuscript_v2.md` (after revisions)

## Schema Validation

All manuscript files are validated against the LinkML schema to ensure:
- Correct filenames
- Required sections present
- Proper structure
- Word count targets met
- Citations included

### Running Validation

```bash
# Validate outline
python scripts/rrwrite-validate-manuscript.py \
  --file manuscript/outline.md \
  --type outline

# Validate literature review
python scripts/rrwrite-validate-manuscript.py \
  --file manuscript/literature.md \
  --type literature

# Validate section
python scripts/rrwrite-validate-manuscript.py \
  --file manuscript/methods.md \
  --type section

# Validate full manuscript
python scripts/rrwrite-validate-manuscript.py \
  --file manuscript/full_manuscript.md \
  --type manuscript

# Validate critique
python scripts/rrwrite-validate-manuscript.py \
  --file manuscript/critique_manuscript_v1.md \
  --type critique
```

## Schema Classes

### ManuscriptOutline
Defines the structure of `outline.md`:
- Target journal (Nature Methods, PLOS, Bioinformatics, etc.)
- Sections with word count targets
- Evidence file mappings
- Key points to cover

### LiteratureResearch
Defines the structure of `literature.md`:
- Minimum 5 papers, maximum 50
- Required sections (Background, Related Work, Recent Advances, Gaps)
- Citation and evidence files
- DOI tracking

### ManuscriptSection
Defines individual section files:
- Valid section names (abstract, introduction, methods, results, discussion, conclusion)
- Word count minimums
- Citations and figure references
- Data files used for verification

### FullManuscript
Defines `full_manuscript.md`:
- Minimum 1000 words
- All required sections included
- Target journal specified
- Ready-for-critique status

### Critique
Defines critique report structure:
- Correct filename pattern
- Critique type (outline, literature, section, manuscript)
- Version number
- Required sections (Summary, Strengths, Issues, Recommendation)
- Recommendation type (Accept Minor, Major Revisions, Reject)

## Workflow Integration

The skills automatically use these conventions:

1. **`/rrwrite-plan-manuscript`**
   - Creates `manuscript/outline.md`
   - Validates against schema

2. **`/rrwrite-research-literature`**
   - Creates `manuscript/literature.md`
   - Creates `manuscript/literature_citations.bib`
   - Creates `manuscript/literature_evidence.csv`
   - Validates against schema

3. **`/rrwrite-draft-section`**
   - Creates `manuscript/SECTIONNAME.md`
   - Validates against schema

4. **`/rrwrite-critique-manuscript`**
   - Creates `manuscript/critique_TYPE_vN.md`
   - Validates against schema

## Benefits

1. **Consistency:** All projects use the same structure
2. **Validation:** Automatic checking of outputs
3. **Traceability:** Clear naming makes it easy to track versions
4. **Automation:** Scripts can reliably find and process files
5. **Collaboration:** Team members know where to find what

## Example Evidence CSV

The `literature_evidence.csv` file format:

```csv
doi,citation_key,evidence
10.1038/s41586-021-03819-2,jumper2021,"We developed AlphaFold, which predicts protein structures with atomic accuracy."
10.1126/science.abj8754,baek2021,"RoseTTAFold generates accurate models using only a protein sequence."
```

## Supported Journals

The schema recognizes these journal types:
- `NATURE_METHODS` - Nature Methods
- `PLOS_COMP_BIO` - PLOS Computational Biology
- `BIOINFORMATICS` - Bioinformatics (Oxford Academic)
- `NATURE_COMMUNICATIONS` - Nature Communications
- `GENERIC` - Generic academic format

## Extending the Schema

To add new journal types or section types:

1. Edit `schemas/manuscript.yaml`
2. Add to the appropriate enum (JournalType or SectionType)
3. Update skills if needed
4. Regenerate Python dataclasses if using LinkML tooling:
   ```bash
   gen-python schemas/manuscript.yaml > manuscript_models.py
   ```

## Questions?

See:
- [LinkML Documentation](https://linkml.io/)
- [WORKFLOW.md](WORKFLOW.md) - Complete workflow guide
- [USAGE_GUIDE.md](USAGE_GUIDE.md) - Detailed usage instructions
