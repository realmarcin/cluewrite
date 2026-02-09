# The 2-5 Minute Rule: Task Decomposition for Drafting

Break section drafting into verifiable micro-tasks with clear done conditions.

## Why 2-5 Minutes?

1. **Verifiable:** Each task has clear pass/fail criterion
2. **Resumable:** Can stop and restart at any checkpoint
3. **Debuggable:** Errors isolated to specific micro-task
4. **Motivating:** Frequent completion signals maintain momentum

## Pattern Template

For each micro-task:

```
Task N: [Action] [Component] ([time estimate])
├─ Step 1: Write failing requirement: "[What I need]"
├─ Step 2: [Execute action] with [specific constraints]
├─ Step 3: Verify: [Testable condition]? [Command]
├─ Step 4: [Additional check] → [Expected result] ✓
└─ Checkpoint: [Component] complete and verified
```

## Example: Drafting Methods Section (800 words target)

### Task 1: Data Collection Paragraph (2 min)
- **Step 1:** Write failing requirement: "I need a paragraph describing data sources with citations"
- **Step 2:** Draft 150-200 words with 2-3 citations from evidence file
- **Step 3:** Verify: Do all citations exist in literature_evidence.csv?
  ```bash
  grep "citation_key" manuscript/literature_evidence.csv
  ```
- **Step 4:** Word count check: `wc -w` → 180 words ✓
- **Checkpoint:** Paragraph complete and verified

### Task 2: Analysis Methods Paragraph (3 min)
- **Step 1:** Write failing requirement: "I need a paragraph describing statistical methods with tool citations"
- **Step 2:** Draft 200-250 words with tool citations only (no principles)
- **Step 3:** Verify: Are citations tools not principles? Read each citation abstract
- **Step 4:** Word count check: `wc -w` → 225 words ✓
- **Checkpoint:** Paragraph complete and verified

### Task 3: Validation Paragraph (2 min)
- **Step 1:** Write failing requirement: "I need a paragraph describing validation approach"
- **Step 2:** Draft 150-200 words describing validation methods
- **Step 3:** Verify: Citations are validation tools? Check evidence file
- **Step 4:** Word count check: `wc -w` → 175 words ✓
- **Checkpoint:** Paragraph complete and verified

### Task 4: Reproducibility Paragraph (2 min)
- **Step 1:** Write failing requirement: "I need a paragraph with code/data locations"
- **Step 2:** Draft 100-150 words with URLs and versions
- **Step 3:** Verify: All URLs accessible? Test links
- **Step 4:** Word count check: `wc -w` → 125 words ✓
- **Checkpoint:** Paragraph complete and verified

### Task 5: Final Assembly (1 min)
- **Step 1:** Combine paragraphs in logical order
- **Step 2:** Add section header and transitions
- **Step 3:** Total word count: 180+225+175+125 = 705 words
- **Step 4:** Verify ±20% of target (800 ± 160): 640-960 range ✓
- **Checkpoint:** Section complete, ready for validation

## Progress Tracking

After each task, update state:

```python
from rrwrite_state_manager import StateManager

manager = StateManager(output_dir="manuscript")
manager.update_section_progress(
    section="methods",
    completed_tasks=["data_collection", "analysis_methods"],
    total_tasks=5
)
```

## Failed Verification Recovery

If verification fails at Step 3 or 4:

1. **Don't proceed to next task**
2. **Fix specific issue identified**
3. **Re-run verification**
4. **Only then mark checkpoint complete**

Example:
```
Task 2: Analysis Methods Paragraph (3 min)
├─ Step 3: Verify citations are tools? ❌
│  └─ Found: [Wilkinson2016] is FAIR principles (abstract concept)
├─ FIX: Remove [Wilkinson2016], add [pandas2023] (actual tool used)
├─ Re-verify: All citations are tools? ✓
└─ Checkpoint: NOW complete
```

## Adaptation by Section

### Introduction (500 words)
- Task 1: Background paragraph (2 min, 150 words)
- Task 2: Problem statement (2 min, 150 words)
- Task 3: Related work summary (3 min, 200 words)
- Task 4: Narrative flow check (1 min)

### Results (800 words)
- Task 1: Per finding paragraph (2-3 min each, 150-200 words)
- Task 2: Figure/table callout verification (1 min per figure)
- Task 3: Numerical claim fact-checking (2 min)
- Task 4: Avoid interpretation (1 min review)

### Discussion (700 words)
- Task 1: Summary paragraph (2 min, 150 words)
- Task 2: Interpretation paragraphs (3 min each, 200 words)
- Task 3: Limitation paragraph (2 min, 150 words)
- Task 4: Future work paragraph (2 min, 150 words)

## Anti-Patterns (Don't Do This)

❌ **Monolithic:** "Draft entire Methods section"
- No intermediate checkpoints
- Hard to debug failures
- Unclear progress

❌ **Too Granular:** "Write first sentence of paragraph"
- Too many micro-tasks (overhead)
- No meaningful verification

❌ **Unverifiable:** "Draft good introduction"
- No testable done condition
- Subjective completion

✅ **Just Right:** "Draft data collection paragraph with 2-3 tool citations, 150-200 words"
- Specific deliverable
- Testable criteria (word count, citation type)
- 2-5 minute scope

## Benefits

| Traditional Approach | 2-5 Minute Rule |
|---------------------|-----------------|
| "Draft methods" (20 min) | 5 × 3-min tasks |
| Failed at end → lost 20 min | Failed at Task 2 → lost 3 min |
| Unclear progress | 40% complete (2/5 tasks) |
| Vague "not done yet" | "Stuck on analysis methods paragraph" |
| Hard to resume | Resume at Task 3 |
