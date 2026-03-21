#!/usr/bin/env python3
"""
Generate structured edit recommendations from critique reports or external feedback.

This script creates actionable edit recommendation files that can be applied
using the holistic editing system.
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

# Add scripts directory to path
SCRIPTS_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPTS_DIR))

from rrwrite_edit_recommendation_generator import EditRecommendationGenerator
from rrwrite_external_feedback_parser import ExternalFeedbackParser


def generate_markdown_summary(
    recommendations: list,
    metadata: dict,
    output_path: Path
) -> None:
    """Generate human-readable Markdown summary of recommendations."""
    md_lines = []

    # Header
    md_lines.append("# Edit Recommendations")
    md_lines.append("")
    md_lines.append(f"**Generated:** {metadata['generated_at']}")
    md_lines.append(f"**Version:** {metadata['version']}")
    md_lines.append(f"**Total Recommendations:** {metadata['total_recommendations']}")
    md_lines.append("")

    # Summary by priority
    md_lines.append("## Summary by Priority")
    md_lines.append("")
    by_priority = metadata['by_priority']
    md_lines.append(f"- **Critical:** {by_priority['critical']}")
    md_lines.append(f"- **Important:** {by_priority['important']}")
    md_lines.append(f"- **Optional:** {by_priority['optional']}")
    md_lines.append("")

    # Recommendations by priority
    for priority in ["critical", "important", "optional"]:
        priority_recs = [r for r in recommendations if r['priority'] == priority]
        if not priority_recs:
            continue

        md_lines.append(f"## {priority.title()} Priority ({len(priority_recs)})")
        md_lines.append("")

        for rec in priority_recs:
            md_lines.append(f"### {rec['id']}: {rec['edit_type']}")
            md_lines.append("")
            md_lines.append(f"**Section:** {rec['section']}")
            md_lines.append(f"**Category:** {rec['category']}")
            md_lines.append("")
            md_lines.append(f"**Issue:** {rec['issue_description']}")
            md_lines.append("")
            md_lines.append(f"**Action:** {rec['recommended_action']}")
            md_lines.append("")

            if rec.get('impact'):
                md_lines.append(f"**Impact:** {rec['impact']}")
                md_lines.append("")

            if rec.get('evidence_citations'):
                md_lines.append(f"**Supporting Citations:** {', '.join(rec['evidence_citations'])}")
                md_lines.append("")

            md_lines.append("---")
            md_lines.append("")

    output_path.write_text('\n'.join(md_lines), encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(
        description="Generate structured edit recommendations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate from critique report
  %(prog)s --manuscript-dir manuscript/project_v1 --version 1

  # Include format critique
  %(prog)s --manuscript-dir manuscript/project_v1 --version 1 --include-format

  # Generate from Word comments
  %(prog)s --manuscript-dir manuscript/project_v1 --word-comments reviewer_feedback.docx

  # Generate from email feedback
  %(prog)s --manuscript-dir manuscript/project_v1 --email-feedback reviewer_email.txt

  # Combine multiple sources
  %(prog)s --manuscript-dir manuscript/project_v1 --version 1 --word-comments feedback.docx
        """
    )

    parser.add_argument(
        "--manuscript-dir",
        type=Path,
        required=True,
        help="Path to manuscript directory"
    )

    parser.add_argument(
        "--version",
        type=int,
        help="Critique version to process"
    )

    parser.add_argument(
        "--include-format",
        action="store_true",
        help="Include format critique issues (when using --version)"
    )

    parser.add_argument(
        "--word-comments",
        type=Path,
        help="Path to .docx file with Word comments"
    )

    parser.add_argument(
        "--email-feedback",
        type=Path,
        help="Path to .txt file with email feedback"
    )

    parser.add_argument(
        "--pdf-annotations",
        type=Path,
        help="Path to .pdf file with annotations"
    )

    parser.add_argument(
        "--output-json",
        type=Path,
        help="Output path for JSON recommendations (default: manuscript_dir/edit_recommendations_vN.json)"
    )

    parser.add_argument(
        "--output-md",
        type=Path,
        help="Output path for Markdown summary (default: manuscript_dir/edit_recommendations_vN.md)"
    )

    parser.add_argument(
        "--skip-validation",
        action="store_true",
        help="Skip JSON schema validation"
    )

    args = parser.parse_args()

    # Validate inputs
    if not args.version and not any([args.word_comments, args.email_feedback, args.pdf_annotations]):
        parser.error("Must specify either --version or at least one external feedback source")

    all_recommendations = []
    sources = []

    # Generate from critique if specified
    if args.version:
        print(f"Generating recommendations from critique v{args.version}...")
        generator = EditRecommendationGenerator(args.manuscript_dir)
        recs = generator.generate_from_critique(args.version, args.include_format)
        all_recommendations.extend(recs)
        sources.append({
            "type": "critique_content",
            "path": str(args.manuscript_dir / f"critique_content_v{args.version}.md")
        })
        if args.include_format:
            sources.append({
                "type": "critique_format",
                "path": str(args.manuscript_dir / f"critique_format_v{args.version}.md")
            })
        print(f"  ✓ Generated {len(recs)} recommendations from critique")

    # Parse external feedback
    ext_parser = ExternalFeedbackParser(args.manuscript_dir)

    if args.word_comments:
        print(f"Parsing Word comments from {args.word_comments.name}...")
        recs = ext_parser.parse_word_comments(args.word_comments)
        # Renumber IDs to avoid conflicts
        offset = len(all_recommendations)
        for i, rec in enumerate(recs, offset + 1):
            rec.id = f"edit_{i:03d}"
        all_recommendations.extend(recs)
        sources.append({
            "type": "word_comments",
            "path": str(args.word_comments)
        })
        print(f"  ✓ Extracted {len(recs)} recommendations from Word comments")

    if args.email_feedback:
        print(f"Parsing email feedback from {args.email_feedback.name}...")
        recs = ext_parser.parse_email_feedback(args.email_feedback)
        offset = len(all_recommendations)
        for i, rec in enumerate(recs, offset + 1):
            rec.id = f"edit_{i:03d}"
        all_recommendations.extend(recs)
        sources.append({
            "type": "email_feedback",
            "path": str(args.email_feedback)
        })
        print(f"  ✓ Extracted {len(recs)} recommendations from email")

    if args.pdf_annotations:
        print(f"Parsing PDF annotations from {args.pdf_annotations.name}...")
        recs = ext_parser.parse_pdf_annotations(args.pdf_annotations)
        offset = len(all_recommendations)
        for i, rec in enumerate(recs, offset + 1):
            rec.id = f"edit_{i:03d}"
        all_recommendations.extend(recs)
        sources.append({
            "type": "pdf_annotations",
            "path": str(args.pdf_annotations)
        })
        print(f"  ✓ Extracted {len(recs)} recommendations from PDF")

    if not all_recommendations:
        print("✗ No recommendations generated")
        return 1

    # Generate summary statistics
    if args.version:
        generator = EditRecommendationGenerator(args.manuscript_dir)
        summary = generator.generate_summary(all_recommendations)
    else:
        # Manual summary
        summary = {
            "total": len(all_recommendations),
            "by_priority": {"critical": 0, "important": 0, "optional": 0},
            "by_edit_type": {},
            "by_section": {},
            "by_status": {"pending": len(all_recommendations)}
        }
        for rec in all_recommendations:
            summary["by_priority"][rec.priority] = summary["by_priority"].get(rec.priority, 0) + 1
            summary["by_edit_type"][rec.edit_type] = summary["by_edit_type"].get(rec.edit_type, 0) + 1
            summary["by_section"][rec.section] = summary["by_section"].get(rec.section, 0) + 1

    # Build output structure
    output = {
        "metadata": {
            "version": args.version or 1,
            "generated_at": datetime.now().isoformat(),
            "sources": sources,
            "manuscript_dir": str(args.manuscript_dir),
            "total_recommendations": len(all_recommendations),
            "by_priority": summary["by_priority"]
        },
        "recommendations": [rec.to_dict() for rec in all_recommendations],
        "summary": summary
    }

    # Validate against schema
    if not args.skip_validation:
        schema_path = SCRIPTS_DIR.parent / "schemas" / "edit_recommendations_schema.json"
        if schema_path.exists():
            try:
                import jsonschema
                with open(schema_path, 'r', encoding='utf-8') as f:
                    schema = json.load(f)
                jsonschema.validate(output, schema)
                print("✓ Recommendations validate against schema")
            except ImportError:
                print("⚠ jsonschema not installed, skipping validation")
            except Exception as e:
                print(f"✗ Validation error: {e}")
                print("Proceeding anyway...")

    # Determine output paths
    version_suffix = f"v{args.version}" if args.version else "v1"

    if not args.output_json:
        args.output_json = args.manuscript_dir / f"edit_recommendations_{version_suffix}.json"

    if not args.output_md:
        args.output_md = args.manuscript_dir / f"edit_recommendations_{version_suffix}.md"

    # Write JSON
    with open(args.output_json, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)
    print(f"✓ JSON recommendations: {args.output_json}")

    # Write Markdown summary
    generate_markdown_summary(
        output["recommendations"],
        output["metadata"],
        args.output_md
    )
    print(f"✓ Markdown summary: {args.output_md}")

    # Print summary
    print("\n" + "=" * 60)
    print("Summary:")
    print(f"  Total recommendations: {len(all_recommendations)}")
    print(f"  Critical: {summary['by_priority']['critical']}")
    print(f"  Important: {summary['by_priority']['important']}")
    print(f"  Optional: {summary['by_priority']['optional']}")
    print(f"\nTop edit types:")
    for edit_type, count in sorted(summary['by_edit_type'].items(), key=lambda x: -x[1])[:5]:
        print(f"  {edit_type}: {count}")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
