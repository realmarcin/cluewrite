# Power User Workflow Guide

For experienced users who want granular control and maximum efficiency.

## Overview

**Two workflows, equivalent results:**

| Aspect | Comprehensive (`/rrwrite-workflow`) | Power User (Individual Commands) |
|--------|-------------------------------------|----------------------------------|
| Control | Guided, automated | Granular, manual |
| Validation | Automatic at each phase | Manual invocation required |
| Output | Verbose with explanations | Terse with `--expert` flag |
| Flexibility | Fixed phase order | Can skip/reorder/parallelize |
| Error handling | Explains why + what to do | Machine-readable with `--output json` |
| Best for | First-time users, safety | Experienced users, speed |

Both achieve: ✅ Same quality | ✅ Same validation | ✅ Same output files

---

## Quick Start: Individual Commands

### Phase 1: Analysis
```bash
python scripts/rrwrite-analyze-repository.py --repo /path/to/repo --output manuscript/repo_v1
```

### Phase 2: Plan
```bash
python scripts/rrwrite-plan-manuscript.py --repo-analysis manuscript/repo_v1/repository_analysis.md --output manuscript/repo_v1/outline.md
python scripts/rrwrite-validate-manuscript.py --file manuscript/repo_v1/outline.md --type outline
```

### Phase 3: Journal
```bash
python scripts/rrwrite-assess-journal.py --outline manuscript/repo_v1/outline.md --output manuscript/repo_v1/journal_assessment.md
# User selects journal
python scripts/rrwrite-fetch-guidelines.py --journal bioinformatics --output manuscript/repo_v1/journal_guidelines.md
```

### Phase 4: Literature
```bash
python scripts/rrwrite-research-literature.py --outline manuscript/repo_v1/outline.md --target-dir manuscript/repo_v1
python scripts/rrwrite-validate-manuscript.py --file manuscript/repo_v1/literature.md --type literature
```

### Phase 5: Draft (with verification gates)
```bash
# For each section:
python scripts/rrwrite-draft-section.py --section methods --target-dir manuscript/repo_v1
python scripts/rrwrite-validate-manuscript.py --file manuscript/repo_v1/methods.md --type section

# ONLY IF exit code 0:
python scripts/rrwrite_state_manager.py --output-dir manuscript/repo_v1 --add-section methods

# Repeat for: abstract, introduction, results, discussion, availability
```

### Phase 6: Assemble
```bash
python scripts/rrwrite-assemble-manuscript.py --target-dir manuscript/repo_v1 --journal bioinformatics
python scripts/rrwrite-validate-manuscript.py --file manuscript/repo_v1/manuscript.md --type manuscript
```

### Phase 7: Review
```bash
# Stage 1: Content
python scripts/rrwrite-critique-content.py --file manuscript/repo_v1/manuscript.md --output manuscript/repo_v1/critique_content_v1.md

# Stage 2: Format
python scripts/rrwrite-critique-format.py --file manuscript/repo_v1/manuscript.md --journal bioinformatics --output manuscript/repo_v1/critique_format_v1.md
```

---

## Power User Features

### 1. Expert Mode (Minimal Output)

```bash
python scripts/rrwrite-validate-manuscript.py \
  --file manuscript/repo_v1/methods.md \
  --type section \
  --expert

# Output:
# ✅ PASSED
# (or errors only if failed)
```

**Use when:** You know what you're doing, want minimal output

### 2. JSON Output (Machine-Readable)

```bash
python scripts/rrwrite-validate-manuscript.py \
  --file manuscript/repo_v1/manuscript.md \
  --type manuscript \
  --output json

# Output:
{
  "status": "passed",
  "errors": [],
  "warnings": ["Table count exceeds Nature limit"],
  "info": ["Word count: 3245", "Citations: 28"]
}
```

**Use when:** Integrating with scripts, automation, parsing results

### 3. Quiet Mode (Errors Only)

