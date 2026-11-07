"""Unit test verifying retrieval latency isolation in orchestrator (US-17, D-029).

FROZEN INVARIANT:
retrieval_events.latency_ms measures isolated capability gate + FAISS selection time only,
never model execution or full review latency.
"""

import time
from datetime import date
from typing import Any
from unittest.mock import patch

from compliance_review.harness.orchestrator import run_review
from compliance_review.skills.schema import ChecklistItem, SelectionEntry, SkillFrontmatter


def test_retrieval_latency_excludes_model_execution() -> None:
    """Verify that retrieval_events.latency_ms records only gate + FAISS selection time."""
    mock_submission = {
        "id": 42,
        "external_id": "test_mixed_sub",
        "source_path": "/fake/mixed/path",
        "submission_type": "mixed",
        "content_sha256": "abc123",
    }

    prose_body = "Report with 500 words. " * 60
    mock_extracted = {
        "text": f"{prose_body}\n\nReferences: 10.1234/test\n\nDisclosure: AI used",
        "word_count": 600,
        "references_present": True,
        "disclosure_present": True,
        "has_disclosure_file": True,
        "files": {"main.py": "print('hello')"},
        "loc": 1,
    }

    dummy_skill = SkillFrontmatter(
        capability="citation-integrity",
        version="v2",
        description="Test skill for latency isolation",
        inputs=["prose", "pdf"],
        eval_status="evaluating",
        owner="tester",
        created_at=date(2026, 11, 4),
        checklist=[
            ChecklistItem(
                id="item-1",
                question="Is test item valid?",
                severity="low",
                evidence_requirement="line:1",
                deterministic_only=True,
            )
        ],
    )

    mock_selected = SelectionEntry(
        capability="citation-integrity",
        version="v2",
        score=0.95,
        reason="top_ranked",
        stage="faiss",
    )
    mock_candidate = SelectionEntry(
        capability="citation-integrity",
        version="v2",
        score=0.95,
        reason="top_ranked",
        stage="faiss",
    )

    # Simulated slow model call taking 50ms per run
    def slow_model_execution(*args: Any, **kwargs: Any) -> tuple[Any, ...]:
        time.sleep(0.05)  # 50 ms delay
        return ([], "qwen3:4b", "digest123", "promptsha", "{}", "ok", 50)

    patch_get_sub = patch(
        "compliance_review.harness.orchestrator.get_submission_by_id",
        return_value=mock_submission,
    )
    patch_parse = patch(
        "compliance_review.harness.orchestrator.parse_submission_content",
        return_value=("hash", mock_extracted),
    )
    patch_select = patch(
        "compliance_review.harness.orchestrator.select_skill_version",
        return_value=(mock_selected, [mock_candidate]),
    )
    patch_skill = patch(
        "compliance_review.harness.orchestrator.load_skill",
        return_value=(dummy_skill, "body"),
    )
    patch_run = patch(
        "compliance_review.harness.orchestrator.run_single_capability_execution",
        side_effect=slow_model_execution,
    )
    patch_rec_run = patch("compliance_review.harness.orchestrator.record_skill_execution_run")
    patch_rec_ret = patch("compliance_review.harness.orchestrator.record_retrieval_event")

    with (
        patch_get_sub,
        patch_parse,
        patch_select,
        patch_skill,
        patch_run,
        patch_rec_run as mock_record_run,
        patch_rec_ret as mock_record_retrieval,
    ):
        # Run review with 4 capabilities and k=3 (total 12 runs * 50ms = 600ms model delay)
        run_review(submission_id=42, k=3)

        assert mock_record_retrieval.called
        kwargs = mock_record_retrieval.call_args.kwargs
        retrieval_latency = kwargs["latency_ms"]
        cap_set = kwargs["capability_set"]

        # 1. Assert all 4 capabilities were enabled in the test mixed submission
        assert len(cap_set) == 4
        assert all(v["enabled"] for v in cap_set.values())

        # 2. Assert retrieval_events.latency_ms is fast (< 500 ms target)
        assert retrieval_latency < 500, f"Retrieval latency {retrieval_latency}ms was >= 500ms"

        # 3. Assert model calls were executed (k=3 * 4 capabilities = 12 runs)
        assert mock_record_run.call_count == 12
        # retrieval_latency must not include the simulated 600ms model runtime
        msg = f"Retrieval latency {retrieval_latency}ms included model delay"
        assert retrieval_latency < 200, msg
