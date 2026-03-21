#!/usr/bin/env python3
"""
Journal Schema Generator - Main orchestrator for dynamic schema generation.

This module coordinates parsing, extraction, and schema building to generate
journal-specific JSON schemas from various sources.
"""

import json
from pathlib import Path
from typing import Dict, Optional, Tuple, Any
from datetime import datetime
import sys

# Add scripts directory to path
SCRIPTS_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPTS_DIR))

from rrwrite_document_parsers import create_parser, ParsingError
from rrwrite_requirement_extractor import RequirementExtractor, ExtractionError
from rrwrite_schema_builder import SchemaBuilder, SchemaBuilderError


class JournalSchemaGenerator:
    """
    Main orchestrator for generating journal-specific schemas.

    Coordinates parsing, extraction, and schema building to generate
    submission requirements and manuscript structure schemas.
    """

    def __init__(self, output_dir: Optional[Path] = None):
        """
        Initialize generator.

        Args:
            output_dir: Base output directory for schemas (defaults to schemas/journals)
        """
        if output_dir is None:
            repo_root = SCRIPTS_DIR.parent
            output_dir = repo_root / "schemas" / "journals"

        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize schema builder
        self.builder = SchemaBuilder()

        # Load or create index
        self.index_path = self.output_dir.parent / "journal_index.json"
        self.index = self._load_index()

    def _load_index(self) -> Dict[str, Any]:
        """Load journal schema index."""
        if self.index_path.exists():
            try:
                with open(self.index_path, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print(f"Warning: Could not load index, creating new one")

        return {
            'version': '1.0',
            'last_updated': datetime.now().isoformat(),
            'journals': {}
        }

    def _save_index(self):
        """Save journal schema index."""
        self.index['last_updated'] = datetime.now().isoformat()
        with open(self.index_path, 'w') as f:
            json.dump(self.index, f, indent=2)

    def _update_index(
        self,
        journal_key: str,
        journal_name: str,
        source_type: str,
        source_path: str
    ):
        """Update index with new journal entry."""
        self.index['journals'][journal_key] = {
            'name': journal_name,
            'key': journal_key,
            'source_type': source_type,
            'source_path': source_path,
            'generated_at': datetime.now().isoformat(),
            'schemas': {
                'submission': f"schemas/journals/{journal_key}/submission_requirements.json",
                'structure': f"schemas/journals/{journal_key}/manuscript_structure.json"
            },
            'validated': False
        }
        self._save_index()

    def check_cache(self, journal_key: str) -> Tuple[bool, Optional[Dict[str, Path]]]:
        """
        Check if schemas exist for a journal.

        Args:
            journal_key: Normalized journal identifier

        Returns:
            Tuple of (exists, schema_paths_dict)
        """
        journal_dir = self.output_dir / journal_key

        if not journal_dir.exists():
            return False, None

        submission_path = journal_dir / "submission_requirements.json"
        structure_path = journal_dir / "manuscript_structure.json"

        if submission_path.exists() and structure_path.exists():
            return True, {
                'submission': submission_path,
                'structure': structure_path,
                'metadata': journal_dir / "metadata.json"
            }

        return False, None

    def generate_from_url(
        self,
        journal_name: str,
        url: str,
        force: bool = False
    ) -> Tuple[bool, Dict[str, Path]]:
        """
        Generate schemas from journal website URL.

        Args:
            journal_name: Name of the journal
            url: URL to guidelines page
            force: Force regeneration even if cached

        Returns:
            Tuple of (success, schema_paths_dict)
        """
        journal_key = self._normalize_journal_key(journal_name)

        # Check cache
        if not force:
            cached, paths = self.check_cache(journal_key)
            if cached:
                print(f"Using cached schemas for {journal_name}")
                return True, paths

        try:
            # Parse HTML
            print(f"Fetching {url}...")
            parser = create_parser(url, 'html')
            parsed_data = parser.parse()

            # Extract requirements
            print("Extracting requirements...")
            extractor = RequirementExtractor(
                parser.get_text(),
                parsed_data
            )
            requirements = extractor.extract_all()

            # Generate schemas
            print("Generating schemas...")
            success = self._generate_and_save_schemas(
                journal_key=journal_key,
                journal_name=journal_name,
                requirements=requirements,
                source_type='url',
                source_path=url
            )

            if success:
                journal_dir = self.output_dir / journal_key
                paths = {
                    'submission': journal_dir / "submission_requirements.json",
                    'structure': journal_dir / "manuscript_structure.json",
                    'metadata': journal_dir / "metadata.json"
                }
                return True, paths

            return False, {}

        except (ParsingError, ExtractionError, SchemaBuilderError) as e:
            print(f"Error generating schemas: {e}")
            return False, {}

    def generate_from_file(
        self,
        journal_name: str,
        file_path: str,
        file_type: str,
        force: bool = False
    ) -> Tuple[bool, Dict[str, Path]]:
        """
        Generate schemas from uploaded file (PDF or DOCX).

        Args:
            journal_name: Name of the journal
            file_path: Path to guidelines file
            file_type: Type of file ('pdf' or 'docx')
            force: Force regeneration even if cached

        Returns:
            Tuple of (success, schema_paths_dict)
        """
        journal_key = self._normalize_journal_key(journal_name)

        # Check cache
        if not force:
            cached, paths = self.check_cache(journal_key)
            if cached:
                print(f"Using cached schemas for {journal_name}")
                return True, paths

        try:
            # Parse file
            print(f"Parsing {file_type.upper()} file...")
            parser = create_parser(file_path, file_type)
            parsed_data = parser.parse()

            # Extract requirements
            print("Extracting requirements...")
            extractor = RequirementExtractor(
                parser.get_text(),
                parsed_data
            )
            requirements = extractor.extract_all()

            # Generate schemas
            print("Generating schemas...")
            success = self._generate_and_save_schemas(
                journal_key=journal_key,
                journal_name=journal_name,
                requirements=requirements,
                source_type=file_type,
                source_path=file_path
            )

            if success:
                journal_dir = self.output_dir / journal_key
                paths = {
                    'submission': journal_dir / "submission_requirements.json",
                    'structure': journal_dir / "manuscript_structure.json",
                    'metadata': journal_dir / "metadata.json"
                }
                return True, paths

            return False, {}

        except (ParsingError, ExtractionError, SchemaBuilderError) as e:
            print(f"Error generating schemas: {e}")
            return False, {}

    def generate_from_yaml(
        self,
        journal_name: str,
        yaml_path: str,
        force: bool = False
    ) -> Tuple[bool, Dict[str, Path]]:
        """
        Generate schemas from existing YAML entry.

        Args:
            journal_name: Name of the journal
            yaml_path: Path to journal_guidelines.yaml
            force: Force regeneration even if cached

        Returns:
            Tuple of (success, schema_paths_dict)
        """
        journal_key = self._normalize_journal_key(journal_name)

        # Check cache
        if not force:
            cached, paths = self.check_cache(journal_key)
            if cached:
                print(f"Using cached schemas for {journal_name}")
                return True, paths

        try:
            # Parse YAML
            print(f"Converting YAML entry for {journal_name}...")
            parser = create_parser(yaml_path, 'yaml', journal_name=journal_name)
            yaml_data = parser.parse()

            # Convert YAML structure to requirements format
            requirements = self._yaml_to_requirements(yaml_data)

            # Generate schemas
            print("Generating schemas...")
            success = self._generate_and_save_schemas(
                journal_key=journal_key,
                journal_name=journal_name,
                requirements=requirements,
                source_type='yaml',
                source_path=yaml_path
            )

            if success:
                journal_dir = self.output_dir / journal_key
                paths = {
                    'submission': journal_dir / "submission_requirements.json",
                    'structure': journal_dir / "manuscript_structure.json",
                    'metadata': journal_dir / "metadata.json"
                }
                return True, paths

            return False, {}

        except (ParsingError, SchemaBuilderError) as e:
            print(f"Error generating schemas: {e}")
            return False, {}

    def _generate_and_save_schemas(
        self,
        journal_key: str,
        journal_name: str,
        requirements: Dict[str, Any],
        source_type: str,
        source_path: str
    ) -> bool:
        """Generate and save schemas for a journal."""
        try:
            # Create journal directory
            journal_dir = self.output_dir / journal_key
            journal_dir.mkdir(parents=True, exist_ok=True)

            # Build submission requirements schema
            submission_schema = self.builder.build_submission_schema(
                journal_name=journal_name,
                requirements=requirements,
                source_type=source_type,
                source_path=source_path
            )

            # Build manuscript structure schema
            structure_schema = self.builder.build_manuscript_schema(
                journal_name=journal_name,
                requirements=requirements,
                source_type=source_type
            )

            # Validate schemas
            valid_sub, errors_sub = self.builder.validate_schema(submission_schema)
            valid_str, errors_str = self.builder.validate_schema(structure_schema)

            if not (valid_sub and valid_str):
                print("Schema validation failed:")
                if errors_sub:
                    print("  Submission schema:", errors_sub)
                if errors_str:
                    print("  Structure schema:", errors_str)
                return False

            # Save schemas
            with open(journal_dir / "submission_requirements.json", 'w') as f:
                json.dump(submission_schema, f, indent=2)

            with open(journal_dir / "manuscript_structure.json", 'w') as f:
                json.dump(structure_schema, f, indent=2)

            # Save metadata
            metadata = {
                'journal_name': journal_name,
                'journal_key': journal_key,
                'source_type': source_type,
                'source_path': source_path,
                'generated_at': datetime.now().isoformat(),
                'validated': False
            }
            with open(journal_dir / "metadata.json", 'w') as f:
                json.dump(metadata, f, indent=2)

            # Update index
            self._update_index(journal_key, journal_name, source_type, source_path)

            print(f"✓ Schemas generated and cached for {journal_name}")
            return True

        except Exception as e:
            print(f"Error saving schemas: {e}")
            return False

    def _yaml_to_requirements(self, yaml_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert YAML journal entry to requirements format."""
        requirements = {}

        # Extract word limits
        if 'word_limits' in yaml_data:
            requirements['word_limits'] = yaml_data['word_limits']

        # Extract section requirements
        if 'sections' in yaml_data:
            section_list = yaml_data['sections']
            requirements['section_requirements'] = {
                'required_sections': [s for s in section_list if s != 'optional'],
                'optional_sections': [],
                'section_order': section_list
            }

        # Extract citation requirements
        if 'citation_style' in yaml_data or 'max_references' in yaml_data:
            requirements['citation_style'] = {
                'style': yaml_data.get('citation_style', 'Unknown'),
                'max_references': yaml_data.get('max_references')
            }

        # Extract figure/table limits
        requirements['figure_table_limits'] = {}
        if 'max_figures' in yaml_data:
            requirements['figure_table_limits']['max_figures'] = yaml_data['max_figures']
        if 'max_tables' in yaml_data:
            requirements['figure_table_limits']['max_tables'] = yaml_data['max_tables']

        # Extract formatting
        if 'format' in yaml_data:
            requirements['formatting_rules'] = yaml_data['format']

        # Extract special requirements
        if 'special_requirements' in yaml_data:
            spec_req = yaml_data['special_requirements']
            if isinstance(spec_req, list):
                requirements['special_requirements'] = [
                    {'requirement': req, 'priority': 'mandatory'}
                    for req in spec_req
                ]

        return requirements

    def _normalize_journal_key(self, journal_name: str) -> str:
        """Generate normalized key from journal name."""
        # Remove special characters and convert to lowercase
        key = journal_name.lower()
        key = key.replace('the ', '')
        key = key.replace('journal of ', '')
        key = ''.join(c if c.isalnum() or c == ' ' else '' for c in key)
        key = key.replace(' ', '_')
        return key


if __name__ == '__main__':
    # Test generator
    generator = JournalSchemaGenerator()

    # Test YAML conversion
    yaml_path = SCRIPTS_DIR.parent / "templates" / "journal_guidelines.yaml"
    if yaml_path.exists():
        success, paths = generator.generate_from_yaml(
            journal_name="Bioinformatics",
            yaml_path=str(yaml_path)
        )
        print(f"\nGeneration {'succeeded' if success else 'failed'}")
        if paths:
            print("Schema paths:")
            for key, path in paths.items():
                print(f"  {key}: {path}")
