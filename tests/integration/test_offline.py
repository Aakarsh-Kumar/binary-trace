"""Integration test verifying offline execution per PRD.md §6.5."""

import socket

import pytest

from compliance_review.checks.deterministic.citation import check_citations
from compliance_review.checks.deterministic.code import check_code
from compliance_review.checks.deterministic.disclosure import check_disclosure
from compliance_review.checks.deterministic.structure import check_structure
from compliance_review.retrieval.capability_gate import determine_capability_set


def test_offline_execution_with_blocked_egress(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify system performs capability gating and deterministic checks with network blocked."""

    def guarded_connect(*args: object, **kwargs: object) -> None:
        raise OSError("Network egress blocked in offline test mode")

    monkeypatch.setattr(socket, "create_connection", guarded_connect)

    # 1. Deterministic capability gate with network blocked
    caps, reasons = determine_capability_set("prose", {"text": "offline text", "word_count": 2})
    assert caps["citation-integrity"] is True
    assert caps["code-quality"] is False

    # 2. Deterministic checks with network blocked
    c_res = check_citations("Sample text with no external calls.")
    assert len(c_res) == 3

    s_res = check_structure("Introduction Method Result Discussion", 4)
    assert len(s_res) == 3

    cd_res = check_code({"test.py": "x = 1\n"})
    assert len(cd_res) == 3

    d_res = check_disclosure("Disclosure: used AI tool", False)
    assert len(d_res) == 3
