"""Unit tests verifying check_source tagging on verdicts (US-20, D-019)."""

from compliance_review.checks.deterministic.citation import check_citations
from compliance_review.checks.deterministic.code import check_code
from compliance_review.checks.deterministic.disclosure import check_disclosure
from compliance_review.checks.deterministic.structure import check_structure
from compliance_review.skills.schema import ModelOutput, ModelVerdict


def test_model_verdict_check_source_default() -> None:
    """ModelVerdict defaults check_source to 'model'."""
    v = ModelVerdict(
        check_id="cite-doi-format",
        verdict="pass",
        confidence=1.0,
        severity="low",
    )
    assert v.check_source == "model"


def test_model_verdict_check_source_deterministic() -> None:
    """ModelVerdict accepts check_source='deterministic'."""
    v = ModelVerdict(
        check_id="cite-doi-resolvable",
        verdict="pass",
        confidence=1.0,
        severity="low",
        check_source="deterministic",
    )
    assert v.check_source == "deterministic"


def test_model_output_verdicts_tagged() -> None:
    """ModelOutput contains verdicts tagged with check_source."""
    out = ModelOutput(
        capability="citation-integrity",
        verdicts=[
            ModelVerdict(
                check_id="cite-doi-format",
                verdict="pass",
                confidence=1.0,
                severity="low",
                check_source="model",
            )
        ],
    )
    assert out.verdicts[0].check_source == "model"


def test_all_deterministic_checks_tag_source() -> None:
    """All 4 deterministic check modules tag check_source='deterministic' on all verdicts."""
    # 1. citation
    cite_verdicts = check_citations("Sample text with DOI 10.1000/182")
    assert len(cite_verdicts) > 0
    for v in cite_verdicts:
        assert v["check_source"] == "deterministic"

    # 2. structure
    struct_verdicts = check_structure("# Introduction\nText\n# Methods\nText", 100)
    assert len(struct_verdicts) > 0
    for v in struct_verdicts:
        assert v["check_source"] == "deterministic"

    # 3. disclosure
    disc_verdicts = check_disclosure("## Responsible AI\nUsed ChatGPT for drafting.")
    assert len(disc_verdicts) > 0
    for v in disc_verdicts:
        assert v["check_source"] == "deterministic"

    # 4. code
    code_files = {"sample.py": "print('hello')\n"}
    code_verdicts = check_code(code_files)
    assert len(code_verdicts) > 0
    for v in code_verdicts:
        assert v["check_source"] == "deterministic"
