#!/usr/bin/env python3
"""
Tests for evidence import and validation functionality.
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import json
import pandas as pd
import sys

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from rrwrite_validate_evidence_tool import (
    validate_doi,
    check_freshness,
    extract_year_from_citation,
    validate_evidence_file,
    generate_validation_summary
)

from rrwrite_import_evidence_tool import (
    detect_previous_version,
    validate_source_evidence,
    import_citations_bib,
    merge_evidence
)


class TestDOIValidation(unittest.TestCase):
    """Test DOI validation functions."""

    def test_validate_doi_valid(self):
        """Test validation with a known valid DOI."""
        # Use a real, stable DOI (AlphaFold Nature paper)
        result = validate_doi("10.1038/s41586-021-03819-2")
        # Accept valid or unknown (network issues), but not invalid
        self.assertIn(result, ["valid", "unknown"])

    def test_validate_doi_invalid(self):
        """Test validation with clearly invalid DOI."""
        result = validate_doi("10.9999/invalid.fake.doi.12345")
        self.assertIn(result, ["invalid", "unknown"])

    def test_validate_doi_empty(self):
        """Test validation with empty DOI."""
        result = validate_doi("")
        self.assertEqual(result, "invalid")

    def test_validate_doi_with_prefix(self):
        """Test validation with DOI that includes https:// prefix."""
        result = validate_doi("https://doi.org/10.1038/s41586-021-03819-2")
        self.assertIn(result, ["valid", "unknown"])


class TestFreshnessCheck(unittest.TestCase):
    """Test paper freshness checking."""

    def test_check_freshness_fresh(self):
        """Test freshness for recent paper."""
        result = check_freshness(2024, current_year=2026)
        self.assertEqual(result, "fresh")

    def test_check_freshness_stale(self):
        """Test freshness for 5-10 year old paper."""
        result = check_freshness(2019, current_year=2026)
        self.assertEqual(result, "stale")

    def test_check_freshness_old(self):
        """Test freshness for >10 year old paper."""
        result = check_freshness(2010, current_year=2026)
        self.assertEqual(result, "old")

    def test_extract_year_from_citation(self):
        """Test year extraction from citations."""
        cases = [
            ("Author et al. (2024)", 2024),
            ("Smith and Jones (2020)", 2020),
            ("Multiple Authors 2019", 2019),
        ]
        for citation, expected_year in cases:
            with self.subTest(citation=citation):
                result = extract_year_from_citation(citation)
                self.assertEqual(result, expected_year)


class TestEvidenceFileValidation(unittest.TestCase):
    """Test evidence CSV validation."""

    def setUp(self):
        """Set up test directory and files."""
        self.test_dir = tempfile.mkdtemp()
        self.test_csv = Path(self.test_dir) / "test_evidence.csv"

    def tearDown(self):
        """Clean up test directory."""
        shutil.rmtree(self.test_dir)

    def test_validate_evidence_file_structure(self):
        """Test validation of evidence file structure."""
        # Create test CSV
        df = pd.DataFrame({
            "doi": ["10.1038/nature", "10.1126/science"],
            "citation_key": ["nature2024", "science2024"],
            "citation": ["Nature Authors (2024)", "Science Team (2024)"],
            "evidence_quote": ["Quote 1", "Quote 2"]
        })
        df.to_csv(self.test_csv, index=False)

        # Validate (skip DOI checks for speed)
        result = validate_evidence_file(
            self.test_csv,
            validate_dois=False,
            check_freshness_flag=True
        )

        # Check structure
        self.assertEqual(len(result), 2)
        self.assertIn("doi_status", result.columns)
        self.assertIn("freshness", result.columns)
        self.assertIn("action", result.columns)
        self.assertIn("reason", result.columns)

    def test_validate_evidence_missing_columns(self):
        """Test validation with missing required columns."""
        # Create CSV with missing columns
        df = pd.DataFrame({
            "doi": ["10.1038/nature"],
            "citation_key": ["nature2024"]
            # Missing: citation, evidence_quote
        })
        df.to_csv(self.test_csv, index=False)

        # Should exit with error
        with self.assertRaises(SystemExit):
            validate_evidence_file(self.test_csv)

    def test_generate_validation_summary(self):
        """Test validation summary generation."""
        # Create validated DataFrame
        df = pd.DataFrame({
            "doi_status": ["valid", "valid", "invalid"],
            "freshness": ["fresh", "stale", "fresh"],
            "action": ["keep", "review", "remove"]
        })

        summary = generate_validation_summary(df)

        self.assertEqual(summary["total_papers"], 3)
        self.assertEqual(summary["valid_papers"], 1)
        self.assertEqual(summary["needs_review"], 1)
        self.assertEqual(summary["to_remove"], 1)


