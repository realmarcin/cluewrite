---
name: rrwrite-assemble
description: Assembles all manuscript sections into a complete manuscript with validation, metadata generation, figure handling, and optional .docx conversion
arguments:
  - name: target_dir
    description: Output directory containing manuscript sections
    default: manuscript
  - name: include_figures
    description: Copy figures from repository to manuscript/figures directory
    default: true
  - name: convert_docx
    description: Convert assembled manuscript to .docx format for Google Docs import
    default: true
allowed-tools:
context: fork
---
# Manuscript Assembly Protocol

## Purpose
Combine all drafted manuscript sections into a complete manuscript file with validation, metadata generation, figure handling, and optional .docx conversion for Google Docs import.

## Prerequisites
**Required files in {target_dir}:**
- `abstract.md`
- `introduction.md`
- `methods.md`
- `results.md`
- `discussion.md`
- `availability.md` (optional)

**Recommended:**
- `literature_citations.bib` - For citation validation
- `outline.md` - For structure verification

## Workflow

### Phase 1: Pre-Assembly Validation

1. **Check Required Sections:**
   ```bash
   cd {target_dir}

   required_sections=("abstract.md" "introduction.md" "results.md" "discussion.md" "methods.md")
   missing=()

   for section in "${required_sections[@]}"; do
       if [ ! -f "$section" ]; then
           missing+=("$section")
       fi
   done

   if [ ${#missing[@]} -gt 0 ]; then
       echo "Error: Missing required sections: ${missing[*]}"
       exit 1
   fi
   ```

2. **Verify Section Completion:**
   Check workflow state to ensure all sections are marked as completed:
   ```python
   import json
   from pathlib import Path

   state_file = Path("{target_dir}/.rrwrite/state.json")
   if state_file.exists():
       with open(state_file) as f:
           state = json.load(f)

       sections = state.get("workflow_status", {}).get("drafting", {}).get("sections", {})
       incomplete = [s for s, data in sections.items() if data.get("status") != "completed"]

       if incomplete:
           print(f"Warning: Incomplete sections: {incomplete}")
   ```

### Phase 2: Section Assembly with Figure Handling

1. **Run Enhanced Assembly Script:**

   The Python script now handles:
   - Section combination in proper order
   - Figure detection and copying from repository
   - Figure reference normalization in markdown
   - Optional .docx conversion using pandoc

   ```bash
   # Standard assembly (includes figures and .docx conversion by default)
   python scripts/rrwrite-assemble-manuscript.py --output-dir {target_dir}

   # Disable figure copying
   python scripts/rrwrite-assemble-manuscript.py \
       --output-dir {target_dir} \
       --no-include-figures

   # Disable .docx conversion
   python scripts/rrwrite-assemble-manuscript.py \
       --output-dir {target_dir} \
       --no-convert-docx

   # Markdown only (no figures, no .docx)
   python scripts/rrwrite-assemble-manuscript.py \
       --output-dir {target_dir} \
       --no-include-figures \
       --no-convert-docx
   ```

2. **Figure Handling Process:**

   When `--include-figures` is used:
   - Scans repository for figure files (*.png, *.jpg, *.pdf, *.svg, *.eps)
   - Creates `{target_dir}/figures/` directory
   - Copies all detected figures to figures/ subdirectory
   - Normalizes figure references in markdown to use `figures/filename.png`
   - Preserves figures for .docx conversion

   **Example Figure Reference in Sections:**
   ```markdown
   ![Figure 1: Sample visualization](figures/plot.png)

   or with alt text:

   ![Distribution of sample sizes across datasets](figures/distribution.png)
   ```

3. **.docx Conversion Process:**

   When `--convert-docx` is used:
   - Converts assembled markdown to Microsoft Word format
   - Preserves heading styles (H1, H2, etc.)
   - Embeds figures automatically
   - Generates `{target_dir}/manuscript_full.docx`
   - Ready for import into Google Docs with all formatting preserved

### Phase 3: Metadata Generation

