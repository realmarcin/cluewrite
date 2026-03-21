# Safe Google Docs Editing Guide

## Overview

This system safely applies manuscript edits to Google Docs while preserving:
- **Paperpile citation links** (using fuzzy matching)
- **Text styles** (11pt font, not 16pt)
- **Document structure**

## Problem Solved

Previous approach using `replaceAllText` caused:
1. **Garbled citations** (EMBL-EBI+3PMC+3) - index shifting corrupted Paperpile links
2. **Font size changes** (11pt → 16pt) - new text inherited default style
3. **Unwanted replacements** - Methods section should not be replaced

## Architecture

### Three Core Scripts

1. **`citation_matcher.py`** - Fuzzy citation matching (85% threshold)
   - Handles multiple citation formats
   - Prepends `cite` to unmatched citations
   - Uses `SequenceMatcher` for similarity scoring

2. **`safe_gdoc_editor.py`** - Segment-based editing with style preservation
   - Extracts section with links and style
   - Replaces content atomically
   - Restores original formatting

3. **`apply_manuscript_edits.py`** - Batch orchestrator
   - Coordinates all 7 batches
   - Validates after each batch
   - Supports dry-run mode

### Batch Strategy

| Batch | Operation | Risk | Method |
|-------|-----------|------|--------|
| 1 | Title replacement | NONE | `replaceAllText` (single occurrence) |
| 2 | Terminology fixes | LOW | Sequential `replaceAllText` |
| 3 | Abstract replacement | MEDIUM | Segment replacement (0 citations) |
| 4 | Introduction replacement | HIGH | Segment + fuzzy citation matching |
| 5 | Results replacement | HIGH | Segment + fuzzy citation matching |
| 6 | Discussion replacement | HIGH | Segment + fuzzy citation matching |
| 7 | Methods replacement | SKIPPED | Do not replace per user clarification |

## Usage

### Step 1: Dry Run (Preview All Changes)

```bash
python scripts/apply_manuscript_edits.py \
    --document-id 1gwjtHp863cFv61rJ3gd7l2RGje6tQy6he3bC8YFBuSU \
    --manuscript-file manuscript/kbaseeco_v2/manuscript_v2_final.md \
    --all \
    --dry-run
```

**Expected output:**
- Text changes (character counts)
- Style preservation details (11pt Arial)
- Citation matching results (exact/fuzzy/unmatched)
- Preview of `cite`-prefixed citations

### Step 2: Apply Safe Batches (1-2)

```bash
# Batches 1-2 have no citations - safest to apply first
python scripts/apply_manuscript_edits.py \
    --document-id 1gwjtHp863cFv61rJ3gd7l2RGje6tQy6he3bC8YFBuSU \
    --manuscript-file manuscript/kbaseeco_v2/manuscript_v2_final.md \
    --batches 1,2 \
    --validate-after-each
```

**Validation:**
- Batch 1: Title includes subtitle
- Batch 2: No forbidden terms ("adaptive significance", "essential for survival", "selection")

### Step 3: Apply Abstract (Batch 3)

```bash
# Abstract typically has 0 citations - low risk
python scripts/apply_manuscript_edits.py \
    --document-id 1gwjtHp863cFv61rJ3gd7l2RGje6tQy6he3bC8YFBuSU \
    --manuscript-file manuscript/kbaseeco_v2/manuscript_v2_final.md \
    --batches 3 \
    --validate-after-each
```

**Validation:**
- Font size is 11pt (not 16pt)
- No garbled text

### Step 4: Apply Citation-Heavy Sections (Batches 4-6)

```bash
# Introduction, Results, Discussion - highest risk
python scripts/apply_manuscript_edits.py \
    --document-id 1gwjtHp863cFv61rJ3gd7l2RGje6tQy6he3bC8YFBuSU \
    --manuscript-file manuscript/kbaseeco_v2/manuscript_v2_final.md \
    --batches 4,5,6 \
    --validate-after-each
```

**Expected output:**
```
Batch 4 (Introduction):
  ✓ Matched 15/18 citations
    - Exact matches: 12
    - Fuzzy matches: 3
    - Unmatched: 0
  ✓ Style preserved: 11pt Arial
  ✅ Section replaced successfully!
```

### Step 5: Manual Citation Cleanup

Search Google Doc for `cite(` to find unmatched citations:

1. Press `Ctrl+F` (or `Cmd+F`)
2. Search for: `cite(`
3. For each result:
   - Remove `cite` prefix
   - Highlight citation
   - Add Paperpile link (right-click → Insert link → Search Paperpile)

