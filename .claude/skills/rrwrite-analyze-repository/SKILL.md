---
name: rrwrite-analyze-repository
description: Use when starting manuscript workflow for new repository. Extracts file structure, generates data tables, identifies research indicators. Do NOT use for repositories already analyzed or mid-workflow.
arguments:
  - name: repo_path
    description: GitHub URL or local repository path to analyze
    required: true
  - name: target_dir
    description: Output directory for analysis results
    default: manuscript
allowed-tools:
context: fork
---

# Repository Analysis Skill

This skill analyzes a code repository (GitHub URL or local path) and generates a structured analysis document containing:
- Repository structure and organization
- Key files identified (data, scripts, figures)
- Inferred research context and topics
- File metadata for downstream manuscript generation

## Phase 0: Input Validation

**Check required arguments:**

```bash
if [ -z "{repo_path}" ]; then
    echo "Error: --repo-path is required"
    echo ""
    echo "Usage: /rrwrite-analyze-repository --repo-path <path-or-url> [--target-dir <dir>]"
    echo ""
    echo "Examples:"
    echo "  /rrwrite-analyze-repository --repo-path https://github.com/user/project"
    echo "  /rrwrite-analyze-repository --repo-path /path/to/local/repo --target-dir manuscript"
    exit 1
fi

# Create target directory
mkdir -p "{target_dir}"

# Set output file path
OUTPUT_FILE="{target_dir}/repository_analysis.md"

echo ""
echo "============================================================"
echo "REPOSITORY ANALYSIS"
echo "============================================================"
echo ""
echo "Repository: {repo_path}"
echo "Output directory: {target_dir}"
echo "Output file: $OUTPUT_FILE"
echo ""
```

## Phase 1: Execute Repository Analysis

**Check for existing analysis and run script:**

```bash
# Check for existing analysis
SKIP_ANALYSIS=false
if [ -f "$OUTPUT_FILE" ]; then
    echo "⚠ Warning: Analysis file already exists: $OUTPUT_FILE"
    echo ""
    read -p "Overwrite existing analysis? [y/N]: " response
    if [[ ! "$response" =~ ^[Yy] ]]; then
        echo "Using existing analysis file."
        SKIP_ANALYSIS=true
    fi
fi

# Run analysis script (unless skipped)
if [ "$SKIP_ANALYSIS" != "true" ]; then
    echo "Analyzing repository structure..."
    echo ""

    python scripts/rrwrite-analyze-repo.py "{repo_path}" --output "$OUTPUT_FILE"

    if [ $? -ne 0 ]; then
        echo ""
        echo "============================================================"
        echo "ANALYSIS FAILED"
        echo "============================================================"
        echo ""
        echo "Troubleshooting:"
        echo "  • For GitHub URLs: Ensure git is installed and URL is correct"
        echo "    - Test clone: git clone {repo_path} /tmp/test_clone"
        echo "  • For local paths: Verify the path exists and is accessible"
        echo "    - Test access: ls -la {repo_path}"
        echo "  • Check you have write permissions to {target_dir}"
        echo "    - Test write: touch {target_dir}/.test && rm {target_dir}/.test"
        echo ""
        echo "Common issues:"
        echo "  • Private repositories require authentication"
        echo "  • Network connectivity problems with GitHub"
        echo "  • Git not installed (install: brew install git)"
        echo ""
        exit 1
    fi

    echo ""
    echo "✓ Analysis complete: $OUTPUT_FILE"
fi
```

## Phase 2: Extract Metadata

**Parse analysis file to extract file counts and research topics:**

