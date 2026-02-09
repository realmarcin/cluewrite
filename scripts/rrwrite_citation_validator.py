#!/usr/bin/env python3
"""
Defense-in-depth citation validation framework.

Provides multi-layer validation:
- Layer 1: Entry validation (fail fast at draft time)
- Layer 2: Business logic validation (section appropriateness)
- Layer 3: Assembly validation (completeness at compilation)
- Layer 4: Audit trail (forensics and debugging)
"""

import re
import csv
from pathlib import Path
from datetime import datetime
from typing import List, Set, Dict, Optional, Tuple
import json


class CitationError(Exception):
    """Base exception for citation errors."""
    pass


class CitationNotFoundError(CitationError):
    """Citation key not found in evidence file."""
    pass


class CitationMismatchError(CitationError):
    """Mismatch between text citations and bibliography."""
    pass


class CitationAppropriateness Warning(Warning):
    """Warning for potentially inappropriate citation usage."""
    pass


# Layer 1: Entry Validation
class CitationEntryValidator:
    """Fast-fail validation at entry time."""

    @staticmethod
    def load_evidence_keys(evidence_csv: Path) -> Set[str]:
        """Load all citation keys from evidence file."""
        if not evidence_csv.exists():
            return set()

        keys = set()
        try:
            with open(evidence_csv, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if 'citation_key' in row:
                        keys.add(row['citation_key'])
        except Exception as e:
            print(f"Warning: Could not load evidence file: {e}")
        return keys

    @staticmethod
    def validate_at_entry(citation_key: str, evidence_csv: Path) -> None:
        """
        Reject citation if not in evidence file - fail fast.

        Raises:
            CitationNotFoundError: If citation not in evidence file
        """
        evidence_keys = CitationEntryValidator.load_evidence_keys(evidence_csv)

        if citation_key not in evidence_keys:
            raise CitationNotFoundError(
                f"\n❌ Citation Verification Failed\n\n"
                f"Citation [{citation_key}] not in literature_evidence.csv\n\n"
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

    @staticmethod
    def validate_multiple(citation_keys: List[str], evidence_csv: Path) -> Tuple[List[str], List[str]]:
        """
        Validate multiple citations, return valid and invalid lists.

        Returns:
            Tuple of (valid_keys, invalid_keys)
        """
        evidence_keys = CitationEntryValidator.load_evidence_keys(evidence_csv)
        valid = [k for k in citation_keys if k in evidence_keys]
        invalid = [k for k in citation_keys if k not in evidence_keys]
        return valid, invalid


# Layer 2: Business Logic Validation
class CitationBusinessValidator:
    """Validate citations are appropriate for section type."""

    SECTION_RULES = {
        'abstract': {
            'max_citations': 2,
            'reason': 'Abstracts should be self-contained, citations rarely appropriate',
            'allowed_types': ['seminal']
        },
        'introduction': {
            'max_citations': None,
            'reason': 'Broad background, any relevant citations appropriate',
            'allowed_types': ['seminal', 'review', 'recent', 'tool']
        },
        'methods': {
            'max_citations': None,
            'reason': 'Should cite tools/datasets/protocols actually used',
            'allowed_types': ['tool', 'protocol', 'dataset'],
            'forbidden_types': ['review']
        },
        'results': {
            'max_citations': None,
            'reason': 'Should compare to other studies, cite benchmarks',
            'allowed_types': ['recent', 'benchmark'],
            'forbidden_types': ['review']
        },
        'discussion': {
            'max_citations': None,
            'reason': 'Broad interpretation, most citation types appropriate',
            'allowed_types': ['seminal', 'review', 'recent', 'tool']
        }
    }

    def __init__(self, evidence_csv: Path):
        self.evidence_csv = evidence_csv
        self.warnings: List[str] = []

    def _load_citation_metadata(self) -> Dict[str, Dict]:
        """Load citation metadata from evidence file."""
        metadata = {}
        if not self.evidence_csv.exists():
            return metadata

        try:
            with open(self.evidence_csv, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if 'citation_key' in row:
                        metadata[row['citation_key']] = {
                            'title': row.get('title', ''),
                            'abstract': row.get('abstract', ''),
                            'doi': row.get('doi', ''),
                            'year': row.get('year', ''),
                            'citation_type': row.get('citation_type', 'unknown')
                        }
        except Exception as e:
            print(f"Warning: Could not load citation metadata: {e}")

        return metadata

    def _infer_citation_type(self, metadata: Dict) -> str:
        """Infer citation type from metadata."""
        title = metadata.get('title', '').lower()
        abstract = metadata.get('abstract', '').lower()

        # Tool indicators
        if any(word in title for word in ['software', 'tool', 'pipeline', 'package', 'algorithm']):
            return 'tool'

        # Review indicators
        if any(word in title for word in ['review', 'survey', 'overview', 'perspectives']):
            return 'review'

        # Protocol indicators
        if any(word in title for word in ['protocol', 'method', 'procedure', 'workflow']):
            return 'protocol'

        # Dataset indicators
        if any(word in title for word in ['database', 'dataset', 'repository', 'collection']):
            return 'dataset'

        # Benchmark indicators
        if any(word in title for word in ['benchmark', 'comparison', 'evaluation']):
            return 'benchmark'

        # Recent research (< 5 years)
        year = metadata.get('year', '')
        if year and int(year) >= datetime.now().year - 5:
            return 'recent'

        # Seminal (older, frequently cited)
        if year and int(year) < datetime.now().year - 10:
            return 'seminal'

        return 'unknown'

    def validate_section_appropriateness(self, section: str, citations: List[str]) -> List[str]:
        """
        Validate citations are appropriate for section type.

        Returns:
            List of warning messages
        """
        self.warnings = []
        section_lower = section.lower()

        if section_lower not in self.SECTION_RULES:
            return self.warnings

        rules = self.SECTION_RULES[section_lower]
        metadata = self._load_citation_metadata()

        # Check citation count limits
        if rules.get('max_citations') and len(citations) > rules['max_citations']:
            self.warnings.append(
                f"⚠️  {section} has {len(citations)} citations, "
                f"but should have ≤{rules['max_citations']}. {rules['reason']}"
            )

        # Check citation types
        for cit in citations:
            if cit not in metadata:
                continue

            cit_type = metadata[cit].get('citation_type', 'unknown')
            if cit_type == 'unknown':
                cit_type = self._infer_citation_type(metadata[cit])

            # Check forbidden types
            if 'forbidden_types' in rules and cit_type in rules['forbidden_types']:
                self.warnings.append(
                    f"⚠️  Citation [{cit}] appears to be {cit_type}, "
                    f"which is not appropriate for {section}. {rules['reason']}"
                )

            # Check allowed types (if specified)
            if 'allowed_types' in rules and cit_type not in rules['allowed_types']:
                self.warnings.append(
                    f"⚠️  Citation [{cit}] appears to be {cit_type}, "
                    f"but {section} typically uses: {', '.join(rules['allowed_types'])}"
                )

        return self.warnings


# Layer 3: Assembly Validation
class CitationAssemblyValidator:
    """Validate completeness at manuscript compilation."""

    @staticmethod
    def extract_citations_from_text(manuscript_path: Path) -> Set[str]:
        """Extract all citation keys from manuscript text."""
        if not manuscript_path.exists():
            return set()

        try:
            with open(manuscript_path, 'r', encoding='utf-8') as f:
                content = f.read()
            # Match [author2024] style citations
            citations = re.findall(r'\[([a-zA-Z]+\d{4}[a-z]?)\]', content)
            return set(citations)
        except Exception as e:
            print(f"Error extracting citations: {e}")
            return set()

    @staticmethod
    def extract_citations_from_bib(bib_path: Path) -> Set[str]:
        """Extract all citation keys from .bib file."""
        if not bib_path.exists():
            return set()

        try:
            with open(bib_path, 'r', encoding='utf-8') as f:
                content = f.read()
            # Match @article{key, or @book{key, etc.
            citations = re.findall(r'@\w+\{([^,]+),', content)
            return set(citations)
        except Exception as e:
            print(f"Error extracting bib citations: {e}")
            return set()

    @staticmethod
    def validate_citation_completeness(manuscript_path: Path, bib_path: Path) -> Tuple[Set[str], Set[str]]:
        """
        Validate all text citations in bib, all bib entries cited.

        Returns:
            Tuple of (orphaned_text, orphaned_bib)

        Raises:
            CitationMismatchError: If mismatches found
        """
        text_cites = CitationAssemblyValidator.extract_citations_from_text(manuscript_path)
        bib_cites = CitationAssemblyValidator.extract_citations_from_bib(bib_path)

        orphaned_text = text_cites - bib_cites
        orphaned_bib = bib_cites - text_cites

        if orphaned_text or orphaned_bib:
            error_msg = "\n❌ Citation Mismatch Error\n\n"

            if orphaned_text:
                error_msg += f"Citations in text but not in bibliography ({len(orphaned_text)}):\n"
                for cit in sorted(orphaned_text):
                    error_msg += f"  - [{cit}]\n"
                error_msg += "\n"

            if orphaned_bib:
                error_msg += f"Citations in bibliography but not in text ({len(orphaned_bib)}):\n"
                for cit in sorted(orphaned_bib):
                    error_msg += f"  - [{cit}]\n"
                error_msg += "\n"

            error_msg += "Next steps:\n"
            if orphaned_text:
                error_msg += "1. Add missing entries to bibliography\n"
            if orphaned_bib:
                error_msg += "2. Remove unused entries from bibliography or cite them in text\n"

            raise CitationMismatchError(error_msg)

        return orphaned_text, orphaned_bib


# Layer 4: Audit Trail
class CitationAuditor:
    """Record citation usage for forensics and debugging."""

    def __init__(self, audit_log_path: Path):
        self.audit_log_path = audit_log_path
        self.audit_log_path.parent.mkdir(parents=True, exist_ok=True)

    def log_citation_usage(
        self,
        section: str,
        citation: str,
        context: str,
        evidence_csv: Path
    ) -> None:
        """Record when/where/why citations used."""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'section': section,
            'citation': citation,
            'context': context[:200],  # First 200 chars
            'doi_verified': self._verify_doi(citation, evidence_csv)
        }

        # Append to JSONL audit log
        with open(self.audit_log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry) + '\n')

    def _verify_doi(self, citation_key: str, evidence_csv: Path) -> bool:
        """Check if citation has verified DOI in evidence file."""
        if not evidence_csv.exists():
            return False

        try:
            with open(evidence_csv, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get('citation_key') == citation_key:
                        doi = row.get('doi', '')
                        return bool(doi and doi.startswith('10.'))
        except Exception:
            pass

        return False

    def get_citation_history(self, citation: str) -> List[Dict]:
        """Retrieve all usage instances of a citation."""
        if not self.audit_log_path.exists():
            return []

        history = []
        try:
            with open(self.audit_log_path, 'r', encoding='utf-8') as f:
                for line in f:
                    entry = json.loads(line)
                    if entry.get('citation') == citation:
                        history.append(entry)
        except Exception as e:
            print(f"Error reading audit log: {e}")

        return history

    def export_audit_report(self, output_path: Path) -> None:
        """Export human-readable audit report."""
        if not self.audit_log_path.exists():
            print("No audit log found")
            return

        entries = []
        try:
            with open(self.audit_log_path, 'r', encoding='utf-8') as f:
                for line in f:
                    entries.append(json.loads(line))
        except Exception as e:
            print(f"Error reading audit log: {e}")
            return

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# Citation Audit Report\n\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n\n")
            f.write(f"Total citation usages: {len(entries)}\n\n")

            # Group by citation
            by_citation = {}
            for entry in entries:
                cit = entry['citation']
                if cit not in by_citation:
                    by_citation[cit] = []
                by_citation[cit].append(entry)

            f.write("## Citations by Key\n\n")
            for cit in sorted(by_citation.keys()):
                usages = by_citation[cit]
                f.write(f"### [{cit}]\n\n")
                f.write(f"- Used {len(usages)} time(s)\n")
                f.write(f"- DOI verified: {usages[0]['doi_verified']}\n")
                f.write(f"- Sections: {', '.join(set(u['section'] for u in usages))}\n\n")


# Convenience function for complete validation
def validate_all_layers(
    citation_keys: List[str],
    section: str,
    evidence_csv: Path,
    manuscript_path: Optional[Path] = None,
    bib_path: Optional[Path] = None,
    audit_log_path: Optional[Path] = None
) -> Tuple[bool, List[str]]:
    """
    Run all validation layers.

    Returns:
        Tuple of (success, error_messages)
    """
    errors = []

    # Layer 1: Entry validation
    try:
        for cit in citation_keys:
            CitationEntryValidator.validate_at_entry(cit, evidence_csv)
    except CitationNotFoundError as e:
        errors.append(str(e))
        return False, errors

    # Layer 2: Business logic validation
    validator = CitationBusinessValidator(evidence_csv)
    warnings = validator.validate_section_appropriateness(section, citation_keys)
    if warnings:
        errors.extend(warnings)

    # Layer 3: Assembly validation (if manuscript provided)
    if manuscript_path and bib_path:
        try:
            CitationAssemblyValidator.validate_citation_completeness(
                manuscript_path, bib_path
            )
        except CitationMismatchError as e:
            errors.append(str(e))
            return False, errors

    # Layer 4: Audit logging (if enabled)
    if audit_log_path:
        auditor = CitationAuditor(audit_log_path)
        for cit in citation_keys:
            auditor.log_citation_usage(section, cit, "", evidence_csv)

    return len(errors) == 0, errors


if __name__ == '__main__':
    # Example usage
    import sys

    if len(sys.argv) < 4:
        print("Usage: python rrwrite_citation_validator.py <section> <evidence_csv> <citation_key>...")
        sys.exit(1)

    section = sys.argv[1]
    evidence_csv = Path(sys.argv[2])
    citations = sys.argv[3:]

    success, errors = validate_all_layers(
        citations,
        section,
        evidence_csv
    )

    if not success:
        print("\n".join(errors))
        sys.exit(1)
    else:
        print(f"✅ All {len(citations)} citations validated successfully")
        sys.exit(0)
