#!/usr/bin/env python3
"""
Generate Journal Schema - CLI for dynamic journal schema generation.

This script provides a command-line interface for generating journal-specific
JSON schemas from various sources (URL, PDF, DOCX, YAML).
"""

import argparse
import sys
from pathlib import Path

# Add scripts directory to path
SCRIPTS_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPTS_DIR))

from rrwrite_journal_schema_generator import JournalSchemaGenerator


def main():
    parser = argparse.ArgumentParser(
        description="Generate journal-specific JSON schemas from various sources",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate from journal website
  %(prog)s --journal "Bioinformatics" --source url \\
    --url https://academic.oup.com/bioinformatics/pages/instructions_for_authors

  # Generate from PDF guidelines
  %(prog)s --journal "Nature Methods" --source pdf \\
    --file ~/Downloads/nature_methods_guidelines.pdf

  # Convert from YAML entry
  %(prog)s --journal "PLOS Computational Biology" --source yaml \\
    --yaml templates/journal_guidelines.yaml

  # Check if schema exists in cache
  %(prog)s --journal "Bioinformatics" --check-cache

  # Force regeneration
  %(prog)s --journal "Bioinformatics" --source yaml \\
    --yaml templates/journal_guidelines.yaml --force
        """
    )

    # Required arguments
    parser.add_argument(
        '--journal',
        required=True,
        help='Journal name (e.g., "Bioinformatics", "Nature Methods")'
    )

    # Source options
    parser.add_argument(
        '--source',
        choices=['url', 'pdf', 'docx', 'yaml'],
        help='Source type for requirements'
    )

    parser.add_argument(
        '--url',
        help='URL to journal guidelines page (requires --source url)'
    )

    parser.add_argument(
        '--file',
        help='Path to PDF or DOCX file (requires --source pdf or docx)'
    )

    parser.add_argument(
        '--yaml',
        help='Path to YAML file (requires --source yaml)'
    )

    # Options
    parser.add_argument(
        '--check-cache',
        action='store_true',
        help='Check if schemas exist in cache without generating'
    )

    parser.add_argument(
        '--force',
        action='store_true',
        help='Force regeneration even if cached schemas exist'
    )

    parser.add_argument(
        '--output-dir',
        type=Path,
        help='Output directory for schemas (default: schemas/journals)'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )

    args = parser.parse_args()

    # Initialize generator
    generator = JournalSchemaGenerator(output_dir=args.output_dir)

    # Check cache mode
    if args.check_cache:
        journal_key = generator._normalize_journal_key(args.journal)
        cached, paths = generator.check_cache(journal_key)

        if cached:
            print(f"✓ Cached schemas found for {args.journal}")
            print(f"  Journal key: {journal_key}")
            print("  Schemas:")
            for schema_type, path in paths.items():
                print(f"    {schema_type}: {path}")
            return 0
        else:
            print(f"✗ No cached schemas for {args.journal}")
            print(f"  Journal key: {journal_key}")
            return 1

    # Validate source arguments
    if not args.source:
        parser.error("--source required (unless using --check-cache)")

    if args.source == 'url' and not args.url:
        parser.error("--url required when --source is url")

    if args.source in ['pdf', 'docx'] and not args.file:
        parser.error("--file required when --source is pdf or docx")

    if args.source == 'yaml' and not args.yaml:
        parser.error("--yaml required when --source is yaml")

    # Generate schemas
    print(f"Generating schemas for {args.journal}...")
    print(f"Source: {args.source}")

    success = False
    paths = {}

    try:
        if args.source == 'url':
            print(f"Fetching from: {args.url}")
            success, paths = generator.generate_from_url(
                journal_name=args.journal,
                url=args.url,
                force=args.force
            )

        elif args.source in ['pdf', 'docx']:
            file_path = Path(args.file)
            if not file_path.exists():
                print(f"Error: File not found: {args.file}", file=sys.stderr)
                return 1

            print(f"Parsing {args.source.upper()}: {args.file}")
            success, paths = generator.generate_from_file(
                journal_name=args.journal,
                file_path=str(file_path),
                file_type=args.source,
                force=args.force
            )

        elif args.source == 'yaml':
            yaml_path = Path(args.yaml)
            if not yaml_path.exists():
                print(f"Error: YAML file not found: {args.yaml}", file=sys.stderr)
                return 1

            print(f"Converting from YAML: {args.yaml}")
            success, paths = generator.generate_from_yaml(
                journal_name=args.journal,
                yaml_path=str(yaml_path),
                force=args.force
            )

    except KeyboardInterrupt:
        print("\nOperation cancelled by user", file=sys.stderr)
        return 130

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

    # Report results
    if success:
        print(f"\n✓ Successfully generated schemas for {args.journal}")
        print(f"  Journal key: {generator._normalize_journal_key(args.journal)}")
        print("  Generated files:")
        for schema_type, path in paths.items():
            print(f"    {schema_type}: {path}")
        print(f"\nIndex updated: {generator.index_path}")
        return 0
    else:
        print(f"\n✗ Failed to generate schemas for {args.journal}", file=sys.stderr)
        print("  Check errors above for details", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
