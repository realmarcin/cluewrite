#!/usr/bin/env python3
"""
Generate detailed, section-by-section edit recommendations for Google Doc.

Produces comprehensive edit list with specific line numbers, old text, new text,
and rationale for each change.

Usage:
    python scripts/generate_detailed_edit_list.py --output manuscript/kbaseeco_v2
"""

import argparse
import re
from pathlib import Path
from typing import List, Dict, Tuple
from difflib import SequenceMatcher


class DetailedEditGenerator:
    """Generate detailed edit recommendations with line numbers and specifics."""

    # Forbidden → Approved terminology mappings
    TERMINOLOGY_REPLACEMENTS = {
        "adaptive traits": "ecosystem-discriminative features",
        "adaptive significance": "discriminative power for ecosystem classification",
        "characteristic traits": "characteristic features",
        "essential for survival": "associated with ecosystem context",
        "essential functions": "associated functions",
        "selection": "association",
        "selected for": "associated with",
        "fitness": "discriminative power",
        "necessarily": "likely",
        "proves": "suggests",
        "demonstrates": "shows",
        "explains": "is consistent with",
        "causes": "is associated with",
        "drives": "contributes to"
    }

    # Key structural components to verify
    REQUIRED_COMPONENTS = {
        'abstract': {
            'positioning': 'framework that identifies which metagenomic features drive ecosystem discrimination',
            'hypothesis_framing': 'generate testable hypotheses',
            'avoid_causal': True
        },
        'introduction': {
            'paragraph_4_positioning': 'Unlike prior global surveys.*and unlike black-box classifiers',
            'funnel_structure': True,
            'paragraph_count': 5
        },
        'results': {
            'subsections': [
                'Feature representations',
                'Structure and molecular basis',
                'ecosystem-discriminative feature structure',
                'Validation and Functional Interpretation',
                'Interpreting ecosystem-discriminative',
                'Similarities of predictive features'
            ]
        },
        'discussion': {
            'themes': [
                'Interpretable.*framework',
                'Biological coherence',
                'Ecosystem relationships',
                'classification ambiguity.*hypothesis signal',
                'functional dark matter',
                'Limitations'
            ]
        }
    }

    def __init__(self, gdoc_path: Path, v2_path: Path):
        """Initialize with paths to current and target documents."""
        self.gdoc_text = gdoc_path.read_text(encoding='utf-8')
        self.v2_text = v2_path.read_text(encoding='utf-8')
        self.gdoc_lines = self.gdoc_text.split('\n')
        self.v2_lines = self.v2_text.split('\n')

    def find_line_number(self, text: str, start_line: int = 0) -> int:
        """Find line number containing specific text."""
        for i in range(start_line, len(self.gdoc_lines)):
            if text in self.gdoc_lines[i]:
                return i + 1  # 1-indexed
        return -1

    def find_all_occurrences(self, pattern: str, case_sensitive: bool = False) -> List[Tuple[int, str]]:
        """Find all occurrences of pattern with line numbers."""
        flags = 0 if case_sensitive else re.IGNORECASE
        regex = re.compile(pattern, flags)
        matches = []

        for i, line in enumerate(self.gdoc_lines):
            for match in regex.finditer(line):
                matches.append((i + 1, match.group()))

        return matches

    def generate_terminology_edits(self) -> List[Dict]:
        """Generate specific edit recommendations for terminology."""
        edits = []

        for old_term, new_term in self.TERMINOLOGY_REPLACEMENTS.items():
            occurrences = self.find_all_occurrences(old_term)

            for line_num, matched_text in occurrences:
                context = self.gdoc_lines[line_num - 1]  # 0-indexed

                edits.append({
                    'priority': 'CRITICAL',
                    'category': 'Terminology',
                    'line_number': line_num,
                    'old_text': context,
                    'find': old_term,
                    'replace': new_term,
                    'rationale': f"Adam's Principle 1: Prediction ≠ Adaptation. Remove evolutionary language.",
                    'new_text': context.replace(matched_text, new_term)
                })

        return edits

    def generate_abstract_edits(self) -> List[Dict]:
        """Generate edits for Abstract section."""
        edits = []

        # Find abstract
        abstract_start = -1
        for i, line in enumerate(self.gdoc_lines):
            if re.match(r'^Abstract\s*\d*', line, re.IGNORECASE):
                abstract_start = i + 1
                break

        if abstract_start == -1:
            return edits

        # Extract abstract content (next ~15 lines)
        abstract_lines = self.gdoc_lines[abstract_start:abstract_start + 20]
        abstract_text = '\n'.join(abstract_lines)

        # Check for causal language
        causal_patterns = ['demonstrates', 'proves', 'explains', 'causes', 'drives']
        for pattern in causal_patterns:
            if pattern in abstract_text.lower():
                line_offset = next((i for i, line in enumerate(abstract_lines) if pattern in line.lower()), None)
                if line_offset is not None:
                    line_num = abstract_start + line_offset + 1
                    edits.append({
                        'priority': 'CRITICAL',
                        'category': 'Abstract',
                        'line_number': line_num,
                        'old_text': self.gdoc_lines[line_num - 1],
                        'find': pattern,
                        'replace': self._get_hedged_alternative(pattern),
                        'rationale': 'Abstract should avoid causal claims',
                        'new_text': self.gdoc_lines[line_num - 1].replace(pattern, self._get_hedged_alternative(pattern))
                    })

        return edits

    def generate_introduction_edits(self) -> List[Dict]:
        """Generate edits for Introduction section."""
        edits = []

        # Find introduction
        intro_start = -1
        intro_end = -1
        for i, line in enumerate(self.gdoc_lines):
            if re.match(r'^#?\s*Introduction', line, re.IGNORECASE):
                intro_start = i + 1
                # Find end (next major section)
                for j in range(i + 1, len(self.gdoc_lines)):
                    if re.match(r'^#\s*(Results|Methods)', self.gdoc_lines[j], re.IGNORECASE):
                        intro_end = j
                        break
                break

        if intro_start == -1:
            return edits

        intro_end = intro_end if intro_end != -1 else intro_start + 50
        intro_lines = self.gdoc_lines[intro_start:intro_end]
        intro_text = '\n'.join(intro_lines)

        # Check for positioning statement
        positioning_pattern = r'Unlike.*prior.*and unlike.*black-box'
        if not re.search(positioning_pattern, intro_text, re.IGNORECASE | re.DOTALL):
            # Find paragraph 4 (rough estimate)
            paragraphs = [p for p in intro_text.split('\n\n') if p.strip()]
            if len(paragraphs) >= 4:
                # Insert after paragraph 3
                paragraph_3_end = intro_text.find(paragraphs[3] if len(paragraphs) > 3 else paragraphs[-1])
                insertion_point = intro_start + intro_text[:paragraph_3_end].count('\n') + 5

                edits.append({
                    'priority': 'CRITICAL',
                    'category': 'Introduction',
                    'line_number': insertion_point,
                    'old_text': '[MISSING]',
                    'find': None,
                    'replace': None,
                    'rationale': 'Add positioning statement per Adam\'s requirement',
                    'new_text': 'Unlike prior global surveys that catalog diversity or distribution, and unlike black-box classifiers that maximize accuracy, our approach identifies which metagenomic features actually drive ecosystem discrimination across many environments simultaneously.',
                    'action_type': 'INSERT'
                })

        return edits

    def generate_results_edits(self) -> List[Dict]:
        """Check Results section structure."""
        edits = []

        # Find Results section
        results_start = -1
        for i, line in enumerate(self.gdoc_lines):
            if re.match(r'^#?\s*Results', line, re.IGNORECASE):
                results_start = i
                break

        if results_start == -1:
            edits.append({
                'priority': 'CRITICAL',
                'category': 'Structure',
                'line_number': -1,
                'old_text': '[MISSING SECTION]',
                'find': None,
                'replace': None,
                'rationale': 'Results section not found or improperly formatted',
                'new_text': 'Verify Results section exists and matches v2 structure'
            })
            return edits

        # Check for key subsections
        for subsection in self.REQUIRED_COMPONENTS['results']['subsections']:
            pattern = subsection
            if not re.search(pattern, self.gdoc_text, re.IGNORECASE):
                edits.append({
                    'priority': 'IMPORTANT',
                    'category': 'Results Structure',
                    'line_number': results_start + 1,
                    'old_text': '[MISSING SUBSECTION]',
                    'find': None,
                    'replace': None,
                    'rationale': f'Missing required Results subsection: {subsection}',
                    'new_text': f'Add subsection: {subsection}'
                })

        return edits

    def generate_discussion_edits(self) -> List[Dict]:
        """Check Discussion section themes."""
        edits = []

        # Find Discussion
        discussion_start = -1
        for i, line in enumerate(self.gdoc_lines):
            if re.match(r'^#?\s*Discussion', line, re.IGNORECASE):
                discussion_start = i
                break

        if discussion_start == -1:
            return edits

        discussion_text = '\n'.join(self.gdoc_lines[discussion_start:])

        # Check for required themes
        for theme in self.REQUIRED_COMPONENTS['discussion']['themes']:
            if not re.search(theme, discussion_text, re.IGNORECASE):
                edits.append({
                    'priority': 'IMPORTANT',
                    'category': 'Discussion',
                    'line_number': discussion_start + 1,
                    'old_text': '[MISSING THEME]',
                    'find': None,
                    'replace': None,
                    'rationale': f'Missing required Discussion theme: {theme}',
                    'new_text': f'Add discussion of: {theme}'
                })

        return edits

    def _get_hedged_alternative(self, causal_term: str) -> str:
        """Get hedged alternative for causal term."""
        alternatives = {
            'demonstrates': 'suggests',
            'proves': 'is consistent with',
            'explains': 'is associated with',
            'causes': 'is associated with',
            'drives': 'contributes to',
            'necessarily': 'likely'
        }
        return alternatives.get(causal_term.lower(), 'is associated with')

    def generate_all_edits(self) -> List[Dict]:
        """Generate complete edit list."""
        all_edits = []

        all_edits.extend(self.generate_terminology_edits())
        all_edits.extend(self.generate_abstract_edits())
        all_edits.extend(self.generate_introduction_edits())
        all_edits.extend(self.generate_results_edits())
        all_edits.extend(self.generate_discussion_edits())

        # Sort by priority and line number
        priority_order = {'CRITICAL': 0, 'IMPORTANT': 1, 'OPTIONAL': 2}
        all_edits.sort(key=lambda x: (
            priority_order.get(x['priority'], 3),
            x['line_number'] if x['line_number'] != -1 else 999999
        ))

        return all_edits


