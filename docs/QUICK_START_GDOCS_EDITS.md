# Quick Start: Safe Google Docs Editing

## TL;DR - Run These Commands

### 1. Dry Run (Preview All Changes)
```bash
python scripts/apply_manuscript_edits.py \
    --document-id 1gwjtHp863cFv61rJ3gd7l2RGje6tQy6he3bC8YFBuSU \
    --manuscript-file manuscript/kbaseeco_v2/manuscript_v2_final.md \
    --all \
    --dry-run
```

### 2. Apply Safe Batches (1-2)
```bash
python scripts/apply_manuscript_edits.py \
    --document-id 1gwjtHp863cFv61rJ3gd7l2RGje6tQy6he3bC8YFBuSU \
    --manuscript-file manuscript/kbaseeco_v2/manuscript_v2_final.md \
    --batches 1,2 \
    --validate-after-each
```

### 3. Apply Abstract (Batch 3)
```bash
python scripts/apply_manuscript_edits.py \
    --document-id 1gwjtHp863cFv61rJ3gd7l2RGje6tQy6he3bC8YFBuSU \
    --manuscript-file manuscript/kbaseeco_v2/manuscript_v2_final.md \
    --batches 3 \
    --validate-after-each
```

### 4. Apply Citation-Heavy Sections (4-6)
```bash
python scripts/apply_manuscript_edits.py \
    --document-id 1gwjtHp863cFv61rJ3gd7l2RGje6tQy6he3bC8YFBuSU \
    --manuscript-file manuscript/kbaseeco_v2/manuscript_v2_final.md \
    --batches 4,5,6 \
    --validate-after-each
```

### 5. Manual Cleanup
1. Open Google Doc
2. Press `Ctrl+F` (or `Cmd+F`)
3. Search: `cite(`
4. For each result: Remove `cite` prefix, add Paperpile link

## What This Does

| Batch | Action | Safe? | What to Check |
|-------|--------|-------|---------------|
| 1 | Replace title | ✅ Yes | Title has subtitle |
| 2 | Fix terminology | ✅ Yes | No forbidden terms |
| 3 | Replace Abstract | ⚠️ Medium | Font is 11pt |
| 4 | Replace Introduction | ⚠️ High | Citations clickable |
| 5 | Replace Results | ⚠️ High | Citations clickable |
| 6 | Replace Discussion | ⚠️ High | Citations clickable |
| 7 | Replace Methods | **SKIPPED** | N/A |

## Safety Features

✅ **Style Preservation** - Keeps 11pt font (not 16pt)
✅ **Paperpile Links** - Fuzzy matching preserves citations
✅ **Atomic Updates** - All-or-nothing (no partial corruption)
✅ **Dry Run Mode** - Preview before applying
✅ **Incremental Batches** - Apply one at a time
✅ **Validation** - Check after each batch

## Key Terminology Replacements (Batch 2)

- "adaptive significance" → "ecosystem-discriminative significance"
- "essential for survival" → "characteristic of"
- "selection" → "enrichment"

## Expected Output

```
✅ Section replaced successfully!
   • Style preserved: 11pt Arial
   • 18 Paperpile citations preserved
   • 2 citations marked with 'cite' prefix

🔍 Validating Batch 4...
  ✓ Found 18 Paperpile citation links
```

## If Something Goes Wrong

1. **Restore document** from Google Docs version history
2. **Check error message** - Usually section name mismatch
3. **Run dry-run again** to verify changes
4. **Apply one batch at a time** with validation

## Full Documentation

- **Usage Guide:** `docs/SAFE_GDOCS_EDITING_GUIDE.md`
- **Implementation:** `SAFE_GDOCS_IMPLEMENTATION.md`
- **Plan Archive:** Transcript in `.claude/projects/.../[id].jsonl`

## Verification Checklist

After all batches:
- [ ] Title includes subtitle
- [ ] No "adaptive significance" / "essential for survival" / "selection"
- [ ] Font is 11pt everywhere (not 16pt)
- [ ] Random citations are clickable (test 5)
- [ ] No garbled text (EMBL-EBI+3PMC+3)
- [ ] Methods unchanged
- [ ] All `cite(` converted to Paperpile links

---

**Ready?** Start with the dry run command above! 🚀
