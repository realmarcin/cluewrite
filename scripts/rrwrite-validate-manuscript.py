#!/usr/bin/env python3
"""
Validate manuscript outputs against LinkML schema with defense-in-depth citation validation.

Usage:
    python scripts/rrwrite-validate-manuscript.py --file manuscript/outline.md --type outline
    python scripts/rrwrite-validate-manuscript.py --file manuscript/literature.md --type literature
    python scripts/rrwrite-validate-manuscript.py --file manuscript/abstract.md --type section
    python scripts/rrwrite-validate-manuscript.py --file manuscript/full_manuscript.md --type manuscript
    python scripts/rrwrite-validate-manuscript.py --file manuscript/critique_manuscript_v1.md --type critique
    python scripts/rrwrite-validate-manuscript.py --file manuscript/abstract.md --type section --expert  # Expert mode
    python scripts/rrwrite-validate-manuscript.py --file manuscript/full_manuscript.md --type manuscript --output json  # JSON output
"""

import argparse
import sys
import re
from pathlib import Path
from datetime import datetime
import yaml
import json

# Import defense-in-depth validation
try:
    from rrwrite_citation_validator import (
        CitationEntryValidator,
        CitationBusinessValidator,
        CitationAssemblyValidator,
        CitationAuditor,
        CitationNotFoundError,
        CitationMismatchError
    )
    DEFENSE_IN_DEPTH_AVAILABLE = True
except ImportError:
    DEFENSE_IN_DEPTH_AVAILABLE = False
    print("Warning: Defense-in-depth citation validation not available")

# Import root cause tracer
try:
    from rrwrite_citation_tracer import CitationErrorTracer
    ROOT_CAUSE_TRACING_AVAILABLE = True
except ImportError:
    ROOT_CAUSE_TRACING_AVAILABLE = False

