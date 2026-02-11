#!/usr/bin/env python3
"""
Assemble full manuscript from individual section files.

Usage:
    python scripts/rrwrite-assemble-manuscript.py
    python scripts/rrwrite-assemble-manuscript.py --output manuscript/full_manuscript.md
    python scripts/rrwrite-assemble-manuscript.py --include-figures --convert-docx
"""

import argparse
import shutil
import re
from pathlib import Path
from datetime import datetime

def assemble_manuscript(manuscript_dir="manuscript", output_file=None,
                       include_figures=False, repository_path=None, convert_docx=False):
    """Assemble sections into full manuscript with optional figure handling.

    Args:
        manuscript_dir: Directory containing section files
        output_file: Output file path
        include_figures: If True, copy figures from repository to manuscript dir
        repository_path: Path to source repository (for figure copying)
        convert_docx: If True, convert output to .docx format after assembly
    """

    manuscript_dir = Path(manuscript_dir)

    if not manuscript_dir.exists():
        print(f"Error: {manuscript_dir} directory not found")
        return False

    # Standard section order
    section_order = [
        "abstract.md",
        "introduction.md",
        "methods.md",
        "results.md",
        "discussion.md",
        "conclusion.md"
    ]

    # Check which sections exist
    found_sections = []
    missing_sections = []

    for section in section_order:
        section_path = manuscript_dir / section
        if section_path.exists():
            found_sections.append(section)
        else:
            # Conclusion is optional
            if section != "conclusion.md":
                missing_sections.append(section)

    if missing_sections:
        print(f"Warning: Missing sections: {', '.join(missing_sections)}")
        print("Proceeding with available sections...\n")

    if not found_sections:
        print("Error: No section files found in manuscript/ directory")
        return False

    # Handle figures if requested
    figures_copied = 0
    if include_figures:
        figures_copied = copy_figures_to_manuscript(manuscript_dir, repository_path)

    # Determine output file
    if output_file is None:
        output_file = manuscript_dir / "full_manuscript.md"
    else:
        output_file = Path(output_file)

    print(f"Assembling manuscript from {len(found_sections)} sections:")
    for section in found_sections:
        print(f"  ✓ {section}")
    print()

    # Assemble sections
    with open(output_file, 'w') as outfile:
        # Write header
        outfile.write(f"# Full Manuscript\n\n")
        outfile.write(f"**Assembled:** {datetime.now().strftime('%Y-%m-%d')}\n\n")
        outfile.write("---\n\n")

        # Write each section
        for section in found_sections:
            section_path = manuscript_dir / section
            section_name = section.replace('.md', '').title()

            # Add section header if not already in file
            with open(section_path, 'r') as infile:
                content = infile.read().strip()

                # Check if content already starts with a title
                if not content.startswith('# '):
                    outfile.write(f"# {section_name}\n\n")

                outfile.write(content)
                outfile.write("\n\n---\n\n")

    print(f"✓ Manuscript assembled: {output_file}")
    print(f"  Total size: {output_file.stat().st_size} bytes")

    # Count words
    with open(output_file, 'r') as f:
        content = f.read()
        words = len(content.split())
        print(f"  Estimated words: {words}")

    # Update state
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent))
        from rrwrite_state_manager import StateManager

        # Use manuscript_dir as output_dir for state manager
        manager = StateManager(output_dir=str(manuscript_dir))
        manager.update_workflow_stage(
            "assembly",
            status="completed",
            file_path=str(output_file.relative_to(manager.project_root))
        )
        print(f"  ✓ Workflow state updated")
    except Exception as e:
        print(f"  Note: Could not update state ({e})")

    # Convert to .docx if requested
    if convert_docx:
        print("\nConverting to .docx format...")
        success = convert_to_docx(output_file)
        if not success:
            print("Warning: .docx conversion failed (manuscript .md still available)")

    print("\nNext steps:")
    print(f"1. Read the manuscript: {output_file}")
    if convert_docx:
        docx_file = output_file.with_suffix('.docx')
        print(f"2. Open Word document: {docx_file}")
        print(f"3. Import to Google Docs: Upload {docx_file} to docs.google.com")
    print(f"4. Validate: python scripts/rrwrite-validate-manuscript.py --file {output_file} --type manuscript")
    print(f"5. Critique: Use /rrwrite-critique-manuscript skill")
    print(f"6. Check status: python scripts/rrwrite-status.py")
    if figures_copied > 0:
        print(f"\n✓ Copied {figures_copied} figure(s) to {manuscript_dir / 'figures'}")

    return True


