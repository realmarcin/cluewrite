#!/usr/bin/env python3
"""
Figure and Table Extraction for RRWrite

Extracts existing figures/tables from analyzed repositories and generates
supplementary visualizations. Creates manifest files with priority metadata.

Priority system:
- Priority 1: Original repository figures/tables (from_repo/)
- Priority 2: Generated analysis visualizations (generated/)

Usage:
    python scripts/rrwrite-extract-figures-tables.py \
        --repo-path /path/to/analyzed/repo \
        --manuscript-dir manuscript/project_v1 \
        --extract figures,tables \
        --generate figures
"""

import argparse
import json
import shutil
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging

# Import existing generators
try:
    from rrwrite_figure_generator import FigureGenerator
    from rrwrite_manifest_generator import ManifestGenerator
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from rrwrite_figure_generator import FigureGenerator
    from rrwrite_manifest_generator import ManifestGenerator


class FigureTableExtractor:
    """Extract figures and tables from repository and generate supplementary content."""

    # File patterns for detection
    FIGURE_PATTERNS = ['*.png', '*.jpg', '*.jpeg', '*.pdf', '*.svg', '*.eps']
    TABLE_PATTERNS = ['*.csv', '*.tsv', '*.xlsx', '*.xls']

    # Exclusion patterns (thumbnails, icons, temp files)
    EXCLUDE_PATTERNS = [
        r'.*thumb.*',
        r'.*icon.*',
        r'.*logo.*',
        r'.*badge.*',
        r'\.git/',
        r'node_modules/',
        r'__pycache__/',
        r'\.pytest_cache/',
        r'\.ipynb_checkpoints/',
        r'build/',
        r'dist/'
    ]

    # Size limits
    MAX_FIGURE_SIZE_MB = 10
    MAX_TABLE_SIZE_MB = 5

    def __init__(self, repo_path: Path, manuscript_dir: Path):
        """Initialize extractor.

        Args:
            repo_path: Path to analyzed repository
            repo_path: Path to manuscript output directory
        """
        self.repo_path = Path(repo_path).resolve()
        self.manuscript_dir = Path(manuscript_dir).resolve()

        # Create output directories
        self.figures_from_repo = self.manuscript_dir / "figures" / "from_repo"
        self.figures_generated = self.manuscript_dir / "figures" / "generated"
        self.tables_from_repo = self.manuscript_dir / "tables" / "from_repo"
        self.tables_generated = self.manuscript_dir / "tables" / "generated"

        self.logger = logging.getLogger(__name__)

    def extract_repository_figures(self) -> List[Dict[str, any]]:
        """Extract existing figures from repository.

        Returns:
            List of figure metadata dicts
        """
        self.logger.info(f"Scanning repository for figures: {self.repo_path}")

        figure_files = []
        for pattern in self.FIGURE_PATTERNS:
            figure_files.extend(self.repo_path.rglob(pattern))

        # Filter out excluded patterns and oversized files
        filtered_figures = []
        for fig_path in figure_files:
            # Check exclusions
            if self._should_exclude(fig_path):
                self.logger.debug(f"Excluding: {fig_path.relative_to(self.repo_path)}")
                continue

            # Check size
            size_mb = fig_path.stat().st_size / (1024 * 1024)
            if size_mb > self.MAX_FIGURE_SIZE_MB:
                self.logger.warning(
                    f"Skipping large figure ({size_mb:.1f}MB): {fig_path.relative_to(self.repo_path)}"
                )
                continue

            filtered_figures.append(fig_path)

        self.logger.info(f"Found {len(filtered_figures)} figures (filtered from {len(figure_files)})")

        # Copy figures to manuscript directory
        self.figures_from_repo.mkdir(parents=True, exist_ok=True)

        extracted_metadata = []
        for idx, fig_path in enumerate(filtered_figures, start=1):
            # Generate unique filename while preserving original
            rel_path = fig_path.relative_to(self.repo_path)
            dest_name = self._sanitize_filename(fig_path.name)
            dest_path = self.figures_from_repo / dest_name

            # Handle duplicates
            if dest_path.exists():
                stem = dest_path.stem
                suffix = dest_path.suffix
                counter = 1
                while dest_path.exists():
                    dest_name = f"{stem}_{counter}{suffix}"
                    dest_path = self.figures_from_repo / dest_name
                    counter += 1

            # Copy file
            shutil.copy2(fig_path, dest_path)
            self.logger.debug(f"Copied: {rel_path} → {dest_path.relative_to(self.manuscript_dir)}")

            # Create metadata
            metadata = {
                "id": f"fig_repo_{idx:03d}",
                "path": str(dest_path.relative_to(self.manuscript_dir)),
                "source": "from_repo",
                "priority": 1,
                "original_path": str(rel_path),
                "recommended_sections": self._infer_sections_from_path(fig_path),
                "default_caption": self._generate_caption_from_filename(fig_path),
                "generating_script": self._find_generating_script(fig_path)
            }
            extracted_metadata.append(metadata)

        # Create README index
        self._create_figures_readme(self.figures_from_repo, extracted_metadata)

        return extracted_metadata

    def extract_repository_tables(self) -> List[Dict[str, any]]:
        """Extract existing data tables from repository.

        Returns:
            List of table metadata dicts
        """
        self.logger.info(f"Scanning repository for tables: {self.repo_path}")

        table_files = []
        for pattern in self.TABLE_PATTERNS:
            table_files.extend(self.repo_path.rglob(pattern))

        # Filter exclusions and oversized files
        filtered_tables = []
        for table_path in table_files:
            if self._should_exclude(table_path):
                self.logger.debug(f"Excluding: {table_path.relative_to(self.repo_path)}")
                continue

            size_mb = table_path.stat().st_size / (1024 * 1024)
            if size_mb > self.MAX_TABLE_SIZE_MB:
                self.logger.warning(
                    f"Skipping large table ({size_mb:.1f}MB): {table_path.relative_to(self.repo_path)}"
                )
                continue

            filtered_tables.append(table_path)

        self.logger.info(f"Found {len(filtered_tables)} tables (filtered from {len(table_files)})")

        # Copy tables to manuscript directory
        self.tables_from_repo.mkdir(parents=True, exist_ok=True)

        extracted_metadata = []
        for idx, table_path in enumerate(filtered_tables, start=1):
            rel_path = table_path.relative_to(self.repo_path)
            dest_name = self._sanitize_filename(table_path.name)
            dest_path = self.tables_from_repo / dest_name

            # Handle duplicates
            if dest_path.exists():
                stem = dest_path.stem
                suffix = dest_path.suffix
                counter = 1
                while dest_path.exists():
                    dest_name = f"{stem}_{counter}{suffix}"
                    dest_path = self.tables_from_repo / dest_name
                    counter += 1

            # Copy file
            shutil.copy2(table_path, dest_path)
            self.logger.debug(f"Copied: {rel_path} → {dest_path.relative_to(self.manuscript_dir)}")

            # Create metadata
            metadata = {
                "id": f"table_repo_{idx:03d}",
                "path": str(dest_path.relative_to(self.manuscript_dir)),
                "source": "from_repo",
                "priority": 1,
                "original_path": str(rel_path),
                "recommended_sections": self._infer_sections_from_path(table_path),
                "default_caption": self._generate_caption_from_filename(table_path),
                "generating_script": self._find_generating_script(table_path)
            }
            extracted_metadata.append(metadata)

        return extracted_metadata

    def generate_supplementary_figures(self) -> List[Dict[str, any]]:
        """Generate supplementary figures from repository analysis data.

        Returns:
            List of generated figure metadata dicts
        """
        self.logger.info("Generating supplementary analysis figures")

        self.figures_generated.mkdir(parents=True, exist_ok=True)

        # Check for data_tables directory from repository analysis
        data_tables_dir = self.manuscript_dir / "data_tables"
        if not data_tables_dir.exists():
            self.logger.warning(f"No data_tables directory found: {data_tables_dir}")
            self.logger.warning("Run repository analysis first to generate data tables")
            return []

        # Generate figures using existing FigureGenerator
        generated_paths = FigureGenerator.generate_repo_figures(
            data_tables_dir=data_tables_dir,
            output_dir=self.figures_generated,
            formats=['png', 'pdf']
        )

        # Create metadata for generated figures
        generated_metadata = []
        for idx, (figure_name, paths) in enumerate(generated_paths.items(), start=1):
            # Use PNG path as primary (PDF is alternate format)
            png_path = next((p for p in paths if p.suffix == '.png'), paths[0])

            metadata = {
                "id": f"fig_gen_{idx:03d}",
                "path": str(png_path.relative_to(self.manuscript_dir)),
                "source": "generated",
                "priority": 2,
                "recommended_sections": self._get_generated_figure_sections(figure_name),
                "default_caption": self._get_generated_figure_caption(figure_name)
            }
            generated_metadata.append(metadata)

        self.logger.info(f"Generated {len(generated_metadata)} supplementary figures")

        return generated_metadata

    def generate_supplementary_tables(self) -> List[Dict[str, any]]:
        """Generate supplementary tables from repository analysis data.

        Returns:
            List of generated table metadata dicts
        """
        self.logger.info("Generating supplementary analysis tables")

        self.tables_generated.mkdir(parents=True, exist_ok=True)

        # Copy data_tables to generated directory (these are analysis outputs)
        data_tables_dir = self.manuscript_dir / "data_tables"
        if not data_tables_dir.exists():
            self.logger.warning(f"No data_tables directory found: {data_tables_dir}")
            return []

        generated_metadata = []
        for idx, table_file in enumerate(data_tables_dir.glob("*.tsv"), start=1):
            dest_path = self.tables_generated / table_file.name
            shutil.copy2(table_file, dest_path)

            metadata = {
                "id": f"table_gen_{idx:03d}",
                "path": str(dest_path.relative_to(self.manuscript_dir)),
                "source": "generated",
                "priority": 2,
                "recommended_sections": ["methods", "results"],
                "default_caption": f"Repository analysis: {table_file.stem.replace('_', ' ')}"
            }
            generated_metadata.append(metadata)

        self.logger.info(f"Generated {len(generated_metadata)} supplementary tables")

        return generated_metadata

    def _should_exclude(self, file_path: Path) -> bool:
        """Check if file matches exclusion patterns."""
        path_str = str(file_path)
        for pattern in self.EXCLUDE_PATTERNS:
            if re.search(pattern, path_str, re.IGNORECASE):
                return True
        return False

    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for safe filesystem use."""
        # Replace problematic characters
        safe_name = re.sub(r'[^\w\-\.]', '_', filename)
        # Remove consecutive underscores
        safe_name = re.sub(r'_+', '_', safe_name)
        return safe_name

    def _infer_sections_from_path(self, file_path: Path) -> List[str]:
        """Infer recommended manuscript sections from file path/name."""
        path_lower = str(file_path).lower()
        sections = []

        # Common patterns in path names
        if any(word in path_lower for word in ['result', 'output', 'plot', 'graph']):
            sections.append('results')
        if any(word in path_lower for word in ['method', 'workflow', 'pipeline', 'process']):
            sections.append('methods')
        if any(word in path_lower for word in ['intro', 'overview', 'diagram']):
            sections.append('introduction')
        if any(word in path_lower for word in ['discuss', 'comparison', 'analysis']):
            sections.append('discussion')

        # Default if no patterns match
        if not sections:
            sections = ['results']

        return sections

    def _generate_caption_from_filename(self, file_path: Path) -> str:
        """Generate default caption from filename."""
        # Clean up filename for caption
        name = file_path.stem
        # Replace underscores/hyphens with spaces
        caption = re.sub(r'[_-]+', ' ', name)
        # Remove common prefixes
        caption = re.sub(r'^(fig|figure|table|plot)\s*\d*\s*', '', caption, flags=re.IGNORECASE)
        # Capitalize first letter
        caption = caption.strip().capitalize()

        return caption if caption else file_path.stem

    def _find_generating_script(self, file_path: Path) -> Optional[str]:
        """Try to find the script that generated this figure/table.

        Searches for Python/R scripts in the same directory that reference the file.
        """
        parent_dir = file_path.parent
        filename = file_path.name

        # Search for scripts that might have generated this file
        for script_ext in ['*.py', '*.R', '*.r', '*.ipynb']:
            for script in parent_dir.glob(script_ext):
                try:
                    content = script.read_text(errors='ignore')
                    # Look for filename reference (without extension or with)
                    if filename in content or file_path.stem in content:
                        return str(script.relative_to(self.repo_path))
                except Exception:
                    continue

        return None

    def _get_generated_figure_sections(self, figure_name: str) -> List[str]:
        """Get recommended sections for generated figures."""
        section_map = {
            'repository_composition': ['methods', 'results'],
            'file_size_distribution': ['methods', 'results'],
            'research_topics': ['introduction', 'methods']
        }
        return section_map.get(figure_name, ['results'])

    def _get_generated_figure_caption(self, figure_name: str) -> str:
        """Get default caption for generated figures."""
        caption_map = {
            'repository_composition': 'Repository composition showing distribution of files by category and size',
            'file_size_distribution': 'File size distribution across repository categories',
            'research_topics': 'Detected research topics ranked by evidence count'
        }
        return caption_map.get(figure_name, figure_name.replace('_', ' ').capitalize())

    def _create_figures_readme(self, figures_dir: Path, metadata: List[Dict]):
        """Create README index for figures directory."""
        readme_path = figures_dir / "README.md"

        lines = [
            f"# Figures from Repository\n",
            f"\nExtracted {len(metadata)} figures from analyzed repository.\n",
            f"\n## Figure Index\n"
        ]

        for fig in metadata:
            lines.append(f"\n### {fig['id']}: {fig['default_caption']}")
            lines.append(f"- **File**: `{Path(fig['path']).name}`")
            lines.append(f"- **Original**: `{fig['original_path']}`")
            lines.append(f"- **Sections**: {', '.join(fig['recommended_sections'])}")
            if fig['generating_script']:
                lines.append(f"- **Script**: `{fig['generating_script']}`")

        readme_path.write_text('\n'.join(lines))
        self.logger.info(f"Created index: {readme_path.relative_to(self.manuscript_dir)}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Extract figures and tables from repository for manuscript"
    )
    parser.add_argument(
        "--repo-path",
        required=True,
        help="Path to analyzed repository"
    )
    parser.add_argument(
        "--manuscript-dir",
        required=True,
        help="Path to manuscript output directory"
    )
    parser.add_argument(
        "--extract",
        default="figures,tables",
        help="What to extract: 'figures', 'tables', or 'figures,tables' (default: both)"
    )
    parser.add_argument(
        "--generate",
        default="figures,tables",
        help="What to generate: 'figures', 'tables', or 'figures,tables' (default: both)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)

    # Parse options
    extract_opts = set(args.extract.lower().split(','))
    generate_opts = set(args.generate.lower().split(','))

    # Initialize extractor
    extractor = FigureTableExtractor(
        repo_path=args.repo_path,
        manuscript_dir=args.manuscript_dir
    )

    # Extract repository content
    all_figures = []
    all_tables = []

    if 'figures' in extract_opts:
        logger.info("=== Extracting Repository Figures ===")
        repo_figures = extractor.extract_repository_figures()
        all_figures.extend(repo_figures)

    if 'tables' in extract_opts:
        logger.info("\n=== Extracting Repository Tables ===")
        repo_tables = extractor.extract_repository_tables()
        all_tables.extend(repo_tables)

    # Generate supplementary content
    if 'figures' in generate_opts:
        logger.info("\n=== Generating Supplementary Figures ===")
        gen_figures = extractor.generate_supplementary_figures()
        all_figures.extend(gen_figures)

    if 'tables' in generate_opts:
        logger.info("\n=== Generating Supplementary Tables ===")
        gen_tables = extractor.generate_supplementary_tables()
        all_tables.extend(gen_tables)

    # Create manifests
    logger.info("\n=== Creating Manifests ===")
    manifest_generator = ManifestGenerator(Path(args.manuscript_dir))

    if all_figures:
        figure_manifest_path = manifest_generator.create_figure_manifest(all_figures)
        logger.info(f"✓ Figure manifest: {figure_manifest_path}")

    if all_tables:
        table_manifest_path = manifest_generator.create_table_manifest(all_tables)
        logger.info(f"✓ Table manifest: {table_manifest_path}")

    # Summary
    logger.info("\n=== Extraction Summary ===")
    logger.info(f"Figures from repository: {sum(1 for f in all_figures if f['source'] == 'from_repo')}")
    logger.info(f"Figures generated: {sum(1 for f in all_figures if f['source'] == 'generated')}")
    logger.info(f"Tables from repository: {sum(1 for t in all_tables if t['source'] == 'from_repo')}")
    logger.info(f"Tables generated: {sum(1 for t in all_tables if t['source'] == 'generated')}")
    logger.info(f"\n✓ Extraction complete!")


if __name__ == "__main__":
    main()
