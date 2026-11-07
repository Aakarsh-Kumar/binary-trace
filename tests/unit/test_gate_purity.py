"""Unit test proving capability_gate.py imports no model, faiss, or torch modules."""

from compliance_review.retrieval import capability_gate


def test_gate_purity_no_forbidden_imports() -> None:
    """Verify capability_gate has zero imports of model libraries or vector indexes."""
    forbidden = ["faiss", "torch", "sentence_transformers", "ollama", "transformers"]

    # Check module attributes and globals
    for name in forbidden:
        assert (
            name not in capability_gate.__dict__
        ), f"Forbidden module '{name}' imported in capability_gate"

    # Verify deterministic behavior under D-028
    caps, reasons = capability_gate.determine_capability_set(
        "prose", {"text": "Hello world", "word_count": 2}
    )
    assert caps["citation-integrity"] is False
    assert caps["report-structure"] is False
    assert caps["rai-disclosure"] is False
    assert caps["code-quality"] is False
    assert "code-quality disabled" in reasons["code-quality"]

    # Verify prose with preconditions satisfied
    caps_full, _ = capability_gate.determine_capability_set(
        "prose",
        {
            "text": "Hello world\n\nReferences: 10.1234\n\nDisclosure: AI used\n" + "word " * 500,
            "word_count": 510,
            "references_present": True,
            "disclosure_present": True,
        },
    )
    assert caps_full["citation-integrity"] is True
    assert caps_full["report-structure"] is True
    assert caps_full["rai-disclosure"] is True
    assert caps_full["code-quality"] is False


def test_gate_rules_for_code() -> None:
    """Verify code submissions strictly ban citation-integrity and rai-disclosure (US-13)."""
    caps, reasons = capability_gate.determine_capability_set(
        "code", {"files": {"main.py": "print(1)"}, "loc": 1}
    )
    assert caps["code-quality"] is True
    assert caps["citation-integrity"] is False
    assert caps["rai-disclosure"] is False
    assert caps["report-structure"] is False


def test_gate_rules_for_mixed() -> None:
    """Verify mixed submissions gate conditionally per §6.2."""
    # Under 500 words and no bibliography
    extracted = {"text": "Short text", "word_count": 20, "files": {"test.py": "x=1"}}
    caps, reasons = capability_gate.determine_capability_set("mixed", extracted)
    assert caps["code-quality"] is True
    assert caps["report-structure"] is False
    assert caps["citation-integrity"] is False
    assert caps["rai-disclosure"] is False

    # Over 500 words with References and Disclosure
    extracted_full = {
        "text": "Introduction\n\nReferences: 10.1234/5678\n\nDisclosure: used AI tool\n"
        + "word " * 550,
        "word_count": 560,
        "files": {"app.py": "pass"},
    }
    caps_full, _ = capability_gate.determine_capability_set("mixed", extracted_full)
    assert caps_full["code-quality"] is True
    assert caps_full["report-structure"] is True
    assert caps_full["citation-integrity"] is True
    assert caps_full["rai-disclosure"] is True
