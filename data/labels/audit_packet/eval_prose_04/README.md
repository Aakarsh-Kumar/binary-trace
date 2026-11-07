# Audit Instructions: eval_prose_04 (ID 114)

**Submission Type**: `prose`  
**Audit Category**: `single_issue`  
**Rationale**: Single-issue focus on rai-sufficiency: note omits empirical sections and lacks complete AI disclosure.

## Checks in Scope

- **Provisional Flags (post-verifier)**: `rai-sufficiency-judgment, struct-minimum-length, struct-required-sections, struct-semantic-coherence`
- **Downgraded Checks (unsupported_evidence)**: `rai-section-present`

## Expected Gold Verdicts

- `rai-sufficiency-judgment`: Expected `flag`
- `struct-minimum-length`: Expected `flag`
- `struct-required-sections`: Expected `flag`
- `struct-semantic-coherence`: Expected `flag`

## Specific Questions for the Auditor

1. **Was this flag correct?**
   - For checks: `rai-sufficiency-judgment, struct-minimum-length, struct-required-sections, struct-semantic-coherence`
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
