#!/usr/bin/env python3
"""
Validate Manuscript Against Schema - Validate manuscript compliance with journal requirements.

This script validates a manuscript against journal-specific schemas to ensure
compliance with submission requirements and structure constraints.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any
import re

# Add scripts directory to path
SCRIPTS_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPTS_DIR))

try:
    import jsonschema
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    JSONSCHEMA_AVAILABLE = False


class SchemaValidator:
    """Validates manuscripts against journal schemas."""

    def __init__(self, manuscript_dir: Path, journal_key: str):
        """
        Initialize validator.

        Args:
            manuscript_dir: Path to manuscript directory
            journal_key: Normalized journal identifier
        """
        self.manuscript_dir = Path(manuscript_dir)
        self.journal_key = journal_key

        # Load schemas
        repo_root = SCRIPTS_DIR.parent
        schema_dir = repo_root / "schemas" / "journals" / journal_key

        if not schema_dir.exists():
            raise ValueError(
                f"No schemas found for journal: {journal_key}\n"
                f"Generate schemas first with: rrwrite-generate-journal-schema.py"
            )

        self.submission_schema = self._load_json(
            schema_dir / "submission_requirements.json"
        )
        self.structure_schema = self._load_json(
            schema_dir / "manuscript_structure.json"
        )

        # Load manuscript data
        self.sections = self._load_sections()
        self.metadata = self._extract_metadata()

    def _load_json(self, path: Path) -> Dict:
        """Load JSON file."""
        with open(path, 'r') as f:
            return json.load(f)

    def _load_sections(self) -> Dict[str, str]:
        """Load all manuscript sections."""
        sections = {}
        sections_dir = self.manuscript_dir / "sections"

        if not sections_dir.exists():
            return sections

        for section_file in sections_dir.glob("*.md"):
            section_name = section_file.stem
            with open(section_file, 'r') as f:
                sections[section_name] = f.read()

        return sections

    def _extract_metadata(self) -> Dict[str, Any]:
        """Extract metadata from manuscript."""
        metadata = {
            'sections_present': list(self.sections.keys()),
            'word_counts': {},
            'total_word_count': 0,
            'citations': set(),
            'figures': [],
            'tables': []
        }

        # Calculate word counts
        for section, content in self.sections.items():
            word_count = len(content.split())
            metadata['word_counts'][section] = word_count
            metadata['total_word_count'] += word_count

            # Extract citations
            citations = re.findall(r'\[@(\w+)\]', content)
            metadata['citations'].update(citations)

        # Count figures and tables
        figures_dir = self.manuscript_dir / "figures"
        if figures_dir.exists():
            metadata['figures'] = list(figures_dir.glob("**/*.png")) + \
                                 list(figures_dir.glob("**/*.pdf"))

        tables_dir = self.manuscript_dir / "tables"
        if tables_dir.exists():
            metadata['tables'] = list(tables_dir.glob("*.md")) + \
                                list(tables_dir.glob("*.tsv"))

        return metadata

    def validate_manuscript_structure(self) -> Tuple[bool, List[str]]:
        """
        Validate manuscript structure against schema.

        Returns:
            Tuple of (is_valid, list_of_violations)
        """
        violations = []

        structure = self.structure_schema.get('structure', {})
        sections_schema = structure.get('sections', [])

        # Check required sections
        for section_spec in sections_schema:
            section_name = section_spec['name']
            required = section_spec.get('required', False)

            if required and section_name not in self.metadata['sections_present']:
                violations.append(
                    f"Missing required section: {section_name}"
                )

        # Check section order
        ordering_rules = structure.get('ordering_rules', {})
        if ordering_rules.get('strict_order', False):
            expected_order = [s['name'] for s in sections_schema]
            actual_order = self.metadata['sections_present']

            # Filter to only compare sections that exist in both
            common_sections = [s for s in expected_order if s in actual_order]
            actual_common = [s for s in actual_order if s in common_sections]

            if common_sections != actual_common:
                violations.append(
                    f"Section order mismatch. Expected: {common_sections}, "
                    f"Got: {actual_common}"
                )

        return (len(violations) == 0, violations)

    def validate_submission_requirements(self) -> Tuple[bool, List[str]]:
        """
        Validate submission requirements against schema.

        Returns:
            Tuple of (is_valid, list_of_violations)
        """
        violations = []

        requirements = self.submission_schema.get('requirements', {})

        # Validate word limits
        word_limits = requirements.get('word_limits', {})
        for section, limits in word_limits.items():
            if section == 'total_manuscript':
                actual_count = self.metadata['total_word_count']
            else:
                actual_count = self.metadata['word_counts'].get(section, 0)

            if 'max' in limits and actual_count > limits['max']:
                violations.append(
                    f"{section}: word count {actual_count} exceeds maximum {limits['max']}"
                )

            if 'min' in limits and actual_count < limits['min']:
                violations.append(
                    f"{section}: word count {actual_count} below minimum {limits['min']}"
                )

        # Validate figure/table limits
        fig_table_req = requirements.get('figure_table_requirements', {})

        if 'max_figures' in fig_table_req:
            max_figs = fig_table_req['max_figures']
            actual_figs = len(self.metadata['figures'])
            if actual_figs > max_figs:
                violations.append(
                    f"Too many figures: {actual_figs} (max: {max_figs})"
                )

        if 'max_tables' in fig_table_req:
            max_tables = fig_table_req['max_tables']
            actual_tables = len(self.metadata['tables'])
            if actual_tables > max_tables:
                violations.append(
                    f"Too many tables: {actual_tables} (max: {max_tables})"
                )

        # Validate citation count
        citation_req = requirements.get('citation_requirements', {})
        if 'max_references' in citation_req:
            max_refs = citation_req['max_references']
            actual_refs = len(self.metadata['citations'])
            if actual_refs > max_refs:
                violations.append(
                    f"Too many references: {actual_refs} (max: {max_refs})"
                )

        return (len(violations) == 0, violations)

    def generate_compliance_report(self) -> str:
        """
        Generate comprehensive compliance report.

        Returns:
            Markdown-formatted compliance report
        """
        structure_valid, structure_violations = self.validate_manuscript_structure()
        submission_valid, submission_violations = self.validate_submission_requirements()

        report = []
        report.append(f"# Schema Compliance Report\n")
        report.append(f"**Journal:** {self.submission_schema['journal']['name']}\n")
        report.append(f"**Manuscript:** {self.manuscript_dir.name}\n")
        report.append(f"**Generated:** {Path(__file__).name}\n\n")

        report.append("## Overall Compliance\n")
        if structure_valid and submission_valid:
            report.append("✓ **PASSED** - Manuscript complies with all requirements\n\n")
        else:
            report.append("✗ **FAILED** - Violations found\n\n")

        # Structure validation
        report.append("## Structure Validation\n")
        if structure_valid:
            report.append("✓ Structure compliant\n\n")
        else:
            report.append(f"✗ {len(structure_violations)} violation(s):\n")
            for v in structure_violations:
                report.append(f"- {v}\n")
            report.append("\n")

        # Submission requirements
        report.append("## Submission Requirements\n")
        if submission_valid:
            report.append("✓ All requirements met\n\n")
        else:
            report.append(f"✗ {len(submission_violations)} violation(s):\n")
            for v in submission_violations:
                report.append(f"- {v}\n")
            report.append("\n")

        # Metadata summary
        report.append("## Manuscript Metadata\n")
        report.append(f"- **Total word count:** {self.metadata['total_word_count']}\n")
        report.append(f"- **Sections:** {len(self.metadata['sections_present'])}\n")
        report.append(f"- **Figures:** {len(self.metadata['figures'])}\n")
        report.append(f"- **Tables:** {len(self.metadata['tables'])}\n")
        report.append(f"- **Citations:** {len(self.metadata['citations'])}\n\n")

        # Section word counts
        report.append("### Section Word Counts\n")
        for section, count in sorted(self.metadata['word_counts'].items()):
            report.append(f"- **{section}:** {count} words\n")

        return ''.join(report)


def main():
    parser = argparse.ArgumentParser(
        description="Validate manuscript against journal-specific schemas",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate manuscript
  %(prog)s --manuscript-dir manuscript/project_v1 --journal bioinformatics

  # Generate compliance report
  %(prog)s --manuscript-dir manuscript/project_v1 --journal bioinformatics \\
    --report compliance_report.md

  # Validate with verbose output
  %(prog)s --manuscript-dir manuscript/project_v1 --journal bioinformatics --verbose
        """
    )

    parser.add_argument(
        '--manuscript-dir',
        required=True,
        type=Path,
        help='Path to manuscript directory'
    )

    parser.add_argument(
        '--journal',
        required=True,
        help='Journal key (e.g., bioinformatics, nature_methods)'
    )

    parser.add_argument(
        '--report',
        type=Path,
        help='Output path for compliance report (markdown)'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )

    args = parser.parse_args()

    # Validate inputs
    if not args.manuscript_dir.exists():
        print(f"Error: Manuscript directory not found: {args.manuscript_dir}",
              file=sys.stderr)
        return 1

    try:
        # Initialize validator
        validator = SchemaValidator(args.manuscript_dir, args.journal)

        # Run validation
        structure_valid, structure_violations = validator.validate_manuscript_structure()
        submission_valid, submission_violations = validator.validate_submission_requirements()

        # Generate report
        report = validator.generate_compliance_report()

        # Output report
        if args.report:
            with open(args.report, 'w') as f:
                f.write(report)
            print(f"Compliance report saved to: {args.report}")
        else:
            print(report)

        # Print summary
        print("\n" + "="*60)
        if structure_valid and submission_valid:
            print("✓ VALIDATION PASSED")
            return 0
        else:
            print("✗ VALIDATION FAILED")
            total_violations = len(structure_violations) + len(submission_violations)
            print(f"  {total_violations} violation(s) found")

            if args.verbose:
                print("\nViolations:")
                for v in structure_violations + submission_violations:
                    print(f"  - {v}")

            return 1

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
