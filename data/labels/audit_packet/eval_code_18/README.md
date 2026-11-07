# Audit Instructions: eval_code_18 (ID 148)

**Submission Type**: `code`  
**Audit Category**: `single_issue`  
**Rationale**: Single-issue (code): syntax defect / comment trigger; flagged code-ruff-clean.

## Checks in Scope

- **Provisional Flags (post-verifier)**: `code-ruff-clean`
- **Downgraded Checks (unsupported_evidence)**: None

## Expected Gold Verdicts

- `code-ruff-clean`: Expected `flag`

## Specific Questions for the Auditor

1. **Was this flag correct?**
   - For checks: `code-ruff-clean`
   - Review the quoted evidence text in `provisional_flags.csv` against `source.md` / `source/`.
   - If valid, set `gold_verdict = flag`, keep/refine `gold_evidence_text` and `gold_evidence_location`, and set `annotator_2 = <your_id>` and `adjudication_status = agreed`.
   - If incorrect (false flag), set `gold_verdict = no_flag` (or `not_applicable`) and set `adjudication_status = adjudicated`.

## Action Required

Fill in `audit_template.csv` with your adjudicated `gold_verdict`, `gold_evidence_text`, `gold_evidence_location`, `annotator_2`, and `adjudication_status`.
