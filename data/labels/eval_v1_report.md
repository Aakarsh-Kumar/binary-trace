# Evaluation Report v1 (P2 Milestone M2 — Mode B Audited Subset)

## Overview
This report presents the empirical evaluation metrics computed from `data/labels/gold_labels.csv` against execution verdicts in the compliance review database across 15 audited submissions (75 evaluated label instances covering 19 distinct checks across 4 capabilities).

Summary Metrics:
- **Total Labels Evaluated**: 75
- **Submissions Audited**: 15 (5 clean, 5 single-issue, 5 adversarial-downgrade)
- **Pre-Verifier Recall**: 1.0000 (10/10 true issues flagged by model)
- **Pre-Verifier Precision**: 0.3448 (10 TP / 29 total model flags)
- **Post-Verifier Recall**: 0.0000 (0/10 surviving flags)
- **Post-Verifier Precision**: 0.0000 (0 TP / 17 surviving flags)
- **Post-Verifier FFR**: 1.0000 (17 surviving flags were false positives)
- **Verdict Agreement across runs ($k=3$)**: 0.9911 (99.11%)
- **Token Jaccard across runs ($k=3$)**: 1.0000

---

## Table 1: Per-Check Metrics

> [!NOTE]
> By design constraint (PRD §6.2, ARCHITECTURE §6.4), any check with fewer than 10 gold-flag instances ($N_{\text{gold}} < 10$) emits `insufficient_sample` for precision, recall, and FFR. In this Mode B audit subset (15 submissions, 75 label instances across 19 checks), all individual checks have $N_{\text{gold}} \le 3 < 10$.

| check_id | capability | N_gold_flags | N_clean | pre_precision | post_precision | pre_recall | post_recall | post_ffr | agreement |
|---|---|---|---|---|---|---|---|---|---|
| code-error-handling | code-quality | 0 | 5 | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample | 1.0000 |
| code-file-loc-limit | code-quality | 3 | 5 | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample | 1.0000 |
| code-modularity | code-quality | 3 | 5 | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample | 1.0000 |
| code-pylint-clean | code-quality | 0 | 5 | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample | 1.0000 |
| code-ruff-clean | code-quality | 0 | 6 | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample | 1.0000 |
| cite-claim-supported | citation-integrity | 0 | 2 | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample | 1.0000 |
| cite-context-accurate | citation-integrity | 0 | 2 | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample | 1.0000 |
| cite-doi-resolvable | citation-integrity | 0 | 7 | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample | 1.0000 |
| cite-no-duplicates | citation-integrity | 0 | 3 | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample | 1.0000 |
| cite-not-retracted | citation-integrity | 0 | 2 | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample | 1.0000 |
| rai-human-oversight-described | rai-disclosure | 1 | 2 | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample | 0.8889 |
| rai-section-present | rai-disclosure | 3 | 2 | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample | 1.0000 |
| rai-sufficiency-judgment | rai-disclosure | 0 | 4 | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample | 0.9167 |
| rai-task-named | rai-disclosure | 0 | 3 | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample | 1.0000 |
| rai-tool-named | rai-disclosure | 0 | 2 | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample | 1.0000 |
| struct-minimum-length | report-structure | 0 | 5 | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample | 1.0000 |
| struct-required-sections | report-structure | 0 | 1 | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample | 1.0000 |
| struct-semantic-coherence | report-structure | 0 | 1 | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample | 1.0000 |
| struct-claim-evidence-alignment | report-structure | 0 | 3 | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample | 1.0000 |

---

## Table 2: Per-Capability Aggregate Metrics

| capability | N_gold_flags | N_clean | pre_precision | post_precision | pre_recall | post_recall | FFR_or_insufficient |
|---|---|---|---|---|---|---|---|
| code-quality | 6 | 26 | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample |
| citation-integrity | 0 | 16 | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample |
| rai-disclosure | 4 | 13 | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample |
| report-structure | 0 | 10 | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample | insufficient_sample |

*(Note: Raw unconstrained pre-verifier precision/recall across capabilities before sample thresholding: `code-quality` pre_P = 0.8571 (6/7), pre_R = 1.0000 (6/6); `rai-disclosure` pre_P = 0.5714 (4/7), pre_R = 1.0000 (4/4); `citation-integrity` pre_P = 0.0000 (0/5), pre_R = 0.0000 (0/0); `report-structure` pre_P = 0.0000 (0/10), pre_R = 0.0000 (0/0)).*

---

## Table 3: Verifier Correctness on Downgrades

