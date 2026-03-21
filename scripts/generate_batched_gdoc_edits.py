#!/usr/bin/env python3
"""
Generate Batched Google Doc Edit Instructions (Paperpile-Safe)

Reads current Google Doc content, target markdown (v2_final), and alignment report
to generate surgical edit batches that preserve Paperpile citation links.

Usage:
    python scripts/generate_batched_gdoc_edits.py \
        --current manuscript/kbaseeco_v2/current_gdoc_content.txt \
        --target manuscript/kbaseeco_v2/manuscript_v2_final.md \
        --report manuscript/kbaseeco_v2/GDOC_ADAM_ALIGNMENT_REPORT.md \
        --output manuscript/kbaseeco_v2/BATCHED_EDIT_PLAN.md
"""

import argparse
import re
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class Edit:
    """Represents a single edit operation"""
    batch_num: int
    batch_name: str
    edit_num: int
    section: str
    old_text: str
    new_text: str
    search_snippet: str  # First 80 chars for Google Doc search
    citation_count_before: int
    citation_count_after: int
    priority: str
    paperpile_risk: str
    instructions: str


def count_citations(text: str) -> int:
    """Count citations in text (various formats)"""
    # Match Paperpile format: (Author et al., YEAR)
    paperpile = len(re.findall(r'\([A-Z][a-z]+(?:\set\sal\.)?,\s*\d{4}[a-z]?\)', text))
    # Match numbered citations: [1], [2,3], [4-6]
    numbered = len(re.findall(r'\[\d+(?:[-,]\d+)*\]', text))
    # Match author-year: Smith et al. 2020
    author_year = len(re.findall(r'[A-Z][a-z]+\set\sal\.\s+\d{4}', text))

    return paperpile + numbered + author_year


def extract_search_snippet(text: str, max_chars: int = 80) -> str:
    """Extract first N chars for Google Doc search, cleaned"""
    snippet = text.strip()[:max_chars]
    # Clean up for better search matching
    snippet = ' '.join(snippet.split())  # Normalize whitespace
    return snippet


def extract_section_text(content: str, section_name: str) -> str:
    """Extract a section from content (handles both markdown and plain text)"""
    lines = content.split('\n')
    section_lines = []
    in_section = False
    section_level = None

    # Define section end markers (common section names)
    section_markers = [
        'Abstract', 'Introduction', 'Results', 'Discussion', 'Methods',
        'Materials and Methods', 'Conclusion', 'Acknowledgments', 'References',
        'Supplementary', 'Figure', 'Table'
    ]

    for i, line in enumerate(lines):
        # Try markdown header match first
        md_match = re.match(r'^(#{1,2})\s+(.+)$', line)
        if md_match:
            section_text = md_match.group(2).strip()
            if section_text.startswith(section_name):
                in_section = True
                section_level = len(md_match.group(1))
                section_lines.append(line)
                continue
            elif in_section and len(md_match.group(1)) <= section_level:
                # Hit another section at same/higher level
                break

        # Try plain text section marker (e.g., "Abstract 242", "Introduction")
        if not in_section:
            # Check if line starts with section name
            if line.strip().startswith(section_name):
                in_section = True
                section_lines.append(line)
                continue

        # If we're in a section, collect lines until we hit another section marker
        if in_section:
            # Check if this line is a new section marker
            is_new_section = False
            for marker in section_markers:
                if line.strip().startswith(marker) and marker != section_name:
                    is_new_section = True
                    break

            if is_new_section:
                break

            section_lines.append(line)

    return '\n'.join(section_lines)


def parse_forbidden_terms(report_content: str) -> Dict[str, int]:
    """Parse forbidden terms from alignment report"""
    forbidden = {}

    # Find the forbidden terms table
    lines = report_content.split('\n')
    in_table = False

    for line in lines:
        if '### Forbidden Terms Found' in line:
            in_table = True
            continue

        if in_table:
            # Parse table rows: | term | count | priority |
            match = re.match(r'\|\s*([^|]+)\s*\|\s*(\d+)\s*\|\s*([^|]+)\s*\|', line)
            if match:
                term = match.group(1).strip()
                count = int(match.group(2).strip())
                if term and term != 'Term':  # Skip header
                    forbidden[term] = count
            elif line.strip().startswith('###'):
                break

    return forbidden


