"""Streamlit dashboard entrypoint conforming to ARCHITECTURE.md §10."""

import streamlit as st

from compliance_review.config import Settings
from compliance_review.dashboard.queries import (
    cached_get_skill_executions_for_submission,
    cached_list_submissions,
)

st.set_page_config(layout="wide", page_title="Compliance Review")

# Sidebar: Submission Selector (D-030)
st.sidebar.title("Compliance Review")
st.sidebar.subheader("Submissions")

subs = cached_list_submissions(limit=100, offset=0)
ext_ids = [s["external_id"] for s in subs] if subs else []

if "selected_submission_external_id" not in st.session_state:
    st.session_state["selected_submission_external_id"] = ext_ids[0] if ext_ids else None

current_idx = 0
if ext_ids and st.session_state.get("selected_submission_external_id") in ext_ids:
    current_idx = ext_ids.index(st.session_state["selected_submission_external_id"])

selected_ext_id = st.sidebar.selectbox(
    "Select Submission",
    options=ext_ids,
    index=current_idx if ext_ids else 0,
    key="submission_selector",
)

if selected_ext_id and selected_ext_id != st.session_state.get("selected_submission_external_id"):
    st.session_state["selected_submission_external_id"] = selected_ext_id
    try:
        st.switch_page("pages/01_submission.py")
    except Exception:
        pass

# Sidebar: Model version + digest display
st.sidebar.divider()
st.sidebar.subheader("Model Telemetry")
settings = Settings()  # type: ignore[call-arg] # reason: pydantic-settings populates from env
model_name = settings.cr_ollama_model

latest_execs = (
    cached_get_skill_executions_for_submission(subs[0]["id"]) if subs else []
)
model_digest = str(latest_execs[0]["model_digest"]) if latest_execs else "359d7dd4bcdab3d8"

st.sidebar.caption(f"**Model:** `{model_name}`")
st.sidebar.caption(f"**Digest:** `{model_digest[:16]}...`")

st.title("Compliance Review Dashboard")
st.markdown("Select a submission from the sidebar or navigate to **Submission Review** page.")

if st.button("Open Submission Review"):
    try:
        st.switch_page("pages/01_submission.py")
    except Exception:
        pass

