#!/usr/bin/env python3
"""
Assess current Google Doc against Adam's rewrite and v2 manuscript.

Generates comprehensive gap analysis and actionable edit recommendations
to align Google Doc with v2/Adam's preferred approach.

Usage:
    python scripts/assess_gdoc_vs_adam.py --output manuscript/kbaseeco_v2
"""

import argparse
import re
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict
import json


class ManuscriptComparator:
    """Compare manuscripts and identify structural and content differences."""

    # Adam's 4 core principles
    PRINCIPLES = {
        1: "Prediction is not adaptation",
        2: "Accuracy licenses interpretation; it is not the result",
        3: "Bias is a result, not an apology",
        4: "Hierarchies and networks are representations, not truths"
    }

    # Forbidden terminology per Adam's feedback
    FORBIDDEN_TERMS = [
        "adaptive traits",
        "adaptive significance",
        "characteristic traits",
        "essential for survival",
        "essential functions",
        "selection",
        "fitness",
        "optimality",
        "necessarily",
        "proves",
        "demonstrates adaptation"
    ]

    # Required terminology (v2/Adam version)
    REQUIRED_TERMS = [
        "ecosystem-discriminative features",
        "discriminative features",
        "interpretable machine learning",
        "hypothesis generation",
        "classification ambiguity",
        "consistent with",
        "associated with",
        "suggests"
    ]

    def __init__(self, gdoc_path: Path, adam_rewrite_path: Path,
                 v2_final_path: Path, adam_feedback_path: Path,
                 v2_vs_adam_path: Path):
        """Initialize with paths to all comparison documents."""
        self.gdoc_text = self._read_file(gdoc_path)
        self.adam_text = self._read_file(adam_rewrite_path)
        self.v2_text = self._read_file(v2_final_path)
        self.adam_feedback = self._read_file(adam_feedback_path)
        self.v2_vs_adam = self._read_file(v2_vs_adam_path)

        # Parse sections
        self.gdoc_sections = self._extract_sections(self.gdoc_text)
        self.adam_sections = self._extract_sections(self.adam_text)
        self.v2_sections = self._extract_sections(self.v2_text)

    def _read_file(self, path: Path) -> str:
        """Read file content."""
        try:
            return path.read_text(encoding='utf-8')
        except Exception as e:
            print(f"Warning: Could not read {path}: {e}")
            return ""

    def _extract_sections(self, text: str) -> Dict[str, str]:
        """Extract manuscript sections by heading."""
        sections = {}

        # Match markdown headings
        pattern = r'^(#{1,3})\s+(.+?)$'
        lines = text.split('\n')

        current_section = None
        current_content = []

        for line in lines:
            match = re.match(pattern, line)
            if match:
                # Save previous section
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()

                # Start new section
                level = len(match.group(1))
                title = match.group(2).strip()
                current_section = title
                current_content = []
            else:
                current_content.append(line)

        # Save last section
        if current_section:
            sections[current_section] = '\n'.join(current_content).strip()

        return sections

    def check_terminology(self) -> Dict[str, List[Tuple[str, int]]]:
        """Check for forbidden and missing required terminology."""
        results = {
            'forbidden_found': [],
            'required_missing': []
        }

        # Check forbidden terms
        for term in self.FORBIDDEN_TERMS:
            pattern = re.compile(r'\b' + re.escape(term) + r'\b', re.IGNORECASE)
            matches = list(pattern.finditer(self.gdoc_text))
            if matches:
                results['forbidden_found'].append((term, len(matches)))

        # Check required terms
        for term in self.REQUIRED_TERMS:
            pattern = re.compile(r'\b' + re.escape(term) + r'\b', re.IGNORECASE)
            matches = list(pattern.finditer(self.gdoc_text))
            if not matches:
                results['required_missing'].append((term, 0))
            elif len(matches) < 3:  # Should appear multiple times
                results['required_missing'].append((term, len(matches)))

        return results

    def compare_abstracts(self) -> Dict[str, any]:
        """Compare abstract content and structure."""
        gdoc_abstract = self.gdoc_sections.get('Abstract', '')
        adam_abstract = self.adam_sections.get('Abstract', '')
        v2_abstract = self.v2_sections.get('Abstract', '')

        # Word counts
        gdoc_words = len(gdoc_abstract.split())
        adam_words = len(adam_abstract.split())
        v2_words = len(v2_abstract.split())

        # Check positioning statement
        positioning_keywords = ['unlike', 'rather than', 'instead of', 'distinguishes']
        has_positioning = any(kw in gdoc_abstract.lower() for kw in positioning_keywords)

        # Check for forbidden causal language
        causal_terms = ['demonstrates', 'proves', 'explains', 'causes']
        has_causal = any(term in gdoc_abstract.lower() for term in causal_terms)

        return {
            'gdoc_words': gdoc_words,
            'target_words': v2_words,
            'has_positioning': has_positioning,
            'has_causal_language': has_causal,
            'gap_analysis': self._text_diff_summary(gdoc_abstract, v2_abstract)
        }

    def compare_introductions(self) -> Dict[str, any]:
        """Compare introduction structure and content."""
        gdoc_intro = self.gdoc_sections.get('Introduction', '')
        v2_intro = self.v2_sections.get('Introduction', '')

        # Check for 5-paragraph funnel structure
        gdoc_paragraphs = [p for p in gdoc_intro.split('\n\n') if p.strip()]
        v2_paragraphs = [p for p in v2_intro.split('\n\n') if p.strip()]

        # Check for positioning statement
        positioning_pattern = r'Unlike.*and unlike.*our approach'
        has_positioning = bool(re.search(positioning_pattern, gdoc_intro, re.IGNORECASE))

        return {
            'gdoc_paragraphs': len(gdoc_paragraphs),
            'target_paragraphs': len(v2_paragraphs),
            'has_positioning_statement': has_positioning,
            'gap_analysis': self._text_diff_summary(gdoc_intro, v2_intro)
        }

    def compare_results(self) -> Dict[str, any]:
        """Compare results structure and subsections."""
        # Extract results subsections
        gdoc_results_sections = {k: v for k, v in self.gdoc_sections.items()
                                 if 'result' in k.lower() or any(
                                     keyword in k.lower() for keyword in
                                     ['feature', 'confusion', 'validation', 'interpretation'])}

        v2_results_sections = {k: v for k, v in self.v2_sections.items()
                               if 'result' in k.lower() or any(
                                   keyword in k.lower() for keyword in
                                   ['feature', 'confusion', 'validation', 'interpretation'])}

        return {
            'gdoc_subsections': list(gdoc_results_sections.keys()),
            'v2_subsections': list(v2_results_sections.keys()),
            'missing_subsections': [s for s in v2_results_sections.keys()
                                   if s not in gdoc_results_sections.keys()]
        }

    def compare_discussion(self) -> Dict[str, any]:
        """Compare discussion structure and themes."""
        gdoc_disc = self.gdoc_sections.get('Discussion', '')
        v2_disc = self.v2_sections.get('Discussion', '')

        # Check for Adam's required subsections
        required_themes = [
            'interpretable',
            'biological coherence',
            'ecosystem relationships',
            'classification ambiguity',
            'functional dark matter',
            'limitations'
        ]

        themes_present = {theme: theme.lower() in gdoc_disc.lower()
                         for theme in required_themes}

        return {
            'themes_present': themes_present,
            'gap_analysis': self._text_diff_summary(gdoc_disc, v2_disc)
        }

    def _text_diff_summary(self, text1: str, text2: str) -> str:
        """Generate high-level summary of differences between two texts."""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        unique_to_text1 = words1 - words2
        unique_to_text2 = words2 - words1

        # Filter out common words
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
        unique_to_text1 = {w for w in unique_to_text1 if w not in stopwords and len(w) > 3}
        unique_to_text2 = {w for w in unique_to_text2 if w not in stopwords and len(w) > 3}

        return {
            'unique_to_current': list(unique_to_text1)[:10],
            'unique_to_target': list(unique_to_text2)[:10]
        }

    def generate_edit_priorities(self) -> List[Dict[str, any]]:
        """Generate prioritized list of edits needed."""
        edits = []

        # Priority 1: Title change
        if 'Adaptive Microbial Traits' in self.gdoc_text:
            edits.append({
                'priority': 'CRITICAL',
                'category': 'Title',
                'location': 'Title',
                'issue': 'Still uses v1 title "Adaptive Microbial Traits"',
                'action': 'Replace with v2 title (TBD based on target journal)',
                'estimated_effort': 'Trivial'
            })

        # Priority 2: Forbidden terminology
        terminology_results = self.check_terminology()
        for term, count in terminology_results['forbidden_found']:
            edits.append({
                'priority': 'CRITICAL',
                'category': 'Terminology',
                'location': 'Throughout manuscript',
                'issue': f'Uses forbidden term "{term}" ({count} occurrences)',
                'action': f'Replace with v2-approved terminology',
                'estimated_effort': 'Medium' if count > 10 else 'Low'
            })

        # Priority 3: Missing required terminology
        for term, count in terminology_results['required_missing']:
            edits.append({
                'priority': 'IMPORTANT',
                'category': 'Terminology',
                'location': 'Throughout manuscript',
                'issue': f'Missing/insufficient "{term}" (only {count} uses)',
                'action': f'Add appropriate uses of "{term}"',
                'estimated_effort': 'Medium'
            })

        # Priority 4: Abstract structure
        abstract_comp = self.compare_abstracts()
        if abstract_comp['has_causal_language']:
            edits.append({
                'priority': 'CRITICAL',
                'category': 'Abstract',
                'location': 'Abstract',
                'issue': 'Contains causal language (demonstrates/proves/explains)',
                'action': 'Replace with hedged language (consistent with/suggests/associated)',
                'estimated_effort': 'Low'
            })

        # Priority 5: Introduction positioning
        intro_comp = self.compare_introductions()
        if not intro_comp['has_positioning_statement']:
            edits.append({
                'priority': 'CRITICAL',
                'category': 'Introduction',
                'location': 'Introduction paragraph 4',
                'issue': 'Missing positioning statement (Unlike... and unlike...)',
                'action': 'Add explicit positioning statement as per v2',
                'estimated_effort': 'Low'
            })

        # Sort by priority
        priority_order = {'CRITICAL': 0, 'IMPORTANT': 1, 'OPTIONAL': 2}
        edits.sort(key=lambda x: priority_order.get(x['priority'], 3))

        return edits

    def estimate_sync_approach(self) -> Dict[str, any]:
        """Estimate whether full replacement or incremental edits is better."""
        # Count significant differences
        terminology_results = self.check_terminology()
        forbidden_count = sum(count for _, count in terminology_results['forbidden_found'])

        abstract_comp = self.compare_abstracts()
        intro_comp = self.compare_introductions()

        # Calculate difference score (higher = more different)
        diff_score = 0
        diff_score += forbidden_count * 2  # Heavily weight forbidden terms
        diff_score += len(terminology_results['required_missing']) * 1.5
        diff_score += 10 if abstract_comp['has_causal_language'] else 0
        diff_score += 15 if not intro_comp['has_positioning_statement'] else 0

        # Decision threshold
        if diff_score > 50:
            approach = "FULL_REPLACEMENT"
            rationale = f"Difference score {diff_score:.0f} indicates extensive structural changes needed"
        else:
            approach = "INCREMENTAL_EDITS"
            rationale = f"Difference score {diff_score:.0f} suggests targeted edits sufficient"

        return {
            'recommended_approach': approach,
            'difference_score': diff_score,
            'rationale': rationale,
            'forbidden_term_count': forbidden_count,
            'missing_required_terms': len(terminology_results['required_missing'])
        }


