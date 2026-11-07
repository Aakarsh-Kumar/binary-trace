"""Cached agreement computation conforming to ARCHITECTURE.md §10.4 and D-031."""

from typing import Any

import streamlit as st

from compliance_review.harness.k_run import compute_agreement


@st.cache_data(ttl=60)
def get_cached_agreement(runs_verdicts: list[list[dict[str, Any]]]) -> dict[str, dict[str, float]]:
    """Compute and cache per-check agreement across runs via harness/k_run.compute_agreement."""
    return compute_agreement(runs_verdicts)
