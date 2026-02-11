#!/usr/bin/env python3
"""
RRWrite Section Reviser

Applies targeted revisions to individual manuscript sections.
Supports both rule-based and LLM-based revision strategies.

Revision strategies:
- Evidence issues: Add citations from literature_evidence.csv
- Word count: Condense while preserving key points
- Reproducibility: Add software versions, parameters from repository_analysis.md
- Citation format: Fix to [Author2024] format
- Interpretation: Move from Results to Discussion
"""

import re
import os
from pathlib import Path

# Optional anthropic import for LLM-based revisions
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
import logging

# Import revision context and parser
try:
    from rrwrite_revision_context import RevisionContext, Citation
    from rrwrite_revision_parser import Issue
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from rrwrite_revision_context import RevisionContext, Citation
    from rrwrite_revision_parser import Issue


@dataclass
class ValidationResult:
    """Result of validation after revision."""
    passed: bool
    errors: List[str]
    warnings: List[str]

    def __str__(self):
        if self.passed:
            return "✓ Validation passed"
        else:
            return f"✗ Validation failed: {len(self.errors)} errors, {len(self.warnings)} warnings"


@dataclass
class RevisionResult:
    """Result of section revision."""
    content: str
    changes_made: List[str]
    validation: ValidationResult
    success: bool

    def __str__(self):
        status = "✓" if self.success else "✗"
        return f"{status} Revision: {len(self.changes_made)} changes, {self.validation}"


