"""Unit tests for ModelOutput schema validation and retry logic (US-21)."""

import json
from unittest.mock import MagicMock, patch

import pytest

from compliance_review.errors import ModelSchemaError
from compliance_review.model.schema_validation import (
    execute_model_evaluation_with_retry,
    parse_and_validate_model_output,
)


def test_parse_valid_output() -> None:
    """Verify parsing valid ModelOutput succeeds without retry."""
    payload = {
        "capability": "citation-integrity",
        "verdicts": [
            {
                "check_id": "cite-claim-supported",
                "verdict": "pass",
                "severity": "high",
                "evidence_text": "Doe et al. established this method.",
                "evidence_location": "page:2",
                "confidence": 0.95,
            }
        ],
    }
    output = parse_and_validate_model_output(
        json.dumps(payload), expected_capability="citation-integrity"
    )
    assert output.capability == "citation-integrity"
    assert len(output.verdicts) == 1
    assert output.verdicts[0].check_id == "cite-claim-supported"


def test_parse_extra_forbidden_keys() -> None:
    """Verify extra keys are strictly forbidden by pydantic schema."""
    payload = {
        "capability": "citation-integrity",
        "verdicts": [],
        "extra_field": "disallowed",
    }
    with pytest.raises(ModelSchemaError, match="Extra inputs are not permitted"):
        parse_and_validate_model_output(json.dumps(payload))


def test_retry_success_on_second_attempt() -> None:
    """Verify retry occurs exactly once and succeeds if second attempt returns valid output."""
    mock_responses = [
        ("INVALID JSON OUTPUT", "fake_digest", 50),
        (
            json.dumps(
                {
                    "capability": "rai-disclosure",
                    "verdicts": [
                        {
                            "check_id": "rai-sufficiency-judgment",
                            "verdict": "pass",
                            "severity": "high",
                            "evidence_text": None,
                            "evidence_location": None,
                            "confidence": 1.0,
                        }
                    ],
                }
            ),
            "fake_digest",
            60,
        ),
    ]

    with patch(
        "compliance_review.model.schema_validation.call_qwen", side_effect=mock_responses
    ) as mock_call:
        status, output, digest, latency, raw = execute_model_evaluation_with_retry(
            prompt="Test prompt",
            capability="rai-disclosure",
            run_index=1,
            client=MagicMock(),
        )
        assert mock_call.call_count == 2
        assert status == "ok"
        assert output is not None
        assert output.capability == "rai-disclosure"
        assert latency == 110


def test_retry_failure_returns_schema_error() -> None:
    """Verify failing twice returns status='schema_error' with no verdicts and exactly 2 calls."""
    mock_responses = [
        ("INVALID 1", "fake_digest", 50),
        ("INVALID 2", "fake_digest", 50),
    ]

    with patch(
        "compliance_review.model.schema_validation.call_qwen", side_effect=mock_responses
    ) as mock_call:
        status, output, digest, latency, raw = execute_model_evaluation_with_retry(
            prompt="Test prompt",
            capability="code-quality",
            run_index=1,
            client=MagicMock(),
        )
        assert mock_call.call_count == 2
        assert status == "schema_error"
        assert output is None
