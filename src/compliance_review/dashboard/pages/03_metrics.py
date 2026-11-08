"""Metrics dashboard page conforming to ARCHITECTURE.md §10.3 and US-34."""

from __future__ import annotations

from datetime import datetime
import hashlib
import json
from pathlib import Path
from typing import Any

import streamlit as st

_orig_st_table = st.table


def _safe_st_table(data: Any, *args: Any, **kwargs: Any) -> Any:
    """Wrap st.table to provide markdown table fallback if pyarrow raises ImportError."""
    try:
        return _orig_st_table(data, *args, **kwargs)
    except Exception as exc:
        if "pyarrow" in str(exc).lower() or isinstance(exc, ImportError):
            if isinstance(data, list) and data and isinstance(data[0], dict):
                headers = list(data[0].keys())
                lines = [
                    "| " + " | ".join(headers) + " |",
                    "| " + " | ".join(["---"] * len(headers)) + " |",
                ]
                for row in data:
                    lines.append("| " + " | ".join(str(row.get(h, "")) for h in headers) + " |")
                return st.markdown("\n".join(lines))
        raise


st.table = _safe_st_table  # type: ignore[assignment]


def render_metrics_page() -> None:
    """Render Metrics page with 5 frozen sections."""
    eval_path = Path("data/labels/eval_v2.json")
    retrieval_path = Path("data/labels/retrieval_eval_v2.json")
    gold_path = Path("data/labels/gold_labels.csv")

    if not eval_path.exists():
        st.warning(
            "Evaluation metrics data not found. To regenerate, run:\n\n"
            "```\nuv run compliance-review metrics --labels data/labels/gold_labels.csv "
            "--out data/labels/eval_v2.json\n```"
        )
        return

    with open(eval_path, "r", encoding="utf-8") as f:
        eval_data: dict[str, Any] = json.load(f)

    retrieval_data: dict[str, Any] = {}
    if retrieval_path.exists():
        with open(retrieval_path, "r", encoding="utf-8") as f:
            retrieval_data = json.load(f)

    # 1. Header & Capability Filter
    st.header("Metrics")
    capabilities = ["all", "code-quality", "citation-integrity", "report-structure", "rai-disclosure"]
    selected = st.selectbox("Capability", capabilities)

    summary = eval_data.get("summary", {})
    cap_groups = eval_data.get("capabilities", {})

    if selected == "all":
        pre_p_val = summary.get("overall_pre_verifier_precision", 0.0)
        pre_r_val = summary.get("overall_pre_verifier_recall", 0.0)
        post_p_val = summary.get("overall_post_verifier_precision", 0.0)
        post_r_val = summary.get("overall_post_verifier_recall", 0.0)
        ffr_val = summary.get("overall_post_verifier_ffr", 0.0)

        pre_p_str = f"{pre_p_val:.4f}"
        pre_r_str = f"{pre_r_val:.4f}"
        post_p_str = f"{post_p_val:.4f}"
        post_r_str = f"{post_r_val:.4f}"
        ffr_str = f"{ffr_val:.4f}"
    else:
        cap_data = cap_groups.get(selected, {}).get("checks", {})
        pre_tp = sum(c["pre_confusion_matrix_2x2"]["tp"] for c in cap_data.values())
        pre_fp = sum(c["pre_confusion_matrix_2x2"]["fp"] for c in cap_data.values())
        pre_fn = sum(c["pre_confusion_matrix_2x2"]["fn"] for c in cap_data.values())
        post_tp = sum(c["post_confusion_matrix_2x2"]["tp"] for c in cap_data.values())
        post_fp = sum(c["post_confusion_matrix_2x2"]["fp"] for c in cap_data.values())
        post_fn = sum(c["post_confusion_matrix_2x2"]["fn"] for c in cap_data.values())

        pre_p_calc = pre_tp / (pre_tp + pre_fp) if (pre_tp + pre_fp) > 0 else 0.0
        pre_r_calc = pre_tp / (pre_tp + pre_fn) if (pre_tp + pre_fn) > 0 else 0.0
        post_p_calc = post_tp / (post_tp + post_fp) if (post_tp + post_fp) > 0 else 0.0
        post_r_calc = post_tp / (post_tp + post_fn) if (post_tp + post_fn) > 0 else 0.0
        ffr_calc = post_fp / (post_fp + post_tp) if (post_fp + post_tp) > 0 else 0.0

        pre_p_str = f"{pre_p_calc:.4f}"
        pre_r_str = f"{pre_r_calc:.4f}"
        post_p_str = f"{post_p_calc:.4f}"
        post_r_str = f"{post_r_calc:.4f}"
        ffr_str = f"{ffr_calc:.4f}"

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.metric("pre_verifier_precision", pre_p_str)
    with c2:
        st.metric("pre_verifier_recall", pre_r_str)
    with c3:
        st.metric("post_verifier_precision", post_p_str)
    with c4:
        st.metric("post_verifier_recall", post_r_str)
    with c5:
        st.metric("FFR", ffr_str)

    # 2. Pre vs Post Verifier Comparison (frozen view — D-020)
    st.subheader("Pre vs Post Verifier")
    compare_rows: list[dict[str, Any]] = []

    active_caps = (
        ["code-quality", "citation-integrity", "report-structure", "rai-disclosure"]
        if selected == "all"
        else [selected]
    )

    for cap in active_caps:
        c_checks = cap_groups.get(cap, {}).get("checks", {})
        pre_tp = sum(c["pre_confusion_matrix_2x2"]["tp"] for c in c_checks.values())
        pre_fp = sum(c["pre_confusion_matrix_2x2"]["fp"] for c in c_checks.values())
        pre_fn = sum(c["pre_confusion_matrix_2x2"]["fn"] for c in c_checks.values())
        post_tp = sum(c["post_confusion_matrix_2x2"]["tp"] for c in c_checks.values())
        post_fp = sum(c["post_confusion_matrix_2x2"]["fp"] for c in c_checks.values())
        post_fn = sum(c["post_confusion_matrix_2x2"]["fn"] for c in c_checks.values())

        p_pre = pre_tp / (pre_tp + pre_fp) if (pre_tp + pre_fp) > 0 else 0.0
        p_post = post_tp / (post_tp + post_fp) if (post_tp + post_fp) > 0 else 0.0
        delta_p = p_post - p_pre
        r_pre = pre_tp / (pre_tp + pre_fn) if (pre_tp + pre_fn) > 0 else 0.0
        r_post = post_tp / (post_tp + post_fn) if (post_tp + post_fn) > 0 else 0.0
        delta_r = r_post - r_pre

        compare_rows.append(
            {
                "capability": cap,
                "pre_P": f"{p_pre:.4f}",
                "post_P": f"{p_post:.4f}",
                "ΔP": f"{delta_p:+.4f}",
                "pre_R": f"{r_pre:.4f}",
                "post_R": f"{r_post:.4f}",
                "ΔR": f"{delta_r:+.4f}",
            }
        )
    st.table(compare_rows)

    # 3. Checklist Performance Table
    st.subheader("Per-Check Performance")
    check_rows: list[dict[str, Any]] = []
    for cap in active_caps:
        c_checks = cap_groups.get(cap, {}).get("checks", {})
        for check_id, c_data in c_checks.items():
            pre_p = c_data["pre_verifier_precision"]
            post_p = c_data["post_verifier_precision"]
            pre_r = c_data["pre_verifier_recall"]
            post_r = c_data["post_verifier_recall"]
            post_ffr = c_data["post_verifier_ffr"]
            agree = c_data["consistency_agreement"]

            check_rows.append(
                {
                    "check_id": check_id,
                    "N_gold_flags": c_data["gold_flags"],
                    "pre_P": str(pre_p),
                    "post_P": str(post_p),
                    "pre_R": str(pre_r),
                    "post_R": str(post_r),
                    "post_FFR": str(post_ffr),
                    "agreement": f"{agree:.4f}" if isinstance(agree, (int, float)) else str(agree),
                }
            )
    st.table(check_rows)

    # 4. Confusion Matrices
    st.subheader("Confusion Matrices")
    for cap in active_caps:
        c_checks = cap_groups.get(cap, {}).get("checks", {})
        for check_id, c_data in c_checks.items():
            n_gold = c_data["gold_flags"]
            if n_gold >= 10:
                cm = c_data["post_confusion_matrix_2x2"]
                st.markdown(f"**`{check_id}`**")
                st.table(
                    [
                        {"": "Gold flag", "Pred flag": cm["tp"], "Pred no-flag": cm["fn"]},
                        {"": "Gold no-flag", "Pred flag": cm["fp"], "Pred no-flag": cm["tn"]},
                    ]
                )
            else:
                st.caption(f"{check_id}: insufficient_sample (N_gold={n_gold} < 10)")

    # 5. Retrieval & System Telemetry
    st.subheader("Retrieval & Telemetry")
    ret_summary = retrieval_data.get("summary", {})
    ret_rows = [
        {
            "capability_recall": ret_summary.get("capability_recall", "N/A"),
            "version_precision@1": ret_summary.get("version_precision@1", "N/A"),
            "over_retrieval": ret_summary.get("over_retrieval_rate", "N/A"),
            "HSR@K": ret_summary.get("HSR@K", "N/A"),
            "latency_p50_ms": ret_summary.get("latency_p50_ms", "N/A"),
            "latency_p99_ms": ret_summary.get("latency_p99_ms", "N/A"),
        }
    ]
    st.table(ret_rows)

    sha = ""
    if gold_path.exists():
        sha = hashlib.sha256(gold_path.read_bytes()).hexdigest()
    mtime = eval_path.stat().st_mtime
    eval_date = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")
    st.caption(f"Evaluated {eval_date} · gold_labels.csv SHA-256 {sha[:12]}")


render_metrics_page()
