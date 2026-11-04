---
capability: code-quality
version: v1
description: Deterministic code quality checks enforcing syntax hygiene, lint score, and file size limits.
inputs:
  - code_repo
checklist:
  - id: code-ruff-clean
    question: Is the Python codebase free from Ruff syntax and undefined name errors (E9, F)?
    severity: critical
    evidence_requirement: file:P:L
    deterministic_only: true
    advisory: false
    false_positive_guardrails:
      - Only inspect valid Python 3.10+ files
  - id: code-file-loc-limit
    question: Are all source code files within the 300 lines of code limit?
    severity: medium
    evidence_requirement: file:P:L
    deterministic_only: true
    advisory: false
    false_positive_guardrails:
      - Ignore virtualenvs, vendored files, and test fixtures
  - id: code-pylint-clean
    question: Does the code pass basic pylint syntax and import inspections?
    severity: low
    evidence_requirement: file:P:L
    deterministic_only: true
    advisory: false
    false_positive_guardrails:
      - Run with minimal ruleset on student source tree only
deterministic_preconditions:
  - python source files present
false_positive_guardrails:
  - Skip non-python files
eval_status: draft
owner: author:survey
created_at: 2026-11-04
---

# Code Quality Skill v1

Deterministic Python code quality and static analysis checks.
