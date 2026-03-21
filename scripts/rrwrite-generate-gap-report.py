#!/usr/bin/env python3
"""
Generate citation gap analysis reports in Markdown and JSON formats.

Creates comprehensive, actionable reports with:
- Executive summary
- Current citation profile
- Critical gaps (must-cite)
- Recommended additions (should-cite)
- Optional citations (emerging work)
- Actionable recommendations

Usage:
    python scripts/rrwrite-generate-gap-report.py \
        --gap-analysis gap_analysis.json \
        --output-dir manuscript/citation_gap_analysis
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict
from collections import defaultdict


class GapReportGenerator:
    """Generate comprehensive gap analysis reports"""

    def __init__(self, gap_analysis: Dict):
        """
        Initialize report generator.

        Args:
            gap_analysis: Gap analysis results dictionary
        """
        self.analysis = gap_analysis
        self.gaps = gap_analysis.get('gaps', [])
        self.summary = gap_analysis.get('summary', {})

    def generate_executive_summary(self) -> str:
        """Generate executive summary section"""
        current_count = self.analysis.get('manuscript_citations', 0)
        total_gaps = self.summary.get('total_gaps', 0)
        critical_gaps = self.summary.get('by_priority', {}).get('critical', 0)
        important_gaps = self.summary.get('by_priority', {}).get('important', 0)

        return f"""## Executive Summary

**Analysis Date:** {datetime.now().strftime('%Y-%m-%d')}

**Current State:**
- **Current Citations:** {current_count} papers
- **Missing Citations:** {total_gaps} papers identified
- **Critical Gaps:** {critical_gaps} papers (must-cite)
- **Important Gaps:** {important_gaps} papers (should-cite)

**Recommendation:** {'Address all critical gaps before submission' if critical_gaps > 0 else 'Citation coverage appears adequate'}
"""

    def generate_current_citation_profile(self) -> str:
        """Generate current citation profile section"""
        current_count = self.analysis.get('manuscript_citations', 0)

        # Count by year from gaps (inferred)
        gap_years = defaultdict(int)
        for gap in self.gaps:
            year = gap.get('year', 0)
            if isinstance(year, int) and year > 0:
                gap_years[year] += 1

        output = f"""## Section 1: Current Citation Profile

**Total Citations in Manuscript:** {current_count}

**Note:** Detailed citation type breakdown requires access to manuscript's BibTeX file.
This analysis focuses on identifying gaps based on search results.
"""

        return output

    def format_gap_entry(self, gap: Dict, rank: int) -> str:
        """Format a single gap entry"""
        title = gap.get('title', 'Untitled')
        authors = gap.get('authors', 'Unknown authors')
        year = gap.get('year', 'Unknown')
        doi = gap.get('doi', 'No DOI')
        citations = gap.get('citations', 0) or gap.get('citationCount', 0)
        abstract = (gap.get('abstract') or 'No abstract available')[:200] + "..."

        similarity = gap.get('semantic_similarity', 0.0)
        cit_type = gap.get('citation_type', 'unknown')
        priority_score = gap.get('priority_score', 0)

        # Truncate long author lists
        if len(authors) > 100:
            authors = authors[:100] + "..."

        output = f"""### {rank}. {title}

**Authors:** {authors}
**Year:** {year}
**DOI:** {doi}
**Citations:** {citations:,}
**Type:** {cit_type}

**Why Missing:**
- Semantic overlap with manuscript: {similarity:.0%}
- Citation impact: {citations:,} citations
- Priority score: {priority_score}/10

**Relevance:**
{abstract}

**Recommended Section:** {'Methods' if cit_type in ['tool', 'method'] else 'Introduction/Discussion'}

**Suggested Context:**
"""

        # Add context suggestion based on type
        if cit_type == 'tool':
            output += f"\"For {title.split(':')[0] if ':' in title else 'this analysis'}, we used {title} [{authors.split(',')[0] if ',' in authors else authors} et al. {year}].\"\n"
        elif cit_type == 'method':
            output += f"\"Similar approaches have been developed, including {title} [{authors.split(',')[0] if ',' in authors else authors} et al. {year}].\"\n"
        elif cit_type == 'review':
            output += f"\"For a comprehensive review of this topic, see {title} [{authors.split(',')[0] if ',' in authors else authors} et al. {year}].\"\n"
        else:
            output += f"\"This work builds on recent advances in the field [{authors.split(',')[0] if ',' in authors else authors} et al. {year}].\"\n"

        output += "\n---\n\n"

        return output

    def generate_critical_gaps(self) -> str:
        """Generate critical gaps section (must-cite)"""
        critical_gaps = [g for g in self.gaps if g.get('priority') == 'critical']

        output = f"""## Section 2: Critical Gaps (Must-Cite)

