#!/usr/bin/env python3
"""
IssueResolver - Tracks resolution of critique issues across manuscript versions.

This module analyzes critique reports from consecutive versions and determines
which issues were resolved, which persist, and which are new.
"""

import re
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from difflib import SequenceMatcher


class Issue:
    """Represents a single critique issue."""

    def __init__(
        self,
        description: str,
        section: Optional[str] = None,
        severity: str = "MINOR",
        category: str = "other",
        issue_number: Optional[int] = None
    ):
        """
        Initialize an issue.

        Args:
            description: Issue description
            section: Affected section
            severity: MAJOR, MINOR, or WARNING
            category: Issue category
            issue_number: Sequential number in critique
        """
        self.description = description
        self.section = section
        self.severity = severity
        self.category = category
        self.issue_number = issue_number
        self.id = self._generate_id()

    def _generate_id(self) -> str:
        """Generate stable ID from issue content."""
        # Use description + section for ID
        content = f"{self.description}:{self.section or 'global'}"
        hash_val = hashlib.md5(content.encode()).hexdigest()[:8]
        return f"issue_{hash_val}"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "issue_id": self.id,
            "description": self.description,
            "section": self.section,
            "severity": self.severity,
            "category": self.category
        }


class IssueResolver:
    """Tracks issue resolution across manuscript versions."""

    def __init__(self, manuscript_dir: Path):
        """
        Initialize issue resolver.

        Args:
            manuscript_dir: Path to manuscript directory
        """
        self.manuscript_dir = Path(manuscript_dir)

    def load_critique_issues(self, critique_path: Path) -> List[Issue]:
        """
        Load issues from a critique report.

        Args:
            critique_path: Path to critique_content_vN.md or critique_format_vN.md

        Returns:
            List of Issue objects
        """
        if not critique_path.exists():
            return []

        content = critique_path.read_text(encoding="utf-8")
        issues = []

        # Parse sections
        is_content = "content" in critique_path.stem
        if is_content:
            issues.extend(self._parse_content_critique(content))
        else:
            issues.extend(self._parse_format_critique(content))

        return issues

    def _parse_content_critique(self, content: str) -> List[Issue]:
        """Parse content critique report."""
        issues = []

        # Find major and minor sections
        major_section = self._extract_section(content, "## Major Issues (Content)")
        minor_section = self._extract_section(content, "## Minor Issues (Content)")

        if major_section:
            issues.extend(self._parse_issue_list(major_section, "MAJOR"))

        if minor_section:
            issues.extend(self._parse_issue_list(minor_section, "MINOR"))

        return issues

    def _parse_format_critique(self, content: str) -> List[Issue]:
        """Parse format critique report."""
        issues = []

        # Find formatting and warning sections
        format_section = self._extract_section(content, "## Formatting Issues")
        warning_section = self._extract_section(content, "## Warnings")

        if format_section:
            issues.extend(self._parse_issue_list(format_section, "MAJOR", category="formatting"))

        if warning_section:
            issues.extend(self._parse_issue_list(warning_section, "WARNING"))

        return issues

    def _extract_section(self, content: str, header: str) -> Optional[str]:
        """Extract content between a header and the next ## header."""
        pattern = rf'{re.escape(header)}(.*?)(?=^##|\Z)'
        match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
        return match.group(1).strip() if match else None

    def _parse_issue_list(
        self,
        section_content: str,
        severity: str,
        category: str = "other"
    ) -> List[Issue]:
        """Parse numbered issue list."""
        issues = []

        # Match pattern: 1. **Category:** Description
        pattern = r'^\d+\.\s+\*\*([^:]+):\*\*\s+(.+?)(?=^\d+\.\s+\*\*|\Z)'
        matches = re.finditer(pattern, section_content, re.MULTILINE | re.DOTALL)

        for i, match in enumerate(matches, 1):
            cat = match.group(1).strip()
            description_block = match.group(2).strip()

            # Extract main description (first line/paragraph)
            lines = description_block.split('\n')
            description = lines[0].strip()

            # Try to infer section from description or Impact/Action fields
            section = self._infer_section(description_block)

            issues.append(Issue(
                description=description,
                section=section,
                severity=severity,
                category=category if category != "other" else cat.lower().replace(' ', '_'),
                issue_number=i
            ))

        return issues

    def _infer_section(self, text: str) -> Optional[str]:
        """Infer affected section from issue text."""
        text_lower = text.lower()

        # Section keywords
        section_keywords = {
            "abstract": ["abstract"],
            "introduction": ["introduction", "intro"],
            "methods": ["methods", "methodology", "materials and methods"],
            "results": ["results"],
            "discussion": ["discussion"],
            "availability": ["availability", "data availability"]
        }

        for section, keywords in section_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return section

        return None

    def match_issues(
        self,
        old_issues: List[Issue],
        new_issues: List[Issue],
        threshold: float = 0.7
    ) -> Tuple[List[Issue], List[Issue], List[Issue]]:
        """
        Match issues between two versions using fuzzy matching.

        Args:
            old_issues: Issues from previous critique
            new_issues: Issues from current critique
            threshold: Similarity threshold for matching (0.0-1.0)

        Returns:
            Tuple of (resolved_issues, persisting_issues, new_issues)
        """
        matched_old = set()
        matched_new = set()
        persisting = []

        # Match issues using description similarity
        for old_issue in old_issues:
            best_match = None
            best_score = 0.0

            for i, new_issue in enumerate(new_issues):
                if i in matched_new:
                    continue

                # Compute similarity
                score = SequenceMatcher(
                    None,
                    old_issue.description.lower(),
                    new_issue.description.lower()
                ).ratio()

                # Boost score if sections match
                if old_issue.section == new_issue.section and old_issue.section:
                    score *= 1.2

                if score > best_score and score >= threshold:
                    best_score = score
                    best_match = i

            if best_match is not None:
                matched_old.add(old_issues.index(old_issue))
                matched_new.add(best_match)
                persisting.append(new_issues[best_match])

        # Resolved = old issues not matched
        resolved = [
            old_issues[i] for i in range(len(old_issues))
            if i not in matched_old
        ]

        # New = new issues not matched
        new = [
            new_issues[i] for i in range(len(new_issues))
            if i not in matched_new
        ]

        return resolved, persisting, new

    def infer_resolution_type(
        self,
        issue: Issue,
        diff_report: Dict[str, Any]
    ) -> str:
        """
        Infer how an issue was resolved based on diff report.

        Args:
            issue: Resolved issue
            diff_report: Diff report from DiffReportGenerator

        Returns:
            Resolution type (content_added, citations_added, etc.)
        """
        # Check section changes if section is known
        if issue.section:
            section_data = next(
                (s for s in diff_report["sections"] if s["section_name"] == issue.section),
                None
            )

            if section_data:
                changes = section_data["changes"]

                # Word count reduction for verbosity issues
                if "verbose" in issue.description.lower() or "concise" in issue.description.lower():
                    if changes["word_count_delta"] < -20:
                        return "word_count_reduced"

                # Content added for missing information
                if "missing" in issue.description.lower() or "lack" in issue.description.lower():
                    if changes["additions"] > 0:
                        return "content_added"

                # Content revised for clarity/accuracy
                if changes["modifications"] > changes["additions"]:
                    return "content_revised"

        # Check citation changes
        if "citation" in issue.description.lower() or "reference" in issue.description.lower():
            if diff_report["summary"]["citations_added"] > 0:
                return "citations_added"

        # Check structure
        if "structure" in issue.description.lower() or "organization" in issue.description.lower():
            if any("Structure reorganized" in s.get("notable_changes", []) for s in diff_report["sections"]):
                return "structure_changed"

        # Default
        return "other"

    def extract_resolution_evidence(
        self,
        issue: Issue,
        diff_report: Dict[str, Any]
    ) -> str:
        """
        Extract evidence of resolution from diff report.

        Args:
            issue: Resolved issue
            diff_report: Diff report

        Returns:
            Evidence string (diff excerpt or description)
        """
        if not issue.section:
            return "Issue resolved through manuscript-wide changes"

        section_data = next(
            (s for s in diff_report["sections"] if s["section_name"] == issue.section),
            None
        )

        if section_data and section_data.get("notable_changes"):
            return "; ".join(section_data["notable_changes"][:3])

        if section_data:
            changes = section_data["changes"]
            return (
                f"{changes['additions']} lines added, "
                f"{changes['deletions']} lines deleted, "
                f"{changes['word_count_delta']:+d} words"
            )

        return "Evidence not available"

    def enrich_diff_report_with_issues(
        self,
        diff_report: Dict[str, Any],
        version_old: int,
        version_new: int
    ) -> Dict[str, Any]:
        """
        Enrich a diff report with issue tracking data.

        Args:
            diff_report: Diff report from DiffReportGenerator
            version_old: Old version number
            version_new: New version number

        Returns:
            Updated diff report with issues populated
        """
        # Load critique reports
        old_critique = self.manuscript_dir / f"critique_content_v{version_old}.md"
        new_critique = self.manuscript_dir / f"critique_content_v{version_new}.md"

        old_issues = self.load_critique_issues(old_critique)
        new_issues = self.load_critique_issues(new_critique)

        # Match issues
        resolved, persisting, new = self.match_issues(old_issues, new_issues)

        # Build resolved issues list
        resolved_list = []
        for issue in resolved:
            resolution_type = self.infer_resolution_type(issue, diff_report)
            evidence = self.extract_resolution_evidence(issue, diff_report)

            resolved_dict = issue.to_dict()
            resolved_dict["resolution_type"] = resolution_type
            resolved_dict["evidence"] = evidence

            resolved_list.append(resolved_dict)

        # Update diff report
        diff_report["issues"] = {
            "resolved": resolved_list,
            "persisting": [i.to_dict() for i in persisting],
            "new": [i.to_dict() for i in new]
        }

        # Update summary
        diff_report["summary"]["issues_resolved"] = len(resolved)
        diff_report["summary"]["issues_remaining"] = len(persisting) + len(new)

        # Compute metrics
        total_old = len(old_issues)
        total_new = len(new_issues)

        improvement_rate = len(resolved) / total_old if total_old > 0 else 0.0

        # Quality scores (simple heuristic: fewer issues = higher quality)
        max_issues = 20  # Normalize to this
        quality_old = max(0, 1 - (total_old / max_issues))
        quality_new = max(0, 1 - (total_new / max_issues))

        # Convergence indicator
        if total_new == 0:
            convergence = "complete"
        elif improvement_rate >= 0.5:
            convergence = "converging"
        elif improvement_rate >= 0.1:
            convergence = "stalled"
        else:
            convergence = "diverging"

        diff_report["metrics"] = {
            "improvement_rate": round(improvement_rate, 3),
            "quality_score_old": round(quality_old, 3),
            "quality_score_new": round(quality_new, 3),
            "convergence_indicator": convergence
        }

        return diff_report


if __name__ == "__main__":
    import sys
    import json

    if len(sys.argv) < 2:
        print("Usage: rrwrite_issue_resolver.py <manuscript_dir>")
        sys.exit(1)

    manuscript_dir = Path(sys.argv[1])
    resolver = IssueResolver(manuscript_dir)

    # Test loading critique
    critique_path = manuscript_dir / "critique_content_v1.md"
    if critique_path.exists():
        issues = resolver.load_critique_issues(critique_path)
        print(f"Loaded {len(issues)} issues from {critique_path.name}")
        for issue in issues[:5]:
            print(f"  - {issue.severity}: {issue.description[:60]}...")
