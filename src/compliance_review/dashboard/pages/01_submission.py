"""Submission Review Streamlit page conforming to ARCHITECTURE.md §10.2 (seven frozen sections)."""

import json
from pathlib import Path
from typing import Any

import streamlit as st

import compliance_review
from compliance_review.config import Settings
from compliance_review.dashboard.agreement import get_cached_agreement
from compliance_review.dashboard.queries import (
    cached_get_evidence_verifications_for_verdict,
    cached_get_retrieval_event_for_submission,
    cached_get_reviewer_feedback_for_submission,
    cached_get_skill_executions_for_submission,
    cached_get_submission_by_external_id,
    cached_get_verdicts_for_execution,
    cached_get_verdicts_for_submission,
    cached_list_submissions,
)
from compliance_review.db.repository import record_reviewer_feedback
from compliance_review.skills.loader import load_all_skills

SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}
REASON_CODES = [
    "evidence_insufficient",
    "check_not_applicable",
    "model_misread",
    "policy_exception",
    "severity_mismatch",
    "other",
]


@st.cache_data(ttl=300)
def get_check_questions_map() -> dict[tuple[str, str], str]:
    """Cache mapping from (capability, check_id) to checklist item question."""
    skills = load_all_skills("skills")
    q_map: dict[tuple[str, str], str] = {}
    for (cap, _), sf in skills.items():
        for item in sf.checklist:
            q_map[(cap, item.id)] = item.question
    return q_map


def extract_context_lines(source_path_str: str, location: str | None, window: int = 5) -> str:
    """Extract context lines around an evidence location for click-through viewer."""
    if not location:
        return "(no location specified)"
    try:
        source_path = Path(source_path_str)
        target_file: Path | None = None
        target_line: int | None = None

        # Parse line number if present
        loc_str = location.strip()
        if ":" in loc_str:
            parts = loc_str.split(":")
            if parts[-1].isdigit():
                target_line = int(parts[-1])
            if len(parts) >= 2 and parts[0] not in ("line", "lines", "page"):
                cand_file = source_path / parts[0] if source_path.is_dir() else source_path
                if cand_file.exists():
                    target_file = cand_file

        if target_file is None:
            if source_path.is_file():
                target_file = source_path
            elif source_path.is_dir():
                cand_md = list(source_path.glob("*.md"))
                cand_py = list(source_path.glob("*.py"))
                target_file = cand_md[0] if cand_md else (cand_py[0] if cand_py else None)

        if not target_file or not target_file.exists():
            return f"(source file {target_file} not found for location {location})"

        lines = target_file.read_text(encoding="utf-8", errors="replace").splitlines()
        if not lines:
            return "(source file is empty)"

        if target_line is None:
            # Show first 15 lines if no line number was parsed
            snippet = lines[:15]
            return "\n".join(f"{i + 1:4d} | {line}" for i, line in enumerate(snippet))

        start = max(0, target_line - window - 1)
        end = min(len(lines), target_line + window)
        result_lines = []
        for i in range(start, end):
            prefix = "-> " if i + 1 == target_line else "   "
            result_lines.append(f"{prefix}{i + 1:4d} | {lines[i]}")
        return "\n".join(result_lines)
    except Exception as exc:
        return f"(unable to load context: {exc})"


# ────────────────────────────────────────────────────────────────────────
# SECTION 1 — HEADER
# ────────────────────────────────────────────────────────────────────────
def render_header(submission: dict[str, Any] | None) -> None:
    """Section 1: Submission Header."""
    st.header("1. Submission Header")
    if submission is None:
        st.info("*No submission selected*")
        return

    col1, col2, col3 = st.columns(3)
    col1.metric("External ID", submission["external_id"])
    col2.metric("Type", submission["submission_type"].capitalize())
    ingested = submission.get("ingested_at")
    ingested_str = (
        ingested.isoformat()
        if ingested is not None and hasattr(ingested, "isoformat")
        else str(ingested)
    )
    col3.metric("Ingested At (UTC)", ingested_str)


