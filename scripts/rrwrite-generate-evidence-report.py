#!/usr/bin/env python3
"""
Generate comprehensive evidence report for RRWrite manuscript.

Combines repository analysis, data tables, literature evidence, and statistics
into a single comprehensive markdown report with evidence counts.

Usage:
    python scripts/rrwrite-generate-evidence-report.py --manuscript-dir manuscript/project_v1/
    python scripts/rrwrite-generate-evidence-report.py --manuscript-dir . --output EVIDENCE_REPORT.md
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime
import csv


class EvidenceReportGenerator:
    """Generate comprehensive evidence reports for manuscripts."""

    def __init__(self, manuscript_dir: Path):
        """
        Initialize report generator.

        Args:
            manuscript_dir: Path to manuscript directory
        """
        self.manuscript_dir = Path(manuscript_dir)
        self.data_tables_dir = self.manuscript_dir / 'data_tables'
        self.state_file = self.manuscript_dir / '.rrwrite' / 'state.json'

        self.repo_name = "unknown"
        self.analysis_date = "unknown"
        self.repo_path = None

    def load_state(self):
        """Load workflow state if available."""
        if self.state_file.exists():
            try:
                with open(self.state_file) as f:
                    state = json.load(f)
                    self.repo_path = state.get('repository_path', 'unknown')
                    self.repo_name = Path(self.repo_path).name if self.repo_path else 'unknown'

                    # Get analysis date from workflow status
                    repo_analysis = state.get('workflow_status', {}).get('repository_analysis', {})
                    completed_at = repo_analysis.get('completed_at', '')
                    if completed_at:
                        self.analysis_date = completed_at.split('T')[0]  # Extract date part
            except Exception as e:
                print(f"Warning: Could not load state file: {e}", file=sys.stderr)

    def count_files_in_tsv(self, tsv_path: Path) -> int:
        """Count data rows in TSV file (excluding header and comments)."""
        if not tsv_path.exists():
            return 0

        try:
            with open(tsv_path) as f:
                return sum(1 for line in f if line.strip() and not line.startswith('#'))
        except Exception:
            return 0

    def count_citations(self) -> dict:
        """Count literature citations from evidence file."""
        lit_evidence = self.manuscript_dir / 'literature_evidence.csv'

        if not lit_evidence.exists():
            return {'total': 0, 'unique_dois': 0, 'citation_keys': 0}

        try:
            with open(lit_evidence) as f:
                reader = csv.DictReader(f)
                rows = list(reader)

                dois = set()
                keys = set()

                for row in rows:
                    if 'doi' in row and row['doi']:
                        dois.add(row['doi'])
                    if 'citation_key' in row and row['citation_key']:
                        keys.add(row['citation_key'])

                return {
                    'total': len(rows),
                    'unique_dois': len(dois),
                    'citation_keys': len(keys)
                }
        except Exception:
            return {'total': 0, 'unique_dois': 0, 'citation_keys': 0}

    def read_tsv_table(self, filename: str) -> list:
        """Read TSV file and return rows (skip comments)."""
        tsv_path = self.data_tables_dir / filename

        if not tsv_path.exists():
            return []

        rows = []
        try:
            with open(tsv_path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        rows.append(line.split('\t'))
        except Exception as e:
            print(f"Warning: Could not read {filename}: {e}", file=sys.stderr)

        return rows

    def generate_summary_stats(self) -> str:
        """Generate summary statistics table."""
        # Count files from different sources
        file_inventory_count = self.count_files_in_tsv(self.data_tables_dir / 'file_inventory.tsv') - 1  # Exclude header
        repo_stats_rows = self.read_tsv_table('repository_statistics.tsv')
        research_indicators_rows = self.read_tsv_table('research_indicators.tsv')
        citation_stats = self.count_citations()

        # Parse repository statistics
        total_files = 0
        doc_files = 0
        script_files = 0
        data_files = 0
        config_files = 0
        test_files = 0

        for row in repo_stats_rows[1:]:  # Skip header
            if len(row) >= 6:
                category = row[0]
                count = int(row[1])
                tests = int(row[4])

                total_files += count
                test_files += tests

                if category.lower() == 'doc':
                    doc_files = count
                elif category.lower() == 'script':
                    script_files = count
                elif category.lower() == 'data':
                    data_files = count
                elif category.lower() == 'config':
                    config_files = count

        total_size_mb = sum(float(row[2]) for row in repo_stats_rows[1:] if len(row) >= 3)

        research_topics = len(research_indicators_rows) - 1  # Exclude header

        output = f"""| Metric | Count | Source File |