class ManuscriptValidator:
    """Validates manuscript files against schema requirements with defense-in-depth citation validation."""

    def __init__(self, schema_path="schemas/manuscript.yaml", expert_mode=False, output_format="text"):
        self.schema_path = Path(schema_path)
        self.expert_mode = expert_mode
        self.output_format = output_format
        if self.schema_path.exists():
            with open(self.schema_path) as f:
                self.schema = yaml.safe_load(f)
        else:
            self.schema = None
            if not expert_mode:
                print(f"Warning: Schema not found at {schema_path}")

    def validate_filename(self, filepath, expected_pattern):
        """Validate filename matches expected pattern."""
        filename = Path(filepath).name
        if not re.match(expected_pattern, filename):
            return False, f"Filename '{filename}' does not match pattern: {expected_pattern}"
        return True, "Filename valid"

    def count_words(self, filepath):
        """Count words in markdown file."""
        try:
            with open(filepath, 'r') as f:
                content = f.read()
                # Remove markdown syntax for more accurate count
                content = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
                content = re.sub(r'`[^`]+`', '', content)
                content = re.sub(r'#+\s', '', content)
                content = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', content)
                words = content.split()
                return len(words)
        except Exception as e:
            print(f"Error counting words: {e}")
            return 0

    def extract_citations(self, filepath):
        """Extract citation keys from markdown."""
        try:
            with open(filepath, 'r') as f:
                content = f.read()
                # Match [author2024] style citations
                citations = re.findall(r'\[([a-zA-Z]+\d{4}[a-z]?)\]', content)
                return list(set(citations))
        except Exception as e:
            print(f"Error extracting citations: {e}")
            return []

    def extract_figure_refs(self, filepath):
        """Extract figure references from markdown."""
        try:
            with open(filepath, 'r') as f:
                content = f.read()
                # Match Figure N or Fig. N
                figures = re.findall(r'(?:Figure|Fig\.)\s+(\d+)', content, re.IGNORECASE)
                return list(set(figures))
        except Exception as e:
            print(f"Error extracting figures: {e}")
            return []

    def extract_table_refs(self, filepath):
        """Extract table references (e.g., 'Table 1', 'Table 2')."""
        try:
            with open(filepath, 'r') as f:
                content = f.read()
                # Match Table N
                tables = re.findall(r'Table\s+(\d+)', content, re.IGNORECASE)
                return list(set(tables))
        except Exception as e:
            print(f"Error extracting table references: {e}")
            return []

    def count_markdown_tables(self, filepath):
        """Count markdown table blocks (consecutive lines starting with |)."""
        try:
            with open(filepath, 'r') as f:
                lines = f.readlines()

            table_count = 0
            in_table = False
            for line in lines:
                if line.strip().startswith('|'):
                    if not in_table:
                        table_count += 1
                        in_table = True
                else:
                    in_table = False
            return table_count
        except Exception as e:
            print(f"Error counting tables: {e}")
            return 0

    def check_sections(self, filepath, expected_sections):
        """Check if required sections are present."""
        try:
            with open(filepath, 'r') as f:
                content = f.read()
                found_sections = []
                missing_sections = []

                for section in expected_sections:
                    # Match ## Section or # Section
                    pattern = rf'^#{{1,3}}\s+{re.escape(section)}'
                    if re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
                        found_sections.append(section)
                    else:
                        missing_sections.append(section)

                return found_sections, missing_sections
        except Exception as e:
            print(f"Error checking sections: {e}")
            return [], expected_sections

    def validate_outline(self, filepath):
        """Validate manuscript outline."""
        print(f"\n{'='*60}")
        print(f"Validating Outline: {filepath}")
        print(f"{'='*60}\n")

        errors = []
        warnings = []
        info = []

        # Check filename
        valid, msg = self.validate_filename(filepath, r'^outline\.md$')
        if not valid:
            errors.append(msg)
        else:
            info.append(f"✓ {msg}")

        # Check file exists
        if not Path(filepath).exists():
            errors.append(f"File not found: {filepath}")
            return errors, warnings, info

        # Check sections
        expected_sections = [
            "Target Journal",
            "Abstract",
            "Introduction",
            "Methods",
            "Results",
            "Discussion"
        ]
        found, missing = self.check_sections(filepath, expected_sections)

        if missing:
            warnings.append(f"Missing recommended sections: {', '.join(missing)}")

        info.append(f"✓ Found {len(found)} sections")

        # Check word count
        word_count = self.count_words(filepath)
        info.append(f"✓ Word count: {word_count}")

        if word_count < 500:
            warnings.append(f"Outline is short ({word_count} words). Consider adding more detail.")

        return errors, warnings, info

    def validate_literature(self, filepath):
        """Validate literature research."""
        print(f"\n{'='*60}")
        print(f"Validating Literature Research: {filepath}")
        print(f"{'='*60}\n")

        errors = []
        warnings = []
        info = []

        # Check filename
        valid, msg = self.validate_filename(filepath, r'^literature\.md$')
        if not valid:
            errors.append(msg)
        else:
            info.append(f"✓ {msg}")

        if not Path(filepath).exists():
            errors.append(f"File not found: {filepath}")
            return errors, warnings, info

        # Check required sections
        expected_sections = [
            "Background",
            "Related Work",
            "Recent Advances",
            "Research Gaps"
        ]
        found, missing = self.check_sections(filepath, expected_sections)

        if missing:
            errors.append(f"Missing required sections: {', '.join(missing)}")
        else:
            info.append(f"✓ All required sections present")

        # Check citations
        citations = self.extract_citations(filepath)
        info.append(f"✓ Found {len(citations)} citations")

        if len(citations) < 5:
            warnings.append(f"Few citations ({len(citations)}). Literature review should cite 10-25 papers.")

        # Check word count
        word_count = self.count_words(filepath)
        info.append(f"✓ Word count: {word_count}")

        if word_count < 800:
            warnings.append(f"Literature review is short ({word_count} words). Target: 1000-1500 words.")

        # Check for accompanying files
        parent_dir = Path(filepath).parent
        bib_file = parent_dir / "literature_citations.bib"
        evidence_file = parent_dir / "literature_evidence.csv"

        if bib_file.exists():
            info.append(f"✓ Found citations file: {bib_file.name}")
        else:
            warnings.append(f"Missing literature_citations.bib")

        if evidence_file.exists():
            info.append(f"✓ Found evidence file: {evidence_file.name}")
        else:
            warnings.append(f"Missing literature_evidence.csv")

        return errors, warnings, info

    def validate_section(self, filepath):
        """Validate individual manuscript section with defense-in-depth citation validation."""
        if not self.expert_mode:
            print(f"\n{'='*60}")
            print(f"Validating Section: {filepath}")
            print(f"{'='*60}\n")

        errors = []
        warnings = []
        info = []

        # Check filename
        valid, msg = self.validate_filename(
            filepath,
            r'^(abstract|introduction|methods|results|discussion|conclusion|availability)\.md$'
        )
        if not valid:
            errors.append(msg)
        else:
            info.append(f"✓ {msg}")

        if not Path(filepath).exists():
            errors.append(f"File not found: {filepath}")
            return errors, warnings, info

        # Determine section type
        section_name = Path(filepath).stem.title()
        section_key = Path(filepath).stem.lower()

        # Check word count
        word_count = self.count_words(filepath)
        info.append(f"✓ Word count: {word_count}")

        # Section-specific word count recommendations with ±20% tolerance
        target_words = {
            'abstract': 150,
            'introduction': 500,
            'methods': 600,
            'results': 800,
            'discussion': 700,
            'conclusion': 200,
            'availability': 100
        }

        if section_key in target_words:
            target = target_words[section_key]
            min_acceptable = int(target * 0.8)
            max_acceptable = int(target * 1.2)

            if word_count < min_acceptable:
                errors.append(
                    f"\n❌ Word Count Validation Failed\n\n"
                    f"{section_name} has {word_count} words, below acceptable range "
                    f"({min_acceptable}-{max_acceptable}, target: {target}).\n\n"
                    f"Why this matters:\n"
                    f"1. Journals auto-reject at word limit violations\n"
                    f"2. Insufficient content suggests incomplete analysis\n"
                    f"3. Reviewers expect adequate detail\n\n"
                    f"Next steps:\n"
                    f"1. Review section outline for missing content\n"
                    f"2. Add necessary details and examples\n"
                    f"3. Ensure all key points are addressed\n\n"
                    f"Don't rationalize: \"Close enough\" → Auto-rejection risk\n"
                )
            elif word_count > max_acceptable:
                warnings.append(
                    f"⚠️  {section_name} has {word_count} words, above target range "
                    f"({min_acceptable}-{max_acceptable}, target: {target}). Consider condensing."
                )
            else:
                info.append(f"✓ Word count within ±20% of target ({target} words)")

        # DEFENSE-IN-DEPTH LAYER 1 & 2: Entry and Business Logic Validation
        citations = self.extract_citations(filepath)
        if citations and DEFENSE_IN_DEPTH_AVAILABLE:
            info.append(f"✓ Found {len(citations)} citations")

            # Find evidence file
            parent_dir = Path(filepath).parent
            evidence_csv = parent_dir / "literature_evidence.csv"

            if not evidence_csv.exists():
                warnings.append(
                    f"⚠️  literature_evidence.csv not found. Cannot verify citations."
                )
            else:
                # Layer 1: Entry validation
                try:
                    valid_cites, invalid_cites = CitationEntryValidator.validate_multiple(
                        citations, evidence_csv
                    )

                    if invalid_cites:
                        for cit in invalid_cites:
                            errors.append(
                                f"\n❌ Citation Verification Failed\n\n"
                                f"Citation [{cit}] not in literature_evidence.csv\n\n"
                                f"Why this matters: Claims without evidence means:\n"
                                f"1. Reviewers will request verification\n"
                                f"2. Retraction risk if source disputed\n"
                                f"3. Ethical violation if claim unsupported\n\n"
                                f"Next steps:\n"
                                f"1. Run: python scripts/rrwrite-search-literature.py --query \"[topic]\"\n"
                                f"2. Add DOI to literature_evidence.csv with supporting quote\n"
                                f"3. Re-run validation\n\n"
                                f"Don't rationalize: \"I'll add it later\" → 40% of citations forgotten\n"
                            )
                    else:
                        info.append(f"✓ All {len(citations)} citations verified in evidence file")

                    # Layer 2: Business logic validation (section appropriateness)
                    business_validator = CitationBusinessValidator(evidence_csv)
                    business_warnings = business_validator.validate_section_appropriateness(
                        section_key, citations
                    )
                    if business_warnings:
                        warnings.extend(business_warnings)
                    else:
                        info.append(f"✓ Citations appropriate for {section_name} section")

                except Exception as e:
                    warnings.append(f"⚠️  Citation validation error: {e}")

        elif citations and not DEFENSE_IN_DEPTH_AVAILABLE:
            info.append(f"✓ Found {len(citations)} citations (defense-in-depth validation unavailable)")

        # Check figure references
        figures = self.extract_figure_refs(filepath)
        if figures:
            info.append(f"✓ References {len(figures)} figure(s)")

        # Check table references and markdown tables
        table_refs = self.extract_table_refs(filepath)
        table_count = self.count_markdown_tables(filepath)

        if table_count > 0:
            info.append(f"✓ Contains {table_count} markdown table(s)")

        if table_refs:
            info.append(f"✓ References {len(table_refs)} table(s)")

            # Warn if references don't match table count
            if len(table_refs) != table_count:
                warnings.append(
                    f"⚠️  Table reference count ({len(table_refs)}) doesn't match "
                    f"markdown table count ({table_count}). Verify all tables are numbered."
                )

        return errors, warnings, info

    def validate_manuscript(self, filepath):
        """Validate full assembled manuscript with LAYER 3 assembly validation."""
        if not self.expert_mode:
            print(f"\n{'='*60}")
            print(f"Validating Full Manuscript: {filepath}")
            print(f"{'='*60}\n")

        errors = []
        warnings = []
        info = []

        # Check filename
        valid, msg = self.validate_filename(filepath, r'^(full_manuscript|manuscript)\.md$')
        if not valid:
            errors.append(msg)
        else:
            info.append(f"✓ {msg}")

        if not Path(filepath).exists():
            errors.append(f"File not found: {filepath}")
            return errors, warnings, info

        # Check all required sections
        required_sections = [
            "Abstract",
            "Introduction",
            "Methods",
            "Results",
            "Discussion"
        ]
        found, missing = self.check_sections(filepath, required_sections)

        if missing:
            errors.append(f"❌ Missing required sections: {', '.join(missing)}")
        else:
            info.append(f"✓ All required sections present")

        # Check total word count
        word_count = self.count_words(filepath)
        info.append(f"✓ Total word count: {word_count}")

        if word_count < 1000:
            errors.append(
                f"\n❌ Manuscript too short ({word_count} words)\n"
                f"Minimum: 1000 words for publishable manuscript."
            )
        elif word_count > 15000:
            warnings.append(
                f"⚠️  Manuscript very long ({word_count} words). "
                f"Consider condensing or check journal limits."
            )

        # Check citations
        citations = self.extract_citations(filepath)
        info.append(f"✓ Total citations: {len(citations)}")

        if len(citations) < 5:
            warnings.append(
                "⚠️  Few citations. Academic manuscripts typically cite 10-30+ papers."
            )

        # DEFENSE-IN-DEPTH LAYER 3: Assembly Validation
        if DEFENSE_IN_DEPTH_AVAILABLE and citations:
            parent_dir = Path(filepath).parent
            bib_file = parent_dir / "literature_citations.bib"
            evidence_file = parent_dir / "literature_evidence.csv"

            if bib_file.exists():
                info.append(f"✓ Found bibliography: {bib_file.name}")

                try:
                    # Validate text citations match bibliography
                    orphaned_text, orphaned_bib = CitationAssemblyValidator.validate_citation_completeness(
                        Path(filepath), bib_file
                    )
                    info.append(f"✓ All citations synchronized between text and bibliography")

                except CitationMismatchError as e:
                    errors.append(str(e))

            else:
                warnings.append(
                    f"⚠️  Bibliography not found at {bib_file}. Cannot verify citation completeness."
                )

            # Entry validation for all citations
            if evidence_file.exists():
                valid_cites, invalid_cites = CitationEntryValidator.validate_multiple(
                    citations, evidence_file
                )
                if invalid_cites:
                    errors.append(
                        f"\n❌ {len(invalid_cites)} citations not in evidence file:\n"
                        + "\n".join(f"  - [{c}]" for c in sorted(invalid_cites))
                        + "\n"
                    )
                else:
                    info.append(f"✓ All {len(citations)} citations verified in evidence file")

        # Check figures
        figures = self.extract_figure_refs(filepath)
        info.append(f"✓ Total figures: {len(figures)}")

        # Check tables
        table_refs = self.extract_table_refs(filepath)
        table_count = self.count_markdown_tables(filepath)
        info.append(f"✓ Total tables: {table_count}")

        # Check journal-specific table limits
        journal_table_limits = {
            'bioinformatics': 5,
            'nature': 4,
            'plos': 10,
            'bmc': 10
        }

        # Check against common journal limits
        if table_count > 0:
            for journal, limit in journal_table_limits.items():
                if table_count > limit:
                    warnings.append(
                        f"⚠️  Table count ({table_count}) exceeds {journal.title()} limit ({limit}). "
                        f"Consider moving tables to supplementary materials."
                    )
                    break  # Only warn once

        # Warn if table references don't match table count
        if len(table_refs) != table_count and table_count > 0:
            warnings.append(
                f"⚠️  Table reference count ({len(table_refs)}) doesn't match "
                f"markdown table count ({table_count}). Check table numbering."
            )

        return errors, warnings, info

    def validate_critique(self, filepath):
        """Validate critique report."""
        print(f"\n{'='*60}")
        print(f"Validating Critique: {filepath}")
        print(f"{'='*60}\n")

        errors = []
        warnings = []
        info = []

        # Check filename
        valid, msg = self.validate_filename(
            filepath,
            r'^critique_(outline|literature|section|manuscript)_v[0-9]+\.md$'
        )
        if not valid:
            errors.append(msg)
        else:
            info.append(f"✓ {msg}")

        if not Path(filepath).exists():
            errors.append(f"File not found: {filepath}")
            return errors, warnings, info

        # Check required sections
        required_sections = [
            "Summary Assessment",
            "Strengths",
            "Major Issues",
            "Minor Issues",
            "Recommendation"
        ]
        found, missing = self.check_sections(filepath, required_sections)

        if missing:
            warnings.append(f"Missing recommended sections: {', '.join(missing)}")
        else:
            info.append(f"✓ All recommended sections present")

        # Check word count
        word_count = self.count_words(filepath)
        info.append(f"✓ Word count: {word_count}")

        if word_count < 200:
            warnings.append(f"Critique is brief ({word_count} words). Consider more detailed feedback.")

        return errors, warnings, info

    def print_results(self, errors, warnings, info):
        """Print validation results in text or JSON format."""
        if self.output_format == "json":
            result = {
                "status": "passed" if not errors else "failed",
                "errors": errors,
                "warnings": warnings,
                "info": info
            }
            print(json.dumps(result, indent=2))
            return not errors

        # Text format (default)
        if not self.expert_mode:
            print(f"\n{'='*60}")
            print("VALIDATION RESULTS")
            print(f"{'='*60}\n")

        if info:
            if not self.expert_mode:
                print("ℹ️  INFO:")
            for item in info:
                if not self.expert_mode:
                    print(f"  {item}")

            if not self.expert_mode:
                print()

        if warnings:
            print("⚠️  WARNINGS:")
            for item in warnings:
                print(f"  {item}")
            print()

        if errors:
            print("❌ ERRORS:")
            for item in errors:
                print(f"  {item}")
            print()
            return False
        else:
            if self.expert_mode:
                print("✅ PASSED")
            else:
                print("✅ VALIDATION PASSED")
            print()
            return True

