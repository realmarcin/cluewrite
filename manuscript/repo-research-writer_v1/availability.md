# Availability and Requirements

## Software Availability

RRWrite is freely available as open-source software under the MIT License. The complete implementation, including all four skills, verification tools, schemas, and documentation, is hosted on GitHub at https://github.com/realmarcin/repo-research-writer. The repository includes a comprehensive example project demonstrating the complete workflow from a protein structure prediction research repository to a formatted manuscript.

## Implementation and Dependencies

The system is implemented in Python 3.7 or later and Bash, with minimal external dependencies. The core verification tools require pandas version 2.0.0 or higher and openpyxl version 3.0.0 or higher for statistical validation and Excel file support. Optional dependencies include PyYAML version 6.0.0 or higher for schema processing and LinkML version 1.7.0 or higher for advanced schema validation. The skills framework requires the Claude Code CLI for skill execution and Git for version control integration.

## Installation

RRWrite employs a global installation model using symbolic links, enabling one-time setup with automatic propagation of updates to all projects. Installation consists of two stages. First, global installation creates symbolic links in the user's home directory pointing to the skill definitions. Second, per-project setup initializes the directory structure, copies verification scripts, and creates the state tracking system. The complete installation process is automated via a single Bash script and typically completes in under one minute.

The global installation command creates symbolic links for all four skills in the `~/.claude/skills/` directory, making them available to any Claude Code session. Per-project setup is performed by running the setup script from within a research project directory, which creates the required directory structure including `manuscript/`, `scripts/`, `schemas/`, `data/`, and `figures/` directories. The setup process also copies the PROJECT.md template, all verification tools, the LinkML schema definition, and initializes the workflow state tracker.

## Documentation

Complete documentation is provided in the repository, including detailed workflow guides describing the five-stage manuscript generation process, installation instructions covering multiple deployment scenarios, a versioning guide explaining the hybrid Git plus state tracking system, and a comprehensive usage guide with examples for different project types. The example project in the `example/` directory provides a full walkthrough of generating a manuscript for a protein structure prediction study, demonstrating evidence mapping, fact verification, and journal-specific formatting.

## System Requirements

RRWrite requires a Unix-like operating system supporting Bash shell scripts and symbolic links. It has been tested on macOS and Linux distributions. Python 3.7 or later must be installed with pip for dependency management. The Claude Code CLI must be installed and configured for skill execution. Git version 2.0 or later is required for version control integration and state management. Approximately 50 MB of disk space is needed for the global installation, with an additional 10-20 MB per project for verification scripts and state tracking.
