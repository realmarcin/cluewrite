# New Literature Additions - March 2026

**Update Date:** 2026-03-05
**Purpose:** Extend existing literature with recent 2024-2026 papers

## New Papers to Add

### 1. Manubot AI Editor (2024)

**Citation Key:** Pividori2024

**Full Citation:**
Pividori, M., & Greene, C. S. (2024). A publishing infrastructure for Artificial Intelligence (AI)-assisted academic authoring. Journal of the American Medical Informatics Association, 31(9), 2103-2113. DOI: 10.1093/jamia/ocae139

**Evidence Quote:**
"The prompt generator integrates metadata using prompt templates to generate section-specific prompts for each paragraph."

**Relevance:** Direct competitor/related work - AI-assisted manuscript revision system integrated into Manubot. Demonstrates LLM integration for scholarly writing within collaborative platforms.

**Integration Point:** Add to "Recent Advances" → "AI-Powered Academic Writing Assistants" subsection

---

### 2. ML Reproducibility Barriers (2024-2025)

**Citation Key:** Semmelrock2025

**Full Citation:**
Semmelrock, H., Ross-Hellauer, T., Kopeinik, S., Theiler, D., Haberl, A., Thalmann, S., & Kowald, D. (2025). Reproducibility in machine-learning-based research: Overview, barriers, and drivers. AI Magazine, 46(1). DOI: 10.1002/aaai.70002 (also available as arXiv:2406.14325)

**Evidence Quote:**
"Issues including lack of transparency, data or code, poor adherence to standards, and the sensitivity of ML training conditions mean that many papers are not even reproducible in principle."

**Relevance:** Establishes context for why automated documentation and fact-checking are critical. Identifies barriers that RRWrite addresses.

**Integration Point:** Add to "Background & Foundations" → "Reproducible Research and Computational Workflows" OR "Recent Advances"

---

### 3. Jupyter Notebook Reproducibility Assessment (2025)

**Citation Key:** Hossain2025

**Full Citation:**
Hossain, A. S. M. S., Brown, C., Koop, D., & Malik, T. (2025). Similarity-Based Assessment of Computational Reproducibility in Jupyter Notebooks. In Proceedings of the 3rd ACM Conference on Reproducibility and Replicability. DOI: 10.1145/3736731.3746159 (also arXiv:2509.23645)

**Evidence Quote:**
"SRI employs novel methods developed based on similarity metrics specific to different types of Python objects to compare rerun outputs against original outputs."

**Relevance:** Advances in computational reproducibility assessment - complements RRWrite's fact-checking approach. Shows state-of-the-art in notebook verification.

**Integration Point:** Add to "Recent Advances" → Create new subsection "Computational Reproducibility Assessment" OR add to Jupyter notebooks subsection

---

## Integration Strategy

### Update "Recent Advances" Section

Add new subsection after "Literature Review Automation":

```markdown
### AI-Assisted Manuscript Revision

The Manubot AI Editor extends the Manubot collaborative writing platform with LLM-based revision capabilities [Pividori2024, DOI:10.1093/jamia/ocae139]. The system generates section-specific prompts using metadata and manuscript structure, producing suggested paragraph revisions for human authors to review. Evaluation through 5 case studies demonstrates that language models can grasp complex academic concepts and enhance text quality, while version control ensures transparency in distinguishing human- and machine-generated text. This approach complements RRWrite's generative workflow by focusing on iterative refinement of existing manuscripts rather than initial draft generation.
```

### Update "Background & Foundations" Section

Add to "Jupyter Notebooks as Publication Format" subsection:

```markdown
Recent advances in notebook reproducibility assessment introduce similarity-based metrics as an alternative to deterministic matching [Hossain2025, DOI:10.1145/3736731.3746159]. The Similarity-based Reproducibility Index (SRI) employs type-specific similarity metrics for Python objects to quantitatively assess reproducibility even when outputs are not identical, addressing the challenge that strict equality checks fail for floating-point computations and stochastic algorithms. These advances in reproducibility verification parallel RRWrite's evidence-based validation approach, both recognizing that computational reproducibility requires nuanced comparison strategies rather than binary pass/fail checks.
```

Add to "Reproducible Research and Computational Workflows":

```markdown
Machine learning research faces particular reproducibility challenges, with issues including lack of transparency, missing data or code, poor adherence to standards, and sensitivity of ML training conditions rendering many papers not reproducible even in principle [Semmelrock2025, DOI:10.1002/aaai.70002]. These systemic barriers underscore the need for automated documentation systems that integrate provenance tracking and fact verification from the outset of research workflows.
```

### Update Citation Integration Guide

Add to Results section:
- Cite [Pividori2024] when comparing RRWrite's generative approach to revision-focused AI tools
- Cite [Hossain2025] when discussing reproducibility verification methods

Add to Discussion section:
- Cite [Semmelrock2025] when discussing motivation for automated documentation
- Cite [Pividori2024] when positioning RRWrite in the landscape of AI writing tools

---

## Updated Statistics

After integration:

- **Papers reviewed:** 25 (was 22)
- **Foundational papers (pre-2020):** 2 (unchanged)
- **Related work papers (2020-2023):** 5 (unchanged)
- **Recent advances (2024-2026):** 18 (was 15)
- **Papers with DOIs:** 23 (was 20, 92%)
- **ArXiv preprints:** 2 (was 1)
- **Conference papers:** 4 (was 3)
- **Journal articles:** 19 (was 18)
