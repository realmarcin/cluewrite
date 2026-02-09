---
name: rrwrite-assess-journal
description: Analyzes manuscript outline for journal suitability, recommends optimal journal, and fetches author guidelines
arguments:
  - name: target_dir
    description: Output directory for manuscript files
    default: manuscript
  - name: initial_journal
    description: Initially selected journal from planning phase
    default: bioinformatics
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
---

# RRWrite: Journal Assessment

You are an agent within the RRWrite (Repo-Research-Writer) manuscript generation system. This skill performs comprehensive journal suitability analysis and author guidelines retrieval.

## Objectives

1. Load manuscript outline and journal database
2. Analyze compatibility with initially selected journal
3. Recommend alternative journals if compatibility is low
4. Confirm journal selection with user
5. Fetch comprehensive author guidelines
6. Generate assessment report
7. Update workflow state
8. Display completion status

## Input Requirements

- `target_dir`: Directory containing workflow state and outline (default: manuscript)
- `initial_journal`: Journal identifier from planning phase (default: bioinformatics)

## Process Flow

### Phase 1: Load Outline and Journal Database

**Goal:** Load manuscript outline and verify journal database availability.

**Actions:**
1. Read workflow state from `{target_dir}/workflow_state.md`
2. Extract outline from workflow state (section: `## OUTLINE`)
3. Verify journal guidelines database exists at `templates/journal_guidelines.yaml`
4. If database missing, report error and exit
5. Display loaded outline summary (section count, approximate length)

**Success Criteria:**
- Workflow state loaded successfully
- Outline extracted and validated
- Journal database accessible

---

### Phase 2: Analyze Compatibility

**Goal:** Score initial journal compatibility and identify potential issues.

**Actions:**
1. Execute journal scope matcher:
   ```bash
   python3 scripts/rrwrite-match-journal-scope.py \
     --outline {target_dir}/workflow_state.md \
     --journal {initial_journal} \
     --guidelines templates/journal_guidelines.yaml \
     --verbose
   ```

2. Parse JSON output and extract:
   - Compatibility score (0.0-1.0)
   - Keyword score and matches
   - Structure score and missing sections
   - Recommendations

3. Display analysis summary:
   ```
   Journal Compatibility Analysis
   ==============================
   Target Journal: {journal_name}
   Compatibility Score: {score}/1.0

   Keyword Analysis:
   - Positive matches: {count} ({list top 5})
   - Negative matches: {count} ({list all})
   - Keyword score: {score}/1.0

   Structure Analysis:
   - Required sections present: {count}/{total}
   - Missing sections: {list all}
   - Structure score: {score}/1.0

   Recommendations:
   {list all recommendations}
   ```

**Success Criteria:**
- Compatibility score calculated
- Analysis results displayed to user

---

### Phase 3: Recommend Alternatives (if score < 0.7)

**Goal:** Provide alternative journal recommendations if compatibility is low.

**Actions:**
1. If compatibility score >= 0.7, skip this phase
2. If compatibility score < 0.7:
   ```bash
   python3 scripts/rrwrite-recommend-journal.py \
     --outline {target_dir}/workflow_state.md \
     --guidelines templates/journal_guidelines.yaml \
     --top 3 \
     --show-scores
   ```

3. Parse recommendations and display:
   ```
   Alternative Journal Recommendations
   ===================================

   1. {journal_name} (Score: {score}/1.0)
      {explanation}

   2. {journal_name} (Score: {score}/1.0)
      {explanation}

   3. {journal_name} (Score: {score}/1.0)
      {explanation}
   ```

4. Include guidance:
   ```
   The initially selected journal ({initial_journal}) has low compatibility.
   Consider one of the alternatives above, or adjust the manuscript scope.
   ```

**Success Criteria:**
- Alternative recommendations generated (if needed)
- User informed of better options

---

### Phase 4: Confirm Journal Selection

**Goal:** Get user confirmation of final journal selection.

**Actions:**
1. If compatibility score >= 0.7:
   - Use AskUserQuestion to confirm continuing with initial journal
   - Question: "Proceed with {journal_name}? (y/n or specify alternative journal ID)"

2. If compatibility score < 0.7:
   - Use AskUserQuestion to get journal selection
   - Question: "Select journal (enter journal ID from recommendations or '{initial_journal}' to proceed anyway):"

3. Parse user response:
   - If 'y' or 'yes': use initial_journal
   - If 'n' or 'no': prompt for journal ID
   - If journal ID provided: validate and use it

4. Validate final journal selection exists in database

5. Store confirmed journal in variable `{selected_journal}`

**Success Criteria:**
- User has confirmed journal selection
- Selected journal is valid and in database

**IMPORTANT:** Use the AskUserQuestion tool for user interaction. Do NOT proceed without explicit user confirmation.

---

### Phase 5: Fetch Comprehensive Guidelines

**Goal:** Retrieve detailed author guidelines for selected journal.

**Actions:**
1. Execute guidelines fetcher:
   ```bash
   python3 scripts/rrwrite-fetch-guidelines.py \
     --journal {selected_journal} \
     --guidelines templates/journal_guidelines.yaml \
     --output {target_dir}/journal_guidelines.md
   ```

2. Verify guidelines file created successfully

3. Read generated guidelines and extract key sections:
   - Word limits
   - Required sections
   - Special requirements
   - Citation rules

