#!/usr/bin/env python3
"""
RRWrite State Manager

Manages workflow state for the RRWrite manuscript generation system.
Tracks progress through planning, assessment, research, drafting, and critique phases.

State is stored in: {manuscript_dir}/.rrwrite/state.json
"""

import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
import logging

# Import GitManager for version control
try:
    from rrwrite_git import GitManager, GitSafetyError, install_tool_repo_protection
except ImportError:
    # Fallback if running from different directory
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from rrwrite_git import GitManager, GitSafetyError, install_tool_repo_protection


class StateManager:
    """Manages RRWrite workflow state."""

    def __init__(self, output_dir: str = "manuscript", enable_git: bool = True, auto_commit: bool = True):
        """Initialize state manager.

        Args:
            output_dir: Base output directory for manuscript files
            enable_git: Enable Git version control for manuscripts
            auto_commit: Automatically commit after completing workflow stages
        """
        self.manuscript_dir = Path(output_dir).resolve()
        self.state_dir = self.manuscript_dir / ".rrwrite"
        self.state_file = self.state_dir / "state.json"
        self.logger = logging.getLogger(__name__)

        # Initialize state structure if needed
        self._init_state()

        # Initialize Git manager (with safety checks)
        self.git_manager = None
        if enable_git:
            self._init_git_manager(auto_commit=auto_commit)

    def _init_state(self):
        """Initialize state structure if it doesn't exist."""
        if not self.state_file.exists():
            self.state = self._create_initial_state()
            self._save_state()
        else:
            self._load_state()

    def _create_initial_state(self) -> Dict[str, Any]:
        """Create initial state structure."""
        return {
            "version": "1.0",
            "created_at": self._get_timestamp(),
            "last_updated": self._get_timestamp(),
            "manuscript_dir": str(self.manuscript_dir),
            "repository_path": None,
            "target_journal": None,

            "workflow_status": {
                "repository_analysis": {
                    "status": "not_started",
                    "file": None,
                    "completed_at": None,
                    "git_commit": None
                },
                "plan": {
                    "status": "not_started",
                    "file": None,
                    "target_journal": None,
                    "completed_at": None,
                    "git_commit": None
                },
                "assessment": {
                    "status": "not_started",
                    "file": None,
                    "journal_initial": None,
                    "journal_confirmed": None,
                    "compatibility_score": None,
                    "required_adjustments": 0,
                    "guidelines_path": None,
                    "completed_at": None,
                    "git_commit": None
                },
                "research": {
                    "status": "not_started",
                    "file": None,
                    "topics_count": 0,
                    "papers_found": 0,
                    "papers_from_previous": 0,
                    "papers_new": 0,
                    "source_version": None,
                    "validation_summary": None,
                    "completed_at": None,
                    "git_commit": None
                },
                "figure_table_extraction": {
                    "status": "not_started",
                    "figures_from_repo": 0,
                    "figures_generated": 0,
                    "tables_from_repo": 0,
                    "tables_generated": 0,
                    "figure_manifest_path": None,
                    "table_manifest_path": None,
                    "scripts_parsed": 0,
                    "completed_at": None,
                    "git_commit": None
                },
                "drafting": {
                    "status": "not_started",
                    "sections": {
                        "abstract": {"status": "not_started", "file": None, "completed_at": None},
                        "introduction": {"status": "not_started", "file": None, "completed_at": None},
                        "methods": {"status": "not_started", "file": None, "completed_at": None},
                        "results": {"status": "not_started", "file": None, "completed_at": None},
                        "discussion": {"status": "not_started", "file": None, "completed_at": None},
                        "availability": {"status": "not_started", "file": None, "completed_at": None}
                    },
                    "completed_sections": 0,
                    "total_sections": 6,
                    "completed_at": None,
                    "git_commit": None
                },
                "assembly": {
                    "status": "not_started",
                    "file": None,
                    "manifest_file": None,
                    "sections_included": 0,
                    "sections_missing": 0,
                    "total_word_count": 0,
                    "validation_warnings": 0,
                    "completed_at": None,
                    "git_commit": None
                },
                "critique": {
                    "status": "not_started",
                    "file": None,
                    "issues_found": 0,
                    "issues_major": 0,
                    "issues_minor": 0,
                    "completed_at": None,
                    "git_commit": None
                },
                "revision": {
                    "status": "not_started",
                    "max_revisions": 0,
                    "current_iteration": 0,
                    "iterations": [],
                    "convergence_status": None,
                    "convergence_reason": None,
                    "completed_at": None,
                    "git_commit": None
                }
            },

            "files": {
                "repository_analysis": None,
                "outline": None,
                "assessment_report": None,
                "author_guidelines": None,
                "literature_review": None,
                "sections": {},
                "critique_report": None,
                "final_manuscript": None
            },

            "metadata": {
                "total_word_count": 0,
                "citations_count": 0,
                "figures_count": 0,
                "tables_count": 0,
                "data_tables_generated": False
            }
        }

    def _load_state(self):
        """Load state from JSON file."""
        with open(self.state_file, 'r') as f:
            self.state = json.load(f)

    def _save_state(self):
        """Save state to JSON file."""
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.state["last_updated"] = self._get_timestamp()

        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)

    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        return datetime.now().isoformat()

    def _init_git_manager(self, auto_commit: bool = True):
        """Initialize Git manager for manuscript version control.

        This creates a SEPARATE git repository in the manuscript directory,
        completely independent of the RRWrite tool repository.

        Args:
            auto_commit: Enable automatic commits
        """
        try:
            # Create GitManager (includes safety checks)
            self.git_manager = GitManager(
                manuscript_dir=self.manuscript_dir,
                auto_commit=auto_commit,
                verbose=True
            )

            # Initialize git repository if needed
            if self.git_manager.initialize_repository():
                self.logger.info(f"✓ Git initialized for manuscript: {self.manuscript_dir}")
                # Update state to track git initialization
                if "git" not in self.state:
                    self.state["git"] = {}
                self.state["git"]["repository_initialized"] = True
                self.state["git"]["initialized_at"] = self._get_timestamp()
                self._save_state()
            else:
                self.logger.info(f"✓ Using existing git repository: {self.manuscript_dir}")

        except GitSafetyError as e:
            # Safety violation - log error but don't crash
            self.logger.error(f"Git initialization failed (safety check): {e}")
            self.git_manager = None
        except Exception as e:
            self.logger.warning(f"Git initialization failed: {e}")
            self.git_manager = None

    def _get_git_commit(self) -> Optional[str]:
        """Get current git commit hash from manuscript repository."""
        if self.git_manager:
            commit = self.git_manager.get_current_commit()
            if commit:
                return commit[:7]  # Short hash
        return None

    def commit_stage(self, files: List[str], stage: str, description: str, **metadata):
        """Commit files for a workflow stage.

        Args:
            files: List of files to commit (relative paths)
            stage: Workflow stage name
            description: Commit description
            **metadata: Additional metadata for commit message
        """
        if not self.git_manager:
            return None

        try:
            return self.git_manager.commit(
                files=files,
                stage=stage,
                description=description,
                metadata=metadata
            )
        except GitSafetyError as e:
            self.logger.error(f"Commit failed (safety check): {e}")
            return None
        except Exception as e:
            self.logger.warning(f"Commit failed: {e}")
            return None

    # ===== Workflow Stage Updates =====

    def update_workflow_stage(self, stage: str, status: str, **kwargs):
        """Update a workflow stage with arbitrary data.

        Args:
            stage: Stage name (e.g., 'plan', 'assessment', 'research')
            status: Status value (e.g., 'in_progress', 'completed')
            **kwargs: Additional stage-specific data
        """
        if stage not in self.state["workflow_status"]:
            raise ValueError(f"Unknown workflow stage: {stage}")

        self.state["workflow_status"][stage]["status"] = status

        # Update stage-specific fields
        for key, value in kwargs.items():
            self.state["workflow_status"][stage][key] = value

        # Add timestamp if completing
        if status == "completed":
            self.state["workflow_status"][stage]["completed_at"] = self._get_timestamp()
            self.state["workflow_status"][stage]["git_commit"] = self._get_git_commit()

        self._save_state()

    def update_assessment_stage(
        self,
        journal_initial: str,
        journal_confirmed: str,
        compatibility_score: float,
        required_adjustments: int,
        guidelines_path: str,
        assessment_file: str
    ):
        """Update assessment workflow stage with journal evaluation results.

        Args:
            journal_initial: Initially proposed journal
            journal_confirmed: User-confirmed journal selection
            compatibility_score: Compatibility score (0.0-1.0)
            required_adjustments: Number of required outline adjustments
            guidelines_path: Path to generated author guidelines
            assessment_file: Path to assessment report
        """
        self.state["workflow_status"]["assessment"] = {
            "status": "completed",
            "file": assessment_file,
            "journal_initial": journal_initial,
            "journal_confirmed": journal_confirmed,
            "compatibility_score": compatibility_score,
            "required_adjustments": required_adjustments,
            "guidelines_path": guidelines_path,
            "completed_at": self._get_timestamp(),
            "git_commit": self._get_git_commit()
        }

        # Update target journal in main state if journal changed
        if journal_confirmed != journal_initial:
            self.state["target_journal"] = journal_confirmed
            print(f"✓ Target journal updated: {journal_initial} → {journal_confirmed}")
        else:
            self.state["target_journal"] = journal_confirmed

        # Update files tracking
        self.state["files"]["assessment_report"] = assessment_file
        self.state["files"]["author_guidelines"] = guidelines_path

        self._save_state()

    def update_research_with_import(
        self,
        source_version: str,
        papers_imported: int,
        papers_new: int,
        validation_summary: dict
    ):
        """Update research stage with import metadata.

        Args:
            source_version: Path to source version directory
            papers_imported: Number of papers imported from previous version
            papers_new: Number of newly found papers
            validation_summary: Validation summary dictionary
        """
        total_papers = papers_imported + papers_new

        self.state["workflow_status"]["research"] = {
            "status": "completed",
            "file": f"{self.manuscript_dir}/literature.md",
            "papers_found": total_papers,
            "papers_from_previous": papers_imported,
            "papers_new": papers_new,
            "source_version": source_version,
            "validation_summary": validation_summary,
            "completed_at": self._get_timestamp(),
            "git_commit": self._get_git_commit()
        }
        self._save_state()

    def update_figure_table_extraction(
        self,
        figures_from_repo: int,
        figures_generated: int,
        tables_from_repo: int,
        tables_generated: int,
        figure_manifest_path: Optional[str] = None,
        table_manifest_path: Optional[str] = None,
        scripts_parsed: int = 0
    ):
        """Update figure_table_extraction workflow stage.

        Args:
            figures_from_repo: Number of figures extracted from repository
            figures_generated: Number of figures generated from analysis
            tables_from_repo: Number of tables extracted from repository
            tables_generated: Number of tables generated from analysis
            figure_manifest_path: Path to figure manifest JSON
            table_manifest_path: Path to table manifest JSON
            scripts_parsed: Number of scripts parsed for figure/table generation info
        """
        total_figures = figures_from_repo + figures_generated
        total_tables = tables_from_repo + tables_generated

        self.state["workflow_status"]["figure_table_extraction"] = {
            "status": "completed",
            "figures_from_repo": figures_from_repo,
            "figures_generated": figures_generated,
            "tables_from_repo": tables_from_repo,
            "tables_generated": tables_generated,
            "figure_manifest_path": figure_manifest_path,
            "table_manifest_path": table_manifest_path,
            "scripts_parsed": scripts_parsed,
            "completed_at": self._get_timestamp(),
            "git_commit": self._get_git_commit()
        }

        # Update metadata
        self.state["metadata"]["figures_count"] = total_figures
        self.state["metadata"]["tables_count"] = total_tables

        self._save_state()

        # Commit to git if enabled
        if self.git_manager:
            files_to_commit = []
            if figure_manifest_path:
                files_to_commit.append(figure_manifest_path)
            if table_manifest_path:
                files_to_commit.append(table_manifest_path)

            # Add figure and table directories
            files_to_commit.extend([
                "figures/from_repo",
                "figures/generated",
                "tables/from_repo",
                "tables/generated"
            ])

            self.git_manager.commit(
                message=f"Extract figures/tables: {total_figures} figures, {total_tables} tables",
                files=files_to_commit
            )

    def update_repository_analysis(
        self,
        analysis_file: str,
        repo_path: str,
        file_counts: Dict[str, int],
        topics_detected: List[str],
        data_tables: Optional[Dict[str, str]] = None
    ):
        """Update repository analysis workflow stage.

        Args:
            analysis_file: Path to generated analysis.md file
            repo_path: Repository path or URL that was analyzed
            file_counts: Dict mapping file types to counts {'data': N, 'scripts': N, 'figures': N}
            topics_detected: List of inferred research topics
            data_tables: Optional dict mapping table names to file paths
        """
        self.state["workflow_status"]["repository_analysis"] = {
            "status": "completed",
            "file": analysis_file,
            "repo_path": repo_path,
            "file_counts": file_counts,
            "topics_detected": topics_detected,
            "completed_at": self._get_timestamp(),
            "git_commit": self._get_git_commit()
        }

        # Track data tables if generated
        if data_tables:
            self.state["workflow_status"]["repository_analysis"]["data_tables"] = data_tables
            self.state["metadata"]["tables_count"] = len(data_tables)
            self.state["metadata"]["data_tables_generated"] = True

        # Update main state fields
        self.state["repository_path"] = repo_path
        self.state["files"]["repository_analysis"] = analysis_file

        self._save_state()

        print(f"✓ Repository analysis completed: {analysis_file}")
        print(f"  Analyzed: {repo_path}")
        print(f"  Topics detected: {len(topics_detected)}")
        if data_tables:
            print(f"  Data tables generated: {len(data_tables)}")

    def update_section_status(
        self,
        section: str,
        status: str,
        file_path: Optional[str] = None,
        table_count: Optional[int] = None
    ):
        """Update status of a specific manuscript section.

        Args:
            section: Section name (e.g., 'introduction', 'methods')
            status: Status value (e.g., 'in_progress', 'completed')
            file_path: Path to the section file
            table_count: Number of tables in the section
        """
        if section not in self.state["workflow_status"]["drafting"]["sections"]:
            # Add new section dynamically
            self.state["workflow_status"]["drafting"]["sections"][section] = {
                "status": "not_started",
                "file": None,
                "completed_at": None
            }
            self.state["workflow_status"]["drafting"]["total_sections"] += 1

        self.state["workflow_status"]["drafting"]["sections"][section]["status"] = status

        if file_path:
            self.state["workflow_status"]["drafting"]["sections"][section]["file"] = file_path
            self.state["files"]["sections"][section] = file_path

        if status == "completed":
            self.state["workflow_status"]["drafting"]["sections"][section]["completed_at"] = self._get_timestamp()

            # Track table count if provided
            if table_count is not None:
                self.state["workflow_status"]["drafting"]["sections"][section]["table_count"] = table_count

                # Update total table count in metadata
                total_tables = sum(
                    s.get("table_count", 0)
                    for s in self.state["workflow_status"]["drafting"]["sections"].values()
                )
                self.state["metadata"]["tables_count"] = total_tables

            # Update completed count
            completed = sum(
                1 for s in self.state["workflow_status"]["drafting"]["sections"].values()
                if s["status"] == "completed"
            )
            self.state["workflow_status"]["drafting"]["completed_sections"] = completed

            # Mark overall drafting as completed if all sections done
            total = self.state["workflow_status"]["drafting"]["total_sections"]
            if completed == total:
                self.state["workflow_status"]["drafting"]["status"] = "completed"
                self.state["workflow_status"]["drafting"]["completed_at"] = self._get_timestamp()
                self.state["workflow_status"]["drafting"]["git_commit"] = self._get_git_commit()

        self._save_state()

    # ===== Query Methods =====

    def get_stage_status(self, stage: str) -> str:
        """Get status of a workflow stage."""
        if stage not in self.state["workflow_status"]:
            return "not_started"
        return self.state["workflow_status"][stage]["status"]

    def get_target_journal(self) -> Optional[str]:
        """Get the target journal."""
        return self.state.get("target_journal")

    def get_guidelines_path(self) -> Optional[str]:
        """Get path to author guidelines if available."""
        return self.state["workflow_status"]["assessment"].get("guidelines_path")

    def get_compatibility_score(self) -> Optional[float]:
        """Get journal compatibility score from assessment."""
        return self.state["workflow_status"]["assessment"].get("compatibility_score")

    def is_stage_completed(self, stage: str) -> bool:
        """Check if a workflow stage is completed."""
        return self.get_stage_status(stage) == "completed"

    def get_completed_sections(self) -> list:
        """Get list of completed manuscript sections."""
        sections = self.state["workflow_status"]["drafting"]["sections"]
        return [
            name for name, data in sections.items()
            if data["status"] == "completed"
        ]

    def get_progress_summary(self) -> Dict[str, Any]:
        """Get overall progress summary."""
        stages = self.state["workflow_status"]

        total_stages = len([s for s in stages.keys() if s != "drafting"])
        completed_stages = len([
            s for s, data in stages.items()
            if s != "drafting" and data["status"] == "completed"
        ])

        # Add drafting progress
        if stages["drafting"]["status"] == "completed":
            completed_stages += 1
            total_stages += 1
        elif stages["drafting"]["status"] != "not_started":
            total_stages += 1

        return {
            "total_stages": total_stages,
            "completed_stages": completed_stages,
            "current_stage": self._get_current_stage(),
            "progress_percentage": (completed_stages / total_stages * 100) if total_stages > 0 else 0,
            "sections_completed": stages["drafting"]["completed_sections"],
            "sections_total": stages["drafting"]["total_sections"]
        }

    def _get_current_stage(self) -> str:
        """Determine the current workflow stage."""
        stages_order = [
            "repository_analysis",
            "plan",
            "assessment",
            "research",
            "figure_table_extraction",
            "drafting",
            "critique",
            "revision"
        ]

        for stage in stages_order:
            status = self.get_stage_status(stage)
            if status == "in_progress":
                return stage
            elif status == "not_started":
                return stage

        return "completed"

    # ===== Revision Stage Methods =====

    def start_revision(self, max_revisions: int):
        """Initialize revision tracking.

        Args:
            max_revisions: Maximum number of revision iterations
        """
        self.state["workflow_status"]["revision"] = {
            "status": "in_progress",
            "max_revisions": max_revisions,
            "current_iteration": 0,
            "iterations": [],
            "convergence_status": None,
            "convergence_reason": None,
            "completed_at": None,
            "git_commit": None
        }
        self._save_state()

    def update_revision_iteration(
        self,
        iteration: int,
        sections_revised: List[str],
        metrics_before: Dict[str, int],
        metrics_after: Dict[str, int],
        critique_files: Dict[str, str]
    ):
        """Record a revision iteration.

        Args:
            iteration: Iteration number
            sections_revised: List of sections that were revised
            metrics_before: Issue counts before revision
            metrics_after: Issue counts after revision
            critique_files: Paths to critique files generated
        """
        major_resolved = metrics_before['major'] - metrics_after['major']
        minor_resolved = metrics_before['minor'] - metrics_after['minor']

        improvement_rate = (
            major_resolved / metrics_before['major']
            if metrics_before['major'] > 0
            else 0.0
        )

        iteration_data = {
            "iteration": iteration,
            "sections_revised": sections_revised,
            "issues_before": metrics_before,
            "issues_after": metrics_after,
            "convergence_metrics": {
                "major_resolved": major_resolved,
                "minor_resolved": minor_resolved,
                "improvement_rate": improvement_rate
            },
            "critique_files": critique_files,
            "git_commit": self._get_git_commit(),
            "timestamp": self._get_timestamp()
        }

        self.state["workflow_status"]["revision"]["iterations"].append(iteration_data)
        self.state["workflow_status"]["revision"]["current_iteration"] = iteration
        self._save_state()

    def check_revision_convergence(
        self,
        metrics_after: Dict[str, int],
        iteration: int,
        max_revisions: int,
        improvement_rate: float,
        min_improvement: float
    ) -> tuple[bool, str]:
        """Check if revision should stop.

        Args:
            metrics_after: Issue counts after this iteration
            iteration: Current iteration number
            max_revisions: Maximum iterations allowed
            improvement_rate: Improvement rate for this iteration
            min_improvement: Minimum improvement rate to continue

        Returns:
            Tuple of (should_stop, reason)
        """
        # All major issues resolved
        if metrics_after['major'] == 0:
            return (True, "major_issues_resolved")

        # Max iterations reached
        if iteration >= max_revisions:
            return (True, "max_iterations_reached")

        # Improvement stalled
        if improvement_rate < min_improvement:
            return (True, "stalled_no_improvement")

        # Continue
        return (False, None)

    def complete_revision(self, convergence_status: str, convergence_reason: str):
        """Mark revision as completed.

        Args:
            convergence_status: "converged" or "stalled"
            convergence_reason: Reason for stopping
        """
        self.state["workflow_status"]["revision"]["status"] = "completed"
        self.state["workflow_status"]["revision"]["convergence_status"] = convergence_status
        self.state["workflow_status"]["revision"]["convergence_reason"] = convergence_reason
        self.state["workflow_status"]["revision"]["completed_at"] = self._get_timestamp()
        self.state["workflow_status"]["revision"]["git_commit"] = self._get_git_commit()
        self._save_state()

    def get_revision_summary(self) -> Dict[str, Any]:
        """Get revision summary for reporting.

        Returns:
            Summary dict with status, iterations, and metrics
        """
        revision_state = self.state["workflow_status"]["revision"]

        if revision_state["status"] == "not_started":
            return {"status": "not_started"}

        iterations = revision_state.get("iterations", [])

        if not iterations:
            return {
                "status": revision_state["status"],
                "iterations": 0
            }

        # Get first and last metrics
        first_iteration = iterations[0]
        last_iteration = iterations[-1]

        issues_initial = first_iteration["issues_before"]
        issues_final = last_iteration["issues_after"]

        total_major_resolved = issues_initial['major'] - issues_final['major']
        total_minor_resolved = issues_initial['minor'] - issues_final['minor']

        return {
            "status": revision_state["status"],
            "iterations": len(iterations),
            "issues_initial": issues_initial,
            "issues_final": issues_final,
            "total_major_resolved": total_major_resolved,
            "total_minor_resolved": total_minor_resolved,
            "convergence_status": revision_state.get("convergence_status"),
            "convergence_reason": revision_state.get("convergence_reason")
        }

    # ===== Export Methods =====

    def export_state(self) -> Dict[str, Any]:
        """Export complete state as dictionary."""
        return self.state.copy()

    def print_summary(self):
        """Print a human-readable summary of the workflow state."""
        print("\n" + "=" * 60)
        print("RRWrite Workflow State Summary")
        print("=" * 60)

        print(f"\nManuscript Directory: {self.manuscript_dir}")
        print(f"Target Journal: {self.state.get('target_journal', 'Not set')}")
        print(f"Last Updated: {self.state['last_updated']}")

        progress = self.get_progress_summary()
        print(f"\nOverall Progress: {progress['progress_percentage']:.1f}%")
        print(f"Current Stage: {progress['current_stage']}")
        print(f"Completed Stages: {progress['completed_stages']}/{progress['total_stages']}")

        print("\nWorkflow Stages:")
        for stage, data in self.state["workflow_status"].items():
            if stage == "drafting":
                status = data["status"]
                sections_done = data["completed_sections"]
                sections_total = data["total_sections"]
                print(f"  - {stage}: {status} ({sections_done}/{sections_total} sections)")
            else:
                print(f"  - {stage}: {data['status']}")

        if self.is_stage_completed("assessment"):
            score = self.get_compatibility_score()
            if score is not None:
                print(f"\nJournal Compatibility Score: {score:.2f}")

        print("=" * 60 + "\n")


