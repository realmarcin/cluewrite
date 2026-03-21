#!/usr/bin/env python3
"""
Edit Applicators - Specialized classes for applying different edit types.

This module contains applicators for:
- Section text edits (add/remove/revise)
- Cross-section content moves
- Figure and table updates
- Consistency fixes
"""

import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from difflib import SequenceMatcher
import sys

SCRIPTS_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPTS_DIR))

from rrwrite_edit_recommendation import EditRecommendation


class SectionEditApplicator:
    """Applies text edits to section files."""

    def __init__(self, manuscript_dir: Path):
        """
        Initialize applicator.

        Args:
            manuscript_dir: Path to manuscript directory
        """
        self.manuscript_dir = Path(manuscript_dir)
        self.sections_dir = manuscript_dir / "sections"

    def apply_edit(self, recommendation: EditRecommendation) -> Tuple[bool, str]:
        """
        Apply a single edit recommendation.

        Args:
            recommendation: Edit to apply

        Returns:
            Tuple of (success, message)
        """
        if recommendation.edit_type == "add_content":
            return self._add_content(recommendation)
        elif recommendation.edit_type == "remove_content":
            return self._remove_content(recommendation)
        elif recommendation.edit_type == "revise_content":
            return self._revise_content(recommendation)
        elif recommendation.edit_type == "citation_fix":
            return self._fix_citation(recommendation)
        else:
            return False, f"Unsupported edit type: {recommendation.edit_type}"

    def _add_content(self, rec: EditRecommendation) -> Tuple[bool, str]:
        """Add content to a section."""
        section_path = self.sections_dir / f"{rec.section}.md"

        if not section_path.exists():
            return False, f"Section file not found: {section_path}"

        content = section_path.read_text(encoding="utf-8")

        # Determine where to add content
        if rec.target_location:
            # Use specified location
            insert_point = self._find_insert_point(content, rec.target_location)
        else:
            # Default: add at end of section
            insert_point = len(content)

        # Generate content to add
        new_content = self._generate_content_to_add(rec)

        # Insert
        updated_content = (
            content[:insert_point] +
            "\n\n" + new_content + "\n" +
            content[insert_point:]
        )

        section_path.write_text(updated_content, encoding="utf-8")

        return True, f"Added content to {rec.section}"

    def _remove_content(self, rec: EditRecommendation) -> Tuple[bool, str]:
        """Remove content from a section."""
        section_path = self.sections_dir / f"{rec.section}.md"

        if not section_path.exists():
            return False, f"Section file not found: {section_path}"

        content = section_path.read_text(encoding="utf-8")

        # Find content to remove using fuzzy matching
        if rec.target_location:
            match_text = rec.target_location.get('context_before', '')
            if match_text:
                # Find matching paragraph
                paragraphs = content.split('\n\n')
                best_match_idx = -1
                best_score = 0.0

                for i, para in enumerate(paragraphs):
                    score = SequenceMatcher(None, match_text.lower(), para.lower()).ratio()
                    if score > best_score and score >= 0.7:
                        best_score = score
                        best_match_idx = i

                if best_match_idx >= 0:
                    # Remove paragraph
                    paragraphs.pop(best_match_idx)
                    updated_content = '\n\n'.join(paragraphs)
                    section_path.write_text(updated_content, encoding="utf-8")
                    return True, f"Removed content from {rec.section}"

        return False, "Could not locate content to remove"

    def _revise_content(self, rec: EditRecommendation) -> Tuple[bool, str]:
        """Revise existing content."""
        section_path = self.sections_dir / f"{rec.section}.md"

        if not section_path.exists():
            return False, f"Section file not found: {section_path}"

        content = section_path.read_text(encoding="utf-8")

        # If replacement text is provided, use it
        if rec.replacement_text and rec.target_location:
            match_text = rec.target_location.get('context_before', '')

            if match_text:
                # Find and replace
                paragraphs = content.split('\n\n')
                best_match_idx = -1
                best_score = 0.0

                for i, para in enumerate(paragraphs):
                    score = SequenceMatcher(None, match_text.lower(), para.lower()).ratio()
                    if score > best_score and score >= 0.7:
                        best_score = score
                        best_match_idx = i

                if best_match_idx >= 0:
                    paragraphs[best_match_idx] = rec.replacement_text
                    updated_content = '\n\n'.join(paragraphs)
                    section_path.write_text(updated_content, encoding="utf-8")
                    return True, f"Revised content in {rec.section}"

        # Fallback: add note about needed revision
        content += f"\n\n<!-- REVISION NEEDED: {rec.recommended_action} -->\n"
        section_path.write_text(content, encoding="utf-8")
        return True, f"Added revision note to {rec.section}"

    def _fix_citation(self, rec: EditRecommendation) -> Tuple[bool, str]:
        """Fix citation in section."""
        section_path = self.sections_dir / f"{rec.section}.md"

        if not section_path.exists():
            return False, f"Section file not found: {section_path}"

        content = section_path.read_text(encoding="utf-8")

        # If replacement citation provided, try to add it
        if rec.replacement_text and rec.evidence_citations:
            # Find location and add citation
            if rec.target_location:
                context = rec.target_location.get('context_before', '')
                if context:
                    # Simple string replacement
                    if context in content:
                        # Add citation after context
                        updated = content.replace(
                            context,
                            f"{context} {rec.replacement_text}"
                        )
                        section_path.write_text(updated, encoding="utf-8")
                        return True, f"Added citation to {rec.section}"

        return False, "Could not apply citation fix automatically"

    def _find_insert_point(self, content: str, location: Dict) -> int:
        """Find insertion point based on target location."""
        if 'paragraph_index' in location:
            paragraphs = content.split('\n\n')
            idx = location['paragraph_index']
            if idx < len(paragraphs):
                # Find character position of paragraph
                pos = 0
                for i in range(idx):
                    pos += len(paragraphs[i]) + 2  # +2 for \n\n
                return pos

        # Default: end of file
        return len(content)

    def _generate_content_to_add(self, rec: EditRecommendation) -> str:
        """Generate content to add based on recommendation."""
        if rec.replacement_text:
            return rec.replacement_text

        # Generate placeholder content
        content_lines = [
            f"<!-- Added to address: {rec.issue_description} -->",
            "",
            rec.recommended_action
        ]

        if rec.evidence_citations:
            citations = " ".join([f"[@{cite}]" for cite in rec.evidence_citations])
            content_lines.append(f"\n{citations}")

        return "\n".join(content_lines)


