"""Unit tests for model digest resolution and refusal invariant (US-19)."""

from unittest.mock import MagicMock

import pytest

from compliance_review.errors import ModelError
from compliance_review.model.qwen_client import resolve_model_digest


def test_resolve_real_model_digest() -> None:
    """Verify live Ollama qwen3:4b digest resolves to valid hex string."""
    digest = resolve_model_digest()
    assert isinstance(digest, str)
    assert len(digest) > 0


def test_missing_model_digest_refuses_execution() -> None:
    """Verify harness strictly refuses execution if model digest cannot be resolved."""
    mock_client = MagicMock()
    mock_client.show.side_effect = Exception("Model not found")
    mock_client.list.return_value = {"models": []}

    with pytest.raises(ModelError, match="Model digest for 'qwen3:4b' could not be resolved"):
        resolve_model_digest(mock_client)
