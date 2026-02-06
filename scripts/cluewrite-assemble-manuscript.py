#!/usr/bin/env python3
"""
Assemble full manuscript from individual section files.

Usage:
    python scripts/cluewrite-assemble-manuscript.py
    python scripts/cluewrite-assemble-manuscript.py --output manuscript/full_manuscript.md
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

    print("\nNext steps:")
    print(f"1. Review the manuscript: {output_file}")
    print(f"2. Validate: python scripts/cluewrite-validate-manuscript.py --file {output_file} --type manuscript")
    print(f"3. Review: Use cluewrite-review-manuscript skill")

    return True

def main():
    parser = argparse.ArgumentParser(
        description="Assemble full manuscript from section files"
    )
    parser.add_argument(
        '--manuscript-dir',
        default='manuscript',
        help='Directory containing section files (default: manuscript)'
    )
    parser.add_argument(
        '--output',
        default=None,
        help='Output file path (default: manuscript/full_manuscript.md)'
    )

    args = parser.parse_args()

    success = assemble_manuscript(args.manuscript_dir, args.output)

    if not success:
        exit(1)

if __name__ == '__main__':
    main()
