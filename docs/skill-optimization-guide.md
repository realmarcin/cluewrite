# Skill Documentation Optimization Guide

Guide for compressing verbose skill documentation while maintaining clarity for power users.

## Token Budget Guidelines

| Skill Frequency | Target Words | Max Words | Rationale |
|-----------------|--------------|-----------|-----------|
| High (draft-section, plan) | 150-200 | 250 | Loaded frequently, optimize aggressively |
| Medium (research, critique) | 250-350 | 450 | Regular use, moderate optimization |
| Low (analyze, assess) | 400-500 | 600 | Infrequent use, can be more detailed |

## Compression Techniques

### 1. Use Tables Instead of Prose

**Before (50 words):**
```markdown
The rrwrite-draft-section skill should be used when you have completed the outline and need to draft a specific section. You can draft sections like abstract, introduction, methods, results, discussion, or availability. This skill enforces citation verification and fact-checking to ensure academic rigor.
```

**After (Table: 25 words):**
```markdown
| Aspect | Details |
|--------|---------|
| Use when | Outline complete, need specific section |
| Sections | abstract, intro, methods, results, discussion, availability |
| Enforces | Citation verification, fact-checking |
```

**Savings: 50%**

### 2. Cross-Reference Shared Docs

**Before (100 words):**
```markdown
### Citation Rules for Methods

When drafting Methods sections, cite ONLY specific tools, datasets, and methodologies that were actually used:

**Appropriate citations:**
- Specific software tools used (e.g., LinkML for schema validation)
- Datasets accessed (e.g., GTDB for taxonomic data)
- Published algorithms implemented

**Inappropriate citations:**
- Abstract principles (FAIR data sharing)
- General best practices papers
- Related tools NOT used in this work

Rationale: Methods describes what YOU did, not general principles.
```

**After (15 words):**
```markdown
### Citation Rules

See `docs/citation-rules-by-section.md` for appropriate citation types per section.
```

**Savings: 85%**

### 3. Inline Simple Commands

**Before (40 words):**
```markdown
To validate the section after drafting, run the validation script with the appropriate parameters. The command should include the file path and document type:

```bash
python scripts/rrwrite-validate-manuscript.py --file {target_dir}/methods.md --type section
```
```

**After (20 words):**
```markdown
Validate: `python scripts/rrwrite-validate-manuscript.py --file {target_dir}/methods.md --type section`
```

**Savings: 50%**

### 4. Remove Redundant Examples

**Before (3 examples, 120 words):**
```markdown
Example 1: Drafting Introduction
...detailed steps...

Example 2: Drafting Methods
...detailed steps...

Example 3: Drafting Results
...detailed steps...
```

**After (1 example + reference, 40 words):**
```markdown
Example: Drafting Methods
...one detailed example...

See `docs/2-5-minute-rule.md` for section-specific templates.
```

**Savings: 67%**

### 5. Condense Command Outputs

**Before (80 words):**
```markdown
After running the command, you will see output like this:

```
✓ Detected previous version: manuscript/project_v1
- Created: 2026-02-05
- Papers: 23
- Status: Research completed

Reuse literature from previous version as starting point?
```

This output shows you the version information and asks if you want to reuse the literature.
```

**After (25 words):**
```markdown
Output shows: version info, paper count, creation date. Prompts to reuse previous literature as base.
```

**Savings: 69%**

### 6. Consolidate Sections

**Before (Multiple small sections, 200 words):**
```markdown
## Purpose
...

## Scope
...

## When to Use
...

## Prerequisites
...

## Requirements
...
```

**After (Combined table, 80 words):**
```markdown
## Quick Reference

| Aspect | Details |
|--------|---------|
| Purpose | Literature research + evidence generation |
| Use when | Outline complete, before drafting |
| Prerequisites | outline.md or PROJECT.md |
| Output | literature.md, evidence.csv, citations.bib |
| Next steps | Draft sections with citations |
```

**Savings: 60%**

## Optimization Priority Order

### Phase 1: Quick Wins (30% reduction)
1. Replace prose with tables for reference information ✓
2. Cross-reference shared docs for citation rules ✓
3. Inline simple commands ✓
4. Remove redundant examples

### Phase 2: Structural (20% reduction)
5. Consolidate small sections into tables
6. Remove verbose explanations (assume power users)
7. Use markdown shortcuts (lists vs. paragraphs)

### Phase 3: Aggressive (10% reduction)
8. Abbreviate common terms (assume domain knowledge)
9. Remove "why" explanations (focus on "what" and "how")
10. Link to external docs for detailed explanations

## Example Optimization: rrwrite-research-literature

### Current Stats
- **Current:** 2599 words
- **Target:** 350 words (medium-frequency skill)
- **Reduction needed:** 2249 words (87%)

### Optimization Strategy

**Section Analysis:**
| Section | Current Words | Optimized Words | Technique |
|---------|---------------|-----------------|-----------|
| Version reuse workflow | 500 | 80 | Table + command inline |
| Search workflow | 800 | 120 | Remove examples, cross-ref |
| DOI extraction | 300 | 50 | Inline commands |
| Evidence file format | 400 | 60 | Table format |
| Output format | 300 | 40 | List instead of prose |
| Total | 2300 | 350 | 85% reduction |

