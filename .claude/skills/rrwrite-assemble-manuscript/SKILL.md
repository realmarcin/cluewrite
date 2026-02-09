---
name: rrwrite-assemble-manuscript
description: Assembles complete manuscript from individual section files in journal-specified order
arguments:
  - name: target_dir
    description: Directory containing manuscript sections
    default: manuscript
  - name: validate
    description: Validate word counts against journal limits
    default: true
allowed-tools:
---

# Manuscript Assembly Protocol

Assembles a complete, reproducible manuscript from individual section files.
Concatenates sections in journal-specified order, adds metadata, validates
word counts, and generates assembly manifest.

## Overview

This skill should be run AFTER all sections are drafted and BEFORE critique.
It creates a single `manuscript.md` file from component sections that:
- Is properly ordered according to journal requirements
- Includes complete metadata (title, authors, journal, word count)
- Is reproducible (manifest tracks what was assembled and when)
- Is validated against journal word limits

---

## Phase 1: Pre-Assembly Validation

### 1.1 Check Workflow State

```bash
# Verify state file exists
STATE_FILE="{target_dir}/.rrwrite/state.json"

if [ ! -f "$STATE_FILE" ]; then
  echo "❌ Error: No workflow state found in {target_dir}"
  echo "   Run /rrwrite-plan-manuscript first"
  exit 1
fi

echo "✓ Workflow state found"
```

### 1.2 Check Drafting Status

```python
import json
from pathlib import Path

# Load state
state_file = Path("{target_dir}") / ".rrwrite" / "state.json"
with open(state_file) as f:
    state = json.load(f)

# Check drafting status
drafting = state['workflow_status']['drafting']
completed = drafting['completed_sections']
total = drafting['total_sections']

print(f"Drafting progress: {completed}/{total} sections completed")

if completed == 0:
    print("❌ Error: No sections have been drafted yet")
    print("   Run /rrwrite-draft-section to draft sections first")
    exit(1)

if completed < total:
    print(f"⚠ Warning: Only {completed}/{total} sections completed")
    print(f"   Missing sections may cause incomplete manuscript")

    # Ask user if they want to proceed
    response = input("Proceed with partial manuscript? (y/n): ")
    if response.lower() != 'y':
        print("Assembly cancelled")
        exit(0)
```

### 1.3 Identify Available Sections

```bash
# List all .md files in target directory (excluding special files)
echo "\nAvailable sections:"
find "{target_dir}" -maxdepth 1 -name "*.md" \
  ! -name "outline.md" \
  ! -name "repository_analysis.md" \
  ! -name "literature.md" \
  ! -name "journal_assessment.md" \
  ! -name "author_guidelines.md" \
  ! -name "critique.md" \
  ! -name "manuscript.md" \
  -exec basename {{}} \; | sort
```

**Expected sections** (typical):
- `abstract.md`
- `introduction.md`
- `methods.md` (or `materials_and_methods.md`, `experimental_procedures.md`)
- `results.md`
- `discussion.md`
- `conclusion.md` (optional)
- `data_availability.md` (or `availability.md`)
- `code_availability.md` (optional)
- `acknowledgements.md` (optional)
- `funding.md` (optional)

---

## Phase 2: Run Assembly Script

### 2.1 Execute Assembly

```bash
echo "\n{'='*60}"
echo "Assembling Manuscript"
echo "{'='*60}\n"

# Run assembly script
python scripts/rrwrite-assemble-manuscript.py \
  --target-dir "{target_dir}" \
  --validate
```

**The script will:**
1. Load journal guidelines from assessment (if available)
2. Determine correct section order for the journal
3. Find and read all section files
4. Concatenate sections in correct order
5. Add manuscript header with metadata
6. Calculate total word count
7. Generate assembly manifest
8. Validate word counts against journal limits
9. Save complete manuscript to `{target_dir}/manuscript.md`

### 2.2 Review Assembly Output

The script outputs:
- Section order used
- Which sections were found/included
- Which sections are missing
- Word count per section
- Total word count
- Validation warnings (if any)

