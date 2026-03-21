#!/usr/bin/env python3
"""
DiffReportGenerator - Compares manuscript versions and generates structured diff reports.

This module provides functionality to compare two versions of a manuscript
(either from git history or different directories) and generate detailed
comparison reports showing changes in sections, citations, and issues.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from difflib import SequenceMatcher
import subprocess


class DiffReportGenerator:
    """Generates structured comparison reports between manuscript versions."""

    def __init__(self, manuscript_dir: Path):
        """
        Initialize the diff generator.

        Args:
            manuscript_dir: Path to manuscript directory
        """
        self.manuscript_dir = Path(manuscript_dir)
        self.sections = [
            "abstract",
            "introduction",
            "methods",
            "results",
            "discussion",
            "availability"
        ]

    def load_manuscript_version(
        self,
        version: int,
        git_commit: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Load a specific manuscript version.

        Args:
            version: Version number
            git_commit: Optional git commit hash (loads from git history)

        Returns:
            Dictionary with section content, citations, and metadata
        """
        if git_commit:
            return self._load_from_git(git_commit)
        else:
            return self._load_from_filesystem(version)

    def _load_from_filesystem(self, version: int) -> Dict[str, Any]:
        """Load manuscript version from filesystem."""
        data = {
            "version": version,
            "sections": {},
            "citations": set(),
            "metadata": {}
        }

        # Load sections
        sections_dir = self.manuscript_dir / "sections"
        if not sections_dir.exists():
            return data

        for section_name in self.sections:
            section_path = sections_dir / f"{section_name}.md"
            if section_path.exists():
                content = section_path.read_text(encoding="utf-8")
                data["sections"][section_name] = content

                # Extract citations
                citations = self._extract_citations(content)
                data["citations"].update(citations)

        # Load metadata
        manifest_path = self.manuscript_dir / "assembly_manifest.json"
        if manifest_path.exists():
            with open(manifest_path, "r", encoding="utf-8") as f:
                data["metadata"] = json.load(f)

        return data

    def _load_from_git(self, commit: str) -> Dict[str, Any]:
        """Load manuscript version from git history."""
        data = {
            "version": None,
            "sections": {},
            "citations": set(),
            "metadata": {"git_commit": commit}
        }

        git_dir = self.manuscript_dir / ".git"
        if not git_dir.exists():
            return data

        # Load each section from git
        for section_name in self.sections:
            section_path = f"sections/{section_name}.md"
            try:
                result = subprocess.run(
                    ["git", f"--git-dir={git_dir}", "show", f"{commit}:{section_path}"],
                    capture_output=True,
                    text=True,
                    check=True
                )
                content = result.stdout
                data["sections"][section_name] = content

                # Extract citations
                citations = self._extract_citations(content)
                data["citations"].update(citations)
            except subprocess.CalledProcessError:
                # Section doesn't exist in this commit
                continue

        return data

    def _extract_citations(self, text: str) -> set:
        """Extract citation keys from text."""
        # Match [@key1; @key2] or [@key1]
        citations = set()
        pattern = r'\[@([a-zA-Z0-9_]+(?:;\s*@[a-zA-Z0-9_]+)*)\]'
        matches = re.findall(pattern, text)

        for match in matches:
            # Split multiple citations
            keys = [k.strip().lstrip('@') for k in match.split(';')]
            citations.update(keys)

        return citations

    def compare_sections(
        self,
        old_version: Dict[str, Any],
        new_version: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Compare sections between two versions.

        Args:
            old_version: Old version data
            new_version: New version data

        Returns:
            List of section comparison results
        """
        section_results = []

        all_sections = set(old_version["sections"].keys()) | set(new_version["sections"].keys())

        for section_name in self.sections:
            if section_name not in all_sections:
                continue

            old_content = old_version["sections"].get(section_name, "")
            new_content = new_version["sections"].get(section_name, "")

            # Determine status
            if not old_content and new_content:
                status = "added"
            elif old_content and not new_content:
                status = "removed"
            elif old_content == new_content:
                status = "unchanged"
            else:
                status = "modified"

            # Compute changes
            changes = self._compute_section_changes(old_content, new_content)

            # Generate notable changes
            notable_changes = self._generate_notable_changes(
                section_name, old_content, new_content, changes
            )

            section_results.append({
                "section_name": section_name,
                "status": status,
                "changes": changes,
                "notable_changes": notable_changes
            })

        return section_results

    def _compute_section_changes(
        self,
        old_content: str,
        new_content: str
    ) -> Dict[str, Any]:
        """Compute detailed changes for a section."""
        old_lines = old_content.split('\n') if old_content else []
        new_lines = new_content.split('\n') if new_content else []

        # Use SequenceMatcher for diff
        sm = SequenceMatcher(None, old_lines, new_lines)

        additions = 0
        deletions = 0
        modifications = 0

        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag == 'insert':
                additions += (j2 - j1)
            elif tag == 'delete':
                deletions += (i2 - i1)
            elif tag == 'replace':
                modifications += max(i2 - i1, j2 - j1)

        # Word counts
        old_words = len(old_content.split()) if old_content else 0
        new_words = len(new_content.split()) if new_content else 0

        # Similarity score
        similarity = sm.ratio()

        return {
            "additions": additions,
            "deletions": deletions,
            "modifications": modifications,
            "word_count_old": old_words,
            "word_count_new": new_words,
            "word_count_delta": new_words - old_words,
            "similarity_score": round(similarity, 3)
        }

    def _generate_notable_changes(
        self,
        section_name: str,
        old_content: str,
        new_content: str,
        changes: Dict[str, Any]
    ) -> List[str]:
        """Generate human-readable descriptions of notable changes."""
        notable = []

        if changes["word_count_delta"] > 50:
            notable.append(f"Expanded by {changes['word_count_delta']} words")
        elif changes["word_count_delta"] < -50:
            notable.append(f"Reduced by {abs(changes['word_count_delta'])} words")

        if changes["additions"] > 5:
            notable.append(f"{changes['additions']} lines added")

        if changes["deletions"] > 5:
            notable.append(f"{changes['deletions']} lines deleted")

        # Check for new citations
        old_citations = self._extract_citations(old_content)
        new_citations = self._extract_citations(new_content)
        added_citations = new_citations - old_citations
        if added_citations:
            notable.append(f"{len(added_citations)} citations added")

        # Check for structural changes (headings)
        old_headings = re.findall(r'^#+\s+(.+)$', old_content, re.MULTILINE)
        new_headings = re.findall(r'^#+\s+(.+)$', new_content, re.MULTILINE)
        if old_headings != new_headings:
            notable.append("Structure reorganized")

        return notable

    def compare_citations(
        self,
        old_version: Dict[str, Any],
        new_version: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compare citations between versions.

        Args:
            old_version: Old version data
            new_version: New version data

        Returns:
            Citation comparison results
        """
        old_cites = old_version["citations"]
        new_cites = new_version["citations"]

        added = new_cites - old_cites
        removed = old_cites - new_cites
        unchanged = old_cites & new_cites

        # Find sections for added citations
        added_with_sections = []
        for cite_key in added:
            for section_name, content in new_version["sections"].items():
                if f"@{cite_key}" in content:
                    # Extract context
                    context = self._extract_citation_context(content, cite_key)
                    added_with_sections.append({
                        "citation_key": cite_key,
                        "section": section_name,
                        "context": context
                    })
                    break

        # Find sections for removed citations
        removed_with_sections = []
        for cite_key in removed:
            for section_name, content in old_version["sections"].items():
                if f"@{cite_key}" in content:
                    removed_with_sections.append({
                        "citation_key": cite_key,
                        "section": section_name
                    })
                    break

        return {
            "added": added_with_sections,
            "removed": removed_with_sections,
            "unchanged": sorted(list(unchanged))
        }

    def _extract_citation_context(self, text: str, cite_key: str, window: int = 50) -> str:
        """Extract surrounding text for a citation."""
        pattern = rf'[@{cite_key}\b]'
        match = re.search(pattern, text)
        if match:
            start = max(0, match.start() - window)
            end = min(len(text), match.end() + window)
            context = text[start:end]
            # Clean up
            context = context.replace('\n', ' ').strip()
            if start > 0:
                context = '...' + context
            if end < len(text):
                context = context + '...'
            return context
        return ""

    def generate_diff_report(
        self,
        version_old: int,
        version_new: int,
        comparison_type: str = "revision",
        git_commit_old: Optional[str] = None,
        git_commit_new: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate complete diff report.

        Args:
            version_old: Old version number
            version_new: New version number
            comparison_type: Type of comparison (revision/version/manual)
            git_commit_old: Optional git commit for old version
            git_commit_new: Optional git commit for new version

        Returns:
            Complete diff report conforming to diff_report_schema.json
        """
        # Load versions
        old = self.load_manuscript_version(version_old, git_commit_old)
        new = self.load_manuscript_version(version_new, git_commit_new)

        # Compare sections
        sections = self.compare_sections(old, new)

        # Compare citations
        citations = self.compare_citations(old, new)

        # Compute summary
        summary = self._compute_summary(sections, citations)

        # Build report
        report = {
            "metadata": {
                "version_old": version_old,
                "version_new": version_new,
                "comparison_type": comparison_type,
                "timestamp": datetime.now().isoformat(),
                "manuscript_dir": str(self.manuscript_dir)
            },
            "summary": summary,
            "sections": sections,
            "citations": citations,
            "issues": {
                "resolved": [],
                "persisting": [],
                "new": []
            },
            "figures_tables": {
                "figures_added": [],
                "figures_removed": [],
                "figures_modified": [],
                "tables_added": [],
                "tables_removed": [],
                "tables_modified": []
            },
            "metrics": {}
        }

        if git_commit_old:
            report["metadata"]["git_commit_old"] = git_commit_old
        if git_commit_new:
            report["metadata"]["git_commit_new"] = git_commit_new

        return report

    def _compute_summary(
        self,
        sections: List[Dict[str, Any]],
        citations: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Compute summary statistics."""
        total_changes = sum(
            s["changes"]["additions"] +
            s["changes"]["deletions"] +
            s["changes"]["modifications"]
            for s in sections
        )

        sections_modified = sum(1 for s in sections if s["status"] == "modified")

        word_count_delta = sum(s["changes"]["word_count_delta"] for s in sections)

        return {
            "total_changes": total_changes,
            "sections_modified": sections_modified,
            "citations_added": len(citations["added"]),
            "citations_removed": len(citations["removed"]),
            "word_count_delta": word_count_delta,
            "issues_resolved": 0,  # Populated by IssueResolver
            "issues_remaining": 0   # Populated by IssueResolver
        }


def validate_diff_report(report: Dict[str, Any], schema_path: Path) -> Tuple[bool, List[str]]:
    """
    Validate diff report against schema.

    Args:
        report: Diff report dictionary
        schema_path: Path to diff_report_schema.json

    Returns:
        Tuple of (is_valid, error_messages)
    """
    try:
        import jsonschema
    except ImportError:
        return True, ["jsonschema not installed, skipping validation"]

    with open(schema_path, 'r', encoding='utf-8') as f:
        schema = json.load(f)

    try:
        jsonschema.validate(report, schema)
        return True, []
    except jsonschema.ValidationError as e:
        return False, [str(e)]


if __name__ == "__main__":
    # Simple test
    import sys

    if len(sys.argv) < 2:
        print("Usage: rrwrite_diff_generator.py <manuscript_dir>")
        sys.exit(1)

    manuscript_dir = Path(sys.argv[1])
    generator = DiffReportGenerator(manuscript_dir)

    # Generate report for v1 → v2
    report = generator.generate_diff_report(1, 2, "revision")

    print(json.dumps(report, indent=2))
