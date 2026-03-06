#!/usr/bin/env python3
"""
Figure generation utilities for RRWrite manuscript pipeline.

This module provides tools for:
1. Automatically generating figures from repository data
2. Creating plots for manuscript sections
3. Selecting appropriate figures for each section
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import pandas as pd


class FigureGenerator:
    """Generate figures from repository analysis data."""

    # Standard figure formats for different use cases
    FIGURE_FORMATS = {
        'print': 'pdf',      # Vector format for print (scalable)
        'digital': 'png',    # Raster format for digital (300 DPI)
        'preview': 'png'     # Lower DPI for quick previews (150 DPI)
    }

    @staticmethod
    def generate_repo_figures(
        data_tables_dir: Path,
        output_dir: Path,
        formats: List[str] = ['png', 'pdf']
    ) -> Dict[str, List[Path]]:
        """
        Generate all standard repository analysis figures.

        Creates figures:
        1. file_size_distribution.png/pdf - Histogram of file sizes by category
        2. repository_composition.png/pdf - Pie/bar chart of file types
        3. code_complexity_metrics.png/pdf - Scatter plot of code metrics
        4. research_topics_radar.png/pdf - Radar chart of detected research areas

        Args:
            data_tables_dir: Directory containing TSV data tables
            output_dir: Directory to save generated figures
            formats: List of output formats ('png', 'pdf', 'svg')

        Returns:
            Dict mapping figure names to lists of output paths
        """
        data_tables_dir = Path(data_tables_dir)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        figure_paths = {}

        try:
            import matplotlib
            matplotlib.use('Agg')  # Non-interactive backend
            import matplotlib.pyplot as plt
            import seaborn as sns

            # Set publication-quality defaults
            sns.set_context("paper")
            sns.set_style("whitegrid")
            plt.rcParams['figure.dpi'] = 300
            plt.rcParams['savefig.dpi'] = 300
            plt.rcParams['font.size'] = 10
            plt.rcParams['axes.labelsize'] = 10
            plt.rcParams['axes.titlesize'] = 11
            plt.rcParams['legend.fontsize'] = 9

        except ImportError:
            print("Warning: matplotlib/seaborn not installed. Skipping figure generation.")
            print("Install with: pip install matplotlib seaborn")
            return figure_paths

        # Figure 1: Repository Composition
        composition_paths = FigureGenerator._generate_composition_figure(
            data_tables_dir, output_dir, formats
        )
        if composition_paths:
            figure_paths['repository_composition'] = composition_paths

        # Figure 2: File Size Distribution
        size_dist_paths = FigureGenerator._generate_size_distribution_figure(
            data_tables_dir, output_dir, formats
        )
        if size_dist_paths:
            figure_paths['file_size_distribution'] = size_dist_paths

        # Figure 3: Research Topics
        topics_paths = FigureGenerator._generate_research_topics_figure(
            data_tables_dir, output_dir, formats
        )
        if topics_paths:
            figure_paths['research_topics'] = topics_paths

        return figure_paths

    @staticmethod
    def _generate_composition_figure(
        data_tables_dir: Path,
        output_dir: Path,
        formats: List[str]
    ) -> List[Path]:
        """Generate repository composition bar chart."""
        import matplotlib.pyplot as plt
        import seaborn as sns

        stats_file = data_tables_dir / "repository_statistics.tsv"
        if not stats_file.exists():
            return []

        # Load data
        df = pd.read_csv(stats_file, sep='\t', comment='#')

        if df.empty or 'category' not in df.columns:
            return []

        # Create figure
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))

        # Plot 1: File count by category
        sns.barplot(data=df, x='category', y='file_count', ax=ax1, palette='viridis')
        ax1.set_xlabel('File Category')
        ax1.set_ylabel('File Count')
        ax1.set_title('Repository Composition by File Count')
        ax1.tick_params(axis='x', rotation=45)

        # Plot 2: Total size by category
        if 'total_size_mb' in df.columns:
            sns.barplot(data=df, x='category', y='total_size_mb', ax=ax2, palette='plasma')
            ax2.set_xlabel('File Category')
            ax2.set_ylabel('Total Size (MB)')
            ax2.set_title('Repository Composition by Size')
            ax2.tick_params(axis='x', rotation=45)

        plt.tight_layout()

        # Save in requested formats
        output_paths = []
        for fmt in formats:
            output_path = output_dir / f"repository_composition.{fmt}"
            plt.savefig(output_path, format=fmt, bbox_inches='tight', dpi=300)
            output_paths.append(output_path)

        plt.close()

        return output_paths

    @staticmethod
    def _generate_size_distribution_figure(
        data_tables_dir: Path,
        output_dir: Path,
        formats: List[str]
    ) -> List[Path]:
        """Generate file size distribution histogram/box plot."""
        import matplotlib.pyplot as plt
        import seaborn as sns

        inventory_file = data_tables_dir / "file_inventory.tsv"
        if not inventory_file.exists():
            return []

        # Load data
        df = pd.read_csv(inventory_file, sep='\t', comment='#')

        if df.empty or 'size_bytes' not in df.columns:
            return []

        # Convert to KB for readability
        df['size_kb'] = df['size_bytes'] / 1024

        # Create figure
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))

        # Plot 1: Histogram (log scale)
        ax1.hist(df['size_kb'], bins=50, edgecolor='black', alpha=0.7)
        ax1.set_xlabel('File Size (KB)')
        ax1.set_ylabel('Frequency')
        ax1.set_title('File Size Distribution')
        ax1.set_xscale('log')
        ax1.set_yscale('log')

        # Plot 2: Box plot by category
        if 'type' in df.columns:
            sns.boxplot(data=df, x='type', y='size_kb', ax=ax2)
            ax2.set_xlabel('File Category')
            ax2.set_ylabel('File Size (KB, log scale)')
            ax2.set_title('File Size by Category')
            ax2.set_yscale('log')
            ax2.tick_params(axis='x', rotation=45)

        plt.tight_layout()

        # Save in requested formats
        output_paths = []
        for fmt in formats:
            output_path = output_dir / f"file_size_distribution.{fmt}"
            plt.savefig(output_path, format=fmt, bbox_inches='tight', dpi=300)
            output_paths.append(output_path)

        plt.close()

        return output_paths

    @staticmethod
    def _generate_research_topics_figure(
        data_tables_dir: Path,
        output_dir: Path,
        formats: List[str]
    ) -> List[Path]:
        """Generate research topics bar chart."""
        import matplotlib.pyplot as plt
        import seaborn as sns

        topics_file = data_tables_dir / "research_indicators.tsv"
        if not topics_file.exists():
            return []

        # Load data
        df = pd.read_csv(topics_file, sep='\t', comment='#')

        if df.empty or 'topic' not in df.columns:
            return []

        # Create figure
        fig, ax = plt.subplots(figsize=(8, 5))

        # Create color map based on confidence
        if 'confidence' in df.columns:
            confidence_colors = {'high': '#2ecc71', 'medium': '#f39c12', 'low': '#e74c3c'}
            colors = [confidence_colors.get(c, '#95a5a6') for c in df['confidence']]
        else:
            colors = sns.color_palette('viridis', len(df))

        # Plot horizontal bar chart
        if 'evidence_count' in df.columns:
            ax.barh(df['topic'], df['evidence_count'], color=colors)
            ax.set_xlabel('Evidence Count')
        ax.set_ylabel('Research Topic')
        ax.set_title('Detected Research Topics')

        # Add confidence legend if available
        if 'confidence' in df.columns:
            from matplotlib.patches import Patch
            legend_elements = [
                Patch(facecolor='#2ecc71', label='High Confidence'),
                Patch(facecolor='#f39c12', label='Medium Confidence'),
                Patch(facecolor='#e74c3c', label='Low Confidence')
            ]
            ax.legend(handles=legend_elements, loc='lower right')

        plt.tight_layout()

        # Save in requested formats
        output_paths = []
        for fmt in formats:
            output_path = output_dir / f"research_topics.{fmt}"
            plt.savefig(output_path, format=fmt, bbox_inches='tight', dpi=300)
            output_paths.append(output_path)

        plt.close()

        return output_paths

    @staticmethod
    def generate_custom_plot(
        data: pd.DataFrame,
        plot_type: str,
        output_path: Path,
        **kwargs
    ) -> Path:
        """
        Generate custom plot from DataFrame.

        Args:
            data: DataFrame containing plot data
            plot_type: Type of plot ('bar', 'scatter', 'line', 'box', 'heatmap')
            output_path: Path to save figure
            **kwargs: Additional arguments for plot customization
                - title: Plot title
                - xlabel: X-axis label
                - ylabel: Y-axis label
                - x_col: Column name for x-axis
                - y_col: Column name for y-axis
                - hue_col: Column for color grouping
                - figsize: Tuple of (width, height)

        Returns:
            Path to saved figure
        """
        import matplotlib.pyplot as plt
        import seaborn as sns

        # Extract kwargs
        title = kwargs.get('title', '')
        xlabel = kwargs.get('xlabel', '')
        ylabel = kwargs.get('ylabel', '')
        x_col = kwargs.get('x_col')
        y_col = kwargs.get('y_col')
        hue_col = kwargs.get('hue_col')
        figsize = kwargs.get('figsize', (8, 6))

        # Create figure
        fig, ax = plt.subplots(figsize=figsize)

        # Generate plot based on type
        if plot_type == 'bar':
            sns.barplot(data=data, x=x_col, y=y_col, hue=hue_col, ax=ax)
        elif plot_type == 'scatter':
            sns.scatterplot(data=data, x=x_col, y=y_col, hue=hue_col, ax=ax)
        elif plot_type == 'line':
            sns.lineplot(data=data, x=x_col, y=y_col, hue=hue_col, ax=ax)
        elif plot_type == 'box':
            sns.boxplot(data=data, x=x_col, y=y_col, hue=hue_col, ax=ax)
        elif plot_type == 'heatmap':
            sns.heatmap(data, ax=ax, cmap='viridis', annot=True, fmt='.2f')

        # Set labels and title
        if title:
            ax.set_title(title)
        if xlabel:
            ax.set_xlabel(xlabel)
        if ylabel:
            ax.set_ylabel(ylabel)

        plt.tight_layout()

        # Save figure
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path, bbox_inches='tight', dpi=300)
        plt.close()

        return output_path


class FigureSelector:
    """Select appropriate figures for manuscript sections."""

    # Mapping of section names to relevant figure files
    SECTION_FIGURE_MAP = {
        'methods': [
            'repository_composition.png',
            'research_topics.png'
        ],
        'results': [
            'repository_composition.png',
            'file_size_distribution.png',
            'research_topics.png'
        ],
        'introduction': [
            'research_topics.png'
        ],
        'discussion': [
            'repository_composition.png'
        ]
    }

    @staticmethod
    def get_figures_for_section(
        section_name: str,
        figures_dir: Path
    ) -> List[Dict[str, any]]:
        """
        Get list of available figures relevant to a manuscript section.

        Args:
            section_name: Name of manuscript section (e.g., 'methods', 'results')
            figures_dir: Directory containing figure files

        Returns:
            List of dicts with keys: name, path, exists, caption
        """
        figures_dir = Path(figures_dir)
        section_lower = section_name.lower()

        # Get relevant figure names for this section
        figure_names = FigureSelector.SECTION_FIGURE_MAP.get(section_lower, [])

        # Check which figures exist
        available_figures = []
        for figure_name in figure_names:
            # Check for both PNG and PDF versions
            for ext in ['png', 'pdf']:
                base_name = Path(figure_name).stem
                figure_path = figures_dir / f"{base_name}.{ext}"

                if figure_path.exists():
                    available_figures.append({
                        'name': figure_name,
                        'path': figure_path,
                        'exists': True,
                        'caption': FigureSelector._generate_caption(base_name)
                    })
                    break  # Only add once if multiple formats exist

        return available_figures

    @staticmethod
    def _generate_caption(figure_name: str) -> str:
        """Generate default caption for figure based on filename."""
        captions = {
            'repository_composition': 'Repository composition showing distribution of files by category and size.',
            'file_size_distribution': 'File size distribution across repository categories (log scale).',
            'research_topics': 'Detected research topics ranked by evidence count and confidence level.',
        }

        return captions.get(figure_name, f"Figure: {figure_name.replace('_', ' ').title()}")

    @staticmethod
    def get_all_figures(figures_dir: Path) -> List[Path]:
        """
        Get all figure files in directory.

        Args:
            figures_dir: Directory containing figure files

        Returns:
            List of paths to figure files (PNG, PDF, SVG)
        """
        figures_dir = Path(figures_dir)

        if not figures_dir.exists():
            return []

        figure_files = []
        for ext in ['png', 'pdf', 'svg', 'jpg', 'jpeg']:
            figure_files.extend(figures_dir.glob(f"*.{ext}"))

        return sorted(figure_files)

    @staticmethod
    def get_figures_from_manifest(
        section_name: str,
        manifest_path: Path,
        prioritize_repo_figures: bool = True
    ) -> List[Dict[str, any]]:
        """
        Get figures for section from manifest, prioritizing repository figures.

        Args:
            section_name: Name of manuscript section (e.g., 'methods', 'results')
            manifest_path: Path to figure_manifest.json
            prioritize_repo_figures: Sort by priority (1=from_repo first, 2=generated second)

        Returns:
            List of figure metadata dicts suitable for the section
        """
        import json

        manifest_path = Path(manifest_path)

        if not manifest_path.exists():
            return []

        # Load manifest
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)

        # Filter by recommended sections
        section_figures = [
            fig for fig in manifest.get('figures', [])
            if section_name in fig.get('recommended_sections', [])
        ]

        # Sort by priority (ascending: 1=from_repo, 2=generated)
        if prioritize_repo_figures:
            section_figures.sort(key=lambda f: f['priority'])

        return section_figures
