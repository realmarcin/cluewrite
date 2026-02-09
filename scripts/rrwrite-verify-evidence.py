#!/usr/bin/env python3
"""
Verify evidence claims in repo_evidence.md.

Parses verification commands from evidence file, executes them,
and compares outputs to recorded values.
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Tuple


class EvidenceVerifier:
    """Verify repository evidence claims."""

    def __init__(self, repo_path: Path, evidence_file: Path):
        """
        Initialize verifier.

        Args:
            repo_path: Path to repository
            evidence_file: Path to repo_evidence.md
        """
        self.repo_path = Path(repo_path).resolve()
        self.evidence_file = Path(evidence_file).resolve()
        self.claims = []

    def parse_evidence_file(self) -> List[Dict]:
        """
        Parse repo_evidence.md and extract claims with verification info.

        Returns:
            List of claim dictionaries
        """
        content = self.evidence_file.read_text()

        # Split into claim sections
        claim_sections = re.split(r'\n---\n', content)

        claims = []

        for section in claim_sections:
            if not section.strip() or section.startswith('#'):
                continue

            # Extract claim text
            claim_match = re.search(r'## Claim: "([^"]+)"', section)
            if not claim_match:
                continue

            claim_text = claim_match.group(1)

            # Extract section
            section_match = re.search(r'\*\*Section\*\*: (.+)', section)
            section_name = section_match.group(1) if section_match else "Unknown"

            # Extract verification command
            verification_match = re.search(
                r'\*\*Verification\*\*:\s*```bash\s*(.+?)\s*```',
                section,
                re.DOTALL
            )
            verification_cmd = verification_match.group(1).strip() if verification_match else None

            # Extract expected output
            output_match = re.search(
                r'\*\*Output\*\*:\s*```\s*(.+?)\s*```',
                section,
                re.DOTALL
            )
            expected_output = output_match.group(1).strip() if output_match else None

            # Extract status
            status_match = re.search(r'\*\*Status\*\*: (.+)', section)
            status = status_match.group(1).strip() if status_match else "Unknown"

            claims.append({
                'claim': claim_text,
                'section': section_name,
                'verification_cmd': verification_cmd,
                'expected_output': expected_output,
                'status': status
            })

        return claims

    def verify_claim(self, claim: Dict) -> Dict:
        """
        Verify a single claim by running its verification command.

        Args:
            claim: Claim dictionary

        Returns:
            Verification result dictionary
        """
        if not claim['verification_cmd']:
            return {
                'claim': claim['claim'],
                'status': 'skip',
                'reason': 'No verification command',
                'expected': claim['expected_output'],
                'actual': None,
                'match': False
            }

        if 'Manual verification required' in claim.get('expected_output', ''):
            return {
                'claim': claim['claim'],
                'status': 'skip',
                'reason': 'Manual verification required',
                'expected': claim['expected_output'],
                'actual': None,
                'match': False
            }

        # Execute verification command
        try:
            result = subprocess.run(
                claim['verification_cmd'],
                shell=True,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=30
            )

            actual_output = result.stdout.strip()

            # Compare outputs
            expected = claim['expected_output'] or ''
            match = actual_output == expected

            # For numerical comparisons, also check approximate match
            approximate_match = False
            if not match and expected and actual_output:
                try:
                    # Extract numbers from outputs
                    expected_num = int(re.sub(r'[^\d]', '', expected))
                    actual_num = int(re.sub(r'[^\d]', '', actual_output))

                    # Within 10% is approximate match
                    diff_pct = abs(expected_num - actual_num) / expected_num * 100
                    approximate_match = diff_pct <= 10
                except (ValueError, ZeroDivisionError):
                    pass

            return {
                'claim': claim['claim'],
                'status': 'verified' if match else ('approximate' if approximate_match else 'mismatch'),
                'reason': None,
                'expected': expected,
                'actual': actual_output,
                'match': match or approximate_match
            }

        except subprocess.TimeoutExpired:
            return {
                'claim': claim['claim'],
                'status': 'error',
                'reason': 'Command timeout (>30s)',
                'expected': claim['expected_output'],
                'actual': None,
                'match': False
            }
        except Exception as e:
            return {
                'claim': claim['claim'],
                'status': 'error',
                'reason': str(e),
                'expected': claim['expected_output'],
                'actual': None,
                'match': False
            }

    def verify_all(self) -> Tuple[List[Dict], Dict]:
        """
        Verify all claims in evidence file.

        Returns:
            Tuple of (results list, summary dict)
        """
        claims = self.parse_evidence_file()

        print(f"Found {len(claims)} claims to verify\n", file=sys.stderr)

        results = []
        for i, claim in enumerate(claims, 1):
            print(f"[{i}/{len(claims)}] Verifying: {claim['claim'][:50]}...", file=sys.stderr)
            result = self.verify_claim(claim)
            results.append(result)

        # Generate summary
        summary = {
            'total': len(results),
            'verified': sum(1 for r in results if r['status'] == 'verified'),
            'approximate': sum(1 for r in results if r['status'] == 'approximate'),
            'mismatch': sum(1 for r in results if r['status'] == 'mismatch'),
            'error': sum(1 for r in results if r['status'] == 'error'),
            'skipped': sum(1 for r in results if r['status'] == 'skip')
        }

        return results, summary

    def generate_report(self, results: List[Dict], summary: Dict) -> str:
        """
        Generate markdown verification report.

        Args:
            results: List of verification results
            summary: Summary statistics

        Returns:
            Markdown report
        """
        from datetime import datetime

        # Get current commit
        try:
            result = subprocess.run(
                ['git', '-C', str(self.repo_path), 'rev-parse', '--short', 'HEAD'],
                capture_output=True,
                text=True
            )
            current_commit = result.stdout.strip()
        except:
            current_commit = 'unknown'

        md = f"""# Evidence Verification Report

