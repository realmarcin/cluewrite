# Remaining Implementation Notes

Tasks not yet fully implemented with detailed specifications for future work.

## Task #9: Parallel Subagent Dispatch System

### Status: NOT STARTED (Foundation ready)

### Objective
Enable parallel drafting of independent manuscript sections for 3-5x speedup on large manuscripts.

### Design Specification

**File:** `scripts/rrwrite_dispatch.py`

```python
#!/usr/bin/env python3
"""
Parallel section dispatcher for manuscript drafting.

Enables concurrent drafting of independent sections (methods, results, availability).
"""

import asyncio
import subprocess
from pathlib import Path
from typing import List, Dict
from dataclasses import dataclass
from enum import Enum


class SectionStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class SectionTask:
    """Represents a section drafting task."""
    section_name: str
    target_dir: Path
    dependencies: List[str]  # Sections that must complete first
    status: SectionStatus
    process: Optional[subprocess.Popen] = None
    output_file: Optional[Path] = None
    error_message: Optional[str] = None


class SectionDispatcher:
    """Orchestrates parallel section drafting."""

    # Section dependencies (what must complete before this section)
    DEPENDENCIES = {
        'abstract': ['introduction', 'methods', 'results', 'discussion'],  # Needs summary of all
        'introduction': [],  # Independent
        'methods': [],  # Independent
        'results': ['methods'],  # Needs methods context
        'discussion': ['results'],  # Needs results to discuss
        'availability': []  # Independent
    }

    def __init__(self, target_dir: Path):
        self.target_dir = target_dir
        self.tasks: Dict[str, SectionTask] = {}

    def create_tasks(self, sections: List[str]) -> Dict[str, SectionTask]:
        """Create tasks for specified sections with dependency resolution."""
        for section in sections:
            self.tasks[section] = SectionTask(
                section_name=section,
                target_dir=self.target_dir,
                dependencies=self.DEPENDENCIES.get(section, []),
                status=SectionStatus.PENDING
            )
        return self.tasks

    def get_ready_tasks(self) -> List[SectionTask]:
        """Get tasks with all dependencies completed."""
        ready = []
        for task in self.tasks.values():
            if task.status != SectionStatus.PENDING:
                continue

            # Check if all dependencies complete
            deps_complete = all(
                self.tasks.get(dep, None) and
                self.tasks[dep].status == SectionStatus.COMPLETED
                for dep in task.dependencies
            )

            if deps_complete or not task.dependencies:
                ready.append(task)

        return ready

    async def dispatch_task(self, task: SectionTask) -> None:
        """Dispatch a single section drafting task."""
        task.status = SectionStatus.IN_PROGRESS
        task.output_file = self.target_dir / f'{task.section_name}_dispatch_log.txt'

        # Run draft command in background
        cmd = [
            'python', 'scripts/rrwrite-draft-section.py',
            '--section', task.section_name,
            '--target-dir', str(task.target_dir)
        ]

        try:
            task.process = subprocess.Popen(
                cmd,
                stdout=open(task.output_file, 'w'),
                stderr=subprocess.STDOUT,
                text=True
            )

            # Wait for completion
            returncode = await asyncio.get_event_loop().run_in_executor(
                None, task.process.wait
            )

            if returncode == 0:
                task.status = SectionStatus.COMPLETED
            else:
                task.status = SectionStatus.FAILED
                task.error_message = f"Draft failed with exit code {returncode}"

        except Exception as e:
            task.status = SectionStatus.FAILED
            task.error_message = str(e)

    async def run_parallel(self, max_concurrent: int = 3) -> Dict[str, SectionTask]:
        """Run tasks in parallel with concurrency limit."""
        while True:
            # Get ready tasks
            ready = self.get_ready_tasks()
            if not ready:
                # Check if all done
                all_done = all(
                    task.status in [SectionStatus.COMPLETED, SectionStatus.FAILED]
                    for task in self.tasks.values()
                )
                if all_done:
                    break

                # Wait for in-progress tasks
                await asyncio.sleep(5)
                continue

            # Dispatch up to max_concurrent tasks
            tasks_to_run = ready[:max_concurrent]
            await asyncio.gather(*[self.dispatch_task(t) for t in tasks_to_run])

        return self.tasks

    def validate_all(self) -> Dict[str, bool]:
        """Validate all completed sections."""
        results = {}
        for section, task in self.tasks.items():
            if task.status != SectionStatus.COMPLETED:
                results[section] = False
                continue

            section_file = self.target_dir / f'{section}.md'
            if not section_file.exists():
                results[section] = False
                continue

            # Run validation
            result = subprocess.run(
                [
                    'python', 'scripts/rrwrite-validate-manuscript.py',
                    '--file', str(section_file),
                    '--type', 'section'
                ],
                capture_output=True
            )

            results[section] = result.returncode == 0

        return results


# CLI interface
def main():
    import sys
    if len(sys.argv) < 3:
        print("Usage: python rrwrite_dispatch.py <target_dir> <section1> <section2> ...")
        sys.exit(1)

    target_dir = Path(sys.argv[1])
    sections = sys.argv[2:]

    dispatcher = SectionDispatcher(target_dir)
    dispatcher.create_tasks(sections)

    # Run parallel dispatch
    print(f"Dispatching {len(sections)} sections in parallel...")
    results = asyncio.run(dispatcher.run_parallel(max_concurrent=3))

    # Report results
    print("\n" + "=" * 70)
    print("DISPATCH RESULTS")
    print("=" * 70)

    for section, task in results.items():
        status_symbol = "✓" if task.status == SectionStatus.COMPLETED else "✗"
        print(f"{status_symbol} {section}: {task.status.value}")
        if task.error_message:
            print(f"  Error: {task.error_message}")

    # Validate all
    print("\n" + "=" * 70)
    print("VALIDATION RESULTS")
    print("=" * 70)

    validation = dispatcher.validate_all()
    for section, valid in validation.items():
        status_symbol = "✓" if valid else "✗"
        print(f"{status_symbol} {section}: {'VALID' if valid else 'INVALID'}")

    # Exit code based on success
    all_success = all(
        task.status == SectionStatus.COMPLETED and validation.get(section, False)
        for section, task in results.items()
    )

    sys.exit(0 if all_success else 1)


if __name__ == '__main__':
    main()
```

