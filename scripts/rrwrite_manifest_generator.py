#!/usr/bin/env python3
"""
Manifest Generator for RRWrite

Creates and validates JSON manifests for figures and tables extracted from
repositories or generated during analysis.

Manifest format provides:
- Unique IDs for each figure/table
- Priority levels (1=from_repo, 2=generated)
- Section recommendations
- Default captions
- Source tracking
"""

import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

# Optional dependency for validation
try:
    import jsonschema
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False


class ManifestGenerator:
    """Generate manifest files for figures and tables."""

    def __init__(self, manuscript_dir: Path):
        """Initialize manifest generator.

        Args:
            manuscript_dir: Path to manuscript directory
        """
        self.manuscript_dir = Path(manuscript_dir)
        self.figures_dir = self.manuscript_dir / "figures"
        self.tables_dir = self.manuscript_dir / "tables"

    def create_figure_manifest(self, figures: List[Dict[str, Any]]) -> Path:
        """Create figure manifest JSON file.

        Args:
            figures: List of figure metadata dicts

        Returns:
            Path to created manifest file
        """
        manifest_path = self.figures_dir / "figure_manifest.json"
        self.figures_dir.mkdir(parents=True, exist_ok=True)

        # Sort by priority (1 first, then 2) and then by ID
        sorted_figures = sorted(figures, key=lambda f: (f['priority'], f['id']))

        manifest = {
            "version": "1.0",
            "created_at": datetime.now().isoformat(),
            "total_figures": len(figures),
            "figures_from_repo": sum(1 for f in figures if f['source'] == 'from_repo'),
            "figures_generated": sum(1 for f in figures if f['source'] == 'generated'),
            "figures": sorted_figures
        }

        # Write manifest
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)

        return manifest_path

    def create_table_manifest(self, tables: List[Dict[str, Any]]) -> Path:
        """Create table manifest JSON file.

        Args:
            tables: List of table metadata dicts

        Returns:
            Path to created manifest file
        """
        manifest_path = self.tables_dir / "table_manifest.json"
        self.tables_dir.mkdir(parents=True, exist_ok=True)

        # Sort by priority and ID
        sorted_tables = sorted(tables, key=lambda t: (t['priority'], t['id']))

        manifest = {
            "version": "1.0",
            "created_at": datetime.now().isoformat(),
            "total_tables": len(tables),
            "tables_from_repo": sum(1 for t in tables if t['source'] == 'from_repo'),
            "tables_generated": sum(1 for t in tables if t['source'] == 'generated'),
            "tables": sorted_tables
        }

        # Write manifest
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)

        return manifest_path

    def load_figure_manifest(self) -> Dict[str, Any]:
        """Load existing figure manifest.

        Returns:
            Manifest dict or empty dict if not found
        """
        manifest_path = self.figures_dir / "figure_manifest.json"

        if not manifest_path.exists():
            return {}

        with open(manifest_path, 'r') as f:
            return json.load(f)

    def load_table_manifest(self) -> Dict[str, Any]:
        """Load existing table manifest.

        Returns:
            Manifest dict or empty dict if not found
        """
        manifest_path = self.tables_dir / "table_manifest.json"

        if not manifest_path.exists():
            return {}

        with open(manifest_path, 'r') as f:
            return json.load(f)

    def get_figures_for_section(
        self,
        section_name: str,
        prioritize_repo: bool = True
    ) -> List[Dict[str, Any]]:
        """Get figures recommended for specific section.

        Args:
            section_name: Name of manuscript section
            prioritize_repo: Sort by priority (repo figures first)

        Returns:
            List of figure metadata dicts
        """
        manifest = self.load_figure_manifest()

        if not manifest:
            return []

        # Filter by section
        section_figures = [
            fig for fig in manifest.get('figures', [])
            if section_name in fig.get('recommended_sections', [])
        ]

        # Sort by priority if requested
        if prioritize_repo:
            section_figures.sort(key=lambda f: f['priority'])

        return section_figures

    def get_tables_for_section(
        self,
        section_name: str,
        prioritize_repo: bool = True
    ) -> List[Dict[str, Any]]:
        """Get tables recommended for specific section.

        Args:
            section_name: Name of manuscript section
            prioritize_repo: Sort by priority (repo tables first)

        Returns:
            List of table metadata dicts
        """
        manifest = self.load_table_manifest()

        if not manifest:
            return []

        # Filter by section
        section_tables = [
            table for table in manifest.get('tables', [])
            if section_name in table.get('recommended_sections', [])
        ]

        # Sort by priority if requested
        if prioritize_repo:
            section_tables.sort(key=lambda t: t['priority'])

        return section_tables


