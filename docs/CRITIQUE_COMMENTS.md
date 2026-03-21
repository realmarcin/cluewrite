# Critique Comments in Word Documents

**NEW FEATURE**: RRWrite now automatically embeds critique comments directly into your manuscript .docx file, making it easier to address feedback.

## Overview

When you run the complete workflow with `rrwrite-assemble`, the system will:

1. Generate content and format critique reports
2. Run automated revisions to fix issues
3. Create a Word document with **embedded comments** for any remaining issues

This gives you a **single document** with all feedback integrated, rather than switching between separate critique report files.

## How It Works

### Automatic Integration

The comment embedding happens automatically during assembly:

```bash
"Use /rrwrite-assemble --target-dir manuscript --convert-docx --max-revisions 2"
```

This creates:
- `full_manuscript.docx` - Clean version
- `manuscript_with_comments_v{N}.docx` - **With embedded comments**

### Comment Format

Each embedded comment includes:

```
💬 COMMENT on "specific text snippet..."

[MAJOR] Content: Evidence | Strong claim without evidence: "our method demonstrates..."
Impact: Unsupported claims undermine credibility
Action: Add citation or data reference to support claim

— RRWrite Critique, 2026-02-11
```

**Components:**
- **Comment marker** (💬) - Easy to spot in the document
- **Text reference** - Shows which text the comment applies to
- **Severity** - MAJOR or MINOR
- **Category** - Content, Format, Structure, etc.
- **Description** - What the issue is
- **Impact** - Why it matters (for major issues)
- **Action** - Specific steps to fix
- **Metadata** - Author and date

### Manual Usage

You can also generate commented documents manually:

```bash
# After running critique
python scripts/rrwrite-embed-critique-comments.py --manuscript-dir manuscript

# For specific version
python scripts/rrwrite-embed-critique-comments.py --manuscript-dir manuscript --version 2

# Only unresolved issues (after revisions)
python scripts/rrwrite-embed-critique-comments.py --manuscript-dir manuscript --unresolved-only
```

## Workflow Integration

### Default Workflow

1. **Assembly** generates critique reports
2. **Revision** addresses major issues automatically
3. **Comment embedding** creates .docx with remaining issues
4. **You review** the commented document and address feedback

### After Revisions

When you run `rrwrite-revise-manuscript`, it:
- Fixes issues iteratively
- Tracks which issues remain
- Generates commented .docx with **only unresolved issues**

This means you only see comments for things that still need attention!

## Comment Types

### Text-Specific Comments

Attached to the exact text where the issue was found:

```
We demonstrate that our method is the best approach...
💬 COMMENT: [MAJOR] Evidence | Strong claim needs support
```

### Section Comments

Attached to section headers when the issue applies to the whole section:

```
# Methods
💬 COMMENT: [MAJOR] Reproducibility | Missing software versions
```

### Summary Comments

If specific locations can't be determined, all comments appear in a summary section at the end.

## Using the Commented Document

### In Microsoft Word

1. Open `manuscript_with_comments_v{N}.docx`
2. Comments appear as styled text with the 💬 marker
3. Address each issue in place
4. Delete the comment marker when resolved
5. Save your revised version

### In Google Docs

1. Upload to Google Docs
2. Comments are preserved as styled text
3. Use "Suggesting" mode to track your changes
4. Share with collaborators to address comments together

### Tracking Progress

- **Before fixes**: All unresolved issues have comments
- **During fixes**: Delete comment markers as you address them
- **After fixes**: Document should have no comment markers
- **Re-run critique**: Verify all issues are resolved

## Comment Filtering

### Severity Levels

- **MAJOR** - Must be fixed before submission
  - Scientific validity issues
  - Missing evidence
  - Logical gaps
  - Critical formatting problems

- **MINOR** - Should be improved
  - Style inconsistencies
  - Minor formatting issues
  - Suggestions for clarity

### Version Tracking

