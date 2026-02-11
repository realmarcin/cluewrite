# Figure References and .docx Export Guide

This guide explains how to include figures in your RRWrite manuscripts and export to Microsoft Word format for Google Docs import.

## Table of Contents
- [Adding Figures to Manuscripts](#adding-figures-to-manuscripts)
- [Converting to .docx Format](#converting-to-docx-format)
- [Complete Workflow](#complete-workflow)
- [Troubleshooting](#troubleshooting)

---

## Adding Figures to Manuscripts

### Overview

RRWrite can automatically:
1. Detect figure files in your repository (*.png, *.jpg, *.pdf, *.svg, *.eps)
2. Copy them to your manuscript directory
3. Ensure figure references render in markdown viewers

### Using Figures in Section Drafts

When drafting sections (especially **Results** and **Methods**), reference figures using standard markdown syntax:

```markdown
![Figure 1: Distribution of sample sizes](figures/distribution.png)

The analysis revealed a bimodal distribution (Figure 1), with peaks at...

![Figure 2: Performance metrics across datasets](figures/performance.png)
```

**Best Practices:**
- Use descriptive alt text (the text in square brackets)
- Store figures in a `figures/` subdirectory
- Use relative paths: `figures/filename.png`
- Include figure numbers and captions in the alt text

### Automatic Figure Handling During Assembly

When assembling your manuscript, use the `--include-figures` flag:

```bash
# From manuscript directory
cd example/rrwrite_v1/

# Run assembly with figure copying
python ../../scripts/rrwrite-assemble-manuscript.py \
    --output-dir . \
    --include-figures
```

This will:
- Scan the source repository for figure files
- Create `figures/` directory in manuscript folder
- Copy all detected figures
- Normalize figure references in the assembled markdown

### Using the Skill

```bash
/rrwrite-assemble --include-figures true
```

---

## Converting to .docx Format

### Why .docx?

Microsoft Word format (.docx) is ideal for:
- **Google Docs import** - preserves heading styles and formatting
- **Collaboration** - widely compatible with Word, LibreOffice, Pages
- **Track changes** - easier for reviewer feedback
- **Embedded figures** - images are automatically included

### Requirements

Install pandoc (one-time setup):

```bash
# macOS
brew install pandoc

# Ubuntu/Debian
sudo apt-get install pandoc

# Or Python package
pip install pypandoc
```

### Using the Conversion Script

**Standalone conversion:**

```bash
# Basic conversion
python scripts/rrwrite-convert-to-docx.py \
    --input example/rrwrite_v1/manuscript_full.md

# Specify output location
python scripts/rrwrite-convert-to-docx.py \
    --input manuscript_full.md \
    --output final_draft.docx

# Use custom Word template for styling
python scripts/rrwrite-convert-to-docx.py \
    --input manuscript_full.md \
    --reference-doc my-template.docx
```

**During assembly:**

```bash
python scripts/rrwrite-assemble-manuscript.py \
    --output-dir example/rrwrite_v1 \
    --convert-docx
```

Or via skill:

```bash
/rrwrite-assemble --convert-docx true
```

### Importing to Google Docs

1. Open [Google Docs](https://docs.google.com)
2. Click **File → Open → Upload**
3. Select your `manuscript_full.docx` file
4. Google Docs will preserve:
   - Heading styles (Heading 1, Heading 2, etc.)
   - Text formatting (bold, italic)
   - Embedded images
   - Table structures

---

## Complete Workflow

### End-to-End Example

Starting from a completed manuscript:

```bash
# Navigate to manuscript directory
cd example/rrwrite_v1/

# Assemble with figures and .docx conversion
python ../../scripts/rrwrite-assemble-manuscript.py \
    --output-dir . \
    --include-figures \
    --convert-docx
```

**Output:**
```
Assembling manuscript from 6 sections:
  ✓ abstract.md
  ✓ introduction.md
  ✓ methods.md
  ✓ results.md
  ✓ discussion.md
  ✓ availability.md

  Copied: plot1.png
  Copied: figure_distribution.png
  Copied: performance_metrics.pdf

✓ Manuscript assembled: manuscript_full.md
  Total size: 45231 bytes
  Estimated words: 4016

Converting to .docx format...
  ✓ Created: manuscript_full.docx (124.3 KB)

✓ Copied 3 figure(s) to figures/

Next steps:
1. Read the manuscript: manuscript_full.md
2. Open Word document: manuscript_full.docx
3. Import to Google Docs: Upload manuscript_full.docx to docs.google.com
```

### Using Skills (Recommended)

```bash
# Full assembly with all features
/rrwrite-assemble --include-figures true --convert-docx true
```

---

## Troubleshooting

### Pandoc Not Found

**Error:**
```
Pandoc not found. Install with: brew install pandoc
```

**Solution:**
```bash
# macOS
brew install pandoc

# Verify installation
pandoc --version
```

### Figures Not Rendering

**Issue:** Figure references show as broken links in markdown viewer

**Solutions:**
1. Ensure figures are in `figures/` subdirectory relative to markdown file
2. Check file extensions are lowercase (.png not .PNG)
3. Verify figure files were copied during assembly

**Check figure paths:**
```bash
cd example/rrwrite_v1/
ls figures/
```

### .docx Missing Figures

**Issue:** Word document doesn't include images

**Solutions:**
1. Ensure `--include-figures` was used during assembly
2. Check that figures exist in `figures/` directory
3. Verify figure references use relative paths: `figures/name.png`

### Word Document Formatting Issues

**Issue:** Headings don't have proper styles in Google Docs

**Solution:**
Use a custom reference document with pandoc:

```bash
# Create reference document (one-time)
pandoc -o reference.docx --print-default-data-file reference.docx

# Edit reference.docx in Word to set custom heading styles

# Use it for conversion
python scripts/rrwrite-convert-to-docx.py \
    --input manuscript_full.md \
    --reference-doc reference.docx
```

---

## Advanced Usage

### Custom Reference Templates

Create a Word document (`template.docx`) with your preferred:
- Heading styles (font, size, spacing)
- Body text formatting
- Caption styles
- Page layout

Use it during conversion:

```bash
python scripts/rrwrite-convert-to-docx.py \
    --input manuscript_full.md \
    --reference-doc template.docx
```

### Figure Directory Structure

**Recommended structure:**
```
manuscript_dir/
├── abstract.md
├── introduction.md
├── methods.md
├── results.md
├── discussion.md
├── figures/
│   ├── fig1_distribution.png
│   ├── fig2_performance.png
│   └── fig3_comparison.pdf
├── manuscript_full.md
└── manuscript_full.docx
```

### Batch Conversion

Convert multiple manuscripts:

```bash
for md in */manuscript_full.md; do
    python scripts/rrwrite-convert-to-docx.py --input "$md"
done
```

---

## Summary

### Quick Reference

**Include figures in assembly:**
```bash
/rrwrite-assemble --include-figures true
```

**Convert to .docx:**
```bash
/rrwrite-assemble --convert-docx true
```

**Both:**
```bash
/rrwrite-assemble --include-figures true --convert-docx true
```

**Standalone .docx conversion:**
```bash
python scripts/rrwrite-convert-to-docx.py --input manuscript_full.md
```

### Key Points

✅ Use `figures/filename.png` syntax in markdown
✅ Run assembly with `--include-figures` to auto-copy from repo
✅ Use `--convert-docx` for Google Docs import
✅ Install pandoc for .docx conversion
✅ Reference documents control Word styling

---

**Need help?** Check the main [RRWrite documentation](../README.md) or open an issue on GitHub.