**Example output:**
```
Assembling manuscript for: Bioinformatics
Target directory: manuscript/repo_v1

Section order (11 sections):
  1. abstract
  2. introduction
  3. methods
  4. results
  5. discussion
  6. conclusion
  7. data_availability
  8. acknowledgements
  9. funding
  10. references

✓ Found: abstract (abstract.md)
  Word count: 247

✓ Found: introduction (introduction.md)
  Word count: 1,423

✓ Found: methods (methods.md)
  Word count: 2,156

✓ Found: results (results.md)
  Word count: 1,876

✓ Found: discussion (discussion.md)
  Word count: 1,102

⚠ Missing: conclusion

✓ Found: data_availability (availability.md)
  Word count: 127

⚠ Missing: acknowledgements

⚠ Missing: funding

⚠ Missing: references

============================================================
✓ Manuscript assembled successfully!
============================================================

Output: manuscript/repo_v1/manuscript.md
Total word count: 6,931 words
Sections included: 6
Sections missing: 4

Manifest saved: manuscript/repo_v1/assembly_manifest.json
```

---

## Phase 3: Validate Assembly

### 3.1 Check Manuscript File

```bash
# Verify manuscript.md was created
MANUSCRIPT_FILE="{target_dir}/manuscript.md"

if [ ! -f "$MANUSCRIPT_FILE" ]; then
  echo "❌ Error: Manuscript file was not created"
  exit 1
fi

echo "✓ Manuscript file created: $MANUSCRIPT_FILE"

# Show file size
FILE_SIZE=$(wc -c < "$MANUSCRIPT_FILE")
echo "  File size: $FILE_SIZE bytes"

# Show line count
LINE_COUNT=$(wc -l < "$MANUSCRIPT_FILE")
echo "  Line count: $LINE_COUNT lines"
```

### 3.2 Review Word Count Validation

If journal guidelines are available, the script validates word counts:

**Example validation output:**
```
============================================================
Word Count Validation
============================================================

✓ Total word count within limits: 6,931 words (3000-7000)
✓ abstract: 247 words (within 150-250)
✓ introduction: 1,423 words (within 500-1500)
❌ methods: 2,156 words > 2000 (maximum)
✓ results: 1,876 words (within 1000-2000)
✓ discussion: 1,102 words (within 500-1500)
✓ data_availability: 127 words (within 50-150)
```

**Action on violations:**
- ❌ (exceeds maximum): Section must be edited down before submission
- ⚠ (below minimum): Consider expanding section
- ✓ (within limits): No action needed

### 3.3 Review Assembly Manifest

```bash
# Display manifest
echo "\nAssembly Manifest:"
cat "{target_dir}/assembly_manifest.json" | jq '.'
```

**Manifest contains:**
```json
{
  "assembled_at": "2026-02-06T15:30:45.123456",
  "target_journal": "bioinformatics",
  "sections_included": [
    {
      "name": "abstract",
      "file": "abstract.md",
      "word_count": 247
    },
    {
      "name": "introduction",
      "file": "introduction.md",
      "word_count": 1423
    }
    // ... more sections
  ],
  "sections_missing": [
    "conclusion",
    "acknowledgements",
    "funding",
    "references"
  ],
  "total_word_count": 6931,
  "section_word_counts": {
    "abstract": 247,
    "introduction": 1423,
    "methods": 2156,
    "results": 1876,
    "discussion": 1102,
    "data_availability": 127
  },
  "validation_warnings": [
    "Required section missing: references"
  ]
}
```

---

## Phase 4: Handle Warnings and Errors

### 4.1 Missing Required Sections

If required sections are missing:

```bash
# Check for required section warnings
WARNINGS=$(cat "{target_dir}/assembly_manifest.json" | jq -r '.validation_warnings[]')

if [ -n "$WARNINGS" ]; then
  echo "\n⚠ Required sections missing:"
  echo "$WARNINGS"

  echo "\nAction required:"
  echo "  1. Draft missing sections using /rrwrite-draft-section"
  echo "  2. Re-run assembly after drafting"
  echo "  3. Or proceed with partial manuscript (not recommended)"
fi
```

### 4.2 Word Count Violations

If word counts exceed limits:

```bash
echo "\n❌ Word count violations detected"
echo "  methods: 2,156 words > 2,000 (maximum)"
echo "\nAction required:"
echo "  1. Edit {target_dir}/methods.md to reduce length"
echo "  2. Re-run assembly: /rrwrite-assemble-manuscript"
echo "  3. Consider moving details to Supplementary Materials"
```

