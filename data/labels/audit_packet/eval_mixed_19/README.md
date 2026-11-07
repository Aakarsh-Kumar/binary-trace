# Audit Instructions: eval_mixed_19 (ID 169)

**Submission Type**: `mixed`  
**Audit Category**: `adversarial_downgrade`  
**Rationale**: Adversarial downgrade: 2 code check downgrades due to truncated location span, plus RAI flags in mixed submission.

## Checks in Scope

- **Provisional Flags (post-verifier)**: `rai-sufficiency-judgment, rai-task-named`
- **Downgraded Checks (unsupported_evidence)**: `code-file-loc-limit, code-modularity`

## Expected Gold Verdicts

- `code-file-loc-limit`: Expected `flag`
- `code-modularity`: Expected `flag`
- `rai-sufficiency-judgment`: Expected `flag`
- `rai-task-named`: Expected `flag`

## Specific Questions for the Auditor

1. **Was this flag correct?**
   - For checks: `rai-sufficiency-judgment, rai-task-named`
   - Review the quoted evidence text in `provisional_flags.csv` against `source.md` / `source/`.
   - If valid, set `gold_verdict = flag`, keep/refine `gold_evidence_text` and `gold_evidence_location`, and set `annotator_2 = <your_id>` and `adjudication_status = agreed`.
   - If incorrect (false flag), set `gold_verdict = no_flag` (or `not_applicable`) and set `adjudication_status = adjudicated`.

2. **Was this downgrade correct?**
   - For checks: `code-file-loc-limit, code-modularity`
   - Inspect `downgraded_flags.csv` to see what the model emitted and why the verifier rejected it.
   - Check: Did the model cite a hallucinated location or non-verbatim quote?
   - If the verifier was right to reject it, set `gold_verdict = no_flag` (or provide the actual valid evidence if an underlying defect truly exists).

## Action Required

Fill in `audit_template.csv` with your adjudicated `gold_verdict`, `gold_evidence_text`, `gold_evidence_location`, `annotator_2`, and `adjudication_status`.