Downgrades audited represent items where the model produced a flag in execution runs, but the evidence verifier downgraded the verdict to `unsupported_evidence`. Correct rejections denote items where human annotation confirmed no violation (`gold_verdict = no_flag`), while wrong rejections denote items where human annotation confirmed a genuine violation (`gold_verdict = flag`).

| capability | downgrades_audited | correct_rejections | wrong_rejections | verifier_precision |
|---|---|---|---|---|
| code-quality | 6 | 0 | 6 | 0.0000 |
| citation-integrity | 0 | 0 | 0 | N/A |
| rai-disclosure | 4 | 0 | 4 | 0.0000 |
| report-structure | 0 | 0 | 0 | N/A |

*(Note: In row-level terms across $k=3$ runs, 28 execution verdicts were downgraded: 18 in `code-quality` across 6 items and 10 in `rai-disclosure` across 4 items. All 10 audited check instances were true compliance violations where the model generated flawed or non-verbatim quote spans, leading to 0.0000 verifier precision on rejections).*

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
| cite-doi-resolvable | 7 | 0 | 0 | 5 | 0 | 2 |
| cite-no-duplicates | 3 | 0 | 0 | 0 | 0 | 3 |
| cite-not-retracted | 2 | 0 | 0 | 0 | 0 | 2 |
| rai-human-oversight-described | 3 | 1 | 0 | 0 | 1 | 2 |
| rai-section-present | 5 | 3 | 0 | 0 | 3 | 2 |
| rai-sufficiency-judgment | 4 | 0 | 0 | 2 | 0 | 2 |
| rai-task-named | 3 | 0 | 0 | 1 | 0 | 2 |
| rai-tool-named | 2 | 0 | 0 | 0 | 0 | 2 |
| struct-minimum-length | 5 | 0 | 0 | 5 | 0 | 0 |
| struct-required-sections | 1 | 0 | 0 | 1 | 0 | 0 |
| struct-semantic-coherence | 1 | 0 | 0 | 1 | 0 | 0 |
| struct-claim-evidence-alignment | 3 | 0 | 0 | 3 | 0 | 0 |

---

## Interpretation of the Pre vs. Post Verifier Gap

### Model Sensitivity vs. Citation Exactness
Before evidence verification, Qwen3-4b exhibited flawless sensitivity across the audited corpus, achieving a raw pre-verifier recall of 1.0000 by successfully flagging all 10 true compliance defects (6 in code quality for modularity and LOC limits, and 4 in RAI disclosure for missing sections and oversight). The model's raw pre-verifier precision was 34.48% (10 true positives vs. 19 false positives). However, the model frequently paraphrased the code defect or extracted non-verbatim explanatory text rather than outputting exact 40-character verbatim substrings directly matchable against the source document.

### Impact of Frozen Evidence Verifier Gating
Because the evidence verifier strictly enforces substring grounding (prefix length $\ge 40$ characters, fuzzy threshold $\ge 0.92$ under Unicode NFKC normalization and whitespace collapse), every single true defect flag raised by the model was rejected and downgraded to `unsupported_evidence`. Consequently, post-verifier recall collapsed from 100% to 0.0000. Meanwhile, heuristic or deterministic checks with exact matching quotes survived (e.g., structural length checks on short prose and synthetic DOI lookup failures), leaving 17 surviving false flags and an overall false-flag rate (FFR) of 1.0000. As confirmed by Table 3, the verifier achieved 0.0000 precision on downgrades because all audited rejections were valid compliance defects rejected solely due to quotation formatting. This diagnostic finding demonstrates that while the evidence gate prevents hallucinated citations, model citation alignment and prompt calibration must be refined in subsequent phases to convert high pre-verifier recall into verified post-verifier precision.

---

## Explicit Notes on Insufficient Sample Returns
Every check in Table 1 returns `insufficient_sample` for precision, recall, and false-flag rate. This behavior is mathematically required by ARCHITECTURE §6.4 and PRD §6.2:
1. **Sample Size Constraint**: The Mode B audit packet sampled 15 submissions (5 clean, 5 single-issue, 5 adversarial-downgrade) yielding 75 total human-audited check judgments. Across the 19 checklist items, the number of gold-standard positive violations per check ranged from 0 to 3, well below the required statistical significance threshold of $N_{\text{gold}} \ge 10$.
2. **FFR Measurement Precondition**: Under PRD §6.2, FFR is strictly defined on clean submissions or un-flagged checks. Reporting a quantitative FFR with fewer than 10 positive reference labels would produce statistically misleading point estimates.
3. **Roadmap to Full Power**: To obtain numeric precision, recall, and FFR values across all individual checks, the remaining 45 submissions of the 60-submission evaluation corpus (or additional synthetic instances) will need full gold labeling during paper evaluation preparation.