# ────────────────────────────────────────────────────────────────────────
# SECTION 2 — RETRIEVAL TRACE
# ────────────────────────────────────────────────────────────────────────
def render_retrieval_trace(retrieval_event: dict[str, Any] | None) -> None:
    """Section 2: Retrieval Trace."""
    st.subheader("2. Retrieval Trace")
    if retrieval_event is None:
        st.info("*No retrieval trace recorded for this submission*")
        return

    cap_set_raw = retrieval_event.get("capability_set", {})
    cap_set = json.loads(cap_set_raw) if isinstance(cap_set_raw, str) else cap_set_raw
    selected_raw = retrieval_event.get("selected", [])
    selected = json.loads(selected_raw) if isinstance(selected_raw, str) else selected_raw
    latency_ms = retrieval_event.get("latency_ms", 0)

    st.markdown(f"**Retrieval Latency:** `{latency_ms} ms` (FAISS version index query)")

    st.markdown("##### Capability Gates")
    if not cap_set:
        st.info("*No capability gate data recorded*")
    else:
        chip_cols = st.columns(len(cap_set))
        for idx, (cap, info) in enumerate(sorted(cap_set.items())):
            enabled = info.get("enabled", False) if isinstance(info, dict) else bool(info)
            reason = info.get("reason", "") if isinstance(info, dict) else ""
            with chip_cols[idx]:
                if enabled:
                    st.success(f"🟢 **{cap}**\n\n*enabled*")
                else:
                    st.caption(f"⚪ **{cap}**\n\n*disabled* ({reason})")

    st.markdown("##### Selected Skill Versions")
    if not selected:
        st.info("*No skills selected*")
    else:
        sel_display = []
        for s in selected:
            sel_display.append(
                {
                    "Capability": s.get("capability", ""),
                    "Version": s.get("version", ""),
                    "Stage": s.get("stage", ""),
                    "Reason": s.get("reason", ""),
                    "FAISS Score": f"{s.get('score', 0.0):.4f}",
                }
            )
        st.dataframe(sel_display, use_container_width=True, hide_index=True)


# ────────────────────────────────────────────────────────────────────────
# SECTION 3 — FINDINGS
# ────────────────────────────────────────────────────────────────────────
def render_findings(
    findings: list[dict[str, Any]],
    submission: dict[str, Any] | None = None,
    existing_feedback: list[dict[str, Any]] | None = None,
) -> None:
    """Section 3: Findings (verdict == 'flag' AND verified == True)."""
    st.subheader("3. Findings")
    if not findings:
        st.markdown("*No findings — all checks passed or unsupported*")
        return

    q_map = get_check_questions_map()
    sub_id = submission["id"] if submission else 0
    source_path_str = submission.get("source_path", "") if submission else ""

    feedback_by_verdict: dict[int, dict[str, Any]] = {}
    if existing_feedback:
        for fb_row in existing_feedback:
            row_v_id = fb_row.get("verdict_id")
            if row_v_id is not None and row_v_id not in feedback_by_verdict:
                feedback_by_verdict[row_v_id] = fb_row

    # Group findings by capability
    by_cap: dict[str, list[dict[str, Any]]] = {}
    for f in findings:
        cap = f.get("skill_capability", "unknown")
        by_cap.setdefault(cap, []).append(f)

    # Sort severity desc then check_id asc
    for cap in sorted(by_cap.keys()):
        cap_findings = by_cap[cap]
        cap_findings.sort(
            key=lambda x: (
                SEVERITY_ORDER.get(str(x.get("severity", "low")).lower(), 99),
                str(x.get("check_id", "")),
            )
        )
        st.markdown(f"#### Capability: `{cap}` ({len(cap_findings)} findings)")

        for f in cap_findings:
            v_id = f["id"]
            check_id = f.get("check_id", "")
            severity = str(f.get("severity", "low")).lower()
            confidence = f.get("confidence")
            evidence_text = f.get("evidence_text", "")
            evidence_location = f.get("evidence_location", "")
            question = q_map.get((cap, check_id), f"Verification check: {check_id}")

            badge_icon = {
                "critical": "🔴 CRITICAL",
                "high": "🟠 HIGH",
                "medium": "🟡 MEDIUM",
                "low": "🔵 LOW",
            }.get(severity, "⚪ " + severity.upper())

            with st.container(border=True):
                top_col1, top_col2 = st.columns([4, 1])
                top_col1.markdown(f"**{question}** (`{check_id}`)")
                top_col2.markdown(f"**{badge_icon}**")

                if confidence is not None:
                    st.caption(f"**Model Confidence:** {float(confidence):.2f}")

                st.markdown("**Evidence Quote:**")
                st.code(evidence_text if evidence_text else "(empty evidence text)")

                # Click-through location viewer (±5 lines around)
                with st.expander(f"📍 Location Context: `{evidence_location}`", expanded=False):
                    context = extract_context_lines(source_path_str, evidence_location, window=5)
                    st.code(context, language="python" if ".py" in source_path_str else "markdown")

                # Action buttons (Approve / Override / Request re-run)
                recorded_fb = feedback_by_verdict.get(v_id)
                if recorded_fb:
                    st.success(
                        f"Action recorded: **{recorded_fb['action'].upper()}** by `{recorded_fb['reviewer_id']}` "
                        + (f"({recorded_fb['reason_code']})" if recorded_fb.get("reason_code") else "")
                    )
                else:
                    btn_c1, btn_c2, btn_c3 = st.columns([1, 2, 1])

                    with btn_c1:
                        if st.button("Approve", key=f"app_{v_id}"):
                            record_reviewer_feedback(
                                submission_id=sub_id,
                                verdict_id=v_id,
                                reviewer_id="reviewer:dashboard",
                                action="approve",
                            )
                            st.rerun()

                    with btn_c2:
                        override_reason = st.selectbox(
                            "Override Reason",
                            options=REASON_CODES,
                            key=f"reason_{v_id}",
                            label_visibility="collapsed",
                        )
                        if st.button("Override", key=f"over_{v_id}"):
                            record_reviewer_feedback(
                                submission_id=sub_id,
                                verdict_id=v_id,
                                reviewer_id="reviewer:dashboard",
                                action="override",
                                reason_code=override_reason,
                            )
                            st.rerun()

                    with btn_c3:
                        if st.button("Request Re-run", key=f"rerun_{v_id}"):
                            record_reviewer_feedback(
                                submission_id=sub_id,
                                verdict_id=v_id,
                                reviewer_id="reviewer:dashboard",
                                action="request_rerun",
                            )
                            st.rerun()