class SectionReviser:
    """Base class for section-specific revision logic."""

    def __init__(
        self,
        section_name: str,
        section_file: Path,
        issues: List[Issue],
        context: RevisionContext
    ):
        """Initialize section reviser.

        Args:
            section_name: Section name (e.g., 'introduction', 'methods')
            section_file: Path to section markdown file
            issues: List of issues to address in this section
            context: Revision context with citations, guidelines, etc.
        """
        self.section_name = section_name
        self.section_file = section_file
        self.issues = issues
        self.context = context
        self.logger = logging.getLogger(__name__)

        # Load section content
        self.original_content = self._load_content()

    def _load_content(self) -> str:
        """Load section content from file."""
        if not self.section_file.exists():
            self.logger.error(f"Section file not found: {self.section_file}")
            return ""

        with open(self.section_file, 'r', encoding='utf-8') as f:
            return f.read()

    def revise(self) -> RevisionResult:
        """Apply revisions to the section.

        Returns:
            RevisionResult with updated content and validation
        """
        changes_made = []
        content = self.original_content

        # Apply revisions based on issue categories
        for issue in self.issues:
            if issue.category == "Citation Format":
                content, changed = self._fix_citation_format(content, issue)
                if changed:
                    changes_made.append(f"Fixed citation format: {issue.description[:50]}")

            elif issue.category == "Word Count":
                content, changed = self._reduce_word_count(content, issue)
                if changed:
                    changes_made.append(f"Reduced word count: {issue.description[:50]}")

            elif issue.category == "Evidence":
                content, changed = self._add_evidence_citations(content, issue)
                if changed:
                    changes_made.append(f"Added evidence: {issue.description[:50]}")

            elif issue.category == "Reproducibility":
                content, changed = self._add_reproducibility_elements(content, issue)
                if changed:
                    changes_made.append(f"Added reproducibility: {issue.description[:50]}")

        # Validate revisions
        validation = self._validate_revisions(content)

        return RevisionResult(
            content=content,
            changes_made=changes_made,
            validation=validation,
            success=validation.passed
        )

    def _fix_citation_format(self, content: str, issue: Issue) -> tuple[str, bool]:
        """Fix citation format to [Author2024].

        Args:
            content: Section content
            issue: Citation format issue

        Returns:
            Tuple of (updated_content, changed)
        """
        # Pattern: malformed citations like "[1]", "[Smith et al.]", etc.
        # This is a rule-based fix for common patterns

        original = content

        # Fix numeric citations [1] -> [authorYYYY]
        # This requires looking up the reference, which we'll skip for now
        # and just flag them for manual review

        # Fix "[Author et al.]" -> "[author2024]"
        # Extract year from surrounding context if possible

        # For now, just log the issue
        self.logger.warning(f"Citation format fix requires manual intervention: {issue.description[:50]}")

        return content, False

    def _reduce_word_count(self, content: str, issue: Issue) -> tuple[str, bool]:
        """Reduce word count using LLM.

        Args:
            content: Section content
            issue: Word count issue

        Returns:
            Tuple of (updated_content, changed)
        """
        # Extract target word count from issue description
        target_match = re.search(r'(\d+)\s+words?', issue.description)
        if not target_match:
            self.logger.warning(f"Cannot extract target word count from: {issue.description}")
            return content, False

        target_count = int(target_match.group(1))

        # Use LLM to condense
        try:
            condensed = self._llm_condense(content, target_count)
            return condensed, True
        except Exception as e:
            self.logger.error(f"Failed to condense content: {e}")
            return content, False

    def _add_evidence_citations(self, content: str, issue: Issue) -> tuple[str, bool]:
        """Add citations for claims lacking evidence.

        Args:
            content: Section content
            issue: Evidence issue

        Returns:
            Tuple of (updated_content, changed)
        """
        # Extract claim from issue description
        claim_match = re.search(r'"([^"]+)"', issue.description)
        if not claim_match:
            # Use first part of description as claim
            claim = issue.description[:100]
        else:
            claim = claim_match.group(1)

        # Find relevant citations
        citations = self.context.find_relevant_citations(claim, max_results=2)

        if not citations:
            self.logger.warning(f"No relevant citations found for: {claim[:50]}")
            return content, False

        # Find claim in content and add citation
        if claim in content:
            # Add citation after the claim
            citation_str = ','.join([c.citation_key for c in citations])
            updated_content = content.replace(claim, f"{claim} [{citation_str}]")
            return updated_content, True

        # If exact match not found, use LLM to insert citation appropriately
        try:
            updated_content = self._llm_add_citation(content, claim, citations)
            return updated_content, True
        except Exception as e:
            self.logger.error(f"Failed to add citations: {e}")
            return content, False

    def _add_reproducibility_elements(self, content: str, issue: Issue) -> tuple[str, bool]:
        """Add reproducibility elements (versions, parameters, data sources).

        Args:
            content: Section content
            issue: Reproducibility issue

        Returns:
            Tuple of (updated_content, changed)
        """
        # Extract software versions from context
        versions = self.context.get_all_software_versions()

        if not versions:
            self.logger.warning("No software versions found in repository analysis")
            return content, False

        # Add software versions section if not present
        if "software versions" not in content.lower():
            versions_text = "\n\n## Software Versions\n\n"
            for name, version in sorted(versions.items()):
                versions_text += f"- {name}: {version}\n"

            # Insert before references or at end
            if "## References" in content:
                content = content.replace("## References", versions_text + "\n## References")
            else:
                content += versions_text

            return content, True

        return content, False

    def _validate_revisions(self, content: str) -> ValidationResult:
        """Validate revised content.

        Args:
            content: Revised content

        Returns:
            ValidationResult
        """
        errors = []
        warnings = []

        # Check 1: Citations exist in literature_evidence.csv
        citation_keys = self.context.extract_citations_from_text(content)
        for key in citation_keys:
            if not self.context.validate_citation_exists(key):
                errors.append(f"Citation not found in evidence: [{key}]")

        # Check 2: No malformed citations
        malformed = re.findall(r'\[\d+\]', content)
        if malformed:
            warnings.append(f"Found {len(malformed)} numeric citations (should use [author2024] format)")

        # Check 3: Word count (if applicable)
        word_limit = self.context.get_word_limit(self.section_name)
        if word_limit:
            word_count = len(re.findall(r'\w+', content))
            if word_count > word_limit:
                warnings.append(f"Word count {word_count} exceeds limit {word_limit}")

        return ValidationResult(
            passed=(len(errors) == 0),
            errors=errors,
            warnings=warnings
        )

    def _llm_condense(self, content: str, target_words: int) -> str:
        """Use LLM to condense content to target word count.

        Args:
            content: Original content
            target_words: Target word count

        Returns:
            Condensed content
        """
        if not ANTHROPIC_AVAILABLE:
            self.logger.warning("Anthropic SDK not available, skipping LLM condensation")
            return content

        client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

        prompt = f"""Condense the following text to approximately {target_words} words while preserving all key points, citations, and technical details.

Original text:
{content}

Requirements:
- Maintain all citations in [author2024] format
- Preserve technical accuracy
- Keep the same section structure
- Target: {target_words} words

Condensed version:"""

        message = client.messages.create(
            model="claude-sonnet-4-5-20241022",
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}]
        )

        return message.content[0].text

    def _llm_add_citation(self, content: str, claim: str, citations: List[Citation]) -> str:
        """Use LLM to add citations to content.

        Args:
            content: Original content
            claim: Claim needing citation
            citations: List of relevant citations

        Returns:
            Updated content with citations
        """
        if not ANTHROPIC_AVAILABLE:
            self.logger.warning("Anthropic SDK not available, skipping LLM citation addition")
            return content

        client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

        citation_info = "\n".join([
            f"- [{c.citation_key}]: {c.evidence}"
            for c in citations
        ])

        prompt = f"""Add appropriate citations to support the following claim in the text.

Text:
{content}

Claim needing citation: "{claim}"

Available citations:
{citation_info}

Instructions:
- Insert citation(s) at the most appropriate location to support the claim
- Use [author2024] format
- Maintain the original text structure and meaning
- Only add citations, do not modify other content

Updated text:"""

        message = client.messages.create(
            model="claude-sonnet-4-5-20241022",
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}]
        )

        return message.content[0].text


