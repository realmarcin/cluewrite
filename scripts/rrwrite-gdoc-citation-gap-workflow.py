#!/usr/bin/env python3
"""
Google Docs citation gap analysis workflow orchestrator.

Chains all steps of the citation gap analysis:
1. Download Google Doc → DOCX
2. Extract citations → JSON
3. Execute multi-tier literature search → JSON
4. Analyze gaps → JSON
5. Generate report → MD + JSON

Usage:
    python scripts/rrwrite-gdoc-citation-gap-workflow.py \
        --document-id 1ABC...XYZ \
        --output-dir manuscript/citation_gap_analysis \
        --search-tiers 1,2,3 \
        --credentials credentials.json
"""

import argparse
import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Dict


class CitationGapWorkflow:
    """Orchestrate complete citation gap analysis workflow"""

    def __init__(
        self,
        document_id: str,
        output_dir: Path,
        credentials: Path,
        search_tiers: List[int]
    ):
        """
        Initialize workflow.

        Args:
            document_id: Google Doc ID
            output_dir: Output directory
            credentials: Google API credentials
            search_tiers: List of search tiers to execute (1, 2, 3)
        """
        self.document_id = document_id
        self.output_dir = Path(output_dir)
        self.credentials = credentials
        self.search_tiers = search_tiers
        self.scripts_dir = Path(__file__).parent

        # Output files
        self.docx_file = self.output_dir / 'manuscript.docx'
        self.citations_file = self.output_dir / 'extracted_citations.json'
        self.gap_analysis_file = self.output_dir / 'gap_analysis.json'
        self.search_results_files = []

        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run_command(self, cmd: List[str], step_name: str) -> int:
        """Run subprocess command with error handling"""
        print(f"\n{'='*60}")
        print(f"▶ {step_name}")
        print(f"{'='*60}")
        print(f"Command: {' '.join(str(c) for c in cmd)}\n")

        try:
            result = subprocess.run(
                cmd,
                capture_output=False,  # Show output in real-time
                text=True
            )

            if result.returncode != 0:
                print(f"\n❌ {step_name} failed with exit code {result.returncode}")
                return result.returncode

            print(f"\n✅ {step_name} completed successfully")
            return 0

        except Exception as e:
            print(f"\n❌ {step_name} failed: {e}")
            return 1

    def step1_download_gdoc(self) -> int:
        """Step 1: Download Google Doc as DOCX"""
        cmd = [
            'python3',
            str(self.scripts_dir / 'rrwrite-download-gdoc.py'),
            '--document-id', self.document_id,
            '--output', str(self.docx_file),
            '--credentials', str(self.credentials),
            '--save-metadata',
            '--verbose'
        ]

        return self.run_command(cmd, "Step 1: Download Google Doc")

    def step2_extract_citations(self) -> int:
        """Step 2: Extract citations from DOCX"""
        cmd = [
            'python3',
            str(self.scripts_dir / 'rrwrite-extract-gdoc-citations.py'),
            '--docx', str(self.docx_file),
            '--output', str(self.citations_file),
            '--stats',
            '--verbose'
        ]

        return self.run_command(cmd, "Step 2: Extract Citations")

    def step3_literature_search(self) -> int:
        """Step 3: Execute multi-tier literature search"""

        # Define search queries for each tier
        tier_queries = {
            1: [
                "automated manuscript generation from code repositories",
                "computational notebook scientific publishing",
                "research code to documentation"
            ],
            2: [
                "Jupyter notebook academic publishing",
                "repository analysis automated documentation",
                "claim verification scientific literature",
                "Quarto scientific publishing",
                "literate programming research"
            ],
            3: [
                "provenance tracking research data",
                "FAIR principles software research",
                "reproducibility computational science",
                "software citation academic research"
            ]
        }

        # Execute searches for selected tiers
        for tier in sorted(self.search_tiers):
            if tier not in tier_queries:
                print(f"⚠️  Warning: Unknown tier {tier}, skipping")
                continue

            queries = tier_queries[tier]
            tier_results = []

            print(f"\n{'='*60}")
            print(f"▶ Step 3.{tier}: Tier {tier} Literature Search")
            print(f"{'='*60}")

            for i, query in enumerate(queries, 1):
                print(f"\n  Query {i}/{len(queries)}: {query}")

                # Determine result count based on tier
                max_results = 20 if tier == 1 else 15 if tier == 2 else 10

                query_output = self.output_dir / f'tier{tier}_query{i}_results.json'

                cmd = [
                    'python3',
                    str(self.scripts_dir / 'rrwrite-search-literature.py'),
                    query,
                    '--max-results', str(max_results),
                    '--output', str(query_output)
                ]

                ret = self.run_command(cmd, f"  Query {i}: {query[:50]}...")

                if ret != 0:
                    print(f"  ⚠️  Query failed, continuing...")
                    continue

                tier_results.append(query_output)

            # Merge tier results
            if tier_results:
                merged_output = self.output_dir / f'tier{tier}_merged.json'
                self._merge_search_results(tier_results, merged_output)
                self.search_results_files.append(merged_output)

        if not self.search_results_files:
            print("\n❌ No search results generated")
            return 1

        print(f"\n✅ Literature search completed: {len(self.search_results_files)} tier files")
        return 0

    def _merge_search_results(self, input_files: List[Path], output_file: Path):
        """Merge multiple search result files, deduplicating by DOI"""
        all_papers = []
        seen_dois = set()

        for input_file in input_files:
            if not input_file.exists():
                continue

            with open(input_file) as f:
                data = json.load(f)

            for paper in data.get('papers', []):
                doi = paper.get('doi', '').lower()

                if doi and doi not in seen_dois:
                    all_papers.append(paper)
                    seen_dois.add(doi)
                elif not doi:
                    # No DOI - check title
                    title = paper.get('title', '').lower()
                    if title not in [p.get('title', '').lower() for p in all_papers]:
                        all_papers.append(paper)

        # Write merged results
        output_data = {
            'merged_at': datetime.now().isoformat(),
            'source_files': [str(f) for f in input_files],
            'total_papers': len(all_papers),
            'papers': all_papers
        }

        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2)

        print(f"  ✓ Merged {len(all_papers)} unique papers → {output_file}")

    def step4_gap_analysis(self) -> int:
        """Step 4: Analyze citation gaps"""
        cmd = [
            'python3',
            str(self.scripts_dir / 'rrwrite-citation-gap-analyzer.py'),
            '--manuscript-citations', str(self.citations_file),
            '--search-results', *[str(f) for f in self.search_results_files],
            '--output', str(self.gap_analysis_file),
            '--similarity-threshold', '0.70',
            '--verbose'
        ]

        return self.run_command(cmd, "Step 4: Gap Analysis")

    def step5_generate_report(self) -> int:
        """Step 5: Generate gap analysis reports"""
        cmd = [
            'python3',
            str(self.scripts_dir / 'rrwrite-generate-gap-report.py'),
            '--gap-analysis', str(self.gap_analysis_file),
            '--output-dir', str(self.output_dir),
            '--verbose'
        ]

        return self.run_command(cmd, "Step 5: Generate Reports")

    def run(self) -> int:
        """Execute complete workflow"""
        print(f"\n{'#'*60}")
        print(f"# Citation Gap Analysis Workflow")
        print(f"{'#'*60}")
        print(f"Document ID: {self.document_id}")
        print(f"Output Dir: {self.output_dir}")
        print(f"Search Tiers: {self.search_tiers}")
        print(f"{'#'*60}\n")

        start_time = datetime.now()

        # Step 1: Download
        ret = self.step1_download_gdoc()
        if ret != 0:
            return ret

        # Step 2: Extract citations
        ret = self.step2_extract_citations()
        if ret != 0:
            return ret

        # Step 3: Literature search
        ret = self.step3_literature_search()
        if ret != 0:
            return ret

        # Step 4: Gap analysis
        ret = self.step4_gap_analysis()
        if ret != 0:
            return ret

        # Step 5: Generate reports
        ret = self.step5_generate_report()
        if ret != 0:
            return ret

        # Summary
        elapsed = (datetime.now() - start_time).total_seconds()

        print(f"\n{'#'*60}")
        print(f"# Workflow Complete!")
        print(f"{'#'*60}")
        print(f"Total time: {elapsed:.1f} seconds ({elapsed/60:.1f} minutes)")
        print(f"\nOutput files:")
        print(f"  - DOCX: {self.docx_file}")
        print(f"  - Citations: {self.citations_file}")
        print(f"  - Gap Analysis: {self.gap_analysis_file}")
        print(f"  - Markdown Report: {self.output_dir / 'citation_gap_report.md'}")
        print(f"  - JSON Report: {self.output_dir / 'citation_gap_report.json'}")
        print(f"{'#'*60}\n")

        return 0


