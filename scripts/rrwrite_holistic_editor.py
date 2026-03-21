#!/usr/bin/env python3
"""
HolisticEditOrchestrator - Coordinates holistic application of edit recommendations.

This module provides the main orchestration for applying edit recommendations
cohesively across the manuscript with dependency analysis and conflict detection.
"""

import json
from pathlib import Path
from typing import List, Dict, Optional, Set, Tuple, Any
from collections import defaultdict
import sys

# Add scripts directory to path
SCRIPTS_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPTS_DIR))

from rrwrite_edit_recommendation import EditRecommendation


class DependencyGraph:
    """Manages dependency relationships between edits."""

    def __init__(self, recommendations: List[EditRecommendation]):
        """
        Initialize dependency graph.

        Args:
            recommendations: List of edit recommendations
        """
        self.recommendations = {rec.id: rec for rec in recommendations}
        self.graph = self._build_graph()

    def _build_graph(self) -> Dict[str, Set[str]]:
        """Build dependency graph."""
        graph = defaultdict(set)

        for rec_id, rec in self.recommendations.items():
            for dep_id in rec.dependencies:
                graph[rec_id].add(dep_id)

        return graph

    def topological_sort(self) -> List[str]:
        """
        Perform topological sort to determine application order.

        Returns:
            List of recommendation IDs in dependency order

        Raises:
            ValueError: If circular dependencies detected
        """
        # Kahn's algorithm
        in_degree = defaultdict(int)

        # Calculate in-degrees
        for rec_id in self.recommendations:
            if rec_id not in in_degree:
                in_degree[rec_id] = 0
            for dep_id in self.graph[rec_id]:
                in_degree[dep_id] += 1

        # Queue of nodes with no dependencies
        queue = [rec_id for rec_id in self.recommendations if in_degree[rec_id] == 0]
        result = []

        while queue:
            # Sort by priority score for deterministic ordering
            queue.sort(
                key=lambda x: self.recommendations[x].calculate_priority_score(),
                reverse=True
            )

            rec_id = queue.pop(0)
            result.append(rec_id)

            # Reduce in-degree for dependent nodes
            for other_id, deps in self.graph.items():
                if rec_id in deps:
                    in_degree[other_id] -= 1
                    if in_degree[other_id] == 0:
                        queue.append(other_id)

        if len(result) != len(self.recommendations):
            raise ValueError("Circular dependency detected")

        return result

    def detect_conflicts(self) -> List[Tuple[str, str, str]]:
        """
        Detect potential conflicts between edits.

        Returns:
            List of (edit_id1, edit_id2, reason) tuples
        """
        conflicts = []

        recs_list = list(self.recommendations.values())

        for i, rec1 in enumerate(recs_list):
            for rec2 in recs_list[i+1:]:
                conflict_reason = self._check_conflict(rec1, rec2)
                if conflict_reason:
                    conflicts.append((rec1.id, rec2.id, conflict_reason))

        return conflicts

    def _check_conflict(
        self,
        rec1: EditRecommendation,
        rec2: EditRecommendation
    ) -> Optional[str]:
        """Check if two recommendations conflict."""
        # Explicit conflicts
        if rec2.id in rec1.conflicts_with or rec1.id in rec2.conflicts_with:
            return "Explicitly marked as conflicting"

        # Same section, incompatible edit types
        if rec1.section == rec2.section:
            if rec1.edit_type == "remove_content" and rec2.edit_type == "add_content":
                return "Conflicting add/remove operations in same section"

            if rec1.edit_type == "restructure" and rec2.edit_type == "restructure":
                return "Multiple restructure operations in same section"

        return None


class ApplicationPlan:
    """Represents a plan for applying edits."""

    def __init__(
        self,
        sorted_edits: List[str],
        conflicts: List[Tuple[str, str, str]],
        recommendations: Dict[str, EditRecommendation]
    ):
        """
        Initialize application plan.

        Args:
            sorted_edits: Edit IDs in application order
            conflicts: List of detected conflicts
            recommendations: Recommendation dictionary
        """
        self.sorted_edits = sorted_edits
        self.conflicts = conflicts
        self.recommendations = recommendations

    def filter_by_priority(self, min_priority: str) -> 'ApplicationPlan':
        """Filter plan to only include edits at or above min priority."""
        priority_order = {"critical": 3, "important": 2, "optional": 1}
        min_level = priority_order.get(min_priority, 1)

        filtered = [
            edit_id for edit_id in self.sorted_edits
            if priority_order.get(self.recommendations[edit_id].priority, 1) >= min_level
        ]

        return ApplicationPlan(filtered, self.conflicts, self.recommendations)

    def filter_by_section(self, section: str) -> 'ApplicationPlan':
        """Filter plan to only include edits for a specific section."""
        filtered = [
            edit_id for edit_id in self.sorted_edits
            if self.recommendations[edit_id].is_applicable_to_section(section)
        ]

        return ApplicationPlan(filtered, self.conflicts, self.recommendations)

    def resolve_conflicts(self, resolution_strategy: str = "priority") -> 'ApplicationPlan':
        """
        Resolve conflicts by removing lower-priority edits.

        Args:
            resolution_strategy: "priority" or "manual"

        Returns:
            New plan with conflicts resolved
        """
        if resolution_strategy != "priority":
            # For manual, just return as-is
            return self

        conflicting_pairs = set()
        for id1, id2, _ in self.conflicts:
            conflicting_pairs.add((id1, id2))

        # Remove lower-priority edit from each conflict
        removed = set()
        for id1, id2 in conflicting_pairs:
            rec1 = self.recommendations[id1]
            rec2 = self.recommendations[id2]

            score1 = rec1.calculate_priority_score()
            score2 = rec2.calculate_priority_score()

            if score1 < score2:
                removed.add(id1)
                rec1.mark_skipped(f"Conflict with higher-priority {id2}")
            else:
                removed.add(id2)
                rec2.mark_skipped(f"Conflict with higher-priority {id1}")

        filtered = [edit_id for edit_id in self.sorted_edits if edit_id not in removed]

        return ApplicationPlan(filtered, [], self.recommendations)