def copy_figures_to_manuscript(manuscript_dir: Path, repository_path: Path = None) -> int:
    """
    Copy figure files from repository to manuscript figures directory.

    Args:
        manuscript_dir: Manuscript directory
        repository_path: Source repository path (auto-detect if None)

    Returns:
        Number of figures copied
    """
    # Determine repository path
    if repository_path is None:
        # Try to get from state file
        try:
            import sys
            sys.path.insert(0, str(Path(__file__).parent))
            from rrwrite_state_manager import StateManager

            manager = StateManager(output_dir=str(manuscript_dir))
            repository_path = Path(manager.state.get('repository_path', '.'))
        except Exception:
            # Fallback to parent of manuscript dir
            repository_path = manuscript_dir.parent

    repository_path = Path(repository_path)

    # Figure patterns to search for
    figure_patterns = ['*.png', '*.jpg', '*.jpeg', '*.pdf', '*.svg', '*.eps']

    # Find figures in repository
    figures = []
    for pattern in figure_patterns:
        figures.extend(repository_path.rglob(pattern))

    # Filter out non-figure directories
    skip_dirs = {'.git', '__pycache__', '.ipynb_checkpoints', 'node_modules',
                 '.venv', 'venv', 'env', 'dist', 'build'}
    figures = [f for f in figures if not any(skip in f.parts for skip in skip_dirs)]

    if not figures:
        print("No figures found in repository")
        return 0

    # Create figures directory in manuscript dir
    figures_dir = manuscript_dir / 'figures'
    figures_dir.mkdir(exist_ok=True)

    # Copy figures
    copied = 0
    for fig in figures:
        try:
            dest = figures_dir / fig.name
            # Avoid overwriting if file exists
            if not dest.exists():
                shutil.copy2(fig, dest)
                copied += 1
                print(f"  Copied: {fig.name}")
        except Exception as e:
            print(f"  Warning: Could not copy {fig.name}: {e}")

    return copied


def normalize_figure_references(content: str, manuscript_dir: Path) -> str:
    """
    Normalize figure references to use local figures/ directory.

    Args:
        content: Markdown content
        manuscript_dir: Manuscript directory path

    Returns:
        Content with normalized figure references
    """
    # Pattern to match markdown image syntax: ![alt](path)
    pattern = r'!\[([^\]]*)\]\(([^)]+)\)'

    def replace_path(match):
        alt_text = match.group(1)
        img_path = match.group(2)

        # If path is already using figures/, leave it
        if img_path.startswith('figures/') or img_path.startswith('./figures/'):
            return match.group(0)

        # Extract filename
        filename = Path(img_path).name

        # Check if file exists in figures/ directory
        figures_dir = manuscript_dir / 'figures'
        if (figures_dir / filename).exists():
            return f'![{alt_text}](figures/{filename})'

        # Return original if not found
        return match.group(0)

    return re.sub(pattern, replace_path, content)


def convert_to_docx(markdown_file: Path) -> bool:
    """
    Convert markdown file to .docx format using pandoc.

    Args:
        markdown_file: Path to markdown file

    Returns:
        True if conversion succeeded
    """
    import subprocess

    docx_file = markdown_file.with_suffix('.docx')

    # Check if pandoc is available
    if not shutil.which('pandoc'):
        print("  Pandoc not found. Install with: brew install pandoc")
        print("  Or use: python scripts/rrwrite-convert-to-docx.py")
        return False

    try:
        cmd = [
            'pandoc',
            str(markdown_file),
            '-o', str(docx_file),
            '-f', 'markdown',
            '-t', 'docx',
            '--standalone'
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        file_size = docx_file.stat().st_size / 1024
        print(f"  ✓ Created: {docx_file} ({file_size:.1f} KB)")
        return True

    except subprocess.CalledProcessError as e:
        print(f"  Conversion failed: {e.stderr}")
        return False
    except Exception as e:
        print(f"  Error: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description="Assemble full manuscript from section files"
    )
    parser.add_argument(
        '--manuscript-dir',
        default='manuscript',
        help='Directory containing section files (default: manuscript). Deprecated, use --output-dir instead.'
    )
    parser.add_argument(
        '--output-dir',
        help='Output directory for manuscript files (e.g., manuscript/repo_v1). Takes precedence over --manuscript-dir.'
    )
    parser.add_argument(
        '--output',
        default=None,
        help='Output file path (default: <output-dir>/full_manuscript.md)'
    )
    parser.add_argument(
        '--include-figures',
        action='store_true',
        help='Copy figure files from repository to manuscript/figures directory'
    )
    parser.add_argument(
        '--repository-path',
        help='Source repository path for figure copying (auto-detected if not specified)'
    )
    parser.add_argument(
        '--convert-docx',
        action='store_true',
        help='Convert assembled manuscript to .docx format (requires pandoc)'
    )

    args = parser.parse_args()

    # Prefer --output-dir over --manuscript-dir
    manuscript_dir = args.output_dir if args.output_dir else args.manuscript_dir

    success = assemble_manuscript(
        manuscript_dir,
        args.output,
        include_figures=args.include_figures,
        repository_path=args.repository_path,
        convert_docx=args.convert_docx
    )

    if not success:
        exit(1)

if __name__ == '__main__':
    main()