1. **Calculate Statistics:**
   ```python
   import re
   from pathlib import Path
   from datetime import datetime
   import json

   target_dir = Path("{target_dir}")
   manuscript_file = target_dir / "manuscript_full.md"

   # Read manuscript
   with open(manuscript_file) as f:
       content = f.read()

   # Count words (exclude markdown headers, code blocks)
   text_only = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
   text_only = re.sub(r'^#.*$', '', text_only, flags=re.MULTILINE)
   text_only = re.sub(r'\[.*?\]', '', text_only)
   words = len(text_only.split())

   # Count citations
   citations = re.findall(r'\[([a-zA-Z0-9,\s]+)\]', content)
   unique_citations = set()
   for cite_group in citations:
       for cite in cite_group.split(','):
           cite = cite.strip()
           if cite and cite[0].islower():  # Citation keys start with lowercase
               unique_citations.add(cite)

   # Count sections
   sections = re.findall(r'^# (.+)$', content, flags=re.MULTILINE)

   # Section word counts
   section_words = {}
   current_section = None
   current_text = []

   for line in content.split('\n'):
       if line.startswith('# '):
           if current_section:
               section_text = ' '.join(current_text)
               section_text = re.sub(r'\[.*?\]', '', section_text)
               section_words[current_section] = len(section_text.split())
           current_section = line[2:].strip()
           current_text = []
       else:
           current_text.append(line)

   if current_section:
       section_text = ' '.join(current_text)
       section_text = re.sub(r'\[.*?\]', '', section_text)
       section_words[current_section] = len(section_text.split())

   # Generate manifest
   manifest = {
       "version": "1.0",
       "generated": datetime.now().isoformat(),
       "manuscript_file": "manuscript_full.md",
       "statistics": {
           "total_words": words,
           "total_sections": len(sections),
           "unique_citations": len(unique_citations),
           "section_breakdown": section_words
       },
       "sections_included": sections,
       "validation": {
           "all_required_sections": True,
           "word_count_target": 3000,  # Nature
           "within_limit": words <= 3500
       }
   }

   # Save manifest
   manifest_file = target_dir / "manifest.json"
   with open(manifest_file, 'w') as f:
       json.dump(manifest, f, indent=2)

   print(f"✓ Generated manifest: {manifest_file}")
   print(f"  Total words: {words}")
   print(f"  Citations: {len(unique_citations)}")
   print(f"  Sections: {len(sections)}")
   ```

### Phase 4: Quality Checks

1. **Check Citation Validity:**
   ```python
   import re
   from pathlib import Path

   target_dir = Path("{target_dir}")
   manuscript_file = target_dir / "manuscript_full.md"
   bib_file = target_dir / "literature_citations.bib"

   # Extract citations from manuscript
   with open(manuscript_file) as f:
       content = f.read()

   cited_keys = set()
   for cite_group in re.findall(r'\[([a-zA-Z0-9,\s]+)\]', content):
       for cite in cite_group.split(','):
           cite = cite.strip()
           if cite and cite[0].islower():
               cited_keys.add(cite)

   # Extract citation keys from .bib file
   if bib_file.exists():
       with open(bib_file) as f:
           bib_content = f.read()

       bib_keys = set(re.findall(r'@\w+\{([^,]+),', bib_content))

       # Check for missing citations
       missing = cited_keys - bib_keys
       if missing:
           print(f"⚠ Warning: Citations not in .bib file: {missing}")
       else:
           print(f"✓ All {len(cited_keys)} citations found in .bib file")
   else:
       print("⚠ Warning: No literature_citations.bib file found")
   ```

2. **Check Word Count Compliance:**
   ```python
   import json
   from pathlib import Path

   target_dir = Path("{target_dir}")
   manifest_file = target_dir / "manifest.json"

   with open(manifest_file) as f:
       manifest = json.load(f)

   total_words = manifest["statistics"]["total_words"]
   target = manifest["validation"]["word_count_target"]

   if total_words > target * 1.2:  # 20% over
       print(f"⚠ Warning: Manuscript is {total_words - target} words over target ({total_words}/{target})")
       print(f"  Recommendation: Trim {total_words - target} words before submission")
   elif total_words < target * 0.8:  # 20% under
       print(f"⚠ Warning: Manuscript is {target - total_words} words under target ({total_words}/{target})")
   else:
       print(f"✓ Word count within acceptable range: {total_words}/{target}")
   ```

