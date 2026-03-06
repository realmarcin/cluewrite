#!/usr/bin/env python3
"""
Assemble full manuscript from individual section files.

Generates multiple output formats:
- Markdown (.md): Source format with all content
- DOCX (.docx): Microsoft Word format with proper figure/table handling
- PDF (.pdf): PDF format (if pdflatex/weasyprint/wkhtmltopdf available)

Figure and Table Handling:
- Images: Place image files (PNG, JPG, PDF) in the manuscript directory or subdirectories
- Reference in markdown: ![Caption text](path/to/image.png)
- Images will be embedded in DOCX using --resource-path and --extract-media options
- Tables: Use markdown pipe syntax or reference external data tables

Data Tables:
- TSV files in data_tables/ can be converted to markdown tables using:
  python scripts/rrwrite-convert-tsv-to-table.py --input data_tables/file.tsv

Usage:
    python scripts/rrwrite-assemble-manuscript.py
    python scripts/rrwrite-assemble-manuscript.py --output-dir manuscript/project_v1
"""

import argparse
from pathlib import Path
from datetime import datetime

def assemble_manuscript(manuscript_dir="manuscript", output_file=None):
    """Assemble sections into full manuscript."""

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

    # Check for sections in two possible locations:
    # 1. Direct: manuscript_dir/abstract.md
    # 2. Subdirectory: manuscript_dir/sections/abstract.md
    sections_dir = manuscript_dir / "sections"
    found_sections = []
    missing_sections = []
    section_paths = {}  # Map section name to full path

    for section in section_order:
        # Try direct path first
        direct_path = manuscript_dir / section
        sections_subdir_path = sections_dir / section

        if direct_path.exists():
            found_sections.append(section)
            section_paths[section] = direct_path
        elif sections_subdir_path.exists():
            found_sections.append(section)
            section_paths[section] = sections_subdir_path
        else:
            # Conclusion is optional
            if section != "conclusion.md":
                missing_sections.append(section)

    if missing_sections:
        print(f"Warning: Missing sections: {', '.join(missing_sections)}")
        print("Proceeding with available sections...\n")

    if not found_sections:
        print(f"Error: No section files found in {manuscript_dir}/ or {sections_dir}/")
        return False

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
            section_path = section_paths[section]
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

    # Generate DOCX and PDF versions
    import subprocess
    import shutil

    if shutil.which("pandoc"):
        print("\nGenerating alternate formats...")

        # Generate DOCX with proper figure and table handling
        docx_file = output_file.with_suffix('.docx')
        try:
            # Set resource paths to include both figure and table directories
            # Priority 1: from_repo directories (original research outputs)
            # Priority 2: generated directories (analysis visualizations)
            resource_paths = [
                str(manuscript_dir),
                str(manuscript_dir / "figures/from_repo"),
                str(manuscript_dir / "figures/generated"),
                str(manuscript_dir / "tables/from_repo"),
                str(manuscript_dir / "tables/generated"),
                str(manuscript_dir / "figures"),  # Fallback for old manuscripts
                str(manuscript_dir / "tables")    # Fallback for old manuscripts
            ]

            # Build pandoc command with proper image/table support
            pandoc_cmd = [
                "pandoc",
                str(output_file),
                "-o", str(docx_file),
                "--standalone",
                "--resource-path", ":".join(resource_paths),  # Colon-separated paths
                "--extract-media", str(manuscript_dir / "media"),
                "--wrap=preserve",
                "--metadata", "title=Manuscript"
            ]

            # Add reference doc if available (for consistent styling)
            reference_doc = Path(__file__).parent.parent / "templates/reference.docx"
            if reference_doc.exists():
                pandoc_cmd.extend(["--reference-doc", str(reference_doc)])

            subprocess.run(pandoc_cmd, check=True, capture_output=True)

            docx_size = docx_file.stat().st_size / 1024  # KB
            print(f"  ✓ DOCX generated: {docx_file} ({docx_size:.1f} KB)")
            print(f"    - Images resolved from:")
            print(f"      • {manuscript_dir / 'figures/from_repo'}/ (Priority 1: Repository)")
            print(f"      • {manuscript_dir / 'figures/generated'}/ (Priority 2: Generated)")
            print(f"    - Media extracted to: {manuscript_dir / 'media'}/")
        except subprocess.CalledProcessError as e:
            print(f"  ⚠ DOCX generation failed: {e.stderr.decode()}")
        except Exception as e:
            print(f"  ⚠ DOCX generation failed: {e}")

        # Generate PDF (try multiple engines)
        pdf_file = output_file.with_suffix('.pdf')
        pdf_engines = ['pdflatex', 'weasyprint', 'wkhtmltopdf']
        pdf_generated = False

        for engine in pdf_engines:
            try:
                subprocess.run([
                    "pandoc",
                    str(output_file),
                    "-o", str(pdf_file),
                    "--pdf-engine=" + engine,
                    "-V", "geometry:margin=1in"
                ], check=True, capture_output=True, timeout=60)
                pdf_size = pdf_file.stat().st_size / 1024  # KB
                print(f"  ✓ PDF generated: {pdf_file} ({pdf_size:.1f} KB) [engine: {engine}]")
                pdf_generated = True
                break
            except subprocess.CalledProcessError:
                continue
            except subprocess.TimeoutExpired:
                print(f"  ⚠ PDF generation timed out with {engine}")
                continue
            except Exception:
                continue

        if not pdf_generated:
            print(f"  ⚠ PDF generation skipped (requires pdflatex, weasyprint, or wkhtmltopdf)")
            print(f"    Install with: brew install basictex  # for pdflatex")
    else:
        print("\n  Note: Pandoc not found. Install to generate DOCX/PDF:")
        print("    brew install pandoc")

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

    print("\nNext steps:")
    print(f"1. Read the manuscript: {output_file}")
    print(f"2. Validate: python scripts/rrwrite-validate-manuscript.py --file {output_file} --type manuscript")
    print(f"3. Critique: Use /rrwrite-critique-manuscript skill")
    print(f"4. Check status: python scripts/rrwrite-status.py")

    return True

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

    args = parser.parse_args()

    # Prefer --output-dir over --manuscript-dir
    manuscript_dir = args.output_dir if args.output_dir else args.manuscript_dir

    success = assemble_manuscript(manuscript_dir, args.output)

    if not success:
        exit(1)

if __name__ == '__main__':
    main()
