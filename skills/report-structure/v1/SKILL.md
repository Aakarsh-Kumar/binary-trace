---
capability: report-structure
version: v1
description: Deterministic verification of report sections, heading sequence, and formatting.
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
deterministic_preconditions:
  - prose length >= 500 words
false_positive_guardrails:
  - Normalize unicode heading punctuation
eval_status: draft
owner: author:survey
created_at: 2026-11-04
---

# Report Structure Skill v1

Deterministic report structure checks ensuring required sections, heading hierarchy, and length constraints.
