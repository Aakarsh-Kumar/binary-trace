"""Unit test verifying SkillFrontmatter validation per US-06, US-07, US-12."""

from datetime import date
from pathlib import Path

import pytest
from pydantic import ValidationError

from compliance_review.errors import SkillValidationError
from compliance_review.skills.loader import load_skill
from compliance_review.skills.schema import ChecklistItem, SkillFrontmatter


def test_valid_frontmatter() -> None:
    """Verify standard valid skill frontmatter validates correctly."""
    item = ChecklistItem(
        id="check-1",
        question="Is it clean?",
        severity="medium",
        evidence_requirement="page:1",
        deterministic_only=True,
    )
    frontmatter = SkillFrontmatter(
        capability="citation-integrity",
        version="v1",
        description="Test skill",
        inputs=["prose", "pdf"],
        checklist=[item],
        eval_status="draft",
        owner="tester",
        created_at=date(2026, 11, 4),
    )
    assert frontmatter.capability == "citation-integrity"
    assert len(frontmatter.checklist) == 1


def test_invalid_capability_enum() -> None:
    """Verify capability outside the fixed enum is rejected (US-12)."""
    item = ChecklistItem(
        id="check-1",
        question="Is it clean?",
        severity="medium",
        evidence_requirement="page:1",
    )
    with pytest.raises(ValidationError):
        SkillFrontmatter(
            capability="non-existent-capability",  # type: ignore[arg-type]
            version="v1",
            description="Test skill",
            inputs=["prose"],
            checklist=[item],
            eval_status="draft",
            owner="tester",
            created_at=date(2026, 11, 4),
        )


def test_empty_checklist_rejected() -> None:
    """Verify skill with zero checklist items is rejected."""
    with pytest.raises(ValidationError):
        SkillFrontmatter(
            capability="code-quality",
            version="v1",
            description="Test skill",
            inputs=["code_repo"],
            checklist=[],
            eval_status="draft",
            owner="tester",
            created_at=date(2026, 11, 4),
        )


def test_loader_rejects_capability_mismatch(tmp_path: Path) -> None:
    """Verify loader rejects skill when folder capability != declared capability (US-06)."""
    skill_dir = tmp_path / "skills" / "code-quality" / "v1"
    skill_dir.mkdir(parents=True)
    bad_skill = skill_dir / "SKILL.md"
    bad_skill.write_text(
        """---
capability: citation-integrity
version: v1
description: Mismatched capability
inputs: [prose]
checklist:
  - id: c1
    question: Q
    severity: low
    evidence_requirement: page:1
eval_status: draft
owner: tester
created_at: 2026-11-04
---
# Mismatch
""",
        encoding="utf-8",
    )
    with pytest.raises(SkillValidationError, match="Capability mismatch"):
        load_skill(bad_skill)
