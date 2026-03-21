#!/usr/bin/env python3
"""
Requirement Extractor - Extract structured requirements from parsed documents.

This module uses regex patterns and NLP techniques to extract journal submission
requirements from parsed document text.
"""

import re
from typing import Dict, List, Optional, Tuple, Any
from collections import defaultdict


class ExtractionError(Exception):
    """Exception raised when requirement extraction fails."""
    pass


class RequirementExtractor:
    """Extracts structured requirements from parsed document text."""

    # Regex patterns for common requirement formats
    WORD_LIMIT_PATTERNS = [
        # "Abstract: 150-250 words"
        r'(?P<section>\w+):\s*(?P<min>\d+)-(?P<max>\d+)\s*words?',
        # "Abstract (max 250 words)"
        r'(?P<section>\w+)\s*\((?:max|maximum)\s*(?P<max>\d+)\s*words?\)',
        # "Abstract should not exceed 250 words"
        r'(?P<section>\w+)\s*should\s*not\s*exceed\s*(?P<max>\d+)\s*words?',
        # "Abstract word limit: 250"
        r'(?P<section>\w+)\s*word\s*limit:\s*(?P<max>\d+)',
        # "250 words for Abstract"
        r'(?P<max>\d+)\s*words?\s*for\s*(?P<section>\w+)',
    ]

    SECTION_PATTERNS = [
        # "Required sections: Abstract, Introduction, ..."
        r'(?:required|mandatory)\s*sections?:\s*(?P<sections>[A-Za-z,\s]+)',
        # "Must include: Abstract, Introduction, ..."
        r'must\s*include:\s*(?P<sections>[A-Za-z,\s]+)',
        # Numbered/bulleted list detection
        r'(?:^\d+\.|^[-*])\s*(?P<section>Abstract|Introduction|Methods|Results|Discussion|Availability)',
    ]

    CITATION_STYLE_PATTERNS = [
        r'(?:citation|reference)\s*style:\s*(?P<style>\w+)',
        r'(?P<style>APA|Vancouver|Nature|IEEE|Chicago|Harvard)\s*(?:style|format)',
        r'references?\s*should\s*follow\s*(?P<style>\w+)',
    ]

    FIGURE_TABLE_PATTERNS = [
        r'(?:maximum|max|up to)\s*(?P<num>\d+)\s*(?P<type>figure|table)s?',
        r'(?P<num>\d+)\s*(?P<type>figure|table)s?\s*(?:maximum|max|allowed)',
    ]

    def __init__(self, text: str, structured_data: Optional[Dict] = None):
        """
        Initialize extractor.

        Args:
            text: Raw text from document
            structured_data: Optional structured data from parser
        """
        self.text = text
        self.structured_data = structured_data or {}
        self.requirements = {}

    def extract_all(self) -> Dict[str, Any]:
        """
        Extract all requirements from document.

        Returns:
            Dictionary containing extracted requirements
        """
        self.requirements = {
            'word_limits': self.extract_word_limits(),
            'section_requirements': self.extract_section_requirements(),
            'citation_style': self.extract_citation_style(),
            'figure_table_limits': self.extract_figure_table_limits(),
            'formatting_rules': self.extract_formatting_rules(),
            'special_requirements': self.extract_special_requirements()
        }

        return self.requirements

    def extract_word_limits(self) -> Dict[str, Dict[str, int]]:
        """
        Extract word count limits for sections.

        Returns:
            Dictionary mapping section names to word limits
        """
        word_limits = {}

        # Try each pattern
        for pattern in self.WORD_LIMIT_PATTERNS:
            for match in re.finditer(pattern, self.text, re.IGNORECASE | re.MULTILINE):
                section = match.group('section').lower()

                # Normalize section name
                section = self._normalize_section_name(section)
                if not section:
                    continue

                limit = {}
                if 'min' in match.groupdict() and match.group('min'):
                    limit['min'] = int(match.group('min'))
                if 'max' in match.groupdict() and match.group('max'):
                    limit['max'] = int(match.group('max'))

                if limit:
                    word_limits[section] = limit

        # Look for total manuscript limits
        total_patterns = [
            r'(?:total|manuscript)\s*(?:word\s*)?limit:\s*(?P<max>\d+)',
            r'(?P<max>\d+)\s*words?\s*(?:total|in\s*total)',
        ]

        for pattern in total_patterns:
            for match in re.finditer(pattern, self.text, re.IGNORECASE):
                word_limits['total_manuscript'] = {'max': int(match.group('max'))}

        return word_limits

    def extract_section_requirements(self) -> Dict[str, Any]:
        """
        Extract required/optional sections and their order.

        Returns:
            Dictionary with required_sections, optional_sections, section_order
        """
        required = set()
        optional = set()
        order = []

        # Extract from patterns
        for pattern in self.SECTION_PATTERNS:
            for match in re.finditer(pattern, self.text, re.IGNORECASE | re.MULTILINE):
                if 'sections' in match.groupdict():
                    sections_str = match.group('sections')
                    sections = [s.strip() for s in sections_str.split(',')]
                    for section in sections:
                        normalized = self._normalize_section_name(section)
                        if normalized:
                            required.add(normalized)
                            if normalized not in order:
                                order.append(normalized)
                elif 'section' in match.groupdict():
                    section = self._normalize_section_name(match.group('section'))
                    if section:
                        required.add(section)
                        if section not in order:
                            order.append(section)

        # If no sections found, use default order
        if not order:
            order = [
                'abstract', 'introduction', 'methods',
                'results', 'discussion', 'availability'
            ]

        return {
            'required_sections': list(required) if required else order,
            'optional_sections': list(optional),
            'section_order': order
        }

    def extract_citation_style(self) -> Dict[str, Any]:
        """
        Extract citation and reference requirements.

        Returns:
            Dictionary with citation style and limits
        """
        citation_info = {}

        # Extract style
        for pattern in self.CITATION_STYLE_PATTERNS:
            match = re.search(pattern, self.text, re.IGNORECASE)
            if match:
                citation_info['style'] = match.group('style')
                break

        # Extract reference limits
        ref_patterns = [
            r'(?:maximum|max|up to)\s*(?P<max>\d+)\s*references?',
            r'(?P<max>\d+)\s*references?\s*(?:maximum|max|allowed)',
        ]

        for pattern in ref_patterns:
            match = re.search(pattern, self.text, re.IGNORECASE)
            if match:
                citation_info['max_references'] = int(match.group('max'))
                break

        return citation_info

    def extract_figure_table_limits(self) -> Dict[str, int]:
        """
        Extract figure and table limits.

        Returns:
            Dictionary with max_figures and max_tables
        """
        limits = {}

        for pattern in self.FIGURE_TABLE_PATTERNS:
            for match in re.finditer(pattern, self.text, re.IGNORECASE):
                limit_type = match.group('type').lower()
                num = int(match.group('num'))

                if limit_type == 'figure':
                    limits['max_figures'] = num
                elif limit_type == 'table':
                    limits['max_tables'] = num

        return limits

    def extract_formatting_rules(self) -> Dict[str, Any]:
        """
        Extract formatting requirements (font, spacing, etc.).

        Returns:
            Dictionary with formatting rules
        """
        formatting = {}

        # Font
        font_pattern = r'(?:font|typeface):\s*(?P<font>[\w\s]+?)(?:\n|,|\.|;|$)'
        match = re.search(font_pattern, self.text, re.IGNORECASE)
        if match:
            formatting['font'] = match.group('font').strip()

        # Font size
        size_pattern = r'(?:font\s*size|point\s*size):\s*(?P<size>\d+)\s*(?:pt|point|points)?'
        match = re.search(size_pattern, self.text, re.IGNORECASE)
        if match:
            formatting['font_size'] = int(match.group('size'))

        # Line spacing
        spacing_pattern = r'(?P<spacing>double|single|1\.5)[\s-]*(?:line[\s-]*)?spac(?:e|ing)'
        match = re.search(spacing_pattern, self.text, re.IGNORECASE)
        if match:
            formatting['line_spacing'] = match.group('spacing').lower()

        # Page/line numbers
        if re.search(r'(?:page|line)\s*numbers?\s*(?:required|must|should)', self.text, re.IGNORECASE):
            if 'page' in match.group(0).lower():
                formatting['page_numbers'] = True
            if 'line' in match.group(0).lower():
                formatting['line_numbers'] = True

        return formatting

    def extract_special_requirements(self) -> List[Dict[str, str]]:
        """
        Extract journal-specific special requirements.

        Returns:
            List of special requirements
        """
        special = []

        # Look for common special requirement indicators
        indicators = [
            r'(?:must|required|mandatory):\s*(.+?)(?:\n|\.)',
            r'(?:important|note):\s*(.+?)(?:\n|\.)',
            r'authors?\s*must\s*(.+?)(?:\n|\.)',
        ]

        for pattern in indicators:
            for match in re.finditer(pattern, self.text, re.IGNORECASE):
                requirement_text = match.group(1).strip()
                if len(requirement_text) > 10:  # Filter out very short matches
                    special.append({
                        'requirement': requirement_text,
                        'priority': 'mandatory'
                    })

        return special[:10]  # Limit to top 10

    def _normalize_section_name(self, name: str) -> Optional[str]:
        """
        Normalize section name to standard format.

        Args:
            name: Raw section name

        Returns:
            Normalized name or None if not recognized
        """
        name_lower = name.lower().strip()

        # Mapping of variations to standard names
        mappings = {
            'abstract': ['abstract', 'summary'],
            'introduction': ['introduction', 'intro', 'background'],
            'methods': ['methods', 'methodology', 'materials and methods',
                       'materials & methods', 'experimental'],
            'results': ['results', 'findings'],
            'discussion': ['discussion', 'conclusions'],
            'availability': ['availability', 'data availability',
                           'code availability', 'supplementary'],
            'author_summary': ['author summary', 'significance statement'],
            'acknowledgments': ['acknowledgments', 'acknowledgements', 'funding'],
            'references': ['references', 'bibliography', 'citations']
        }

        for standard, variations in mappings.items():
            if name_lower in variations or any(v in name_lower for v in variations):
                return standard

        return None

    def extract_from_table(self, table_data: List[List[str]]) -> Dict[str, Any]:
        """
        Extract requirements from a table structure.

        Args:
            table_data: 2D list representing table

        Returns:
            Extracted requirements
        """
        requirements = {}

        if not table_data or len(table_data) < 2:
            return requirements

        # Check if first row is header
        headers = [h.lower() for h in table_data[0]]

        # Look for word limit columns
        if 'section' in headers or 'word limit' in ' '.join(headers):
            section_idx = None
            limit_idx = None

            for i, h in enumerate(headers):
                if 'section' in h.lower():
                    section_idx = i
                if 'word' in h.lower() or 'limit' in h.lower():
                    limit_idx = i

            if section_idx is not None and limit_idx is not None:
                word_limits = {}
                for row in table_data[1:]:
                    if len(row) > max(section_idx, limit_idx):
                        section = self._normalize_section_name(row[section_idx])
                        limit_str = row[limit_idx]

                        # Parse limit (handle ranges like "150-250")
                        if '-' in limit_str:
                            parts = limit_str.split('-')
                            try:
                                word_limits[section] = {
                                    'min': int(parts[0].strip()),
                                    'max': int(parts[1].strip())
                                }
                            except ValueError:
                                pass
                        else:
                            try:
                                num = int(re.search(r'\d+', limit_str).group())
                                word_limits[section] = {'max': num}
                            except (AttributeError, ValueError):
                                pass

                if word_limits:
                    requirements['word_limits'] = word_limits

        return requirements


if __name__ == '__main__':
    # Test extractor
    sample_text = """
    Manuscript Preparation Guidelines

    Word Limits:
    - Abstract: 150-250 words
    - Introduction: Maximum 1000 words
    - Methods: No limit
    - Results: 2000 words maximum
    - Discussion: Up to 1500 words

    Required Sections: Abstract, Introduction, Methods, Results, Discussion

    Citation Style: Vancouver

    Figures and Tables: Maximum 6 figures and 4 tables

    Formatting: Double spacing, 12 pt Times New Roman
    """

    extractor = RequirementExtractor(sample_text)
    requirements = extractor.extract_all()

    import json
    print(json.dumps(requirements, indent=2))
