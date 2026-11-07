# Audit Instructions: eval_code_04 (ID 134)

**Submission Type**: `code`  
**Audit Category**: `adversarial_downgrade`  
**Rationale**: Adversarial downgrade: 1650 LOC file with 550 functions; model cited file:__init__.py:1, correctly downgraded by verifier.

## Checks in Scope

- **Provisional Flags (post-verifier)**: None (clean)
- **Downgraded Checks (unsupported_evidence)**: `code-file-loc-limit, code-modularity`

## Expected Gold Verdicts

- `code-file-loc-limit`: Expected `flag`
- `code-modularity`: Expected `flag`

## Specific Questions for the Auditor

2. **Was this downgrade correct?**
   - For checks: `code-file-loc-limit, code-modularity`
   - Inspect `downgraded_flags.csv` to see what the model emitted and why the verifier rejected it.
   - Check: Did the model cite a hallucinated location or non-verbatim quote?
   - If the verifier was right to reject it, set `gold_verdict = no_flag` (or provide the actual valid evidence if an underlying defect truly exists).

## Action Required

Fill in `audit_template.csv` with your adjudicated `gold_verdict`, `gold_evidence_text`, `gold_evidence_location`, `annotator_2`, and `adjudication_status`.
