---
capability: code-quality
version: v2
description: Hybrid code quality checks combining static analysis with model-based
  error handling and modularity analysis.
inputs:
- code_repo
checklist:
- id: code-ruff-clean
  question: Is the Python codebase free from Ruff syntax and undefined name errors
    (E9, F)?
  severity: critical
  evidence_requirement: file:PATH:LINE (verbatim syntax error line)
  deterministic_only: true
  advisory: false
  false_positive_guardrails:
  - Only inspect valid Python 3.10+ files
- id: code-file-loc-limit
  question: Are all source code files within the 300 lines of code limit?
  severity: medium
  evidence_requirement: file:PATH:1 (first line of module)
  deterministic_only: true
  advisory: false
  false_positive_guardrails:
  - Ignore virtualenvs, vendored files, and test fixtures
- id: code-pylint-clean
  question: Does the code pass basic pylint syntax and import inspections?
  severity: low
  evidence_requirement: file:PATH:1 (first line of module)
  deterministic_only: true
  advisory: false
  false_positive_guardrails:
  - Run with minimal ruleset on student source tree only
- id: code-error-handling
  question: Are error conditions and edge cases safely handled rather than silently
    swallowed?
  severity: medium
  evidence_requirement: file:PATH:LINE (verbatim code line, e.g. function call or
    handler)
  deterministic_only: false
  advisory: false
  false_positive_guardrails:
  - Do not flag bare except when followed by immediate logging and re-raise
  - Allow intentional pass in cleanup blocks
- id: code-modularity
  question: Are core responsibilities separated into testable functions with low coupling?
  severity: medium
  evidence_requirement: file:PATH:LINE (verbatim code line, e.g. function call or
    handler)
  deterministic_only: false
  advisory: false
  false_positive_guardrails:
  - Permit procedural scripts under 50 lines without separate modules
  - Do not require object-oriented structures when functions suffice
deterministic_preconditions:
- python source files present
false_positive_guardrails:
- Skip non-python files and build artifacts
eval_status: evaluating
owner: author:survey
created_at: 2026-11-05
---
# Code Quality Skill v2

Hybrid code quality verification evaluating static lint errors, file length, error handling robustness, and code modularity.
