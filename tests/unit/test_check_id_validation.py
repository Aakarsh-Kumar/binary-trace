"""Unit tests for check_id validation against canonical checklist (D-045)."""

import json
from unittest.mock import patch

import pytest

from compliance_review.errors import ModelSchemaError
from compliance_review.model.schema_validation import (
    execute_model_evaluation_with_retry,
    validate_model_output,
)


def test_valid_check_ids_pass() -> None:
    """Verify that output with only canonical check IDs passes validation."""
    canonical = {"cite-claim-supported", "cite-context-accurate"}
    payload = {
        "capability": "citation-integrity",
        "verdicts": [
            {
                "check_id": "cite-claim-supported",
                "verdict": "pass",
                "severity": "high",
                "evidence_text": None,
                "evidence_location": None,
                "confidence": 0.95,
            },
            {
                "check_id": "cite-context-accurate",
                "verdict": "pass",
                "severity": "medium",
                "evidence_text": None,
                "evidence_location": None,
                "confidence": 0.90,
            },
        ],
    }
    output = validate_model_output(
        json.dumps(payload),
        canonical_check_ids=canonical,
        expected_capability="citation-integrity",
    )
    assert output.capability == "citation-integrity"
    assert len(output.verdicts) == 2
    assert {v.check_id for v in output.verdicts} == canonical


def test_hallucinated_check_id_rejected() -> None:
    """Verify that hallucinated check_id is rejected with informative error message."""
    canonical = {"cite-claim-supported", "cite-context-accurate"}
    payload = {
        "capability": "citation-integrity",
        "verdicts": [
            {
                "check_id": "cite-using-numeric-notation",
                "verdict": "pass",
                "severity": "high",
                "evidence_text": None,
                "evidence_location": None,
                "confidence": 0.95,
            }
        ],
    }
    with pytest.raises(ModelSchemaError) as exc_info:
        validate_model_output(
            json.dumps(payload),
            canonical_check_ids=canonical,
            expected_capability="citation-integrity",
        )
    err = str(exc_info.value)
    assert "Hallucinated check_id: 'cite-using-numeric-notation'" in err
    assert "['cite-claim-supported', 'cite-context-accurate']" in err


def test_retry_on_hallucination() -> None:
    """Verify mock returning phantom check ID triggers retry and succeeds on valid attempt."""
    canonical = {"cite-claim-supported", "cite-context-accurate"}
    phantom_payload = {
        "capability": "citation-integrity",
        "verdicts": [
            {
                "check_id": "cite-using-numeric-notation",
                "verdict": "pass",
                "severity": "high",
                "evidence_text": None,
                "evidence_location": None,
                "confidence": 0.95,
            }
        ],
    }
    valid_payload = {
        "capability": "citation-integrity",
        "verdicts": [
            {
                "check_id": "cite-claim-supported",
                "verdict": "pass",
                "severity": "high",
                "evidence_text": None,
                "evidence_location": None,
                "confidence": 0.95,
            }
        ],
    }

    mock_responses = [
        (json.dumps(phantom_payload), "digest1", 40),
        (json.dumps(valid_payload), "digest2", 50),
    ]

    target_fn = "compliance_review.model.schema_validation.call_qwen"
    with patch(target_fn, side_effect=mock_responses) as mock_call:
        status, output, digest, total_latency, raw_output = execute_model_evaluation_with_retry(
            prompt="Evaluation prompt",
            capability="citation-integrity",
            canonical_check_ids=canonical,
        )

        assert mock_call.call_count == 2
        assert status == "ok"
        assert output is not None
        assert len(output.verdicts) == 1
        assert output.verdicts[0].check_id == "cite-claim-supported"
        assert total_latency == 90
