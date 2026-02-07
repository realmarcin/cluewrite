# Abstract

**Motivation:** Computational researchers invest substantial effort manually translating code and data into manuscript text, introducing transcription errors and breaking provenance chains between published claims and source files. Existing tools address isolated aspects of scientific writing but lack end-to-end automation with rigorous fact verification.

**Results:** We present Repo Research Writer (RRWrite), an AI-powered system that automatically generates scientifically accurate, journal-compliant manuscripts directly from research code repositories. RRWrite implements a five-stage workflow—plan, research, draft, critique, and assemble—orchestrated through four Claude Code skills. The system enforces mandatory fact-checking via Python verification tools that validate all numerical claims against source CSV/Excel files, maintaining complete provenance from data to publication. RRWrite supports multiple journal formats (Nature Methods, PLOS Computational Biology, Bioinformatics) and integrates Git-based version control with workflow state tracking. The architecture combines LinkML schema validation [matentzoglu2025linkml], automated citation management, and adversarial critique iterations to ensure scientific rigor. Implementation includes 10 Python tools, 4 AI skills (400+ lines each), and comprehensive schema definitions.

**Availability and Implementation:** RRWrite is open source (MIT license) at https://github.com/realmarcin/repo-research-writer. The system requires Python 3.7+, Git, and Claude Code CLI with optional dependencies for Excel support.

**Contact:** marcin@lbl.gov

**Supplementary information:** Complete documentation, workflow guides, and example projects available at the GitHub repository.