```bash
python scripts/rrwrite-validate-manuscript.py \
  --file manuscript/repo_v1/methods.md \
  --type section \
  --quiet

# Output:
# (only prints if errors, silent if passed)
```

**Use when:** Chaining commands, scripts, want clean output

### 4. Skip Validation Override (Not Recommended)

```bash
python scripts/rrwrite-validate-manuscript.py \
  --file manuscript/repo_v1/methods.md \
  --type section \
  --no-validate

# Output:
# ⚠️  Validation skipped (--no-validate flag)
```

**Use when:** Debugging, testing, know issue is false positive

**Warning:** Bypasses safety checks. Use sparingly.

---

## Command Chaining

### Pipe Validation to Grep

```bash
python scripts/rrwrite-validate-manuscript.py \
  --file manuscript/repo_v1/manuscript.md \
  --type manuscript \
  --quiet 2>&1 | grep "✗"

# Shows only failed checks
```

### Validate All Sections in Loop

```bash
for section in abstract introduction methods results discussion availability; do
  echo "Validating $section..."
  python scripts/rrwrite-validate-manuscript.py \
    --file manuscript/repo_v1/${section}.md \
    --type section \
    --expert

  if [ $? -ne 0 ]; then
    echo "❌ Failed: $section"
    exit 1
  fi
done

echo "✅ All sections passed"
```

### Parallel Section Drafting (Independent Sections)

```bash
# Draft methods, results, availability in parallel
python scripts/rrwrite-draft-section.py --section methods --target-dir manuscript/repo_v1 &
P1=$!

python scripts/rrwrite-draft-section.py --section availability --target-dir manuscript/repo_v1 &
P2=$!

# Results depends on methods, wait for methods first
wait $P1
python scripts/rrwrite-draft-section.py --section results --target-dir manuscript/repo_v1 &
P3=$!

# Wait for all
wait $P2 $P3

echo "✅ Parallel drafting complete"
```

**Note:** Future Task #9 will automate this with `rrwrite_dispatch.py`

---

## Shell Aliases (Recommended Setup)

Add to `~/.bashrc` or `~/.zshrc`:

```bash
# ========================================
# RRWrite Power User Aliases
# ========================================

# Base commands
alias rr-analyze='python scripts/rrwrite-analyze-repository.py'
alias rr-plan='python scripts/rrwrite-plan-manuscript.py'
alias rr-assess='python scripts/rrwrite-assess-journal.py'
alias rr-literature='python scripts/rrwrite-research-literature.py'
alias rr-draft='python scripts/rrwrite-draft-section.py'
alias rr-assemble='python scripts/rrwrite-assemble-manuscript.py'
alias rr-validate='python scripts/rrwrite-validate-manuscript.py'
alias rr-critique-content='python scripts/rrwrite-critique-content.py'
alias rr-critique-format='python scripts/rrwrite-critique-format.py'
alias rr-trace='python scripts/rrwrite_citation_tracer.py'
alias rr-status='python scripts/rrwrite-status.py'

# Compound workflows
alias rr-draft-validate='rr-draft "$@" && rr-validate'
alias rr-full-critique='rr-critique-content "$@" && rr-critique-format "$@"'

# Quick validation (expert mode)
alias rr-check='rr-validate --expert'

# JSON output for parsing
alias rr-validate-json='rr-validate --output json'

# Status check
alias rr-progress='rr-status --output-dir'

# ========================================
# Usage Examples:
# ========================================
# rr-draft --section methods --target-dir manuscript/repo_v1
# rr-check --file manuscript/repo_v1/methods.md --type section
# rr-trace smith2024 methods manuscript/repo_v1
# rr-progress manuscript/repo_v1
```

**Installation:**
```bash
# Add to your shell config
echo "source ~/.rrwrite_aliases" >> ~/.bashrc  # or ~/.zshrc
source ~/.bashrc  # Reload
```

---

## Keyboard-Driven Workflow

Optimized for minimal context switching:

### Step-by-Step with History Shortcuts

