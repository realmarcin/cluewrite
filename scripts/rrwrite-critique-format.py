#!/usr/bin/env python3
"""
Format review script - Stage 2 of two-stage review.

Focus: Citation formatting, structure compliance, journal requirements.
Mindset: Copy editor - trust content, verify presentation.

Usage:
    python scripts/rrwrite-critique-format.py --file manuscript/manuscript.md --journal bioinformatics --output manuscript/critique_format_v1.md
"""

import argparse
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Set


class FormatReviewer:
    """Review formatting and structure compliance."""

    JOURNAL_REQUIREMENTS = {
        'nature': {
            'abstract_max_words': 150,
            'max_tables': 4,
            'max_figures': 8,
            'required_sections': ['Abstract', 'Introduction', 'Results', 'Discussion', 'Methods']
        },
        'plos': {
            'abstract_max_words': 300,
            'max_tables': 10,
            'max_figures': 10,
            'required_sections': ['Abstract', 'Introduction', 'Methods', 'Results', 'Discussion', 'Data Availability']
        },
        'bioinformatics': {
            'abstract_max_words': 250,
            'max_tables': 5,
            'max_figures': 6,
            'required_sections': ['Abstract', 'Introduction', 'Methods', 'Results', 'Discussion']
        }
    }

    def __init__(self, manuscript_path: Path, journal: str = None):
        self.manuscript_path = manuscript_path
        self.journal = journal.lower() if journal else None
        self.content = self._load_manuscript()
        self.issues = []
        self.warnings = []

    def _load_manuscript(self) -> str:
        """Load manuscript content."""
        if not self.manuscript_path.exists():
            raise FileNotFoundError(f"Manuscript not found: {self.manuscript_path}")

        with open(self.manuscript_path, 'r', encoding='utf-8') as f:
            return f.read()

    def check_citation_formatting(self) -> None:
        """Verify citations are formatted correctly."""
        # Extract citation keys
        citations = re.findall(r'\[([a-zA-Z]+\d{4}[a-z]?)\]', self.content)

        if not citations:
            self.warnings.append({
                'category': 'Citations',
                'description': 'No citations found in manuscript',
                'action': 'Verify manuscript should have citations; add if missing'
            })
            return

        # Check for malformed citations
        potential_bad_cites = re.findall(r'\[([^\]]{20,})\]', self.content)
        for bad_cite in potential_bad_cites:
            if not re.match(r'^[a-zA-Z]+\d{4}[a-z]?$', bad_cite):
                self.issues.append({
                    'category': 'Citation Format',
                    'description': f'Malformed citation: [{bad_cite[:50]}...]',
                    'action': 'Use [author2024] format for citations'
                })

        # Check for duplicate citations
        cite_counts = {}
        for cite in citations:
            cite_counts[cite] = cite_counts.get(cite, 0) + 1

        duplicates = {k: v for k, v in cite_counts.items() if v > 5}
        if duplicates:
            for cite, count in duplicates.items():
                self.warnings.append({
                    'category': 'Citation Usage',
                    'description': f'Citation [{cite}] used {count} times',
                    'action': 'Verify citation is not overused; combine discussions if possible'
                })

    def check_table_formatting(self) -> None:
        """Verify tables are formatted and numbered correctly."""
        # Count markdown tables
        table_blocks = re.findall(r'(\|[^\n]+\|(?:\n\|[^\n]+\|)+)', self.content)
        table_count = len(table_blocks)

        # Extract table references
        table_refs = re.findall(r'Table\s+(\d+)', self.content, re.IGNORECASE)
        unique_refs = sorted(set(int(r) for r in table_refs))

        if table_count != len(unique_refs):
            self.issues.append({
                'category': 'Table Numbering',
                'description': f'Found {table_count} tables but {len(unique_refs)} unique table references',
                'action': 'Verify all tables are numbered and referenced'
            })

        # Check sequential numbering
        if unique_refs:
            expected = list(range(1, len(unique_refs) + 1))
            if unique_refs != expected:
                self.issues.append({
                    'category': 'Table Numbering',
                    'description': f'Table numbers not sequential: {unique_refs}',
                    'action': 'Renumber tables sequentially from 1'
                })

        # Check table captions
        for i, table_block in enumerate(table_blocks, 1):
            # Look for caption before or after table
            table_pos = self.content.find(table_block)
            context_before = self.content[max(0, table_pos - 200):table_pos]
            context_after = self.content[table_pos + len(table_block):table_pos + len(table_block) + 200]

            has_caption = bool(
                re.search(r'Table\s+\d+[:\.]', context_before, re.IGNORECASE) or
                re.search(r'\*\*Table\s+\d+', context_before, re.IGNORECASE) or
                re.search(r'Table\s+\d+[:\.]', context_after, re.IGNORECASE)
            )

            if not has_caption:
                self.issues.append({
                    'category': 'Table Captions',
                    'description': f'Table {i} missing caption',
                    'action': 'Add caption above or below table in format: **Table {i}: [Description]**'
                })

        # Check journal limits
        if self.journal and table_count > 0:
            max_tables = self.JOURNAL_REQUIREMENTS.get(self.journal, {}).get('max_tables')
            if max_tables and table_count > max_tables:
                self.issues.append({
                    'category': 'Journal Compliance',
                    'description': f'{table_count} tables exceeds {self.journal.title()} limit of {max_tables}',
                    'action': 'Move excess tables to supplementary materials'
                })

    def check_figure_references(self) -> None:
        """Verify figure references are formatted correctly."""
        figure_refs = re.findall(r'(?:Figure|Fig\.?)\s+(\d+)', self.content, re.IGNORECASE)
        unique_refs = sorted(set(int(r) for r in figure_refs))

        if not unique_refs:
            return

        # Check sequential numbering
        expected = list(range(1, len(unique_refs) + 1))
        if unique_refs != expected:
            self.issues.append({
                'category': 'Figure Numbering',
                'description': f'Figure numbers not sequential: {unique_refs}',
                'action': 'Renumber figures sequentially from 1'
            })

        # Check consistent formatting (Figure vs. Fig.)
        figure_forms = re.findall(r'(Figure|Fig\.?)\s+\d+', self.content, re.IGNORECASE)
        fig_count = sum(1 for f in figure_forms if f.lower().startswith('fig'))
        figure_count = len(figure_forms) - fig_count

        if fig_count > 0 and figure_count > 0:
            self.warnings.append({
                'category': 'Figure References',
                'description': f'Inconsistent figure references: {figure_count} "Figure", {fig_count} "Fig."',
                'action': 'Use consistent format (prefer "Figure" in text)'
            })

        # Check journal limits
        if self.journal and unique_refs:
            max_figures = self.JOURNAL_REQUIREMENTS.get(self.journal, {}).get('max_figures')
            if max_figures and len(unique_refs) > max_figures:
                self.issues.append({
                    'category': 'Journal Compliance',
                    'description': f'{len(unique_refs)} figures exceeds {self.journal.title()} limit of {max_figures}',
                    'action': 'Move excess figures to supplementary materials'
                })

    def check_section_structure(self) -> None:
        """Verify required sections are present."""
        sections = re.findall(r'^#\s+(\w+)', self.content, re.MULTILINE)
        section_lower = [s.lower() for s in sections]

        if self.journal:
            required = [s.lower() for s in self.JOURNAL_REQUIREMENTS[self.journal]['required_sections']]
            missing = [s for s in required if s not in section_lower]

            if missing:
                self.issues.append({
                    'category': 'Structure',
                    'description': f'Missing required sections for {self.journal.title()}: {", ".join(missing)}',
                    'action': f'Add missing sections: {", ".join(missing)}'
                })

    def check_abstract_word_count(self) -> None:
        """Verify abstract meets word count requirements."""
        abstract_match = re.search(
            r'#\s+Abstract\s+(.*?)(?=^#\s+|\Z)',
            self.content,
            re.DOTALL | re.MULTILINE | re.IGNORECASE
        )

        if not abstract_match:
            if self.journal:
                self.issues.append({
                    'category': 'Structure',
                    'description': 'Abstract section not found',
                    'action': 'Add Abstract section at beginning of manuscript'
                })
            return

        abstract_text = abstract_match.group(1)
        words = abstract_text.split()
        word_count = len(words)

        if self.journal:
            max_words = self.JOURNAL_REQUIREMENTS[self.journal]['abstract_max_words']
            if word_count > max_words:
                self.issues.append({
                    'category': 'Word Count',
                    'description': f'Abstract has {word_count} words, exceeds {self.journal.title()} limit of {max_words}',
                    'action': f'Reduce abstract to {max_words} words or fewer'
                })

    def check_orphaned_references(self) -> None:
        """Check for references that aren't cited."""
        # Look for bibliography section
        bib_match = re.search(
            r'#\s+References\s+(.*?)(?=^#\s+|\Z)',
            self.content,
            re.DOTALL | re.MULTILINE | re.IGNORECASE
        )

        if not bib_match:
            return

        bib_text = bib_match.group(1)

        # Extract cited keys
        cited = set(re.findall(r'\[([a-zA-Z]+\d{4}[a-z]?)\]', self.content))

        # Extract bibliography keys (various formats)
        bib_keys = set(re.findall(r'^\s*\[([a-zA-Z]+\d{4}[a-z]?)\]', bib_text, re.MULTILINE))

        orphaned = bib_keys - cited
        if orphaned:
            self.warnings.append({
                'category': 'References',
                'description': f'{len(orphaned)} bibliography entries not cited: {", ".join(sorted(orphaned)[:5])}...',
                'action': 'Remove uncited entries or add citations to text'
            })

    def generate_report(self, output_path: Path) -> None:
        """Generate format review report."""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# Format Review Report (Stage 2)\n\n")
            f.write(f"**Reviewed:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
            f.write(f"**Manuscript:** {self.manuscript_path}\n")
            if self.journal:
                f.write(f"**Target Journal:** {self.journal.title()}\n")
            f.write(f"**Focus:** Citations, structure, journal requirements\n\n")

            # Summary
            issue_count = len(self.issues)
            warning_count = len(self.warnings)

            f.write("## Summary Assessment\n\n")
            if issue_count == 0:
                f.write("Formatting is compliant with no issues. ")
            else:
                f.write(f"Found {issue_count} formatting issues requiring correction. ")

            if warning_count > 0:
                f.write(f"{warning_count} warnings for review.\n\n")
            else:
                f.write("No warnings.\n\n")

            # Issues
            if self.issues:
                f.write("## Formatting Issues\n\n")
                for i, issue in enumerate(self.issues, 1):
                    f.write(f"{i}. **{issue['category']}:** {issue['description']}\n")
                    f.write(f"   - **Action:** {issue['action']}\n\n")

            # Warnings
            if self.warnings:
                f.write("## Warnings\n\n")
                for i, warning in enumerate(self.warnings, 1):
                    f.write(f"{i}. **{warning['category']}:** {warning['description']}\n")
                    f.write(f"   - **Action:** {warning['action']}\n\n")

            # Checklist
            f.write("## Format Checklist\n\n")
            f.write(f"- [{'x' if not any('Citation' in i['category'] for i in self.issues) else ' '}] Citations formatted correctly\n")
            f.write(f"- [{'x' if not any('Table' in i['category'] for i in self.issues) else ' '}] Tables numbered and captioned\n")
            f.write(f"- [{'x' if not any('Figure' in i['category'] for i in self.issues) else ' '}] Figures referenced correctly\n")
            f.write(f"- [{'x' if not any('Structure' in i['category'] for i in self.issues) else ' '}] Required sections present\n")

            if self.journal:
                f.write(f"- [{'x' if not any('Journal' in i['category'] for i in self.issues) else ' '}] Journal requirements met\n")

            f.write("\n")

            # Recommendation
            f.write("## Recommendation\n\n")
            if issue_count == 0:
                f.write("✅ Format approved - manuscript ready for submission\n")
            elif issue_count <= 3:
                f.write("⚠️  Minor format corrections required\n")
            else:
                f.write("❌ Significant format issues require revision\n")

    def run_review(self) -> None:
        """Run all format checks."""
        self.check_citation_formatting()
        self.check_table_formatting()
        self.check_figure_references()
        self.check_section_structure()
        self.check_abstract_word_count()
        self.check_orphaned_references()


def main():
    parser = argparse.ArgumentParser(
        description="Stage 2 Format Review: Citations, structure, journal compliance"
    )
    parser.add_argument(
        '--file',
        required=True,
        help='Path to manuscript file'
    )
    parser.add_argument(
        '--output',
        required=True,
        help='Output path for review report'
    )
    parser.add_argument(
        '--journal',
        choices=['nature', 'plos', 'bioinformatics'],
        help='Target journal for compliance check'
    )

    args = parser.parse_args()

    reviewer = FormatReviewer(Path(args.file), args.journal)
    reviewer.run_review()
    reviewer.generate_report(Path(args.output))

    print(f"✅ Format review complete: {args.output}")

    # Exit with error code if issues found
    if reviewer.issues:
        print(f"⚠️  Found {len(reviewer.issues)} format issues")
        return 1

    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