### 4.3 Section Order Issues

If sections are in non-standard order:

```bash
# The assembler automatically reorders sections based on journal guidelines
# But inform user if original files were in different order

echo "\n✓ Sections reordered according to journal requirements"
echo "  Original order: (from file timestamps)"
echo "  Final order: (from journal guidelines)"
echo "\nNo action needed - assembly handles reordering automatically"
```

---

## Phase 5: Update Workflow State

### 5.1 Mark Assembly Complete

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path('scripts').resolve()))
from rrwrite_state_manager import StateManager

manager = StateManager(output_dir="{target_dir}")

# Read manifest for statistics
import json
manifest_file = Path("{target_dir}") / "assembly_manifest.json"
with open(manifest_file) as f:
    manifest = json.load(f)

# Update assembly stage
manager.update_workflow_stage(
    "assembly",
    status="completed",
    file="{target_dir}/manuscript.md",
    manifest_file="{target_dir}/assembly_manifest.json",
    sections_included=len(manifest['sections_included']),
    sections_missing=len(manifest['sections_missing']),
    total_word_count=manifest['total_word_count'],
    validation_warnings=len(manifest.get('validation_warnings', []))
)

# Update main files tracking
manager.state["files"]["final_manuscript"] = "{target_dir}/manuscript.md"
manager.state["metadata"]["total_word_count"] = manifest['total_word_count']
manager._save_state()

print("✓ Workflow state updated")
```

---

## Phase 6: Display Assembly Summary

### 6.1 Generate Summary Report

```bash
echo "\n{'='*60}"
echo "Assembly Complete"
echo "{'='*60}\n"

echo "Manuscript: {target_dir}/manuscript.md"
echo "Manifest: {target_dir}/assembly_manifest.json"

# Load manifest for summary
TOTAL_WORDS=$(cat "{target_dir}/assembly_manifest.json" | jq -r '.total_word_count')
SECTIONS_INCLUDED=$(cat "{target_dir}/assembly_manifest.json" | jq -r '.sections_included | length')
SECTIONS_MISSING=$(cat "{target_dir}/assembly_manifest.json" | jq -r '.sections_missing | length')

echo "\nStatistics:"
echo "  Total word count: $TOTAL_WORDS words"
echo "  Sections included: $SECTIONS_INCLUDED"
echo "  Sections missing: $SECTIONS_MISSING"

# Journal info
JOURNAL=$(cat "{target_dir}/assembly_manifest.json" | jq -r '.target_journal')
echo "  Target journal: $JOURNAL"
```

### 6.2 Next Steps Guidance

```bash
echo "\nNext Steps:"

if [ $SECTIONS_MISSING -gt 0 ]; then
  echo "  1. ⚠ Draft missing sections (if required)"
  echo "  2. Re-run assembly: /rrwrite-assemble-manuscript"
  echo "  3. Run critique: /rrwrite-critique-manuscript"
else
  echo "  1. ✓ All sections included"
  echo "  2. Run critique: /rrwrite-critique-manuscript"
  echo "  3. Review critique feedback"
  echo "  4. Make final edits"
  echo "  5. Re-assemble if sections were edited"
fi

echo "\nReproducibility:"
echo "  To reassemble manuscript: /rrwrite-assemble-manuscript --target-dir {target_dir}"
echo "  Manifest tracks all assembly details for reproducibility"
```

---

## Phase 7: Verify Reproducibility

### 7.1 Test Reassembly

To verify reproducibility, the manuscript can be reassembled at any time:

```bash
# Reassemble (should produce identical output)
python scripts/rrwrite-assemble-manuscript.py \
  --target-dir "{target_dir}" \
  --output "{target_dir}/manuscript_v2.md"

# Compare outputs
diff "{target_dir}/manuscript.md" "{target_dir}/manuscript_v2.md"

# If no diff output, assembly is reproducible
# (timestamps will differ, but content should be identical)
```

### 7.2 Track Assembly History

Each assembly creates a new manifest with timestamp:

```bash
# Rename manifests to track history
mv "{target_dir}/assembly_manifest.json" \
   "{target_dir}/assembly_manifest_$(date +%Y%m%d_%H%M%S).json"