```bash
# 1. Draft section
rr-draft --section methods --target-dir manuscript/repo_v1

# 2. Validate (↑ + edit: change rr-draft → rr-validate)
rr-validate --file manuscript/repo_v1/methods.md --type section

# 3. If errors: (view error message, fix in editor)

# 4. Re-validate (↑ to recall)
rr-validate --file manuscript/repo_v1/methods.md --type section

# 5. Update state (↑↑↑ + edit: change rr-validate → python scripts/rrwrite_state_manager.py)
python scripts/rrwrite_state_manager.py --output-dir manuscript/repo_v1 --add-section methods

# 6. Check progress
rr-status --output-dir manuscript/repo_v1

# 7. Next section (↑↑↑↑↑↑ + edit: change methods → results)
rr-draft --section results --target-dir manuscript/repo_v1
```

### Tab Completion (Optional)

Add to `~/.bashrc`:

```bash
# RRWrite tab completion
_rr_complete_sections() {
    local sections="abstract introduction methods results discussion availability"
    COMPREPLY=($(compgen -W "$sections" -- "${COMP_WORDS[COMP_CWORD]}"))
}

complete -F _rr_complete_sections rr-draft
```

**Usage:**
```bash
rr-draft --section me<TAB>  # Completes to: methods
```

---

## Pre-Commit Hooks

Automatic validation before git commits.

### Installation

```bash
# Copy template
cp docs/git-hooks/pre-commit-manuscript .git/hooks/pre-commit

# Make executable
chmod +x .git/hooks/pre-commit

# Test
git commit -m "Test commit"  # Will validate all sections first
```

### Hook Template

**File:** `docs/git-hooks/pre-commit-manuscript`

```bash
#!/bin/bash
# Pre-commit hook for manuscript validation
# Validates all manuscript sections before allowing commit

MANUSCRIPT_DIR="manuscript"
FAILED=0

echo "🔍 Validating manuscript sections..."

# Find all manuscript directories
for ms_dir in ${MANUSCRIPT_DIR}/*_v*/; do
    if [ ! -d "$ms_dir" ]; then
        continue
    fi

    echo "  Checking: $ms_dir"

    # Validate each section
    for section in abstract introduction methods results discussion availability; do
        SECTION_FILE="${ms_dir}${section}.md"

        if [ -f "$SECTION_FILE" ]; then
            python scripts/rrwrite-validate-manuscript.py \
                --file "$SECTION_FILE" \
                --type section \
                --expert \
                --quiet

            if [ $? -ne 0 ]; then
                echo "  ❌ Validation failed: $section"
                FAILED=1
            fi
        fi
    done

    # Validate full manuscript if exists
    MANUSCRIPT_FILE="${ms_dir}manuscript.md"
    if [ -f "$MANUSCRIPT_FILE" ]; then
        python scripts/rrwrite-validate-manuscript.py \
            --file "$MANUSCRIPT_FILE" \
            --type manuscript \
            --expert \
            --quiet

        if [ $? -ne 0 ]; then
            echo "  ❌ Validation failed: manuscript"
            FAILED=1
        fi
    fi
done

if [ $FAILED -eq 1 ]; then
    echo ""
    echo "❌ Pre-commit validation failed"
    echo "Fix errors or bypass with: git commit --no-verify"
    exit 1
fi

echo "✅ All validations passed"
exit 0
```

**Bypass if needed:**
```bash
git commit --no-verify -m "Work in progress"
```

---

## Automation Integration

### CI/CD Pipeline Example

```yaml
# .github/workflows/manuscript-validation.yml
name: Manuscript Validation

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'

      - name: Validate sections
        run: |
          for section in manuscript/*_v*/abstract.md manuscript/*_v*/introduction.md manuscript/*_v*/methods.md; do
            if [ -f "$section" ]; then
              python scripts/rrwrite-validate-manuscript.py \
                --file "$section" \
                --type section \
                --output json || exit 1
            fi
          done

      - name: Validate manuscript
        run: |
          for ms in manuscript/*_v*/manuscript.md; do
            if [ -f "$ms" ]; then
              python scripts/rrwrite-validate-manuscript.py \
                --file "$ms" \
                --type manuscript \
                --output json || exit 1
            fi
          done
```