def generate_terminology_batch(current: str, forbidden_terms: Dict[str, int]) -> List[Edit]:
    """Generate Batch 2: Terminology find/replace edits"""
    edits = []

    # Define replacements for forbidden terms
    replacements = {
        'adaptive significance': 'ecosystem-discriminative significance',
        'essential for survival': 'characteristic of',
        'selection': 'enrichment',
        'adaptive traits': 'characteristic traits',
        'selection pressure': 'environmental filtering',
        'evolutionary selection': 'differential distribution'
    }

    edit_num = 1
    for old_term, expected_count in forbidden_terms.items():
        if old_term in replacements:
            new_term = replacements[old_term]

            # Count actual occurrences (case-insensitive)
            pattern = re.compile(re.escape(old_term), re.IGNORECASE)
            matches = list(pattern.finditer(current))
            actual_count = len(matches)

            if actual_count > 0:
                # Create a single global find/replace edit
                edits.append(Edit(
                    batch_num=2,
                    batch_name="Terminology",
                    edit_num=edit_num,
                    section="Throughout",
                    old_text=old_term,
                    new_text=new_term,
                    search_snippet=old_term,
                    citation_count_before=0,
                    citation_count_after=0,
                    priority="CRITICAL",
                    paperpile_risk="LOW (find/replace safe)",
                    instructions=f"Use Google Docs Find & Replace (Ctrl+H):\n"
                                f"   - Find: '{old_term}'\n"
                                f"   - Replace: '{new_term}'\n"
                                f"   - Match case: No\n"
                                f"   - Expected replacements: {actual_count}"
                ))
                edit_num += 1

    return edits


def split_into_paragraphs(text: str) -> List[str]:
    """Split text into paragraphs, preserving structure"""
    # Split by double newlines
    paragraphs = re.split(r'\n\s*\n', text)
    return [p.strip() for p in paragraphs if p.strip()]


def generate_section_edits(
    batch_num: int,
    batch_name: str,
    section_name: str,
    current_section: str,
    target_section: str,
    special_instructions: str = None
) -> List[Edit]:
    """Generate paragraph-level edits for a section"""
    edits = []

    # Split into paragraphs
    current_paras = split_into_paragraphs(current_section)
    target_paras = split_into_paragraphs(target_section)

    # Simple alignment: if paragraph counts differ significantly, flag for manual review
    if len(current_paras) != len(target_paras):
        # Create a single edit for the entire section
        edits.append(Edit(
            batch_num=batch_num,
            batch_name=batch_name,
            edit_num=1,
            section=section_name,
            old_text=current_section[:500] + "..." if len(current_section) > 500 else current_section,
            new_text=target_section[:500] + "..." if len(target_section) > 500 else target_section,
            search_snippet=extract_search_snippet(current_section),
            citation_count_before=count_citations(current_section),
            citation_count_after=count_citations(target_section),
            priority="CRITICAL",
            paperpile_risk="MEDIUM (manual verification required)",
            instructions=f"⚠️ Paragraph count mismatch ({len(current_paras)} → {len(target_paras)})\n"
                        f"   Manual review required. See full section text below."
        ))
    else:
        # Paragraph-by-paragraph comparison
        edit_num = 1
        for i, (current_para, target_para) in enumerate(zip(current_paras, target_paras), 1):
            if current_para.strip() != target_para.strip():
                # Significant difference, create edit
                edits.append(Edit(
                    batch_num=batch_num,
                    batch_name=batch_name,
                    edit_num=edit_num,
                    section=f"{section_name} (Paragraph {i})",
                    old_text=current_para,
                    new_text=target_para,
                    search_snippet=extract_search_snippet(current_para),
                    citation_count_before=count_citations(current_para),
                    citation_count_after=count_citations(target_para),
                    priority="IMPORTANT" if count_citations(target_para) > 0 else "OPTIONAL",
                    paperpile_risk="HIGH" if count_citations(target_para) > count_citations(current_para) else "MEDIUM",
                    instructions=f"Find paragraph starting with:\n   '{extract_search_snippet(current_para)}'\n"
                                f"Replace entire paragraph with text below."
                ))
                edit_num += 1

    # Add special instruction edit if provided
    if special_instructions and not any(special_instructions in e.instructions for e in edits):
        edits.append(Edit(
            batch_num=batch_num,
            batch_name=batch_name,
            edit_num=len(edits) + 1,
            section=f"{section_name} (Special)",
            old_text="",
            new_text=special_instructions,
            search_snippet="",
            citation_count_before=0,
            citation_count_after=0,
            priority="CRITICAL",
            paperpile_risk="LOW",
            instructions=special_instructions
        ))

    return edits


