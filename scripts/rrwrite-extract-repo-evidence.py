#!/usr/bin/env python3
"""
Extract repository evidence from manuscript.

Scans manuscript for factual claims about the repository and generates
verification commands in repo_evidence.md.
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple


class RepositoryEvidenceExtractor:
    """Extract and verify repository claims from manuscript."""

    def __init__(self, repo_path: Path, manuscript_path: Path):
        """
        Initialize extractor.

        Args:
            repo_path: Path to repository
            manuscript_path: Path to manuscript file
        """
        self.repo_path = Path(repo_path).resolve()
        self.manuscript_path = Path(manuscript_path).resolve()
        self.claims = []

    def extract_claims(self) -> List[Dict]:
        """
        Extract numerical and factual claims from manuscript.

        Returns:
            List of claim dictionaries
        """
        content = self.manuscript_path.read_text()

        # Patterns to detect claims
        patterns = [
            # Numbers with units: "372 commits", "12 contributors"
            (r'(\d+(?:,\d+)*)\s+(commits?|contributors?|files?|lines?|directories|classes|functions|tests)', 'count'),
            # File counts: "17 schema files"
            (r'(\d+)\s+(\w+\s+files?)', 'file_count'),
            # Version numbers: "Python 3.9+", "version 1.2.3"
            (r'(Python|version)\s+([\d.]+\+?)', 'version'),
            # Percentages: "95% coverage", "100% validation"
            (r'(\d+)%\s+(\w+)', 'percentage'),
            # Line counts: "4,365 lines"
            (r'([\d,]+)\s+lines', 'lines'),
        ]

        for pattern, claim_type in patterns:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                # Find section context
                section = self._find_section(content, match.start())

                self.claims.append({
                    'text': match.group(0),
                    'type': claim_type,
                    'section': section,
                    'match': match
                })

        return self.claims

    def _find_section(self, content: str, position: int) -> str:
        """Find section heading before position."""
        before = content[:position]
        # Find last markdown heading
        headings = re.findall(r'^#+ (.+)$', before, re.MULTILINE)
        if headings:
            return headings[-1]
        return "Unknown Section"

    def generate_evidence(self, claim: Dict) -> Dict:
        """
        Generate evidence entry for a claim.

        Args:
            claim: Claim dictionary

        Returns:
            Evidence dictionary with verification command
        """
        claim_type = claim['type']
        text = claim['text']

        if claim_type == 'count' and 'commit' in text.lower():
            return self._verify_commits(claim)
        elif claim_type == 'count' and 'contributor' in text.lower():
            return self._verify_contributors(claim)
        elif claim_type == 'file_count' or claim_type == 'count':
            return self._verify_file_count(claim)
        elif claim_type == 'lines':
            return self._verify_line_count(claim)
        else:
            return {
                'claim': text,
                'section': claim['section'],
                'evidence_source': 'Unknown',
                'verification': None,
                'status': '❌ Unverified'
            }

    def _verify_commits(self, claim: Dict) -> Dict:
        """Verify commit count claim."""
        try:
            result = subprocess.run(
                ['git', '-C', str(self.repo_path), 'rev-list', '--all', '--count'],
                capture_output=True,
                text=True,
                timeout=10
            )
            count = result.stdout.strip()

            return {
                'claim': claim['text'],
                'section': claim['section'],
                'evidence_source': 'Git repository metadata',
                'verification': 'git rev-list --all --count',
                'output': count,
                'status': '✅ Verified' if count in claim['text'] else '⚠ Approximate'
            }
        except Exception as e:
            return {
                'claim': claim['text'],
                'section': claim['section'],
                'evidence_source': 'Git repository metadata',
                'verification': 'git rev-list --all --count',
                'output': f'Error: {e}',
                'status': '❌ Unverified'
            }

    def _verify_contributors(self, claim: Dict) -> Dict:
        """Verify contributor count claim."""
        try:
            result = subprocess.run(
                ['git', '-C', str(self.repo_path), 'log', '--all', '--format=%ae'],
                capture_output=True,
                text=True,
                timeout=10
            )
            contributors = len(set(result.stdout.strip().split('\n')))

            return {
                'claim': claim['text'],
                'section': claim['section'],
                'evidence_source': 'Git repository metadata',
                'verification': "git log --all --format='%ae' | sort -u | wc -l",
                'output': str(contributors),
                'status': '✅ Verified' if str(contributors) in claim['text'] else '⚠ Approximate'
            }
        except Exception as e:
            return {
                'claim': claim['text'],
                'section': claim['section'],
                'evidence_source': 'Git repository metadata',
                'verification': "git log --all --format='%ae' | sort -u | wc -l",
                'output': f'Error: {e}',
                'status': '❌ Unverified'
            }

    def _verify_file_count(self, claim: Dict) -> Dict:
        """Verify file count claim."""
        text = claim['text'].lower()

        # Try to infer file pattern
        if 'schema' in text and 'yaml' in text:
            pattern = 'src/**/*.yaml'
        elif 'python' in text or '.py' in text:
            pattern = '**/*.py'
        elif 'test' in text:
            pattern = 'tests/**/*'
        else:
            pattern = '**/*'

        try:
            files = list(self.repo_path.glob(pattern))
            count = len([f for f in files if f.is_file()])

            return {
                'claim': claim['text'],
                'section': claim['section'],
                'evidence_source': f'File pattern: {pattern}',
                'verification': f'find . -path "./{pattern}" -type f | wc -l',
                'output': str(count),
                'status': '✅ Verified' if str(count) in claim['text'] else '⚠ Approximate'
            }
        except Exception as e:
            return {
                'claim': claim['text'],
                'section': claim['section'],
                'evidence_source': f'File pattern: {pattern}',
                'verification': f'find . -path "./{pattern}" -type f | wc -l',
                'output': f'Error: {e}',
                'status': '❌ Unverified'
            }

    def _verify_line_count(self, claim: Dict) -> Dict:
        """Verify line count claim."""
        # Extract number
        match = re.search(r'([\d,]+)', claim['text'])
        if not match:
            return {'claim': claim['text'], 'status': '❌ Unverified'}

        expected = match.group(1).replace(',', '')

        # Try to find likely file
        # This is heuristic-based - may need manual refinement
        return {
            'claim': claim['text'],
            'section': claim['section'],
            'evidence_source': 'Source file (needs manual identification)',
            'verification': 'wc -l <file>',
            'output': 'Manual verification required',
            'status': '⚠ Requires manual verification'
        }

    def generate_markdown(self, evidence_entries: List[Dict]) -> str:
        """
        Generate markdown evidence file.

        Args:
            evidence_entries: List of evidence dictionaries

        Returns:
            Markdown content
        """
        # Get git commit hash
        try:
            result = subprocess.run(
                ['git', '-C', str(self.repo_path), 'rev-parse', '--short', 'HEAD'],
                capture_output=True,
                text=True
            )
            commit_hash = result.stdout.strip()
        except:
            commit_hash = 'unknown'

        # Get remote URL
        try:
            result = subprocess.run(
                ['git', '-C', str(self.repo_path), 'config', '--get', 'remote.origin.url'],
                capture_output=True,
                text=True
            )
            repo_url = result.stdout.strip()
        except:
            repo_url = str(self.repo_path)

        md = f"""# Repository Evidence

