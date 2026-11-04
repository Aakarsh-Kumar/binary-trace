---
capability: citation-integrity
version: v1
description: Deterministic verification of reference DOIs, retractions, and duplicates.
inputs:
  - prose
  - pdf
checklist:
  - id: cite-doi-resolvable
    question: Are all cited DOIs resolvable via Crossref API?
    severity: high
    evidence_requirement: page:N
    deterministic_only: true
    advisory: false
    false_positive_guardrails:
      - Ignore non-DOI bibliographic entries
  - id: cite-not-retracted
    question: Are cited works free from known retractions in Crossref/OpenAlex?
    severity: critical
    evidence_requirement: page:N
    deterministic_only: true
    advisory: false
    false_positive_guardrails:
      - Confirm exact DOI match before raising retraction flag
  - id: cite-no-duplicates
    question: Is the bibliography free of duplicate references?
    severity: low
    evidence_requirement: section:references
    deterministic_only: true
    advisory: false
    false_positive_guardrails:
      - Compare normalized titles and DOI identifiers
deterministic_preconditions:
  - bibliography detected
false_positive_guardrails:
  - Cache Crossref queries locally
eval_status: draft
owner: author:survey
created_at: 2026-11-04
---

# Citation Integrity Skill v1

Deterministic citation integrity checks verifying DOI resolvability, retraction status, and deduplication.
