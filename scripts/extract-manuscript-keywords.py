#!/usr/bin/env python3
"""
Extract key terms and concepts from manuscript for targeted literature search.

Analyzes manuscript to find:
- Tool/database names (SILVA, Rfam, CatBoost, etc.)
- Method names (SHAP, gradient boosting, etc.)
- Domain-specific terms (metagenome, 16S rRNA, etc.)
- Statistical methods
- Key concepts

Usage:
    python scripts/extract-manuscript-keywords.py \
    --docx manuscript.docx \
    --output keywords.json
"""

import argparse
import json
import re
from pathlib import Path
from collections import Counter
from typing import List, Dict, Set

try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    print("Error: python-docx required")
    exit(1)


class ManuscriptKeywordExtractor:
    """Extract domain-specific keywords from manuscript"""

    # Known tool/database patterns
    TOOLS = [
        'KBase', 'MGnify', 'SILVA', 'Rfam', 'KEGG', 'Pfam',
        'CatBoost', 'SHAP', 'SciPy', 'scikit-learn',
        'antiSMASH', 'VirSorter', 'CheckM', 'GTDB',
        'IMG/M', 'JGI', 'NCBI', 'EMBL', 'UniProt'
    ]

    # Statistical/ML methods
    METHODS = [
        'gradient boosting', 'random forest', 'neural network',
        'feature importance', 'feature selection', 'SHAP',
        'Mann-Whitney', 'Pearson correlation', 'principal component',
        'machine learning', 'deep learning', 'classification',
        'permutation', 'cross-validation', 'confusion matrix'
    ]

    # Domain terms
    DOMAIN_TERMS = [
        'metagenome', 'metagenomics', '16S rRNA', '18S rRNA',
        'taxonomy', 'taxonomic', 'phylogeny', 'phylogenetic',
        'ecosystem', 'microbiome', 'microbial community',
        'bacterial', 'archaeal', 'viral', 'fungal',
        'biosynthetic gene cluster', 'functional annotation',
        'abundance', 'diversity', 'alpha diversity', 'beta diversity'
    ]

    def __init__(self):
        self.text = ""
        self.keywords = {
            'tools_databases': [],
            'methods': [],
            'domain_terms': [],
            'extracted_phrases': [],
            'suggested_queries': []
        }

    def load_manuscript(self, docx_path: Path):
        """Load manuscript text"""
        doc = Document(docx_path)
        self.text = '\n'.join([para.text for para in doc.paragraphs])

    def extract_tools_databases(self) -> List[str]:
        """Extract tool and database names"""
        found = []

        # Known tools (case-insensitive)
        for tool in self.TOOLS:
            if re.search(rf'\b{re.escape(tool)}\b', self.text, re.IGNORECASE):
                found.append(tool)

        # Pattern for version numbers (e.g., "MGnify v5.0")
        version_pattern = r'\b([A-Z][A-Za-z0-9]+)\s+v?\d+\.?\d*'
        for match in re.finditer(version_pattern, self.text):
            tool_name = match.group(1)
            if len(tool_name) > 3:  # Skip short acronyms
                found.append(tool_name)

        # Database patterns (uppercase acronyms)
        db_pattern = r'\b([A-Z]{3,})\b'
        for match in re.finditer(db_pattern, self.text):
            acronym = match.group(1)
            # Filter common words
            if acronym not in ['DNA', 'RNA', 'USA', 'THE', 'AND', 'FOR']:
                found.append(acronym)

        return list(set(found))

    def extract_methods(self) -> List[str]:
        """Extract statistical and computational methods"""
        found = []

        for method in self.METHODS:
            if re.search(rf'\b{re.escape(method)}\b', self.text, re.IGNORECASE):
                found.append(method)

        # Statistical test patterns
        stat_pattern = r'\b([A-Z][a-z]+(?:-[A-Z][a-z]+)?)\s+(?:test|analysis|correlation)\b'
        for match in re.finditer(stat_pattern, self.text):
            test_name = match.group(0)
            found.append(test_name)

        return list(set(found))

    def extract_domain_terms(self) -> List[str]:
        """Extract domain-specific terminology"""
        found = []

        for term in self.DOMAIN_TERMS:
            if re.search(rf'\b{re.escape(term)}\b', self.text, re.IGNORECASE):
                found.append(term)

        # Extract quoted technical terms
        quoted_pattern = r'"([^"]{10,50})"'
        for match in re.finditer(quoted_pattern, self.text):
            term = match.group(1)
            if not term[0].isupper():  # Skip sentences
                continue
            found.append(term)

        return list(set(found))

    def extract_key_phrases(self) -> List[str]:
        """Extract frequent multi-word phrases"""
        # Extract 2-4 word phrases
        phrases = []

        # Bigrams
        bigram_pattern = r'\b([a-z]+(?:-[a-z]+)?)\s+([a-z]+(?:-[a-z]+)?)\b'
        bigrams = re.findall(bigram_pattern, self.text.lower())
        bigram_counts = Counter([' '.join(bg) for bg in bigrams])

        # Trigrams
        trigram_pattern = r'\b([a-z]+)\s+([a-z]+)\s+([a-z]+)\b'
        trigrams = re.findall(trigram_pattern, self.text.lower())
        trigram_counts = Counter([' '.join(tg) for tg in trigrams])

        # Top phrases (appearing 3+ times)
        for phrase, count in bigram_counts.most_common(50):
            if count >= 3 and len(phrase) > 10:
                # Filter stopwords
                if not any(sw in phrase.split() for sw in ['the', 'and', 'for', 'with', 'from']):
                    phrases.append(phrase)

        for phrase, count in trigram_counts.most_common(30):
            if count >= 2 and len(phrase) > 15:
                phrases.append(phrase)

        return phrases[:20]  # Top 20

    def generate_search_queries(self) -> List[Dict]:
        """Generate targeted search queries from extracted keywords"""
        queries = []

        tools = self.keywords['tools_databases']
        methods = self.keywords['methods']
        domain = self.keywords['domain_terms']

        # Query 1: Primary tools + domain
        if tools and domain:
            primary_tools = tools[:3]
            primary_domain = domain[:2]
            query = f"{' '.join(primary_tools)} {' '.join(primary_domain)}"
            queries.append({
                'query': query,
                'tier': 1,
                'rationale': 'Primary tools and domain terms from manuscript'
            })

        # Query 2: Methods + domain
        if methods and domain:
            primary_methods = methods[:2]
            query = f"{' '.join(primary_methods)} {' '.join(domain[:2])}"
            queries.append({
                'query': query,
                'tier': 1,
                'rationale': 'Key methods applied in manuscript'
            })

        # Query 3: Specific tool citations
        for tool in tools[:5]:
            queries.append({
                'query': f"{tool} microbiome metagenome",
                'tier': 2,
                'rationale': f'Citations for {tool} tool'
            })

        # Query 4: Method citations
        for method in methods[:3]:
            queries.append({
                'query': f"{method} ecology microbial",
                'tier': 2,
                'rationale': f'Method papers for {method}'
            })

        return queries

    def extract_all(self):
        """Run all extraction methods"""
        self.keywords['tools_databases'] = self.extract_tools_databases()
        self.keywords['methods'] = self.extract_methods()
        self.keywords['domain_terms'] = self.extract_domain_terms()
        self.keywords['extracted_phrases'] = self.extract_key_phrases()
        self.keywords['suggested_queries'] = self.generate_search_queries()


