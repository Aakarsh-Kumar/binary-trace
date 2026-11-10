"""Unit tests for prompt canonical check_id enumeration conforming to D-046."""

from compliance_review.model.prompts import build_evaluation_prompt
from compliance_review.skills.loader import load_skill


def test_citation_prompt_enumerates_all_five_check_ids() -> None:
    """Verify citation-integrity prompt enumerates all five canonical check IDs."""
    prompt = build_evaluation_prompt(
        capability="citation-integrity",
        version="v2",
        submission_type="prose",
        checklist=[
            {
                "id": "cite-claim-supported",
                "question": "Q1",
                "severity": "high",
                "evidence_requirement": "page:1",
            },
            {
                "id": "cite-context-accurate",
                "question": "Q2",
                "severity": "medium",
                "evidence_requirement": "page:1",
            },
        ],
        submission_text="Sample paper text",
    )

    expected_header = (
        "Your response MUST contain a verdict for EACH of these five check_ids,\n"
        "using these exact strings (do not invent new check_ids):"
    )
    assert expected_header in prompt
    assert "- cite-claim-supported:" in prompt
    assert "- cite-context-accurate:" in prompt
    assert "- cite-doi-resolvable:" in prompt
    assert "- cite-no-duplicates:" in prompt
    assert "- cite-not-retracted:" in prompt
    assert "Do not return any other check_id." in prompt


def test_all_four_capabilities_enumerate_canonical_check_ids() -> None:
    """Verify all four capabilities in v2 enumerate canonical check IDs from SkillFrontmatter."""
    capabilities = [
        "citation-integrity",
        "report-structure",
        "code-quality",
        "rai-disclosure",
    ]

    for cap in capabilities:
        frontmatter, _ = load_skill(f"skills/{cap}/v2/SKILL.md")
        expected_check_ids = [item.id for item in frontmatter.checklist]
        assert len(expected_check_ids) == 5

        sub_type = "code_repo" if cap == "code-quality" else "prose"
        prompt = build_evaluation_prompt(
            capability=cap,
            version="v2",
            submission_type=sub_type,
            checklist=[item.model_dump() for item in frontmatter.checklist],
            submission_text="Sample submission content",
        )

        assert "Your response MUST contain a verdict for EACH of these five check_ids" in prompt
        for check_id in expected_check_ids:
            assert f"- {check_id}:" in prompt
        assert "Do not return any other check_id." in prompt


def test_fallback_to_provided_checklist_when_skill_file_missing() -> None:
    """Verify build_evaluation_prompt falls back to provided checklist when no skill file exists."""
    custom_checklist = [
        {
            "id": "custom-chk-1",
            "question": "Question 1",
            "severity": "high",
            "evidence_requirement": "file:test:1",
        },
        {
            "id": "custom-chk-2",
            "question": "Question 2",
            "severity": "medium",
            "evidence_requirement": "file:test:2",
        },
        {
            "id": "custom-chk-3",
            "question": "Question 3",
            "severity": "low",
            "evidence_requirement": "file:test:3",
        },
    ]

    prompt = build_evaluation_prompt(
        capability="custom-capability",
        version="v99",
        submission_type="prose",
        checklist=custom_checklist,
        submission_text="Sample text",
    )

    assert "Your response MUST contain a verdict for EACH of these three check_ids" in prompt
    assert "- custom-chk-1: Question 1" in prompt
    assert "- custom-chk-2: Question 2" in prompt
    assert "- custom-chk-3: Question 3" in prompt
    assert "Do not return any other check_id." in prompt