class ManifestValidator:
    """Validate manifest files against schemas."""

    def __init__(self, schemas_dir: Path):
        """Initialize validator.

        Args:
            schemas_dir: Path to directory containing JSON schemas
        """
        self.schemas_dir = Path(schemas_dir)

    def validate_figure_manifest(self, manifest_path: Path) -> tuple[bool, List[str]]:
        """Validate figure manifest against schema.

        Args:
            manifest_path: Path to manifest file

        Returns:
            Tuple of (is_valid, error_messages)
        """
        if not HAS_JSONSCHEMA:
            return False, ["jsonschema module not installed. Install with: pip install jsonschema"]

        schema_path = self.schemas_dir / "figure_manifest_schema.json"

        if not schema_path.exists():
            return False, [f"Schema not found: {schema_path}"]

        # Load schema and manifest
        with open(schema_path, 'r') as f:
            schema = json.load(f)

        with open(manifest_path, 'r') as f:
            manifest = json.load(f)

        # Validate
        errors = []
        try:
            jsonschema.validate(instance=manifest, schema=schema)
            return True, []
        except jsonschema.exceptions.ValidationError as e:
            errors.append(str(e))
            return False, errors

    def validate_table_manifest(self, manifest_path: Path) -> tuple[bool, List[str]]:
        """Validate table manifest against schema.

        Args:
            manifest_path: Path to manifest file

        Returns:
            Tuple of (is_valid, error_messages)
        """
        if not HAS_JSONSCHEMA:
            return False, ["jsonschema module not installed. Install with: pip install jsonschema"]

        schema_path = self.schemas_dir / "table_manifest_schema.json"

        if not schema_path.exists():
            return False, [f"Schema not found: {schema_path}"]

        # Load schema and manifest
        with open(schema_path, 'r') as f:
            schema = json.load(f)

        with open(manifest_path, 'r') as f:
            manifest = json.load(f)

        # Validate
        errors = []
        try:
            jsonschema.validate(instance=manifest, schema=schema)
            return True, []
        except jsonschema.exceptions.ValidationError as e:
            errors.append(str(e))
            return False, errors


def main():
    """Demo/testing entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Manifest generator utilities")
    parser.add_argument("--manuscript-dir", required=True, help="Manuscript directory")
    parser.add_argument("--section", help="Get figures/tables for specific section")
    parser.add_argument("--validate", action="store_true", help="Validate manifests")
    parser.add_argument("--schemas-dir", default="schemas", help="Path to schemas directory")

    args = parser.parse_args()

    generator = ManifestGenerator(Path(args.manuscript_dir))

    if args.validate:
        validator = ManifestValidator(Path(args.schemas_dir))

        # Validate figure manifest
        fig_manifest_path = Path(args.manuscript_dir) / "figures" / "figure_manifest.json"
        if fig_manifest_path.exists():
            valid, errors = validator.validate_figure_manifest(fig_manifest_path)
            if valid:
                print(f"✓ Figure manifest valid: {fig_manifest_path}")
            else:
                print(f"✗ Figure manifest invalid: {fig_manifest_path}")
                for error in errors:
                    print(f"  - {error}")

        # Validate table manifest
        table_manifest_path = Path(args.manuscript_dir) / "tables" / "table_manifest.json"
        if table_manifest_path.exists():
            valid, errors = validator.validate_table_manifest(table_manifest_path)
            if valid:
                print(f"✓ Table manifest valid: {table_manifest_path}")
            else:
                print(f"✗ Table manifest invalid: {table_manifest_path}")
                for error in errors:
                    print(f"  - {error}")

    elif args.section:
        # Get figures/tables for section
        figures = generator.get_figures_for_section(args.section)
        tables = generator.get_tables_for_section(args.section)

        print(f"\nFigures for section '{args.section}':")
        for fig in figures:
            print(f"  [{fig['priority']}] {fig['id']}: {fig['path']}")

        print(f"\nTables for section '{args.section}':")
        for table in tables:
            print(f"  [{table['priority']}] {table['id']}: {table['path']}")

    else:
        # Show summary
        fig_manifest = generator.load_figure_manifest()
        table_manifest = generator.load_table_manifest()

        if fig_manifest:
            print(f"Figure manifest:")
            print(f"  Total: {fig_manifest.get('total_figures', 0)}")
            print(f"  From repo: {fig_manifest.get('figures_from_repo', 0)}")
            print(f"  Generated: {fig_manifest.get('figures_generated', 0)}")

        if table_manifest:
            print(f"\nTable manifest:")
            print(f"  Total: {table_manifest.get('total_tables', 0)}")
            print(f"  From repo: {table_manifest.get('tables_from_repo', 0)}")
            print(f"  Generated: {table_manifest.get('tables_generated', 0)}")


if __name__ == "__main__":
    main()
