# Audit Instructions: eval_code_16 (ID 146)

**Submission Type**: `code`  
**Audit Category**: `single_issue`  
**Rationale**: Single-issue focus on code-modularity: 550 helper functions; model flagged modularity, verifier downgraded.

## Checks in Scope

- **Provisional Flags (post-verifier)**: None (clean)
- **Downgraded Checks (unsupported_evidence)**: `code-file-loc-limit, code-modularity`

## Expected Gold Verdicts

- `code-modularity`: Expected `flag`
- `code-file-loc-limit`: Expected `flag`

## Specific Questions for the Auditor

2. **Was this downgrade correct?**
   - For checks: `code-file-loc-limit, code-modularity`
   - Inspect `downgraded_flags.csv` to see what the model emitted and why the verifier rejected it.
   - Check: Did the model cite a hallucinated location or non-verbatim quote?
   - If the verifier was right to reject it, set `gold_verdict = no_flag` (or provide the actual valid evidence if an underlying defect truly exists).

## Action Required

Fill in `audit_template.csv` with your adjudicated `gold_verdict`, `gold_evidence_text`, `gold_evidence_location`, `annotator_2`, and `adjudication_status`.
