# Author Guidelines Integration for RRWrite Skills

This document provides integration guidance for RRWrite skills to use author guidelines fetched by the `rrwrite-assess-journal` skill.

## Overview

After the journal assessment step completes, two key files are available:
- `{target_dir}/author_guidelines.md` - Comprehensive journal-specific guidelines
- `{target_dir}/journal_assessment.md` - Compatibility analysis and recommendations

All downstream skills (research, drafting, critique) should load and apply these guidelines.

---

## Integration Pattern for All Skills

### 1. Check for Guidelines File

```python
from pathlib import Path

def load_guidelines(target_dir: str) -> dict:
    """Load author guidelines if available."""
    guidelines_file = Path(target_dir) / "author_guidelines.md"

    if not guidelines_file.exists():
        print("⚠ No author guidelines found. Run /rrwrite-assess-journal first.")
        return None

    # Parse guidelines markdown file
    guidelines_text = guidelines_file.read_text()

    return {
        "text": guidelines_text,
        "path": str(guidelines_file)
    }
```

### 2. Extract Relevant Information

Parse the guidelines markdown to extract:
- **Word Limits**: For each section and total manuscript
- **Citation Rules**: Section-specific citation guidelines
- **Special Requirements**: Journal-specific mandatory elements
- **Scope Keywords**: For filtering research papers
- **Structural Requirements**: Required sections and order

---

## Skill-Specific Integration

### rrwrite-research-literature

**File**: `.claude/skills/rrwrite-research-literature/SKILL.md`

**Integration Point**: After extracting topics, before conducting literature searches

#### Add Phase 1.5: Load Journal Guidelines

```markdown
## Phase 1.5: Load Journal Guidelines (NEW)

Before conducting searches, load journal scope from assessment:

```bash
# Check if assessment was run
if [ -f "{target_dir}/author_guidelines.md" ]; then
  echo "✓ Journal guidelines available - filtering by journal scope"
  # Extract scope section
  SCOPE_KEYWORDS=$(grep -A 20 "## Scope" {target_dir}/author_guidelines.md)
fi
```

**Extract journal scope keywords** from the "Scope" section of author_guidelines.md.

Example scope keywords for Bioinformatics:
- computational biology methods
- bioinformatics algorithms
- sequence analysis
- systems biology
- database development
- software tools

**Apply to searches**:
- Include journal-relevant papers (match scope keywords)
- Exclude out-of-scope papers (e.g., don't search "clinical trials" for Bioinformatics)
- Prioritize papers published in target journal (higher relevance)
- Use scope keywords to refine search queries

**Example Modifications**:

**Before guidelines:**
```python
search_query = f"{topic} computational method"
```

**After guidelines:**
```python
# Load scope keywords from guidelines
scope = extract_scope_keywords(guidelines)  # ['bioinformatics', 'algorithm', 'software']

# Enhance search query with scope keywords
search_query = f"{topic} {' OR '.join(scope[:3])}"
# Result: "protein structure bioinformatics OR algorithm OR software"
```

**Benefits:**
- Literature is pre-filtered for journal relevance
- Reduces citations to out-of-scope papers
- Improves manuscript fit with journal expectations
```

---

### rrwrite-draft-section

**File**: `.claude/skills/rrwrite-draft-section/SKILL.md`

**Integration Point**: Before drafting ANY section

#### Add to Section-Specific Guidelines

```markdown
### All Sections: Journal-Specific Guidelines (MANDATORY)

**Before drafting ANY section**, load and apply journal-specific guidelines:

```bash
# Load guidelines if available
GUIDELINES_FILE="{target_dir}/author_guidelines.md"

if [ -f "$GUIDELINES_FILE" ]; then
  echo "✓ Loading journal guidelines for section-specific requirements"

  # Extract section-specific word limits
  WORD_LIMITS=$(grep -A 10 "## Word Limits" "$GUIDELINES_FILE")

  # Extract citation rules for this section
  CITATION_RULES=$(grep -A 30 "## Citation Guidelines by Section" "$GUIDELINES_FILE")

  # Extract special requirements
  SPECIAL_REQS=$(grep -A 20 "## Special Requirements" "$GUIDELINES_FILE")

  echo "Applying guidelines during drafting..."
else
  echo "⚠ No guidelines found - using default formatting"
