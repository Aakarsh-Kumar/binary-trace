"""Skill version selector conforming to ARCHITECTURE.md §6.3 and §6.4."""

from pathlib import Path
from typing import Any, cast

from compliance_review.errors import NoActiveSkillError
from compliance_review.retrieval.vector_index import query_skills_index
from compliance_review.skills.schema import Capability, SelectionEntry

MIN_CANDIDATE_SCORE = 0.30


def select_skill_version(
    capability: str,
    query_text: str,
    skill_status: str = "active",
    min_candidate_score: float = MIN_CANDIDATE_SCORE,
    index_dir: Path | str = "data/vector_index",
) -> tuple[SelectionEntry, list[SelectionEntry]]:
    """Select the appropriate skill version for an enabled capability using FAISS retrieval."""
    results = query_skills_index(query_text=query_text, top_k=20, index_dir=index_dir)

    # Filter to versions matching the specific capability
    cap_results: list[dict[str, Any]] = [r for r in results if r["capability"] == capability]

    # Candidates above min_candidate_score (ARCHITECTURE.md §6.4)
    candidate_entries: list[SelectionEntry] = []
    for r in cap_results:
        if r["score"] >= min_candidate_score:
            candidate_entries.append(
                SelectionEntry(
                    capability=cast(Capability, r["capability"]),
                    version=r["version"],
                    reason=f"faiss_candidate_status_{r['eval_status']}",
                    score=round(float(r["score"]), 4),
                    stage="faiss",
                )
            )

    # Filter to requested status (default 'active'; in P1 can be 'evaluating' or 'draft' or 'all')
    matching: list[dict[str, Any]] = []
    for r in cap_results:
        if skill_status == "all" or r["eval_status"] == skill_status:
            matching.append(r)

    if not matching:
        raise NoActiveSkillError(
            f"No skill with status '{skill_status}' found for capability '{capability}'"
        )

    # Sort matching by FAISS similarity score descending
    matching.sort(key=lambda x: float(x["score"]), reverse=True)

    if len(matching) == 1:
        chosen = matching[0]
        reason = "only_active" if skill_status == "active" else f"only_{skill_status}"
    else:
        chosen = matching[0]
        reason = "highest_faiss_score"

    selected_entry = SelectionEntry(
        capability=cast(Capability, chosen["capability"]),
        version=chosen["version"],
        reason=reason,
        score=round(float(chosen["score"]), 4),
        stage="faiss",
    )

    return selected_entry, candidate_entries