### Phase 5: State Update

1. **Update Workflow State:**
   ```python
   import sys
   from pathlib import Path
   sys.path.insert(0, str(Path('scripts').resolve()))
   from rrwrite_state_manager import StateManager
   import json

   target_dir = "{target_dir}"
   manager = StateManager(output_dir=target_dir, enable_git=False)

   # Load manifest for statistics
   manifest_file = Path(target_dir) / "manifest.json"
   with open(manifest_file) as f:
       manifest = json.load(f)

   # Update assembly stage
   manager.update_workflow_stage(
       "assembly",
       status="completed",
       file=f"{target_dir}/manuscript_full.md",
       manifest_file=f"{target_dir}/manifest.json",
       sections_included=manifest["statistics"]["total_sections"],
       total_word_count=manifest["statistics"]["total_words"],
       validation_warnings=0  # TODO: count actual warnings
   )

   print("✓ Workflow state updated")
   ```

## Output Files

The assembly process generates:

1. **`{target_dir}/manuscript_full.md`**
   - Complete manuscript with all sections
   - Section headers and separators
   - Figure references (if --include-figures used)
   - References placeholder

2. **`{target_dir}/manuscript_full.docx`** (if --convert-docx used)
   - Microsoft Word format
   - Preserves heading styles
   - Embedded figures
   - Ready for Google Docs import

3. **`{target_dir}/figures/`** (if --include-figures used)
   - All figure files from repository
   - Referenced by markdown and embedded in .docx

4. **`{target_dir}/manifest.json`**
   - Assembly metadata
   - Word counts per section
   - Citation statistics
   - Validation results

## Validation Criteria

The manuscript is considered successfully assembled if:

✅ All required sections present and combined
✅ Word count statistics calculated
✅ Citations extracted and validated against .bib file
✅ Manifest generated with complete metadata
✅ Workflow state updated to mark assembly as completed

## Display Summary

After successful assembly, display:

```
============================================================
MANUSCRIPT ASSEMBLY COMPLETE
============================================================

Output Files:
  • Markdown: {target_dir}/manuscript_full.md
  • Word format: {target_dir}/manuscript_full.docx (if converted)
  • Figures: {target_dir}/figures/ ([N] files, if included)

Statistics:
  • Total words: [X]
  • Target: [Y] (Nature: 3000 words)
  • Status: [Within limit / Over by X words]
  • Citations: [N] unique citations
  • Sections: [M] sections included

Section Breakdown:
  • Abstract: [X] words
  • Introduction: [X] words
  • Results: [X] words
  • Discussion: [X] words
  • Methods: [X] words
  • Availability: [X] words

Next Steps:
  1. Review manuscript_full.md (or open manuscript_full.docx)
  2. Import to Google Docs:
     - Go to https://docs.google.com
     - File > Open > Upload
     - Select manuscript_full.docx
  3. Run critique:
     /rrwrite-critique-manuscript --target-dir {target_dir} --file manuscript_full.md
  4. Address critique feedback
  5. Trim to target word count if needed

============================================================
```

## Error Handling

**Missing sections:**
```
Error: Missing required sections: [list]
Please draft all sections before assembly:
  /rrwrite-draft-section --target-dir {target_dir} --section [name]
```

**No sections found:**
```
Error: No manuscript sections found in {target_dir}
Expected files: abstract.md, introduction.md, results.md, discussion.md, methods.md
```

**Invalid target directory:**
```
Error: Target directory not found: {target_dir}
Please specify a valid manuscript directory
```

## Notes

- Assembly does NOT modify individual section files
- Original sections remain unchanged in {target_dir}
- Manifest can be regenerated by re-running assembly
- Word counts exclude markdown formatting and citations
- Nature format uses Abstract → Intro → Results → Discussion → Methods order
- For other journals (PLOS, Bioinformatics), adjust section order as needed
