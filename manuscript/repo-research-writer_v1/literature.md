# Literature Review: Automated Manuscript Generation from Research Code Repositories Using Large Language Models

**Generated:** 2026-02-05
**Based on:** RR-WRITE-PROJECT.md

## Background

### AI-Powered Scientific Writing

Large language models have fundamentally transformed scientific writing workflows over the past three years. GPT-4, introduced in March 2023 [achiam2023, DOI:arXiv:2303.08774], demonstrated unprecedented capabilities in understanding and generating scientific text across diverse domains. A comprehensive pilot study by Wang et al. (2024) [wang2024gpt4, DOI:10.1186/s13040-024-00371-3] evaluated GPT-4's ability to write biomedical review articles, finding that while the model could generate coherent scientific text and maintain consistency across regenerations, it struggled with extracting precise information for tables and required additional training for specialized biomedical terminology.

The adoption of LLMs in scientific writing has been rapid and measurable. Kobak et al. (2025) [kobak2025excess, DOI:10.1126/sciadv.adt3813] analyzed over 15 million biomedical abstracts from PubMed (2010-2024) and identified a dramatic vocabulary shift following LLM introduction, estimating that at least 13.5% of 2024 abstracts were processed with LLMs, with some subcorpora reaching 40% usage.

### Computational Research Workflows

Scientific workflow systems provide the foundation for automating complex computational pipelines. These systems have evolved from simple script-based approaches to sophisticated platforms that manage multi-step data processing, ensure reproducibility, and track provenance [scientific_workflows]. Key platforms include Galaxy (web-based, community-driven analysis platform), Kepler (visual workflow builder with drag-and-drop interface), and AiiDA (automated infrastructure with strong provenance tracking for materials science) [dip_ai_workflows].

The W3C PROV family of standards [w3c_prov] defines a data model for representing provenance information, establishing "entity," "activity," and "agent" as core concepts. ProvONE extends W3C PROV specifically for scientific workflows [provone], enabling capture of computational processes with sufficient detail for reproducibility.

### Reproducibility and Jupyter Notebooks

Jupyter notebooks have become the de facto standard for documenting computational research, combining executable code with narrative text and visualizations [rule2018jupyter, arXiv:1810.08055]. Rule et al. (2018) established ten simple rules for reproducible research in Jupyter notebooks, emphasizing version control, documentation, and environment specification. However, Kanwal et al. (2017) [kanwal2017provenance, DOI:10.1186/s12859-017-1747-0] demonstrated through a genomic workflow case study that reproducibility remains challenging due to incomplete understanding of requirements and insufficient provenance tracking across workflow definition approaches.

### Schema Validation and Data Modeling

LinkML (Linked Data Modeling Language) [matentzoglu2025linkml, DOI:10.1093/gigascience/giaf152] provides an open framework for authoring, validating, and sharing structured scientific data. Published in GigaScience (2025), LinkML supports data structures ranging from flat lists to complex normalized models with polymorphism and inheritance, facilitating FAIR (Findable, Accessible, Interoperable, Reusable) data practices across biology, chemistry, biomedicine, and other fields.

## Related Work

### Automated Literature Review and Citation Management

Several AI-powered platforms have emerged to automate literature review processes. Rayyan [rayyan] provides AI-driven systematic review management, reducing screening time by up to 90% through automated duplicate detection and relevance filtering. Elicit [elicit] pulls structured data from over 125 million papers, generating editable research reports and achieving up to 80% time savings for systematic reviews. ResearchRabbit [researchrabbit] maps citation relationships between studies, authors, and topics, enabling discovery of related papers and research trend tracking.

Semantic Scholar [semanticscholar], developed by the Allen Institute for AI, indexes 225M+ papers with 2.8B citation edges, providing AI-generated TLDR summaries, semantic analysis, citation context, and influence metrics. These platforms demonstrate automated citation management capabilities but focus on discovery and synthesis rather than full manuscript generation from computational artifacts.

### End-to-End Automated Scientific Discovery