def format_edit_markdown(edit: Edit) -> str:
    """Format a single edit as markdown"""
    md = f"### Edit {edit.edit_num}: {edit.section}\n\n"
    md += f"**Priority:** {edit.priority}  \n"
    md += f"**Paperpile Risk:** {edit.paperpile_risk}  \n"
    md += f"**Citations:** {edit.citation_count_before} → {edit.citation_count_after}  \n\n"

    md += f"#### Search For (First 80 chars)\n\n"
    md += f"```\n{edit.search_snippet}\n```\n\n"

    if edit.old_text:
        md += f"#### Old Text\n\n"
        md += f"```\n{edit.old_text}\n```\n\n"

    if edit.new_text:
        md += f"#### Replace With\n\n"
        md += f"```\n{edit.new_text}\n```\n\n"

    md += f"#### Instructions\n\n"
    md += f"{edit.instructions}\n\n"

    # Citation verification
    if edit.citation_count_before != edit.citation_count_after:
        md += f"⚠️ **Citation Count Changed:** {edit.citation_count_before} → {edit.citation_count_after}\n"
        md += f"   Verify Paperpile links remain intact after replacement.\n\n"

    md += "---\n\n"

    return md


def generate_batched_edits(
    current_path: Path,
    target_path: Path,
    report_path: Path,
    output_path: Path
):
    """Main function to generate batched edit plan"""

    # Read input files
    current = current_path.read_text()
    target = target_path.read_text()
    report = report_path.read_text()

    # Extract titles
    current_title_match = re.search(r'^(.+)$', current, re.MULTILINE)
    target_title_match = re.search(r'^#\s+(.+)$', target, re.MULTILINE)

    current_title = current_title_match.group(1).strip() if current_title_match else ""
    target_title = target_title_match.group(1).strip() if target_title_match else ""

    # Parse forbidden terms
    forbidden_terms = parse_forbidden_terms(report)

    # Generate batches
    all_edits = []

    # Batch 1: Title
    if current_title != target_title:
        all_edits.append(Edit(
            batch_num=1,
            batch_name="Title",
            edit_num=1,
            section="Title",
            old_text=current_title,
            new_text=target_title,
            search_snippet=current_title[:80],
            citation_count_before=0,
            citation_count_after=0,
            priority="CRITICAL",
            paperpile_risk="NONE",
            instructions="Replace document title (first line)"
        ))

    # Batch 2: Terminology
    terminology_edits = generate_terminology_batch(current, forbidden_terms)
    all_edits.extend(terminology_edits)

    # Batch 3: Abstract
    current_abstract = extract_section_text(current, "Abstract")
    target_abstract = extract_section_text(target, "Abstract")
    if target_abstract:
        abstract_edits = generate_section_edits(3, "Abstract", "Abstract", current_abstract, target_abstract)
        all_edits.extend(abstract_edits)

    # Batch 4: Introduction (with positioning statement)
    current_intro = extract_section_text(current, "Introduction")
    target_intro = extract_section_text(target, "Introduction")
    positioning_instruction = (
        "⚠️ ADD POSITIONING STATEMENT after paragraph 3:\n"
        "   'Unlike prior global surveys that catalog diversity or distribution, and unlike black-box "
        "classifiers that maximize accuracy, our approach identifies which metagenomic features actually "
        "drive ecosystem discrimination'"
    )
    if target_intro:
        intro_edits = generate_section_edits(
            4, "Introduction", "Introduction",
            current_intro, target_intro,
            special_instructions=positioning_instruction
        )
        all_edits.extend(intro_edits)

    # Batch 5: Results
    current_results = extract_section_text(current, "Results")
    target_results = extract_section_text(target, "Results")
    if target_results:
        results_edits = generate_section_edits(5, "Results", "Results", current_results, target_results)
        all_edits.extend(results_edits)

    # Batch 6: Discussion
    current_discussion = extract_section_text(current, "Discussion")
    target_discussion = extract_section_text(target, "Discussion")
    if target_discussion:
        discussion_edits = generate_section_edits(6, "Discussion", "Discussion", current_discussion, target_discussion)
        all_edits.extend(discussion_edits)

    # Batch 7: Methods
    current_methods = extract_section_text(current, "Methods")
    target_methods = extract_section_text(target, "Methods")
    if target_methods:
        methods_edits = generate_section_edits(7, "Methods", "Methods", current_methods, target_methods)
        all_edits.extend(methods_edits)

    # Generate output markdown
    output_md = generate_output_markdown(all_edits, current_title, target_title)

    # Write output
    output_path.write_text(output_md)
    print(f"✅ Generated {len(all_edits)} edits in 7 batches")
    print(f"📄 Output: {output_path}")

    # Summary statistics
    batch_counts = {}
    for edit in all_edits:
        batch_counts[edit.batch_num] = batch_counts.get(edit.batch_num, 0) + 1

    print("\n📊 Batch Summary:")
    for batch_num in sorted(batch_counts.keys()):
        print(f"   Batch {batch_num}: {batch_counts[batch_num]} edits")