def generate_detailed_report(edits: List[Dict], output_path: Path):
    """Generate detailed markdown edit report."""
    report = []

    report.append("# Detailed Section-by-Section Edit Recommendations")
    report.append("")
    report.append("**Purpose:** Line-by-line edit guidance to align Google Doc with v2/Adam's approach")
    report.append("**Generated:** generate_detailed_edit_list.py")
    report.append("")
    report.append("---")
    report.append("")

    # Executive Summary
    critical_edits = [e for e in edits if e['priority'] == 'CRITICAL']
    important_edits = [e for e in edits if e['priority'] == 'IMPORTANT']
    optional_edits = [e for e in edits if e['priority'] == 'OPTIONAL']

    report.append("## Executive Summary")
    report.append("")
    report.append(f"**Total edits:** {len(edits)}")
    report.append(f"- CRITICAL: {len(critical_edits)}")
    report.append(f"- IMPORTANT: {len(important_edits)}")
    report.append(f"- OPTIONAL: {len(optional_edits)}")
    report.append("")
    report.append("---")
    report.append("")

    # Group edits by section
    by_category = {}
    for edit in edits:
        category = edit['category']
        if category not in by_category:
            by_category[category] = []
        by_category[category].append(edit)

    # Generate section-by-section edits
    for category in sorted(by_category.keys()):
        category_edits = by_category[category]
        report.append(f"## {category} Edits ({len(category_edits)} changes)")
        report.append("")

        for i, edit in enumerate(category_edits, 1):
            report.append(f"### Edit #{i} [{edit['priority']}]")
            report.append("")

            if edit['line_number'] != -1:
                report.append(f"**Line:** {edit['line_number']}")
            else:
                report.append(f"**Location:** [Section-level]")

            report.append(f"**Rationale:** {edit['rationale']}")
            report.append("")

            if edit.get('action_type') == 'INSERT':
                report.append("**Action:** INSERT")
                report.append("")
                report.append("```")
                report.append(edit['new_text'])
                report.append("```")
            elif edit['find'] and edit['replace']:
                report.append("**Action:** REPLACE")
                report.append("")
                report.append(f"**Find:** `{edit['find']}`")
                report.append(f"**Replace:** `{edit['replace']}`")
                report.append("")
                report.append("**Context (old):**")
                report.append("```")
                report.append(edit['old_text'][:200])  # Truncate if too long
                report.append("```")
                report.append("")
                report.append("**Context (new):**")
                report.append("```")
                report.append(edit['new_text'][:200])
                report.append("```")
            else:
                report.append(f"**Current:** {edit['old_text']}")
                report.append(f"**Recommended:** {edit['new_text']}")

            report.append("")
            report.append("---")
            report.append("")

    # Implementation guidance
    report.append("## Implementation Steps")
    report.append("")
    report.append("1. **Address CRITICAL edits first** (must fix before submission)")
    report.append("2. **Address IMPORTANT edits** (significantly improve manuscript)")
    report.append("3. **Review OPTIONAL edits** (polish and refinement)")
    report.append("4. **Validate changes** - Re-run assessment script")
    report.append("")
    report.append("### Recommended Tools")
    report.append("")
    report.append("- **Find & Replace:** Use for terminology changes (CRITICAL edits 1-N)")
    report.append("- **Manual editing:** For structural changes (Introduction positioning, etc.)")
    report.append("- **Section comparison:** Use v2_final.md as reference for missing subsections")
    report.append("")
    report.append("---")
    report.append("")
    report.append("**For detailed alignment analysis, see:** `GDOC_ADAM_ALIGNMENT_REPORT.md`")
    report.append("**For v2 vs Adam comparison, see:** `V2_VS_ADAM_COMPARISON.md`")

    output_path.write_text('\n'.join(report), encoding='utf-8')
    print(f"✅ Detailed edit list generated: {output_path}")