def main():
    parser = argparse.ArgumentParser(
        description='Google Docs citation gap analysis workflow',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        '--document-id',
        required=True,
        help='Google Doc document ID (from URL)'
    )
    parser.add_argument(
        '--output-dir',
        type=Path,
        required=True,
        help='Output directory for all results'
    )
    parser.add_argument(
        '--credentials',
        type=Path,
        default=Path('credentials.json'),
        help='Google API credentials file (default: credentials.json)'
    )
    parser.add_argument(
        '--search-tiers',
        type=str,
        default='1,2,3',
        help='Comma-separated list of search tiers to execute (default: 1,2,3)'
    )

    args = parser.parse_args()

    # Parse search tiers
    try:
        search_tiers = [int(t.strip()) for t in args.search_tiers.split(',')]
    except ValueError:
        print(f"❌ Error: Invalid search tiers format: {args.search_tiers}", file=sys.stderr)
        print("Use comma-separated integers, e.g., '1,2,3'", file=sys.stderr)
        return 1

    # Validate credentials
    if not args.credentials.exists():
        print(f"❌ Error: Credentials file not found: {args.credentials}", file=sys.stderr)
        return 1

    try:
        workflow = CitationGapWorkflow(
            document_id=args.document_id,
            output_dir=args.output_dir,
            credentials=args.credentials,
            search_tiers=search_tiers
        )

        return workflow.run()

    except Exception as e:
        print(f"\n❌ Workflow failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
