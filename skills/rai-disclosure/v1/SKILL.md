---
capability: rai-disclosure
version: v1
description: Deterministic checks for Responsible-AI disclosure section, tool naming, and task specification.
inputs:
  - prose
  - pdf
  - disclosure_section
checklist:
  - id: rai-section-present
    question: Is an AI or Responsible-AI disclosure section present in the submission?
    severity: high
    evidence_requirement: section:disclosure
    deterministic_only: true
    advisory: false
    false_positive_guardrails:
      - Match known section titles (AI Use, Disclosure, Responsible AI)
  - id: rai-tool-named
    question: Does the disclosure explicitly name the AI assistance tools utilized?
    severity: medium
    evidence_requirement: section:disclosure
    deterministic_only: true
    advisory: false
    false_positive_guardrails:
      - Recognize common model and tool names
  - id: rai-task-named
    question: Does the disclosure specify the exact tasks AI was employed to assist with?
    severity: medium
    evidence_requirement: section:disclosure
    deterministic_only: true
    advisory: false
    false_positive_guardrails:
      - Verify affirmative statement of assisted activities
deterministic_preconditions:
  - disclosure section detected or DISCLOSURE.md present
false_positive_guardrails:
  - Accept negative declaration of no AI usage
eval_status: draft
owner: author:survey
created_at: 2026-11-04
---

# Responsible-AI Disclosure Skill v1

Deterministic verification of required AI usage disclosures.
