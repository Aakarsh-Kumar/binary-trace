"""Skill Library page conforming to ARCHITECTURE.md §10.1 and US-11."""

from __future__ import annotations

from typing import Any

import streamlit as st

from compliance_review.db.repository import get_skill_execution_stats_for_capability
from compliance_review.skills.registry import registry

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


def render_skill_library() -> None:
    """Render Skill Library page."""
    if not registry._loaded:
        registry.load()

    all_skills = registry.list_all()
    n_skills = len(all_skills)
    capabilities_in_skills = sorted({s.capability for s in all_skills})
    n_capabilities = len(capabilities_in_skills)
    n_active = len([s for s in all_skills if s.eval_status == "active"])
    n_evaluating = len([s for s in all_skills if s.eval_status == "evaluating"])
    n_draft = len([s for s in all_skills if s.eval_status == "draft"])

    st.header("Skill Library")
    st.caption(
        f"{n_skills} skills across {n_capabilities} capabilities · "
        f"{n_active} active · {n_evaluating} evaluating · {n_draft} draft"
    )

    capabilities = ["citation-integrity", "report-structure", "code-quality", "rai-disclosure"]
    tabs = st.tabs(capabilities)

    for cap_tab, capability in zip(tabs, capabilities, strict=False):
        with cap_tab:
            st.subheader(capability)
            cap_skills = [s for s in all_skills if s.capability == capability]
            cap_skills.sort(key=lambda s: s.version)

            if not cap_skills:
                st.info("No versions found for this capability")
                continue

            for skill in cap_skills:
                expander_label = f"{skill.version} — {skill.eval_status} — {len(skill.checklist)} checks"
                with st.expander(expander_label):
                    st.markdown("#### Frontmatter")
                    frontmatter_data = [
                        {
                            "owner": skill.owner,
                            "created_at": str(skill.created_at),
                            "eval_status": skill.eval_status,
                            "inputs": ", ".join(skill.inputs),
                        }
                    ]
                    st.table(frontmatter_data)

                    st.markdown("#### Checklist")
                    checklist_rows: list[dict[str, Any]] = []
                    for item in skill.checklist:
                        req_text = item.evidence_requirement
                        req_display = req_text if len(req_text) <= 100 else req_text[:97] + "..."
                        checklist_rows.append(
                            {
                                "check_id": item.id,
                                "question": item.question,
                                "severity": item.severity,
                                "evidence_requirement": req_display,
                                "deterministic_only": item.deterministic_only,
                            }
                        )
                    st.table(checklist_rows)

                    with st.expander("Full evidence requirements"):
                        for item in skill.checklist:
                            st.markdown(f"**`{item.id}`**")
                            st.code(item.evidence_requirement, language="text")

                    if skill.deterministic_preconditions:
                        st.markdown("#### Preconditions")
                        for pre in skill.deterministic_preconditions:
                            st.markdown(f"- {pre}")

                    if skill.false_positive_guardrails:
                        st.markdown("#### False-Positive Guardrails")
                        for g in skill.false_positive_guardrails:
                            st.markdown(f"- {g}")

                    stats = get_skill_execution_stats_for_capability(capability, skill.version)
                    n_runs = stats.get("run_count", 0)
                    if n_runs > 0:
                        avg_ms = stats.get("avg_latency_ms", 0.0)
                        err_count = stats.get("schema_error_count", 0)
                        rate = err_count / n_runs if n_runs else 0.0
                        st.markdown("#### Execution Stats")
                        c1, c2, c3 = st.columns(3)
                        with c1:
                            st.metric("Executions", n_runs)
                        with c2:
                            st.metric("Avg latency", f"{avg_ms:.0f} ms")
                        with c3:
                            st.metric("Schema error rate", f"{rate:.1%}")


render_skill_library()
