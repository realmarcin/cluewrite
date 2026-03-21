#!/usr/bin/env python3
"""
Consolidate multiple feedback sources into structured edit recommendations.

Merges:
1. Adam's rewrite patterns (structural/terminology changes)
2. Adam's formal feedback (4 core principles)
3. Actionable v1 Word comments

Generates: edit_recommendations_v1.json
"""

import argparse
import json
import re
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class EditRecommendation:
    """Structured edit recommendation."""
    recommendation_id: str
    priority: str  # critical, important, optional
    edit_type: str  # structural, content, language, claim, figure, citation
    section: str   # Abstract, Introduction, Results, Discussion, Methods, All
    rationale: str
    source: str    # Adam's rewrite, Adam's feedback, v1 comments
    original_text: Optional[str] = None
    recommended_text: Optional[str] = None
    dependencies: Optional[List[str]] = None


class FeedbackConsolidator:
    """Consolidate feedback from multiple sources."""

    def __init__(self, manuscript_dir: Path):
        self.manuscript_dir = manuscript_dir
        self.recommendations: List[EditRecommendation] = []
        self.rec_counter = 0

    def _next_id(self) -> str:
        """Generate next recommendation ID."""
        self.rec_counter += 1
        return f"R{self.rec_counter:03d}"

    def add_recommendation(self, **kwargs) -> str:
        """Add a recommendation and return its ID."""
        rec_id = self._next_id()
        rec = EditRecommendation(recommendation_id=rec_id, **kwargs)
        self.recommendations.append(rec)
        return rec_id

    def generate_from_adams_principles(self):
        """Generate recommendations from Adam's 4 core principles."""

        # Principle 1: Prediction ≠ Adaptation
        self.add_recommendation(
            priority="critical",
            edit_type="language",
            section="All",
            rationale="Replace 'adaptive traits' with 'ecosystem-discriminative features' throughout. Prediction reflects discriminative power, not evolutionary selection.",
            source="Adam's feedback - Principle 1",
            original_text="adaptive traits",
            recommended_text="ecosystem-discriminative features"
        )

        self.add_recommendation(
            priority="critical",
            edit_type="language",
            section="All",
            rationale="Replace 'characteristic traits' with 'ecosystem-discriminative features' or 'ecosystem-associated features'",
            source="Adam's feedback - Principle 1",
            original_text="characteristic traits",
            recommended_text="ecosystem-discriminative features"
        )

        self.add_recommendation(
            priority="critical",
            edit_type="language",
            section="Results",
            rationale="Remove or heavily moderate any language implying adaptation, selection, or fitness in Results. Reserve for Discussion as hypothesis only.",
            source="Adam's feedback - Principle 1",
            original_text="essential for survival|selection|adaptive significance",
            recommended_text="associated with|statistically robust discriminators|may warrant investigation of adaptive hypotheses"
        )

        # Principle 2: Accuracy as Foundation
        self.add_recommendation(
            priority="important",
            edit_type="content",
            section="Results",
            rationale="Reframe accuracy discussion: accuracy justifies interpretation, but the contribution is the compact, interpretable feature set. Don't present as competition with black-box models.",
            source="Adam's feedback - Principle 2"
        )

        self.add_recommendation(
            priority="important",
            edit_type="content",
            section="Results",
            rationale="Emphasize that 183-feature model matches full model performance WHILE enabling interpretability. Lead with feature compactness and robustness, not just accuracy numbers.",
            source="Adam's feedback - Principle 2"
        )

        # Principle 3: Bias as Result
        self.add_recommendation(
            priority="important",
            edit_type="content",
            section="Results",
            rationale="Reframe uneven sampling and feature-sharing asymmetries as informative outcomes, not defensive caveats. E.g., 'Host-associated ecosystems show more shared features—this reflects both biology and data density'",
            source="Adam's feedback - Principle 3"
        )

        # Principle 4: Representations ≠ Truth
        self.add_recommendation(
            priority="critical",
            edit_type="content",
            section="Results",
            rationale="Reframe hierarchy/network analysis: these are complementary representations, not corrections to GOLD. Agreement AND disagreement with GOLD are both informative.",
            source="Adam's feedback - Principle 4"
        )

        self.add_recommendation(
            priority="critical",
            edit_type="language",
            section="Discussion",
            rationale="Remove language suggesting hierarchies/networks reveal 'true structure' or 'correct' GOLD. Use: 'complementary lens', 'alternative representation', 'informative perspective'",
            source="Adam's feedback - Principle 4",
            original_text="true structure|corrects GOLD|reveals actual relationships",
            recommended_text="provides complementary view|offers alternative lens|exposes different organizational scales"
        )

    def generate_from_adams_rewrite(self):
        """Generate recommendations from Adam's rewrite patterns."""

        # Abstract restructuring
        self.add_recommendation(
            priority="critical",
            edit_type="structural",
            section="Abstract",
            rationale="Rewrite abstract to: (1) open with biology context, (2) explicitly contrast with prior work (16S, black-box), (3) frame as framework enabling hypotheses not proving mechanisms, (4) emphasize interpretability",
            source="Adam's rewrite - Abstract"
        )

        # Introduction restructuring (6-paragraph funnel)
        intro_id = self.add_recommendation(
            priority="critical",
            edit_type="structural",
            section="Introduction",
            rationale="Restructure to 5-6 paragraph funnel: (1) Microbial importance, (2) Survey context - aggregation enables features, (3) Prior work limitations (categorized), (4) Our framework - explicit contrast, (5) Study goals - discriminative features for hypotheses",
            source="Adam's rewrite - Introduction"
        )

        self.add_recommendation(
            priority="critical",
            edit_type="content",
            section="Introduction",
            rationale="Add explicit positioning statement early: 'Unlike prior global surveys that catalog diversity or distribution, and unlike black-box classifiers that maximize accuracy, our approach identifies which metagenomic features actually drive ecosystem discrimination'",
            source="Adam's rewrite - Introduction",
            dependencies=[intro_id]
        )

        self.add_recommendation(
            priority="important",
            edit_type="content",
            section="Introduction",
            rationale="Delay adaptive language to later paragraphs. Frame adaptation as motivating hypothesis rather than premise.",
            source="Adam's rewrite - Introduction",
            dependencies=[intro_id]
        )

        # Results section titles
        self.add_recommendation(
            priority="important",
            edit_type="structural",
            section="Results",
            rationale="Rename Results subsections to remove 'traits' language: 'Toward traits of microbiomes' → 'Toward ecosystem-discriminative feature structure'; 'Interpreting putative adaptive traits' → 'Interpreting ecosystem-discriminative metagenome features'",
            source="Adam's rewrite - Results"
        )

        # Confusion analysis
        self.add_recommendation(
            priority="critical",
            edit_type="content",
            section="Results",
            rationale="Reframe confusion matrix analysis: (1) Keep insight in main text (structured, non-random misclassification), (2) Move detailed taxonomy to Supplement, (3) AVOID adaptation/gene-flow language - use 'associated with', 'consistent with', 'indicative of shared pressures'",
            source="Adam's rewrite - Results (Confusion)"
        )

        self.add_recommendation(
            priority="critical",
            edit_type="language",
            section="Results",
            rationale="Remove evolutionary/causal assertions from confusion analysis. The value is that misclassification becomes informative structure, NOT that it explains mechanisms.",
            source="Adam's rewrite - Results (Confusion)"
        )

        # Feature sharing
        self.add_recommendation(
            priority="important",
            edit_type="content",
            section="Results",
            rationale="Introduce 'ecosystem-discriminative features' first, use 'traits' explicitly as interpretive lens, not claim. Frame asymmetries in feature sharing as informative about data landscape as much as biology.",
            source="Adam's rewrite - Results (Features)"
        )

        # Validation section
        self.add_recommendation(
            priority="important",
            edit_type="content",
            section="Results",
            rationale="Functional validation: foreground asymmetry - some signals (gut carbohydrates) are biologically anchored (confidence), others are statistically robust but mechanistically underdetermined. Resisting forced interpretation is STRENGTH not weakness.",
            source="Adam's rewrite - Results (Validation)"
        )

        # Pseudo-abundance
        self.add_recommendation(
            priority="important",
            edit_type="content",
            section="Methods",
            rationale="Single, confident pseudo-abundance justification: state what it captures (diversity of genomic contexts, robustness to depth), what it doesn't (fitness, selection), then stop revisiting. Don't be defensive.",
            source="Adam's rewrite - Methods"
        )

        # Discussion
        self.add_recommendation(
            priority="important",
            edit_type="content",
            section="Discussion",
            rationale="Tighten Discussion to: (1) Synthesize insights at correct epistemic level, (2) Treat misclassification/networks as hypothesis-generating, (3) Emphasize uneven interpretability as insight, (4) Avoid causal/evolutionary claims unless labeled as future directions",
            source="Adam's rewrite - Discussion"
        )

        self.add_recommendation(
            priority="important",
            edit_type="content",
            section="Discussion",
            rationale="Conclusion should reinforce what framework ENABLES not what it PROVES. Soften phrases implying demonstrated adaptation or mapped gene flow.",
            source="Adam's rewrite - Discussion"
        )

    def generate_from_v1_comments(self):
        """Generate recommendations from actionable v1 comments."""

        # Introduction clarity (Comments 8-9, 10)
        self.add_recommendation(
            priority="important",
            edit_type="content",
            section="Introduction",
            rationale="Implement Adam's suggested 6-paragraph structure from Comment 8-9: establishes motivation → survey context → prior work (4-5 examples) → our approach → results preview → biological findings preview",
            source="v1 Comment 8-9 (Adam)"
        )

        # Prior work positioning (Comment 13, 14, 15)
        self.add_recommendation(
            priority="important",
            edit_type="content",
            section="Introduction",
            rationale="Clarify four dimensions when reviewing prior work: (1) nature/resolution of features, (2) nature of predictions, (3) model interpretability, (4) model quality. Contrast our approach on each dimension.",
            source="v1 Comment 14 (Adam)"
        )

        self.add_recommendation(
            priority="important",
            edit_type="content",
            section="Introduction",
            rationale="Justify MGnify choice (not criticize others for not using it). Motivate why we chose MGnify then explain processing to get reasonable features.",
            source="v1 Comment 14 (Adam)"
        )

        # Results jargon reduction (Comments 57, 60, 63 - Joshua)
        self.add_recommendation(
            priority="important",
            edit_type="language",
            section="Results",
            rationale="Reduce jargon in ML methods paragraph. Make accessible to broader audience (Joshua's comment repeated 3x suggests importance).",
            source="v1 Comments 57, 60, 63 (Joshua)"
        )

        # ML methods simplification (Comments 18-19, 61, 64 - Adam)
        self.add_recommendation(
            priority="important",
            edit_type="content",
            section="Results",
            rationale="Simplify ML workflow description: single paragraph covering CatBoost, hyperparameter tuning, knockoff permutation, Shapley scores. Move details to Methods/Supplement. See Adam's suggested condensed text in Comment 18.",
            source="v1 Comments 18-19, 61, 64 (Adam)"
        )

        # Performance metrics justification (Comments 19, 59, 62, 65)
        self.add_recommendation(
            priority="optional",
            edit_type="content",
            section="Methods",
            rationale="Add justification for performance metric choice (accuracy, precision, recall vs MCC, Cohen's Kappa). Explain why these metrics chosen for multiclass imbalance problem.",
            source="v1 Comments 19, 59, 62, 65 (Adam)"
        )

        # Confusion matrix presentation (Comment 78 - Adam)
        self.add_recommendation(
            priority="important",
            edit_type="content",
            section="Results",
            rationale="Reorganize confusion matrix paragraph: (1) Open with strong diagonal performance, (2) State 36 errors, (3) Present categories in decreasing order of importance, (4) Clarify contamination = biological trace DNA not label error",
            source="v1 Comment 78 (Adam)"
        )

        # Feature interpretation clarity (Comment 38 - Adam)
        self.add_recommendation(
            priority="important",
            edit_type="content",
            section="Results",
            rationale="Organize taxonomic vs functional features section: (1) Taxonomic features are interpretably associated (examples), (2) Annotated proteins less mechanistically clear, (3) Most predictive features are poorly annotated → motivates deeper investigation",
            source="v1 Comment 38 (Adam)"
        )

        # Pseudo-abundance explanation (Comments 71, 72, 78)
        self.add_recommendation(
            priority="important",
            edit_type="content",
            section="Methods",
            rationale="Clarify pseudo-abundance: represents diversity of genomic contexts (how many different microbes have this feature), NOT total abundance. Predictive of environment presence, not read count. Marcin's explanation in Comment 72.",
            source="v1 Comments 71-72 (Marcin)"
        )

        # Hierarchy reconstruction justification (Comments 40-41)
        self.add_recommendation(
            priority="optional",
            edit_type="content",
            section="Results",
            rationale="Justify tanglegram analysis: not just sanity check. Since trained on leaf labels only (not all hierarchical combinations), successful hierarchy reconstruction is non-trivial given noisy, heterogeneous data. Shows robustness.",
            source="v1 Comments 40-41 (Adam/Marcin)"
        )

        # COG analysis clarity (Comment 36, 56)
        self.add_recommendation(
            priority="optional",
            edit_type="content",
            section="Results",
            rationale="Clarify COG functional analysis: (1) Uses InterPro domains only (not taxonomic), (2) COG chosen over GO because less biased against microbes and GO derived from InterPro, (3) Purpose is full-length protein validation of domain behavior",
            source="v1 Comments 36, 56 (Adam/Marcin)"
        )

        # Network analysis clarity (Comment 48)
        self.add_recommendation(
            priority="optional",
            edit_type="content",
            section="Results",
            rationale="Clarify network representation purpose: identifies ecosystem 'bridges' where mixed important features suggest interfaces/transitions beyond strict hierarchies. Networks expose where ontology is insufficient, not where it's wrong.",
            source="v1 Comment 48 (Adam)"
        )

        # Robustness discussion (Comment 1, from Adam feedback doc)
        self.add_recommendation(
            priority="important",
            edit_type="content",
            section="Results",
            rationale="Address feature stability: claim is robustness of patterns and feature classes, not invariance of individual 183 features. Acknowledge this explicitly without new experiments.",
            source="Adam's feedback - Robustness"
        )

        # Fast vs slow adaptations (Comment 33 - Paramvir)
        self.add_recommendation(
            priority="optional",
            edit_type="content",
            section="Discussion",
            rationale="Clarify or remove 'fast vs slow adaptations' concept. If keeping: explain toxin/antitoxin as potentially rapid response vs stable ecosystem traits. Note temporal data limitation.",
            source="v1 Comment 33 (Paramvir)"
        )

        # Claims moderation (Comments 50-51)
        self.add_recommendation(
            priority="important",
            edit_type="language",
            section="Discussion",
            rationale="Tone down big claims throughout Discussion. Chris Neely flagged: 'pretty big claim... opens us up to push-back'. Marcin responded 'toned down and edited more' - ensure this is consistent.",
            source="v1 Comments 50-51 (Chris/Marcin)"
        )

    def generate_all_recommendations(self):
        """Generate all recommendations from all sources."""
        print("Generating recommendations from Adam's 4 principles...")
        self.generate_from_adams_principles()

        print("Generating recommendations from Adam's rewrite patterns...")
        self.generate_from_adams_rewrite()

        print("Generating recommendations from actionable v1 comments...")
        self.generate_from_v1_comments()

        print(f"\n✓ Generated {len(self.recommendations)} total recommendations")

        # Summary by priority
        by_priority = {}
        for rec in self.recommendations:
            by_priority[rec.priority] = by_priority.get(rec.priority, 0) + 1

        print("\nBreakdown by priority:")
        for priority in ['critical', 'important', 'optional']:
            count = by_priority.get(priority, 0)
            print(f"  • {priority.capitalize()}: {count}")

        # Summary by section
        by_section = {}
        for rec in self.recommendations:
            by_section[rec.section] = by_section.get(rec.section, 0) + 1

        print("\nBreakdown by section:")
        for section in sorted(by_section.keys()):
            print(f"  • {section}: {by_section[section]}")

    def save_json(self, output_file: Path):
        """Save recommendations to JSON file."""
        recommendations_dict = [asdict(rec) for rec in self.recommendations]

        output = {
            "metadata": {
                "manuscript_dir": str(self.manuscript_dir),
                "total_recommendations": len(self.recommendations),
                "sources": [
                    "Adam's feedback - 4 core principles",
                    "Adam's rewrite - structural patterns",
                    "Actionable v1 Word comments (35/83)"
                ],
                "generated_by": "rrwrite-consolidate-feedback.py"
            },
            "recommendations": recommendations_dict
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        print(f"\n✅ Saved recommendations to: {output_file}")

    def save_markdown(self, output_file: Path):
        """Save human-readable markdown summary."""
        lines = [
            "# Edit Recommendations for KBase Manuscript v2",
            "",
            f"**Total Recommendations:** {len(self.recommendations)}",
            "",
            "**Sources:**",
            "1. Adam's feedback - 4 core principles",
            "2. Adam's rewrite - structural patterns",
            "3. Actionable v1 Word comments (35/83)",
            "",
            "---",
            ""
        ]

        # Group by priority
        for priority in ['critical', 'important', 'optional']:
            priority_recs = [r for r in self.recommendations if r.priority == priority]

            if not priority_recs:
                continue

            lines.append(f"## {priority.upper()} Priority ({len(priority_recs)} recommendations)")
            lines.append("")

            # Group by section within priority
            by_section = {}
            for rec in priority_recs:
                if rec.section not in by_section:
                    by_section[rec.section] = []
                by_section[rec.section].append(rec)

            for section in sorted(by_section.keys()):
                lines.append(f"### {section}")
                lines.append("")

                for rec in by_section[section]:
                    lines.append(f"**{rec.recommendation_id}** ({rec.edit_type})")
                    lines.append(f"- **Rationale:** {rec.rationale}")
                    lines.append(f"- **Source:** {rec.source}")

                    if rec.original_text:
                        lines.append(f"- **Original:** `{rec.original_text}`")
                    if rec.recommended_text:
                        lines.append(f"- **Recommended:** `{rec.recommended_text}`")
                    if rec.dependencies:
                        lines.append(f"- **Dependencies:** {', '.join(rec.dependencies)}")

                    lines.append("")

            lines.append("---")
            lines.append("")

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

        print(f"✅ Saved markdown summary to: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Consolidate feedback sources into edit recommendations"
    )
    parser.add_argument(
        '--manuscript-dir',
        type=Path,
        required=True,
        help='Manuscript directory containing feedback files'
    )
    parser.add_argument(
        '--output',
        type=Path,
        help='Output JSON file (default: {manuscript_dir}/edit_recommendations_v1.json)'
    )
    parser.add_argument(
        '--output-md',
        type=Path,
        help='Output markdown file (default: {manuscript_dir}/edit_recommendations_v1.md)'
    )

    args = parser.parse_args()

    # Validate manuscript directory
    if not args.manuscript_dir.exists():
        parser.error(f"Manuscript directory not found: {args.manuscript_dir}")

    # Set default output paths
    if not args.output:
        args.output = args.manuscript_dir / "edit_recommendations_v1.json"
    if not args.output_md:
        args.output_md = args.manuscript_dir / "edit_recommendations_v1.md"

    print(f"Consolidating feedback for: {args.manuscript_dir}\n")

    # Generate recommendations
    consolidator = FeedbackConsolidator(args.manuscript_dir)
    consolidator.generate_all_recommendations()

    # Save outputs
    consolidator.save_json(args.output)
    consolidator.save_markdown(args.output_md)

    print("\n✅ Feedback consolidation complete!")
    print(f"\nNext steps:")
    print(f"1. Review: {args.output_md}")
    print(f"2. Validate: python scripts/rrwrite-validate-edit-recommendations.py --recommendations {args.output}")
    print(f"3. Apply: python scripts/rrwrite-apply-edits.py --manuscript-dir {args.manuscript_dir} --recommendations {args.output}")


if __name__ == '__main__':
    exit(main())
