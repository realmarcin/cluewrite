# Citation Rules by Section

Quick reference for appropriate citation types in each manuscript section.

## Abstract
- **Max Citations:** 0-2
- **Allowed:** Seminal papers only (rare)
- **Forbidden:** All others
- **Rationale:** Self-contained, citations break flow

## Introduction
- **Max Citations:** Unlimited
- **Allowed:** Seminal, review, recent, tool
- **Forbidden:** None
- **Rationale:** Broad background, all relevant citations appropriate

## Methods
- **Max Citations:** Unlimited
- **Allowed:** Tool, protocol, dataset citations ONLY
- **Forbidden:** Abstract principles, reviews, unused tools
- **Rationale:** Cite what YOU used, not general concepts

### Examples (Methods)
✅ **Correct:**
- `Schema validation used LinkML [LinkML2024]`
- `Analyzed sequences from GTDB [GTDB2024]`
- `Implemented MaxPro design [Smith2020]`

❌ **Incorrect:**
- `Data follow FAIR principles [Wilkinson2016]` → Abstract concept
- `Used best practices [Review2023]` → General review
- `Could have used Manubot [Manubot2019]` → Not actually used

## Results
- **Max Citations:** Unlimited
- **Allowed:** Papers/datasets analyzed, benchmarks compared, tools measured
- **Forbidden:** Explanations, justifications, future work
- **Rationale:** Report observations, not interpretations

### Examples (Results)
✅ **Correct:**
- `Identified 29 papers including [Example2024, Example2025]` → Found in analysis
- `Compared against [Smith2020] benchmark` → Measurement comparison
- `Sequences from [GTDB2024] showed...` → Data source result

❌ **Incorrect:**
- `Provenance chains established [Himmelstein2019]` → Explaining what provenance is
- `Addresses hallucination concerns [CliVER2024]` → Justifying why
- `Future integration with [Standard2024]` → Future work (→ Discussion)

## Discussion
- **Max Citations:** Unlimited
- **Allowed:** Seminal, review, recent, tool
- **Forbidden:** None
- **Rationale:** Broad interpretation, all types appropriate

## Data Availability
- **Max Citations:** 0-3
- **Allowed:** Platform-specific (Zenodo DOI, Docker, GitHub)
- **Forbidden:** General methodology (FAIR, reproducibility)
- **Rationale:** Factual access info, not methodology justifications

### Examples (Availability)
✅ **Correct:**
- `Code at https://github.com/user/repo under MIT license`
- `Data in Zenodo [zenodo2023] (DOI: 10.5281/zenodo.123)`
- `Docker images available [docker2024]`

❌ **Incorrect:**
- `Documentation follows FAIR principles [Wilkinson2016]` → Abstract methodology
- `Reproducible using best practices [Review2023]` → General concept

## Quick Decision Tree

```
Is this a tool/dataset/protocol I ACTUALLY USED?
├─ YES → Cite in Methods
└─ NO
   ├─ Is it a paper I ANALYZED/BENCHMARKED AGAINST?
   │  └─ YES → Cite in Results (as data point)
   └─ NO
      ├─ Is it background/motivation?
      │  └─ YES → Cite in Introduction
      └─ Is it interpretation/future work?
         └─ YES → Cite in Discussion
```

## Common Mistakes

| Citation Type | Wrong Section | Right Section | Reason |
|---------------|---------------|---------------|---------|
| FAIR principles [Wilkinson2016] | Methods, Availability | Introduction | Abstract concept, not tool |
| Reproducibility framework [Peng2011] | Methods | Introduction/Discussion | Methodology review, not used tool |
| Unused tool [Manubot2019] | Methods | None (or Introduction if comparing approaches) | Not actually used |
| Explaining concepts [Paper2024] | Results | Introduction/Discussion | Results report, not explain |
| Future standards [Standard2024] | Results | Discussion | Future work, not current results |

## Validation Commands

Check citations in section:
```bash
python scripts/rrwrite_citation_validator.py {section} manuscript/literature_evidence.csv [citation_keys...]
```

Check appropriateness:
```python
from rrwrite_citation_validator import CitationBusinessValidator
validator = CitationBusinessValidator(evidence_csv)
warnings = validator.validate_section_appropriateness(section, citations)
```
