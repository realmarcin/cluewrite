#!/usr/bin/env python3
"""
RRWrite Plotting Tool - Publication-Quality Data Visualization

Generate plots from CSV/TSV/JSON data with natural language descriptions.

Usage:
    python scripts/rrwrite-plot.py data.csv "scatter plot of x vs y"
    python scripts/rrwrite-plot.py data.tsv "bar chart" --x category --y count
    python scripts/rrwrite-plot.py data.json "heatmap" --output figure.pdf
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np

# Try to import plotting libraries
try:
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    import matplotlib.pyplot as plt
    import seaborn as sns
    PLOTTING_AVAILABLE = True
except ImportError:
    PLOTTING_AVAILABLE = False
    print("❌ Error: matplotlib and seaborn required")
    print("Install with: pip install matplotlib seaborn")
    sys.exit(1)


class PlotGenerator:
    """Generate publication-quality plots from data"""

    # Journal style presets
    STYLE_PRESETS = {
        'nature': {
            'style': 'whitegrid',
            'context': 'paper',
            'font_scale': 1.0,
            'palette': 'Set2'
        },
        'science': {
            'style': 'white',
            'context': 'paper',
            'font_scale': 0.9,
            'palette': 'muted'
        },
        'minimal': {
            'style': 'ticks',
            'context': 'paper',
            'font_scale': 1.0,
            'palette': 'colorblind'
        },
        'dark': {
            'style': 'darkgrid',
            'context': 'paper',
            'font_scale': 1.0,
            'palette': 'bright'
        }
    }

    def __init__(self, style: str = 'nature', dpi: int = 300):
        """Initialize plot generator with style settings"""
        self.dpi = dpi
        self.apply_style(style)

    def apply_style(self, style: str):
        """Apply journal style preset"""
        if style not in self.STYLE_PRESETS:
            print(f"⚠️  Unknown style '{style}', using 'nature'")
            style = 'nature'

        preset = self.STYLE_PRESETS[style]
        sns.set_style(preset['style'])
        sns.set_context(preset['context'], font_scale=preset['font_scale'])
        sns.set_palette(preset['palette'])

        # Publication quality settings
        plt.rcParams['figure.dpi'] = self.dpi
        plt.rcParams['savefig.dpi'] = self.dpi
        plt.rcParams['font.size'] = 10
        plt.rcParams['axes.labelsize'] = 11
        plt.rcParams['axes.titlesize'] = 12
        plt.rcParams['xtick.labelsize'] = 9
        plt.rcParams['ytick.labelsize'] = 9
        plt.rcParams['legend.fontsize'] = 9
        plt.rcParams['figure.titlesize'] = 13

    def load_data(self, file_path: Path) -> pd.DataFrame:
        """Load data from CSV, TSV, or JSON"""
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        suffix = file_path.suffix.lower()

        try:
            if suffix == '.csv':
                df = pd.read_csv(file_path)
            elif suffix == '.tsv':
                df = pd.read_csv(file_path, sep='\t')
            elif suffix == '.json':
                df = pd.read_json(file_path)
            elif suffix in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path)
            else:
                # Try CSV as default
                df = pd.read_csv(file_path)

            print(f"✓ Loaded {len(df)} rows, {len(df.columns)} columns")
            print(f"  Columns: {', '.join(df.columns.tolist())}")
            return df

        except Exception as e:
            raise ValueError(f"Error loading data: {e}")

    def infer_plot_params(
        self,
        df: pd.DataFrame,
        plot_type: str,
        description: Optional[str] = None,
        **kwargs
    ) -> Dict:
        """Infer plot parameters from description and data"""

        params = {
            'x': kwargs.get('x'),
            'y': kwargs.get('y'),
            'hue': kwargs.get('hue'),
            'title': kwargs.get('title', ''),
            'xlabel': kwargs.get('xlabel'),
            'ylabel': kwargs.get('ylabel'),
            'figsize': kwargs.get('figsize', (10, 6))
        }

        # If no columns specified, try to infer from data
        if not params['x'] and len(df.columns) >= 1:
            params['x'] = df.columns[0]
        if not params['y'] and len(df.columns) >= 2:
            params['y'] = df.columns[1]
        if not params['hue'] and len(df.columns) >= 3:
            # Only use hue if reasonable number of categories
            if df[df.columns[2]].nunique() <= 10:
                params['hue'] = df.columns[2]

        # Infer labels from column names if not specified
        if not params['xlabel'] and params['x']:
            params['xlabel'] = params['x'].replace('_', ' ').title()
        if not params['ylabel'] and params['y']:
            params['ylabel'] = params['y'].replace('_', ' ').title()

        return params

    def generate_plot(
        self,
        df: pd.DataFrame,
        plot_type: str,
        output_path: Path,
        description: Optional[str] = None,
        **kwargs
    ) -> Path:
        """Generate plot of specified type"""

        # Infer parameters
        params = self.infer_plot_params(df, plot_type, description, **kwargs)

        # Create figure
        figsize = params['figsize']
        fig, ax = plt.subplots(figsize=figsize)

        try:
            # Generate plot based on type
            if plot_type in ['bar', 'barplot']:
                sns.barplot(data=df, x=params['x'], y=params['y'],
                           hue=params['hue'], ax=ax)

            elif plot_type in ['barh', 'horizontal_bar']:
                sns.barplot(data=df, x=params['y'], y=params['x'],
                           hue=params['hue'], ax=ax, orient='h')

            elif plot_type in ['scatter', 'scatterplot']:
                sns.scatterplot(data=df, x=params['x'], y=params['y'],
                               hue=params['hue'], ax=ax, s=100, alpha=0.6)
                # Add trend line if specified
                if kwargs.get('trendline') or 'trend' in (description or '').lower():
                    x_data = df[params['x']].dropna()
                    y_data = df[params['y']].dropna()
                    z = np.polyfit(x_data, y_data, 1)
                    p = np.poly1d(z)
                    ax.plot(x_data, p(x_data), "r--", alpha=0.8, label='Trend')

            elif plot_type in ['line', 'lineplot']:
                sns.lineplot(data=df, x=params['x'], y=params['y'],
                            hue=params['hue'], ax=ax, marker='o')

            elif plot_type in ['box', 'boxplot']:
                sns.boxplot(data=df, x=params['x'], y=params['y'],
                           hue=params['hue'], ax=ax)

            elif plot_type in ['violin', 'violinplot']:
                sns.violinplot(data=df, x=params['x'], y=params['y'],
                              hue=params['hue'], ax=ax)

            elif plot_type in ['heatmap']:
                # For heatmap, use entire DataFrame or pivot
                if params['x'] and params['y'] and params.get('values'):
                    pivot_df = df.pivot(index=params['y'], columns=params['x'],
                                       values=params.get('values'))
                    sns.heatmap(pivot_df, ax=ax, cmap='viridis',
                               annot=True, fmt='.2f', cbar_kws={'label': params.get('values')})
                else:
                    # Assume data is already in matrix form
                    numeric_df = df.select_dtypes(include=[np.number])
                    sns.heatmap(numeric_df.corr(), ax=ax, cmap='coolwarm',
                               annot=True, fmt='.2f', center=0,
                               vmin=-1, vmax=1, cbar_kws={'label': 'Correlation'})

            elif plot_type in ['histogram', 'hist']:
                df[params['x']].hist(ax=ax, bins=kwargs.get('bins', 30),
                                    edgecolor='black', alpha=0.7)

            elif plot_type in ['kde', 'density']:
                sns.kdeplot(data=df, x=params['x'], hue=params['hue'],
                           ax=ax, fill=True, alpha=0.5)

            elif plot_type in ['count', 'countplot']:
                sns.countplot(data=df, x=params['x'], hue=params['hue'], ax=ax)

            elif plot_type in ['strip', 'stripplot']:
                sns.stripplot(data=df, x=params['x'], y=params['y'],
                             hue=params['hue'], ax=ax)

            elif plot_type in ['swarm', 'swarmplot']:
                sns.swarmplot(data=df, x=params['x'], y=params['y'],
                             hue=params['hue'], ax=ax)

            else:
                raise ValueError(f"Unknown plot type: {plot_type}")

            # Set labels and title
            if params['title']:
                ax.set_title(params['title'])
            if params['xlabel']:
                ax.set_xlabel(params['xlabel'])
            if params['ylabel']:
                ax.set_ylabel(params['ylabel'])

            # Rotate x-axis labels if too many or too long
            if params['x'] and df[params['x']].dtype == 'object':
                if df[params['x']].nunique() > 5 or df[params['x']].astype(str).str.len().max() > 10:
                    plt.xticks(rotation=45, ha='right')

            plt.tight_layout()

            # Save figure
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(output_path, bbox_inches='tight', dpi=self.dpi)
            plt.close()

            print(f"✓ Saved: {output_path}")
            return output_path

        except Exception as e:
            plt.close()
            raise ValueError(f"Error generating plot: {e}")


def parse_plot_description(description: str) -> Tuple[str, Dict]:
    """Parse natural language plot description to extract plot type and parameters"""

    description_lower = description.lower()

    # Detect plot type
    plot_type = 'scatter'  # default

    plot_type_keywords = {
        'bar': ['bar chart', 'bar plot', 'bar graph'],
        'barh': ['horizontal bar', 'barh'],
        'scatter': ['scatter plot', 'scatter', 'scatterplot'],
        'line': ['line plot', 'line chart', 'line graph', 'time series'],
        'box': ['box plot', 'boxplot', 'box-and-whisker'],
        'violin': ['violin plot', 'violinplot'],
        'heatmap': ['heatmap', 'heat map', 'correlation matrix'],
        'histogram': ['histogram', 'hist', 'distribution'],
        'kde': ['kde', 'density plot', 'kernel density'],
        'count': ['count plot', 'frequency'],
    }

    for ptype, keywords in plot_type_keywords.items():
        if any(kw in description_lower for kw in keywords):
            plot_type = ptype
            break

    # Detect special options
    params = {}

    if 'trend' in description_lower or 'regression' in description_lower:
        params['trendline'] = True

    return plot_type, params


def main():
    parser = argparse.ArgumentParser(
        description='Generate publication-quality plots from data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument('data', type=Path, help='Data file (CSV, TSV, JSON)')
    parser.add_argument('description', nargs='?', help='Natural language plot description')
    parser.add_argument('--type', choices=[
        'bar', 'barh', 'scatter', 'line', 'box', 'violin',
        'heatmap', 'histogram', 'kde', 'count', 'strip', 'swarm'
    ], help='Plot type (auto-detected from description if not specified)')
    parser.add_argument('--x', help='X-axis column')
    parser.add_argument('--y', help='Y-axis column')
    parser.add_argument('--hue', help='Color grouping column')
    parser.add_argument('--title', help='Plot title')
    parser.add_argument('--xlabel', help='X-axis label')
    parser.add_argument('--ylabel', help='Y-axis label')
    parser.add_argument('--figsize', help='Figure size as "width,height"')
    parser.add_argument('--output', type=Path, help='Output file path')
    parser.add_argument('--formats', default='png', help='Output formats (comma-separated: png,pdf,svg)')
    parser.add_argument('--style', default='nature',
                       choices=['nature', 'science', 'minimal', 'dark'],
                       help='Journal style preset')
    parser.add_argument('--dpi', type=int, default=300, help='Resolution (DPI)')
    parser.add_argument('--show-data', action='store_true', help='Show data preview')

    args = parser.parse_args()

    # Initialize generator
    generator = PlotGenerator(style=args.style, dpi=args.dpi)

    # Load data
    print(f"📊 Loading data from {args.data}...")
    try:
        df = generator.load_data(args.data)
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

    if args.show_data:
        print(f"\n📋 Data preview:")
        print(df.head())
        print(f"\n📊 Data types:")
        print(df.dtypes)
        return 0

    # Determine plot type
    if args.type:
        plot_type = args.type
        params = {}
    elif args.description:
        plot_type, params = parse_plot_description(args.description)
        print(f"🎨 Detected plot type: {plot_type}")
    else:
        print(f"❌ Error: Must specify either --type or provide description")
        return 1

    # Prepare output path
    if args.output:
        output_base = args.output.with_suffix('')
    else:
        output_dir = Path('figures/generated')
        output_dir.mkdir(parents=True, exist_ok=True)
        output_base = output_dir / f'plot_{plot_type}'

    # Parse figsize
    figsize = (10, 6)
    if args.figsize:
        try:
            w, h = map(float, args.figsize.split(','))
            figsize = (w, h)
        except:
            print(f"⚠️  Invalid figsize, using default (10, 6)")

    # Generate plots in requested formats
    formats = args.formats.split(',')
    output_paths = []

    for fmt in formats:
        output_path = output_base.with_suffix(f'.{fmt}')
        print(f"\n🎨 Generating {plot_type} plot...")

        try:
            path = generator.generate_plot(
                df=df,
                plot_type=plot_type,
                output_path=output_path,
                description=args.description,
                x=args.x,
                y=args.y,
                hue=args.hue,
                title=args.title,
                xlabel=args.xlabel,
                ylabel=args.ylabel,
                figsize=figsize,
                **params
            )
            output_paths.append(path)

        except Exception as e:
            print(f"❌ Error: {e}")
            return 1

    print(f"\n✅ Success! Generated {len(output_paths)} file(s)")
    for path in output_paths:
        print(f"   📁 {path}")

    return 0


if __name__ == '__main__':
    sys.exit(main())