### Usage Example

```bash
# Draft methods, results, and availability in parallel
python scripts/rrwrite_dispatch.py manuscript/ methods results availability

# Output shows parallel progress:
# ⏳ Dispatching 3 sections in parallel...
# ✓ methods: completed (2m 15s)
# ✓ results: completed (3m 45s) [waited for methods]
# ✓ availability: completed (1m 30s)
#
# All sections validated: ✓
```

### Integration Points

**In rrwrite-draft-section skill:**
```markdown
## Parallel Mode (Advanced)

For manuscripts with 5+ sections, use parallel dispatch:

```bash
python scripts/rrwrite_dispatch.py {target_dir} methods results availability
```

**Requirements:**
- Sections must be independent (no cross-references)
- Outline and citations must be complete
- Sufficient system resources (3 concurrent processes)

**When to use:** Large manuscripts (>5 sections), tight deadlines
**When NOT to use:** First drafts, highly interconnected arguments
```

### Testing Strategy

1. **Unit tests:** Test dependency resolution
2. **Integration tests:** Run parallel dispatch on test manuscript
3. **Performance tests:** Measure speedup vs. sequential
4. **Failure tests:** Verify graceful handling of section failures

### Estimated Effort: 20 hours
- Implementation: 12 hours
- Testing: 5 hours
- Documentation: 3 hours

---

## Task #10: Power User Optimizations (Remaining)

### Status: PARTIALLY COMPLETE (expert mode done)

### Remaining Work

#### 10.1 Command Chaining Support

**File:** Update scripts to support piping

```bash
# Enable bash pipelines
python scripts/rrwrite-validate-manuscript.py --file manuscript.md --type manuscript --quiet | \
  grep "✗" | \
  python scripts/rrwrite-citation-tracer.py --stdin
```

**Changes needed:**
- Add `--quiet` flag (only errors, no info)
- Add `--stdin` support for tracer
- Ensure exit codes propagate correctly

