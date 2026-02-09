#!/usr/bin/env python3
"""
Content review script - Stage 1 of two-stage review.

Focus: Scientific validity, argument strength, evidence quality.
Mindset: Skeptical scientist - assume claims wrong until proven.

Usage:
    python scripts/rrwrite-critique-content.py --file manuscript/manuscript.md --output manuscript/critique_content_v1.md
"""

import argparse
import re
from pathlib import Path
from datetime import datetime


class ContentReviewer:
    """Review scientific content and arguments."""

    def __init__(self, manuscript_path: Path):
        self.manuscript_path = manuscript_path
        self.content = self._load_manuscript()
        self.issues = []
        self.strengths = []

    def _load_manuscript(self) -> str:
        """Load manuscript content."""
        if not self.manuscript_path.exists():
            raise FileNotFoundError(f"Manuscript not found: {self.manuscript_path}")

        with open(self.manuscript_path, 'r', encoding='utf-8') as f:
            return f.read()

    def check_research_question(self) -> None:
        """Verify manuscript addresses stated research question."""
        # Look for research question in introduction
        intro_match = re.search(
            r'#\s+Introduction\s+(.*?)(?=#\s+\w+|\Z)',
            self.content,
            re.DOTALL | re.IGNORECASE
        )

        if not intro_match:
            self.issues.append({
                'severity': 'major',
                'category': 'Structure',
                'description': 'No Introduction section found to establish research question',
                'impact': 'Readers cannot understand what the manuscript aims to answer',
                'action': 'Add Introduction section with clear research question or hypothesis'
            })
            return

        intro_text = intro_match.group(1)

        # Check for question indicators
        question_indicators = [
            'we ask',
            'we investigate',
            'research question',
            'hypothesis',
            'aim',
            'objective',
            'goal',
            '?'
        ]

        has_question = any(ind in intro_text.lower() for ind in question_indicators)

        if not has_question:
            self.issues.append({
                'severity': 'major',
                'category': 'Clarity',
                'description': 'Research question or hypothesis not clearly stated',
                'impact': 'Unclear what problem the work solves',
                'action': 'Add explicit research question or hypothesis statement in Introduction'
            })
        else:
            self.strengths.append("Research question clearly articulated")

    def check_claim_evidence_support(self) -> None:
        """Verify claims are supported by evidence."""
        # Extract sentences with strong claims
        claim_patterns = [
            r'\b(demonstrates?|proves?|shows?|establishes?)\s',
            r'\b(clearly|significantly|substantially|dramatically)\s',
            r'\b(the best|superior|optimal|ideal)\s',
            r'\b(always|never|all|none|every)\s'
        ]

        for pattern in claim_patterns:
            matches = re.finditer(pattern, self.content, re.IGNORECASE)
            for match in matches:
                # Get sentence containing claim
                start = self.content.rfind('.', 0, match.start()) + 1
                end = self.content.find('.', match.end())
                if end == -1:
                    end = len(self.content)

                sentence = self.content[start:end].strip()

                # Check if citation or data reference nearby
                has_citation = bool(re.search(r'\[[a-zA-Z]+\d{4}[a-z]?\]', sentence))
                has_figure = bool(re.search(r'(?:Figure|Table)\s+\d+', sentence, re.IGNORECASE))

                if not (has_citation or has_figure):
                    self.issues.append({
                        'severity': 'major',
                        'category': 'Evidence',
                        'description': f'Strong claim without evidence: "{sentence[:100]}..."',
                        'impact': 'Unsupported claims undermine credibility',
                        'action': 'Add citation or data reference to support claim'
                    })

    def check_logical_flow(self) -> None:
        """Check for logical gaps in arguments."""
        # Extract section headers
        sections = re.findall(r'^#\s+(\w+)', self.content, re.MULTILINE | re.IGNORECASE)

        # Check required logical flow
        required_flow = ['introduction', 'methods', 'results', 'discussion']
        section_lower = [s.lower() for s in sections]

        for required in required_flow:
            if required not in section_lower:
                self.issues.append({
                    'severity': 'major',
                    'category': 'Structure',
                    'description': f'Missing {required.title()} section breaks logical flow',
                    'impact': 'Readers cannot follow argument progression',
                    'action': f'Add {required.title()} section with appropriate content'
                })

    def check_methods_reproducibility(self) -> None:
        """Verify methods are reproducible."""
        methods_match = re.search(
            r'#\s+Methods\s+(.*?)(?=#\s+\w+|\Z)',
            self.content,
            re.DOTALL | re.IGNORECASE
        )

        if not methods_match:
            return

        methods_text = methods_match.group(1)

        # Check for reproducibility elements
        reproducibility_elements = {
            'software versions': [r'version\s+\d', r'v\d+\.\d+', r'python\s+3\.\d+'],
            'parameters': [r'parameter', r'threshold', r'cutoff', r'alpha\s*=', r'p\s*<'],
            'data sources': [r'dataset', r'database', r'repository', r'downloaded from'],
            'code availability': [r'github', r'gitlab', r'available at', r'code is']
        }

        missing_elements = []
        for element, patterns in reproducibility_elements.items():
            if not any(re.search(p, methods_text, re.IGNORECASE) for p in patterns):
                missing_elements.append(element)

        if missing_elements:
            self.issues.append({
                'severity': 'major',
                'category': 'Reproducibility',
                'description': f'Methods missing reproducibility elements: {", ".join(missing_elements)}',
                'impact': 'Work cannot be reproduced by others',
                'action': f'Add missing elements: {", ".join(missing_elements)}'
            })
        else:
            self.strengths.append("Methods include key reproducibility elements")

    def check_results_interpretation(self) -> None:
        """Validate results interpretations."""
        results_match = re.search(
            r'#\s+Results\s+(.*?)(?=#\s+\w+|\Z)',
            self.content,
            re.DOTALL | re.IGNORECASE
        )

        if not results_match:
            return

        results_text = results_match.group(1)

        # Check for interpretation vs. observation
        interpretation_verbs = [
            'suggests', 'indicates', 'implies', 'means', 'demonstrates',
            'proves', 'confirms', 'validates'
        ]

        interpretation_count = sum(
            len(re.findall(rf'\b{verb}\b', results_text, re.IGNORECASE))
            for verb in interpretation_verbs
        )

        if interpretation_count > 10:
            self.issues.append({
                'severity': 'minor',
                'category': 'Interpretation',
                'description': f'Results section has {interpretation_count} interpretation statements',
                'impact': 'Results should report observations; interpretations belong in Discussion',
                'action': 'Move interpretation statements to Discussion, keep Results observational'
            })

    def check_narrative_coherence(self) -> None:
        """Check if narrative flows logically."""
        # Check for transitions between sections
        sections = re.split(r'^#\s+\w+', self.content, flags=re.MULTILINE)

        if len(sections) < 3:
            return

        # Check if sections reference each other
        for i, section in enumerate(sections[1:], 1):
            # Look for backward references
            has_reference = any(ref in section.lower() for ref in [
                'as described', 'previously', 'above', 'earlier',
                'as shown', 'following', 'next', 'below'
            ])

            if not has_reference and len(section.split()) > 100:
                # Only flag long sections without transitions
                self.issues.append({
                    'severity': 'minor',
                    'category': 'Coherence',
                    'description': f'Section {i} lacks transitional references',
                    'impact': 'Sections feel disconnected',
                    'action': 'Add transitional phrases linking to previous/next sections'
                })

    def generate_report(self, output_path: Path) -> None:
        """Generate content review report."""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# Content Review Report (Stage 1)\n\n")
            f.write(f"**Reviewed:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
            f.write(f"**Manuscript:** {self.manuscript_path}\n")
            f.write(f"**Focus:** Scientific validity, argument strength, evidence quality\n\n")

            # Summary
            major_count = sum(1 for i in self.issues if i['severity'] == 'major')
            minor_count = sum(1 for i in self.issues if i['severity'] == 'minor')

            f.write("## Summary Assessment\n\n")
            if major_count == 0:
                f.write("Content is scientifically sound with no major validity issues. ")
            else:
                f.write(f"Found {major_count} major content issues requiring revision. ")

            if minor_count > 0:
                f.write(f"{minor_count} minor issues could improve clarity and rigor.\n\n")
            else:
                f.write("No minor issues identified.\n\n")

            # Strengths
            if self.strengths:
                f.write("## Strengths\n\n")
                for i, strength in enumerate(self.strengths, 1):
                    f.write(f"{i}. {strength}\n")
                f.write("\n")

            # Major issues
            major_issues = [i for i in self.issues if i['severity'] == 'major']
            if major_issues:
                f.write("## Major Issues (Content)\n\n")
                for i, issue in enumerate(major_issues, 1):
                    f.write(f"{i}. **{issue['category']}:** {issue['description']}\n")
                    f.write(f"   - **Impact:** {issue['impact']}\n")
                    f.write(f"   - **Action:** {issue['action']}\n\n")

            # Minor issues
            minor_issues = [i for i in self.issues if i['severity'] == 'minor']
            if minor_issues:
                f.write("## Minor Issues (Content)\n\n")
                for i, issue in enumerate(minor_issues, 1):
                    f.write(f"{i}. **{issue['category']}:** {issue['description']}\n")
                    f.write(f"   - **Action:** {issue['action']}\n\n")

            # Next steps
            f.write("## Next Steps\n\n")
            f.write("1. Address all major content issues\n")
            f.write("2. Run Stage 2 (format review) after content is validated\n")
            f.write("3. Use command: `python scripts/rrwrite-critique-format.py --file [manuscript]`\n\n")

            # Recommendation
            f.write("## Recommendation\n\n")
            if major_count == 0:
                f.write("✅ Content approved - proceed to format review\n")
            elif major_count <= 2:
                f.write("⚠️  Minor content revisions required before format review\n")
            else:
                f.write("❌ Major content revisions required before format review\n")

    def run_review(self) -> None:
        """Run all content checks."""
        self.check_research_question()
        self.check_claim_evidence_support()
        self.check_logical_flow()
        self.check_methods_reproducibility()
        self.check_results_interpretation()
        self.check_narrative_coherence()


def main():
    parser = argparse.ArgumentParser(
        description="Stage 1 Content Review: Scientific validity and arguments"
    )
    parser.add_argument(
        '--file',
        required=True,
        help='Path to manuscript file'
    )
    parser.add_argument(
        '--output',
        required=True,
        help='Output path for review report'
    )

    args = parser.parse_args()

    reviewer = ContentReviewer(Path(args.file))
    reviewer.run_review()
    reviewer.generate_report(Path(args.output))

    print(f"✅ Content review complete: {args.output}")

    # Exit with error code if major issues found
    major_issues = sum(1 for i in reviewer.issues if i['severity'] == 'major')
    if major_issues > 0:
        print(f"⚠️  Found {major_issues} major content issues")
        return 1

    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