def generate_markdown_report(comparator: ManuscriptComparator, output_path: Path):
    """Generate comprehensive markdown report."""

    # Run all analyses
    terminology = comparator.check_terminology()
    abstract_comp = comparator.compare_abstracts()
    intro_comp = comparator.compare_introductions()
    results_comp = comparator.compare_results()
    discussion_comp = comparator.compare_discussion()
    edits = comparator.generate_edit_priorities()
    approach = comparator.estimate_sync_approach()

    # Build report
    report = []
    report.append("# Google Doc vs Adam's Rewrite: Comprehensive Alignment Report")
    report.append("")
    report.append(f"**Generated:** {Path(__file__).name}")
    report.append(f"**Purpose:** Assess current Google Doc alignment with v2/Adam's approach")
    report.append("")
    report.append("---")
    report.append("")

    # Executive Summary
    report.append("## Executive Summary")
    report.append("")
    report.append(f"**Recommended Approach:** {approach['recommended_approach']}")
    report.append(f"**Difference Score:** {approach['difference_score']:.0f}/100")
    report.append(f"**Rationale:** {approach['rationale']}")
    report.append("")
    report.append("### Critical Findings")
    report.append("")
    report.append(f"- **Forbidden terminology:** {approach['forbidden_term_count']} occurrences")
    report.append(f"- **Missing required terms:** {approach['missing_required_terms']} terms")
    report.append(f"- **Abstract causal language:** {'YES ❌' if abstract_comp['has_causal_language'] else 'NO ✅'}")
    report.append(f"- **Introduction positioning:** {'YES ✅' if intro_comp['has_positioning_statement'] else 'NO ❌'}")
    report.append("")
    report.append("---")
    report.append("")

    # Terminology Analysis
    report.append("## 1. Terminology Compliance")
    report.append("")
    report.append("### Forbidden Terms Found ❌")
    report.append("")
    if terminology['forbidden_found']:
        report.append("| Term | Occurrences | Priority |")
        report.append("|------|-------------|----------|")
        for term, count in terminology['forbidden_found']:
            report.append(f"| {term} | {count} | CRITICAL |")
    else:
        report.append("✅ No forbidden terms found")
    report.append("")

    report.append("### Required Terms Missing/Insufficient ⚠️")
    report.append("")
    if terminology['required_missing']:
        report.append("| Term | Current Count | Target | Priority |")
        report.append("|------|---------------|--------|----------|")
        for term, count in terminology['required_missing']:
            report.append(f"| {term} | {count} | 5+ | IMPORTANT |")
    else:
        report.append("✅ All required terms present")
    report.append("")
    report.append("---")
    report.append("")

    # Abstract Comparison
    report.append("## 2. Abstract Alignment")
    report.append("")
    report.append(f"**Current word count:** {abstract_comp['gdoc_words']}")
    report.append(f"**Target word count:** {abstract_comp['target_words']}")
    report.append(f"**Has positioning statement:** {'YES ✅' if abstract_comp['has_positioning'] else 'NO ❌'}")
    report.append(f"**Contains causal language:** {'YES ❌' if abstract_comp['has_causal_language'] else 'NO ✅'}")
    report.append("")

    if abstract_comp['gap_analysis']:
        report.append("### Key Differences")
        report.append("")
        report.append("**Unique to current Google Doc:**")
        for word in abstract_comp['gap_analysis']['unique_to_current'][:5]:
            report.append(f"- {word}")
        report.append("")
        report.append("**Unique to v2 target:**")
        for word in abstract_comp['gap_analysis']['unique_to_target'][:5]:
            report.append(f"- {word}")
    report.append("")
    report.append("---")
    report.append("")

    # Introduction Comparison
    report.append("## 3. Introduction Structure")
    report.append("")
    report.append(f"**Current paragraphs:** {intro_comp['gdoc_paragraphs']}")
    report.append(f"**Target paragraphs:** {intro_comp['target_paragraphs']} (5-paragraph funnel)")
    report.append(f"**Has positioning statement:** {'YES ✅' if intro_comp['has_positioning_statement'] else 'NO ❌'}")
    report.append("")

    if not intro_comp['has_positioning_statement']:
        report.append("### ❌ Missing Positioning Statement")
        report.append("")
        report.append("**Required format (paragraph 4):**")
        report.append("> Unlike prior global surveys that catalog diversity or distribution, and unlike black-box classifiers that maximize accuracy, our approach identifies which metagenomic features actually drive ecosystem discrimination")
        report.append("")
    report.append("---")
    report.append("")

    # Results Comparison
    report.append("## 4. Results Structure")
    report.append("")
    report.append("### Current Subsections")
    for section in results_comp['gdoc_subsections']:
        report.append(f"- {section}")
    report.append("")

    if results_comp['missing_subsections']:
        report.append("### Missing Subsections ❌")
        for section in results_comp['missing_subsections']:
            report.append(f"- {section}")
        report.append("")
    report.append("---")
    report.append("")

    # Discussion Comparison
    report.append("## 5. Discussion Themes")
    report.append("")
    report.append("### Adam's Required Themes")
    report.append("")
    report.append("| Theme | Present | Status |")
    report.append("|-------|---------|--------|")
    for theme, present in discussion_comp['themes_present'].items():
        status = "✅" if present else "❌"
        report.append(f"| {theme} | {present} | {status} |")
    report.append("")
    report.append("---")
    report.append("")

    # Prioritized Edit List
    report.append("## 6. Prioritized Edit Recommendations")
    report.append("")
    report.append(f"**Total edits identified:** {len(edits)}")
    report.append("")

    # Group by priority
    for priority in ['CRITICAL', 'IMPORTANT', 'OPTIONAL']:
        priority_edits = [e for e in edits if e['priority'] == priority]
        if priority_edits:
            report.append(f"### {priority} Priority ({len(priority_edits)} edits)")
            report.append("")
            report.append("| # | Category | Location | Issue | Action | Effort |")
            report.append("|---|----------|----------|-------|--------|--------|")
            for i, edit in enumerate(priority_edits, 1):
                report.append(f"| {i} | {edit['category']} | {edit['location']} | {edit['issue']} | {edit['action']} | {edit['estimated_effort']} |")
            report.append("")

    report.append("---")
    report.append("")

    # Adam's 4 Principles Checklist
    report.append("## 7. Adam's 4 Principles Compliance")
    report.append("")
    for num, principle in comparator.PRINCIPLES.items():
        report.append(f"### Principle {num}: {principle}")
        report.append("")

        if num == 1:
            status = "❌ VIOLATED" if any('adaptive' in term.lower() for term, _ in terminology['forbidden_found']) else "✅ COMPLIANT"
            report.append(f"**Status:** {status}")
            if status == "❌ VIOLATED":
                report.append("- Remove all 'adaptive traits', 'selection', 'fitness' language")
                report.append("- Reserve evolutionary interpretation for Discussion with hedging")
        elif num == 2:
            status = "✅ COMPLIANT"  # Harder to check automatically
            report.append(f"**Status:** {status}")
            report.append("- Emphasize interpretability over accuracy competition")
        elif num == 3:
            status = "⚠️ NEEDS REVIEW"
            report.append(f"**Status:** {status}")
            report.append("- Present sampling asymmetries as informative, not apologetic")
        elif num == 4:
            status = "⚠️ NEEDS REVIEW"
            report.append(f"**Status:** {status}")
            report.append("- Ensure hierarchies/networks presented as 'complementary lenses'")

        report.append("")

    report.append("---")
    report.append("")

    # Implementation Strategy
    report.append("## 8. Implementation Strategy")
    report.append("")

    if approach['recommended_approach'] == "FULL_REPLACEMENT":
        report.append("### Recommended: Full Document Replacement")
        report.append("")
        report.append("**Rationale:** Extensive structural changes needed justify complete sync with v2_final.md")
        report.append("")
        report.append("**Steps:**")
        report.append("1. Backup current Google Doc version")
        report.append("2. Replace entire content with `manuscript_v2_final.md`")
        report.append("3. Manually review/integrate any Google Doc-specific formatting")
        report.append("4. Verify figures/tables preserved correctly")
        report.append("5. Run final terminology check")
    else:
        report.append("### Recommended: Incremental Targeted Edits")
        report.append("")
        report.append("**Rationale:** Differences are focused; targeted fixes more efficient")
        report.append("")
        report.append("**Steps:**")
        report.append("1. Address all CRITICAL priority edits (see Section 6)")
        report.append("2. Address IMPORTANT priority edits")
        report.append("3. Spot-check OPTIONAL edits")
        report.append("4. Run terminology validation")
        report.append("5. Compare section structure against v2")

    report.append("")
    report.append("---")
    report.append("")

    # Next Steps
    report.append("## Next Steps")
    report.append("")
    report.append("1. **Review this report** - Validate findings and priorities")
    report.append("2. **Choose approach** - Full replacement vs. incremental edits")
    report.append("3. **Execute edits** - Following priority order (CRITICAL → IMPORTANT → OPTIONAL)")
    report.append("4. **Validate alignment** - Re-run this script to verify changes")
    report.append("5. **Sync with v2** - Ensure Google Doc matches `manuscript_v2_final.md`")
    report.append("")
    report.append("---")
    report.append("")
    report.append(f"**Report generated by:** `{Path(__file__).name}`")
    report.append(f"**For questions:** Refer to `V2_VS_ADAM_COMPARISON.md` for detailed alignment analysis")

    # Write report
    output_path.write_text('\n'.join(report), encoding='utf-8')
    print(f"\n✅ Report generated: {output_path}")

    return len(edits)


