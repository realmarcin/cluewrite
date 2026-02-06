#!/usr/bin/env python3
"""
Validate manuscript outputs against LinkML schema.

Usage:
    python scripts/cluewrite-validate-manuscript.py --file manuscript/outline.md --type outline
    python scripts/cluewrite-validate-manuscript.py --file manuscript/literature.md --type literature
    python scripts/cluewrite-validate-manuscript.py --file manuscript/abstract.md --type section
    python scripts/cluewrite-validate-manuscript.py --file manuscript/full_manuscript.md --type manuscript
    python scripts/cluewrite-validate-manuscript.py --file manuscript/review_manuscript_v1.md --type review
"""

import argparse
import sys
import re
from pathlib import Path
from datetime import datetime
import yaml

class ManuscriptValidator:
    """Validates manuscript files against schema requirements."""

    def __init__(self, schema_path="schemas/manuscript.yaml"):
        self.schema_path = Path(schema_path)
        if self.schema_path.exists():
            with open(self.schema_path) as f:
                self.schema = yaml.safe_load(f)
        else:
            self.schema = None
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
        """Validate individual manuscript section."""
        print(f"\n{'='*60}")
        print(f"Validating Section: {filepath}")
        print(f"{'='*60}\n")

        errors = []
        warnings = []
        info = []

        # Check filename
        valid, msg = self.validate_filename(
            filepath,
            r'^(abstract|introduction|methods|results|discussion|conclusion)\.md$'
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

        # Check word count
        word_count = self.count_words(filepath)
        info.append(f"✓ Word count: {word_count}")

        # Section-specific word count recommendations
        min_words = {
            'abstract': 100,
            'introduction': 300,
            'methods': 400,
            'results': 400,
            'discussion': 400,
            'conclusion': 150
        }

        section_key = Path(filepath).stem.lower()
        if section_key in min_words:
            if word_count < min_words[section_key]:
                warnings.append(
                    f"{section_name} is short ({word_count} words). "
                    f"Minimum recommended: {min_words[section_key]} words."
                )

        # Check citations
        citations = self.extract_citations(filepath)
        if citations:
            info.append(f"✓ Found {len(citations)} citations")

        # Check figure references
        figures = self.extract_figure_refs(filepath)
        if figures:
            info.append(f"✓ References {len(figures)} figure(s)")

        return errors, warnings, info

    def validate_manuscript(self, filepath):
        """Validate full assembled manuscript."""
        print(f"\n{'='*60}")
        print(f"Validating Full Manuscript: {filepath}")
        print(f"{'='*60}\n")

        errors = []
        warnings = []
        info = []

        # Check filename
        valid, msg = self.validate_filename(filepath, r'^full_manuscript\.md$')
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
            errors.append(f"Missing required sections: {', '.join(missing)}")
        else:
            info.append(f"✓ All required sections present")

        # Check total word count
        word_count = self.count_words(filepath)
        info.append(f"✓ Total word count: {word_count}")

        if word_count < 1000:
            errors.append(f"Manuscript too short ({word_count} words). Minimum: 1000 words.")
        elif word_count > 15000:
            warnings.append(f"Manuscript very long ({word_count} words). Consider condensing.")

        # Check citations
        citations = self.extract_citations(filepath)
        info.append(f"✓ Total citations: {len(citations)}")

        if len(citations) < 5:
            warnings.append("Few citations. Academic manuscripts typically cite 10-30+ papers.")

        # Check figures
        figures = self.extract_figure_refs(filepath)
        info.append(f"✓ Total figures: {len(figures)}")

        return errors, warnings, info

    def validate_review(self, filepath):
        """Validate review report."""
        print(f"\n{'='*60}")
        print(f"Validating Review: {filepath}")
        print(f"{'='*60}\n")

        errors = []
        warnings = []
        info = []

        # Check filename
        valid, msg = self.validate_filename(
            filepath,
            r'^review_(outline|literature|section|manuscript)_v[0-9]+\.md$'
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
            warnings.append(f"Review is brief ({word_count} words). Consider more detailed feedback.")

        return errors, warnings, info

    def print_results(self, errors, warnings, info):
        """Print validation results."""
        print(f"\n{'='*60}")
        print("VALIDATION RESULTS")
        print(f"{'='*60}\n")

        if info:
            print("ℹ️  INFO:")
            for item in info:
                print(f"  {item}")
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
            print("✅ VALIDATION PASSED")
            print()
            return True

def main():
    parser = argparse.ArgumentParser(
        description="Validate manuscript outputs against schema"
    )
    parser.add_argument(
        '--file',
        required=True,
        help='Path to manuscript file'
    )
    parser.add_argument(
        '--type',
        required=True,
        choices=['outline', 'literature', 'section', 'manuscript', 'review'],
        help='Type of document to validate'
    )
    parser.add_argument(
        '--schema',
        default='schemas/manuscript.yaml',
        help='Path to LinkML schema file'
    )

    args = parser.parse_args()

    validator = ManuscriptValidator(args.schema)

    # Route to appropriate validator
    if args.type == 'outline':
        errors, warnings, info = validator.validate_outline(args.file)
    elif args.type == 'literature':
        errors, warnings, info = validator.validate_literature(args.file)
    elif args.type == 'section':
        errors, warnings, info = validator.validate_section(args.file)
    elif args.type == 'manuscript':
        errors, warnings, info = validator.validate_manuscript(args.file)
    elif args.type == 'review':
        errors, warnings, info = validator.validate_review(args.file)

    # Print results
    success = validator.print_results(errors, warnings, info)

    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