```python
import sys
import re
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path('scripts').resolve()))

# Read analysis file
analysis_file = Path("{target_dir}/repository_analysis.md")

if not analysis_file.exists():
    print(f"Error: Analysis file not found: {analysis_file}")
    sys.exit(1)

content = analysis_file.read_text(encoding='utf-8')

# Extract file counts by counting file references in each section
data_section = re.search(r'### Data Files.*?(?=###|\Z)', content, re.DOTALL)
data_files = len(re.findall(r'- `[^`]+`', data_section.group())) if data_section else 0

script_section = re.search(r'### (Analysis Scripts|Scripts).*?(?=###|\Z)', content, re.DOTALL)
script_files = len(re.findall(r'- `[^`]+`', script_section.group())) if script_section else 0

figure_section = re.search(r'### Figures.*?(?=###|\Z)', content, re.DOTALL)
figure_files = len(re.findall(r'- `[^`]+`', figure_section.group())) if figure_section else 0

file_counts = {
    "data": data_files,
    "scripts": script_files,
    "figures": figure_files
}

# Extract topics from "Inferred Research Context" section
topics_section = re.search(r'## Inferred Research Context.*?(?=##|\Z)', content, re.DOTALL)
topics = []
if topics_section:
    # Look for bullet points or numbered items
    topic_matches = re.findall(r'[-*\d.]+\s+(.+?)$', topics_section.group(), re.MULTILINE)
    topics = [t.strip() for t in topic_matches if t.strip()]

# Check for empty repository
if sum(file_counts.values()) == 0:
    print("\n⚠ Warning: Repository appears to be empty")
    print("  No data, scripts, or figures detected")
    print("\nAnalysis will continue with minimal information.")

print("\nExtracted metadata:")
print(f"  Data files: {file_counts['data']}")
print(f"  Scripts: {file_counts['scripts']}")
print(f"  Figures: {file_counts['figures']}")
print(f"  Topics detected: {len(topics)}")

# Store for next phase
globals()['file_counts'] = file_counts
globals()['topics'] = topics
globals()['analysis_file_path'] = str(analysis_file)
```

## Phase 3: Update Workflow State

**Update state manager with analysis results:**

```python
from rrwrite_state_manager import StateManager

# Initialize state manager (disable git for this operation)
manager = StateManager(output_dir="{target_dir}", enable_git=False)

# Update repository analysis stage
manager.update_repository_analysis(
    analysis_file=analysis_file_path,
    repo_path="{repo_path}",
    file_counts=file_counts,
    topics_detected=topics
)

print("✓ Workflow state updated")
```

## Phase 4: Display Summary

**Show completion summary and next steps:**

```bash
echo ""
echo "============================================================"
echo "REPOSITORY ANALYSIS COMPLETE"
echo "============================================================"
echo ""
echo "Repository: {repo_path}"
echo "Output: {target_dir}/repository_analysis.md"
echo ""
echo "Summary:"
echo "  • Data files: {file_counts[data]}"
echo "  • Scripts: {file_counts[scripts]}"
echo "  • Figures: {file_counts[figures]}"
echo "  • Topics detected: {len(topics)}"
echo ""
echo "Next Steps:"
echo "  1. Review repository_analysis.md"
echo "  2. Generate manuscript outline:"
echo "     /rrwrite-plan-manuscript --target-dir {target_dir} --journal <name>"
echo ""
echo "  Or check workflow status:"
echo "     python scripts/rrwrite-status.py --output-dir {target_dir}"
echo ""
echo "============================================================"
```

## Error Handling

### Invalid Repository Path
- **Symptom:** Script exits with "Error cloning repository" or file not found
- **Solution:** Verify path exists and is accessible

### GitHub Cloning Failures
- **Symptom:** Git clone fails with authentication or network errors
- **Solutions:**
  - Check repository is public or you have SSH keys configured
  - Verify network connectivity
  - Clone manually first, then analyze local path

### Permission Denied
- **Symptom:** Cannot write to target directory
- **Solution:** Check directory permissions or use different target directory

### Empty Repository
- **Symptom:** Zero file counts detected
- **Behavior:** Analysis continues but warns user about minimal information

## Notes

- Analysis output follows schemas/manuscript.yaml requirements
- File counts are used by downstream skills for validation
- Topics inform literature search and section planning
- State tracking enables workflow coordination between skills