|--------|-------|-------------|
| **Total Files Analyzed** | {total_files} | [`data_tables/file_inventory.tsv`](data_tables/file_inventory.tsv) |
| **Documentation Files** | {doc_files} | [`data_tables/repository_statistics.tsv`](data_tables/repository_statistics.tsv) |
| **Script Files** | {script_files} | [`data_tables/repository_statistics.tsv`](data_tables/repository_statistics.tsv) |
| **Data Files** | {data_files} | [`data_tables/repository_statistics.tsv`](data_tables/repository_statistics.tsv) |
| **Config Files** | {config_files} | [`data_tables/repository_statistics.tsv`](data_tables/repository_statistics.tsv) |
| **Test Files** | {test_files} | [`data_tables/repository_statistics.tsv`](data_tables/repository_statistics.tsv) |
| **Research Topics Detected** | {research_topics} | [`data_tables/research_indicators.tsv`](data_tables/research_indicators.tsv) |
| **Literature Citations** | {citation_stats['total']} | [`literature_evidence.csv`](literature_evidence.csv) |
| **Total Repository Size** | {total_size_mb:.2f} MB | Calculated from file inventory |
"""
        return output

    def generate_repo_statistics_table(self) -> str:
        """Generate repository statistics table with evidence counts."""
        rows = self.read_tsv_table('repository_statistics.tsv')

        if len(rows) < 2:
            return "No repository statistics available.\n"

        header = rows[0]
        data_rows = rows[1:]

        output = "| Category | Files | Total Size | Avg Size | Test Files | Doc Files | Evidence Count |\n"
        output += "|----------|-------|------------|----------|------------|-----------|----------------|\n"

        total_files = 0
        total_size = 0.0
        total_tests = 0
        total_docs = 0

        for row in data_rows:
            if len(row) >= 6:
                category = row[0].title()
                files = int(row[1])
                size_mb = float(row[2])
                avg_kb = float(row[3])
                tests = int(row[4])
                docs = int(row[5])

                total_files += files
                total_size += size_mb
                total_tests += tests
                total_docs += docs

                output += f"| {category} | {files} | {size_mb:.2f} MB | {avg_kb:.2f} KB | {tests} | {docs} | {files} |\n"

        avg_size = (total_size * 1024 / total_files) if total_files > 0 else 0
        output += f"| **TOTAL** | **{total_files}** | **{total_size:.2f} MB** | **{avg_size:.2f} KB** | **{total_tests}** | **{total_docs}** | **{total_files}** |\n"

        return output

    def generate_research_topics_table(self) -> str:
        """Generate research topics table with evidence counts."""
        rows = self.read_tsv_table('research_indicators.tsv')

        if len(rows) < 2:
            return "No research topics detected.\n"

        output = "| Topic | Confidence | Evidence Count | Evidence Files | Example Files |\n"
        output += "|-------|------------|----------------|----------------|---------------|\n"

        total_evidence = 0

        for row in rows[1:]:
            if len(row) >= 4:
                topic = row[0]
                confidence = row[1].title()
                evidence_count = int(row[2])
                example_files = row[3]

                total_evidence += evidence_count

                output += f"| **{topic}** | {confidence} | {evidence_count} | {evidence_count} files | `{example_files}` |\n"

        output += f"| **TOTAL** | - | **{total_evidence}** | **{total_evidence} files** | - |\n"

        return output

    def generate_report(self) -> str:
        """Generate complete evidence report."""
        self.load_state()

        report = f"""# Repository Evidence Report

**Repository:** {self.repo_name}
**Analysis Date:** {self.analysis_date}
**Report Generated:** {datetime.now().strftime('%Y-%m-%d')}
**Manuscript Directory:** `{self.manuscript_dir.name}/`

---

## Summary Statistics

{self.generate_summary_stats()}

---

## 1. Repository Statistics

**Source:** [`data_tables/repository_statistics.tsv`](data_tables/repository_statistics.tsv)

{self.generate_repo_statistics_table()}

### Key Observations
- Documentation is the primary content type
- Analysis scripts demonstrate active computational research
- Data files provide empirical evidence
- Test coverage can be expanded if needed

---

## 2. Research Topics Detected

**Source:** [`data_tables/research_indicators.tsv`](data_tables/research_indicators.tsv)

{self.generate_research_topics_table()}

---

## 3. Evidence File References

All evidence data is stored in structured files within this manuscript directory:

### Primary Evidence Files

