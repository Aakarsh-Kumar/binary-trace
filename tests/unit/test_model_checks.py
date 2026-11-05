"""Unit tests for model-based checks across four capabilities (US-20)."""

from unittest.mock import patch

from compliance_review.checks.model_based.citation import evaluate_citation_model_checks
from compliance_review.checks.model_based.code import evaluate_code_model_checks
from compliance_review.checks.model_based.disclosure import evaluate_disclosure_model_checks
from compliance_review.checks.model_based.structure import evaluate_structure_model_checks
from compliance_review.skills.schema import ModelOutput, ModelVerdict


def test_empty_model_items_returns_early() -> None:
    """Verify checks with only deterministic items return immediately without model call."""
    checklist = [{"id": "det-1", "question": "q", "severity": "low", "deterministic_only": True}]
    status, verdicts, digest, lat, raw = evaluate_citation_model_checks(
        checklist, {"text": "Hello"}
    )
    assert status == "ok"
    assert verdicts == []


def test_evaluate_citation_model_checks() -> None:
    """Verify citation check invokes model with prompt and parses verdicts."""
    checklist = [
        {
            "id": "cite-claim-supported",
            "question": "Is claim supported?",
            "severity": "high",
            "evidence_requirement": "page:1",
            "deterministic_only": False,
        }
    ]
    mock_output = ModelOutput(
        capability="citation-integrity",
        verdicts=[
            ModelVerdict(
                check_id="cite-claim-supported",
                verdict="flag",
                severity="high",
                evidence_text="Claim without citation",
                evidence_location="page:1",
                confidence=0.9,
            )
        ],
    )

    with patch(
        "compliance_review.checks.model_based.citation.execute_model_evaluation_with_retry",
        return_value=("ok", mock_output, "test_digest", 120, "{}"),
    ):
        status, verdicts, digest, lat, raw = evaluate_citation_model_checks(
            checklist, {"text": "Claim without citation"}, version="v2"
        )
        assert status == "ok"
        assert len(verdicts) == 1
        assert verdicts[0]["check_id"] == "cite-claim-supported"
        assert verdicts[0]["verdict"] == "flag"


def test_evaluate_structure_code_disclosure_checks() -> None:
    """Verify structure, code, and disclosure model check execution."""
    struct_item = [
        {
            "id": "struct-semantic-coherence",
            "question": "q",
            "severity": "medium",
            "evidence_requirement": "section:methods",
            "deterministic_only": False,
        }
    ]
    code_item = [
        {
            "id": "code-error-handling",
            "question": "q",
            "severity": "medium",
            "evidence_requirement": "file:P:L",
            "deterministic_only": False,
        }
    ]
    disc_item = [
        {
            "id": "rai-sufficiency-judgment",
            "question": "q",
            "severity": "high",
            "evidence_requirement": "section:disclosure",
            "deterministic_only": False,
        }
    ]

    dummy_output = ModelOutput(capability="report-structure", verdicts=[])
    with patch(
        "compliance_review.checks.model_based.structure.execute_model_evaluation_with_retry",
        return_value=("ok", dummy_output, "d", 50, "{}"),
    ):
        st, v_struct, d, lat_s, raw_s = evaluate_structure_model_checks(
            struct_item, {"text": "Intro"}
        )
        assert st == "ok"

    code_output = ModelOutput(capability="code-quality", verdicts=[])
    with patch(
        "compliance_review.checks.model_based.code.execute_model_evaluation_with_retry",
        return_value=("ok", code_output, "d", 50, "{}"),
    ):
        st, v_code, d, lat_c, raw_c = evaluate_code_model_checks(
            code_item, {"files": {"main.py": "pass"}}
        )
        assert st == "ok"

    disc_output = ModelOutput(capability="rai-disclosure", verdicts=[])
    with patch(
        "compliance_review.checks.model_based.disclosure.execute_model_evaluation_with_retry",
        return_value=("ok", disc_output, "d", 50, "{}"),
    ):
        st, v_disc, d, lat_d, raw_d = evaluate_disclosure_model_checks(
            disc_item, {"text": "AI was used"}
        )
        assert st == "ok"