Each revision iteration creates a new version:
- `critique_content_v1.md` → Initial critique
- `critique_content_v2.md` → After first revision
- `manuscript_with_comments_v2.docx` → Only issues remaining after revisions

### Unresolved-Only Mode

Use `--unresolved-only` to see only issues that remain after automated fixes:

```bash
python scripts/rrwrite-embed-critique-comments.py \
  --manuscript-dir manuscript \
  --unresolved-only
```

## Technical Details

### Requirements

```bash
pip install python-docx lxml
```

### Implementation

The script:
1. Parses critique reports (content + format)
2. Extracts issue details (severity, category, description, action)
3. Identifies text snippets mentioned in critique
4. Searches manuscript for matching text
5. Inserts styled comments near relevant text
6. Falls back to section headers or summary if text not found

### Comment Placement

Priority order:
1. **Exact text match** - If critique mentions specific text, place comment there
2. **Section header** - If text not found but section known, place at section start
3. **Summary section** - If location unknown, add to end summary

### Limitations

- python-docx doesn't support native Word comments, so comments are styled text
- Future versions may use full OOXML comment support
- For now, comments are visible inline (actually better for most users!)

## Best Practices

### During Writing

1. Run assembly with critiques enabled (default)
2. Let automated revisions fix what they can
3. Review commented .docx for remaining issues
4. Address all MAJOR comments before submission
5. Consider MINOR comments for improvement

### Before Submission

1. Ensure no comment markers (💬) remain in document
2. Re-run critique to verify all issues resolved
3. Check that `critique_content_v{N}.md` shows no major issues
4. Review evidence report for citation accuracy

### Collaboration

1. Share `manuscript_with_comments_v{N}.docx` with co-authors
2. Each author can address comments in their expertise area
3. Use track changes to show what was fixed
4. Delete comment markers when consensus reached

## Examples

### Complete Workflow

```bash
# Start from repository
"Use /rrwrite-analyze-repository --repo-path . --target-dir manuscript"

# Generate outline
"Use /rrwrite-plan-manuscript for Bioinformatics"

# Draft sections
"Use /rrwrite-draft-section to write Methods"
"Use /rrwrite-draft-section to write Results"
# ... etc

# Assemble with automatic critique, revision, and comment embedding
"Use /rrwrite-assemble --target-dir manuscript --convert-docx --max-revisions 2"

# Result: manuscript_with_comments_v3.docx has all remaining issues marked
```

### Manual Comment Embedding

```bash
# Run critique manually
python scripts/rrwrite-critique-manuscript.py --manuscript-dir manuscript

# Embed comments
python scripts/rrwrite-embed-critique-comments.py --manuscript-dir manuscript

# Output: manuscript_with_comments_v1.docx
```

### After Addressing Comments

```bash
# Make your fixes in the .docx or .md file

# Re-run assembly to verify
"Use /rrwrite-assemble --target-dir manuscript --no-convert-docx"

# Check new critique reports - should show fewer/no issues
```

## Troubleshooting

### No Comments Appearing

- Check that critique reports exist (`critique_content_v*.md`)
- Verify pandoc is installed for .docx conversion
- Check python-docx is installed: `pip install python-docx lxml`

### Comments in Wrong Places

- The script tries to match text snippets from critiques
- If text changed since critique, matches may fail
- Comments fall back to section headers or summary section

### Want Native Word Comments

Future enhancement - current implementation uses styled text which is:
- Visible to all users
- Easy to find and delete
- Compatible with Google Docs
- Simpler than OOXML comment API

## Future Enhancements

Planned improvements:
- [ ] Native Word comment support via OOXML
- [ ] Highlight specific text ranges
- [ ] Interactive comment resolution tracking
- [ ] Export resolved vs. unresolved comment lists
- [ ] Integration with track changes
- [ ] Comment threading for discussions

## Support

For issues or questions:
- GitHub: https://github.com/anthropics/claude-code/issues
- Include your critique version and command used
- Attach sample critique report if possible