# ────────────────────────────────────────────────────────────────────────
# SECTION 4 — DISAGREEMENT VIEW
# ────────────────────────────────────────────────────────────────────────
def render_disagreement(
    disagreements: list[dict[str, Any]],
    runs_by_cap: dict[str, list[list[dict[str, Any]]]],
) -> None:
    """Section 4: Disagreement view across k runs (agreement < 0.85)."""
    st.subheader("4. Disagreement View")
    if not disagreements:
        st.markdown("*No disagreement — all checks meet stability threshold (≥ 0.85)*")
        return

    for item in disagreements:
        cap = item["capability"]
        check_id = item["check_id"]
        agreement_val = item["agreement"]

        ag_msg = (
            f"⚠️ Requires adjudication — agreement on `{check_id}`: "
            f"**{agreement_val:.2f}** (< 0.85)"
        )
        st.warning(ag_msg)

        cap_runs = runs_by_cap.get(cap, [])
        num_runs = len(cap_runs)
        if num_runs > 0:
            cols = st.columns(num_runs)
            for r_idx, run_verdicts in enumerate(cap_runs):
                if isinstance(run_verdicts, dict) and "verdicts" in run_verdicts:
                    v_items = run_verdicts["verdicts"]
                elif isinstance(run_verdicts, list):
                    v_items = run_verdicts
                else:
                    v_items = []
                matching = [
                    v for v in v_items if isinstance(v, dict) and v.get("check_id") == check_id
                ]
                with cols[r_idx]:
                    st.markdown(f"**Run {r_idx + 1}**")
                    if matching:
                        m = matching[0]
                        verd = m.get("verdict", "unknown")
                        conf = m.get("confidence")
                        ev = m.get("evidence_text", "")
                        conf_str = f" (conf: {float(conf):.2f})" if conf else ""
                        st.caption(f"Verdict: **{verd}**{conf_str}")
                        if ev:
                            st.code(ev[:150] + ("..." if len(ev) > 150 else ""))
                    else:
                        st.caption("*(not executed)*")