class CrossSectionApplicator:
    """Applies edits that move content between sections."""

    def __init__(self, manuscript_dir: Path):
        self.manuscript_dir = Path(manuscript_dir)
        self.sections_dir = manuscript_dir / "sections"

    def move_content(
        self,
        source_section: str,
        target_section: str,
        content_identifier: str
    ) -> Tuple[bool, str]:
        """Move content from one section to another."""
        source_path = self.sections_dir / f"{source_section}.md"
        target_path = self.sections_dir / f"{target_section}.md"

        if not source_path.exists() or not target_path.exists():
            return False, "Source or target section not found"

        source_content = source_path.read_text(encoding="utf-8")
        target_content = target_path.read_text(encoding="utf-8")

        # Find content in source
        paragraphs = source_content.split('\n\n')
        best_match_idx = -1
        best_score = 0.0
        moved_content = ""

        for i, para in enumerate(paragraphs):
            score = SequenceMatcher(None, content_identifier.lower(), para.lower()).ratio()
            if score > best_score and score >= 0.6:
                best_score = score
                best_match_idx = i
                moved_content = para

        if best_match_idx < 0:
            return False, "Could not locate content to move"

        # Remove from source
        paragraphs.pop(best_match_idx)
        updated_source = '\n\n'.join(paragraphs)

        # Add to target
        updated_target = target_content + "\n\n" + moved_content

        # Write updates
        source_path.write_text(updated_source, encoding="utf-8")
        target_path.write_text(updated_target, encoding="utf-8")

        return True, f"Moved content from {source_section} to {target_section}"


