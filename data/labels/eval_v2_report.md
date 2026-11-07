# Evaluation Report v2 (P2 Milestone M2 — Audit-Corrected Run)

## Overview
This report presents the empirical evaluation metrics computed from the audit-corrected `data/labels/gold_labels.csv` against execution verdicts in the compliance review database across 15 audited submissions (75 evaluated label instances covering 19 distinct checks across 4 capabilities).

Summary Metrics:
- **Total Labels Evaluated**: 75
- **Submissions Audited**: 15 (5 clean, 5 single-issue, 5 adversarial-downgrade)
- **Pre-Verifier Recall**: 1.0000 (20/20 true issues flagged by model)
- **Pre-Verifier Precision**: 0.6897 (20 TP / 29 total model flags)
- **Post-Verifier Recall**: 0.5000 (10/20 surviving flags)
- **Post-Verifier Precision**: 0.5263 (10 TP / 19 surviving flags)
- **Post-Verifier FFR**: 0.4737 (9 false flags / 19 total surviving flags)
- **Verdict Agreement across runs ($k=3$)**: 0.9911 (99.11%)
- **Token Jaccard across runs ($k=3$)**: 1.0000

---

## Table 1: Per-Check Metrics

> [!NOTE]
> By design constraint (PRD §6.2, ARCHITECTURE §6.4), any check with fewer than 10 gold-flag instances ($N_{\text{gold}} < 10$) emits `insufficient_sample` for precision, recall, and FFR. In this Mode B audit subset (15 submissions, 75 label instances across 19 checks), all individual checks have $N_{\text{gold}} \le 5 < 10$.

| check_id | capability | N_gold_flags | N_clean | pre_precision | post_precision | pre_recall | post_recall | post_ffr | agreement |
|---|---|---|---|---|---|---|---|---|---|
| code-error-handling | code-quality | 0 | 5 | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample | 1.0000 |
| code-file-loc-limit | code-quality | 3 | 5 | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample | 1.0000 |
| code-modularity | code-quality | 3 | 5 | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample | 1.0000 |
| code-pylint-clean | code-quality | 0 | 5 | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample | 1.0000 |
| code-ruff-clean | code-quality | 0 | 6 | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample | 1.0000 |
| cite-claim-supported | citation-integrity | 0 | 2 | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample | 1.0000 |
| cite-context-accurate | citation-integrity | 0 | 2 | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample | 1.0000 |
| cite-doi-resolvable | citation-integrity | 5 | 2 | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample | 1.0000 |
| cite-no-duplicates | citation-integrity | 0 | 3 | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample | 1.0000 |
| cite-not-retracted | citation-integrity | 0 | 2 | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample | 1.0000 |
| rai-human-oversight-described | rai-disclosure | 1 | 2 | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample | 0.8889 |
| rai-section-present | rai-disclosure | 3 | 2 | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample | 1.0000 |
| rai-sufficiency-judgment | rai-disclosure | 0 | 4 | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample | 0.9167 |
| rai-task-named | rai-disclosure | 0 | 3 | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample | 1.0000 |
| rai-tool-named | rai-disclosure | 0 | 2 | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample | 1.0000 |
| struct-minimum-length | report-structure | 5 | 0 | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample | 1.0000 |
| struct-required-sections | report-structure | 0 | 1 | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample | 1.0000 |
| struct-semantic-coherence | report-structure | 0 | 1 | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample | 1.0000 |
| struct-claim-evidence-alignment | report-structure | 0 | 3 | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample | 1.0000 |

---

## Table 2: Per-Capability Aggregate Metrics

| capability | N_gold_flags | N_clean | pre_precision | post_precision | pre_recall | post_recall | FFR_or_insufficient |
|---|---|---|---|---|---|---|---|
| code-quality | 6 | 26 | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample |
| citation-integrity | 5 | 11 | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample |
| rai-disclosure | 4 | 13 | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample |
| report-structure | 5 | 5 | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample |

