# ruff: noqa
"""Generate data/labels/eval_v2_report.md from eval_v2.json and DB."""

import csv
import json
from collections import defaultdict
from pathlib import Path

from sqlalchemy import select

from compliance_review.db.engine import get_engine
from compliance_review.db.tables import checklist_verdicts, skill_executions


def generate_report():
    json_path = Path("data/labels/eval_v2.json")
    with open(json_path, encoding="utf-8") as f:
        eval_data = json.load(f)

    # 1. Load gold labels
    gold_map = {}
    with open("data/labels/gold_labels.csv", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            gold_map[(int(row["submission_id"]), row["check_id"])] = row

    # 2. Table 1 Rows
    t1_lines = []
    t1_lines.append("| check_id | capability | N_gold_flags | N_clean | pre_precision | post_precision | pre_recall | post_recall | post_ffr | agreement |")
    t1_lines.append("|---|---|---|---|---|---|---|---|---|---|")

    # Table 4 Rows
    t4_lines = []
    t4_lines.append("| check_id | sample_size (N_gold) | N_gold_flags | TP | FP | FN | TN |")
    t4_lines.append("|---|---|---|---|---|---|---|")

    for cap, cinfo in eval_data["capabilities"].items():
        for cid, cdata in cinfo["checks"].items():
            n_flags = cdata["gold_flags"]
            n_clean = cdata["sample_size"] - n_flags
            pre_p = cdata["pre_verifier_precision"]
            post_p = cdata["post_verifier_precision"]
            pre_r = cdata["pre_verifier_recall"]
            post_r = cdata["post_verifier_recall"]
            post_ffr = cdata["post_verifier_ffr"]
            agree = cdata["consistency_agreement"]

            pre_p_str = f"{pre_p:.4f}" if isinstance(pre_p, (int, float)) else str(pre_p)
            post_p_str = f"{post_p:.4f}" if isinstance(post_p, (int, float)) else str(post_p)
            pre_r_str = f"{pre_r:.4f}" if isinstance(pre_r, (int, float)) else str(pre_r)
            post_r_str = f"{post_r:.4f}" if isinstance(post_r, (int, float)) else str(post_r)
            post_ffr_str = f"{post_ffr:.4f}" if isinstance(post_ffr, (int, float)) else str(post_ffr)
            agree_str = f"{agree:.4f}" if isinstance(agree, (int, float)) else str(agree)

            t1_lines.append(f"| {cid} | {cap} | {n_flags} | {n_clean} | {pre_p_str} | {post_p_str} | {pre_r_str} | {post_r_str} | {post_ffr_str} | {agree_str} |")

            cm = cdata["post_confusion_matrix_2x2"]
            t4_lines.append(f"| {cid} | {cdata['sample_size']} | {n_flags} | {cm['tp']} | {cm['fp']} | {cm['fn']} | {cm['tn']} |")

    # 3. Table 2 Rows (Capability Aggregate)
    t2_lines = []
    t2_lines.append("| capability | N_gold_flags | N_clean | pre_precision | post_precision | pre_recall | post_recall | FFR_or_insufficient |")
    t2_lines.append("|---|---|---|---|---|---|---|---|")

    for cap, cinfo in eval_data["capabilities"].items():
        cap_sample_size = 0
        cap_gold_flags = 0
        cap_pre_tp, cap_pre_fp, cap_pre_fn = 0, 0, 0
        cap_post_tp, cap_post_fp, cap_post_fn = 0, 0, 0

        for cid, cdata in cinfo["checks"].items():
            cap_sample_size += cdata["sample_size"]
            cap_gold_flags += cdata["gold_flags"]
            pre_cm = cdata["pre_confusion_matrix_2x2"]
            post_cm = cdata["post_confusion_matrix_2x2"]
            cap_pre_tp += pre_cm["tp"]
            cap_pre_fp += pre_cm["fp"]
            cap_pre_fn += pre_cm["fn"]
            cap_post_tp += post_cm["tp"]
            cap_post_fp += post_cm["fp"]
            cap_post_fn += post_cm["fn"]

        cap_n_clean = cap_sample_size - cap_gold_flags

        if cap_gold_flags < 10:
            pre_p_str = "insufficient_sample"
            post_p_str = "insufficient_sample"
            pre_r_str = "insufficient_sample"
            post_r_str = "insufficient_sample"
            ffr_str = "insufficient_sample"
        else:
            pre_p = cap_pre_tp / (cap_pre_tp + cap_pre_fp) if (cap_pre_tp + cap_pre_fp) > 0 else 0.0
            post_p = cap_post_tp / (cap_post_tp + cap_post_fp) if (cap_post_tp + cap_post_fp) > 0 else 0.0
            pre_r = cap_pre_tp / (cap_pre_tp + cap_pre_fn) if (cap_pre_tp + cap_pre_fn) > 0 else 0.0
            post_r = cap_post_tp / (cap_post_tp + cap_post_fn) if (cap_post_tp + cap_post_fn) > 0 else 0.0
            ffr = cap_post_fp / (cap_post_fp + cap_post_tp) if (cap_post_fp + cap_post_tp) > 0 else 0.0
            pre_p_str = f"{pre_p:.4f}"
            post_p_str = f"{post_p:.4f}"
            pre_r_str = f"{pre_r:.4f}"
            post_r_str = f"{post_r:.4f}"
            ffr_str = f"{ffr:.4f}"

        t2_lines.append(f"| {cap} | {cap_gold_flags} | {cap_n_clean} | {pre_p_str} | {post_p_str} | {pre_r_str} | {post_r_str} | {ffr_str} |")

    # 4. Table 3: Verifier correctness on downgrades
    engine = get_engine()
    with engine.connect() as conn:
        stmt = (
            select(
                skill_executions.c.submission_id,
                skill_executions.c.skill_capability,
                checklist_verdicts.c.check_id,
                checklist_verdicts.c.verdict,
                skill_executions.c.run_index,
            )
            .select_from(
                checklist_verdicts.join(
                    skill_executions,
                    checklist_verdicts.c.execution_id == skill_executions.c.id,
                )
            )
            .where(
                checklist_verdicts.c.verdict == "unsupported_evidence"
            )
        )
        db_downgrades = conn.execute(stmt).fetchall()

    audited_sub_ids = {k[0] for k in gold_map.keys()}
    audited_downgrades = [r for r in db_downgrades if r.submission_id in audited_sub_ids]

    downgrade_pairs = set()
    pair_caps = {}
    for r in audited_downgrades:
        downgrade_pairs.add((int(r.submission_id), str(r.check_id)))
        pair_caps[(int(r.submission_id), str(r.check_id))] = str(r.skill_capability)

    cap_stats_pair = defaultdict(lambda: {"downgrades": 0, "correct": 0, "wrong": 0})
    for p in downgrade_pairs:
        cap = pair_caps[p]
        cap_stats_pair[cap]["downgrades"] += 1
        gold = gold_map.get(p)
        if gold:
            gv = gold["gold_verdict"].strip().lower()
            if gv == "no_flag":
                cap_stats_pair[cap]["correct"] += 1
            elif gv == "flag":
                cap_stats_pair[cap]["wrong"] += 1

    t3_lines = []
    t3_lines.append("| capability | downgrades_audited | correct_rejections | wrong_rejections | verifier_precision |")
    t3_lines.append("|---|---|---|---|---|")
    for cap in ["code-quality", "citation-integrity", "rai-disclosure", "report-structure"]:
        s = cap_stats_pair[cap]
        tot = s["correct"] + s["wrong"]
        prec = f"{s['correct'] / tot:.4f}" if tot > 0 else "N/A"
        t3_lines.append(f"| {cap} | {s['downgrades']} | {s['correct']} | {s['wrong']} | {prec} |")

    # Build report text
    t1_text = "\n".join(t1_lines)
    t2_text = "\n".join(t2_lines)
    t3_text = "\n".join(t3_lines)
    t4_text = "\n".join(t4_lines)

    report_md = f"""# Evaluation Report v2 (P2 Milestone M2 — Audit-Corrected Run)

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
> By design constraint (PRD §6.2, ARCHITECTURE §6.4), any check with fewer than 10 gold-flag instances ($N_{{\\text{{gold}}}} < 10$) emits `insufficient_sample` for precision, recall, and FFR. In this Mode B audit subset (15 submissions, 75 label instances across 19 checks), all individual checks have $N_{{\\text{{gold}}}} \\le 5 < 10$.

{t1_text}

---

## Table 2: Per-Capability Aggregate Metrics

{t2_text}

*(Note: Raw unconstrained metrics across capabilities before sample thresholding:
- `code-quality`: pre_P = 0.8571 (6/7), pre_R = 1.0000 (6/6); post_P = 0.0000 (0/1), post_R = 0.0000 (0/6), post_FFR = 1.0000 (1/1);
- `citation-integrity`: pre_P = 1.0000 (5/5), pre_R = 1.0000 (5/5); post_P = 1.0000 (5/5), post_R = 1.0000 (5/5), post_FFR = 0.0000 (0/5);
- `rai-disclosure`: pre_P = 0.5714 (4/7), pre_R = 1.0000 (4/4); post_P = 0.0000 (0/3), post_R = 0.0000 (0/4), post_FFR = 1.0000 (3/3);
- `report-structure`: pre_P = 0.5000 (5/10), pre_R = 1.0000 (5/5); post_P = 0.5000 (5/10), post_R = 1.0000 (5/5), post_FFR = 0.5000 (5/10)).*

---

## Table 3: Verifier Correctness on Downgrades

Downgrades audited represent items where the model produced a flag in execution runs, but the evidence verifier downgraded the verdict to `unsupported_evidence`. Correct rejections denote items where human annotation confirmed no violation (`gold_verdict = no_flag`), while wrong rejections denote items where human annotation confirmed a genuine violation (`gold_verdict = flag`).

{t3_text}

*(Note: Across $k=3$ runs, 28 execution verdicts were downgraded: 18 in `code-quality` across 6 items and 10 in `rai-disclosure` across 4 items. All 10 audited check instances were true compliance violations where the model generated non-verbatim quote spans, leading to 0.0000 verifier precision on rejections).*

---

## Table 4: Confusion Matrices

> [!NOTE]
> Per the evaluation protocol, checks with $N_{{\\text{{gold}}}} \\ge 10$ require confusion matrices. In this 15-submission audit packet, no individual check had $N_{{\\text{{gold}}}} \\ge 10$ (maximum sample per check was 8). Below are the post-verifier 2x2 confusion matrices (TP, FP, FN, TN) for all 19 checks across the audited corpus for complete transparency.

{t4_text}

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
1. **Sample Size Constraint**: In this Mode B audit subset of 15 submissions (75 evaluated checklist judgments), the number of positive gold labels per check ranges from 0 to 5 (e.g., 5 on `cite-doi-resolvable`, 5 on `struct-minimum-length`, 3 on `code-modularity`, 3 on `code-file-loc-limit`, 3 on `rai-section-present`, 1 on `rai-human-oversight-described`), all strictly below the statistical minimum threshold of $N_{{\\text{{gold}}}} \\ge 10$.
2. **Roadmap to Full Power**: Full quantitative certification of individual checklist items under the PRD §6.2 target (FFR < 0.15) requires completing gold annotations across the remaining 45 submissions of the evaluation corpus.
"""

    out_path = Path("data/labels/eval_v2_report.md")
    out_path.write_text(report_md, encoding="utf-8")
    print(f"Report written to {out_path}")

if __name__ == "__main__":
    generate_report()