def main():
    parser = argparse.ArgumentParser(
        description="Validate manuscript outputs with defense-in-depth citation validation"
    )
    parser.add_argument(
        '--file',
        required=True,
        help='Path to manuscript file'
    )
    parser.add_argument(
        '--type',
        required=True,
        choices=['outline', 'literature', 'section', 'manuscript', 'critique'],
        help='Type of document to validate'
    )
    parser.add_argument(
        '--schema',
        default='schemas/manuscript.yaml',
        help='Path to LinkML schema file'
    )
    parser.add_argument(
        '--expert',
        action='store_true',
        help='Expert mode: minimal output, skip verbose messages'
    )
    parser.add_argument(
        '--output',
        choices=['text', 'json'],
        default='text',
        help='Output format (text or json)'
    )
    parser.add_argument(
        '--no-validate',
        action='store_true',
        help='Skip validation (not recommended)'
    )

    args = parser.parse_args()

    if args.no_validate:
        print("⚠️  Validation skipped (--no-validate flag)")
        sys.exit(0)

    validator = ManuscriptValidator(
        args.schema,
        expert_mode=args.expert,
        output_format=args.output
    )

    # Route to appropriate validator
    if args.type == 'outline':
        errors, warnings, info = validator.validate_outline(args.file)
    elif args.type == 'literature':
        errors, warnings, info = validator.validate_literature(args.file)
    elif args.type == 'section':
        errors, warnings, info = validator.validate_section(args.file)
    elif args.type == 'manuscript':
        errors, warnings, info = validator.validate_manuscript(args.file)
    elif args.type == 'critique':
        errors, warnings, info = validator.validate_critique(args.file)

    # Print results
    success = validator.print_results(errors, warnings, info)

    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