# Keep latest as assembly_manifest.json for tools
cp "{target_dir}/assembly_manifest_$(date +%Y%m%d_%H%M%S).json" \
   "{target_dir}/assembly_manifest.json"
```

---

## Output Files

### Primary Outputs

1. **`{target_dir}/manuscript.md`**
   - Complete assembled manuscript
   - All sections in correct order
   - Metadata header
   - Assembly manifest as HTML comment at end

2. **`{target_dir}/assembly_manifest.json`**
   - Assembly metadata
   - Sections included/missing
   - Word counts per section
   - Validation warnings
   - Timestamp for reproducibility

### State Updates

3. **`{target_dir}/.rrwrite/state.json`**
   - Assembly stage marked complete
   - Manuscript file path recorded
   - Total word count updated
   - Validation warnings count tracked

---

## Error Handling

### Common Errors

**Error: "No workflow state found"**
- **Cause**: Assembly run before planning
- **Solution**: Run `/rrwrite-plan-manuscript` first

**Error: "No sections have been drafted yet"**
- **Cause**: Assembly run before drafting
- **Solution**: Draft sections with `/rrwrite-draft-section`

**Error: "Manuscript file was not created"**
- **Cause**: Assembly script failed
- **Solution**: Check script output for errors, verify Python dependencies

**Warning: "Required section missing"**
- **Cause**: Journal-required section not drafted
- **Solution**: Draft missing section or proceed with partial manuscript

**Warning: "Word count exceeds limit"**
- **Cause**: Section too long for journal
- **Solution**: Edit section to reduce length, or move content to Supplementary

---

## Validation

### Validate Assembly Structure

```bash
# Check manuscript has all expected components
grep -q "^# " "{target_dir}/manuscript.md" && echo "✓ Has title" || echo "❌ Missing title"
grep -q "Target Journal:" "{target_dir}/manuscript.md" && echo "✓ Has journal" || echo "❌ Missing journal"
grep -q "Total Word Count:" "{target_dir}/manuscript.md" && echo "✓ Has word count" || echo "❌ Missing word count"
grep -q "<!-- Section:" "{target_dir}/manuscript.md" && echo "✓ Has section markers" || echo "❌ Missing sections"
grep -q "<!-- Assembly Manifest" "{target_dir}/manuscript.md" && echo "✓ Has manifest" || echo "❌ Missing manifest"
```

### Validate Manifest Structure

```bash
# Validate JSON
jq empty "{target_dir}/assembly_manifest.json" && echo "✓ Valid JSON" || echo "❌ Invalid JSON"

# Check required fields
jq -e '.assembled_at' "{target_dir}/assembly_manifest.json" > /dev/null && echo "✓ Has timestamp"
jq -e '.target_journal' "{target_dir}/assembly_manifest.json" > /dev/null && echo "✓ Has journal"
jq -e '.sections_included' "{target_dir}/assembly_manifest.json" > /dev/null && echo "✓ Has sections"
jq -e '.total_word_count' "{target_dir}/assembly_manifest.json" > /dev/null && echo "✓ Has word count"
```

---

## Success Criteria

Assembly is successful when:

1. ✅ `manuscript.md` file created with all available sections
2. ✅ Sections in correct order per journal guidelines
3. ✅ Metadata header includes title, authors, journal, word count
4. ✅ Assembly manifest generated with complete metadata
5. ✅ Workflow state updated with assembly completion
6. ✅ Word count validation performed (if guidelines available)
7. ✅ Assembly is reproducible (can be run multiple times with same output)

---

## Notes

- **Idempotent**: Assembly can be run multiple times safely
- **Reproducible**: Manifest tracks exact state of assembly for reproducibility
- **Flexible**: Works with partial manuscripts (missing optional sections)
- **Validated**: Checks word counts against journal limits automatically
- **Ordered**: Uses journal-specific section order from guidelines
- **Tracked**: State manager records assembly completion and statistics

---

## See Also

- `scripts/rrwrite-assemble-manuscript.py` - Assembly script documentation
- `scripts/rrwrite_state_manager.py` - State management
- `.claude/commands/rrwrite.md` - Full pipeline documentation
- `templates/journal_guidelines.yaml` - Journal section order specifications
