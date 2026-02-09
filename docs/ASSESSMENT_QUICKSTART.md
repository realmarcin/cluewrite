# Journal Assessment - Quick Start Guide

Get started with the RRWrite journal assessment feature in 5 minutes.

---

## What is Journal Assessment?

Journal assessment is a new step in the RRWrite pipeline that:
- **Analyzes** your outline's fit with a target journal
- **Recommends** alternative journals if a better match exists
- **Fetches** comprehensive author guidelines
- **Ensures** guidelines are followed throughout drafting

---

## Quick Example

```bash
# 1. Plan your manuscript (as usual)
/rrwrite-plan-manuscript --target-dir manuscript/my_repo_v1 --journal bioinformatics

# 2. Run assessment (NEW STEP)
/rrwrite-assess-journal --target-dir manuscript/my_repo_v1 --initial-journal bioinformatics

# The skill will:
# - Analyze compatibility (shows score 0.0-1.0)
# - Recommend alternatives if needed
# - Ask you to confirm or switch journal
# - Fetch comprehensive guidelines

# 3. Continue with rest of pipeline
/rrwrite-research-literature --target-dir manuscript/my_repo_v1
/rrwrite-draft-section introduction --target-dir manuscript/my_repo_v1
# ... etc
```

---

## What Happens During Assessment?

### Step 1: Compatibility Analysis
```
Analyzing compatibility with Bioinformatics...
✓ Keyword Analysis: 85% match
✓ Structural Alignment: 80% match
✓ Overall Compatibility: 0.83 (GOOD MATCH)
```

### Step 2: Recommendations (if score < 0.7)
```
Your outline scores 0.62 with Bioinformatics
Consider these alternatives:

1. PLOS Computational Biology (0.92)
   - Emphasizes biological insight
   - Better fit for systems biology content

2. BMC Bioinformatics (0.78)
   - More flexible scope
   - Allows hybrid experimental/computational
```

### Step 3: User Confirmation
```
Select journal:
[ ] Keep Bioinformatics (compatibility: 0.83)
[X] Switch to PLOS Computational Biology (Recommended - 0.92)
[ ] Switch to BMC Bioinformatics (Alternative - 0.78)
```

### Step 4: Guidelines Fetched
```
✓ Fetching author guidelines for PLOS Computational Biology...
✓ Guidelines saved to: manuscript/my_repo_v1/author_guidelines.md

Key Requirements:
- Author Summary required (100-200 words, non-technical)
- Total word limit: 4000-10000 words
- Numbered citations required
- Data Availability statement mandatory
```

---

## Interpreting Compatibility Scores

| Score | Meaning | Action |
|-------|---------|--------|
| **0.75-1.00** | Excellent match | ✅ Proceed with confidence |
| **0.60-0.74** | Good match | ✅ Minor adjustments may help |
| **0.45-0.59** | Moderate match | ⚠️ Consider alternatives |
| **0.00-0.44** | Poor match | ❌ Strongly recommend switching |

---

## Supported Journals

Currently supported journals (7 total):

1. **Bioinformatics** (Oxford)
   - Computational methods, algorithms, software tools
   - Word limit: 3000-7000 words

2. **Nature Methods** (Nature)
   - Novel methods with broad applicability
   - Word limit: 3000-5000 words (strict)

3. **PLOS Computational Biology** (PLOS)
   - Biological insight emphasis
   - No strict word limit

4. **BMC Bioinformatics** (BMC)
   - Flexible scope, open access
   - Word limit: 3000-8000 words

5. **Genome Biology** (BMC)
   - Genome-scale studies
   - Word limit: 4000-8000 words

6. **Cell Systems** (Cell Press)
   - Systems biology, multi-omics
   - Word limit: 4000-7000 words

7. **Nucleic Acids Research** (Oxford)
   - Nucleic acids, databases, tools
   - Word limit: 4000-9000 words

---

## Output Files

Assessment creates two files:

### 1. `journal_assessment.md`
Assessment report with:
- Compatibility analysis
- Keyword matches
- Structural alignment
- Recommendations
- User decision rationale

### 2. `author_guidelines.md`
Comprehensive guidelines with:
- Journal scope
- Required sections and order
- Word limits (total + per-section)
- Citation rules
- Special requirements
- Compliance checklist

---

## Using Guidelines in Downstream Steps

### During Literature Research
- Papers filtered by journal scope
- Out-of-scope research excluded
- Target journal papers prioritized

### During Drafting
- Word limits enforced per section
- Citation rules applied automatically
- Special requirements followed
- Journal-specific formatting used

