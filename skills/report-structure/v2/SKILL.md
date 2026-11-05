---
capability: report-structure
version: v2
description: Hybrid report structure checks verifying deterministic sections and hierarchy
  alongside model-based coherence analysis.
inputs:
- prose
- pdf
checklist:
- id: struct-required-sections
  question: Are required sections (Introduction, Methods, Results, Discussion) present?
  severity: high
  evidence_requirement: section:headings
  deterministic_only: true
  advisory: false
  false_positive_guardrails:
  - Match standard heading synonyms
- id: struct-heading-order
  question: Are headings placed in an admissible logical progression?
  severity: medium
  evidence_requirement: section:headings
  deterministic_only: true
  advisory: false
  false_positive_guardrails:
  - Allow Appendix sections after References
- id: struct-minimum-length
  question: Does the report satisfy the minimum 500 words requirement?
  severity: medium
  evidence_requirement: page:1
  deterministic_only: true
  advisory: false
  false_positive_guardrails:
  - Exclude bibliography and title metadata from word count
- id: struct-semantic-coherence
  question: Does each section transition logically into the subsequent section without
    abrupt topical disconnects?
  severity: medium
  evidence_requirement: section:methods
  deterministic_only: false
  advisory: false
  false_positive_guardrails:
  - Account for concise technical reporting styles in quantitative methods
  - Allow subheadings to introduce specialized sub-topics
- id: struct-claim-evidence-alignment
  question: Are quantitative claims in the discussion substantiated by reported results
    or data tables?
  severity: high
  evidence_requirement: section:discussion
  deterministic_only: false
  advisory: false
  false_positive_guardrails:
  - Allow qualitative inferences that refer back to general findings
  - Do not flag speculative statements explicitly qualified as future work
deterministic_preconditions:
- prose length >= 500 words
false_positive_guardrails:
- Normalize unicode heading punctuation
eval_status: evaluating
owner: author:survey
created_at: 2026-11-05
---
# Report Structure Skill v2

Hybrid structural compliance skill verifying standard section headings, document length, logical section flow, and claim-evidence alignment.
