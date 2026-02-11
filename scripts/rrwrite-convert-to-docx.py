#!/usr/bin/env python3
"""
Convert RRWrite markdown manuscript to Microsoft Word (.docx) format.

Converts the assembled markdown manuscript to .docx format suitable for
importing into Google Docs or Microsoft Word, preserving heading styles,
citations, and embedded figures.

Usage:
    python scripts/rrwrite-convert-to-docx.py
    python scripts/rrwrite-convert-to-docx.py --input manuscript_full.md --output manuscript.docx
    python scripts/rrwrite-convert-to-docx.py --reference-doc custom-template.docx

Requirements:
    pip install pypandoc
    # OR system pandoc:
    # macOS: brew install pandoc
    # Ubuntu: apt-get install pandoc
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


class DocxConverter:
    """Convert markdown manuscripts to .docx format."""

    def __init__(self, input_file: Path, output_file: Path = None, reference_doc: Path = None):
        """
        Initialize converter.

        Args:
            input_file: Path to markdown file
            output_file: Path to output .docx file (default: same name as input)
            reference_doc: Optional path to reference .docx template for styling
        """
        self.input_file = Path(input_file)
        self.output_file = output_file or self.input_file.with_suffix('.docx')
        self.reference_doc = Path(reference_doc) if reference_doc else None

        if not self.input_file.exists():
            raise FileNotFoundError(f"Input file not found: {self.input_file}")

    def check_pandoc(self) -> bool:
        """Check if pandoc is available."""
        return shutil.which('pandoc') is not None

    def convert_with_pandoc(self) -> bool:
        """
        Convert markdown to .docx using system pandoc.

        Returns:
            True if conversion succeeded
        """
        cmd = [
            'pandoc',
            str(self.input_file),
            '-o', str(self.output_file),
            '-f', 'markdown',
            '-t', 'docx',
            '--standalone'
        ]

        # Add reference document if provided
        if self.reference_doc and self.reference_doc.exists():
            cmd.extend(['--reference-doc', str(self.reference_doc)])
            print(f"Using reference template: {self.reference_doc}")

        try:
            print(f"Converting {self.input_file} to {self.output_file}...")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            return True
        except subprocess.CalledProcessError as e:
            print(f"Pandoc conversion failed: {e.stderr}", file=sys.stderr)
            return False

    def convert_with_pypandoc(self) -> bool:
        """
        Convert markdown to .docx using pypandoc library.

        Returns:
            True if conversion succeeded
        """
        try:
            import pypandoc

            extra_args = []
            if self.reference_doc and self.reference_doc.exists():
                extra_args.append(f'--reference-doc={self.reference_doc}')
                print(f"Using reference template: {self.reference_doc}")

            print(f"Converting {self.input_file} to {self.output_file}...")
            pypandoc.convert_file(
                str(self.input_file),
                'docx',
                outputfile=str(self.output_file),
                extra_args=extra_args
            )
            return True
        except ImportError:
            print("pypandoc not installed", file=sys.stderr)
            return False
        except Exception as e:
            print(f"pypandoc conversion failed: {e}", file=sys.stderr)
            return False

    def convert(self) -> bool:
        """
        Convert markdown to .docx using available method.

        Returns:
            True if conversion succeeded
        """
        # Try system pandoc first (faster and more reliable)
        if self.check_pandoc():
            success = self.convert_with_pandoc()
            if success:
                self.print_success()
                return True

        # Fallback to pypandoc
        print("System pandoc not found, trying pypandoc...")
        success = self.convert_with_pypandoc()
        if success:
            self.print_success()
            return True

        # Both methods failed
        print("\n❌ Conversion failed!", file=sys.stderr)
        print("\nTo install pandoc:", file=sys.stderr)
        print("  macOS:  brew install pandoc", file=sys.stderr)
        print("  Ubuntu: sudo apt-get install pandoc", file=sys.stderr)
        print("  or:     pip install pypandoc", file=sys.stderr)
        return False

    def print_success(self):
        """Print success message with file details."""
        file_size = self.output_file.stat().st_size
        size_kb = file_size / 1024

        print(f"\n✓ Conversion successful!")
        print(f"  Output: {self.output_file}")
        print(f"  Size: {size_kb:.1f} KB")
        print(f"\nNext steps:")
        print(f"1. Open in Microsoft Word: {self.output_file}")
        print(f"2. Import to Google Docs:")
        print(f"   - Go to https://docs.google.com")
        print(f"   - File > Open > Upload")
        print(f"   - Select: {self.output_file}")
        print(f"3. Heading styles (H1, H2, etc.) are preserved")
        print(f"4. Images are embedded (if present)")


def main():
    parser = argparse.ArgumentParser(
        description="Convert RRWrite markdown manuscript to .docx format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        '--input', '-i',
        help='Input markdown file (default: manuscript_full.md in current directory)',
        default=None
    )
    parser.add_argument(
        '--output', '-o',
        help='Output .docx file (default: same name as input with .docx extension)',
        default=None
    )
    parser.add_argument(
        '--manuscript-dir',
        help='Manuscript directory (default: current directory)',
        default='.'
    )
    parser.add_argument(
        '--reference-doc',
        help='Reference .docx template for styling',
        default=None
    )

    args = parser.parse_args()

    # Determine input file
    if args.input:
        input_file = Path(args.input)
    else:
        # Look for manuscript_full.md in manuscript directory
        manuscript_dir = Path(args.manuscript_dir)
        input_file = manuscript_dir / 'manuscript_full.md'

        if not input_file.exists():
            print(f"Error: {input_file} not found", file=sys.stderr)
            print(f"Please specify --input or run from manuscript directory", file=sys.stderr)
            return 1

    # Determine output file
    output_file = Path(args.output) if args.output else None

    try:
        converter = DocxConverter(
            input_file=input_file,
            output_file=output_file,
            reference_doc=args.reference_doc
        )
        success = converter.convert()
        return 0 if success else 1

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
