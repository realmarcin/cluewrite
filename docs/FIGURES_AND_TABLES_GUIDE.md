# Guide: Adding Figures and Tables to RRWrite Manuscripts

This guide explains how to add figures and tables to RRWrite manuscripts and ensure they appear in the DOCX output.

## Overview

The `rrwrite-assemble-manuscript.py` script generates three formats:
- **Markdown** (.md): Source format
- **DOCX** (.docx): Microsoft Word format with embedded figures and tables
- **PDF** (.pdf): PDF format (if LaTeX tools available)

As of 2026-03-05, the assembly script uses enhanced Pandoc options to properly handle figures and tables.

## Adding Figures

### 1. Place Image Files

Place image files in your manuscript directory or subdirectories:

```
manuscript/project_v1/
├── sections/
│   ├── results.md
│   └── ...
├── figures/          # Create this directory
│   ├── figure1.png
│   ├── figure2.jpg
│   └── workflow.pdf
└── ...
```

**Supported formats:** PNG, JPG, JPEG, PDF, SVG

### 2. Reference in Markdown

In your section files, reference images using standard markdown syntax:

```markdown
![Figure 1: System architecture showing the agent-based workflow](figures/figure1.png)

The experimental design (Figure 2) demonstrates...

![Figure 2: MaxPro optimal blocking design](figures/figure2.png)
```

### 3. Assemble Manuscript

Run the assembly script:

```bash
python scripts/rrwrite-assemble-manuscript.py --output-dir manuscript/project_v1
```

The DOCX file will:
- Embed all referenced images
- Extract media files to `manuscript/project_v1/media/`
- Use the manuscript directory as the resource path for resolving image paths

## Adding Tables

### Option 1: Markdown Tables (Simple)

For small tables, use markdown pipe syntax directly in your section files:

```markdown
## Results

**Table 1: Repository Statistics**

| Category | File Count | Total Size (MB) | Avg Size (KB) |
|----------|------------|-----------------|---------------|
| Doc      | 421        | 181.94          | 442.53        |
| Figure   | 365        | 256.34          | 719.14        |
| Data     | 179        | 2891.99         | 16544.13      |
| Script   | 35         | 1.36            | 39.84         |
```

These will render properly in both markdown and DOCX.

### Option 2: Convert TSV Files (Complex Tables)

For larger tables or data from `data_tables/`, use the conversion utility:

#### Convert Single Table

```bash
python scripts/rrwrite-convert-tsv-to-table.py \
    --input manuscript/project_v1/data_tables/repository_statistics.tsv \
    --caption "Table 1: Repository Statistics"
```

This outputs markdown table to stdout. Redirect to file or copy into your section:

```bash
# Save to file
python scripts/rrwrite-convert-tsv-to-table.py \
    --input manuscript/project_v1/data_tables/repository_statistics.tsv \
    --caption "Table 1: Repository Statistics" \
    --output manuscript/project_v1/tables/table1.md

# Then include in section file:
# In results.md:
{{include tables/table1.md}}
```

#### Convert All Tables in Directory

```bash
python scripts/rrwrite-convert-tsv-to-table.py \
    --input-dir manuscript/project_v1/data_tables/ \
    --output-dir manuscript/project_v1/tables/
```

This creates markdown files for all TSV files.

#### Limit Large Tables

For tables with many rows, limit displayed rows:

```bash
python scripts/rrwrite-convert-tsv-to-table.py \
    --input data_tables/large_file_inventory.tsv \
    --max-rows 10 \
    --caption "Table 2: File Inventory (showing first 10 of 1000 entries)"
```

## Pandoc Options Used

The assembly script uses these Pandoc options for DOCX generation:

```bash
pandoc manuscript.md -o manuscript.docx \
    --standalone \
    --resource-path <manuscript_dir> \
    --extract-media <manuscript_dir>/media \
    --wrap=preserve \
    --metadata title=Manuscript
```

**Key options:**
- `--resource-path`: Tells Pandoc where to find referenced images
- `--extract-media`: Embeds images in DOCX and extracts to media/ folder
- `--wrap=preserve`: Maintains table column alignment
- `--standalone`: Creates complete DOCX document

## Custom Styling (Optional)

Create a reference DOCX template with custom styles:

1. Create `templates/reference.docx` with your preferred styles
2. Assembly script automatically uses it if present
3. Styles include: Normal, Heading 1-6, Caption, Table styles

## Troubleshooting

### Images Not Showing in DOCX

**Problem:** Figures referenced in markdown don't appear in DOCX

**Solutions:**
1. Check image paths are relative to manuscript directory
2. Verify image files exist at specified paths
3. Use forward slashes in paths: `figures/image.png` (not `figures\image.png`)
4. Check Pandoc output for warnings: run assembly script and review messages

### Tables Not Formatting Properly

**Problem:** Tables appear misaligned or malformed

**Solutions:**
1. Ensure all rows have same number of columns
2. Check separator row uses `---` (at least 3 dashes per column)
3. Verify TSV files don't have inconsistent column counts
4. Use `--max-rows` to limit very wide tables

### Missing Media Directory

**Problem:** `media/` directory not created

**Solution:** This is normal if no images were extracted. Pandoc only creates media/ if images are embedded.

## Example Workflow

Complete workflow for adding figures and tables:

```bash
# 1. Create directories
mkdir -p manuscript/project_v1/figures
mkdir -p manuscript/project_v1/tables

# 2. Add image files
cp /path/to/figure1.png manuscript/project_v1/figures/

# 3. Convert data tables
python scripts/rrwrite-convert-tsv-to-table.py \
    --input-dir manuscript/project_v1/data_tables/ \
    --output-dir manuscript/project_v1/tables/

# 4. Edit section files to add figure references
vim manuscript/project_v1/sections/results.md
# Add: ![Figure 1: Description](figures/figure1.png)

# 5. Reassemble manuscript
python scripts/rrwrite-assemble-manuscript.py \
    --output-dir manuscript/project_v1

# 6. Verify DOCX contains figures/tables
open manuscript/project_v1/full_manuscript.docx
```

## PLOS and Journal Requirements

Many journals (PLOS, Nature, etc.) require:

### Figure Captions
- Place caption text in markdown alt text: `![Caption here](image.png)`
- Pandoc converts this to proper DOCX figure caption
- Number figures sequentially: Figure 1, Figure 2, etc.

### Table Titles
- Place above table using bold: `**Table 1: Description**`
- Keep title concise (< 125 characters for PLOS)

### Figure Quality
- Use high resolution: 300 DPI minimum for print
- Preferred formats: PNG (plots), PDF (vector graphics), JPG (photos)
- File size: < 10 MB per figure

## References

- Pandoc documentation: https://pandoc.org/MANUAL.html
- PLOS figure guidelines: https://journals.plos.org/plosone/s/figures
- Assembly script: `scripts/rrwrite-assemble-manuscript.py`
- TSV converter: `scripts/rrwrite-convert-tsv-to-table.py`