fi
```

**Apply the following from guidelines:**

#### 1. Word Count Limits

Extract and enforce section-specific word limits:

**Example for Introduction section:**
```
Introduction: 500-1500 words
```

**Implementation:**
- Draft within the specified range
- Use lower bound as minimum target
- Use upper bound as hard limit
- If text exceeds limit, edit down before finalizing

#### 2. Citation Style

Extract citation style from guidelines:
- **numbered**: Use [1], [2], [3] format
- **author-year**: Use (Smith et al., 2023) format

Apply consistently throughout section.

#### 3. Section-Specific Citation Rules

Guidelines specify what to cite in each section:

**Introduction:**
- Cite previous methods being improved upon
- Cite related computational approaches
- Avoid excessive background citations

**Methods:**
- Cite algorithms and statistical methods used
- Cite software dependencies and libraries
- Cite data sources and datasets

**Results:**
- Cite benchmark datasets
- Cite compared tools and methods
- Minimal review citations

**Discussion:**
- Cite papers for comparison and context
- Cite future directions if building on prior work

**Apply these rules:** Only cite papers that match the section's citation rules.

#### 4. Special Requirements

Some journals have unique requirements:

**Nature Methods:**
- Methods section goes at END, not beginning
- Keep Methods citations minimal
- Move extensive methods to Supplementary (not drafted)

**PLOS Computational Biology:**
- Include Author Summary section (non-technical)
- Emphasize biological insight in all sections
- Comprehensive Data Availability required

**Bioinformatics:**
- Software must cite original publications
- Include Data and Code Availability statement
- Compare with at least 2 existing tools

**Check for journal-specific notes** in the Special Requirements section and apply them.

#### 5. Formatting Constraints

Reference limits, figure limits, etc.:
```
- Reference limit: 50
- Figure limit: 6
- Table limit: 4
```

Track counts during drafting and stay within limits.

---

### Example Integration in Draft Phase

```markdown
## Phase 2: Draft Content (Enhanced)

### Load Guidelines First

```python
from pathlib import Path

# Load guidelines
guidelines_file = Path(f"{target_dir}/author_guidelines.md")
guidelines = {}

if guidelines_file.exists():
    guidelines_text = guidelines_file.read_text()

    # Extract word limits for this section
    import re
    word_limit_match = re.search(
        rf'\*\*{section_name.title()}\*\*:\s*(\d+)-(\d+)\s*words',
        guidelines_text,
        re.IGNORECASE
    )

    if word_limit_match:
        guidelines['min_words'] = int(word_limit_match.group(1))
        guidelines['max_words'] = int(word_limit_match.group(2))
        print(f"✓ Word limit: {guidelines['min_words']}-{guidelines['max_words']} words")

    # Extract citation rules for this section
    citation_section = re.search(
        rf'\*\*{section_name.title()}\*\*:([^\*]+)',
        guidelines_text,
        re.IGNORECASE
    )

    if citation_section:
        guidelines['citation_rules'] = citation_section.group(1).strip()
        print(f"✓ Citation rules: {guidelines['citation_rules'][:100]}...")
```

### Apply During Drafting

Use the loaded guidelines to:
1. Target the word count range
2. Apply citation rules when adding references
3. Format according to journal style
4. Include any special requirements

### Validate Before Finalizing

```python
# Check word count
word_count = len(section_text.split())

if guidelines.get('max_words'):
    if word_count > guidelines['max_words']:
        print(f"⚠ WARNING: Section exceeds limit ({word_count} > {guidelines['max_words']})")
        # Trigger editing phase to reduce length
    elif word_count < guidelines.get('min_words', 0):
        print(f"⚠ WARNING: Section below minimum ({word_count} < {guidelines['min_words']})")
        # Suggest expanding content
    else:
        print(f"✓ Word count within limits: {word_count} words")
```

---

### rrwrite-critique-manuscript

**File**: `.claude/skills/rrwrite-critique-manuscript/SKILL.md`