class AbstractReviser(SectionReviser):
    """Specialized reviser for abstract section."""

    def _reduce_word_count(self, content: str, issue: Issue) -> tuple[str, bool]:
        """Abstract-specific word count reduction.

        Focus on:
        - Remove redundant phrases
        - Condense background
        - Keep key results and conclusions
        """
        return super()._reduce_word_count(content, issue)


class MethodsReviser(SectionReviser):
    """Specialized reviser for methods section."""

    def _add_reproducibility_elements(self, content: str, issue: Issue) -> tuple[str, bool]:
        """Methods-specific reproducibility enhancement.

        Add:
        - Software versions
        - Algorithm parameters
        - Data sources
        - Code availability
        """
        # Get repository path
        repo_path = self.context.get_repository_path()

        # Add code availability statement
        if repo_path and "code availability" not in content.lower():
            availability = f"\n\n## Code Availability\n\nAll analysis code is available at: {repo_path}\n"

            # Insert before references or at end
            if "## References" in content:
                content = content.replace("## References", availability + "\n## References")
            else:
                content += availability

            return content, True

        return super()._add_reproducibility_elements(content, issue)


class ResultsReviser(SectionReviser):
    """Specialized reviser for results section."""

    def revise(self) -> RevisionResult:
        """Results-specific revision.

        Handle:
        - Move interpretation to discussion
        - Add figure/table references
        """
        # First apply base revisions
        result = super().revise()

        # Check for interpretation statements to move
        interpretation_keywords = [
            "this suggests", "this indicates", "this implies",
            "this demonstrates", "this shows that", "therefore",
            "thus", "hence", "consequently"
        ]

        # Flag interpretations (don't auto-move, too risky)
        for keyword in interpretation_keywords:
            if keyword in result.content.lower():
                result.validation.warnings.append(
                    f"Possible interpretation found (consider moving to Discussion): '{keyword}'"
                )

        return result


class DiscussionReviser(SectionReviser):
    """Specialized reviser for discussion section."""

    def _add_evidence_citations(self, content: str, issue: Issue) -> tuple[str, bool]:
        """Discussion-specific citation addition.

        Focus on:
        - Supporting claims with literature
        - Strengthening arguments
        - Comparing to prior work
        """
        return super()._add_evidence_citations(content, issue)


def get_reviser(
    section_name: str,
    section_file: Path,
    issues: List[Issue],
    context: RevisionContext
) -> SectionReviser:
    """Factory function to get appropriate reviser for section.

    Args:
        section_name: Section name
        section_file: Path to section file
        issues: List of issues for this section
        context: Revision context

    Returns:
        Appropriate SectionReviser subclass
    """
    revisers = {
        "abstract": AbstractReviser,
        "methods": MethodsReviser,
        "results": ResultsReviser,
        "discussion": DiscussionReviser,
    }

    reviser_class = revisers.get(section_name, SectionReviser)
    return reviser_class(section_name, section_file, issues, context)


def main():
    """CLI for testing section reviser."""
    import argparse
    from rrwrite_revision_parser import CritiqueParser

    parser = argparse.ArgumentParser(description="Test RRWrite section reviser")
    parser.add_argument("--manuscript-dir", required=True, help="Manuscript directory")
    parser.add_argument("--section", required=True, help="Section name")
    parser.add_argument("--version", type=int, default=1, help="Critique version")
    parser.add_argument("--dry-run", action="store_true", help="Don't save changes")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format='%(levelname)s: %(message)s'
    )

    manuscript_dir = Path(args.manuscript_dir)

    # Load context
    context = RevisionContext(manuscript_dir)

    # Parse critiques
    critique_parser = CritiqueParser(manuscript_dir)
    all_issues = critique_parser.parse_critique_reports(version=args.version)
    all_issues = critique_parser.infer_all_sections(all_issues)

    # Filter issues for this section
    section_issues = [i for i in all_issues if i.section == args.section]

    if not section_issues:
        print(f"No issues found for section: {args.section}")
        return

    print(f"\nRevising {args.section} ({len(section_issues)} issues)")

    # Get section file
    section_file = manuscript_dir / f"{args.section}.md"

    # Create reviser
    reviser = get_reviser(args.section, section_file, section_issues, context)

    # Revise
    result = reviser.revise()

    # Print result
    print(f"\n{result}")
    print(f"\nChanges made:")
    for change in result.changes_made:
        print(f"  - {change}")

    print(f"\nValidation:")
    print(f"  Errors: {len(result.validation.errors)}")
    for error in result.validation.errors:
        print(f"    - {error}")
    print(f"  Warnings: {len(result.validation.warnings)}")
    for warning in result.validation.warnings:
        print(f"    - {warning}")

    # Save if not dry run
    if not args.dry_run and result.success:
        with open(section_file, 'w', encoding='utf-8') as f:
            f.write(result.content)
        print(f"\n✓ Saved revised section: {section_file}")


if __name__ == "__main__":
    main()