*(Note: Raw unconstrained metrics across capabilities before sample thresholding:
- `code-quality`: pre_P = 0.8571 (6/7), pre_R = 1.0000 (6/6); post_P = 0.0000 (0/1), post_R = 0.0000 (0/6), post_FFR = 1.0000 (1/1);
- `citation-integrity`: pre_P = 1.0000 (5/5), pre_R = 1.0000 (5/5); post_P = 1.0000 (5/5), post_R = 1.0000 (5/5), post_FFR = 0.0000 (0/5);
- `rai-disclosure`: pre_P = 0.5714 (4/7), pre_R = 1.0000 (4/4); post_P = 0.0000 (0/3), post_R = 0.0000 (0/4), post_FFR = 1.0000 (3/3);
- `report-structure`: pre_P = 0.5000 (5/10), pre_R = 1.0000 (5/5); post_P = 0.5000 (5/10), post_R = 1.0000 (5/5), post_FFR = 0.5000 (5/10)).*

---

## Table 3: Verifier Correctness on Downgrades

Downgrades audited represent items where the model produced a flag in execution runs, but the evidence verifier downgraded the verdict to `unsupported_evidence`. Correct rejections denote items where human annotation confirmed no violation (`gold_verdict = no_flag`), while wrong rejections denote items where human annotation confirmed a genuine violation (`gold_verdict = flag`).

| capability | downgrades_audited | correct_rejections | wrong_rejections | verifier_precision |
|---|---|---|---|---|
| code-quality | 6 | 0 | 6 | 0.0000 |
| citation-integrity | 0 | 0 | 0 | N/A |
| rai-disclosure | 4 | 0 | 4 | 0.0000 |
| report-structure | 0 | 0 | 0 | N/A |

*(Note: Across $k=3$ runs, 28 execution verdicts were downgraded: 18 in `code-quality` across 6 items and 10 in `rai-disclosure` across 4 items. All 10 audited check instances were true compliance violations where the model generated non-verbatim quote spans, leading to 0.0000 verifier precision on rejections).*

---

## Table 4: Confusion Matrices

> [!NOTE]
> Per the evaluation protocol, checks with $N_{\text{gold}} \ge 10$ require confusion matrices. In this 15-submission audit packet, no individual check had $N_{\text{gold}} \ge 10$ (maximum sample per check was 8). Below are the post-verifier 2x2 confusion matrices (TP, FP, FN, TN) for all 19 checks across the audited corpus for complete transparency.

| check_id | sample_size (N_gold) | N_gold_flags | TP | FP | FN | TN |
|---|---|---|---|---|---|---|
| code-error-handling | 5 | 0 | 0 | 0 | 0 | 5 |
| code-file-loc-limit | 8 | 3 | 0 | 0 | 3 | 5 |
| code-modularity | 8 | 3 | 0 | 0 | 3 | 5 |
| code-pylint-clean | 5 | 0 | 0 | 0 | 0 | 5 |
| code-ruff-clean | 6 | 0 | 0 | 1 | 0 | 5 |
| cite-claim-supported | 2 | 0 | 0 | 0 | 0 | 2 |
| cite-context-accurate | 2 | 0 | 0 | 0 | 0 | 2 |
| cite-doi-resolvable | 7 | 5 | 5 | 0 | 0 | 2 |
| cite-no-duplicates | 3 | 0 | 0 | 0 | 0 | 3 |
| cite-not-retracted | 2 | 0 | 0 | 0 | 0 | 2 |
| rai-human-oversight-described | 3 | 1 | 0 | 0 | 1 | 2 |
| rai-section-present | 5 | 3 | 0 | 0 | 3 | 2 |
| rai-sufficiency-judgment | 4 | 0 | 0 | 2 | 0 | 2 |
| rai-task-named | 3 | 0 | 0 | 1 | 0 | 2 |
| rai-tool-named | 2 | 0 | 0 | 0 | 0 | 2 |
| struct-minimum-length | 5 | 5 | 5 | 0 | 0 | 0 |
| struct-required-sections | 1 | 0 | 0 | 1 | 0 | 0 |
| struct-semantic-coherence | 1 | 0 | 0 | 1 | 0 | 0 |
| struct-claim-evidence-alignment | 3 | 0 | 0 | 3 | 0 | 0 |

