# Audit Instructions: eval_prose_07 (ID 117)

**Submission Type**: `prose`  
**Audit Category**: `single_issue`  
**Rationale**: Single-issue focus on cite-no-duplicates: reference list contains distinct items; auditor verifies absence of duplicates.

## Checks in Scope

- **Provisional Flags (post-verifier)**: `cite-doi-resolvable, struct-minimum-length`
- **Downgraded Checks (unsupported_evidence)**: None

## Expected Gold Verdicts

- `cite-no-duplicates`: Expected `no_flag`
- `cite-doi-resolvable`: Expected `flag`
- `struct-minimum-length`: Expected `flag`

## Specific Questions for the Auditor

1. **Was this flag correct?**
   - For checks: `cite-doi-resolvable, struct-minimum-length`
   - Review the quoted evidence text in `provisional_flags.csv` against `source.md` / `source/`.
   - If valid, set `gold_verdict = flag`, keep/refine `gold_evidence_text` and `gold_evidence_location`, and set `annotator_2 = <your_id>` and `adjudication_status = agreed`.
   - If incorrect (false flag), set `gold_verdict = no_flag` (or `not_applicable`) and set `adjudication_status = adjudicated`.

## Action Required

Fill in `audit_template.csv` with your adjudicated `gold_verdict`, `gold_evidence_text`, `gold_evidence_location`, `annotator_2`, and `adjudication_status`.
