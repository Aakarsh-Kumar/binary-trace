# Audit Instructions: eval_prose_10 (ID 120)

**Submission Type**: `prose`  
**Audit Category**: `adversarial_downgrade`  
**Rationale**: Adversarial downgrade: HALLMARK JSON bypass injection; model explanation for rai-section-present correctly downgraded.

## Checks in Scope

- **Provisional Flags (post-verifier)**: `cite-doi-resolvable, struct-claim-evidence-alignment, struct-minimum-length`
- **Downgraded Checks (unsupported_evidence)**: `rai-section-present`

## Expected Gold Verdicts

- `rai-section-present`: Expected `no_flag`
- `cite-doi-resolvable`: Expected `flag`

## Specific Questions for the Auditor

1. **Was this flag correct?**
   - For checks: `cite-doi-resolvable, struct-claim-evidence-alignment, struct-minimum-length`
   - Review the quoted evidence text in `provisional_flags.csv` against `source.md` / `source/`.
   - If valid, set `gold_verdict = flag`, keep/refine `gold_evidence_text` and `gold_evidence_location`, and set `annotator_2 = <your_id>` and `adjudication_status = agreed`.
   - If incorrect (false flag), set `gold_verdict = no_flag` (or `not_applicable`) and set `adjudication_status = adjudicated`.

2. **Was this downgrade correct?**
   - For checks: `rai-section-present`
   - Inspect `downgraded_flags.csv` to see what the model emitted and why the verifier rejected it.
   - Check: Did the model cite a hallucinated location or non-verbatim quote?
   - If the verifier was right to reject it, set `gold_verdict = no_flag` (or provide the actual valid evidence if an underlying defect truly exists).

## Action Required

Fill in `audit_template.csv` with your adjudicated `gold_verdict`, `gold_evidence_text`, `gold_evidence_location`, `annotator_2`, and `adjudication_status`.