# ────────────────────────────────────────────────────────────────────────
# SECTION 5 — PASSED CHECKS
# ────────────────────────────────────────────────────────────────────────
def render_passed_checks(passed: list[dict[str, Any]]) -> None:
    """Section 5: Passed checks (collapsed expander)."""
    with st.expander(f"5. Passed Checks ({len(passed)})", expanded=False):
        if not passed:
            st.markdown("*No passed checks*")
            return

        # Display one line per check: check_id, severity, confidence
        md_lines = [
            "| Capability | Check ID | Verdict | Severity | Confidence |",
            "| :--- | :--- | :--- | :--- | :--- |",
        ]
        for p in passed:
            conf = p.get("confidence")
            conf_str = f"{float(conf):.2f}" if conf is not None else "N/A"
            cap = p.get("skill_capability", "")
            chk = p.get("check_id", "")
            verd = p.get("verdict", "pass")
            sev = p.get("severity", "")
            md_lines.append(f"| `{cap}` | `{chk}` | {verd} | {sev} | {conf_str} |")
        st.markdown("\n".join(md_lines))


# ────────────────────────────────────────────────────────────────────────
# SECTION 6 — UNSUPPORTED
# ────────────────────────────────────────────────────────────────────────
def render_unsupported(unsupported: list[dict[str, Any]]) -> None:
    """Section 6: Unsupported evidence (collapsed expander)."""
    header_text = f"6. Unsupported Evidence ({len(unsupported)}) — not surfaced as findings"
    with st.expander(header_text, expanded=False):
        if not unsupported:
            st.markdown("*No unsupported evidence records*")
            return

        for u in unsupported:
            check_id = u.get("check_id", "")
            cap = u.get("skill_capability", "")
            reason = u.get("failure_reason", "not_located")
            ev_text = u.get("evidence_text", "")
            ev_loc = u.get("evidence_location", "")

            with st.container(border=True):
                st.markdown(f"**`{cap}` / `{check_id}`** — Reason: *{reason}*")
                st.caption(f"Location claimed: `{ev_loc}`")
                st.code(ev_text if ev_text else "(empty text)")


# ────────────────────────────────────────────────────────────────────────
# SECTION 7 — AUDIT FOOTER
# ────────────────────────────────────────────────────────────────────────
def render_audit_footer(audit_info: dict[str, Any]) -> None:
    """Section 7: Audit footer with model telemetry and hashes."""
    st.divider()
    st.subheader("7. Audit Footer")
    model_name = audit_info.get("model_name", "qwen3:4b")
    model_digest = audit_info.get("model_digest", "unknown")
    skill_versions = audit_info.get("skill_versions", {})
    prompt_hashes = audit_info.get("prompt_hashes", {})
    harness_ver = audit_info.get("harness_version", compliance_review.__version__)

    if skill_versions:
        ver_summary = ", ".join(f"{c}:{v}" for c, v in skill_versions.items())
    else:
        ver_summary = "none"

    if prompt_hashes:
        prompt_summary = ", ".join(f"{c}:{h[:8]}..." for c, h in prompt_hashes.items())
    else:
        prompt_summary = "none"

    footer_text = (
        f"**Model:** `{model_name}` | **Digest:** `{model_digest[:16]}...` | "
        f"**Harness:** `compliance-review v{harness_ver}`\n\n"
        f"**Skill Versions:** {ver_summary}\n\n"
        f"**Prompt Hashes:** {prompt_summary}"
    )
    st.caption(footer_text)


