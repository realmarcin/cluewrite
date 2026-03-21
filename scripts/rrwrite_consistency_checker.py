#!/usr/bin/env python3
"""
ConsistencyChecker - Detects inconsistencies across manuscript.

Checks for:
- Terminology inconsistencies
- Citation style inconsistencies
- Figure/table numbering issues
- Abbreviation usage
"""

import re
from pathlib import Path
from typing import List, Dict, Set, Tuple
from collections import Counter, defaultdict


class ConsistencyChecker:
    """Detects consistency issues in manuscript."""

    def __init__(self, manuscript_dir: Path):
        """
        Initialize checker.

        Args:
            manuscript_dir: Path to manuscript directory
        """
        self.manuscript_dir = Path(manuscript_dir)
        self.sections_dir = manuscript_dir / "sections"
        self.issues = []

    def check_terminology(self) -> List[Dict[str, str]]:
        """Check for terminology inconsistencies."""
        issues = []

        # Common technical term variants to check
        term_variants = {
            "dataset": ["dataset", "data set", "data-set"],
            "workflow": ["workflow", "work flow", "work-flow"],
            "metadata": ["metadata", "meta data", "meta-data"],
            "database": ["database", "data base", "data-base"]
        }

        all_content = self._load_all_sections()

        for canonical, variants in term_variants.items():
            usage_counts = {}
            for variant in variants:
                # Case-insensitive count
                count = len(re.findall(rf'\b{variant}\b', all_content, re.IGNORECASE))
                if count > 0:
                    usage_counts[variant] = count

            # If multiple variants used, flag inconsistency
            if len(usage_counts) > 1:
                issues.append({
                    "type": "terminology",
                    "severity": "minor",
                    "description": f"Inconsistent usage of '{canonical}': {usage_counts}",
                    "suggestion": f"Standardize to one variant (recommend: '{canonical}')"
                })

        return issues

    def check_citation_style(self) -> List[Dict[str, str]]:
        """Check for citation style inconsistencies."""
        issues = []
        all_content = self._load_all_sections()

        # Find all citation patterns
        square_bracket = len(re.findall(r'\[@\w+\]', all_content))
        parenthetical = len(re.findall(r'\(@\w+\)', all_content))
        numbered = len(re.findall(r'\[\d+\]', all_content))

        styles_used = []
        if square_bracket > 0:
            styles_used.append(f"[@author] style ({square_bracket} instances)")
        if parenthetical > 0:
            styles_used.append(f"(@author) style ({parenthetical} instances)")
        if numbered > 0:
            styles_used.append(f"[N] numbered style ({numbered} instances)")

        if len(styles_used) > 1:
            issues.append({
                "type": "citation_style",
                "severity": "major",
                "description": f"Multiple citation styles detected: {', '.join(styles_used)}",
                "suggestion": "Standardize to single citation style ([@author] recommended for Markdown)"
            })

        return issues

    def check_figure_numbering(self) -> List[Dict[str, str]]:
        """Check for figure numbering issues."""
        issues = []

        # Load sections in order
        section_order = ["abstract", "introduction", "methods", "results", "discussion", "availability"]
        figure_numbers = []

        for section_name in section_order:
            section_path = self.sections_dir / f"{section_name}.md"
            if not section_path.exists():
                continue

            content = section_path.read_text(encoding="utf-8")

            # Find all "Figure N" references
            matches = re.findall(r'Figure\s+(\d+)', content, re.IGNORECASE)
            for match in matches:
                figure_numbers.append((section_name, int(match)))

        if not figure_numbers:
            return issues

        # Check for:
        # 1. Sequential numbering
        expected = 1
        for section, num in figure_numbers:
            if num != expected:
                issues.append({
                    "type": "figure_numbering",
                    "severity": "major",
                    "description": f"Figure numbering gap in {section}: expected {expected}, found {num}",
                    "suggestion": "Renumber figures sequentially"
                })
            expected = num + 1

        # 2. Duplicate numbers
        counts = Counter([num for _, num in figure_numbers])
        for num, count in counts.items():
            if count > 1:
                issues.append({
                    "type": "figure_numbering",
                    "severity": "critical",
                    "description": f"Figure {num} referenced {count} times",
                    "suggestion": "Ensure each figure has unique number"
                })

        return issues

    def check_table_numbering(self) -> List[Dict[str, str]]:
        """Check for table numbering issues."""
        issues = []

        section_order = ["abstract", "introduction", "methods", "results", "discussion", "availability"]
        table_numbers = []

        for section_name in section_order:
            section_path = self.sections_dir / f"{section_name}.md"
            if not section_path.exists():
                continue

            content = section_path.read_text(encoding="utf-8")

            # Find all "Table N" references
            matches = re.findall(r'Table\s+(\d+)', content, re.IGNORECASE)
            for match in matches:
                table_numbers.append((section_name, int(match)))

        if not table_numbers:
            return issues

        # Check sequential numbering
        expected = 1
        for section, num in table_numbers:
            if num != expected:
                issues.append({
                    "type": "table_numbering",
                    "severity": "major",
                    "description": f"Table numbering gap in {section}: expected {expected}, found {num}",
                    "suggestion": "Renumber tables sequentially"
                })
            expected = num + 1

        # Check duplicates
        counts = Counter([num for _, num in table_numbers])
        for num, count in counts.items():
            if count > 1:
                issues.append({
                    "type": "table_numbering",
                    "severity": "critical",
                    "description": f"Table {num} referenced {count} times",
                    "suggestion": "Ensure each table has unique number"
                })

        return issues

    def check_abbreviations(self) -> List[Dict[str, str]]:
        """Check for abbreviation consistency."""
        issues = []

        # Find all likely abbreviations (2-5 uppercase letters)
        all_content = self._load_all_sections()
        abbreviations = re.findall(r'\b([A-Z]{2,5})\b', all_content)

        # Count usage
        abbrev_counts = Counter(abbreviations)

        # Check if abbreviations are defined
        for abbrev, count in abbrev_counts.items():
            if count >= 3:  # Only check frequently used abbreviations
                # Look for definition pattern: "abbrev (ABBREV)"
                definition_pattern = rf'\w+\s+\({abbrev}\)'
                if not re.search(definition_pattern, all_content):
                    issues.append({
                        "type": "abbreviation",
                        "severity": "minor",
                        "description": f"Abbreviation '{abbrev}' used {count} times but not defined",
                        "suggestion": f"Define '{abbrev}' at first use"
                    })

        return issues

    def check_all(self) -> List[Dict[str, str]]:
        """Run all consistency checks."""
        all_issues = []

        all_issues.extend(self.check_terminology())
        all_issues.extend(self.check_citation_style())
        all_issues.extend(self.check_figure_numbering())
        all_issues.extend(self.check_table_numbering())
        all_issues.extend(self.check_abbreviations())

        self.issues = all_issues
        return all_issues

    def generate_report(self, output_path: Path) -> None:
        """Generate consistency report."""
        md_lines = []

        md_lines.append("# Manuscript Consistency Report")
        md_lines.append("")
        md_lines.append(f"**Total issues found:** {len(self.issues)}")
        md_lines.append("")

        # Group by severity
        by_severity = defaultdict(list)
        for issue in self.issues:
            by_severity[issue['severity']].append(issue)

        for severity in ["critical", "major", "minor"]:
            issues_at_level = by_severity[severity]
            if not issues_at_level:
                continue

            md_lines.append(f"## {severity.title()} Issues ({len(issues_at_level)})")
            md_lines.append("")

            for issue in issues_at_level:
                md_lines.append(f"### {issue['type'].replace('_', ' ').title()}")
                md_lines.append("")
                md_lines.append(f"**Description:** {issue['description']}")
                md_lines.append("")
                md_lines.append(f"**Suggestion:** {issue['suggestion']}")
                md_lines.append("")

        output_path.write_text('\n'.join(md_lines), encoding='utf-8')

    def _load_all_sections(self) -> str:
        """Load and concatenate all section content."""
        all_content = []

        section_order = ["abstract", "introduction", "methods", "results", "discussion", "availability"]

        for section_name in section_order:
            section_path = self.sections_dir / f"{section_name}.md"
            if section_path.exists():
                content = section_path.read_text(encoding="utf-8")
                all_content.append(content)

        return "\n\n".join(all_content)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: rrwrite_consistency_checker.py <manuscript_dir>")
        sys.exit(1)

    manuscript_dir = Path(sys.argv[1])
    checker = ConsistencyChecker(manuscript_dir)

    issues = checker.check_all()

    print(f"Found {len(issues)} consistency issues:")
    for issue in issues:
        print(f"  [{issue['severity'].upper()}] {issue['type']}: {issue['description']}")

    # Generate report
    report_path = manuscript_dir / "consistency_report.md"
    checker.generate_report(report_path)
    print(f"\nReport written to: {report_path}")