## Verification Checklist

After all batches complete:

- [ ] Title includes subtitle
- [ ] No "adaptive significance", "essential for survival", "selection" terms
- [ ] Font size is 11pt throughout (not 16pt)
- [ ] Paperpile citations are clickable (test 5 randomly)
- [ ] No garbled text (EMBL-EBI+3PMC+3 patterns)
- [ ] Methods section unchanged (Batch 7 skipped)
- [ ] Search for `cite(` - convert to Paperpile links

## Advanced Usage

### Apply Single Section

```bash
# Use safe_gdoc_editor directly for one section
python -c "
from safe_gdoc_editor import SafeGoogleDocEditor
from google.oauth2 import service_account
from googleapiclient.discovery import build
from pathlib import Path

creds = service_account.Credentials.from_service_account_file(
    'credentials.json',
    scopes=['https://www.googleapis.com/auth/documents']
)
service = build('docs', 'v1', credentials=creds)
editor = SafeGoogleDocEditor(service, '1gwjtHp863cFv61rJ3gd7l2RGje6tQy6he3bC8YFBuSU')

new_text = Path('manuscript/kbaseeco_v2/sections/introduction_v2.md').read_text()
editor.replace_section('Introduction', new_text, dry_run=True)
"
```

### Customize Fuzzy Threshold

```python
# In apply_manuscript_edits.py, modify:
self.editor = SafeGoogleDocEditor(service, document_id, fuzzy_threshold=0.90)
```

**Higher threshold (0.90-0.95):** Stricter matching, more `cite` prefixes
**Lower threshold (0.75-0.80):** More lenient, fewer `cite` prefixes (risk of wrong matches)

## Troubleshooting

### "Section not found or empty"

**Cause:** Section header doesn't match expected format
**Fix:** Check Google Doc has heading style (not just bold text)

### "Font size still 16pt"

**Cause:** Style extraction failed
**Fix:** Check `safe_gdoc_editor.py` extracted dominant style correctly

### Too many `cite` prefixes

**Cause:** Citations changed between v1 and v2
**Fix:** Lower fuzzy threshold or manually add Paperpile links

### API quota exceeded

**Cause:** Too many requests in short time
**Fix:** Wait 60 seconds, apply batches one at a time

## Safety Features

### 1. Atomic Operations
Each batch is a single `batchUpdate` call - either all succeed or all fail

### 2. Dry Run Mode
Preview all changes before applying

### 3. Index Isolation
Segment-based replacement prevents cascading index shifts

### 4. Style Preservation
Extracts and reapplies original formatting (fontSize, fontFamily, bold, italic)

### 5. Fuzzy Citation Matching
Handles slight variations in citation format

### 6. Unmatched Citation Marking
`cite` prefix makes missing links easy to find

## File Dependencies

```
scripts/
├── citation_matcher.py       # Fuzzy citation matching engine
├── safe_gdoc_editor.py       # Section editor with style preservation
└── apply_manuscript_edits.py # Batch orchestrator (main entry point)

manuscript/kbaseeco_v2/
└── manuscript_v2_final.md    # Source for edits

credentials.json              # Google API service account credentials
```

## Workflow Summary

```
1. Dry run all batches → Review output
2. Apply Batches 1-2 (safe) → Validate
3. Apply Batch 3 (Abstract) → Check font size
4. Apply Batches 4-6 (citations) → Check Paperpile links
5. Skip Batch 7 (Methods)
6. Search for cite( → Add Paperpile links manually
7. Final verification checklist
```

## Example Output

```
======================================================================
BATCH 4: INTRODUCTION (Risk: HIGH)
======================================================================
Extracted 3,421 characters from Introduction

📖 Extracting section: Introduction
  ✓ Found section header at index 1234
  ✓ Extracted 3,156 characters
  ✓ Found 18 Paperpile citations
  ✓ Dominant style: 11pt Arial

🔗 Matching 18 citations to new text (fuzzy threshold: 0.85)...
  ✓ Found 18 citation patterns in new text
  ✓ Matched 18/18 citations
    - Exact matches: 15
    - Fuzzy matches: 3
    - Unmatched: 0

📝 Generated 21 API requests

✅ Section replaced successfully!
   • Style preserved: 11pt Arial
   • 18 Paperpile citations preserved

🔍 Validating Batch 4...
  ✓ Found 18 Paperpile citation links
```

## Next Steps

After successful application:
1. Review document in browser
2. Spot-check 5 random citations (click to verify Paperpile links work)
3. Check font consistency
4. Address any `cite(` prefixed citations
5. Share with collaborators