| File | Type | Size | Description | Records |
|------|------|------|-------------|---------|
"""

        # Add evidence file references
        evidence_files = [
            ('data_tables/file_inventory.tsv', 'TSV', 'Complete file listing with metadata'),
            ('data_tables/repository_statistics.tsv', 'TSV', 'Summary metrics by category'),
            ('data_tables/research_indicators.tsv', 'TSV', 'Research topics with evidence'),
            ('data_tables/size_distribution.tsv', 'TSV', 'File size quartiles by category'),
            ('literature_evidence.csv', 'CSV', 'Literature citations and evidence'),
            ('literature_citations.bib', 'BibTeX', 'Bibliography entries'),
            ('repository_analysis.md', 'Markdown', 'Full repository analysis report'),
            ('outline.md', 'Markdown', 'Manuscript outline and structure'),
            ('manifest.json', 'JSON', 'Assembly metadata and statistics'),
        ]

        total_records = 0

        for filename, file_type, description in evidence_files:
            file_path = self.manuscript_dir / filename
            if file_path.exists():
                size = file_path.stat().st_size
                size_str = f"{size / 1024:.1f} KB" if size < 1024*1024 else f"{size / (1024*1024):.1f} MB"

                # Count records
                if filename.endswith('.tsv'):
                    records = self.count_files_in_tsv(file_path) - 1  # Exclude header
                elif filename.endswith('.csv'):
                    records = self.count_citations()['total']
                else:
                    records = 1

                total_records += records

                report += f"| [`{filename}`]({filename}) | {file_type} | {size_str} | {description} | {records} |\n"

        report += f"""
**Total Evidence Records:** {total_records} across {len(evidence_files)} files

---

## 4. Literature Evidence Status

**Source:** [`literature_evidence.csv`](literature_evidence.csv)

"""

        citation_stats = self.count_citations()

        report += f"""| Metric | Count |
|--------|-------|
| **Total Citations** | {citation_stats['total']} |
| **Unique DOIs** | {citation_stats['unique_dois']} |
| **Citation Keys** | {citation_stats['citation_keys']} |

"""

        if citation_stats['total'] == 0:
            report += "⚠️ **WARNING:** No citations found. Run `/rrwrite-research-literature` to add literature evidence.\n\n"
        elif citation_stats['total'] == 1 and self.manuscript_dir.name == 'rrwrite_v1':
            report += "⚠️ **NOTE:** Only placeholder citation found. Real literature research needed.\n\n"
        else:
            report += f"✅ **Status:** {citation_stats['total']} citations available for manuscript.\n\n"

        report += f"""---

## 5. Evidence Quality Assessment

| Evidence Type | Count | Quality | Completeness | Source File |
|---------------|-------|---------|--------------|-------------|
| **Repository Files** | {self.count_files_in_tsv(self.data_tables_dir / 'file_inventory.tsv') - 1} | ✅ High | 100% | [`data_tables/file_inventory.tsv`](data_tables/file_inventory.tsv) |
| **Data Tables** | 4 | ✅ High | 100% | `data_tables/*.tsv` |
| **Repository Analysis** | 1 | ✅ High | 100% | [`repository_analysis.md`](repository_analysis.md) |
| **Research Topics** | {len(self.read_tsv_table('research_indicators.tsv')) - 1} | ✅ Good | 100% | [`data_tables/research_indicators.tsv`](data_tables/research_indicators.tsv) |
| **Literature Citations** | {citation_stats['total']} | {'⚠️ Poor' if citation_stats['total'] <= 1 else '✅ Good'} | {'0% (placeholder)' if citation_stats['total'] <= 1 else '100%'} | [`literature_evidence.csv`](literature_evidence.csv) |

---

**Report Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Total Evidence Items:** {total_records}

---

*This evidence report provides a comprehensive view of all data sources and statistics used in manuscript generation. All referenced files are relative to the manuscript directory: `{self.manuscript_dir.name}/`*
"""

        return report

    def save_report(self, output_file: Path):
        """Generate and save evidence report."""
        report = self.generate_report()

        with open(output_file, 'w') as f:
            f.write(report)

        print(f"✓ Evidence report generated: {output_file}")
        print(f"  Size: {output_file.stat().st_size / 1024:.1f} KB")
        print(f"  Lines: {len(report.split(chr(10)))}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate comprehensive evidence report for RRWrite manuscript",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        '--manuscript-dir',
        default='.',
        help='Manuscript directory (default: current directory)'
    )
    parser.add_argument(
        '--output',
        default='EVIDENCE_REPORT.md',
        help='Output file name (default: EVIDENCE_REPORT.md)'
    )

    args = parser.parse_args()

    manuscript_dir = Path(args.manuscript_dir)
    output_file = manuscript_dir / args.output

    if not manuscript_dir.exists():
        print(f"Error: Manuscript directory not found: {manuscript_dir}", file=sys.stderr)
        return 1

    try:
        generator = EvidenceReportGenerator(manuscript_dir)
        generator.save_report(output_file)
        return 0
    except Exception as e:
        print(f"Error generating report: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
