"""Unit tests for FAISS vector index and version selector (US-14, US-15, US-16)."""

from pathlib import Path

import pytest

from compliance_review.errors import NoActiveSkillError
from compliance_review.retrieval.selector import select_skill_version
from compliance_review.retrieval.vector_index import (
    build_skills_index,
    load_skills_index,
    query_skills_index,
)


def test_build_and_query_skills_index(tmp_path: Path) -> None:
    """Verify FAISS vector index builds from skills/ and query returns scored matches."""
    index_path, count = build_skills_index(skills_root="skills", index_dir=tmp_path)
    assert index_path.is_file()
    assert count == 8

    index, meta = load_skills_index(tmp_path)
    assert index.ntotal == 8
    assert len(meta) == 8

    results = query_skills_index(
        query_text="Checking citation DOI validity and retractions",
        top_k=4,
        index_dir=tmp_path,
    )
    assert len(results) > 0
    top = results[0]
    assert "capability" in top
    assert "version" in top
    assert "score" in top
    assert 0.0 <= top["score"] <= 1.0


def test_selector_with_evaluating_status(tmp_path: Path) -> None:
    """Verify version selector finds v2 skills when skill_status='evaluating'."""
    build_skills_index(skills_root="skills", index_dir=tmp_path)

    selected, candidates = select_skill_version(
        capability="citation-integrity",
        query_text="DOI resolution and retractions",
        skill_status="evaluating",
        index_dir=tmp_path,
    )
    assert selected.capability == "citation-integrity"
    assert selected.version == "v2"
    assert "only_evaluating" in selected.reason or "highest_faiss_score" in selected.reason
    assert len(candidates) >= 1


def test_selector_no_active_skill_raises(tmp_path: Path) -> None:
    """Verify NoActiveSkillError is raised when requested status is missing (US-16)."""
    build_skills_index(skills_root="skills", index_dir=tmp_path)

    # In P1, no skills are active yet (v1 is draft, v2 is evaluating)
    with pytest.raises(NoActiveSkillError, match="No skill with status 'active'"):
        select_skill_version(
            capability="citation-integrity",
            query_text="DOI check",
            skill_status="active",
            index_dir=tmp_path,
        )
