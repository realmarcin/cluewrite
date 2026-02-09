#!/usr/bin/env python3
"""
Root cause tracer for citation errors using 5-level analysis.

Traces citation errors from symptom to root cause with actionable fixes.

Usage:
    python scripts/rrwrite_citation_tracer.py [citation_key] [section] [manuscript_dir]
"""

import re
import csv
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple


class CitationErrorTracer:
    """Traces citation errors back to root cause using 5-level analysis."""

    def __init__(self, manuscript_dir: Path):
        self.manuscript_dir = manuscript_dir
        self.git_available = self._check_git()

    def _check_git(self) -> bool:
        """Check if git is available and repository initialized."""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--git-dir'],
                cwd=self.manuscript_dir.parent,
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False

    def trace_error(
        self,
        citation_key: str,
        section: str,
        symptom: str
    ) -> Dict:
        """
        Trace citation error through 5 levels:
        Level 1: Observe symptom
        Level 2: Find immediate cause
        Level 3: Trace call chain
        Level 4: Find data origin
        Level 5: Identify trigger

        Returns:
            Dict with analysis at each level plus suggested fix
        """
        analysis = {
            'citation_key': citation_key,
            'section': section,
            'symptom': symptom,
            'timestamp': datetime.now().isoformat(),
            'levels': {}
        }

        # Level 1: Symptom
        analysis['levels']['symptom'] = self._level1_symptom(
            citation_key, section, symptom
        )

        # Level 2: Immediate cause
        analysis['levels']['immediate'] = self._level2_immediate(
            citation_key, section
        )

        # Level 3: Usage trace
        analysis['levels']['usage'] = self._level3_usage(
            citation_key, section
        )

        # Level 4: Data origin
        analysis['levels']['origin'] = self._level4_origin(
            citation_key
        )

        # Level 5: Trigger
        analysis['levels']['trigger'] = self._level5_trigger(
            citation_key
        )

        # Generate fix
        analysis['suggested_fix'] = self._suggest_fix(analysis)
        analysis['prevention'] = self._suggest_prevention(analysis)

        return analysis

    def _level1_symptom(
        self,
        citation_key: str,
        section: str,
        symptom: str
    ) -> Dict:
        """Level 1: Observe and document the symptom."""
        return {
            'observation': symptom,
            'location': f'{section}.md',
            'citation': citation_key,
            'detected_at': 'validation',
            'severity': 'error' if 'not found' in symptom.lower() else 'warning'
        }

    def _level2_immediate(
        self,
        citation_key: str,
        section: str
    ) -> Dict:
        """Level 2: Find immediate cause (where is it failing?)."""
        evidence_file = self.manuscript_dir / 'literature_evidence.csv'
        section_file = self.manuscript_dir / f'{section}.md'

        immediate = {
            'evidence_file_exists': evidence_file.exists(),
            'section_file_exists': section_file.exists(),
            'citation_in_evidence': False,
            'citation_in_section': False
        }

        # Check evidence file
        if evidence_file.exists():
            try:
                with open(evidence_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if row.get('citation_key') == citation_key:
                            immediate['citation_in_evidence'] = True
                            immediate['evidence_entry'] = row
                            break
            except Exception as e:
                immediate['evidence_error'] = str(e)

        # Check section file
        if section_file.exists():
            try:
                with open(section_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if f'[{citation_key}]' in content:
                        immediate['citation_in_section'] = True
                        # Extract context (50 chars before/after)
                        matches = list(re.finditer(
                            re.escape(f'[{citation_key}]'),
                            content
                        ))
                        immediate['usage_count'] = len(matches)
                        immediate['first_usage_context'] = content[
                            max(0, matches[0].start() - 50):
                            min(len(content), matches[0].end() + 50)
                        ] if matches else None
            except Exception as e:
                immediate['section_error'] = str(e)

        # Diagnosis
        if not immediate['evidence_file_exists']:
            immediate['diagnosis'] = 'Evidence file missing'
        elif not immediate['citation_in_evidence']:
            immediate['diagnosis'] = 'Citation not in evidence file'
        elif immediate['citation_in_section']:
            immediate['diagnosis'] = 'Citation in section but validation failed'
        else:
            immediate['diagnosis'] = 'Unknown immediate cause'

        return immediate

    def _level3_usage(
        self,
        citation_key: str,
        section: str
    ) -> Dict:
        """Level 3: Trace call chain (how did citation get here?)."""
        usage = {
            'first_mention': None,
            'sections_used': [],
            'total_usages': 0
        }

        # Check all section files
        for section_file in self.manuscript_dir.glob('*.md'):
            if section_file.stem in ['literature', 'outline', 'manuscript']:
                continue

            try:
                with open(section_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    matches = list(re.finditer(
                        re.escape(f'[{citation_key}]'),
                        content
                    ))
                    if matches:
                        usage['sections_used'].append({
                            'section': section_file.stem,
                            'count': len(matches),
                            'first_context': content[
                                max(0, matches[0].start() - 50):
                                min(len(content), matches[0].end() + 50)
                            ]
                        })
                        usage['total_usages'] += len(matches)
            except Exception:
                pass

        # Check audit log if available
        audit_log = self.manuscript_dir / 'citation_audit.jsonl'
        if audit_log.exists():
            try:
                with open(audit_log, 'r', encoding='utf-8') as f:
                    for line in f:
                        entry = json.loads(line)
                        if entry.get('citation') == citation_key:
                            if usage['first_mention'] is None:
                                usage['first_mention'] = entry
                            usage['audit_entries'] = usage.get('audit_entries', 0) + 1
            except Exception as e:
                usage['audit_error'] = str(e)

        return usage

    def _level4_origin(self, citation_key: str) -> Dict:
        """Level 4: Find data origin (where was citation added?)."""
        origin = {
            'evidence_entry_exists': False,
            'bib_entry_exists': False,
            'literature_mention': False
        }

        # Check evidence file for full entry
        evidence_file = self.manuscript_dir / 'literature_evidence.csv'
        if evidence_file.exists():
            try:
                with open(evidence_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if row.get('citation_key') == citation_key:
                            origin['evidence_entry_exists'] = True
                            origin['evidence_data'] = {
                                'doi': row.get('doi', ''),
                                'title': row.get('title', ''),
                                'year': row.get('year', ''),
                                'added_date': row.get('added_date', '')
                            }
                            break
            except Exception as e:
                origin['evidence_error'] = str(e)

        # Check bibliography
        bib_file = self.manuscript_dir / 'literature_citations.bib'
        if bib_file.exists():
            try:
                with open(bib_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if f'@' in content and citation_key in content:
                        origin['bib_entry_exists'] = True
                        # Extract bib entry
                        match = re.search(
                            rf'@\w+\{{{re.escape(citation_key)},(.*?)\n\}}',
                            content,
                            re.DOTALL
                        )
                        if match:
                            origin['bib_entry'] = match.group(0)
            except Exception as e:
                origin['bib_error'] = str(e)

        # Check literature review
        lit_file = self.manuscript_dir / 'literature.md'
        if lit_file.exists():
            try:
                with open(lit_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if f'[{citation_key}]' in content:
                        origin['literature_mention'] = True
            except Exception as e:
                origin['lit_error'] = str(e)

        return origin

    def _level5_trigger(self, citation_key: str) -> Dict:
        """Level 5: Identify trigger (when/why did problem start?)."""
        trigger = {
            'git_history_available': self.git_available,
            'likely_cause': 'unknown'
        }

        if not self.git_available:
            trigger['likely_cause'] = 'No git history available for analysis'
            return trigger

        # Check git history for this citation
        evidence_file = self.manuscript_dir / 'literature_evidence.csv'

        try:
            # Find when evidence file was last modified
            result = subprocess.run(
                ['git', 'log', '--pretty=format:%h|%ai|%s', '--', str(evidence_file)],
                cwd=self.manuscript_dir.parent,
                capture_output=True,
                text=True
            )

            if result.returncode == 0 and result.stdout:
                commits = []
                for line in result.stdout.split('\n')[:5]:  # Last 5 commits
                    if line:
                        hash, date, msg = line.split('|', 2)
                        commits.append({
                            'hash': hash,
                            'date': date,
                            'message': msg
                        })
                trigger['evidence_file_history'] = commits

                # Check if citation was ever in evidence file
                if commits:
                    latest_hash = commits[0]['hash']
                    result = subprocess.run(
                        ['git', 'show', f'{latest_hash}:{evidence_file}'],
                        cwd=self.manuscript_dir.parent,
                        capture_output=True,
                        text=True
                    )
                    if result.returncode == 0 and citation_key in result.stdout:
                        trigger['likely_cause'] = 'Citation was present, then removed or file modified'
                    else:
                        trigger['likely_cause'] = 'Citation never added to evidence file'

        except Exception as e:
            trigger['git_error'] = str(e)

        return trigger

    def _suggest_fix(self, analysis: Dict) -> Dict:
        """Generate specific fix based on analysis."""
        immediate = analysis['levels']['immediate']
        origin = analysis['levels']['origin']

        fix = {
            'steps': [],
            'commands': [],
            'estimated_time': '2-5 minutes'
        }

        # Determine fix based on diagnosis
        if not immediate.get('evidence_file_exists'):
            fix['steps'] = [
                'Create literature_evidence.csv',
                'Run literature search to populate citations',
                'Re-validate section'
            ]
            fix['commands'] = [
                f'python scripts/rrwrite-research-literature.py --target-dir {self.manuscript_dir}',
                f'python scripts/rrwrite-validate-manuscript.py --file {self.manuscript_dir}/{{section}}.md --type section'
            ]

        elif not immediate.get('citation_in_evidence'):
            if origin.get('bib_entry_exists'):
                fix['steps'] = [
                    'Citation exists in .bib but not in evidence.csv',
                    'Add entry to evidence.csv with DOI and quote',
                    'Re-validate section'
                ]
                fix['commands'] = [
                    '# Manually add to literature_evidence.csv:',
                    f'# citation_key,doi,title,year,quote',
                    f'# {analysis["citation_key"]},10.xxxx/xxxx,Paper Title,2024,"Supporting quote"',
                    f'python scripts/rrwrite-validate-manuscript.py --file {self.manuscript_dir}/{{section}}.md --type section'
                ]
            else:
                fix['steps'] = [
                    'Citation not in evidence file or bibliography',
                    'Search for paper and add with DOI',
                    'Re-validate section'
                ]
                fix['commands'] = [
                    f'python scripts/rrwrite-search-literature.py --query "{analysis["citation_key"]} [topic]"',
                    '# Add found paper to literature_evidence.csv',
                    f'python scripts/rrwrite-validate-manuscript.py --file {self.manuscript_dir}/{{section}}.md --type section'
                ]

        else:
            fix['steps'] = [
                'Validation error despite citation in evidence',
                'Check for typo in citation key',
                'Verify evidence.csv format is correct'
            ]
            fix['commands'] = [
                f'grep "{analysis["citation_key"]}" {self.manuscript_dir}/literature_evidence.csv',
                f'# Check for whitespace, case sensitivity, special characters'
            ]

        return fix

    def _suggest_prevention(self, analysis: Dict) -> List[str]:
        """Suggest preventive measures based on error type."""
        immediate = analysis['levels']['immediate']

        prevention = []

        if not immediate.get('citation_in_evidence'):
            prevention.extend([
                'Use defense-in-depth validation: validate citations before using in text',
                'Run validation after adding each citation: python scripts/rrwrite_citation_validator.py',
                'Enable citation audit logging to track usage history',
                'Use rrwrite-research-literature skill to ensure citations in evidence file'
            ])

        if analysis['levels']['usage']['total_usages'] > 1:
            prevention.append(
                f'Citation used {analysis["levels"]["usage"]["total_usages"]} times - '
                'consolidate usage or verify each instance'
            )

        prevention.extend([
            'Validate sections immediately after drafting (verification gate)',
            'Never skip validation before marking section complete',
            'Check evidence file exists before starting to draft'
        ])

        return prevention

    def format_report(self, analysis: Dict) -> str:
        """Format analysis as human-readable report."""
        report = []

        report.append("=" * 70)
        report.append("CITATION ERROR ROOT CAUSE ANALYSIS")
        report.append("=" * 70)
        report.append("")

        # Citation info
        report.append(f"Citation: [{analysis['citation_key']}]")
        report.append(f"Section: {analysis['section']}")
        report.append(f"Analysis Time: {analysis['timestamp']}")
        report.append("")

        # Level 1: Symptom
        report.append("Level 1 - SYMPTOM")
        report.append("-" * 70)
        symptom = analysis['levels']['symptom']
        report.append(f"Observation: {symptom['observation']}")
        report.append(f"Location: {symptom['location']}")
        report.append(f"Severity: {symptom['severity'].upper()}")
        report.append("")

        # Level 2: Immediate Cause
        report.append("Level 2 - IMMEDIATE CAUSE")
        report.append("-" * 70)
        immediate = analysis['levels']['immediate']
        report.append(f"Diagnosis: {immediate['diagnosis']}")
        report.append(f"Evidence file exists: {immediate['evidence_file_exists']}")
        report.append(f"Citation in evidence: {immediate['citation_in_evidence']}")
        report.append(f"Citation in section: {immediate['citation_in_section']}")
        if immediate.get('usage_count'):
            report.append(f"Usage count in section: {immediate['usage_count']}")
        report.append("")

        # Level 3: Usage Trace
        report.append("Level 3 - USAGE TRACE")
        report.append("-" * 70)
        usage = analysis['levels']['usage']
        report.append(f"Total usages: {usage['total_usages']}")
        report.append(f"Sections used in: {len(usage['sections_used'])}")
        for sec in usage['sections_used']:
            report.append(f"  - {sec['section']}: {sec['count']} time(s)")
        report.append("")

        # Level 4: Origin
        report.append("Level 4 - DATA ORIGIN")
        report.append("-" * 70)
        origin = analysis['levels']['origin']
        report.append(f"Evidence entry exists: {origin['evidence_entry_exists']}")
        report.append(f"Bibliography entry exists: {origin['bib_entry_exists']}")
        report.append(f"Mentioned in literature review: {origin['literature_mention']}")
        if origin.get('evidence_data'):
            report.append(f"Evidence data: {origin['evidence_data']}")
        report.append("")

        # Level 5: Trigger
        report.append("Level 5 - TRIGGER")
        report.append("-" * 70)
        trigger = analysis['levels']['trigger']
        report.append(f"Git history available: {trigger['git_history_available']}")
        report.append(f"Likely cause: {trigger['likely_cause']}")
        if trigger.get('evidence_file_history'):
            report.append("Recent evidence file commits:")
            for commit in trigger['evidence_file_history'][:3]:
                report.append(f"  {commit['hash']} ({commit['date'][:10]}): {commit['message']}")
        report.append("")

        # Suggested Fix
        report.append("=" * 70)
        report.append("RECOMMENDED FIX")
        report.append("=" * 70)
        fix = analysis['suggested_fix']
        report.append(f"Estimated time: {fix['estimated_time']}")
        report.append("")
        report.append("Steps:")
        for i, step in enumerate(fix['steps'], 1):
            report.append(f"{i}. {step}")
        report.append("")
        report.append("Commands:")
        for cmd in fix['commands']:
            report.append(f"  {cmd}")
        report.append("")

        # Prevention
        report.append("=" * 70)
        report.append("PREVENTION STRATEGIES")
        report.append("=" * 70)
        for i, prev in enumerate(analysis['prevention'], 1):
            report.append(f"{i}. {prev}")
        report.append("")

        return "\n".join(report)


def main():
    import sys

    if len(sys.argv) < 4:
        print("Usage: python rrwrite_citation_tracer.py <citation_key> <section> <manuscript_dir>")
        print("Example: python rrwrite_citation_tracer.py smith2024 methods manuscript/")
        sys.exit(1)

    citation_key = sys.argv[1]
    section = sys.argv[2]
    manuscript_dir = Path(sys.argv[3])

    if not manuscript_dir.exists():
        print(f"Error: Manuscript directory not found: {manuscript_dir}")
        sys.exit(1)

    tracer = CitationErrorTracer(manuscript_dir)
    analysis = tracer.trace_error(
        citation_key,
        section,
        f"Citation [{citation_key}] not found in literature_evidence.csv"
    )

    print(tracer.format_report(analysis))

    # Save analysis to file
    output_file = manuscript_dir / f'citation_trace_{citation_key}_{section}.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, indent=2)

    print(f"\nFull analysis saved to: {output_file}")


if __name__ == '__main__':
    main()