#### 10.2 Shell Aliases Documentation

**File:** `docs/power-user-aliases.md`

```bash
# Add to ~/.bashrc or ~/.zshrc

# RRWrite shortcuts
alias rr-draft='python scripts/rrwrite-draft-section.py'
alias rr-validate='python scripts/rrwrite-validate-manuscript.py'
alias rr-critique-content='python scripts/rrwrite-critique-content.py'
alias rr-critique-format='python scripts/rrwrite-critique-format.py'
alias rr-trace='python scripts/rrwrite_citation_tracer.py'

# Common workflows
alias rr-draft-validate='rr-draft && rr-validate'
alias rr-full-critique='rr-critique-content && rr-critique-format'

# Status check
alias rr-status='python scripts/rrwrite-status.py'
```

#### 10.3 Pre-commit Hook Templates

**File:** `docs/git-hooks/pre-commit-manuscript`

```bash
#!/bin/bash
# Pre-commit hook for manuscript validation

MANUSCRIPT_DIR="manuscript"

if [ -d "$MANUSCRIPT_DIR" ]; then
    # Find all section files
    for section in abstract introduction methods results discussion availability; do
        SECTION_FILE="$MANUSCRIPT_DIR/${section}.md"

        if [ -f "$SECTION_FILE" ]; then
            echo "Validating $section..."
            python scripts/rrwrite-validate-manuscript.py \
                --file "$SECTION_FILE" \
                --type section \
                --expert \
                --quiet

            if [ $? -ne 0 ]; then
                echo "❌ Validation failed for $section"
                echo "Fix errors or use: git commit --no-verify"
                exit 1
            fi
        fi
    done

    echo "✓ All sections validated"
fi

exit 0
```

**Installation:**
```bash
cp docs/git-hooks/pre-commit-manuscript .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

#### 10.4 Keyboard-Driven Workflow Documentation

**File:** `docs/keyboard-workflow.md`

Document optimal keyboard-driven workflow for power users:

1. **Draft section:** `rr-draft --section methods`
2. **Validate (↑ + edit):** `rr-validate --file manuscript/methods.md --type section`
3. **Fix errors (if any):** (use error messages as guide)
4. **Re-validate:** `↑↑` (bash history)
5. **Update state:** `python scripts/rrwrite_state_manager.py ...`
6. **Check status:** `rr-status`
7. **Move to next:** `rr-draft --section results`

### Estimated Effort: 8 hours
- Command chaining: 3 hours
- Documentation: 3 hours
- Hook templates: 2 hours

---

## Task #12: End-to-End Integration Testing

### Status: NOT STARTED

### Test Plan

#### Test Suite 1: Citation Validation

**Test case 1.1:** Entry validation catches missing citations
```python
def test_entry_validation_missing_citation():
    # Create section with citation not in evidence
    section = create_test_section(citations=['missing2024'])
    evidence = create_test_evidence(citations=['present2024'])

    result = validate_section(section, evidence)

    assert result.exit_code == 1
    assert 'missing2024' in result.errors
    assert 'not in literature_evidence.csv' in result.errors
```

**Test case 1.2:** Business logic catches inappropriate citations
```python
def test_business_logic_abstract_in_methods():
    # Create methods section with abstract principle citation
    section = create_test_section(
        name='methods',
        citations=['fair2016']  # FAIR principles = abstract
    )
    evidence = create_test_evidence(citations=['fair2016'], types=['abstract'])

    result = validate_section(section, evidence)

    assert 'inappropriate' in result.warnings.lower()
    assert 'methods' in result.warnings.lower()
```

**Test case 1.3:** Assembly validation catches orphaned citations
```python
def test_assembly_orphaned_citations():
    manuscript = create_test_manuscript(citations=['smith2024', 'jones2023'])
    bib = create_test_bib(citations=['smith2024'])  # Missing jones2023

    result = validate_manuscript(manuscript, bib)

    assert result.exit_code == 1
    assert 'jones2023' in result.errors
    assert 'orphaned' in result.errors.lower()