The AI Scientist [lu2024scientist, arXiv:2408.06292], released by Sakana AI in August 2024, represents the first comprehensive framework for fully automatic scientific discovery. The system generates novel research ideas, writes code, executes experiments, visualizes results, writes full scientific papers, and runs simulated peer review—all for less than $15 per paper. An automated reviewer achieves near-human performance in evaluating paper quality, with some generated papers exceeding acceptance thresholds for top machine learning conferences.

The AI Scientist-v2 [lu2025scientist_v2, arXiv:2504.08066], released in April 2025, eliminated reliance on human-authored code templates and produced the first entirely AI-generated peer-review-accepted workshop paper. While groundbreaking, these systems focus on generating new research within machine learning domains rather than documenting existing computational research projects.

### Fact-Checking and Verification

Automated fact-checking has become critical for validating AI-generated content. Guo et al. (2022) [guo2022survey, DOI:10.1162/tacl_a_00454] surveyed automated fact-checking approaches, identifying three key stages: claim detection, evidence retrieval, and claim verification. NLP-based fact-checkers can validate claims against trustworthy sources, though they struggle with complex scientific claims requiring detailed reasoning.

A major challenge in LLM-generated scientific writing is hallucinated references and fabricated data. Studies testing different ChatGPT versions found tendencies to generate incomplete, erroneous, or nonexistent citations [wang2024gpt4]. While automated fact-checkers achieve accuracy rates around 86.69%, they should be used as aids rather than final arbiters of truth [originality_ai_factcheck].

### Agent Skills and Workflow Frameworks

Anthropic's Agent Skills [anthropic_skills] provide a framework for packaging expertise into reusable, composable resources that transform general-purpose AI agents into domain specialists. Skills follow an open standard that works across multiple AI tools, with Claude Code extending the standard with invocation control, subagent execution, and dynamic context injection. Skills are token-efficient (occupying only dozens of tokens until loaded) and have demonstrated 90% workflow execution time reductions across multiple industries [accio_claude_skills].

## Recent Advances

### AI-Assisted Manuscript Writing (2024-2025)

A blinded randomized controlled study compared GPT-4 and human researchers in writing scientific introduction sections, finding them equal in quality when GPT-4 was provided with study aims from previously published works [chatgpt4_intros]. However, hallucinations remain problematic—particularly fabricated references that include real researcher names studying related topics.

The advent of specialized AI writing tools like Paperpal [paperpal], SciSpace [scispace], and Paperguide [paperguide] demonstrates commercialization of AI-assisted scientific writing. These tools focus on literature analysis, text clarity enhancement, and formatting adherence rather than full manuscript generation from computational artifacts.

### Adversarial Attacks on AI Review Systems

Recent research has identified vulnerabilities in AI-assisted peer review. Authors can manipulate AI review systems through structure spoofing (mimicking high-impact paper architecture), prompt injection (hidden directives steering reviews toward positive judgments), and data poisoning (injecting crafted content into arXiv and other repositories) [adversarial_ml_review]. Publishers are deploying counter-AI verification systems using semantic fingerprinting, citation network analysis, and adversarial prompting to detect synthetic content.

### Provenance Tracking in Modern Systems

Recent provenance tracking systems address reproducibility challenges in complex computational environments. ReproZip [chirigati2013reprozip] captures detailed provenance by tracking operating system calls, packaging data dependencies, libraries, and configuration parameters into portable bundles. The yProv4ML library [provml] collects provenance data in JSON format compliant with W3C PROV and ProvML standards specifically for machine learning pipelines.

WorkflowHub [workflowhub, DOI:10.1038/s41597-025-04786-3], published in Scientific Data (2025), provides a unified registry for computational workflows that links to community repositories and supports FAIR workflow sharing. Galaxy demonstrated degrees of workflow provenance focused on capturing computational methods in genomics research [kanwal2017provenance].

### LinkML Reference Validation

LinkML has extended beyond schema definition to include specialized validation tools. The linkml-reference-validator [linkml_refval] fetches scientific publications from PubMed/PMC and verifies that quoted text (supporting_text) appears in referenced documents using deterministic substring matching—directly addressing the evidence verification gap in scientific data systems.

## Research Gaps