class TestVersionDetection(unittest.TestCase):
    """Test previous version detection."""

    def setUp(self):
        """Set up test directory structure."""
        self.test_dir = tempfile.mkdtemp()
        self.parent_dir = Path(self.test_dir)

    def tearDown(self):
        """Clean up test directory."""
        shutil.rmtree(self.test_dir)

    def test_detect_previous_version_found(self):
        """Test detection when previous version exists."""
        # Create v1 with completed research
        v1_dir = self.parent_dir / "manuscript_v1"
        v1_state_dir = v1_dir / ".rrwrite"
        v1_state_dir.mkdir(parents=True)

        state = {
            "created_at": "2026-02-01T10:00:00",
            "workflow_status": {
                "research": {
                    "status": "completed",
                    "papers_found": 20
                }
            }
        }

        with open(v1_state_dir / "state.json", "w") as f:
            json.dump(state, f)

        # Create v2 (current)
        v2_dir = self.parent_dir / "manuscript_v2"
        v2_dir.mkdir()

        # Detect from v2
        result = detect_previous_version(v2_dir)

        self.assertIsNotNone(result)
        detected_path, detected_state = result
        # Resolve paths to handle symlinks (/var vs /private/var)
        self.assertEqual(detected_path.resolve(), v1_dir.resolve())
        self.assertEqual(detected_state["workflow_status"]["research"]["papers_found"], 20)

    def test_detect_previous_version_not_found(self):
        """Test detection when no previous version exists."""
        # Create v1 without completed research
        v1_dir = self.parent_dir / "manuscript_v1"
        v1_state_dir = v1_dir / ".rrwrite"
        v1_state_dir.mkdir(parents=True)

        state = {
            "created_at": "2026-02-01T10:00:00",
            "workflow_status": {
                "research": {
                    "status": "not_started",
                    "papers_found": 0
                }
            }
        }

        with open(v1_state_dir / "state.json", "w") as f:
            json.dump(state, f)

        # Create v2 (current)
        v2_dir = self.parent_dir / "manuscript_v2"
        v2_dir.mkdir()

        # Detect from v2
        result = detect_previous_version(v2_dir)

        self.assertIsNone(result)

    def test_detect_most_recent_version(self):
        """Test that most recent version is detected when multiple exist."""
        # Create v1
        v1_dir = self.parent_dir / "manuscript_v1"
        v1_state_dir = v1_dir / ".rrwrite"
        v1_state_dir.mkdir(parents=True)

        state_v1 = {
            "created_at": "2026-02-01T10:00:00",
            "workflow_status": {
                "research": {"status": "completed", "papers_found": 15}
            }
        }

        with open(v1_state_dir / "state.json", "w") as f:
            json.dump(state_v1, f)

        # Create v2 (more recent)
        v2_dir = self.parent_dir / "manuscript_v2"
        v2_state_dir = v2_dir / ".rrwrite"
        v2_state_dir.mkdir(parents=True)

        state_v2 = {
            "created_at": "2026-02-05T10:00:00",
            "workflow_status": {
                "research": {"status": "completed", "papers_found": 20}
            }
        }

        with open(v2_state_dir / "state.json", "w") as f:
            json.dump(state_v2, f)

        # Create v3 (current)
        v3_dir = self.parent_dir / "manuscript_v3"
        v3_dir.mkdir()

        # Detect from v3
        result = detect_previous_version(v3_dir)

        self.assertIsNotNone(result)
        detected_path, detected_state = result
        # Should detect v2 (most recent) - resolve paths for symlink handling
        self.assertEqual(detected_path.resolve(), v2_dir.resolve())
        self.assertEqual(detected_state["workflow_status"]["research"]["papers_found"], 20)


class TestSourceValidation(unittest.TestCase):
    """Test source evidence validation."""

    def setUp(self):
        """Set up test directory."""
        self.test_dir = tempfile.mkdtemp()
        self.source_dir = Path(self.test_dir) / "source"
        self.source_dir.mkdir()

    def tearDown(self):
        """Clean up test directory."""
        shutil.rmtree(self.test_dir)

    def test_validate_source_evidence_complete(self):
        """Test validation with all required files."""
        # Create required files
        (self.source_dir / "literature_evidence.csv").touch()
        (self.source_dir / "literature_citations.bib").touch()
        (self.source_dir / "literature.md").touch()

        is_valid, error = validate_source_evidence(self.source_dir)
        self.assertTrue(is_valid)
        self.assertEqual(error, "")

    def test_validate_source_evidence_missing_files(self):
        """Test validation with missing files."""
        # Create only one file
        (self.source_dir / "literature.md").touch()

        is_valid, error = validate_source_evidence(self.source_dir)
        self.assertFalse(is_valid)
        self.assertIn("Missing files", error)