# ────────────────────────────────────────────────────────────────────────
# MAIN PAGE RENDERER
# ────────────────────────────────────────────────────────────────────────
def render_submission_page(external_id: str | None = None) -> None:
    """Render full Submission Review page with all seven frozen sections."""
    if external_id is None:
        external_id = st.session_state.get("selected_submission_external_id")

    if not external_id:
        subs = cached_list_submissions(limit=1, offset=0)
        if subs:
            external_id = subs[0]["external_id"]
            st.session_state["selected_submission_external_id"] = external_id

    submission = cached_get_submission_by_external_id(external_id) if external_id else None
    if not submission:
        render_header(None)
        render_retrieval_trace(None)
        render_findings([], None)
        render_disagreement([], {})
        render_passed_checks([])
        render_unsupported([])
        render_audit_footer({})
        return

    sub_id = submission["id"]

    # Load data via D-030 read-only helpers
    retrieval_event = cached_get_retrieval_event_for_submission(sub_id)
    executions = cached_get_skill_executions_for_submission(sub_id)
    all_verdicts = cached_get_verdicts_for_submission(sub_id)
    existing_feedback = cached_get_reviewer_feedback_for_submission(sub_id)

    # 1. Header
    render_header(submission)

    # 2. Retrieval Trace
    render_retrieval_trace(retrieval_event)

    # 3. Findings (verdict == 'flag' AND verified == True)
    verified_findings: list[dict[str, Any]] = []
    seen_checks: set[str] = set()

    for v in all_verdicts:
        if v.get("verdict") == "flag":
            v_id = v["id"]
            c_id = v.get("check_id", "")
            if c_id in seen_checks:
                continue
            evs = cached_get_evidence_verifications_for_verdict(v_id)
            if any(ev.get("verified") is True for ev in evs):
                verified_findings.append(v)
                seen_checks.add(c_id)

    render_findings(verified_findings, submission, existing_feedback)

    # 4. Disagreement View via D-031
    runs_by_cap: dict[str, list[list[dict[str, Any]]]] = {}
    disagreements: list[dict[str, Any]] = []

    # Group executions by capability and load runs
    caps_in_exec = sorted(list({e["skill_capability"] for e in executions}))
    settings = Settings()  # type: ignore[call-arg]
    stability_thresh = settings.cr_stability_threshold

    for cap in caps_in_exec:
        cap_execs = [e for e in executions if e["skill_capability"] == cap]
        cap_execs.sort(key=lambda x: x["run_index"])
        runs: list[list[dict[str, Any]]] = []
        for ex in cap_execs:
            v_list = cached_get_verdicts_for_execution(ex["id"])
            runs.append(v_list)
        runs_by_cap[cap] = runs

        # D-031 cached agreement call
        agreement_metrics = get_cached_agreement(runs)
        for chk_id, metrics in agreement_metrics.items():
            ag_val = metrics.get("agreement", 1.0)
            if ag_val < stability_thresh:
                disagreements.append(
                    {
                        "capability": cap,
                        "check_id": chk_id,
                        "agreement": ag_val,
                    }
                )

    render_disagreement(disagreements, runs_by_cap)

    # 5. Passed Checks
    passed_verdicts: list[dict[str, Any]] = []
    seen_passed: set[str] = set()
    for v in all_verdicts:
        if v.get("verdict") in ("pass", "not_applicable"):
            c_id = v.get("check_id", "")
            if c_id not in seen_passed:
                passed_verdicts.append(v)
                seen_passed.add(c_id)

    render_passed_checks(passed_verdicts)

    # 6. Unsupported
    unsupported_verdicts: list[dict[str, Any]] = []
    seen_unsupp: set[str] = set()
    for v in all_verdicts:
        if v.get("verdict") == "unsupported_evidence":
            c_id = v.get("check_id", "")
            if c_id not in seen_unsupp:
                v_id = v["id"]
                evs = cached_get_evidence_verifications_for_verdict(v_id)
                fail_reason = evs[0].get("failure_reason", "not_located") if evs else "not_located"
                item = dict(v)
                item["failure_reason"] = fail_reason
                unsupported_verdicts.append(item)
                seen_unsupp.add(c_id)

    render_unsupported(unsupported_verdicts)

    # 7. Audit Footer
    skill_versions = {}
    prompt_hashes = {}
    model_name = "qwen3:4b"
    model_digest = "unknown"
    for e in executions:
        cap = e["skill_capability"]
        skill_versions[cap] = e["skill_version"]
        prompt_hashes[cap] = e["prompt_sha256"]
        model_name = e["model_name"]
        model_digest = e["model_digest"]

    audit_info = {
        "model_name": model_name,
        "model_digest": model_digest,
        "skill_versions": skill_versions,
        "prompt_hashes": prompt_hashes,
        "harness_version": compliance_review.__version__,
    }
    render_audit_footer(audit_info)


if __name__ == "__main__":
    render_submission_page()