```

#### Test Suite 2: Verification Gates

**Test case 2.1:** Incomplete section blocked from state update
```python
def test_verification_gate_blocks_incomplete():
    section = create_test_section(word_count=100)  # Target: 500
    state_manager = StateManager()

    # Attempt to mark complete without validation
    with pytest.raises(VerificationGateError):
        state_manager.add_section_completed('methods')

    # Should require validation pass first
```

**Test case 2.2:** Validation failure prevents progression
```python
def test_validation_failure_blocks_progression():
    section = create_test_section(citations=['missing2024'])

    result = validate_and_update_state(section)

    assert result.state_updated == False
    assert 'validation failed' in result.message.lower()
```

#### Test Suite 3: Two-Stage Review

**Test case 3.1:** Content review identifies scientific issues
```python
def test_content_review_finds_unsupported_claims():
    manuscript = create_test_manuscript(
        content='This demonstrates the best approach. [no citation]'
    )

    content_review = run_content_review(manuscript)

    assert len(content_review.major_issues) > 0
    assert any('unsupported' in issue.lower() for issue in content_review.major_issues)
```

**Test case 3.2:** Format review identifies structure issues
```python
def test_format_review_finds_missing_captions():
    manuscript = create_test_manuscript(
        tables=['| A | B |\n| 1 | 2 |']  # Table without caption
    )

    format_review = run_format_review(manuscript)

    assert any('caption' in issue.lower() for issue in format_review.issues)
```

#### Test Suite 4: Token Efficiency

**Test case 4.1:** Skill documentation within budget
```python
def test_skill_token_budget():
    skill_files = glob('skills/rrwrite-*/SKILL.md')

    budgets = {
        'draft-section': 250,
        'research-literature': 450,
        'plan-manuscript': 250
    }

    for skill_file in skill_files:
        skill_name = extract_skill_name(skill_file)
        word_count = count_words(skill_file)
        budget = budgets.get(skill_name, 600)

        assert word_count <= budget, \
            f'{skill_name} exceeds budget: {word_count} > {budget}'
```

#### Test Suite 5: Root Cause Tracing

**Test case 5.1:** Tracer identifies 5 levels
```python
def test_tracer_5_levels():
    citation = 'missing2024'
    section = 'methods'

    trace = run_citation_trace(citation, section)

    assert 'symptom' in trace.levels
    assert 'immediate' in trace.levels
    assert 'usage' in trace.levels
    assert 'origin' in trace.levels
    assert 'trigger' in trace.levels
```

**Test case 5.2:** Tracer suggests actionable fix
```python
def test_tracer_actionable_fix():
    trace = run_citation_trace('missing2024', 'methods')

    assert trace.suggested_fix is not None
    assert len(trace.suggested_fix.steps) > 0
    assert len(trace.suggested_fix.commands) > 0
```

### Success Metrics

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Citation error rate | <5% | Count errors in production manuscripts |
| Incomplete section rate | 0% | Check state manager logs |
| User error comprehension | >90% | Survey after validation failure |
| Skill loading time | <50% baseline | Measure token count before/after |
| Manuscript completion time | >3x with parallel | Time sequential vs. parallel |

### Estimated Effort: 30 hours
- Test implementation: 20 hours
- CI/CD integration: 5 hours
- Documentation: 5 hours

---

## Implementation Priority

**Week 1 (COMPLETE):** ✓
- Tasks #1-5: Core reliability and usability
- ~2,500 lines of code

**Week 2 (COMPLETE):** ✓
- Tasks #6-8: Task decomposition, optimization guide, root cause tracing
- ~1,000 lines of code

**Week 3 (Recommended Next):**
- Task #9: Parallel dispatch system
- Task #10: Complete power user optimizations
- Estimated: 28 hours

**Week 4 (Final):**
- Task #12: Integration testing
- Performance benchmarking
- User documentation
- Estimated: 30 hours

---

## Total Implementation Status

**Completed:** 8/12 tasks (67%)
**Remaining:** 4 tasks (33%)
**Code written:** ~3,500 lines
**Code remaining:** ~1,000 lines estimated
**Time invested:** ~60 hours
**Time remaining:** ~60 hours estimated
