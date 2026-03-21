# Plotting Quick Start Guide

## New `/plot` Skill Available!

Generate publication-quality plots from data using natural language descriptions.

## Basic Usage

### Method 1: Use the Skill (Recommended)
```bash
/plot data.csv "scatter plot of X vs Y with trend line"
```

### Method 2: CLI Tool
```bash
python3 scripts/rrwrite-plot.py data.csv "bar chart showing citations by category"
```

## Real Examples

### Example 1: Citation Gap Analysis
```bash
# Scatter plot showing gap priorities
python3 scripts/rrwrite-plot.py \
  manuscript/citation_gaps/gap_analysis_targeted.json \
  "scatter plot of citations vs priority_score colored by type" \
  --output figures/gap_analysis_scatter.png
```

### Example 2: Feature Importance
```bash
# Bar chart of top features
python3 scripts/rrwrite-plot.py \
  feature_importance.csv \
  "horizontal bar chart of top 20 features by SHAP value" \
  --output figures/top_features.pdf
```

### Example 3: Correlation Heatmap
```bash
# Heatmap of feature correlations
python3 scripts/rrwrite-plot.py \
  correlation_matrix.csv \
  "heatmap with annotations" \
  --output figures/correlation_heatmap.png
```

### Example 4: Time Series
```bash
# Line plot over time
python3 scripts/rrwrite-plot.py \
  citations_over_time.csv \
  "line plot of citation counts by year grouped by journal" \
  --output figures/citations_timeline.pdf
```

### Example 5: Distribution Comparison
```bash
# Box plot comparing groups
python3 scripts/rrwrite-plot.py \
  ecosystem_diversity.tsv \
  "box plot comparing alpha diversity across ecosystem types" \
  --output figures/diversity_comparison.png
```

## Advanced Options

### Save Multiple Formats
```bash
python3 scripts/rrwrite-plot.py data.csv "scatter plot" \
  --formats png,pdf,svg  # Get all three formats
```

### Specify Columns Explicitly
```bash
python3 scripts/rrwrite-plot.py data.csv "bar chart" \
  --x ecosystem_type \
  --y feature_count \
  --hue category \
  --title "Feature Distribution by Ecosystem"
```

### Change Style
```bash
python3 scripts/rrwrite-plot.py data.csv "line plot" \
  --style science  # Options: nature, science, minimal, dark
```

### High Resolution
```bash
python3 scripts/rrwrite-plot.py data.csv "scatter plot" \
  --dpi 600  # High-res for print
```

### Preview Data First
```bash
python3 scripts/rrwrite-plot.py data.csv --show-data
```

## Supported Plot Types

| Type | Description | Example Use |
|------|-------------|-------------|
| `scatter` | Scatter plot | Correlation between variables |
| `bar` | Bar chart | Category comparisons |
| `barh` | Horizontal bar | Long category names |
| `line` | Line plot | Time series, trends |
| `box` | Box plot | Distribution comparison |
| `violin` | Violin plot | Detailed distributions |
| `heatmap` | Heat map | Correlation matrices |
| `histogram` | Histogram | Single variable distribution |
| `kde` | Density plot | Smooth distributions |
| `count` | Count plot | Frequency counts |
| `strip` | Strip plot | Individual points |
| `swarm` | Swarm plot | Categorical scatter |

## Natural Language Features

The tool understands:
- **Plot types:** "scatter plot", "bar chart", "heatmap"
- **Relationships:** "X vs Y", "X over time", "X by category"
- **Grouping:** "colored by Z", "grouped by type"
- **Enhancements:** "with trend line", "with error bars"
- **Ordering:** "top 20", "sorted by value"

## Tips for Best Results

1. **Be specific:** "scatter plot of citations vs year" > "plot the data"
2. **Check columns:** Use `--show-data` to see available columns
3. **Start simple:** Get basic plot first, then add customization
4. **Use full paths:** Specify complete file paths to avoid confusion
5. **Multiple formats:** Always save PDF for publications (vector format)

## Common Patterns

### Pattern 1: Quick Exploratory Plot
```bash
# Just look at the data
python3 scripts/rrwrite-plot.py data.csv --show-data

# Make a quick scatter
python3 scripts/rrwrite-plot.py data.csv "scatter plot"
```

### Pattern 2: Publication-Ready Figure
```bash
python3 scripts/rrwrite-plot.py data.csv "scatter plot" \
  --x feature_importance \
  --y citations \
  --hue category \
  --title "Feature Importance vs Citation Count" \
  --style nature \
  --formats pdf,png \
  --dpi 300 \
  --output figures/figure1.pdf
```

### Pattern 3: Batch Processing
```bash
# Create multiple plots from same data
for type in scatter bar box; do
  python3 scripts/rrwrite-plot.py data.csv "$type plot" \
    --output figures/analysis_$type.png
done
```

## Integration with RRWrite

The plotting tool integrates with RRWrite manuscript pipeline:

1. **Extract data:** Use RRWrite to analyze repository
2. **Generate plots:** Create figures with `/plot`
3. **Include in manuscript:** Reference plots in sections
4. **Assemble:** RRWrite includes figures automatically

## Troubleshooting

**Error: "matplotlib not installed"**
```bash
pip install matplotlib seaborn pandas numpy
```

**Error: "Column not found"**
```bash
# Check available columns first
python3 scripts/rrwrite-plot.py data.csv --show-data
```

**Error: "Invalid plot type"**
```bash
# Use one of: bar, scatter, line, box, violin, heatmap, etc.
# Or use natural language description
```

**Warning: "Too many categories"**
```bash
# Limit data before plotting
head -50 data.csv | python3 scripts/rrwrite-plot.py - "bar chart"
```

## Next Steps

- Try plotting your citation gap analysis results
- Create figures for your manuscript
- Experiment with different styles and formats
- Use in combination with other RRWrite tools

📚 **Full documentation:** `.claude/skills/plot/SKILL.md`
