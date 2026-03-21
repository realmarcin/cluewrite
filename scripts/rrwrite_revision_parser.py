#!/usr/bin/env python3
"""
RRWrite Revision Parser

Parses critique reports (critique_content_vN.md and critique_format_vN.md)
to extract structured issues for automated revision.

Extracts:
- Severity (major/minor)
- Category (Evidence, Citation Format, Reproducibility, etc.)
- Description
- Action (recommended fix)
- Section inference (introduction, methods, results, discussion, etc.)
"""

import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional, Dict
import logging


@dataclass
class Issue:
    """Represents a single critique issue."""
    severity: str  # 'major' or 'minor'
    category: str  # 'Evidence', 'Citation Format', 'Reproducibility', etc.
    description: str
    action: str  # Recommended fix
    section: Optional[str] = None  # Inferred: 'introduction', 'methods', etc.
    source_file: Optional[str] = None  # critique_content_v1.md or critique_format_v1.md

    def __str__(self):
        return f"[{self.severity.upper()}] {self.category}: {self.description[:60]}..."


class CritiqueParser:
    """Parses critique reports to extract structured issues."""

    # Category-to-section mapping rules
    CATEGORY_TO_SECTION = {
        "Reproducibility": "methods",
        "Methods": "methods",
        "Interpretation": "results",  # May also be discussion
        "Citation Format": None,  # Cross-cutting
        "Word Count": None,  # Section-specific, determined by description
        "Evidence": None,  # Need to infer from context
        "Coherence": None,  # Cross-cutting
        "Structure": None,  # Cross-cutting
    }

    # Section keywords for context search
    SECTION_KEYWORDS = {
        "abstract": ["abstract", "summary"],
        "introduction": ["introduction", "background"],
        "methods": ["methods", "methodology", "approach", "implementation"],
        "results": ["results", "findings", "validation"],
        "discussion": ["discussion", "implications", "future"],
        "availability": ["availability", "data availability", "code availability"],
    }

    def __init__(self, manuscript_dir: Path):
        """Initialize parser.

        Args:
            manuscript_dir: Path to manuscript directory
        """
        self.manuscript_dir = Path(manuscript_dir)
        self.logger = logging.getLogger(__name__)

    def parse_critique_reports(self, version: int = 1) -> List[Issue]:
        """Parse both content and format critique reports.

        Args:
            version: Critique version number (default: 1)

        Returns:
            List of Issue objects
        """
        issues = []

        # Parse content critique
        content_file = self.manuscript_dir / f"critique_content_v{version}.md"
        if content_file.exists():
            issues.extend(self.parse_content_critique(content_file))
        else:
            self.logger.warning(f"Content critique not found: {content_file}")

        # Parse format critique
        format_file = self.manuscript_dir / f"critique_format_v{version}.md"
        if format_file.exists():
            issues.extend(self.parse_format_critique(format_file))
        else:
            self.logger.warning(f"Format critique not found: {format_file}")

        return issues

    def parse_content_critique(self, filepath: Path) -> List[Issue]:
        """Parse critique_content_vN.md file.

        Args:
            filepath: Path to content critique file

        Returns:
            List of Issue objects
        """
        issues = []

        with open(filepath, 'r') as f:
            content = f.read()

        # Parse major issues
        major_section = self._extract_section(content, "## Major Issues (Content)")
        if major_section:
            issues.extend(self._parse_issue_list(major_section, severity="major", source_file=str(filepath)))

        # Parse minor issues
        minor_section = self._extract_section(content, "## Minor Issues (Content)")
        if minor_section:
            issues.extend(self._parse_issue_list(minor_section, severity="minor", source_file=str(filepath)))

        self.logger.info(f"Parsed {len(issues)} content issues from {filepath.name}")
        return issues

    def parse_format_critique(self, filepath: Path) -> List[Issue]:
        """Parse critique_format_vN.md file.

        Args:
            filepath: Path to format critique file

        Returns:
            List of Issue objects
        """
        issues = []

        with open(filepath, 'r') as f:
            content = f.read()

        # Parse formatting issues
        format_section = self._extract_section(content, "## Formatting Issues")
        if format_section:
            issues.extend(self._parse_issue_list(format_section, severity="major", source_file=str(filepath)))

        # Parse warnings (treat as minor)
        warning_section = self._extract_section(content, "## Warnings")
        if warning_section:
            issues.extend(self._parse_issue_list(warning_section, severity="minor", source_file=str(filepath)))

        self.logger.info(f"Parsed {len(issues)} format issues from {filepath.name}")
        return issues

    def _extract_section(self, content: str, heading: str) -> Optional[str]:
        """Extract content between a heading and the next heading.

        Robustly handles quoted/embedded headers in issue descriptions.

        Args:
            content: Full file content
            heading: Section heading (e.g., "## Major Issues")

        Returns:
            Section content or None
        """
        # Find all top-level section headers
        # Strategy: Real section headers are preceded by blank lines (or file start)
        # and are NOT inside quoted text blocks or numbered list items
        header_pattern = r'^##\s+(.+?)$'
        headers = []

        for match in re.finditer(header_pattern, content, re.MULTILINE):
            start_pos = match.start()
            end_pos = match.end()
            header_text = match.group(0).strip()

            # Check context before header - is it preceded by blank line?
            before_context = content[max(0, start_pos-200):start_pos]
            lines_before = before_context.split('\n')

            # Real section headers typically have:
            # 1. Blank line immediately before, OR start of file
            # 2. NOT inside a numbered list item

            # Strategy: Check if there's a numbered item start in the last 100 chars
            # AND if the next line after the header is NOT a numbered item
            # If both are true, this header is embedded in an issue description
            recent_context = content[max(0, start_pos-100):start_pos]
            item_start = re.search(r'\n\d+\.\s+\*\*[^:]+:\*\*', recent_context)

            if item_start:
                # Check what comes after this header
                # Real section headers are followed by blank line + numbered item
                # Embedded headers are followed by more text, then **Impact:** or **Action:**
                after_header = content[end_pos:min(len(content), end_pos+100)].lstrip()

                # If the next line is a numbered item, this is a real section header
                if not re.match(r'^\d+\.\s+\*\*', after_header):
                    # Not followed by an item, likely embedded in description - skip it
                    continue

            headers.append((header_text, start_pos, end_pos))

        # Find the requested heading
        target_idx = None
        for idx, (header_text, start_pos, end_pos) in enumerate(headers):
            if header_text == heading:
                target_idx = idx
                break

        if target_idx is None:
            return None

        # Extract content from end of this header to start of next header (or end of file)
        content_start = headers[target_idx][2]
        content_end = headers[target_idx + 1][1] if target_idx + 1 < len(headers) else len(content)

        section_content = content[content_start:content_end].strip()
        return section_content if section_content else None

    def _parse_issue_list(self, section_content: str, severity: str, source_file: str) -> List[Issue]:
        """Parse a numbered list of issues.

        Format:
        1. **Category:** Description
           - **Impact:** Impact description
           - **Action:** Action description

        Args:
            section_content: Content of issue section
            severity: 'major' or 'minor'
            source_file: Source critique file

        Returns:
            List of Issue objects
        """
        issues = []

        # Split by numbered items
        item_pattern = r'^\d+\.\s+\*\*([^:]+):\*\*\s+(.+?)(?=^\d+\.\s+\*\*|\Z)'
        matches = re.finditer(item_pattern, section_content, re.MULTILINE | re.DOTALL)

        for match in matches:
            category = match.group(1).strip()
            item_content = match.group(2).strip()

            # Extract description (everything before "Impact:" or "Action:")
            # Handle multi-line descriptions that may contain markdown
            impact_pos = item_content.find('- **Impact:**')
            action_pos = item_content.find('- **Action:**')

            if impact_pos > 0:
                description = item_content[:impact_pos].strip()
            elif action_pos > 0:
                description = item_content[:action_pos].strip()
            else:
                # Fallback: first line only
                description_match = re.match(r'([^\n]+?)(?:\n|$)', item_content)
                description = description_match.group(1).strip() if description_match else item_content

            # Extract action
            action_match = re.search(r'-\s+\*\*Action:\*\*\s+(.+?)(?:\n|$)', item_content)
            action = action_match.group(1).strip() if action_match else "Review and address this issue"

            # Create issue
            issue = Issue(
                severity=severity,
                category=category,
                description=description,
                action=action,
                source_file=source_file
            )

            issues.append(issue)

        return issues

    def infer_section_from_issue(self, issue: Issue, manuscript_content: Optional[str] = None) -> str:
        """Infer which section an issue belongs to.

        Strategy:
        1. Category mapping (Reproducibility -> methods)
        2. Word Count category -> parse description for section name
        3. Action text parsing (e.g., "Add ... in Introduction")
        4. Context search in manuscript
        5. Fallback to "manuscript_full"

        Args:
            issue: Issue object
            manuscript_content: Optional manuscript content for context search

        Returns:
            Section name (e.g., 'introduction', 'methods', 'manuscript_full')
        """
        # Strategy 1: Category mapping
        if issue.category in self.CATEGORY_TO_SECTION:
            mapped_section = self.CATEGORY_TO_SECTION[issue.category]
            if mapped_section:
                return mapped_section

        # Strategy 2: Word Count -> parse description
        if issue.category == "Word Count":
            section = self._extract_section_from_word_count(issue.description)
            if section:
                return section

        # Strategy 3: Parse action text for section mentions
        section = self._extract_section_from_action(issue.action)
        if section:
            return section

        # Strategy 4: Context search in manuscript
        if manuscript_content:
            section = self._search_context_for_section(issue.description, manuscript_content)
            if section:
                return section

        # Fallback: manuscript_full
        return "manuscript_full"

    def _extract_section_from_word_count(self, description: str) -> Optional[str]:
        """Extract section name from word count description.

        Examples:
        - "Abstract has 151 words" -> "abstract"
        - "Introduction exceeds limit" -> "introduction"

        Args:
            description: Issue description

        Returns:
            Section name or None
        """
        for section in self.SECTION_KEYWORDS.keys():
            if section.lower() in description.lower():
                return section
        return None

    def _extract_section_from_action(self, action: str) -> Optional[str]:
        """Extract section name from action text.

        Examples:
        - "Add ... in Introduction" -> "introduction"
        - "Revise Methods section" -> "methods"

        Args:
            action: Action text

        Returns:
            Section name or None
        """
        action_lower = action.lower()

        for section in self.SECTION_KEYWORDS.keys():
            # Check for "in Section" or "Section section" patterns
            if f" in {section}" in action_lower or f"{section} section" in action_lower:
                return section

        return None

    def _search_context_for_section(self, description: str, manuscript_content: str) -> Optional[str]:
        """Search manuscript for issue description and infer section from context.

        Args:
            description: Issue description (may contain snippet)
            manuscript_content: Full manuscript content

        Returns:
            Section name or None
        """
        # Extract a search snippet (first 30 chars or quoted text)
        quote_match = re.search(r'"([^"]{10,})"', description)
        if quote_match:
            snippet = quote_match.group(1)
        else:
            # Use first 30 chars of description
            snippet = description[:30]

        # Handle truncated snippets (ending with "...")
        if snippet.endswith("..."):
            # Search for beginning of snippet (first 40-60 chars before ...)
            snippet = snippet[:-3].strip()
            # Take first significant chunk (before any punctuation if possible)
            snippet_parts = re.split(r'[.!?,;]', snippet)
            if snippet_parts:
                snippet = snippet_parts[0].strip()
                # Ensure we have at least 20 chars for meaningful search
                if len(snippet) < 20 and len(snippet_parts) > 1:
                    snippet = snippet_parts[0] + snippet_parts[1]

        # Search for snippet in manuscript
        if len(snippet) >= 15 and snippet in manuscript_content:
            # Find position and look backwards for nearest section header
            pos = manuscript_content.find(snippet)
            before_content = manuscript_content[:pos]

            # Find last section header (## Section Name or # Section Name)
            header_match = re.findall(r'^#{1,2}\s+(.+?)$', before_content, re.MULTILINE)
            if header_match:
                last_header = header_match[-1].strip().lower()

                # Map header to standard section names
                for section, keywords in self.SECTION_KEYWORDS.items():
                    if any(kw in last_header for kw in keywords):
                        return section

        return None

    def infer_all_sections(self, issues: List[Issue]) -> List[Issue]:
        """Infer section for all issues using manuscript context.

        Args:
            issues: List of Issue objects

        Returns:
            Updated list with section field populated
        """
        # Load manuscript content (try both naming conventions)
        manuscript_file = self.manuscript_dir / "full_manuscript.md"
        if not manuscript_file.exists():
            manuscript_file = self.manuscript_dir / "manuscript_full.md"

        manuscript_content = None
        if manuscript_file.exists():
            with open(manuscript_file, 'r') as f:
                manuscript_content = f.read()
        else:
            self.logger.warning(f"Manuscript not found: {manuscript_file}")

        # Infer section for each issue
        for issue in issues:
            issue.section = self.infer_section_from_issue(issue, manuscript_content)

        return issues

    def count_issues(self, issues: List[Issue]) -> Dict[str, int]:
        """Count issues by severity.

        Args:
            issues: List of Issue objects

        Returns:
            Dict with 'major' and 'minor' counts
        """
        counts = {"major": 0, "minor": 0}

        for issue in issues:
            counts[issue.severity] = counts.get(issue.severity, 0) + 1

        return counts

    def group_by_section(self, issues: List[Issue]) -> Dict[str, List[Issue]]:
        """Group issues by section.

        Args:
            issues: List of Issue objects

        Returns:
            Dict mapping section names to issue lists
        """
        grouped = {}

        for issue in issues:
            section = issue.section or "manuscript_full"
            if section not in grouped:
                grouped[section] = []
            grouped[section].append(issue)

        return grouped


def main():
    """CLI for testing critique parser."""
    import argparse

    parser = argparse.ArgumentParser(description="Parse RRWrite critique reports")
    parser.add_argument("--manuscript-dir", required=True, help="Manuscript directory")
    parser.add_argument("--version", type=int, default=1, help="Critique version number")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format='%(levelname)s: %(message)s'
    )

    # Parse critiques
    critique_parser = CritiqueParser(args.manuscript_dir)
    issues = critique_parser.parse_critique_reports(version=args.version)

    # Infer sections
    issues = critique_parser.infer_all_sections(issues)

    # Print summary
    counts = critique_parser.count_issues(issues)
    print(f"\nFound {len(issues)} total issues:")
    print(f"  - Major: {counts['major']}")
    print(f"  - Minor: {counts['minor']}")

    # Group by section
    grouped = critique_parser.group_by_section(issues)
    print(f"\nIssues by section:")
    for section, section_issues in sorted(grouped.items()):
        print(f"  - {section}: {len(section_issues)} issues")

    # Print issues
    if args.verbose:
        print("\nAll issues:")
        for issue in issues:
            print(f"\n{issue}")
            print(f"  Section: {issue.section}")
            print(f"  Action: {issue.action}")


if __name__ == "__main__":
    main()