class HolisticEditOrchestrator:
    """Main orchestrator for holistic edit application."""

    def __init__(self, manuscript_dir: Path):
        """
        Initialize orchestrator.

        Args:
            manuscript_dir: Path to manuscript directory
        """
        self.manuscript_dir = Path(manuscript_dir)
        self.recommendations = []
        self.plan = None

    def load_recommendations(self, recommendations_path: Path) -> int:
        """
        Load edit recommendations from JSON file.

        Args:
            recommendations_path: Path to edit_recommendations.json

        Returns:
            Number of recommendations loaded
        """
        with open(recommendations_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.recommendations = [
            EditRecommendation.from_dict(rec)
            for rec in data['recommendations']
        ]

        return len(self.recommendations)

    def plan_application(
        self,
        min_priority: Optional[str] = None,
        section: Optional[str] = None,
        resolve_conflicts: bool = True
    ) -> ApplicationPlan:
        """
        Create an application plan with dependency analysis.

        Args:
            min_priority: Minimum priority level to include
            section: Only include edits for this section
            resolve_conflicts: Automatically resolve conflicts

        Returns:
            ApplicationPlan object
        """
        # Build dependency graph
        dep_graph = DependencyGraph(self.recommendations)

        # Detect conflicts
        conflicts = dep_graph.detect_conflicts()

        # Topological sort
        try:
            sorted_edits = dep_graph.topological_sort()
        except ValueError as e:
            raise ValueError(f"Cannot create plan: {e}")

        # Create plan
        recs_dict = {rec.id: rec for rec in self.recommendations}
        plan = ApplicationPlan(sorted_edits, conflicts, recs_dict)

        # Apply filters
        if min_priority:
            plan = plan.filter_by_priority(min_priority)

        if section:
            plan = plan.filter_by_section(section)

        # Resolve conflicts
        if resolve_conflicts and conflicts:
            plan = plan.resolve_conflicts("priority")

        self.plan = plan
        return plan

    def preview_plan(self) -> Dict[str, Any]:
        """
        Generate a preview of the application plan.

        Returns:
            Dictionary with plan summary
        """
        if not self.plan:
            raise ValueError("No plan created. Call plan_application() first.")

        return {
            "total_edits": len(self.plan.sorted_edits),
            "conflicts_detected": len(self.plan.conflicts),
            "edit_order": self.plan.sorted_edits,
            "by_section": self._group_by_section(),
            "by_priority": self._group_by_priority(),
            "by_edit_type": self._group_by_edit_type()
        }

    def _group_by_section(self) -> Dict[str, int]:
        """Group plan edits by section."""
        groups = defaultdict(int)
        for edit_id in self.plan.sorted_edits:
            section = self.plan.recommendations[edit_id].section
            groups[section] += 1
        return dict(groups)

    def _group_by_priority(self) -> Dict[str, int]:
        """Group plan edits by priority."""
        groups = defaultdict(int)
        for edit_id in self.plan.sorted_edits:
            priority = self.plan.recommendations[edit_id].priority
            groups[priority] += 1
        return dict(groups)

    def _group_by_edit_type(self) -> Dict[str, int]:
        """Group plan edits by edit type."""
        groups = defaultdict(int)
        for edit_id in self.plan.sorted_edits:
            edit_type = self.plan.recommendations[edit_id].edit_type
            groups[edit_type] += 1
        return dict(groups)

    def get_recommendations_for_section(self, section: str) -> List[EditRecommendation]:
        """Get all recommendations applicable to a section."""
        if not self.plan:
            raise ValueError("No plan created")

        return [
            self.plan.recommendations[edit_id]
            for edit_id in self.plan.sorted_edits
            if self.plan.recommendations[edit_id].is_applicable_to_section(section)
        ]


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: rrwrite_holistic_editor.py <manuscript_dir> <recommendations.json>")
        sys.exit(1)

    manuscript_dir = Path(sys.argv[1])
    recommendations_path = Path(sys.argv[2])

    orchestrator = HolisticEditOrchestrator(manuscript_dir)
    count = orchestrator.load_recommendations(recommendations_path)
    print(f"Loaded {count} recommendations")

    plan = orchestrator.plan_application(resolve_conflicts=True)
    preview = orchestrator.preview_plan()

    print(f"\nApplication Plan:")
    print(f"  Total edits: {preview['total_edits']}")
    print(f"  Conflicts: {preview['conflicts_detected']}")
    print(f"\nBy priority:")
    for priority, count in preview['by_priority'].items():
        print(f"  {priority}: {count}")
