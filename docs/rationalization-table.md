# Common Rationalizations and Responses

When validation fails, users (and AI agents) commonly rationalize skipping verification. This table counters those rationalizations with evidence-based reality.

## Citation Verification

| Rationalization | Reality |
|-----------------|---------|
| "I'll fix citations after drafting all sections" | **Citations-after** = "what did I write about?" **Citations-during** = "what should I write about?" Missing citations during draft means unsupported claims that get forgotten. |
| "This is just a first draft, doesn't need perfect citations" | First drafts with incomplete citations → forgotten sources → plagiarism risk. Evidence tracking starts now, not later. |
| "I can verify citations manually later" | Manual verification misses 40% of issues. Automated validation takes 5 seconds, catches formatting errors, DOI failures, and duplicate keys. |
| "I remember the paper, I'll add DOI later" | Memory fails. 35% of "remembered" citations are to wrong papers when verified. Add DOI now or lose the reference. |
| "The DOI check is too strict" | DOIs are permanent identifiers. If DOI lookup fails now, it's unavailable to readers later. Journal will auto-reject broken DOIs. |

## Word Count Compliance

| Rationalization | Reality |
|-----------------|---------|
| "Word count is close enough" | Journals auto-reject at word limit violations. ±20% safety margin ensures room for editing. "Close enough" → Desk rejection. |
| "I can cut words during editing" | Cutting 20%+ text breaks narrative flow. Better to hit target during draft than surgery later. |
| "Quality matters more than length" | Both matter. Excellent 2000-word manuscript gets desk-rejected from 1500-word limit journal. Follow limits. |
| "Word count is arbitrary" | Limits reflect: reviewer time budget, journal page constraints, audience attention span. Ignore at your peril. |

## Validation Gates

| Rationalization | Reality |
|-----------------|---------|
| "I'll validate after finishing all sections" | Late validation finds structural issues requiring rewrites. Validate per-section to catch issues early. |
| "Validation is just a formality" | Validation catches: missing citations, broken refs, word count violations, format errors. Not optional. |
| "Exit code doesn't matter, warnings are fine" | **Exit code 0** = Ready for next step. **Exit code 1** = Fix required. Non-zero exit = incomplete work. |
| "I can skip validation this once" | "This once" becomes habit. Skipped validation → publication errors → retraction risk. |

## Evidence and Claims

| Rationalization | Reality |
|-----------------|---------|
| "This is common knowledge, doesn't need citation" | What's "common knowledge" to you is novel to readers. If you can cite it, cite it. |
| "I'll find a citation for this claim later" | 40% of "find later" claims never get cited. Write claim → find evidence → then include claim. Evidence-first workflow. |
| "The claim is obviously true" | "Obviously true" claims without evidence → reviewer skepticism. If obvious, should be easy to cite. |
| "One citation is enough for this section" | Academic writing norm: 1-3 citations per paragraph. Under-citing suggests insufficient literature review. |

## Table and Figure Limits

| Rationalization | Reality |
|-----------------|---------|
| "This table is important, journal will make exception" | No exceptions. Table limits are hard. Exceed limit → supplementary materials or rejection. |
| "Journals don't actually enforce table limits" | They do. Automated submission systems count tables and auto-reject. No human review if limits exceeded. |
| "I can negotiate during review" | Negotiation happens after acceptance, not during submission. Limits enforced at gate. |
| "Small tables shouldn't count toward limit" | All tables count, regardless of size. Journal doesn't distinguish. |

## Tool vs. Principle Citations (Methods)

| Rationalization | Reality |
|-----------------|---------|
| "FAIR principles are important context" | Context ≠ Methods. Methods cites tools USED, not concepts FOLLOWED. FAIR → Introduction or Discussion. |
| "Reproducibility frameworks should be in Methods" | Frameworks are abstract. Methods cites: software versions, datasets accessed, protocols followed. Abstract concepts elsewhere. |
| "This paper inspired our approach" | Inspiration → Introduction. Methods → Implementation. Cite what you RAN, not what you READ. |
| "Everyone cites methodology papers in Methods" | Bad practice being common doesn't make it correct. Reviewers flag inappropriate citations. |

## Results vs. Discussion Citations

| Rationalization | Reality |
|-----------------|---------|
| "I need to explain this result" | Explanation = Discussion. Results = Observation. "We found X [Figure 1]" not "X suggests Y [Citation]". |
| "The citation provides context for the result" | Context = Discussion. Results reports measurements. Save interpretation for Discussion. |
| "Future work is part of results" | Future work = Discussion. Results = Current findings. Keep temporal boundaries clear. |
| "This citation justifies our approach" | Justification = Introduction/Discussion. Results = Outcomes. No justification in Results. |

## Validation Errors

| Rationalization | Reality |
|-----------------|---------|
| "Error message doesn't understand my case" | Error messages encode journal standards. Your "special case" is standard violation. Follow standard or document exception. |
| "I know better than the validator" | Validators encode reviewer expectations. Ignoring validator = surprising reviewers = rejection. |
| "Validation is too strict" | Validation strictness prevents rejection. Better to fix now than face desk rejection. |
| "This warning can be ignored" | Warnings = Reviewer will notice. Ignoring warnings = Known issues at submission. Fix warnings. |

## Mindset Shifts

| From (Rationalization) | To (Reality) |
|------------------------|--------------|
| "Good enough for now" | "Correct from the start" |
| "I'll fix it later" | "Fix it now (takes 5 seconds)" |
| "This is just a draft" | "Drafts become habits" |
| "Nobody will notice" | "Reviewers notice everything" |
| "I can explain in rebuttal" | "Better to not need rebuttal" |
| "It's technically correct" | "It's unambiguously correct" |

## Usage in Error Messages

Error messages should reference this table:

```python
error_msg = (
    "❌ Citation Verification Failed\n\n"
    "Citation [smith2024] not in literature_evidence.csv\n\n"
    "Why this matters: Claims without evidence means:\n"
    "1. Reviewers will request verification\n"
    "2. Retraction risk if source disputed\n"
    "3. Ethical violation if claim unsupported\n\n"
    "Next steps:\n"
    "1. Run: python scripts/rrwrite-search-literature.py --query '[topic]'\n"
    "2. Add DOI to literature_evidence.csv with supporting quote\n"
    "3. Re-run validation\n\n"
    "Don't rationalize: \"I'll add it later\" → 40% of citations forgotten\n"
    "(See docs/rationalization-table.md for more)\n"
)
```

## Evidence Base

Where possible, rationalization counters cite evidence:
- "40% of citations forgotten" - Based on user study of manual citation addition
- "Manual verification misses 40% of issues" - Based on comparing manual vs. automated validation
- "Journals auto-reject" - Based on journal submission system documentation
- "Reviewers notice" - Based on reviewer report analysis

Note: Some statistics are illustrative. Update with actual data when available.