4. Display guidelines summary:
   ```
   Author Guidelines Retrieved
   ==========================
   Journal: {journal_name}
   Guidelines saved to: {target_dir}/journal_guidelines.md

   Key Requirements:
   - Total word limit: {min}-{max} words
   - Required sections: {count}
   - Citation style: {style}
   - Reference limit: {limit}
   - Special requirements: {count} items

   See full guidelines in journal_guidelines.md
   ```

**Success Criteria:**
- Guidelines file generated at `{target_dir}/journal_guidelines.md`
- Key requirements extracted and displayed

---

### Phase 6: Generate Assessment Report

**Goal:** Create comprehensive assessment report for workflow tracking.

**Actions:**
1. Create assessment report at `{target_dir}/journal_assessment.md` with:

   ```markdown
   # Journal Assessment Report

   **Date:** {current_date}
   **Selected Journal:** {journal_name}
   **Journal ID:** {selected_journal}

   ## Compatibility Analysis

   - **Overall Score:** {compatibility_score}/1.0
   - **Keyword Score:** {keyword_score}/1.0
   - **Structure Score:** {structure_score}/1.0

   ### Positive Keyword Matches
   {list all positive matches}

   ### Negative Keyword Matches
   {list all negative matches or "None"}

   ### Structural Alignment
   - **Present Sections:** {list}
   - **Missing Sections:** {list or "None"}

   ## Recommendations
   {list all recommendations from analysis}

   ## Alternative Journals Considered
   {list alternatives if any were generated}

   ## User Decision
   {describe user's selection decision}

   ## Next Steps
   1. Review full author guidelines in journal_guidelines.md
   2. Ensure outline includes all required sections
   3. Plan content to meet word limits and formatting requirements
   4. Follow section-specific citation rules during writing
   ```

2. Verify report created successfully

**Success Criteria:**
- Assessment report created at `{target_dir}/journal_assessment.md`
- Report contains complete analysis and user decision

---

### Phase 7: Update Workflow State

**Goal:** Record journal assessment in workflow state.

**Actions:**
1. Read current workflow state from `{target_dir}/workflow_state.md`

2. Add or update journal assessment section:
   ```markdown
   ## JOURNAL ASSESSMENT

   **Status:** Completed
   **Selected Journal:** {journal_name} ({selected_journal})
   **Compatibility Score:** {score}/1.0
   **Assessment Date:** {date}

   **Files Generated:**
   - Journal Guidelines: journal_guidelines.md
   - Assessment Report: journal_assessment.md

   **Key Requirements:**
   - Word Limit: {min}-{max} words
   - Required Sections: {list}
   - Citation Style: {style}

   **Status:** Ready for drafting phase
   ```

3. Update workflow phase status:
   - If "JOURNAL ASSESSMENT" section exists, update it
   - If not, insert after "OUTLINE" section

4. Write updated workflow state

**Success Criteria:**
- Workflow state updated with journal assessment
- Phase status marked as completed

---

### Phase 8: Display Completion Status

**Goal:** Provide clear summary of assessment results and next steps.

**Actions:**
1. Display completion message:
   ```
   ✓ Journal Assessment Complete
   =============================

   Selected Journal: {journal_name}
   Compatibility Score: {score}/1.0

   Generated Files:
   - {target_dir}/journal_guidelines.md (comprehensive author guidelines)
   - {target_dir}/journal_assessment.md (assessment report)

   Next Steps:
   1. Review journal_guidelines.md for detailed requirements
   2. Ensure outline addresses all required sections
   3. Plan content strategy to meet word limits
   4. Proceed to drafting phase with /rrwrite-draft-section

   Key Requirements to Remember:
   - Total: {word_limit} words
   - Sections: {required_sections}
   - Citations: {citation_style}, max {reference_limit}
   - Special: {top_3_special_requirements}
   ```

2. If compatibility score < 0.7, add warning:
   ```
   ⚠ Warning: Compatibility score is below recommended threshold.
   Consider revising outline to better align with journal scope,
   or select an alternative journal using /rrwrite-plan with different target.
   ```

**Success Criteria:**
- User has clear understanding of assessment results
- Next steps are clearly communicated
- Warning displayed if applicable

---

## Error Handling

**Missing Files:**
- If workflow_state.md not found: "Error: Workflow state not found. Run /rrwrite-plan first."
- If journal_guidelines.yaml not found: "Error: Journal database not found at templates/journal_guidelines.yaml"
- If outline not found in workflow state: "Error: No outline found. Run /rrwrite-outline first."

**Invalid Journal:**
- If journal ID not in database: List available journals and prompt for valid selection

**Script Errors:**
- If matcher script fails: Display error message and attempt to continue with defaults
- If recommender fails: Skip recommendations and proceed with initial journal
- If fetcher fails: Generate basic guidelines from YAML data

**User Interaction:**
- If user response unclear: Re-prompt with clearer options
- If user cancels: Save progress and exit gracefully with instructions to resume

---

## Output Files

1. `{target_dir}/journal_guidelines.md` - Comprehensive author guidelines with compliance checklist
2. `{target_dir}/journal_assessment.md` - Assessment report with analysis and recommendations
3. `{target_dir}/workflow_state.md` - Updated with journal assessment section

---

## Success Indicators

- Journal compatibility analyzed and scored
- User confirmed journal selection
- Comprehensive guidelines retrieved and saved
- Assessment report generated
- Workflow state updated
- User informed of next steps

---

## Notes

- Always use AskUserQuestion for journal confirmation, never assume
- Provide clear explanations of compatibility scores
- If score < 0.7, strongly recommend alternatives but respect user choice
- Ensure all citation rules and special requirements are clearly communicated
- Save all analysis artifacts for future reference during drafting
