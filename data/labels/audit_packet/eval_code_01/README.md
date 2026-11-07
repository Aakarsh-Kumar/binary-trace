# Audit Instructions: eval_code_01 (ID 131)

**Submission Type**: `code`  
**Audit Category**: `clean`  
**Rationale**: Clean control (code): pure numerical routines (mean, variance), zero defects injected.

## Checks in Scope

- **Provisional Flags (post-verifier)**: None (clean)
- **Downgraded Checks (unsupported_evidence)**: None

## Expected Gold Verdicts

- `all_checks`: Expected `no_flag`

## Specific Questions for the Auditor

1. **False Negative Check**: Did the system correctly identify that this submission is clean?
2. Confirm that `gold_verdict` is `no_flag` for all checks, or if a defect was missed, provide the verbatim evidence span.
## Action Required

Fill in `audit_template.csv` with your adjudicated `gold_verdict`, `gold_evidence_text`, `gold_evidence_location`, `annotator_2`, and `adjudication_status`.