**Repository**: {self.repo_path}
**Commit**: {current_commit}
**Verified**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Evidence File**: {self.evidence_file.name}

---

## Summary

- **Total Claims**: {summary['total']}
- **✅ Verified**: {summary['verified']} (exact match)
- **⚠ Approximate**: {summary['approximate']} (within 10%)
- **❌ Mismatch**: {summary['mismatch']} (needs update)
- **⚠ Error**: {summary['error']} (verification failed)
- **➖ Skipped**: {summary['skipped']} (manual verification)

**Verification Rate**: {(summary['verified'] + summary['approximate']) / summary['total'] * 100:.1f}%

---

## Detailed Results

"""

        # Group by status
        for status_type, icon, description in [
            ('verified', '✅', 'Verified (Exact Match)'),
            ('approximate', '⚠️', 'Approximate Match (Within 10%)'),
            ('mismatch', '❌', 'Mismatch (Needs Update)'),
            ('error', '⚠️', 'Verification Error'),
            ('skip', '➖', 'Skipped (Manual Verification)')
        ]:
            status_results = [r for r in results if r['status'] == status_type]

            if not status_results:
                continue

            md += f"### {icon} {description} ({len(status_results)})\n\n"

            for result in status_results:
                md += f"**Claim**: \"{result['claim']}\"\n\n"

                if result['reason']:
                    md += f"**Reason**: {result['reason']}\n\n"
                elif result['expected'] and result['actual']:
                    md += f"- **Expected**: `{result['expected']}`\n"
                    md += f"- **Actual**: `{result['actual']}`\n\n"

                md += "---\n\n"

        # Recommendations
        md += "## Recommendations\n\n"

        if summary['mismatch'] > 0:
            md += f"1. **Update {summary['mismatch']} mismatched claims** in manuscript\n"
            md += "   - Run extraction again after updates\n"
            md += "   - Or manually update evidence file with current values\n\n"

        if summary['error'] > 0:
            md += f"2. **Review {summary['error']} verification errors**\n"
            md += "   - Check verification commands are correct\n"
            md += "   - Ensure repository is accessible\n\n"

        if summary['skipped'] > 0:
            md += f"3. **Manually verify {summary['skipped']} claims**\n"
            md += "   - Identify specific files for line count claims\n"
            md += "   - Add verification commands to evidence file\n\n"

        if summary['verified'] + summary['approximate'] == summary['total']:
            md += "✅ **All claims verified!** Evidence file is up to date.\n"

        return md


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Verify evidence claims in repo_evidence.md'
    )
    parser.add_argument(
        '--repo-path',
        type=Path,
        required=True,
        help='Path to repository'
    )
    parser.add_argument(
        '--evidence',
        type=Path,
        required=True,
        help='Path to repo_evidence.md'
    )
    parser.add_argument(
        '--output',
        type=Path,
        help='Output report file (default: print to stdout)'
    )

    args = parser.parse_args()

    # Validate inputs
    if not args.repo_path.exists():
        print(f"Error: Repository not found: {args.repo_path}", file=sys.stderr)
        return 1

    if not args.evidence.exists():
        print(f"Error: Evidence file not found: {args.evidence}", file=sys.stderr)
        return 1

    # Verify evidence
    verifier = EvidenceVerifier(args.repo_path, args.evidence)
    results, summary = verifier.verify_all()

    # Generate report
    report = verifier.generate_report(results, summary)

    # Output
    if args.output:
        args.output.write_text(report)
        print(f"\n✓ Verification report written to {args.output}", file=sys.stderr)
    else:
        print(report)

    # Print summary to stderr
    print(f"\nSummary:", file=sys.stderr)
    print(f"  ✅ Verified: {summary['verified']}", file=sys.stderr)
    print(f"  ⚠ Approximate: {summary['approximate']}", file=sys.stderr)
    print(f"  ❌ Mismatch: {summary['mismatch']}", file=sys.stderr)
    print(f"  ⚠ Error: {summary['error']}", file=sys.stderr)
    print(f"  ➖ Skipped: {summary['skipped']}", file=sys.stderr)

    # Exit code: 0 if all verified, 1 if mismatches
    return 0 if summary['mismatch'] == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