**Identified Gaps:**

1. **No integration of verification with generation**: Existing AI writing tools (The AI Scientist, GPT-4 assistants) generate content but do not systematically verify numerical claims against source data files. Fact-checking tools operate separately from generation workflows.

2. **Lack of repository-to-manuscript automation**: While scientific workflow systems automate computational pipelines and AI tools assist with writing, no system automatically generates publication-ready manuscripts from existing research code repositories with complete provenance from data to claims.

3. **Insufficient multi-journal formatting**: Current tools require manual reformatting for different journal requirements. Automated format adaptation to Nature, PLOS, Bioinformatics, and other guidelines remains largely manual.

4. **Missing adversarial critique integration**: While AI review systems exist (e.g., The AI Scientist's automated reviewer), they are not integrated into iterative manuscript improvement workflows that enforce journal-specific quality standards before human review.

5. **Incomplete schema-based validation**: LinkML provides schema definition and basic validation, but no framework combines LinkML schemas with fact-checking, citation verification, and multi-journal formatting in a single manuscript generation pipeline.

**How Our Work Fits:**

RRWrite addresses these gaps by integrating (1) automatic fact verification against source data files, (2) complete provenance tracking from repository artifacts to manuscript claims, (3) multi-journal formatting automation, (4) adversarial critique cycles against journal standards, and (5) schema-based validation using LinkML for structured manuscript components. This creates the first end-to-end system for generating scientifically accurate, journal-compliant manuscripts directly from computational research repositories.

## 5. Key Citations to Add

### Background (Introduction)

- [achiam2023]: Foundational LLM capabilities (GPT-4)
- [kobak2025excess]: Quantified LLM adoption in scientific writing
- [rule2018jupyter]: Reproducible research in computational notebooks
- [matentzoglu2025linkml]: Schema-based data modeling framework
- [w3c_prov]: Provenance standards for scientific workflows

### Related Work (Methods/Discussion)

- [wang2024gpt4]: GPT-4 evaluation for scientific review writing
- [lu2024scientist]: End-to-end automated scientific discovery (AI Scientist)
- [lu2025scientist_v2]: Recent advances in autonomous research (AI Scientist-v2)
- [guo2022survey]: Automated fact-checking survey
- [kanwal2017provenance]: Provenance tracking and reproducibility challenges

### Tools and Platforms (Methods)

- [anthropic_skills]: Agent Skills framework for task automation
- [rayyan]: AI-powered systematic review platform
- [elicit]: AI research assistant for literature synthesis
- [semanticscholar]: Semantic Scholar AI-powered research tool
- [chirigati2013reprozip]: ReproZip for computational reproducibility

### Recent Comparisons (Results/Discussion)

- [workflowhub]: Unified workflow registry (2025)
- [linkml_refval]: Reference validation for scientific data
- [adversarial_ml_review]: Vulnerabilities in AI review systems

## 6. Citation Integration Guide

**Introduction:**

- Cite [achiam2023, wang2024gpt4, kobak2025excess] when introducing AI's impact on scientific writing
- Cite [rule2018jupyter, kanwal2017provenance] when discussing reproducibility challenges in computational research
- Cite [matentzoglu2025linkml, w3c_prov] when explaining the need for structured data validation and provenance

**Methods:**

- Cite [anthropic_skills] when describing the Agent Skills framework architecture
- Cite [matentzoglu2025linkml] when explaining schema-based validation
- Cite [chirigati2013reprozip, workflowhub] when positioning RRWrite among workflow systems

**Results:**

- Cite [rayyan, elicit, semanticscholar] when comparing literature research automation
- Cite [lu2024scientist, lu2025scientist_v2] when contrasting with end-to-end discovery systems
- Cite [guo2022survey] when discussing fact verification capabilities

**Discussion:**

- Cite [adversarial_ml_review] when discussing quality assurance and verification
- Cite [linkml_refval] when highlighting evidence validation approaches
- Cite [kanwal2017provenance] when positioning provenance tracking innovations

---

## References

Full BibTeX entries available in `literature_citations.bib`
Evidence quotes available in `literature_evidence.csv`
