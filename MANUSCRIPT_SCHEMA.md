# Manuscript Schema and Conventions

This document explains the LinkML schema (`schemas/manuscript.yaml`) and file naming conventions used by Research Writer.

## Overview

All manuscript-related outputs are stored in the `manuscript/` directory with standardized names and structures validated against a LinkML schema.

## Directory Structure

```
your-project/
├── CLUEWRITE.md              # Project context
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
│   ├── review_outline_v1.md      # Outline review
│   ├── review_literature_v1.md   # Literature review
│   ├── review_manuscript_v1.md   # Manuscript review
│   └── review_manuscript_v2.md   # Subsequent review
├── schemas/
│   └── manuscript.yaml      # LinkML schema definition
├── scripts/
│   └── cluewrite-validate-manuscript.py  # Validator
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
- **Purpose:** Complete assembled manuscript ready for review/submission
- **Contents:** All sections combined in order

### Reviews
- **Filename pattern:** `manuscript/review_TYPE_vN.md`
  - `TYPE`: one of `outline`, `literature`, `section`, `manuscript`
  - `N`: version number (1, 2, 3, ...)
- **Examples:**
  - `review_outline_v1.md`
  - `review_manuscript_v1.md`
  - `review_manuscript_v2.md` (after revisions)

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
python scripts/cluewrite-validate-manuscript.py \
  --file manuscript/outline.md \
  --type outline

# Validate literature review
python scripts/cluewrite-validate-manuscript.py \
  --file manuscript/literature.md \
  --type literature

# Validate section
python scripts/cluewrite-validate-manuscript.py \
  --file manuscript/methods.md \
  --type section

# Validate full manuscript
python scripts/cluewrite-validate-manuscript.py \
  --file manuscript/full_manuscript.md \
  --type manuscript

# Validate review
python scripts/cluewrite-validate-manuscript.py \
  --file manuscript/review_manuscript_v1.md \
  --type review
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
- Ready-for-review status

### Review
Defines review report structure:
- Correct filename pattern
- Review type (outline, literature, section, manuscript)
- Version number
- Required sections (Summary, Strengths, Issues, Recommendation)
- Recommendation type (Accept Minor, Major Revisions, Reject)

## Workflow Integration

The skills automatically use these conventions:

1. **`cluewrite-plan-manuscript`**
   - Creates `manuscript/outline.md`
   - Validates against schema

2. **`cluewrite-research-literature`**
   - Creates `manuscript/literature.md`
   - Creates `manuscript/literature_citations.bib`
   - Creates `manuscript/literature_evidence.csv`
   - Validates against schema

3. **`cluewrite-draft-section`**
   - Creates `manuscript/SECTIONNAME.md`
   - Validates against schema

4. **`cluewrite-review-manuscript`**
   - Creates `manuscript/review_TYPE_vN.md`
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
