#!/usr/bin/env python3
"""
EditRecommendationGenerator - Transforms critique issues into structured edits.

This module converts raw issues from critique reports into enriched,
actionable edit recommendations with supporting evidence and examples.
"""

import re
from pathlib import Path
from typing import List, Dict, Optional, Any
import sys

# Add scripts directory to path
SCRIPTS_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPTS_DIR))

from rrwrite_issue_resolver import Issue, IssueResolver
from rrwrite_edit_recommendation import (
    EditRecommendation,
    classify_edit_type,
    calculate_priority,
    infer_impact
)


class EditRecommendationGenerator:
    """Generates structured edit recommendations from critique issues."""

    def __init__(self, manuscript_dir: Path):
        """
        Initialize the generator.

        Args:
            manuscript_dir: Path to manuscript directory
        """
        self.manuscript_dir = Path(manuscript_dir)
        self.issue_resolver = IssueResolver(manuscript_dir)

        # Load context for enrichment
        self.literature_citations = self._load_literature_citations()
        self.sections_content = self._load_sections()

    def _load_literature_citations(self) -> Dict[str, Any]:
        """Load available citations from literature_citations.bib."""
        citations = {}
        bib_path = self.manuscript_dir / "literature_citations.bib"

        if not bib_path.exists():
            return citations

        content = bib_path.read_text(encoding="utf-8")

        # Parse BibTeX entries
        entries = re.findall(r'@\w+\{([^,]+),', content)
        for entry_key in entries:
            citations[entry_key] = True  # Simple presence check

        return citations

    def _load_sections(self) -> Dict[str, str]:
        """Load all section content."""
        sections = {}
        sections_dir = self.manuscript_dir / "sections"

        if not sections_dir.exists():
            return sections

        for section_file in sections_dir.glob("*.md"):
            section_name = section_file.stem
            sections[section_name] = section_file.read_text(encoding="utf-8")

        return sections

    def generate_from_critique(
        self,
        critique_version: int,
        include_format: bool = True
    ) -> List[EditRecommendation]:
        """
        Generate edit recommendations from critique reports.

        Args:
            critique_version: Critique version number
            include_format: Include format critique issues

        Returns:
            List of EditRecommendation objects
        """
        recommendations = []

        # Load content critique
        content_critique = self.manuscript_dir / f"critique_content_v{critique_version}.md"
        if content_critique.exists():
            issues = self.issue_resolver.load_critique_issues(content_critique)
            for i, issue in enumerate(issues, 1):
                rec = self._issue_to_recommendation(
                    issue,
                    f"edit_{i:03d}",
                    "critique_content"
                )
                recommendations.append(rec)

        # Load format critique
        if include_format:
            format_critique = self.manuscript_dir / f"critique_format_v{critique_version}.md"
            if format_critique.exists():
                issues = self.issue_resolver.load_critique_issues(format_critique)
                offset = len(recommendations)
                for i, issue in enumerate(issues, offset + 1):
                    rec = self._issue_to_recommendation(
                        issue,
                        f"edit_{i:03d}",
                        "critique_format"
                    )
                    recommendations.append(rec)

        # Enrich recommendations
        recommendations = self._enrich_recommendations(recommendations)

        return recommendations

    def _issue_to_recommendation(
        self,
        issue: Issue,
        edit_id: str,
        source: str
    ) -> EditRecommendation:
        """
        Convert an Issue to EditRecommendation.

        Args:
            issue: Issue object
            edit_id: Unique ID for this edit
            source: Source of the issue (critique_content, critique_format)

        Returns:
            EditRecommendation object
        """
        # Extract action if present in description
        action = self._extract_recommended_action(issue.description)

        # Classify edit type
        edit_type = classify_edit_type(
            issue.description,
            action,
            issue.category
        )

        # Calculate priority
        priority = calculate_priority(
            issue.severity,
            issue.category,
            issue.section or "global",
            issue.description
        )

        # Determine section(s)
        section = issue.section or "global"
        target_sections = []
        if section in ["global", "multiple"]:
            target_sections = self._infer_target_sections(issue.description)

        # Infer impact
        impact = infer_impact(edit_type, issue.category, section)

        return EditRecommendation(
            id=edit_id,
            source=source,
            source_issue_id=issue.id,
            category=issue.category,
            priority=priority,
            edit_type=edit_type,
            section=section,
            target_sections=target_sections,
            issue_description=issue.description,
            recommended_action=action,
            impact=impact
        )

    def _extract_recommended_action(self, description: str) -> str:
        """Extract recommended action from issue description."""
        # Look for action keywords
        action_patterns = [
            r'should\s+(.+)',
            r'must\s+(.+)',
            r'need to\s+(.+)',
            r'recommend\s+(.+)',
            r'consider\s+(.+)',
        ]

        for pattern in action_patterns:
            match = re.search(pattern, description, re.IGNORECASE)
            if match:
                action = match.group(1).strip()
                # Capitalize first letter
                return action[0].upper() + action[1:] if action else description

        # Default: use description as action
        return description

    def _infer_target_sections(self, description: str) -> List[str]:
        """Infer which sections are affected by this issue."""
        desc_lower = description.lower()
        sections = []

        section_keywords = {
            "abstract": ["abstract"],
            "introduction": ["introduction", "background"],
            "methods": ["methods", "methodology", "materials"],
            "results": ["results", "findings"],
            "discussion": ["discussion", "interpretation"],
            "availability": ["availability", "data access"]
        }

        for section, keywords in section_keywords.items():
            if any(kw in desc_lower for kw in keywords):
                sections.append(section)

        return sections

    def _enrich_recommendations(
        self,
        recommendations: List[EditRecommendation]
    ) -> List[EditRecommendation]:
        """
        Enrich recommendations with supporting evidence and examples.

        Args:
            recommendations: List of base recommendations

        Returns:
            Enriched recommendations
        """
        for rec in recommendations:
            # Find supporting citations
            rec.evidence_citations = self._find_supporting_citations(rec)

            # Find reference examples from literature
            rec.reference_examples = self._find_reference_examples(rec)

            # Generate replacement text for simple cases
            if rec.edit_type == "citation_fix":
                rec.replacement_text = self._suggest_citation_fix(rec)

            # Identify dependencies
            rec.dependencies = self._identify_dependencies(rec, recommendations)

        return recommendations

    def _find_supporting_citations(self, rec: EditRecommendation) -> List[str]:
        """Find citations that support this recommendation."""
        citations = []

        # Category-specific citation keywords
        keywords_map = {
            "evidence_support": ["evidence", "validation", "benchmark"],
            "reproducibility": ["reproducibility", "replication", "workflow"],
            "citation_quality": ["reference", "literature", "prior work"],
            "content_accuracy": ["accuracy", "precision", "validation"]
        }

        keywords = keywords_map.get(rec.category, [])

        # Search for relevant citations
        for cite_key in self.literature_citations.keys():
            # Simple keyword matching (could be enhanced with embeddings)
            cite_lower = cite_key.lower()
            if any(kw in cite_lower for kw in keywords):
                citations.append(cite_key)

        return citations[:3]  # Limit to top 3

    def _find_reference_examples(self, rec: EditRecommendation) -> List[Dict[str, str]]:
        """Find example text from literature showing best practice."""
        examples = []

        # For certain edit types, extract examples from sections
        if rec.edit_type == "add_content" and rec.section in self.sections_content:
            section_content = self.sections_content[rec.section]

            # Find well-cited paragraphs as examples
            paragraphs = section_content.split('\n\n')
            for para in paragraphs:
                # Count citations in paragraph
                citations = re.findall(r'\[@([^\]]+)\]', para)
                if len(citations) >= 2:
                    # Well-supported paragraph
                    examples.append({
                        "citation_key": "manuscript_example",
                        "text": para[:200] + "..." if len(para) > 200 else para
                    })
                    break

        return examples[:2]  # Limit to 2 examples

    def _suggest_citation_fix(self, rec: EditRecommendation) -> Optional[str]:
        """Suggest replacement text for citation fixes."""
        if "missing citation" in rec.issue_description.lower():
            # Suggest adding a citation
            if rec.evidence_citations:
                return f"[@{rec.evidence_citations[0]}]"

        return None

    def _identify_dependencies(
        self,
        rec: EditRecommendation,
        all_recs: List[EditRecommendation]
    ) -> List[str]:
        """Identify which other edits this recommendation depends on."""
        dependencies = []

        # Restructure before content changes
        if rec.edit_type in ["add_content", "revise_content"]:
            for other in all_recs:
                if (other.section == rec.section and
                    other.edit_type == "restructure" and
                    other.id != rec.id):
                    dependencies.append(other.id)

        # Citation fixes before content that references them
        if rec.edit_type == "add_content":
            for other in all_recs:
                if (other.edit_type == "citation_fix" and
                    other.section == rec.section and
                    other.id != rec.id):
                    dependencies.append(other.id)

        return dependencies

    def generate_summary(
        self,
        recommendations: List[EditRecommendation]
    ) -> Dict[str, Any]:
        """
        Generate summary statistics for recommendations.

        Args:
            recommendations: List of recommendations

        Returns:
            Summary dictionary
        """
        summary = {
            "total": len(recommendations),
            "by_priority": {"critical": 0, "important": 0, "optional": 0},
            "by_edit_type": {},
            "by_section": {},
            "by_status": {"pending": 0, "applied": 0, "skipped": 0, "failed": 0, "conflict": 0}
        }

        for rec in recommendations:
            # By priority
            summary["by_priority"][rec.priority] = summary["by_priority"].get(rec.priority, 0) + 1

            # By edit type
            summary["by_edit_type"][rec.edit_type] = summary["by_edit_type"].get(rec.edit_type, 0) + 1

            # By section
            summary["by_section"][rec.section] = summary["by_section"].get(rec.section, 0) + 1

            # By status
            summary["by_status"][rec.status] = summary["by_status"].get(rec.status, 0) + 1

        return summary


if __name__ == "__main__":
    import json

    if len(sys.argv) < 3:
        print("Usage: rrwrite_edit_recommendation_generator.py <manuscript_dir> <critique_version>")
        sys.exit(1)

    manuscript_dir = Path(sys.argv[1])
    critique_version = int(sys.argv[2])

    generator = EditRecommendationGenerator(manuscript_dir)
    recommendations = generator.generate_from_critique(critique_version)

    print(f"Generated {len(recommendations)} recommendations")
    print(json.dumps([r.to_dict() for r in recommendations[:3]], indent=2))