**Count:** {len(critical_gaps)} papers

**Definition:** Highly-cited papers with direct methodological overlap or foundational relevance.
These papers should be cited to avoid reviewer criticism and demonstrate field awareness.

"""

        if not critical_gaps:
            output += "*No critical gaps identified. Current citation coverage appears adequate.*\n"
            return output

        for i, gap in enumerate(critical_gaps, 1):
            output += self.format_gap_entry(gap, i)

        return output

    def generate_recommended_additions(self) -> str:
        """Generate recommended additions section (should-cite)"""
        important_gaps = [g for g in self.gaps if g.get('priority') == 'important']

        output = f"""## Section 3: Recommended Additions (Should-Cite)

**Count:** {len(important_gaps)} papers

**Definition:** Papers with significant relevance but not critical for publication.
Adding these will strengthen the manuscript and broaden literature coverage.

"""

        if not important_gaps:
            output += "*No important gaps identified.*\n"
            return output

        # Group by citation type
        by_type = defaultdict(list)
        for gap in important_gaps:
            by_type[gap.get('citation_type', 'unknown')].append(gap)

        for cit_type, gaps_list in sorted(by_type.items()):
            output += f"### {cit_type.title()} Papers ({len(gaps_list)})\n\n"

            for i, gap in enumerate(gaps_list[:5], 1):  # Limit to top 5 per type
                output += self.format_gap_entry(gap, i)

        return output

    def generate_optional_citations(self) -> str:
        """Generate optional citations section (emerging work)"""
        optional_gaps = [g for g in self.gaps if g.get('priority') == 'optional']

        output = f"""## Section 4: Optional Citations (Emerging Work)

**Count:** {len(optional_gaps)} papers

**Definition:** Recent or less-cited papers that may be relevant for specific contexts.
Consider adding if discussing emerging trends or niche topics.

"""

        if not optional_gaps:
            output += "*No optional citations identified.*\n"
            return output

        # Show only top 10 by year + citations (normalize year to int)
        def sort_key(x):
            year = x.get('year', 0)
            # Convert year to int if it's a string
            if isinstance(year, str):
                try:
                    year = int(year)
                except (ValueError, TypeError):
                    year = 0
            citations = x.get('citations', 0)
            return (year, citations)

        optional_gaps.sort(key=sort_key, reverse=True)

        for i, gap in enumerate(optional_gaps[:10], 1):
            title = gap.get('title', 'Untitled')
            authors = gap.get('authors', 'Unknown')
            year = gap.get('year', 'Unknown')
            doi = gap.get('doi', 'No DOI')

            if len(authors) > 50:
                authors = authors[:50] + "..."

            output += f"{i}. **{title}**  \n"
            output += f"   {authors} ({year}) - DOI: {doi}\n\n"

        return output

    def generate_actionable_recommendations(self) -> str:
        """Generate actionable recommendations section"""
        critical_count = self.summary.get('by_priority', {}).get('critical', 0)
        important_count = self.summary.get('by_priority', {}).get('important', 0)
        optional_count = self.summary.get('by_priority', {}).get('optional', 0)

        output = f"""## Section 5: Actionable Recommendations

### Immediate Actions (Next Draft)

"""

        if critical_count > 0:
            output += f"1. **Add {critical_count} critical citations** identified in Section 2\n"
            output += f"   - These are must-cite papers with high impact and direct relevance\n"
            output += f"   - Allocate to Introduction and Methods sections\n\n"

        if important_count > 0:
            output += f"2. **Consider {important_count} important citations** from Section 3\n"
            output += f"   - Strengthen literature coverage\n"
            output += f"   - Prioritize by citation type relevance to your sections\n\n"

        output += """### Medium Priority (Post-Review)

"""

        if important_count > 5:
            output += f"3. **Review remaining important citations** ({important_count - 5} papers)\n"
            output += f"   - Address during revision if reviewers request broader coverage\n\n"

        output += """### Low Priority

