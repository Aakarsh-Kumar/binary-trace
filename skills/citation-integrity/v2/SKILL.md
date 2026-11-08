---
capability: citation-integrity
version: v2
description: Hybrid citation integrity verification combining deterministic checks
  with model-based claim support analysis.
inputs:
- prose
- pdf
checklist:
- id: cite-doi-resolvable
  question: Are all cited DOIs resolvable via Crossref API?
  severity: high
  evidence_requirement: section:references (verbatim DOI string)
  deterministic_only: true
  advisory: false
  false_positive_guardrails:
  - Ignore non-DOI bibliographic entries
- id: cite-not-retracted
  question: Are cited works free from known retractions in Crossref/OpenAlex?
  severity: critical
  evidence_requirement: section:references (verbatim reference entry)
  deterministic_only: true
  advisory: false
  false_positive_guardrails:
  - Confirm exact DOI match before raising retraction flag
- id: cite-no-duplicates
  question: Is the bibliography free of duplicate references?
  severity: low
  evidence_requirement: "A complete bibliography entry copied verbatim, beginning with its reference marker ([N] or N.). Both copies of the duplicated entry must appear in the submission. Page headers, footers, and page numbers are not valid evidence."
  deterministic_only: true
  advisory: false
  false_positive_guardrails:
  - Compare normalized titles and DOI identifiers
- id: cite-claim-supported
  question: Does the cited source actually support the empirical claim made in the
    text?
  severity: high
  evidence_requirement: page:1 (verbatim sentence of claim or citation)
  deterministic_only: false
  advisory: false
  false_positive_guardrails:
  - Allow conceptual citations and background literature references
  - Do not flag if the claim is standard domain knowledge
- id: cite-context-accurate
  question: Is the source summarized or quoted without distorting its primary conclusion?
  severity: medium
  evidence_requirement: page:1 (verbatim sentence of claim or citation)
  deterministic_only: false
  advisory: false
  false_positive_guardrails:
  - Disregard minor stylistic variations in summarization
  - Verify original abstract before concluding distortion
deterministic_preconditions:
- bibliography detected
false_positive_guardrails:
- Verify exact quotation or cited span in submission text
eval_status: evaluating
owner: author:survey
created_at: 2026-11-05
---
# Citation Integrity Skill v2

Hybrid citation verification evaluating DOI validity, retractions, duplicate references, and model-based citation claim support.