**Optimization Approach:**

**Before (Version Reuse, 500 words):**
```markdown
### Phase 0: Version Reuse Detection (Automatic)

**Purpose:** Detect if a previous manuscript version exists with completed literature research and offer to reuse it as a starting point.

1. **Auto-Detect Previous Version:**
   ```bash
   python scripts/rrwrite_import_evidence_tool.py \
     --detect-only \
     --target-dir {target_dir}
   ```

2. **If Previous Version Found:**
   Display information about the detected version and ask user if they want to reuse the literature:
   [extensive output example]

3. **If User Accepts (Y or blank):**
   [detailed steps A, B, C with examples]
```

**After (Version Reuse, 80 words):**
```markdown
## Workflow

| Phase | Command | Output |
|-------|---------|--------|
| 0: Detect | `python scripts/rrwrite_import_evidence_tool.py --detect-only --target-dir {dir}` | Shows previous versions |
| 1: Import (optional) | `--validate` flag | Imports validated papers, excludes broken DOIs |
| 2: Search | Query outline/PROJECT.md → scholar search | New papers |
| 3: Extract | DOI lookup + CrossRef | evidence.csv with quotes |
| 4: Generate | Format as literature.md | 1-page summary |

**Version reuse:** Imports previous literature, validates DOIs, allows expansion with new papers.
```

**Savings: 84%**

## Template: Optimized Skill Structure (200 words max)

```markdown
---
name: skill-name
description: Use when [trigger]. Do NOT use [anti-pattern]. [Key constraint].
---

# Skill Name

## Quick Reference

| Aspect | Details |
|--------|---------|
| Input | Required files |
| Output | Generated files |
| Validation | Command |
| Next steps | Following skill |

## Core Pattern

```bash
# Minimal command example
command --required-args
```

## Section-Specific Rules (if applicable)

See `docs/[reference].md` for detailed rules.

## Validation Gate

Run: `command --validate`
Requirements: [checklist]

## Common Issues

| Issue | Solution |
|-------|----------|
| Error 1 | Fix 1 |
| Error 2 | Fix 2 |

See `docs/troubleshooting.md` for more.
```

## Skills Requiring Optimization

### High Priority (>1500 words)
1. **rrwrite-research-literature** (2599 → 350 words, 87% reduction)
2. **rrwrite-assemble-manuscript** (1921 → 350 words, 82% reduction)
3. **rrwrite-draft-section** (1657 → 200 words, 88% reduction)
4. **rrwrite-critique-manuscript** (1447 → 350 words, 76% reduction)
5. **rrwrite-assess-journal** (1415 → 450 words, 68% reduction)

### Medium Priority (1000-1500 words)
6. **rrwrite-assemble** (1216 → 350 words, 71% reduction)

### Low Priority (<1000 words)
7. **rrwrite-analyze-repository** (911 → 450 words, 51% reduction)
8. **rrwrite-plan-manuscript** (613 → 200 words, 67% reduction)

## Testing Optimized Skills

### Readability Check
- Power user can understand workflow in <30 seconds
- No critical information missing
- Commands copy-paste ready
- Cross-references accessible

### Functionality Check
- All required commands present
- Validation steps clear
- Error handling documented
- Next steps obvious

### Token Efficiency Check
- Word count within target budget
- No redundant prose
- Tables used for reference data
- Cross-references reduce duplication

## Success Metrics

**Target (across all 8 skills):**
- Current total: ~12,000 words
- Target total: ~2,800 words
- Reduction: 77%
- Token savings: ~9,200 words (~12,000 tokens)

**Per-skill targets:**
| Skill | Current | Target | Reduction |
|-------|---------|--------|-----------|
| research-literature | 2599 | 350 | 87% |
| assemble-manuscript | 1921 | 350 | 82% |
| draft-section | 1657 | 200 | 88% |
| critique-manuscript | 1447 | 350 | 76% |
| assess-journal | 1415 | 450 | 68% |
| assemble | 1216 | 350 | 71% |
| analyze-repository | 911 | 450 | 51% |
| plan-manuscript | 613 | 200 | 67% |
| **Total** | **12,779** | **2,700** | **79%** |

## Implementation Checklist

- [ ] Optimize rrwrite-research-literature (Priority 1)
- [ ] Optimize rrwrite-assemble-manuscript (Priority 1)
- [ ] Optimize rrwrite-draft-section (Priority 1)
- [ ] Optimize rrwrite-critique-manuscript (Priority 1)
- [ ] Optimize rrwrite-assess-journal (Priority 1)
- [ ] Optimize rrwrite-assemble (Priority 2)
- [ ] Optimize rrwrite-analyze-repository (Priority 2)
- [ ] Optimize rrwrite-plan-manuscript (Priority 2)
- [ ] Test all optimized skills for readability
- [ ] Verify no critical information lost
- [ ] Measure actual token reduction
- [ ] Update IMPLEMENTATION_SUMMARY.md with results

## Notes

- Optimization is aggressive for power users
- Beginners may need more verbose documentation (can be separate guide)
- Focus on "what" and "how", not "why" (assume domain knowledge)
- Cross-references are key to reducing duplication
- Tables are more token-efficient than prose for reference information