"""

        if optional_count > 0:
            output += f"4. **Optional citations** ({optional_count} papers) can be added if:\n"
            output += f"   - Discussing emerging trends or niche topics\n"
            output += f"   - Reviewers request more recent references\n"
            output += f"   - Expanding discussion section\n\n"

        # Generate BibTeX suggestion
        output += """### Next Steps

1. **Download PDFs** for critical and important papers
2. **Add BibTeX entries** to `literature_citations.bib`
3. **Extract evidence quotes** to `literature_evidence.csv`
4. **Integrate citations** into manuscript sections
5. **Re-run gap analysis** to verify completeness

**Automated Workflow:**
```bash
# Update literature database
python scripts/rrwrite-search-literature.py --query "[your topic]" --max-results 50

# Re-run gap analysis
python scripts/rrwrite-gdoc-citation-gap-workflow.py --document-id [YOUR_DOC_ID]
```
"""

        return output

    def generate_markdown_report(self) -> str:
        """Generate complete Markdown report"""
        report = f"""# Citation Gap Analysis Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Analysis Source:** {self.analysis.get('manuscript_citations', 0)} manuscript citations vs {self.analysis.get('search_results', 0)} search results
**Similarity Threshold:** {self.analysis.get('similarity_threshold', 0.7):.0%}

---

{self.generate_executive_summary()}

---

{self.generate_current_citation_profile()}

---

{self.generate_critical_gaps()}

---

{self.generate_recommended_additions()}

---

{self.generate_optional_citations()}

---

{self.generate_actionable_recommendations()}

---

*Report generated by RRWrite Citation Gap Analyzer*
"""
        return report

    def generate_json_report(self) -> Dict:
        """Generate machine-readable JSON report"""
        return {
            'report_metadata': {
                'generated_at': datetime.now().isoformat(),
                'analysis_date': self.analysis.get('analysis_date'),
                'similarity_threshold': self.analysis.get('similarity_threshold', 0.7)
            },
            'summary': self.summary,
            'gaps_by_priority': {
                'critical': [g for g in self.gaps if g.get('priority') == 'critical'],
                'important': [g for g in self.gaps if g.get('priority') == 'important'],
                'optional': [g for g in self.gaps if g.get('priority') == 'optional']
            },
            'gaps_by_type': {
                cit_type: [g for g in self.gaps if g.get('citation_type') == cit_type]
                for cit_type in set(g.get('citation_type', 'unknown') for g in self.gaps)
            },
            'all_gaps': self.gaps
        }


def main():
    parser = argparse.ArgumentParser(
        description='Generate citation gap analysis reports',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        '--gap-analysis',
        type=Path,
        required=True,
        help='Gap analysis JSON file'
    )
    parser.add_argument(
        '--output-dir',
        type=Path,
        required=True,
        help='Output directory for reports'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Verbose output'
    )

    args = parser.parse_args()

    # Validate inputs
    if not args.gap_analysis.exists():
        print(f"❌ Error: Gap analysis file not found: {args.gap_analysis}", file=sys.stderr)
        return 1

    try:
        # Load gap analysis
        with open(args.gap_analysis) as f:
            gap_data = json.load(f)

        # Generate reports
        print("📊 Generating reports...")
        generator = GapReportGenerator(gap_data)

        # Create output directory
        args.output_dir.mkdir(parents=True, exist_ok=True)

        # Markdown report
        md_report = generator.generate_markdown_report()
        md_path = args.output_dir / 'citation_gap_report.md'
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(md_report)
        print(f"✓ Markdown report: {md_path}")

        # JSON report
        json_report = generator.generate_json_report()
        json_path = args.output_dir / 'citation_gap_report.json'
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(json_report, f, indent=2)
        print(f"✓ JSON report: {json_path}")

        # Summary
        print(f"\n✅ Reports generated successfully!")
        print(f"  Total gaps: {gap_data['summary']['total_gaps']}")
        print(f"  Critical: {gap_data['summary']['by_priority'].get('critical', 0)}")
        print(f"  Important: {gap_data['summary']['by_priority'].get('important', 0)}")
        print(f"  Optional: {gap_data['summary']['by_priority'].get('optional', 0)}")
        print(f"\n  Output directory: {args.output_dir}")

        return 0

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