def generate_output_markdown(edits: List[Edit], current_title: str, target_title: str) -> str:
    """Generate complete output markdown document"""

    md = "# Batched Google Doc Edit Plan (Paperpile-Safe)\n\n"
    md += f"**Generated:** `generate_batched_gdoc_edits.py`  \n"
    md += f"**Purpose:** Surgical edits to align Google Doc with v2_final while preserving Paperpile links  \n"
    md += f"**Total Edits:** {len(edits)}  \n\n"

    md += "---\n\n"

    md += "## Overview\n\n"
    md += "This document contains 7 batches of edits organized by risk and complexity:\n\n"
    md += "1. **Batch 1 - Title:** Simple title replacement (0 citations)\n"
    md += "2. **Batch 2 - Terminology:** Global find/replace (Paperpile-safe)\n"
    md += "3. **Batch 3 - Abstract:** Paragraph-level edits (minimal Paperpile risk)\n"
    md += "4. **Batch 4 - Introduction:** Paragraph-level edits + positioning statement\n"
    md += "5. **Batch 5 - Results:** Surgical paragraph edits (citations present)\n"
    md += "6. **Batch 6 - Discussion:** Surgical paragraph edits (citations present)\n"
    md += "7. **Batch 7 - Methods:** Surgical paragraph edits (citations present)\n\n"

    md += "### ⚠️ Paperpile Citation Preservation\n\n"
    md += "- **LOW RISK:** Find/replace and title edits (no citations)\n"
    md += "- **MEDIUM RISK:** Paragraph replacement where citation count stays constant\n"
    md += "- **HIGH RISK:** Paragraph replacement where citations are added\n"
    md += "- **Action:** For HIGH RISK edits, manually verify Paperpile links after paste\n\n"

    md += "---\n\n"

    # Group edits by batch
    batches = {}
    for edit in edits:
        if edit.batch_num not in batches:
            batches[edit.batch_num] = []
        batches[edit.batch_num].append(edit)

    # Generate each batch
    batch_names = {
        1: "Title Replacement",
        2: "Terminology Find/Replace (Paperpile-Safe)",
        3: "Abstract Paragraph Edits",
        4: "Introduction Edits + Positioning Statement",
        5: "Results Paragraph Edits",
        6: "Discussion Paragraph Edits",
        7: "Methods Paragraph Edits"
    }

    for batch_num in sorted(batches.keys()):
        batch_edits = batches[batch_num]
        batch_name = batch_names.get(batch_num, f"Batch {batch_num}")

        md += f"## Batch {batch_num}: {batch_name}\n\n"
        md += f"**Total Edits:** {len(batch_edits)}  \n"

        # Count citations
        total_cites_before = sum(e.citation_count_before for e in batch_edits)
        total_cites_after = sum(e.citation_count_after for e in batch_edits)
        md += f"**Total Citations:** {total_cites_before} → {total_cites_after}  \n"

        # Risk assessment
        max_risk = max((e.paperpile_risk for e in batch_edits), key=lambda x: ['NONE', 'LOW', 'MEDIUM', 'HIGH'].index(x.split()[0]))
        md += f"**Max Paperpile Risk:** {max_risk}  \n\n"

        md += "---\n\n"

        # Add each edit
        for edit in batch_edits:
            md += format_edit_markdown(edit)

    # Add verification checklist
    md += "## Post-Edit Verification Checklist\n\n"
    md += "- [ ] All CRITICAL edits applied\n"
    md += "- [ ] All terminology replacements verified\n"
    md += "- [ ] Positioning statement added to Introduction\n"
    md += "- [ ] Citation counts match expected values\n"
    md += "- [ ] Paperpile links functional (click test)\n"
    md += "- [ ] No forbidden terms remain (Ctrl+F search)\n"
    md += "- [ ] Document formatting preserved\n\n"

    return md


def main():
    parser = argparse.ArgumentParser(
        description="Generate batched Google Doc edits (Paperpile-safe)",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '--current',
        type=Path,
        required=True,
        help="Path to current Google Doc content (.txt)"
    )
    parser.add_argument(
        '--target',
        type=Path,
        required=True,
        help="Path to target manuscript (.md with Paperpile links)"
    )
    parser.add_argument(
        '--report',
        type=Path,
        required=True,
        help="Path to alignment report (.md)"
    )
    parser.add_argument(
        '--output',
        type=Path,
        required=True,
        help="Output path for batched edit plan (.md)"
    )

    args = parser.parse_args()

    # Validate inputs
    if not args.current.exists():
        raise FileNotFoundError(f"Current content not found: {args.current}")
    if not args.target.exists():
        raise FileNotFoundError(f"Target manuscript not found: {args.target}")
    if not args.report.exists():
        raise FileNotFoundError(f"Alignment report not found: {args.report}")

    # Generate edits
    generate_batched_edits(args.current, args.target, args.report, args.output)


if __name__ == '__main__':
    main()
