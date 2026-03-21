#!/usr/bin/env python3
"""
Schema Builder - Build JSON schemas from extracted requirements.

This module generates JSON schemas for journal submission requirements and
manuscript structure based on extracted data and base templates.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime
import sys

# Add scripts directory to path
SCRIPTS_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPTS_DIR))


class SchemaBuilderError(Exception):
    """Exception raised when schema building fails."""
    pass


class SchemaBuilder:
    """Builds JSON schemas from extracted requirements."""

    def __init__(self, templates_dir: Optional[Path] = None):
        """
        Initialize schema builder.

        Args:
            templates_dir: Path to templates directory (defaults to schemas/templates)
        """
        if templates_dir is None:
            repo_root = SCRIPTS_DIR.parent
            templates_dir = repo_root / "schemas" / "templates"

        self.templates_dir = Path(templates_dir)

        if not self.templates_dir.exists():
            raise SchemaBuilderError(
                f"Templates directory not found: {templates_dir}"
            )

        self.base_submission = self._load_template("base_submission_requirements.json")
        self.base_structure = self._load_template("base_manuscript_structure.json")

    def _load_template(self, filename: str) -> Dict[str, Any]:
        """Load a template file."""
        template_path = self.templates_dir / filename

        if not template_path.exists():
            raise SchemaBuilderError(f"Template not found: {template_path}")

        try:
            with open(template_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise SchemaBuilderError(f"Invalid JSON in template {filename}: {e}")

    def build_submission_schema(
        self,
        journal_name: str,
        requirements: Dict[str, Any],
        source_type: str,
        source_path: str
    ) -> Dict[str, Any]:
        """
        Build submission requirements schema for a journal.

        Args:
            journal_name: Name of the journal
            requirements: Extracted requirements
            source_type: How requirements were obtained (url, pdf, yaml, etc.)
            source_path: Path or URL to source

        Returns:
            Complete submission requirements schema
        """
        schema = self.base_submission.copy()

        # Populate journal info
        schema['journal'] = {
            'name': journal_name,
            'short_name': self._generate_short_name(journal_name),
            'publisher': requirements.get('publisher', 'Unknown'),
            'url': requirements.get('journal_url', ''),
            'submission_url': source_path if source_type == 'url' else ''
        }

        # Build requirements section
        schema['requirements'] = {
            'word_limits': self._build_word_limits(requirements.get('word_limits', {})),
            'section_requirements': self._build_section_requirements(
                requirements.get('section_requirements', {})
            ),
            'citation_requirements': self._build_citation_requirements(
                requirements.get('citation_style', {})
            ),
            'figure_table_requirements': self._build_figure_table_requirements(
                requirements.get('figure_table_limits', {})
            ),
            'formatting_requirements': requirements.get('formatting_rules', {}),
            'special_requirements': requirements.get('special_requirements', [])
        }

        # Add metadata
        schema['metadata'] = {
            'schema_version': '1.0',
            'generated_at': datetime.now().isoformat(),
            'source_type': source_type,
            'source_path': source_path,
            'validated': False,
            'notes': f'Auto-generated from {source_type} source'
        }

        return schema

    def build_manuscript_schema(
        self,
        journal_name: str,
        requirements: Dict[str, Any],
        source_type: str
    ) -> Dict[str, Any]:
        """
        Build manuscript structure schema for a journal.

        Args:
            journal_name: Name of the journal
            requirements: Extracted requirements
            source_type: How requirements were obtained

        Returns:
            Complete manuscript structure schema
        """
        schema = self.base_structure.copy()

        # Populate journal info
        schema['journal'] = {'name': journal_name}

        # Build sections array
        section_req = requirements.get('section_requirements', {})
        required_sections = section_req.get('required_sections', [])
        section_order = section_req.get('section_order', required_sections)
        word_limits = requirements.get('word_limits', {})

        sections = []
        for section_name in section_order:
            section = {
                'name': section_name,
                'required': section_name in required_sections,
                'heading_level': 1 if section_name == 'abstract' else 2
            }

            # Add word limit if available
            if section_name in word_limits:
                section['word_limit'] = word_limits[section_name]

            # Add description based on section type
            section['description'] = self._get_section_description(section_name)

            sections.append(section)

        schema['structure'] = {
            'sections': sections,
            'global_constraints': self._build_global_constraints(requirements),
            'ordering_rules': {
                'strict_order': True,
                'allowed_deviations': []
            }
        }

        # Add metadata
        schema['metadata'] = {
            'schema_version': '1.0',
            'generated_at': datetime.now().isoformat(),
            'source_type': source_type,
            'validated': False
        }

        return schema

    def _build_word_limits(self, word_limits: Dict[str, Dict[str, int]]) -> Dict:
        """Build word limits section."""
        limits = {}
        for section, limit in word_limits.items():
            limits[section] = limit
        return limits

    def _build_section_requirements(self, section_req: Dict[str, Any]) -> Dict:
        """Build section requirements."""
        return {
            'required_sections': section_req.get('required_sections', []),
            'optional_sections': section_req.get('optional_sections', []),
            'section_order': section_req.get('section_order', []),
            'special_requirements': {}
        }

    def _build_citation_requirements(self, citation_info: Dict[str, Any]) -> Dict:
        """Build citation requirements."""
        return {
            'style': citation_info.get('style', 'Unknown'),
            'max_references': citation_info.get('max_references'),
            'min_references': citation_info.get('min_references'),
            'reference_formatting': citation_info.get('formatting', '')
        }

    def _build_figure_table_requirements(self, limits: Dict[str, int]) -> Dict:
        """Build figure/table requirements."""
        return {
            'max_figures': limits.get('max_figures'),
            'max_tables': limits.get('max_tables'),
            'figure_formats': ['PNG', 'PDF', 'TIFF', 'EPS'],
            'resolution_requirements': '300 DPI minimum'
        }

    def _build_global_constraints(self, requirements: Dict[str, Any]) -> Dict:
        """Build global manuscript constraints."""
        constraints = {}

        word_limits = requirements.get('word_limits', {})
        if 'total_manuscript' in word_limits:
            constraints['total_word_count'] = word_limits['total_manuscript']

        fig_table = requirements.get('figure_table_limits', {})
        if 'max_figures' in fig_table:
            constraints['max_figures'] = fig_table['max_figures']
        if 'max_tables' in fig_table:
            constraints['max_tables'] = fig_table['max_tables']

        citation = requirements.get('citation_style', {})
        if 'max_references' in citation:
            constraints['max_references'] = citation['max_references']

        return constraints

    def _get_section_description(self, section_name: str) -> str:
        """Get standard description for a section."""
        descriptions = {
            'abstract': 'Concise summary of the research question, methods, results, and conclusions',
            'introduction': 'Background, motivation, and research objectives',
            'methods': 'Detailed description of experimental procedures and computational methods',
            'results': 'Presentation of findings with figures and tables',
            'discussion': 'Interpretation of results, implications, and limitations',
            'availability': 'Data and code availability statements',
            'author_summary': 'Lay summary of the significance and impact',
            'acknowledgments': 'Funding sources and acknowledgments',
            'references': 'Bibliography of cited works'
        }
        return descriptions.get(section_name, '')

    def _generate_short_name(self, full_name: str) -> str:
        """Generate short name from full journal name."""
        # Remove common words
        words = full_name.split()
        filtered = [w for w in words if w.lower() not in ['the', 'journal', 'of', 'and']]

        if len(filtered) <= 2:
            return full_name
        else:
            return ' '.join(filtered[:2])

    def validate_schema(self, schema: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate generated schema.

        Args:
            schema: Schema to validate

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # Check for journal and metadata (common to both types)
        if 'journal' not in schema:
            errors.append("Missing required key: journal")
        elif 'name' not in schema['journal']:
            errors.append("Missing journal name")

        if 'metadata' not in schema:
            errors.append("Missing required key: metadata")
        else:
            meta = schema['metadata']
            if 'generated_at' not in meta:
                errors.append("Missing metadata.generated_at")
            if 'source_type' not in meta:
                errors.append("Missing metadata.source_type")

        # Check schema-specific keys
        if 'requirements' in schema:
            # This is a submission requirements schema
            pass  # Already has requirements
        elif 'structure' in schema:
            # This is a manuscript structure schema
            pass  # Already has structure
        else:
            errors.append("Missing either 'requirements' or 'structure' key")

        return (len(errors) == 0, errors)


if __name__ == '__main__':
    # Test schema builder
    test_requirements = {
        'word_limits': {
            'abstract': {'min': 150, 'max': 250},
            'introduction': {'max': 1000},
            'total_manuscript': {'max': 5000}
        },
        'section_requirements': {
            'required_sections': ['abstract', 'introduction', 'methods', 'results'],
            'section_order': ['abstract', 'introduction', 'methods', 'results', 'discussion']
        },
        'citation_style': {
            'style': 'Vancouver',
            'max_references': 50
        },
        'figure_table_limits': {
            'max_figures': 6,
            'max_tables': 4
        }
    }

    builder = SchemaBuilder()

    # Build submission schema
    submission_schema = builder.build_submission_schema(
        journal_name='Test Journal',
        requirements=test_requirements,
        source_type='test',
        source_path='/test/path'
    )

    # Validate
    valid, errors = builder.validate_schema(submission_schema)
    print(f"Schema valid: {valid}")
    if errors:
        print("Errors:", errors)
    else:
        print(json.dumps(submission_schema, indent=2))