### Makefile Example

```makefile
# Makefile for manuscript generation
MANUSCRIPT_DIR := manuscript/myrepo_v1
SECTIONS := abstract introduction methods results discussion availability

.PHONY: all analyze plan literature draft assemble review

all: analyze plan literature draft assemble review

analyze:
	python scripts/rrwrite-analyze-repository.py --repo ../myrepo --output $(MANUSCRIPT_DIR)

plan: analyze
	python scripts/rrwrite-plan-manuscript.py --repo-analysis $(MANUSCRIPT_DIR)/repository_analysis.md --output $(MANUSCRIPT_DIR)/outline.md
	python scripts/rrwrite-validate-manuscript.py --file $(MANUSCRIPT_DIR)/outline.md --type outline

literature: plan
	python scripts/rrwrite-research-literature.py --outline $(MANUSCRIPT_DIR)/outline.md --target-dir $(MANUSCRIPT_DIR)
	python scripts/rrwrite-validate-manuscript.py --file $(MANUSCRIPT_DIR)/literature.md --type literature

draft: literature
	@for section in $(SECTIONS); do \
		echo "Drafting $$section..."; \
		python scripts/rrwrite-draft-section.py --section $$section --target-dir $(MANUSCRIPT_DIR); \
		python scripts/rrwrite-validate-manuscript.py --file $(MANUSCRIPT_DIR)/$$section.md --type section || exit 1; \
	done

assemble: draft
	python scripts/rrwrite-assemble-manuscript.py --target-dir $(MANUSCRIPT_DIR)
	python scripts/rrwrite-validate-manuscript.py --file $(MANUSCRIPT_DIR)/manuscript.md --type manuscript

review: assemble
	python scripts/rrwrite-critique-content.py --file $(MANUSCRIPT_DIR)/manuscript.md --output $(MANUSCRIPT_DIR)/critique_content_v1.md
	python scripts/rrwrite-critique-format.py --file $(MANUSCRIPT_DIR)/manuscript.md --output $(MANUSCRIPT_DIR)/critique_format_v1.md

clean:
	rm -rf $(MANUSCRIPT_DIR)
```

**Usage:**
```bash
make all           # Run full workflow
make draft         # Just draft sections
make assemble      # Just assemble manuscript
```

---

## Advanced Patterns

### 1. Incremental Validation During Drafting

```bash
# Draft in chunks, validate after each
rr-draft --section methods --target-dir manuscript/repo_v1 --partial 1
rr-validate --file manuscript/repo_v1/methods.md --type section

rr-draft --section methods --target-dir manuscript/repo_v1 --partial 2
rr-validate --file manuscript/repo_v1/methods.md --type section

# Etc. (if tool supports partial drafting)
```

### 2. Citation Audit Trail Review

```bash
# View all citation usage
cat manuscript/repo_v1/.rrwrite/citation_audit.jsonl | jq .

# Find specific citation usage
cat manuscript/repo_v1/.rrwrite/citation_audit.jsonl | jq 'select(.citation == "smith2024")'

# Count citation usage per section
cat manuscript/repo_v1/.rrwrite/citation_audit.jsonl | jq -r '.section' | sort | uniq -c
```

### 3. Diff Between Versions

```bash
# Compare manuscripts across versions
diff manuscript/repo_v1/manuscript.md manuscript/repo_v2/manuscript.md

# Or use git diff
cd manuscript/repo_v1
git diff v1.0..v2.0 manuscript.md
```

---

## Troubleshooting Power User Issues

### Validation Fails but Looks Correct

**Try root cause tracer:**
```bash
rr-trace {citation_key} {section} {manuscript_dir}
```

**Common causes:**
- Whitespace in citation key
- Case sensitivity mismatch
- CSV format issues (quotes, commas in fields)