def main():
    parser = argparse.ArgumentParser(
        description='Extract keywords from manuscript for targeted literature search'
    )
    parser.add_argument('--docx', type=Path, required=True, help='Manuscript DOCX')
    parser.add_argument('--output', type=Path, required=True, help='Output JSON')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')

    args = parser.parse_args()

    if not args.docx.exists():
        print(f"Error: File not found: {args.docx}")
        return 1

    # Extract keywords
    extractor = ManuscriptKeywordExtractor()
    extractor.load_manuscript(args.docx)
    extractor.extract_all()

    # Save results
    with open(args.output, 'w') as f:
        json.dump(extractor.keywords, f, indent=2)

    # Print summary
    print(f"✓ Extracted keywords from: {args.docx}")
    print(f"\nTools/Databases ({len(extractor.keywords['tools_databases'])}):")
    for tool in extractor.keywords['tools_databases'][:10]:
        print(f"  - {tool}")

    print(f"\nMethods ({len(extractor.keywords['methods'])}):")
    for method in extractor.keywords['methods'][:10]:
        print(f"  - {method}")

    print(f"\nDomain Terms ({len(extractor.keywords['domain_terms'])}):")
    for term in extractor.keywords['domain_terms'][:10]:
        print(f"  - {term}")

    print(f"\nSuggested Queries ({len(extractor.keywords['suggested_queries'])}):")
    for i, q in enumerate(extractor.keywords['suggested_queries'][:5], 1):
        print(f"  {i}. {q['query']}")
        print(f"     → {q['rationale']}")

    print(f"\n✓ Full results: {args.output}")

    return 0


if __name__ == '__main__':
    exit(main())
