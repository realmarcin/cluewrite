#!/usr/bin/env python3
"""
Convert full manuscript markdown to individual section files.

Splits a complete manuscript markdown file into separate section files
based on standard section headings (Abstract, Introduction, Results, Discussion, Methods).
"""

import argparse
import re
from pathlib import Path
from typing import Dict, List, Tuple


def detect_sections(content: str) -> Dict[str, Tuple[int, int]]:
    """
    Detect section boundaries in the manuscript.

    Returns dictionary mapping section name to (start_line, end_line).
    """
    lines = content.split('\n')
    sections = {}

    # Define section patterns (case-insensitive)
    section_patterns = {
        'abstract': r'^##\s+Abstract',
        'introduction': r'^##\s+Introduction',
        'results': r'^##\s+Results',
        'discussion': r'^##\s+Discussion',
        'methods': r'^##\s+Methods',
        'availability': r'^##\s+(Data\s+)?Availability|^##\s+Code\s+Availability',
    }

    section_starts = {}

    # Find section start lines
    for i, line in enumerate(lines):
        for section_name, pattern in section_patterns.items():
            if re.match(pattern, line, re.IGNORECASE):
                section_starts[section_name] = i
                break

    # Determine section boundaries
    sorted_sections = sorted(section_starts.items(), key=lambda x: x[1])

    for i, (section_name, start_line) in enumerate(sorted_sections):
        # End line is start of next section or end of document
        if i + 1 < len(sorted_sections):
            end_line = sorted_sections[i + 1][1]
        else:
            end_line = len(lines)

        sections[section_name] = (start_line, end_line)

    return sections


def extract_section(content: str, start_line: int, end_line: int,
                    remove_heading: bool = False) -> str:
    """Extract section content between start and end lines."""
    lines = content.split('\n')
    section_lines = lines[start_line:end_line]

    if remove_heading and section_lines:
        # Remove the first line (section heading)
        section_lines = section_lines[1:]

    # Strip trailing empty lines
    while section_lines and not section_lines[-1].strip():
        section_lines.pop()

    return '\n'.join(section_lines)


def split_manuscript(
    input_file: Path,
    output_dir: Path,
    remove_headings: bool = False,
    preserve_figures: bool = True
) -> Dict[str, Path]:
    """
    Split manuscript into separate section files.

    Args:
        input_file: Path to full manuscript markdown
        output_dir: Directory to save section files
        remove_headings: Whether to remove section headings from output
        preserve_figures: Keep figure/table references intact

    Returns:
        Dictionary mapping section names to output file paths
    """
    # Read manuscript
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Detect sections
    sections = detect_sections(content)

    if not sections:
        raise ValueError(f"No sections detected in {input_file}")

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Write section files
    output_files = {}

    for section_name, (start_line, end_line) in sections.items():
        section_content = extract_section(
            content, start_line, end_line, remove_heading=remove_headings
        )

        # Save to file
        output_file = output_dir / f"{section_name}.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(section_content)

        output_files[section_name] = output_file
        print(f"✓ Created {output_file} ({len(section_content)} chars)")

    return output_files


def main():
    parser = argparse.ArgumentParser(
        description="Split manuscript markdown into separate section files"
    )
    parser.add_argument(
        '--input',
        type=Path,
        required=True,
        help='Input manuscript markdown file'
    )
    parser.add_argument(
        '--output-dir',
        type=Path,
        required=True,
        help='Output directory for section files'
    )
    parser.add_argument(
        '--remove-headings',
        action='store_true',
        help='Remove section headings from output files'
    )
    parser.add_argument(
        '--preserve-figures',
        action='store_true',
        default=True,
        help='Keep figure/table references intact (default: True)'
    )

    args = parser.parse_args()

    # Validate input
    if not args.input.exists():
        parser.error(f"Input file not found: {args.input}")

    # Split manuscript
    print(f"\nSplitting manuscript: {args.input}")
    print(f"Output directory: {args.output_dir}\n")

    try:
        output_files = split_manuscript(
            args.input,
            args.output_dir,
            remove_headings=args.remove_headings,
            preserve_figures=args.preserve_figures
        )

        print(f"\n✅ Successfully split manuscript into {len(output_files)} sections")
        print("\nSection files created:")
        for section_name, file_path in sorted(output_files.items()):
            print(f"  • {section_name}: {file_path.name}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1

    return 0


if __name__ == '__main__':
    exit(main())
