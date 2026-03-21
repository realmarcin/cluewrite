---
name: plot
description: Generate publication-quality plots from data files or DataFrames
tags: [visualization, plotting, figures, data-analysis]
---

# Plot Skill - Data Visualization Agent

Generate publication-quality plots from CSV/TSV data or pandas DataFrames using natural language descriptions.

## Usage

### Basic Syntax
```bash
/plot <data_file> "<plot_description>"
```

### Examples

**Bar chart:**
```bash
/plot results.csv "bar chart of citations by year"
```

**Scatter plot with trend:**
```bash
/plot feature_importance.csv "scatter plot of SHAP values vs feature importance with regression line"
```

**Heatmap:**
```bash
/plot correlation_matrix.csv "heatmap showing correlation between features"
```

**Box plot:**
```bash
/plot distributions.tsv "box plot comparing ecosystem diversity across biomes"
```

**Line plot:**
```bash
/plot timeseries.csv "line plot of citation counts over time by category"
```

**Multiple subplots:**
```bash
/plot metrics.csv "create 2x2 subplot grid: top-left accuracy, top-right precision, bottom-left recall, bottom-right F1 score"
```

## Advanced Options

### Specify columns explicitly
```bash
/plot data.csv "bar chart" --x ecosystem --y feature_count --hue category
```

### Customize appearance
```bash
/plot data.csv "scatter plot" --title "Feature Analysis" --figsize 10,8 --dpi 300
```

### Save in multiple formats
```bash
/plot data.csv "line plot" --output figure.png --formats png,pdf,svg
```

### Use existing DataFrame (from context)
```python
# In a Python cell or script
df = pd.read_csv('data.csv')
# Then use /plot with --dataframe flag
```

## Supported Plot Types

| Type | Description | Use Case |
|------|-------------|----------|
| `bar` | Bar chart | Categorical comparisons |
| `barh` | Horizontal bar chart | Long category names |
| `scatter` | Scatter plot | Relationships between variables |
| `line` | Line plot | Time series, trends |
| `box` | Box plot | Distribution comparisons |
| `violin` | Violin plot | Detailed distributions |
| `heatmap` | Heat map | Correlation matrices |
| `histogram` | Histogram | Single variable distribution |
| `kde` | Kernel density | Smooth distributions |
| `pair` | Pair plot | Multi-variable relationships |
| `count` | Count plot | Frequency counts |
| `strip` | Strip plot | Individual data points |
| `swarm` | Swarm plot | Categorical scatter |

## Style Presets

```bash
/plot data.csv "scatter plot" --style nature  # Nature journal style
/plot data.csv "bar chart" --style science   # Science journal style
/plot data.csv "line plot" --style minimal   # Minimal clean style
/plot data.csv "heatmap" --style dark        # Dark theme
```

## Output Options

**Default:** Saves to `figures/generated/` with timestamp
**Custom path:** `--output my_figure.png`
**Multiple formats:** `--formats png,pdf,svg`
**DPI:** `--dpi 300` (default) or `--dpi 600` (high-res)

## Examples with Real Data

### Example 1: Citation Gap Analysis Results
```bash
/plot manuscript/citation_gaps/gap_analysis_targeted.json \
  "scatter plot of citation count vs priority score, colored by gap type"
```

### Example 2: Repository Statistics
```bash
/plot data_tables/file_statistics.tsv \
  "horizontal bar chart showing top 20 files by size"
```

### Example 3: Feature Importance
```bash
/plot feature_importance.csv \
  "bar chart of top 30 features sorted by SHAP value with error bars"
```

### Example 4: Confusion Matrix
```bash
/plot confusion_matrix.csv \
  "heatmap with annotations showing prediction accuracy per ecosystem"
```

## Implementation Details

### Tools Available
- Python execution for data loading and processing
- matplotlib for plotting
- seaborn for statistical visualizations
- pandas for data manipulation
- Read/Write tools for file I/O

### Workflow
1. Parse user's plot description using LLM understanding
2. Load data from specified file or DataFrame
3. Determine appropriate plot type and parameters
4. Generate plot with publication-quality settings
5. Save in requested format(s)
6. Return figure path and preview

### Quality Standards
- 300 DPI default (publication quality)
- Vector formats (PDF, SVG) for scalability
- Seaborn styling for professional appearance
- Proper axis labels and legends
- Tight layout to avoid clipping

## Error Handling

**Invalid data file:**
```
❌ Error: File not found: data.csv
   Available files in current directory: [list]
```

**Missing columns:**
```
❌ Error: Column 'citations' not found in data
   Available columns: [feature, importance, p_value]
```

**Ambiguous plot request:**
```
⚠️  Multiple interpretations possible:
   1. Scatter plot of A vs B
   2. Line plot of A over B
   Which would you like? (1/2)
```

## Tips for Best Results

1. **Be specific:** "scatter plot of X vs Y" is better than "plot the data"
2. **Specify aesthetics:** Include "with trend line" or "colored by category"
3. **Use clear column names:** The skill will attempt to match fuzzy column names
4. **Check data first:** Use `head data.csv` to verify column names
5. **Iterate:** Start simple, then add customization

## Related Skills

- `/rrwrite-extract-figures-tables` - Extract figures from repository
- `/rrwrite-draft-section` - Use plots in manuscript sections

## Technical Notes

**Dependencies:** matplotlib, seaborn, pandas, numpy
**Performance:** Handles datasets up to ~1M rows efficiently
**Memory:** Loads entire dataset into memory (use sampling for huge files)