def main():
    """Main execution."""
    parser = argparse.ArgumentParser(
        description="Generate detailed section-by-section edit list"
    )
    parser.add_argument(
        '--manuscript-dir',
        type=Path,
        default=Path('manuscript/kbaseeco_v2'),
        help='Manuscript directory'
    )
    parser.add_argument(
        '--output',
        type=Path,
        help='Output path (default: manuscript-dir/DETAILED_EDIT_LIST.md)'
    )

    args = parser.parse_args()

    manuscript_dir = args.manuscript_dir
    output_path = args.output or manuscript_dir / 'DETAILED_EDIT_LIST.md'

    gdoc_path = manuscript_dir / 'current_gdoc_content.txt'
    v2_path = manuscript_dir / 'manuscript_v2_final.md'

    if not gdoc_path.exists():
        print(f"❌ Google Doc content not found: {gdoc_path}")
        return 1

    if not v2_path.exists():
        print(f"❌ v2 manuscript not found: {v2_path}")
        return 1

    print("📝 Generating detailed edit list...")
    print(f"  - Current Google Doc: {gdoc_path}")
    print(f"  - Target (v2): {v2_path}")
    print("")

    generator = DetailedEditGenerator(gdoc_path, v2_path)
    edits = generator.generate_all_edits()

    generate_detailed_report(edits, output_path)

    print(f"\n📊 Summary:")
    print(f"  - Total edits: {len(edits)}")
    print(f"  - CRITICAL: {len([e for e in edits if e['priority'] == 'CRITICAL'])}")
    print(f"  - IMPORTANT: {len([e for e in edits if e['priority'] == 'IMPORTANT'])}")
    print(f"  - Output: {output_path}")
    print("")
    print("✅ Complete!")

    return 0


if __name__ == '__main__':
    exit(main())
