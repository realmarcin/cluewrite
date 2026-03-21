#!/usr/bin/env python3
"""
ExternalFeedbackParser - Parse feedback from Word comments, PDFs, and emails.

This module extracts structured edit recommendations from various external
feedback sources like reviewer comments, collaborator feedback, etc.
"""

import re
from pathlib import Path
from typing import List, Dict, Optional, Any
import sys

# Add scripts directory to path
SCRIPTS_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPTS_DIR))

from rrwrite_edit_recommendation import (
    EditRecommendation,
    classify_edit_type,
    calculate_priority
)


class ExternalFeedbackParser:
    """Parses external feedback into EditRecommendations."""

    def __init__(self, manuscript_dir: Path):
        """
        Initialize parser.

        Args:
            manuscript_dir: Path to manuscript directory
        """
        self.manuscript_dir = Path(manuscript_dir)

    def parse_word_comments(self, docx_path: Path) -> List[EditRecommendation]:
        """
        Parse comments from a Word .docx file.

        Args:
            docx_path: Path to .docx file with comments

        Returns:
            List of EditRecommendation objects
        """
        try:
            from docx import Document
        except ImportError:
            print("Warning: python-docx not installed. Install with: pip install python-docx")
            return []

        doc = Document(docx_path)
        recommendations = []

        # Extract comments
        comments = self._extract_docx_comments(doc)

        for i, comment_data in enumerate(comments, 1):
            rec = self._comment_to_recommendation(
                comment_data,
                f"edit_{i:03d}",
                "word_comments"
            )
            recommendations.append(rec)

        return recommendations

    def _extract_docx_comments(self, doc) -> List[Dict[str, Any]]:
        """Extract all comments from a Word document."""
        from docx.oxml.text.paragraph import CT_P
        from docx.oxml.shape import CT_Shape

        comments = []

        # Access comment part (if it exists)
        try:
            comments_part = doc.part.package.part_related_by("http://schemas.openxmlformats.org/officeDocument/2006/relationships/comments")
            comment_elements = comments_part.element.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}comment')

            for comment_el in comment_elements:
                comment_id = comment_el.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}id')
                author = comment_el.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}author', 'Unknown')

                # Extract comment text
                comment_text = ""
                for para in comment_el.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'):
                    comment_text += para.text

                # Find referenced text (context)
                context = self._find_comment_context(doc, comment_id)

                comments.append({
                    "id": comment_id,
                    "author": author,
                    "text": comment_text,
                    "context": context
                })

        except Exception as e:
            print(f"Warning: Could not extract comments: {e}")

        return comments

    def _find_comment_context(self, doc, comment_id: str) -> str:
        """Find the text that a comment is attached to."""
        # This is complex in Word's XML structure
        # For now, return empty - could be enhanced
        return ""

    def _comment_to_recommendation(
        self,
        comment: Dict[str, Any],
        edit_id: str,
        source: str
    ) -> EditRecommendation:
        """Convert a Word comment to EditRecommendation."""
        text = comment['text']

        # Infer section from context or comment
        section = self._infer_section_from_text(text + " " + comment.get('context', ''))

        # Infer category
        category = self._infer_category_from_text(text)

        # Infer severity
        severity = self._infer_severity_from_text(text)

        # Classify edit type
        edit_type = classify_edit_type(text, text, category)

        # Calculate priority
        priority = calculate_priority(severity, category, section, text)

        # Extract action
        action = self._extract_action_from_comment(text)

        return EditRecommendation(
            id=edit_id,
            source=source,
            category=category,
            priority=priority,
            edit_type=edit_type,
            section=section,
            issue_description=text,
            recommended_action=action,
            notes=f"Author: {comment.get('author', 'Unknown')}"
        )

    def parse_email_feedback(self, email_path: Path) -> List[EditRecommendation]:
        """
        Parse feedback from an email saved as .txt.

        Args:
            email_path: Path to email text file

        Returns:
            List of EditRecommendation objects
        """
        content = email_path.read_text(encoding="utf-8")

        # Split into paragraphs
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]

        recommendations = []

        for i, para in enumerate(paragraphs, 1):
            # Skip very short paragraphs (likely not feedback)
            if len(para) < 20:
                continue

            # Check if this looks like actionable feedback
            if not self._is_actionable_feedback(para):
                continue

            rec = self._text_to_recommendation(
                para,
                f"edit_{i:03d}",
                "email_feedback"
            )
            recommendations.append(rec)

        return recommendations

    def _is_actionable_feedback(self, text: str) -> bool:
        """Determine if text contains actionable feedback."""
        actionable_keywords = [
            "should",
            "must",
            "need to",
            "consider",
            "suggest",
            "recommend",
            "missing",
            "unclear",
            "confusing",
            "incorrect",
            "please",
            "could you",
            "would be better"
        ]

        text_lower = text.lower()
        return any(kw in text_lower for kw in actionable_keywords)

    def _text_to_recommendation(
        self,
        text: str,
        edit_id: str,
        source: str
    ) -> EditRecommendation:
        """Convert general feedback text to EditRecommendation."""
        # Infer properties
        section = self._infer_section_from_text(text)
        category = self._infer_category_from_text(text)
        severity = self._infer_severity_from_text(text)
        edit_type = classify_edit_type(text, text, category)
        priority = calculate_priority(severity, category, section, text)
        action = self._extract_action_from_comment(text)

        return EditRecommendation(
            id=edit_id,
            source=source,
            category=category,
            priority=priority,
            edit_type=edit_type,
            section=section,
            issue_description=text,
            recommended_action=action
        )

    def _infer_section_from_text(self, text: str) -> str:
        """Infer section from text."""
        text_lower = text.lower()

        section_keywords = {
            "abstract": ["abstract"],
            "introduction": ["introduction", "background"],
            "methods": ["methods", "methodology", "materials"],
            "results": ["results", "findings"],
            "discussion": ["discussion", "conclusion"],
            "availability": ["availability", "data", "code"]
        }

        for section, keywords in section_keywords.items():
            if any(kw in text_lower for kw in keywords):
                return section

        return "global"

    def _infer_category_from_text(self, text: str) -> str:
        """Infer category from text."""
        text_lower = text.lower()

        category_keywords = {
            "evidence_support": ["evidence", "support", "citation", "reference"],
            "content_accuracy": ["incorrect", "inaccurate", "wrong", "error"],
            "clarity": ["unclear", "confusing", "ambiguous", "vague"],
            "reproducibility": ["reproducible", "replicate", "workflow", "pipeline"],
            "structure": ["organize", "structure", "order", "flow"],
            "formatting": ["format", "style", "heading", "font"],
            "citation_quality": ["citation", "reference", "cite"],
            "word_count": ["verbose", "concise", "lengthy", "brief"]
        }

        for category, keywords in category_keywords.items():
            if any(kw in text_lower for kw in keywords):
                return category

        return "other"

    def _infer_severity_from_text(self, text: str) -> str:
        """Infer severity from text."""
        text_lower = text.lower()

        # Major indicators
        if any(kw in text_lower for kw in ["critical", "major", "must", "essential", "required"]):
            return "MAJOR"

        # Warning indicators
        if any(kw in text_lower for kw in ["consider", "suggest", "might", "could"]):
            return "WARNING"

        # Default to MINOR
        return "MINOR"

    def _extract_action_from_comment(self, text: str) -> str:
        """Extract recommended action from comment text."""
        # Look for imperative sentences
        sentences = text.split('.')

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            # Check for action verbs
            action_verbs = ["add", "remove", "revise", "change", "update", "clarify", "specify", "include"]

            words = sentence.lower().split()
            if any(verb in words for verb in action_verbs):
                return sentence

        # Default: use first sentence
        return sentences[0].strip() if sentences else text

    def parse_pdf_annotations(self, pdf_path: Path) -> List[EditRecommendation]:
        """
        Parse annotations from a PDF file.

        Args:
            pdf_path: Path to PDF file with annotations

        Returns:
            List of EditRecommendation objects

        Note: Requires PyPDF2 or similar library
        """
        try:
            import PyPDF2
        except ImportError:
            print("Warning: PyPDF2 not installed. Install with: pip install PyPDF2")
            return []

        recommendations = []

        try:
            with open(pdf_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)

                for page_num, page in enumerate(pdf_reader.pages):
                    if '/Annots' in page:
                        annotations = page['/Annots']

                        for i, annotation in enumerate(annotations):
                            annot_obj = annotation.get_object()

                            if '/Contents' in annot_obj:
                                comment_text = annot_obj['/Contents']

                                rec = self._text_to_recommendation(
                                    comment_text,
                                    f"edit_{len(recommendations) + 1:03d}",
                                    "pdf_annotations"
                                )
                                rec.notes = f"Page {page_num + 1}"
                                recommendations.append(rec)

        except Exception as e:
            print(f"Warning: Could not parse PDF annotations: {e}")

        return recommendations


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: rrwrite_external_feedback_parser.py <manuscript_dir> <feedback_file>")
        print("  feedback_file can be .docx, .txt (email), or .pdf")
        sys.exit(1)

    manuscript_dir = Path(sys.argv[1])
    feedback_file = Path(sys.argv[2])

    parser = ExternalFeedbackParser(manuscript_dir)

    if feedback_file.suffix == '.docx':
        recs = parser.parse_word_comments(feedback_file)
    elif feedback_file.suffix == '.txt':
        recs = parser.parse_email_feedback(feedback_file)
    elif feedback_file.suffix == '.pdf':
        recs = parser.parse_pdf_annotations(feedback_file)
    else:
        print(f"Unsupported file type: {feedback_file.suffix}")
        sys.exit(1)

    print(f"Extracted {len(recs)} recommendations")
    for rec in recs[:5]:
        print(f"  [{rec.priority}] {rec.edit_type}: {rec.issue_description[:60]}...")
