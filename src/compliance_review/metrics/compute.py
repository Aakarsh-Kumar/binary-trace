"""Metrics computation module with pre/post verifier split (US-35, D-018).

Computes:
- pre_verifier_precision and pre_verifier_recall
- post_verifier_precision and post_verifier_recall
- post_verifier_ffr (false-flag rate)
- consistency_agreement and consistency_jaccard across k runs
- 2x2 confusion matrices
- insufficient_sample guard (< 10 gold-flag items emits 'insufficient_sample')
"""

import csv
from pathlib import Path
from typing import Any

from sqlalchemy import Connection, select

from compliance_review.db.engine import get_engine
from compliance_review.db.tables import checklist_verdicts, skill_executions
from compliance_review.evidence.verifier import normalize_span

MIN_GOLD_FLAG_SAMPLE = 10


def _compute_jaccard(tokens1: set[str], tokens2: set[str]) -> float:
    """Compute Jaccard similarity between two token sets."""
    if not tokens1 and not tokens2:
        return 1.0
    union = tokens1 | tokens2
    if not union:
        return 0.0
    return len(tokens1 & tokens2) / len(union)


def compute_metrics(
    labels_path: Path | str,
    conn: Connection | None = None,
) -> dict[str, Any]:
    """Compute evaluation metrics from gold labels CSV against DB execution verdicts.

    Read-only contract: Never writes to database.
    """
    labels_file = Path(labels_path)
    if not labels_file.exists():
        raise FileNotFoundError(f"Labels file not found: {labels_file}")

    # 1. Parse gold labels CSV
    gold_records: list[dict[str, str]] = []
    with labels_file.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            status = row.get("adjudication_status", "").strip().lower()
            # Accept agreed, adjudicated, or if status column is empty/omitted
            if status in ("", "agreed", "adjudicated"):
                gold_records.append(row)

    if not gold_records:
        return {"summary": {"total_labels": 0}, "capabilities": {}}

    # Collect submission IDs to query
    submission_ids = {int(r["submission_id"]) for r in gold_records if r.get("submission_id")}

    # 2. Query checklist verdicts and executions (Read-Only)
    should_close_conn = False
    if conn is None:
        engine = get_engine()
        active_conn = engine.connect()
        should_close_conn = True
    else:
        active_conn = conn

    try:
        # Join checklist_verdicts with skill_executions to get run_index
        stmt = (
            select(
                checklist_verdicts.c.submission_id,
                checklist_verdicts.c.check_id,
                checklist_verdicts.c.skill_capability,
                checklist_verdicts.c.verdict,
                checklist_verdicts.c.evidence_text,
                checklist_verdicts.c.check_source,
                skill_executions.c.run_index,
            )
            .select_from(
                checklist_verdicts.join(
                    skill_executions,
                    checklist_verdicts.c.execution_id == skill_executions.c.id,
                )
            )
            .where(checklist_verdicts.c.submission_id.in_(submission_ids))
        )
        db_rows = active_conn.execute(stmt).fetchall()
    finally:
        if should_close_conn:
            active_conn.close()

    # Index DB verdicts by (submission_id, check_id) -> list of runs
    db_runs_map: dict[tuple[int, str], list[dict[str, Any]]] = {}
    for r in db_rows:
        key = (int(r.submission_id), str(r.check_id))
        db_runs_map.setdefault(key, []).append(
            {
                "run_index": int(r.run_index),
                "verdict": str(r.verdict),
                "evidence_text": r.evidence_text,
                "check_source": str(r.check_source),
            }
        )

    # 3. Aggregate per check_id
    checks_data: dict[str, dict[str, Any]] = {}

    for row in gold_records:
        sub_id = int(row["submission_id"])
        c_id = str(row["check_id"])
        cap = str(row["skill_capability"])
        gold_verdict = str(row["gold_verdict"]).strip().lower()

        if c_id not in checks_data:
            checks_data[c_id] = {
                "capability": cap,
                "gold_total": 0,
                "gold_flags": 0,
                "pre_tp": 0,
                "pre_fp": 0,
                "pre_tn": 0,
                "pre_fn": 0,
                "post_tp": 0,
                "post_fp": 0,
                "post_tn": 0,
                "post_fn": 0,
                "agreements": [],
                "jaccards": [],
            }

        item = checks_data[c_id]
        item["gold_total"] += 1
        is_gold_flag = gold_verdict == "flag"
        if is_gold_flag:
            item["gold_flags"] += 1

        # Look up system predictions for this submission and check
        runs = db_runs_map.get((sub_id, c_id), [])
        if runs:
            # Primary run is run_index 1 if present, else first run
            primary_run = next((r for r in runs if r["run_index"] == 1), runs[0])
            p_verd = primary_run["verdict"]

            # Pre-verifier: flag if verdict is flag or unsupported_evidence
            pre_flag = p_verd in ("flag", "unsupported_evidence")
            # Post-verifier: flag if verified flag
            post_flag = p_verd == "flag"

            # Compute consistency across runs for this submission
            k = len(runs)
            verd_counts: dict[str, int] = {}
            for run_item in runs:
                v = run_item["verdict"]
                verd_counts[v] = verd_counts.get(v, 0) + 1
            max_c = max(verd_counts.values()) if verd_counts else 0
            item["agreements"].append(max_c / k)

            flag_tokens: list[set[str]] = []
            for run_item in runs:
                if run_item["verdict"] == "flag" and run_item.get("evidence_text"):
                    norm = normalize_span(str(run_item["evidence_text"]))
                    tokens = set(norm.split())
                    if tokens:
                        flag_tokens.append(tokens)
            if len(flag_tokens) >= 2:
                pairwise: list[float] = []
                for i in range(len(flag_tokens)):
                    for j in range(i + 1, len(flag_tokens)):
                        pairwise.append(_compute_jaccard(flag_tokens[i], flag_tokens[j]))
                if pairwise:
                    item["jaccards"].append(sum(pairwise) / len(pairwise))
        else:
            pre_flag = False
            post_flag = False

        # Update confusion matrices
        if is_gold_flag:
            if pre_flag:
                item["pre_tp"] += 1
            else:
                item["pre_fn"] += 1

            if post_flag:
                item["post_tp"] += 1
            else:
                item["post_fn"] += 1
        else:
            if pre_flag:
                item["pre_fp"] += 1
            else:
                item["pre_tn"] += 1

            if post_flag:
                item["post_fp"] += 1
            else:
                item["post_tn"] += 1

    # 4. Compute metrics per check and capability
    cap_groups: dict[str, dict[str, Any]] = {}
    total_post_tp = 0
    total_post_fp = 0
    total_post_fn = 0
    total_pre_tp = 0
    total_pre_fp = 0
    total_pre_fn = 0

    all_agreements: list[float] = []
    all_jaccards: list[float] = []

    for c_id, data in checks_data.items():
        cap = data["capability"]
        cap_groups.setdefault(cap, {"checks": {}})

        gold_flags = data["gold_flags"]
        pre_tp = data["pre_tp"]
        pre_fp = data["pre_fp"]
        pre_fn = data["pre_fn"]

        post_tp = data["post_tp"]
        post_fp = data["post_fp"]
        post_fn = data["post_fn"]

        total_post_tp += post_tp
        total_post_fp += post_fp
        total_post_fn += post_fn
        total_pre_tp += pre_tp
        total_pre_fp += pre_fp
        total_pre_fn += pre_fn

        mean_agreement = (
            sum(data["agreements"]) / len(data["agreements"]) if data["agreements"] else 1.0
        )
        mean_jaccard = sum(data["jaccards"]) / len(data["jaccards"]) if data["jaccards"] else 0.0

        all_agreements.extend(data["agreements"])
        all_jaccards.extend(data["jaccards"])

        check_res: dict[str, Any] = {
            "sample_size": data["gold_total"],
            "gold_flags": gold_flags,
            "consistency_agreement": round(mean_agreement, 4),
            "consistency_jaccard": round(mean_jaccard, 4),
            "pre_confusion_matrix_2x2": {
                "tp": pre_tp,
                "fp": pre_fp,
                "tn": data["pre_tn"],
                "fn": pre_fn,
            },
            "post_confusion_matrix_2x2": {
                "tp": post_tp,
                "fp": post_fp,
                "tn": data["post_tn"],
                "fn": post_fn,
            },
        }

        # Insufficient sample guard (< 10 gold-flag items)
        if gold_flags < MIN_GOLD_FLAG_SAMPLE:
            check_res["pre_verifier_precision"] = "insufficient_sample"
            check_res["pre_verifier_recall"] = "insufficient_sample"
            check_res["post_verifier_precision"] = "insufficient_sample"
            check_res["post_verifier_recall"] = "insufficient_sample"
            check_res["post_verifier_ffr"] = "insufficient_sample"
        else:
            pre_p = pre_tp / (pre_tp + pre_fp) if (pre_tp + pre_fp) > 0 else 0.0
            pre_r = pre_tp / (pre_tp + pre_fn) if (pre_tp + pre_fn) > 0 else 0.0
            post_p = post_tp / (post_tp + post_fp) if (post_tp + post_fp) > 0 else 0.0
            post_r = post_tp / (post_tp + post_fn) if (post_tp + post_fn) > 0 else 0.0
            ffr = post_fp / (post_fp + post_tp) if (post_fp + post_tp) > 0 else 0.0

            check_res["pre_verifier_precision"] = round(pre_p, 4)
            check_res["pre_verifier_recall"] = round(pre_r, 4)
            check_res["post_verifier_precision"] = round(post_p, 4)
            check_res["post_verifier_recall"] = round(post_r, 4)
            check_res["post_verifier_ffr"] = round(ffr, 4)

        cap_groups[cap]["checks"][c_id] = check_res

    # Overall aggregates
    overall_post_p = (
        total_post_tp / (total_post_tp + total_post_fp)
        if (total_post_tp + total_post_fp) > 0
        else 0.0
    )
    overall_post_r = (
        total_post_tp / (total_post_tp + total_post_fn)
        if (total_post_tp + total_post_fn) > 0
        else 0.0
    )
    overall_pre_p = (
        total_pre_tp / (total_pre_tp + total_pre_fp) if (total_pre_tp + total_pre_fp) > 0 else 0.0
    )
    overall_pre_r = (
        total_pre_tp / (total_pre_tp + total_pre_fn) if (total_pre_tp + total_pre_fn) > 0 else 0.0
    )
    overall_ffr = (
        total_post_fp / (total_post_fp + total_post_tp)
        if (total_post_fp + total_post_tp) > 0
        else 0.0
    )
    overall_agree = sum(all_agreements) / len(all_agreements) if all_agreements else 1.0
    overall_jacc = sum(all_jaccards) / len(all_jaccards) if all_jaccards else 0.0

    return {
        "summary": {
            "total_labels": len(gold_records),
            "total_submissions": len(submission_ids),
            "overall_post_verifier_precision": round(overall_post_p, 4),
            "overall_post_verifier_recall": round(overall_post_r, 4),
            "overall_pre_verifier_precision": round(overall_pre_p, 4),
            "overall_pre_verifier_recall": round(overall_pre_r, 4),
            "overall_post_verifier_ffr": round(overall_ffr, 4),
            "overall_consistency_agreement": round(overall_agree, 4),
            "overall_consistency_jaccard": round(overall_jacc, 4),
        },
        "capabilities": cap_groups,
    }