---

## Interpretation of the Corrected Run and Pre vs. Post Verifier Gap

### Material Shift from Initial Evaluation Run
The previous evaluation run (eval_v1) reported a post-verifier precision of 0.0000 and post-verifier recall of 0.0000 (with an apparent 100% false-flag rate). In this corrected run (eval_v2), the empirical metrics shift materially:
- **Post-Verifier Precision** increases from **0.0000 to 0.5263** (10 true positive flags among 19 surviving flags).
- **Post-Verifier Recall** increases from **0.0000 to 0.5000** (10 of the 20 ground-truth violations verified and surfaced).
- **Pre-Verifier Precision** increases from **0.3448 to 0.6897**, while Pre-Verifier Recall remains perfect at **1.0000** (20/20 true defects captured by the model).
- **False-Flag Rate (FFR)** drops from **1.0000 down to 0.4737**.

### Origin of the Difference: Correction of 10 Human Audit Errors
This dramatic correction stems directly from resolving 10 audit mislabelings in the original gold reference set:
1. **`struct-minimum-length` (5 prose submissions)**: In eval_v1, five prose submissions (`eval_prose_04`, `eval_prose_06`, `eval_prose_07`, `eval_prose_10`, `eval_prose_12`) each containing between 50 and 187 words were erroneously marked `no_flag`. Because the compliance specification establishes a strict 500-word minimum threshold, all 5 submissions are genuine non-compliant violations. The verifier had correctly verified and surfaced the model's flags; correcting the reference labels converted 5 false positives into 5 verified true positives (`post_tp = 5`, `post_fp = 5` for structural checks).
2. **`cite-doi-resolvable` (5 submissions)**: In eval_v1, five submissions containing injected corrupted DOIs of the pattern `10.0000/corrupt.*` (`eval_mixed_12`, `eval_prose_06`, `eval_prose_07`, `eval_prose_10`, `eval_prose_12`) were mistakenly audited as `no_flag`. Correcting these labels revealed that all 5 DOI-unresolvable flags generated by the review system and verified by exact string matching against the reference sections were genuine true positives (`post_tp = 5`, `post_fp = 0` on `cite-doi-resolvable`). In fact, on `citation-integrity`, post-verifier precision and recall are both **1.0000** with an FFR of **0.0000**.

### Pre vs. Post Verifier Gap on Semantic/Code Checks
The remaining gap between pre-verifier recall (1.0000) and post-verifier recall (0.5000) is entirely concentrated in `code-quality` (6 missed true positives) and `rai-disclosure` (4 missed true positives). In these two capabilities, the model successfully recognized all 10 true compliance defects (achieving perfect sensitivity), but summarized or paraphrased the evidence rather than extracting verbatim substrings meeting the frozen 40-character prefix and 0.92 fuzzy matching threshold. As a result, the evidence verifier faithfully downgraded all 10 true defect flags to `unsupported_evidence`. This confirms that the evidence verifier is functioning strictly according to its mathematical specification, but underscores the operational necessity of refining prompt instructions or evidence quote extractors to output exact verbatim source spans.

---

## Explicit Notes on Insufficient Sample Returns
Every check in Table 1 returns `insufficient_sample` for precision, recall, and false-flag rate. This behavior is mathematically mandated by ARCHITECTURE §6.4 and PRD §6.2:
1. **Sample Size Constraint**: In this Mode B audit subset of 15 submissions (75 evaluated checklist judgments), the number of positive gold labels per check ranges from 0 to 5 (e.g., 5 on `cite-doi-resolvable`, 5 on `struct-minimum-length`, 3 on `code-modularity`, 3 on `code-file-loc-limit`, 3 on `rai-section-present`, 1 on `rai-human-oversight-described`), all strictly below the statistical minimum threshold of $N_{\text{gold}} \ge 10$.
2. **Roadmap to Full Power**: Full quantitative certification of individual checklist items under the PRD §6.2 target (FFR < 0.15) requires completing gold annotations across the remaining 45 submissions of the evaluation corpus.