class FigureEditApplicator:
    """Applies edits to figure metadata and captions."""

    def __init__(self, manuscript_dir: Path):
        self.manuscript_dir = Path(manuscript_dir)
        self.manifest_path = manuscript_dir / "figures" / "figures_manifest.json"

    def update_caption(self, figure_id: str, new_caption: str) -> Tuple[bool, str]:
        """Update figure caption."""
        import json

        if not self.manifest_path.exists():
            return False, "Figure manifest not found"

        with open(self.manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)

        # Find figure
        for fig in manifest.get('figures', []):
            if fig.get('id') == figure_id or fig.get('filename') == figure_id:
                fig['caption'] = new_caption
                fig['modified'] = True

                # Write updated manifest
                with open(self.manifest_path, 'w', encoding='utf-8') as f:
                    json.dump(manifest, f, indent=2)

                return True, f"Updated caption for {figure_id}"

        return False, f"Figure {figure_id} not found in manifest"


class TableEditApplicator:
    """Applies edits to table metadata and titles."""

    def __init__(self, manuscript_dir: Path):
        self.manuscript_dir = Path(manuscript_dir)
        self.manifest_path = manuscript_dir / "tables" / "tables_manifest.json"

    def update_title(self, table_id: str, new_title: str) -> Tuple[bool, str]:
        """Update table title."""
        import json

        if not self.manifest_path.exists():
            return False, "Table manifest not found"

        with open(self.manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)

        # Find table
        for tbl in manifest.get('tables', []):
            if tbl.get('id') == table_id or tbl.get('filename') == table_id:
                tbl['title'] = new_title
                tbl['modified'] = True

                # Write updated manifest
                with open(self.manifest_path, 'w', encoding='utf-8') as f:
                    json.dump(manifest, f, indent=2)

                return True, f"Updated title for {table_id}"

        return False, f"Table {table_id} not found in manifest"


class ConsistencyApplicator:
    """Applies consistency fixes across manuscript."""

    def __init__(self, manuscript_dir: Path):
        self.manuscript_dir = Path(manuscript_dir)
        self.sections_dir = manuscript_dir / "sections"

    def standardize_terminology(
        self,
        old_term: str,
        new_term: str,
        case_sensitive: bool = True
    ) -> Tuple[bool, str]:
        """Standardize terminology across all sections."""
        changes = 0

        for section_file in self.sections_dir.glob("*.md"):
            content = section_file.read_text(encoding="utf-8")

            if case_sensitive:
                updated = content.replace(old_term, new_term)
            else:
                # Case-insensitive replacement
                pattern = re.compile(re.escape(old_term), re.IGNORECASE)
                updated = pattern.sub(new_term, content)

            if updated != content:
                section_file.write_text(updated, encoding="utf-8")
                changes += 1

        return True, f"Standardized '{old_term}' → '{new_term}' in {changes} sections"

    def renumber_figures(self) -> Tuple[bool, str]:
        """Renumber figures sequentially across sections."""
        # Load all sections in order
        section_order = ["abstract", "introduction", "methods", "results", "discussion", "availability"]
        figure_count = 0

        for section_name in section_order:
            section_path = self.sections_dir / f"{section_name}.md"
            if not section_path.exists():
                continue

            content = section_path.read_text(encoding="utf-8")

            # Find all figure references
            def replace_figure_number(match):
                nonlocal figure_count
                figure_count += 1
                return f"Figure {figure_count}"

            # Replace "Figure X" with sequential numbers
            updated = re.sub(r'Figure\s+\d+', replace_figure_number, content)

            if updated != content:
                section_path.write_text(updated, encoding="utf-8")

        return True, f"Renumbered {figure_count} figure references"

    def renumber_tables(self) -> Tuple[bool, str]:
        """Renumber tables sequentially across sections."""
        section_order = ["abstract", "introduction", "methods", "results", "discussion", "availability"]
        table_count = 0

        for section_name in section_order:
            section_path = self.sections_dir / f"{section_name}.md"
            if not section_path.exists():
                continue

            content = section_path.read_text(encoding="utf-8")

            def replace_table_number(match):
                nonlocal table_count
                table_count += 1
                return f"Table {table_count}"

            updated = re.sub(r'Table\s+\d+', replace_table_number, content)

            if updated != content:
                section_path.write_text(updated, encoding="utf-8")

        return True, f"Renumbered {table_count} table references"


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: rrwrite_edit_applicators.py <manuscript_dir>")
        sys.exit(1)

    manuscript_dir = Path(sys.argv[1])
    applicator = SectionEditApplicator(manuscript_dir)

    print(f"Section edit applicator initialized for {manuscript_dir}")
