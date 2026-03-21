#!/usr/bin/env python3
"""
Fuzzy Citation Matcher for Paperpile Links

Matches citations between old and new text using fuzzy string matching
to handle slight variations in citation format.

Usage:
    from citation_matcher import CitationMatcher

    matcher = CitationMatcher(similarity_threshold=0.85)
    matched_links, unmatched_citations = matcher.match_citations(old_links, new_text)
"""

import re
from typing import List, Tuple, Dict, Set
from dataclasses import dataclass
from difflib import SequenceMatcher


@dataclass
class CitationLink:
    """Represents a Paperpile citation link"""
    text: str  # e.g., "(Zhao et al. 2022)"
    url: str   # e.g., "https://paperpile.com/c/aBwggu/g8fB"
    start_index: int  # Character position in text
    end_index: int    # Character position in text


class CitationMatcher:
    """
    Intelligent citation matching with fuzzy matching and multiple format support
    """

    # Citation patterns covering various academic citation formats
    # IMPORTANT: Order matters - more specific patterns first, then general ones
    CITATION_PATTERNS = [
        # Multiple citations with semicolons (most complex, must come first)
        # Handles: (Author et al. 2020; Author and Author 2021; Author et al. 2022)
        r'\([A-Z][a-z]+(?:\s+et\s+al\.|\s+and\s+[A-Z][a-z]+|,\s+[A-Z][a-z]+,\s+and\s+[A-Z][a-z]+)?\s+\d{4}[a-z]?(?:;\s*[A-Z][a-z]+(?:\s+et\s+al\.|\s+and\s+[A-Z][a-z]+|,\s+[A-Z][a-z]+,\s+and\s+[A-Z][a-z]+)?\s+\d{4}[a-z]?)+\)',

        # Nature-style numeric citations
        r'\[\d+[-,]\d+\]',  # [1-3] or [1,2]
        r'\[\d+\]',  # [1]

        # Three-author format with commas
        r'\([A-Z][a-z]+,\s+[A-Z][a-z]+,\s+and\s+[A-Z][a-z]+\s+\d{4}[a-z]?\)',  # (Smith, Jones, and Brown 2020)

        # Two-author format
        r'\([A-Z][a-z]+\s+and\s+[A-Z][a-z]+\s+\d{4}[a-z]?\)',  # (Smith and Jones 2020)

        # Et al format
        r'\([A-Z][a-z]+\s+et\s+al\.\s+\d{4}[a-z]?\)',  # (Smith et al. 2020)

        # Single author
        r'\([A-Z][a-z]+\s+\d{4}[a-z]?\)',  # (Smith 2020)
    ]

    def __init__(self, similarity_threshold: float = 0.85):
        """
        Initialize citation matcher

        Args:
            similarity_threshold: Minimum similarity ratio (0-1) for fuzzy matching
        """
        self.similarity_threshold = similarity_threshold
        self.compiled_patterns = [re.compile(p) for p in self.CITATION_PATTERNS]

    def find_citations_in_text(self, text: str) -> List[Tuple[str, int, int]]:
        """
        Find all citation patterns in text

        Returns:
            List of (citation_text, start_pos, end_pos) tuples
        """
        citations = []
        seen = set()  # Avoid duplicates from overlapping patterns

        for pattern in self.compiled_patterns:
            for match in pattern.finditer(text):
                cite_text = match.group()
                start = match.start()
                end = match.end()

                # Skip if we already found this citation
                position_key = (start, end)
                if position_key in seen:
                    continue

                seen.add(position_key)
                citations.append((cite_text, start, end))

        # Sort by position
        citations.sort(key=lambda x: x[1])

        return citations

    def normalize_citation(self, citation: str) -> str:
        """
        Normalize citation text for comparison

        - Collapse whitespace
        - Standardize "et al."
        - Remove punctuation variations
        """
        normalized = ' '.join(citation.split())
        normalized = normalized.replace('et al', 'et al.')
        normalized = normalized.replace('et al..', 'et al.')
        return normalized

    def similarity(self, str1: str, str2: str) -> float:
        """
        Calculate similarity ratio between two strings

        Uses SequenceMatcher for fuzzy matching (0.0 to 1.0)
        """
        norm1 = self.normalize_citation(str1)
        norm2 = self.normalize_citation(str2)
        return SequenceMatcher(None, norm1, norm2).ratio()

    def find_best_match(
        self,
        citation: str,
        candidates: Dict[str, str]
    ) -> Tuple[str, float]:
        """
        Find best matching citation from candidates

        Args:
            citation: Citation text to match
            candidates: Dict mapping citation text to Paperpile URL

        Returns:
            (best_match_url, similarity_score) or (None, 0.0)
        """
        best_match = None
        best_score = 0.0

        for candidate_text, url in candidates.items():
            score = self.similarity(citation, candidate_text)

            if score > best_score:
                best_score = score
                best_match = url

        return best_match, best_score

    def match_citations(
        self,
        old_links: List[CitationLink],
        new_text: str,
        prepend_cite: bool = True
    ) -> Tuple[List[CitationLink], str, List[str]]:
        """
        Match old Paperpile links to citations in new text using fuzzy matching

        Args:
            old_links: List of CitationLink objects from original section
            new_text: New section text with citations
            prepend_cite: If True, prepend 'cite' to unmatched citations

        Returns:
            (matched_links, modified_text, unmatched_citations)

            - matched_links: CitationLink objects for citations in new text
            - modified_text: New text with 'cite' prepended to unmatched citations
            - unmatched_citations: List of citation texts that had no match
        """
        print(f"\n🔗 Matching {len(old_links)} citations to new text (fuzzy threshold: {self.similarity_threshold})...")

        # Find all citations in new text
        new_citations = self.find_citations_in_text(new_text)
        print(f"  ✓ Found {len(new_citations)} citation patterns in new text")

        # Build lookup map: normalized citation text -> Paperpile URL
        citation_to_url = {}
        for link in old_links:
            normalized = self.normalize_citation(link.text)
            citation_to_url[normalized] = link.url

        # Match new citations to old URLs using fuzzy matching
        matched_links = []
        unmatched_citations = []
        text_modifications = []  # (position, old_text, new_text) for 'cite' insertions

        match_stats = {'exact': 0, 'fuzzy': 0, 'unmatched': 0}

        for cite_text, start, end in new_citations:
            # Try exact match first
            normalized = self.normalize_citation(cite_text)

            if normalized in citation_to_url:
                # Exact match found
                matched_links.append(CitationLink(
                    text=cite_text,
                    url=citation_to_url[normalized],
                    start_index=start,
                    end_index=end
                ))
                match_stats['exact'] += 1
            else:
                # Try fuzzy match
                best_url, score = self.find_best_match(cite_text, citation_to_url)

                if best_url and score >= self.similarity_threshold:
                    # Fuzzy match found
                    matched_links.append(CitationLink(
                        text=cite_text,
                        url=best_url,
                        start_index=start,
                        end_index=end
                    ))
                    match_stats['fuzzy'] += 1
                    print(f"    ~ Fuzzy match ({score:.2f}): {cite_text[:40]}")
                else:
                    # No match - will prepend 'cite'
                    unmatched_citations.append(cite_text)
                    if prepend_cite:
                        text_modifications.append((start, end, cite_text))
                    match_stats['unmatched'] += 1

        # Apply 'cite' prefix to unmatched citations (reverse order to preserve positions)
        modified_text = new_text
        if prepend_cite:
            for start, end, cite_text in reversed(text_modifications):
                modified_text = modified_text[:start] + 'cite' + modified_text[start:]

        # Recalculate matched link positions after 'cite' insertions
        if prepend_cite and text_modifications:
            final_matched_links = []
            for link in matched_links:
                # Count how many 'cite' prefixes were added before this link
                offset = sum(4 for mod_start, _, _ in text_modifications if mod_start < link.start_index)

                final_matched_links.append(CitationLink(
                    text=link.text,
                    url=link.url,
                    start_index=link.start_index + offset,
                    end_index=link.end_index + offset
                ))
            matched_links = final_matched_links

        # Report results
        print(f"  ✓ Matched {len(matched_links)}/{len(new_citations)} citations")
        print(f"    - Exact matches: {match_stats['exact']}")
        print(f"    - Fuzzy matches: {match_stats['fuzzy']}")
        print(f"    - Unmatched: {match_stats['unmatched']}")

        if unmatched_citations:
            print(f"\n  ⚠️ {len(unmatched_citations)} citations {'prepended with cite' if prepend_cite else 'unmatched'}:")
            for cite in unmatched_citations[:5]:
                print(f"     - {'cite' if prepend_cite else ''}{cite}")
            if len(unmatched_citations) > 5:
                print(f"     ... and {len(unmatched_citations) - 5} more")
            if prepend_cite:
                print(f"  → Easy to find with Ctrl+F 'cite(' and add Paperpile links manually")

        return matched_links, modified_text, unmatched_citations


if __name__ == '__main__':
    # Test the citation matcher
    test_text = """
    Previous work (Smith et al. 2020) showed that microbes adapt quickly.
    Another study (Jones and Brown 2021) confirmed this. Recent findings
    (Wang et al. 2024; Li et al. 2023) support the hypothesis.
    """

    # Simulate old links
    old_links = [
        CitationLink("(Smith et al. 2020)", "https://paperpile.com/c/abc123/xyz", 0, 0),
        CitationLink("(Jones and Brown 2021)", "https://paperpile.com/c/def456/uvw", 0, 0),
    ]

    matcher = CitationMatcher(similarity_threshold=0.85)
    matched, modified, unmatched = matcher.match_citations(old_links, test_text)

    print(f"\n{'='*60}")
    print(f"Test Results:")
    print(f"  Matched: {len(matched)}")
    print(f"  Unmatched: {len(unmatched)}")
    print(f"\nModified text preview:")
    print(modified[:200])