### During Critique
- Compliance validated automatically
- Violations flagged by severity
- Guideline-specific checks added

---

## Common Scenarios

### Scenario 1: High Compatibility
```bash
/rrwrite-assess-journal --target-dir manuscript/repo_v1 --initial-journal bioinformatics

# Output:
# ✓ Compatibility: 0.87 (EXCELLENT)
# User confirms: Keep Bioinformatics
# → Continue with confidence
```

### Scenario 2: Low Compatibility, User Switches
```bash
/rrwrite-assess-journal --target-dir manuscript/repo_v1 --initial-journal bioinformatics

# Output:
# ⚠ Compatibility: 0.58 (MODERATE)
# Recommended: PLOS Computational Biology (0.93)
# User confirms: Switch to PLOS Comp Biol
# → Guidelines updated, journal changed
```

### Scenario 3: Low Compatibility, User Keeps Original
```bash
/rrwrite-assess-journal --target-dir manuscript/repo_v1 --initial-journal bioinformatics

# Output:
# ⚠ Compatibility: 0.55 (MODERATE)
# Recommended: Nature Methods (0.82)
# User confirms: Keep Bioinformatics anyway
# → Proceeds with original journal (user choice respected)
```

---

## Troubleshooting

### Problem: "No workflow state found"
**Solution**: Run planning first
```bash
/rrwrite-plan-manuscript --target-dir manuscript/repo_v1 --journal bioinformatics
```

### Problem: "Journal not found in database"
**Solution**: Check available journals
```bash
# View all journals
cat templates/journal_guidelines.yaml | grep "^  [a-z_]*:"
```

### Problem: Score seems incorrect
**Solution**: Review outline content
- Check if outline uses journal-relevant terminology
- Verify required sections are present
- Run with verbose flag to see detailed analysis

---

## Advanced Usage

### Compare All Journals
```bash
python scripts/rrwrite-recommend-journal.py \
  --outline manuscript/repo_v1/outline.md \
  --guidelines templates/journal_guidelines.yaml \
  --top 7 \
  --show-scores
```

### View Guidelines Without Assessment
```bash
python scripts/rrwrite-fetch-guidelines.py \
  --journal nature_methods \
  --guidelines templates/journal_guidelines.yaml \
  --output preview.md
```

### Re-assess After Outline Changes
```bash
# If you significantly revise your outline
/rrwrite-assess-journal \
  --target-dir manuscript/repo_v1 \
  --initial-journal bioinformatics
# → Re-analyzes compatibility with updated outline
```

### Check Assessment Status
```bash
python scripts/rrwrite-status.py --output-dir manuscript/repo_v1

# Shows:
# ✓ Journal Assessment: COMPLETED
#    Compatibility: 85% (0.85/1.00)
#    Guidelines: manuscript/repo_v1/author_guidelines.md
```

---

## Tips for Best Results

### 1. Run Early
- Run assessment **immediately after planning**
- Don't wait until after drafting starts
- Easier to switch journals before writing begins

### 2. Review Recommendations
- Don't ignore low scores
- Consider alternative journals seriously
- Better to switch early than rewrite later

### 3. Read Guidelines
- Review `author_guidelines.md` before drafting
- Pay attention to special requirements
- Use compliance checklist as guide

### 4. Trust the Process
- Assessment uses data-driven analysis
- Compatibility scores are calibrated
- Recommendations based on objective criteria

---

## When to Skip Assessment

Assessment is **optional** but recommended. You might skip it if:
- You're 100% confident in journal choice
- You're writing for a journal not in the database
- You're drafting an internal document

However, **we strongly recommend** running assessment because:
- ✅ Takes only 2-3 minutes
- ✅ Prevents costly rewrites
- ✅ Improves acceptance probability
- ✅ Ensures guideline compliance

---

## Getting Help

### View Assessment Skill Help
```bash
/rrwrite-assess-journal --help
```

### View Full Pipeline Documentation
```bash
cat .claude/commands/rrwrite.md
```

### View Integration Guide
```bash
cat docs/GUIDELINES_INTEGRATION.md
```

### View Implementation Details
```bash
cat docs/IMPLEMENTATION_SUMMARY.md
```

---

## Next Steps

After successful assessment:

1. **Review guidelines** in `author_guidelines.md`
2. **Continue pipeline** with literature research
3. **Draft sections** with guidelines in mind
4. **Run critique** to validate compliance
5. **Check status** to track progress

---

**Ready to get started?**

```bash
/rrwrite-assess-journal --target-dir manuscript/your_repo_v1 --initial-journal bioinformatics
```

Happy writing! 🚀
