#!/usr/bin/env python3
"""
Citation gap analysis with semantic similarity and prioritization.

Performs 4-layer analysis to identify missing citations:
1. DOI/Title exact matching
2. Semantic overlap detection (TF-IDF similarity)
3. Citation type categorization
4. Citation network analysis (impact-based prioritization)

Usage:
    python scripts/rrwrite-citation-gap-analyzer.py \
        --manuscript-citations extracted_citations.json \
        --search-results tier1_results.json tier2_results.json \
        --output gap_analysis.json \
        --similarity-threshold 0.70
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Set, Tuple
from collections import defaultdict

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("Warning: scikit-learn not installed. Semantic similarity disabled.", file=sys.stderr)
    print("Install with: pip install scikit-learn", file=sys.stderr)


class CitationGapAnalyzer:
    """Analyze missing citations with semantic similarity"""

    def __init__(self, similarity_threshold: float = 0.70, manuscript_keywords: Dict = None):
        """
        Initialize analyzer.

        Args:
            similarity_threshold: TF-IDF similarity threshold (0-1)
            manuscript_keywords: Keywords extracted from manuscript (tools, methods, domain terms)
        """
        self.similarity_threshold = similarity_threshold
        self.current_year = datetime.now().year
        self.manuscript_keywords = manuscript_keywords or {
            'tools_databases': [],
            'methods': [],
            'domain_terms': []
        }

        # Irrelevant tools (common tools NOT used in manuscript)
        self.irrelevant_tools = set([
            'phyloseq', 'vsearch', 'picrust', 'fasttree', 'qiime',
            'mothur', 'usearch', 'metaphlan', 'humann', 'kraken'
        ])

    def load_manuscript_citations(self, citations_file: Path) -> Dict:
        """Load citations extracted from manuscript"""
        with open(citations_file) as f:
            data = json.load(f)

        # Extract DOIs and titles from citations
        dois = set()
        titles = set()
        citation_keys = set()

        for cit in data.get('citations', []):
            if cit.get('doi'):
                dois.add(cit['doi'].lower())
            if cit.get('title'):
                titles.add(cit['title'].lower())
            if cit.get('citation_key'):
                citation_keys.add(cit['citation_key'])

        return {
            'dois': dois,
            'titles': titles,
            'citation_keys': citation_keys,
            'raw': data.get('citations', [])
        }

    def load_search_results(self, search_files: List[Path]) -> List[Dict]:
        """Load and merge search results from multiple files"""
        all_papers = []
        seen_dois = set()

        for search_file in search_files:
            with open(search_file) as f:
                data = json.load(f)

            papers = data.get('papers', [])

            # Deduplicate by DOI
            for paper in papers:
                doi = paper.get('doi', '').lower()
                if doi and doi not in seen_dois:
                    all_papers.append(paper)
                    seen_dois.add(doi)
                elif not doi:
                    # Papers without DOI - deduplicate by title
                    title = paper.get('title', '').lower()
                    if title not in [p.get('title', '').lower() for p in all_papers]:
                        all_papers.append(paper)

        return all_papers

    def exact_match_gaps(
        self,
        manuscript_cites: Dict,
        search_results: List[Dict]
    ) -> List[Dict]:
        """Find papers in search results NOT in manuscript (Layer 1)"""
        gaps = []

        for paper in search_results:
            doi = paper.get('doi', '').lower()
            title = paper.get('title', '').lower()

            # Check if already cited
            is_cited = False

            if doi and doi in manuscript_cites['dois']:
                is_cited = True
            elif title and title in manuscript_cites['titles']:
                is_cited = True

            if not is_cited:
                gaps.append({
                    **paper,
                    'gap_type': 'exact_match',
                    'match_score': 1.0
                })

        return gaps

    def semantic_overlap_gaps(
        self,
        manuscript_cites: Dict,
        gap_papers: List[Dict]
    ) -> List[Dict]:
        """Detect semantic overlap using TF-IDF similarity (Layer 2)"""
        if not SKLEARN_AVAILABLE:
            # Fall back to keyword matching
            return self._keyword_overlap_fallback(gap_papers)

        # Build corpus: manuscript citation abstracts + gap paper abstracts
        manuscript_abstracts = [
            cit.get('abstract', '') for cit in manuscript_cites['raw']
            if cit.get('abstract')
        ]

        gap_abstracts = [
            paper.get('abstract', '') for paper in gap_papers
            if paper.get('abstract')
        ]

        if not manuscript_abstracts or not gap_abstracts:
            return gap_papers  # No abstracts to compare

        # TF-IDF vectorization
        vectorizer = TfidfVectorizer(
            max_features=500,
            stop_words='english',
            ngram_range=(1, 2)
        )

        # Fit on all abstracts
        all_abstracts = manuscript_abstracts + gap_abstracts
        tfidf_matrix = vectorizer.fit_transform(all_abstracts)

        # Split back into manuscript and gap matrices
        manuscript_matrix = tfidf_matrix[:len(manuscript_abstracts)]
        gap_matrix = tfidf_matrix[len(manuscript_abstracts):]

        # Compute similarity for each gap paper
        enriched_gaps = []

        for i, paper in enumerate(gap_papers):
            if i >= gap_matrix.shape[0]:
                continue

            # Compute max similarity to any manuscript citation
            similarities = cosine_similarity(gap_matrix[i:i+1], manuscript_matrix)
            max_similarity = float(similarities.max()) if similarities.size > 0 else 0.0

            enriched_gaps.append({
                **paper,
                'semantic_similarity': max_similarity,
                'has_semantic_overlap': max_similarity >= self.similarity_threshold
            })

        return enriched_gaps

    def _keyword_overlap_fallback(self, gap_papers: List[Dict]) -> List[Dict]:
        """Fallback keyword matching when scikit-learn unavailable"""
        # Simple keyword-based similarity
        for paper in gap_papers:
            paper['semantic_similarity'] = 0.0
            paper['has_semantic_overlap'] = False

        return gap_papers

    def categorize_citation_type(self, paper: Dict) -> str:
        """Infer citation type from paper metadata (Layer 3)"""
        title = (paper.get('title') or '').lower()
        abstract = (paper.get('abstract') or '').lower()
        year = paper.get('year', 0)

        if isinstance(year, str):
            try:
                year = int(year)
            except (ValueError, TypeError):
                year = 0

        # Tool/software indicators
        if any(word in title for word in [
            'software', 'tool', 'pipeline', 'package', 'algorithm',
            'framework', 'library', 'platform', 'system'
        ]):
            return 'tool'

        # Review indicators
        if any(word in title for word in [
            'review', 'survey', 'overview', 'perspectives',
            'state of the art', 'recent advances'
        ]):
            return 'review'

        # Method/protocol indicators
        if any(word in title for word in [
            'protocol', 'method', 'procedure', 'workflow',
            'approach', 'technique'
        ]):
            return 'method'

        # Benchmark/comparison indicators
        if any(word in title for word in [
            'benchmark', 'comparison', 'evaluation',
            'comparative', 'assessment'
        ]):
            return 'benchmark'

        # Dataset/database indicators
        if any(word in title for word in [
            'database', 'dataset', 'repository',
            'collection', 'resource', 'atlas'
        ]):
            return 'dataset'

        # Recent research (< 3 years)
        if year >= self.current_year - 3:
            return 'recent'

        # Seminal (older + highly cited)
        citations = paper.get('citations', 0) or paper.get('citationCount', 0)
        if year < self.current_year - 10 and citations > 500:
            return 'seminal'

        return 'research'

    def check_workflow_relevance(self, paper: Dict) -> Tuple[int, str]:
        """
        Check if paper is about tools/methods used in manuscript workflow.

        Returns:
            (relevance_score, relevance_reason)
            - 5: Core method/tool used in manuscript (SHAP, CatBoost, KBase)
            - 3: Related method in same category
            - 1: Domain-relevant but different tool
            - 0: Generic or irrelevant
            - -5: Explicitly about tools NOT used
        """
        title = (paper.get('title') or '').lower()
        abstract = (paper.get('abstract') or '').lower()
        text = f"{title} {abstract}"

        # Check for irrelevant tools (heavy penalty)
        for irrelevant in self.irrelevant_tools:
            if irrelevant.lower() in title:
                return (-5, f"About {irrelevant} (not used in manuscript)")

        # Check for tools/databases actually used
        tools_used = self.manuscript_keywords.get('tools_databases', [])
        for tool in tools_used:
            if tool.lower() in title or tool.lower() in text[:500]:
                return (5, f"About {tool} (used in manuscript)")

        # Check for methods actually used
        methods_used = self.manuscript_keywords.get('methods', [])
        for method in methods_used:
            if method.lower() in title:
                return (5, f"About {method} (used in manuscript)")
            elif method.lower() in text[:500]:
                return (3, f"Mentions {method} (related method)")

        # Check for domain relevance
        domain_terms = self.manuscript_keywords.get('domain_terms', [])
        domain_matches = sum(1 for term in domain_terms if term.lower() in text)
        if domain_matches >= 3:
            return (1, f"Domain-relevant ({domain_matches} matching terms)")

        return (0, "Generic relevance")

    def prioritize_gaps(self, gaps: List[Dict]) -> List[Dict]:
        """Assign priority based on workflow relevance, citation impact, and semantic similarity (Layer 4)"""
        for paper in gaps:
            citations = paper.get('citations', 0) or paper.get('citationCount', 0)
            year = paper.get('year', 0)
            semantic_similarity = paper.get('semantic_similarity', 0.0)
            cit_type = paper.get('citation_type', 'unknown')

            if isinstance(year, str):
                try:
                    year = int(year)
                except (ValueError, TypeError):
                    year = 0

            # Check workflow relevance (NEW - most important factor)
            workflow_score, workflow_reason = self.check_workflow_relevance(paper)
            paper['workflow_relevance'] = workflow_score
            paper['workflow_reason'] = workflow_reason

            # Calculate priority score
            score = 0

            # Workflow relevance (HIGHEST WEIGHT)
            if workflow_score == 5:
                score += 6  # Core method/tool used
            elif workflow_score == 3:
                score += 3  # Related method
            elif workflow_score == 1:
                score += 1  # Domain-relevant
            elif workflow_score == -5:
                score -= 10  # Explicitly irrelevant (will be filtered)

            # Citation count (normalized, REDUCED WEIGHT)
            if citations > 1000:
                score += 3
            elif citations > 100:
                score += 2
            elif citations > 50:
                score += 1

            # Recency (within 2 years)
            if year >= self.current_year - 2:
                score += 1  # Reduced from 2

            # Semantic overlap
            if semantic_similarity >= 0.80:
                score += 3
            elif semantic_similarity >= 0.70:
                score += 2

            # Citation type relevance (only for workflow-relevant papers)
            if workflow_score >= 1:
                if cit_type in ['method', 'tool']:
                    score += 2
                elif cit_type in ['benchmark', 'review']:
                    score += 1

            # Assign priority based on workflow-aware scoring
            if score >= 8 or workflow_score == 5:
                priority = 'critical'  # Must cite (core workflow method)
            elif score >= 4:
                priority = 'important'
            else:
                priority = 'optional'

            paper['priority_score'] = score
            paper['priority'] = priority

        # Filter out irrelevant tools (negative workflow score)
        original_count = len(gaps)
        gaps = [g for g in gaps if g.get('workflow_relevance', 0) >= 0]
        filtered_count = original_count - len(gaps)

        if filtered_count > 0:
            print(f"  Filtered {filtered_count} papers about irrelevant tools")

        # Sort by priority score
        gaps.sort(key=lambda x: x['priority_score'], reverse=True)

        return gaps

    def analyze(
        self,
        manuscript_citations_file: Path,
        search_results_files: List[Path]
    ) -> Dict:
        """Run complete gap analysis"""

        # Load data
        print("📊 Loading manuscript citations...")
        manuscript_cites = self.load_manuscript_citations(manuscript_citations_file)
        print(f"  Found {len(manuscript_cites['raw'])} citations in manuscript")

        print("📊 Loading search results...")
        search_results = self.load_search_results(search_results_files)
        print(f"  Found {len(search_results)} papers in search results")

        # Layer 1: Exact matching
        print("\n🔍 Layer 1: Exact match analysis...")
        gaps = self.exact_match_gaps(manuscript_cites, search_results)
        print(f"  Found {len(gaps)} missing papers")

        if not gaps:
            return {
                'analysis_date': datetime.now().isoformat(),
                'manuscript_citations': len(manuscript_cites['raw']),
                'search_results': len(search_results),
                'gaps': [],
                'summary': {
                    'total_gaps': 0,
                    'by_priority': {},
                    'by_type': {}
                }
            }

        # Layer 2: Semantic overlap
        print("\n🔍 Layer 2: Semantic overlap detection...")
        gaps = self.semantic_overlap_gaps(manuscript_cites, gaps)
        semantic_overlap_count = sum(1 for g in gaps if g.get('has_semantic_overlap', False))
        print(f"  Found {semantic_overlap_count} papers with semantic overlap (>{self.similarity_threshold:.0%})")

        # Layer 3: Citation type categorization
        print("\n🔍 Layer 3: Citation type categorization...")
        for gap in gaps:
            gap['citation_type'] = self.categorize_citation_type(gap)

        type_counts = defaultdict(int)
        for gap in gaps:
            type_counts[gap['citation_type']] += 1
        print(f"  Types: {dict(type_counts)}")

        # Layer 4: Prioritization
        print("\n🔍 Layer 4: Priority assignment...")
        gaps = self.prioritize_gaps(gaps)

        priority_counts = defaultdict(int)
        for gap in gaps:
            priority_counts[gap['priority']] += 1
        print(f"  Priorities: {dict(priority_counts)}")

        # Build summary
        summary = {
            'total_gaps': len(gaps),
            'by_priority': dict(priority_counts),
            'by_type': dict(type_counts),
            'semantic_overlap_count': semantic_overlap_count
        }

        return {
            'analysis_date': datetime.now().isoformat(),
            'similarity_threshold': self.similarity_threshold,
            'manuscript_citations': len(manuscript_cites['raw']),
            'search_results': len(search_results),
            'gaps': gaps,
            'summary': summary
        }


def main():
    parser = argparse.ArgumentParser(
        description='Citation gap analysis with semantic similarity',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        '--manuscript-citations',
        type=Path,
        required=True,
        help='Extracted citations JSON from manuscript'
    )
    parser.add_argument(
        '--search-results',
        type=Path,
        nargs='+',
        required=True,
        help='Literature search results JSON files'
    )
    parser.add_argument(
        '--output',
        type=Path,
        required=True,
        help='Output gap analysis JSON'
    )
    parser.add_argument(
        '--similarity-threshold',
        type=float,
        default=0.70,
        help='Semantic similarity threshold (default: 0.70)'
    )
    parser.add_argument(
        '--manuscript-keywords',
        type=Path,
        help='Manuscript keywords JSON (from extract-manuscript-keywords.py)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Verbose output'
    )

    args = parser.parse_args()

    # Validate inputs
    if not args.manuscript_citations.exists():
        print(f"❌ Error: Manuscript citations file not found: {args.manuscript_citations}", file=sys.stderr)
        return 1

    for search_file in args.search_results:
        if not search_file.exists():
            print(f"❌ Error: Search results file not found: {search_file}", file=sys.stderr)
            return 1

    # Load manuscript keywords if provided
    manuscript_keywords = None
    if args.manuscript_keywords:
        if not args.manuscript_keywords.exists():
            print(f"⚠ Warning: Keywords file not found: {args.manuscript_keywords}", file=sys.stderr)
        else:
            with open(args.manuscript_keywords) as f:
                manuscript_keywords = json.load(f)
            print(f"✓ Loaded manuscript keywords: {len(manuscript_keywords.get('tools_databases', []))} tools, {len(manuscript_keywords.get('methods', []))} methods")

    try:
        # Run analysis
        analyzer = CitationGapAnalyzer(
            similarity_threshold=args.similarity_threshold,
            manuscript_keywords=manuscript_keywords
        )
        results = analyzer.analyze(
            args.manuscript_citations,
            args.search_results
        )

        # Write output
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)

        print(f"\n✅ Gap analysis complete!")
        print(f"  Total gaps: {results['summary']['total_gaps']}")
        print(f"  Critical: {results['summary']['by_priority'].get('critical', 0)}")
        print(f"  Important: {results['summary']['by_priority'].get('important', 0)}")
        print(f"  Optional: {results['summary']['by_priority'].get('optional', 0)}")
        print(f"\n  Output: {args.output}")

        return 0

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
