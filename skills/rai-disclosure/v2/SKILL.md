---
capability: rai-disclosure
version: v2
description: Hybrid Responsible-AI disclosure checks combining deterministic presence
  checks with model-based sufficiency judgment.
inputs:
- prose
- pdf
- disclosure_section
checklist:
- id: rai-section-present
  question: Is an AI or Responsible-AI disclosure section present in the submission?
  severity: high
  evidence_requirement: section:disclosure (verbatim sentence from disclosure)
  deterministic_only: true
  advisory: false
  false_positive_guardrails:
  - Match known section titles (AI Use, Disclosure, Responsible AI)
- id: rai-tool-named
  question: Does the disclosure explicitly name the AI assistance tools utilized?
  severity: medium
  evidence_requirement: section:disclosure (verbatim sentence from disclosure)
  deterministic_only: true
  advisory: false
  false_positive_guardrails:
  - Recognize common model and tool names
- id: rai-task-named
  question: Does the disclosure specify the exact tasks AI was employed to assist
    with?
  severity: medium
  evidence_requirement: section:disclosure (verbatim sentence from disclosure)
  deterministic_only: true
  advisory: false
  false_positive_guardrails:
  - Verify affirmative statement of assisted activities
- id: rai-sufficiency-judgment
  question: Is the disclosure sufficiently detailed to assess whether academic integrity
    policies were respected?
  severity: high
  evidence_requirement: section:disclosure (verbatim sentence from disclosure)
  deterministic_only: false
  advisory: false
  false_positive_guardrails:
  - Accept brief disclosures if student confirms zero AI tools used
  - Do not demand proprietary prompts or full conversation transcripts
- id: rai-human-oversight-described
  question: Does the disclosure explain how generated outputs were reviewed, verified,
    or corrected by the author?
  severity: medium
  evidence_requirement: section:disclosure (verbatim sentence from disclosure)
  deterministic_only: false
  advisory: false
  false_positive_guardrails:
  - Allow concise descriptions of verification such as manual proofreading or unit
    testing
  - Do not flag if AI was only used for minor spelling and grammar correction
deterministic_preconditions:
- disclosure section detected or DISCLOSURE.md present
false_positive_guardrails:
- Accept negative declaration of no AI usage
eval_status: evaluating
owner: author:survey
created_at: 2026-11-05
---
# Responsible-AI Disclosure Skill v2

Hybrid verification evaluating presence of disclosure, named tools, assisted tasks, sufficiency of description, and human verification oversight.
