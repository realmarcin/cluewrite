#!/usr/bin/env python3
"""
EditRecommendation - Structured edit recommendation with priority and metadata.

This module defines the EditRecommendation dataclass used throughout the
edit recommendation and holistic editing systems.
"""

from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any
from datetime import datetime


@dataclass
class EditRecommendation:
    """Represents a structured edit recommendation."""

    id: str
    source: str  # critique_content, critique_format, word_comments, etc.
    category: str  # content_accuracy, evidence_support, citation_quality, etc.
    priority: str  # critical, important, optional
    edit_type: str  # add_content, remove_content, revise_content, etc.
    section: str  # abstract, introduction, methods, etc.
    issue_description: str
    recommended_action: str

    # Optional fields
    source_issue_id: Optional[str] = None
    target_sections: List[str] = field(default_factory=list)
    target_location: Optional[Dict[str, Any]] = None
    replacement_text: Optional[str] = None
    evidence_citations: List[str] = field(default_factory=list)
    reference_examples: List[Dict[str, str]] = field(default_factory=list)
    impact: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    conflicts_with: List[str] = field(default_factory=list)
    status: str = "pending"
    applied_at: Optional[str] = None
    failure_reason: Optional[str] = None
    notes: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EditRecommendation':
        """Create from dictionary."""
        return cls(**data)

    def calculate_priority_score(self) -> float:
        """
        Calculate numeric priority score for sorting.

        Returns:
            Float score (higher = more urgent)
        """
        # Base priority
        priority_scores = {
            "critical": 100,
            "important": 50,
            "optional": 10
        }
        score = priority_scores.get(self.priority, 10)

        # Category modifiers
        category_modifiers = {
            "evidence_support": 1.5,
            "reproducibility": 1.5,
            "content_accuracy": 1.3,
            "citation_quality": 1.2,
            "journal_compliance": 1.4,
            "structure": 1.1,
            "clarity": 1.0,
            "formatting": 0.8,
            "word_count": 0.9
        }
        modifier = category_modifiers.get(self.category, 1.0)
        score *= modifier

        # Edit type modifiers (some edits are riskier/more impactful)
        edit_modifiers = {
            "add_content": 1.2,
            "restructure": 1.3,
            "move_content": 1.1,
            "revise_content": 1.0,
            "citation_fix": 0.9,
            "remove_content": 0.8,
            "formatting": 0.7
        }
        edit_mod = edit_modifiers.get(self.edit_type, 1.0)
        score *= edit_mod

        return score

    def is_applicable_to_section(self, section_name: str) -> bool:
        """Check if this edit applies to a given section."""
        if self.section == section_name:
            return True
        if self.section in ["multiple", "global"]:
            if section_name in self.target_sections:
                return True
        return False

    def mark_applied(self) -> None:
        """Mark this edit as successfully applied."""
        self.status = "applied"
        self.applied_at = datetime.now().isoformat()

    def mark_failed(self, reason: str) -> None:
        """Mark this edit as failed with reason."""
        self.status = "failed"
        self.failure_reason = reason

    def mark_skipped(self, reason: str) -> None:
        """Mark this edit as skipped with reason."""
        self.status = "skipped"
        self.notes = reason if not self.notes else f"{self.notes}; {reason}"

    def has_dependency_on(self, other_id: str) -> bool:
        """Check if this edit depends on another."""
        return other_id in self.dependencies

    def conflicts_with_edit(self, other_id: str) -> bool:
        """Check if this edit conflicts with another."""
        return other_id in self.conflicts_with


def classify_edit_type(
    issue_description: str,
    recommended_action: str,
    category: str
) -> str:
    """
    Classify edit type based on issue and action descriptions.

    Args:
        issue_description: Description of the issue
        recommended_action: Recommended action to take
        category: Issue category

    Returns:
        Edit type (add_content, remove_content, etc.)
    """
    desc_lower = issue_description.lower()
    action_lower = recommended_action.lower()
    combined = f"{desc_lower} {action_lower}"

    # Add content
    if any(kw in combined for kw in ["missing", "add", "include", "provide", "specify"]):
        return "add_content"

    # Remove content
    if any(kw in combined for kw in ["remove", "delete", "redundant", "unnecessary", "verbose"]):
        return "remove_content"

    # Restructure
    if any(kw in combined for kw in ["reorganize", "restructure", "reorder", "move to"]):
        if "move" in action_lower:
            return "move_content"
        return "restructure"

    # Citation fix
    if any(kw in combined for kw in ["citation", "reference", "cite"]):
        return "citation_fix"

    # Figure/table updates
    if "figure" in combined:
        return "figure_update"
    if "table" in combined:
        return "table_update"

    # Formatting
    if category == "formatting" or any(kw in combined for kw in ["format", "style", "heading"]):
        return "formatting"

    # Default to revise_content
    return "revise_content"


def calculate_priority(
    severity: str,
    category: str,
    section: str,
    issue_description: str
) -> str:
    """
    Calculate priority level based on issue characteristics.

    Args:
        severity: Issue severity (MAJOR, MINOR, WARNING)
        category: Issue category
        section: Affected section
        issue_description: Description of the issue

    Returns:
        Priority level (critical, important, optional)
    """
    desc_lower = issue_description.lower()

    # Critical: blocks publication
    critical_keywords = [
        "reproducibility",
        "missing data",
        "incorrect",
        "fabricated",
        "plagiarism",
        "ethics",
        "falsified"
    ]
    if any(kw in desc_lower for kw in critical_keywords):
        return "critical"

    # Critical categories regardless of severity
    if category in ["evidence_support", "reproducibility", "content_accuracy"]:
        if severity == "MAJOR":
            return "critical"

    # Important: MAJOR issues or critical categories
    if severity == "MAJOR":
        return "important"

    # Important categories even if MINOR
    if category in ["journal_compliance", "structure", "citation_quality"]:
        return "important"

    # Abstract is high priority
    if section == "abstract" and severity in ["MAJOR", "MINOR"]:
        return "important"

    # Everything else is optional
    return "optional"


def infer_impact(edit_type: str, category: str, section: str) -> str:
    """
    Infer expected impact of applying this edit.

    Args:
        edit_type: Type of edit
        category: Issue category
        section: Target section

    Returns:
        Impact description
    """
    impacts = {
        "add_content": f"Adds missing information to {section}, improving completeness",
        "remove_content": f"Reduces verbosity in {section}, improving clarity",
        "revise_content": f"Improves accuracy and clarity in {section}",
        "restructure": f"Reorganizes {section} for better flow",
        "move_content": "Relocates content to more appropriate section",
        "citation_fix": "Strengthens citation support and credibility",
        "figure_update": "Improves figure presentation and clarity",
        "table_update": "Improves table presentation and clarity",
        "formatting": "Ensures compliance with journal formatting requirements"
    }

    base_impact = impacts.get(edit_type, "Improves manuscript quality")

    # Add category-specific notes
    if category == "evidence_support":
        base_impact += "; strengthens evidence base"
    elif category == "reproducibility":
        base_impact += "; enhances reproducibility"
    elif category == "journal_compliance":
        base_impact += "; ensures journal compliance"

    return base_impact


if __name__ == "__main__":
    # Test
    edit = EditRecommendation(
        id="edit_001",
        source="critique_content",
        category="evidence_support",
        priority="critical",
        edit_type="add_content",
        section="methods",
        issue_description="Missing parameter descriptions",
        recommended_action="Add detailed parameter explanations"
    )

    print(f"Edit ID: {edit.id}")
    print(f"Priority Score: {edit.calculate_priority_score()}")
    print(f"Dict: {edit.to_dict()}")