### Parallel Drafting Conflicts

**Symptoms:**
- Sections overwrite each other
- State updates lost

**Solution:**
- Use separate terminal windows
- OR use future `rrwrite_dispatch.py` (Task #9)

### Pre-Commit Hook Too Slow

**Optimization:**
```bash
# Only validate changed files
git diff --cached --name-only --diff-filter=ACM | grep "\.md$" | while read file; do
  python scripts/rrwrite-validate-manuscript.py --file "$file" --type section --expert
done
```

---

## Performance Tips

### 1. Use Expert Mode by Default

```bash
# Add to aliases
alias rr-validate='python scripts/rrwrite-validate-manuscript.py --expert'
```

### 2. Skip Validation for WIP (Temporarily)

```bash
# During rapid iteration
rr-draft --section methods --no-validate  # Not recommended for final
```

### 3. Cache Literature Evidence

```bash
# Reuse from previous version (Phase 4)
python scripts/rrwrite_import_evidence_tool.py \
  --source manuscript/repo_v1 \
  --target manuscript/repo_v2 \
  --validate
```

### 4. Parallel Independent Operations

```bash
# Run content and format review simultaneously
rr-critique-content --file manuscript/repo_v1/manuscript.md --output manuscript/repo_v1/critique_content_v1.md &
rr-critique-format --file manuscript/repo_v1/manuscript.md --journal bioinformatics --output manuscript/repo_v1/critique_format_v1.md &
wait
```

---

## Comparison Table: Comprehensive vs. Power User

| Feature | Comprehensive (`/rrwrite-workflow`) | Power User |
|---------|-------------------------------------|------------|
| **Invocation** | Single skill call | Individual commands |
| **Phases** | 7 sequential | Manual control |
| **Validation** | Automatic at each phase | Manual `rr-validate` |
| **Error messages** | Verbose with explanations | Terse with `--expert` |
| **Output format** | Text only | Text or `--output json` |
| **Flexibility** | Fixed order | Skip/reorder/parallelize |
| **Aliases** | N/A | `rr-*` shortcuts |
| **Pre-commit hooks** | N/A | Supported |
| **CI/CD** | Harder to integrate | Easy with `--output json` |
| **Speed** | ~45 min (includes pauses) | ~35 min (expert user) |
| **Safety** | High (auto-validation) | Medium (manual validation) |
| **Learning curve** | Low | Medium-High |
| **Best for** | First-time, safety | Experienced, speed |

---

## Recommended Workflow for Power Users

**Initial manuscript (first time):**
1. Use comprehensive workflow to learn the process
2. Observe output, understand phase dependencies
3. Note validation checkpoints

**Subsequent manuscripts:**
1. Switch to power user workflow
2. Use shell aliases for speed
3. Enable pre-commit hooks for safety
4. Automate with Makefile or scripts

**Iterative refinement:**
1. Use individual commands for specific phases
2. Expert mode for validation
3. Root cause tracer for debugging
4. JSON output for automation

---

## Summary

**Power user workflow = Same results, more control, faster execution**

**Key tools:**
- Expert mode: `--expert`
- JSON output: `--output json`
- Quiet mode: `--quiet`
- Shell aliases: `rr-*`
- Pre-commit hooks: Automatic validation
- Command chaining: Pipe validation results
- Parallel execution: Independent sections

**Same quality guarantees:**
- ✅ Defense-in-depth validation (4 layers)
- ✅ Verification gates (mandatory checks)
- ✅ Two-stage review (content + format)
- ✅ Rationalization counters (error messages)
- ✅ Task decomposition (checkpoints)
- ✅ Root cause tracing (debugging)

**Choose based on:**
- **Experience level:** Beginner → Comprehensive | Expert → Power User
- **Context:** Learning → Comprehensive | Production → Power User
- **Control needs:** Guided → Comprehensive | Granular → Power User
- **Speed priority:** Safety → Comprehensive | Speed → Power User