class TestEvidenceMerge(unittest.TestCase):
    """Test evidence merging."""

    def setUp(self):
        """Set up test directory."""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)

    def tearDown(self):
        """Clean up test directory."""
        shutil.rmtree(self.test_dir)

    def test_merge_evidence_no_duplicates(self):
        """Test merging without duplicates."""
        # Create old evidence
        old_df = pd.DataFrame({
            "doi": ["10.1038/nature1", "10.1038/nature2"],
            "citation_key": ["nature1", "nature2"],
            "citation": ["Citation 1", "Citation 2"],
            "evidence_quote": ["Quote 1", "Quote 2"]
        })
        old_csv = self.test_path / "old.csv"
        old_df.to_csv(old_csv, index=False)

        # Create new evidence
        new_df = pd.DataFrame({
            "doi": ["10.1038/nature3", "10.1038/nature4"],
            "citation_key": ["nature3", "nature4"],
            "citation": ["Citation 3", "Citation 4"],
            "evidence_quote": ["Quote 3", "Quote 4"]
        })
        new_csv = self.test_path / "new.csv"
        new_df.to_csv(new_csv, index=False)

        # Merge
        output_csv = self.test_path / "merged.csv"
        stats = merge_evidence(old_csv, new_csv, output_csv)

        # Check stats
        self.assertEqual(stats["papers_old"], 2)
        self.assertEqual(stats["papers_new"], 2)
        self.assertEqual(stats["papers_merged"], 4)
        self.assertEqual(stats["duplicates_removed"], 0)

        # Check merged file
        merged_df = pd.read_csv(output_csv)
        self.assertEqual(len(merged_df), 4)

    def test_merge_evidence_with_duplicates(self):
        """Test merging with duplicate DOIs."""
        # Create old evidence
        old_df = pd.DataFrame({
            "doi": ["10.1038/nature1", "10.1038/nature2"],
            "citation_key": ["nature1", "nature2"],
            "citation": ["Citation 1", "Citation 2"],
            "evidence_quote": ["Old quote 2", "Old quote 2"]
        })
        old_csv = self.test_path / "old.csv"
        old_df.to_csv(old_csv, index=False)

        # Create new evidence (with one duplicate DOI)
        new_df = pd.DataFrame({
            "doi": ["10.1038/nature2", "10.1038/nature3"],
            "citation_key": ["nature2", "nature3"],
            "citation": ["Citation 2", "Citation 3"],
            "evidence_quote": ["New quote 2", "Quote 3"]
        })
        new_csv = self.test_path / "new.csv"
        new_df.to_csv(new_csv, index=False)

        # Merge
        output_csv = self.test_path / "merged.csv"
        stats = merge_evidence(old_csv, new_csv, output_csv)

        # Check stats
        self.assertEqual(stats["papers_old"], 2)
        self.assertEqual(stats["papers_new"], 2)
        self.assertEqual(stats["papers_merged"], 3)  # One duplicate removed
        self.assertEqual(stats["duplicates_removed"], 1)

        # Check merged file (should keep new version of duplicate)
        merged_df = pd.read_csv(output_csv)
        self.assertEqual(len(merged_df), 3)

        # Find the duplicate entry
        nature2 = merged_df[merged_df["doi"] == "10.1038/nature2"]
        self.assertEqual(len(nature2), 1)
        # Should keep the new quote (last occurrence)
        self.assertEqual(nature2.iloc[0]["evidence_quote"], "New quote 2")


class TestCitationBibImport(unittest.TestCase):
    """Test .bib file import and filtering."""

    def setUp(self):
        """Set up test directory."""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)

    def tearDown(self):
        """Clean up test directory."""
        shutil.rmtree(self.test_dir)

    def test_import_citations_bib_filtering(self):
        """Test that .bib import filters to valid citation keys."""
        # Create source .bib
        bib_content = """@article{nature2024,
  title={Nature Paper},
  author={Author, First},
  journal={Nature},
  year={2024},
  doi={10.1038/nature}
}

@article{science2024,
  title={Science Paper},
  author={Author, Second},
  journal={Science},
  year={2024},
  doi={10.1126/science}
}

@article{removed2023,
  title={Removed Paper},
  author={Author, Third},
  journal={Journal},
  year={2023},
  doi={10.9999/removed}
}
"""
        source_bib = self.test_path / "source.bib"
        with open(source_bib, "w") as f:
            f.write(bib_content)

        # Create evidence CSV (only includes nature2024 and science2024)
        evidence_df = pd.DataFrame({
            "doi": ["10.1038/nature", "10.1126/science"],
            "citation_key": ["nature2024", "science2024"],
            "citation": ["Citation 1", "Citation 2"],
            "evidence_quote": ["Quote 1", "Quote 2"]
        })
        evidence_csv = self.test_path / "evidence.csv"
        evidence_df.to_csv(evidence_csv, index=False)

        # Import and filter
        target_bib = self.test_path / "target.bib"
        import_citations_bib(source_bib, evidence_csv, target_bib)

        # Read filtered .bib
        with open(target_bib, "r") as f:
            filtered_content = f.read()

        # Check that only valid entries are included
        self.assertIn("nature2024", filtered_content)
        self.assertIn("science2024", filtered_content)
        self.assertNotIn("removed2023", filtered_content)


def run_tests():
    """Run all tests."""
    unittest.main(argv=[''], exit=False, verbosity=2)


if __name__ == "__main__":
    run_tests()