**Integration Point**: Add new critique category (#7)

#### Add Guideline Compliance Check

```markdown
## Critique Categories (Updated)

### 7. Author Guidelines Compliance (NEW)

**Purpose**: Verify manuscript complies with all journal-specific requirements

**Check if guidelines exist:**
```bash
GUIDELINES_FILE="{target_dir}/author_guidelines.md"

if [ ! -f "$GUIDELINES_FILE" ]; then
  echo "⚠ No author guidelines found - skipping compliance check"
  echo "   Run /rrwrite-assess-journal to fetch guidelines"
else
  echo "✓ Validating against author guidelines..."
fi
```

**Validation Checklist:**

#### 7.1 Structural Compliance

**Required Sections:**
- Extract "Required Sections" from guidelines
- Verify all are present in manuscript
- **VIOLATION**: Flag as MAJOR if any required section missing

Example:
```
❌ MAJOR: Missing required section 'Data Availability' (required by Bioinformatics)
```

**Section Order:**
- Extract "Recommended Section Order" from guidelines
- Compare against actual manuscript structure
- **VIOLATION**: Flag as MINOR if order is non-standard

Example:
```
⚠ MINOR: Section order differs from journal recommendation
   Expected: Introduction → Methods → Results → Discussion
   Actual: Introduction → Results → Methods → Discussion
   Note: Nature Methods places Methods at END
```

#### 7.2 Word Count Compliance

**Total Word Count:**
- Extract "Total" word limit from guidelines
- Count words in all sections (exclude references, acknowledgments)
- **VIOLATION**: Flag as MAJOR if >10% over limit

Example:
```
❌ MAJOR: Total word count exceeds limit by 15%
   Actual: 5750 words
   Limit: 5000 words (Nature Methods)
   Action: Reduce by 750 words
```

**Section Word Counts:**
- Extract word limits for each section
- Count words in each section
- **VIOLATION**: Flag as MINOR if section exceeds by <20%, MAJOR if >20%

Example:
```
⚠ MINOR: Methods section exceeds recommended length
   Actual: 2200 words
   Recommended: 1000-2000 words
   Consider moving details to Supplementary
```

#### 7.3 Citation Compliance

**Citation Style:**
- Extract "Citation Style" from guidelines
- Check all citations match format (numbered vs. author-year)
- **VIOLATION**: Flag as MAJOR if inconsistent style used

Example:
```
❌ MAJOR: Citations must use numbered format [1], [2]
   Found: Author-year format in Introduction (Smith et al., 2023)
   Journal: Bioinformatics requires numbered citations
```

**Reference Count:**
- Extract "Reference Limit" from guidelines
- Count total references
- **VIOLATION**: Flag as MAJOR if exceeds limit

Example:
```
❌ MAJOR: Reference count exceeds journal limit
   Actual: 65 references
   Limit: 50 references (Bioinformatics)
   Action: Remove 15 references, prioritize most relevant
```

**Section-Specific Citation Rules:**
- Extract citation rules for each section
- Validate citations in each section follow the rules
- **VIOLATION**: Flag as MINOR if inappropriate citations

Example:
```
⚠ MINOR: Results section contains review citations
   Found: 3 review papers cited in Results
   Guideline: "Results - Minimal review citations" (Bioinformatics)
   Action: Move reviews to Introduction or Discussion
```

#### 7.4 Special Requirements

**Journal-Specific Elements:**
- Extract all items from "Special Requirements" section
- Check if each is addressed in manuscript
- **VIOLATION**: Flag as MAJOR if mandatory requirement missing

Examples:
```
❌ MAJOR: Missing Author Summary section
   Required by: PLOS Computational Biology
   Description: Non-technical summary for broad audience (100-200 words)
   Action: Add Author Summary after Abstract

❌ MAJOR: Software availability not specified
   Required by: Bioinformatics
   Must include: Operating system, license, restrictions
   Action: Add "Availability and Requirements" section

⚠ MINOR: No comparison with existing tools
   Recommended by: Bioinformatics ("Compare with at least 2 existing tools")
   Action: Add benchmarking results to Results section
```

#### 7.5 Formatting Requirements

**Figures and Tables:**
- Extract limits from guidelines
- Count figures and tables in manuscript
- **VIOLATION**: Flag as MAJOR if exceeds limits

Example:
```
❌ MAJOR: Too many figures
   Actual: 8 figures
   Limit: 6 figures (Nature Methods)
   Action: Move 2 figures to Supplementary
```

---

### Implementation Template

```python
def validate_guidelines_compliance(target_dir, manuscript_sections):
    """Validate manuscript against author guidelines."""

    guidelines_file = Path(target_dir) / "author_guidelines.md"

    if not guidelines_file.exists():
        return {
            "status": "skipped",
            "message": "No author guidelines found"
        }

    guidelines_text = guidelines_file.read_text()
    issues = []

    # 1. Check required sections
    required_sections = extract_required_sections(guidelines_text)
    for section in required_sections:
        if section not in manuscript_sections:
            issues.append({
                "severity": "MAJOR",
                "category": "Structure",
                "message": f"Missing required section: {section}",
                "guideline": get_journal_name(guidelines_text)
            })

    # 2. Check word counts
    word_limits = extract_word_limits(guidelines_text)
    for section, content in manuscript_sections.items():
        word_count = len(content.split())
        limits = word_limits.get(section)

        if limits and 'max' in limits:
            if word_count > limits['max']:
                overage_pct = (word_count - limits['max']) / limits['max'] * 100
                severity = "MAJOR" if overage_pct > 20 else "MINOR"

                issues.append({
                    "severity": severity,
                    "category": "Word Count",
                    "message": f"{section} exceeds limit: {word_count} words (max: {limits['max']})",
                    "suggestion": f"Reduce by {word_count - limits['max']} words"
                })

    # 3. Check citation style
    citation_style = extract_citation_style(guidelines_text)
    if not validate_citation_style(manuscript_sections, citation_style):
        issues.append({
            "severity": "MAJOR",
            "category": "Citations",
            "message": f"Citations must use {citation_style} format",
            "guideline": "Check all citation formats for consistency"
        })

    # 4. Check special requirements
    special_reqs = extract_special_requirements(guidelines_text)
    for req in special_reqs:
        if not is_requirement_met(manuscript_sections, req):
            issues.append({
                "severity": "MAJOR",
                "category": "Special Requirements",
                "message": req,
                "action": "Address this journal-specific requirement"
            })

    return {
        "status": "completed",
        "issues": issues,
        "total_issues": len(issues),
        "major_issues": len([i for i in issues if i["severity"] == "MAJOR"]),
        "minor_issues": len([i for i in issues if i["severity"] == "MINOR"])
    }
```

---

## Testing Integration

### Test Checklist

For each skill, verify:

1. **Guidelines Loading**
   - [ ] Skill checks for `{target_dir}/author_guidelines.md`
   - [ ] Skill parses guidelines correctly
   - [ ] Skill handles missing guidelines gracefully

2. **Guidelines Application**
   - [ ] Relevant sections extracted from guidelines
   - [ ] Guidelines applied during skill execution
   - [ ] Compliance validated before completion

3. **Error Handling**
   - [ ] Clear warning if guidelines missing
   - [ ] Suggestion to run assessment first
   - [ ] Skill continues with defaults if no guidelines

4. **Validation**
   - [ ] Output conforms to guidelines
   - [ ] Violations flagged appropriately
   - [ ] User notified of compliance status

### Example Test Cases

**Test 1: Guidelines Available**
```bash
# Setup
/rrwrite-assess-journal --target-dir test_output --initial-journal bioinformatics

# Test drafting with guidelines
/rrwrite-draft-section introduction --target-dir test_output

# Verify
# - Introduction is 500-1500 words (Bioinformatics limit)
# - Citations are numbered format
# - Computational methods emphasized
```

**Test 2: No Guidelines**
```bash
# Test drafting without guidelines
/rrwrite-draft-section introduction --target-dir test_output_no_guidelines

# Expected
# - Warning: "No author guidelines found"
# - Section drafted with default formatting
# - Suggestion to run assessment
```

**Test 3: Compliance Validation**
```bash
# Setup with guidelines
/rrwrite-assess-journal --target-dir test_output --initial-journal nature_methods

# Draft sections
/rrwrite-draft-section methods --target-dir test_output

# Critique
/rrwrite-critique-manuscript --target-dir test_output

# Verify
# - Critique flags if Methods section not at end
# - Word count validated against 3000-word limit
# - Reference count checked against 60 limit
```

---

## Summary

**Key Integration Points:**
1. **rrwrite-research-literature**: Filter papers by journal scope
2. **rrwrite-draft-section**: Apply word limits, citation rules, special requirements
3. **rrwrite-critique-manuscript**: Validate full compliance with all guidelines

**Benefits:**
- Manuscripts comply with journal requirements from the start
- Reduces revision cycles
- Increases acceptance probability
- Ensures consistency across all sections

**Implementation Status:**
- ✓ Assessment skill fetches guidelines
- ✓ Guidelines stored in accessible format
- ⏳ Downstream skills need integration (this document provides guidance)
- ⏳ Testing and validation pending