def main():
    """Main execution."""
    parser = argparse.ArgumentParser(
        description="Assess Google Doc alignment with Adam's rewrite and v2"
    )
    parser.add_argument(
        '--manuscript-dir',
        type=Path,
        default=Path('manuscript/kbaseeco_v2'),
        help='Manuscript directory containing files'
    )
    parser.add_argument(
        '--output',
        type=Path,
        help='Output report path (default: manuscript-dir/GDOC_ADAM_ALIGNMENT_REPORT.md)'
    )

    args = parser.parse_args()

    # Set up paths
    manuscript_dir = args.manuscript_dir
    output_path = args.output or manuscript_dir / 'GDOC_ADAM_ALIGNMENT_REPORT.md'

    # Input files
    gdoc_path = manuscript_dir / 'current_gdoc_content.txt'
    adam_rewrite_path = manuscript_dir.parent / 'kbaseeco_v1' / 'adam_biome_rewrite.md'
    v2_final_path = manuscript_dir / 'manuscript_v2_final.md'
    adam_feedback_path = manuscript_dir.parent / 'kbaseeco_v1' / 'adam_feedback.md'
    v2_vs_adam_path = manuscript_dir / 'V2_VS_ADAM_COMPARISON.md'

    # Validate inputs
    missing = []
    for path in [gdoc_path, adam_rewrite_path, v2_final_path, adam_feedback_path, v2_vs_adam_path]:
        if not path.exists():
            missing.append(str(path))

    if missing:
        print("❌ Missing required files:")
        for path in missing:
            print(f"  - {path}")
        return 1

    print("📊 Analyzing Google Doc vs Adam's rewrite...")
    print(f"  - Current Google Doc: {gdoc_path}")
    print(f"  - Adam's rewrite: {adam_rewrite_path}")
    print(f"  - v2 final: {v2_final_path}")
    print(f"  - Adam's feedback: {adam_feedback_path}")
    print(f"  - v2 vs Adam comparison: {v2_vs_adam_path}")
    print("")

    # Create comparator
    comparator = ManuscriptComparator(
        gdoc_path=gdoc_path,
        adam_rewrite_path=adam_rewrite_path,
        v2_final_path=v2_final_path,
        adam_feedback_path=adam_feedback_path,
        v2_vs_adam_path=v2_vs_adam_path
    )

    # Generate report
    edit_count = generate_markdown_report(comparator, output_path)

    print(f"\n📋 Summary:")
    print(f"  - Total edits identified: {edit_count}")
    print(f"  - Report: {output_path}")
    print(f"\n✅ Assessment complete!")

    return 0


if __name__ == '__main__':
    exit(main())