**Repository**: {repo_url}
**Commit**: {commit_hash}
**Analyzed**: {datetime.now().strftime('%Y-%m-%d')}
**Purpose**: Evidence for claims about repository contents

---

"""

        for entry in evidence_entries:
            md += f"""## Claim: "{entry['claim']}"

**Section**: {entry['section']}

**Evidence Source**: {entry.get('evidence_source', 'Unknown')}

"""
            if entry.get('verification'):
                md += f"""**Verification**:
```bash
{entry['verification']}
```

"""
            if entry.get('output'):
                md += f"""**Output**:
```
{entry['output']}
```

"""
            md += f"""**Status**: {entry['status']}

---

"""

        return md


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Extract repository evidence from manuscript'
    )
    parser.add_argument(
        '--repo-path',
        type=Path,
        required=True,
        help='Path to repository'
    )
    parser.add_argument(
        '--manuscript',
        type=Path,
        required=True,
        help='Path to manuscript file'
    )
    parser.add_argument(
        '--output',
        type=Path,
        required=True,
        help='Output markdown file'
    )

    args = parser.parse_args()

    # Validate inputs
    if not args.repo_path.exists():
        print(f"Error: Repository not found: {args.repo_path}", file=sys.stderr)
        return 1

    if not args.manuscript.exists():
        print(f"Error: Manuscript not found: {args.manuscript}", file=sys.stderr)
        return 1

    # Extract claims
    print(f"Extracting claims from {args.manuscript}", file=sys.stderr)
    extractor = RepositoryEvidenceExtractor(args.repo_path, args.manuscript)
    claims = extractor.extract_claims()

    print(f"Found {len(claims)} potential claims", file=sys.stderr)

    # Generate evidence
    evidence_entries = []
    for claim in claims:
        evidence = extractor.generate_evidence(claim)
        evidence_entries.append(evidence)

    # Generate markdown
    markdown = extractor.generate_markdown(evidence_entries)

    # Write output
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(markdown)

    print(f"✓ Evidence file written to {args.output}", file=sys.stderr)

    # Summary
    verified = sum(1 for e in evidence_entries if '✅' in e['status'])
    approximate = sum(1 for e in evidence_entries if '⚠' in e['status'])
    unverified = sum(1 for e in evidence_entries if '❌' in e['status'])

    print(f"\nSummary:", file=sys.stderr)
    print(f"  ✅ Verified: {verified}", file=sys.stderr)
    print(f"  ⚠ Approximate: {approximate}", file=sys.stderr)
    print(f"  ❌ Unverified: {unverified}", file=sys.stderr)

    return 0


if __name__ == '__main__':
    sys.exit(main())
