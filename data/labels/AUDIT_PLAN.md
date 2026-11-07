# Mode B Audit Plan (15 Submissions)

This plan specifies the 25% stratified audit sample (15 out of 60 submissions) for Mode B evaluation per PRD.md §4.7 and Decision D-010.

> [!NOTE]
> **Inter-rater Agreement Disclosure**: In accordance with the Mode B protocol (agent-first-pass with human audit), dual independent annotation is not performed. A single human auditor audits and adjudicates this 25% stratified sample. Therefore, inter-annotator agreement (Cohen's κ) is not computed for this audit pass, and the evaluation report will state this transparently.

## Audit Sample Composition (15 Submissions)

| # | External ID | Submission ID | Type | Category | Flagged Checks (Provisional) | Downgraded Checks (Unsupported) | Selection Rationale / Focus |
|---|---|---|---|---|---|---|---|
| 1 | `eval_code_01` | 131 | `code` | `clean` | None | None | Clean control (code): pure numerical routines (mean, variance), zero defects injected. |
| 2 | `eval_code_02` | 132 | `code` | `clean` | None | None | Clean control (code): clean PyMETA Python module, passes all 5 code quality checks. |
| 3 | `eval_code_08` | 138 | `code` | `clean` | None | None | Clean control (code): clean mathematical library functions, no flags or downgrades. |
| 4 | `eval_mixed_02` | 152 | `mixed` | `clean` | None | None | Clean control (mixed): complete paper + clean code + valid RAI disclosure, 0 flags across all 15 checks. |
| 5 | `eval_mixed_04` | 154 | `mixed` | `clean` | None | None | Clean control (mixed): complete empirical paper with valid citations, code, and disclosure. |
| 6 | `eval_mixed_12` | 162 | `mixed` | `single_issue` | `cite-doi-resolvable` | None | Single-issue (citation): injected corrupted CiteMe DOI (10.0000/corrupt.citeme.05). |
| 7 | `eval_prose_07` | 117 | `prose` | `single_issue` | `cite-doi-resolvable`, `struct-minimum-length` | None | Single-issue focus on cite-no-duplicates: reference list contains distinct items; auditor verifies absence of duplicates. |
| 8 | `eval_code_18` | 148 | `code` | `single_issue` | `code-ruff-clean` | None | Single-issue (code): syntax defect / comment trigger; flagged code-ruff-clean. |
| 9 | `eval_code_16` | 146 | `code` | `single_issue` | None | `code-file-loc-limit`, `code-modularity` | Single-issue focus on code-modularity: 550 helper functions; model flagged modularity, verifier downgraded. |
| 10 | `eval_prose_04` | 114 | `prose` | `single_issue` | `rai-sufficiency-judgment`, `struct-minimum-length`, `struct-required-sections`, `struct-semantic-coherence` | `rai-section-present` | Single-issue focus on rai-sufficiency: note omits empirical sections and lacks complete AI disclosure. |
| 11 | `eval_code_04` | 134 | `code` | `adversarial_downgrade` | None | `code-file-loc-limit`, `code-modularity` | Adversarial downgrade: 1650 LOC file with 550 functions; model cited file:__init__.py:1, correctly downgraded by verifier. |
| 12 | `eval_mixed_19` | 169 | `mixed` | `adversarial_downgrade` | `rai-sufficiency-judgment`, `rai-task-named` | `code-file-loc-limit`, `code-modularity` | Adversarial downgrade: 2 code check downgrades due to truncated location span, plus RAI flags in mixed submission. |
| 13 | `eval_prose_06` | 116 | `prose` | `adversarial_downgrade` | `cite-doi-resolvable`, `struct-claim-evidence-alignment`, `struct-minimum-length` | `rai-section-present` | Adversarial downgrade: HALLMARK prompt override injection; model explanation for rai-section-present correctly downgraded. |
| 14 | `eval_prose_10` | 120 | `prose` | `adversarial_downgrade` | `cite-doi-resolvable`, `struct-claim-evidence-alignment`, `struct-minimum-length` | `rai-section-present` | Adversarial downgrade: HALLMARK JSON bypass injection; model explanation for rai-section-present correctly downgraded. |
| 15 | `eval_prose_12` | 122 | `prose` | `adversarial_downgrade` | `cite-doi-resolvable`, `struct-claim-evidence-alignment`, `struct-minimum-length` | `rai-human-oversight-described` | Adversarial downgrade: model cited invalid file location grammar on prose submission, correctly rejected by location verifier. |

## Detailed Submission Manifest & Expected Ground Truth

### 1. `eval_code_01` (ID 131) — `clean`
- **Type**: `code`
- **Flagged Checks**: None
- **Downgraded Checks**: None
- **Selection Rationale**: Clean control (code): pure numerical routines (mean, variance), zero defects injected.
- **Expected Gold Verdicts**:
  - `all_checks`: `no_flag`

### 2. `eval_code_02` (ID 132) — `clean`
- **Type**: `code`
- **Flagged Checks**: None
- **Downgraded Checks**: None
- **Selection Rationale**: Clean control (code): clean PyMETA Python module, passes all 5 code quality checks.
- **Expected Gold Verdicts**:
  - `all_checks`: `no_flag`

### 3. `eval_code_08` (ID 138) — `clean`
- **Type**: `code`
- **Flagged Checks**: None
- **Downgraded Checks**: None
- **Selection Rationale**: Clean control (code): clean mathematical library functions, no flags or downgrades.
- **Expected Gold Verdicts**:
  - `all_checks`: `no_flag`

### 4. `eval_mixed_02` (ID 152) — `clean`
- **Type**: `mixed`
- **Flagged Checks**: None
- **Downgraded Checks**: None
- **Selection Rationale**: Clean control (mixed): complete paper + clean code + valid RAI disclosure, 0 flags across all 15 checks.
- **Expected Gold Verdicts**:
  - `all_checks`: `no_flag`

### 5. `eval_mixed_04` (ID 154) — `clean`
- **Type**: `mixed`
- **Flagged Checks**: None
- **Downgraded Checks**: None
- **Selection Rationale**: Clean control (mixed): complete empirical paper with valid citations, code, and disclosure.
- **Expected Gold Verdicts**:
  - `all_checks`: `no_flag`

### 6. `eval_mixed_12` (ID 162) — `single_issue`
- **Type**: `mixed`
- **Flagged Checks**: `cite-doi-resolvable`
- **Downgraded Checks**: None
- **Selection Rationale**: Single-issue (citation): injected corrupted CiteMe DOI (10.0000/corrupt.citeme.05).
- **Expected Gold Verdicts**:
  - `cite-doi-resolvable`: `flag`

### 7. `eval_prose_07` (ID 117) — `single_issue`
- **Type**: `prose`
- **Flagged Checks**: `cite-doi-resolvable`, `struct-minimum-length`
- **Downgraded Checks**: None
- **Selection Rationale**: Single-issue focus on cite-no-duplicates: reference list contains distinct items; auditor verifies absence of duplicates.
- **Expected Gold Verdicts**:
  - `cite-no-duplicates`: `no_flag`
  - `cite-doi-resolvable`: `flag`
  - `struct-minimum-length`: `flag`

### 8. `eval_code_18` (ID 148) — `single_issue`
- **Type**: `code`
- **Flagged Checks**: `code-ruff-clean`
- **Downgraded Checks**: None
- **Selection Rationale**: Single-issue (code): syntax defect / comment trigger; flagged code-ruff-clean.
- **Expected Gold Verdicts**:
  - `code-ruff-clean`: `flag`

### 9. `eval_code_16` (ID 146) — `single_issue`
- **Type**: `code`
- **Flagged Checks**: None
- **Downgraded Checks**: `code-file-loc-limit`, `code-modularity`
- **Selection Rationale**: Single-issue focus on code-modularity: 550 helper functions; model flagged modularity, verifier downgraded.
- **Expected Gold Verdicts**:
  - `code-modularity`: `flag`
  - `code-file-loc-limit`: `flag`

### 10. `eval_prose_04` (ID 114) — `single_issue`
- **Type**: `prose`
- **Flagged Checks**: `rai-sufficiency-judgment`, `struct-minimum-length`, `struct-required-sections`, `struct-semantic-coherence`
- **Downgraded Checks**: `rai-section-present`
- **Selection Rationale**: Single-issue focus on rai-sufficiency: note omits empirical sections and lacks complete AI disclosure.
- **Expected Gold Verdicts**:
  - `rai-sufficiency-judgment`: `flag`
  - `struct-minimum-length`: `flag`
  - `struct-required-sections`: `flag`
  - `struct-semantic-coherence`: `flag`

### 11. `eval_code_04` (ID 134) — `adversarial_downgrade`
- **Type**: `code`
- **Flagged Checks**: None
- **Downgraded Checks**: `code-file-loc-limit`, `code-modularity`
- **Selection Rationale**: Adversarial downgrade: 1650 LOC file with 550 functions; model cited file:__init__.py:1, correctly downgraded by verifier.
- **Expected Gold Verdicts**:
  - `code-file-loc-limit`: `flag`
  - `code-modularity`: `flag`

### 12. `eval_mixed_19` (ID 169) — `adversarial_downgrade`
- **Type**: `mixed`
- **Flagged Checks**: `rai-sufficiency-judgment`, `rai-task-named`
- **Downgraded Checks**: `code-file-loc-limit`, `code-modularity`
- **Selection Rationale**: Adversarial downgrade: 2 code check downgrades due to truncated location span, plus RAI flags in mixed submission.
- **Expected Gold Verdicts**:
  - `code-file-loc-limit`: `flag`
  - `code-modularity`: `flag`
  - `rai-sufficiency-judgment`: `flag`
  - `rai-task-named`: `flag`

### 13. `eval_prose_06` (ID 116) — `adversarial_downgrade`
- **Type**: `prose`
- **Flagged Checks**: `cite-doi-resolvable`, `struct-claim-evidence-alignment`, `struct-minimum-length`
- **Downgraded Checks**: `rai-section-present`
- **Selection Rationale**: Adversarial downgrade: HALLMARK prompt override injection; model explanation for rai-section-present correctly downgraded.
- **Expected Gold Verdicts**:
  - `rai-section-present`: `no_flag`
  - `cite-doi-resolvable`: `flag`

### 14. `eval_prose_10` (ID 120) — `adversarial_downgrade`
- **Type**: `prose`
- **Flagged Checks**: `cite-doi-resolvable`, `struct-claim-evidence-alignment`, `struct-minimum-length`
- **Downgraded Checks**: `rai-section-present`
- **Selection Rationale**: Adversarial downgrade: HALLMARK JSON bypass injection; model explanation for rai-section-present correctly downgraded.
- **Expected Gold Verdicts**:
  - `rai-section-present`: `no_flag`
  - `cite-doi-resolvable`: `flag`

### 15. `eval_prose_12` (ID 122) — `adversarial_downgrade`
- **Type**: `prose`
- **Flagged Checks**: `cite-doi-resolvable`, `struct-claim-evidence-alignment`, `struct-minimum-length`
- **Downgraded Checks**: `rai-human-oversight-described`
- **Selection Rationale**: Adversarial downgrade: model cited invalid file location grammar on prose submission, correctly rejected by location verifier.
- **Expected Gold Verdicts**:
  - `rai-human-oversight-described`: `no_flag`
  - `cite-doi-resolvable`: `flag`

