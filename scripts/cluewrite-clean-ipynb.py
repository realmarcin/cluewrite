#!/usr/bin/env python3
"""
Jupyter Notebook cleaning tool for LLM ingestion.
Removes output cells and base64 images to reduce token count.
"""

import json
import sys
import argparse
from pathlib import Path


def clean_notebook(filepath, output_path=None):
    """
    Clean a Jupyter notebook by removing outputs and extracting only code and markdown.

    Args:
        filepath: Path to the .ipynb file
        output_path: Optional path for cleaned output (default: stdout or .md file)
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        nb = json.load(f)

    clean_cells = []

    for i, cell in enumerate(nb['cells']):
        if cell['cell_type'] == 'markdown':
            # Keep markdown cells as-is
            content = ''.join(cell['source'])
            if content.strip():
                clean_cells.append(content)

        elif cell['cell_type'] == 'code':
            source = ''.join(cell['source'])

            # Skip empty cells
            if not source.strip():
                continue

            # Skip cells that are purely plotting commands without logic
            if source.strip() in ['plt.show()', 'plt.tight_layout()', 'display()']:
                continue

            # Add code cell with delimiter
            clean_cells.append(f"```python\n# Cell {i+1}\n{source}\n```")

    output = '\n\n'.join(clean_cells)

    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"Cleaned notebook saved to: {output_path}", file=sys.stderr)
    else:
        print(output)

    return output


def main():
    parser = argparse.ArgumentParser(
        description='Clean Jupyter notebooks for LLM ingestion by removing outputs'
    )
    parser.add_argument('notebook', help='Path to .ipynb file')
    parser.add_argument(
        '-o', '--output',
        help='Output path (default: same name with .md extension)'
    )
    parser.add_argument(
        '--stdout',
        action='store_true',
        help='Print to stdout instead of file'
    )

    args = parser.parse_args()

    # Check input file exists
    if not Path(args.notebook).exists():
        print(f"Error: File not found: {args.notebook}", file=sys.stderr)
        sys.exit(1)

    # Determine output path
    if args.stdout:
        output_path = None
    elif args.output:
        output_path = args.output
    else:
        # Default: replace .ipynb with .md
        output_path = Path(args.notebook).with_suffix('.md')

    # Clean the notebook
    try:
        clean_notebook(args.notebook, output_path)
    except Exception as e:
        print(f"Error cleaning notebook: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