def main():
    """CLI interface for state manager."""
    import argparse

    parser = argparse.ArgumentParser(description="RRWrite State Manager")
    parser.add_argument("--output-dir", default="manuscript", help="Manuscript output directory")
    parser.add_argument("--summary", action="store_true", help="Print state summary")
    parser.add_argument("--export", action="store_true", help="Export state as JSON")
    parser.add_argument("--enable-git", action="store_true", default=True, help="Enable Git version control")
    parser.add_argument("--no-git", action="store_true", help="Disable Git version control")
    parser.add_argument("--install-tool-protection", action="store_true",
                        help="Install pre-commit hook in tool repository")

    args = parser.parse_args()

    # Install tool protection hook if requested
    if args.install_tool_protection:
        tool_repo_path = Path(__file__).parent.parent  # scripts/ -> repo root
        install_tool_repo_protection(tool_repo_path)
        print("✓ Tool repository protection installed")
        return

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s: %(message)s'
    )

    enable_git = not args.no_git if args.no_git else args.enable_git
    manager = StateManager(output_dir=args.output_dir, enable_git=enable_git)

    if args.summary:
        manager.print_summary()
    elif args.export:
        print(json.dumps(manager.export_state(), indent=2))
    else:
        # Default: print summary
        manager.print_summary()


if __name__ == "__main__":
    main()
