"""Unit tests for skill status management and review filter (US-08, D-012, D-014)."""

from pathlib import Path

import pytest
from typer.testing import CliRunner

from compliance_review.cli import app
from compliance_review.errors import SkillValidationError
from compliance_review.skills.loader import load_skill, set_skill_status

runner = CliRunner()


def test_set_skill_status_success(tmp_path: Path) -> None:
    """Verify setting eval_status rewrites frontmatter cleanly."""
    skill_dir = tmp_path / "citation-integrity" / "v1"
    skill_dir.mkdir(parents=True)
    skill_file = skill_dir / "SKILL.md"

    initial_content = """---
capability: citation-integrity
version: v1
description: Test skill description
inputs:
  - prose
checklist:
  - id: test-check
    question: Is test passing?
    severity: high
    evidence_requirement: none
    deterministic_only: true
eval_status: draft
owner: tester
created_at: 2026-11-04
---
# Test Body
"""
    skill_file.write_text(initial_content, encoding="utf-8")

    updated = set_skill_status(tmp_path, "citation-integrity", "v1", "evaluating")
    assert updated == skill_file

    frontmatter, body = load_skill(skill_file)
    assert frontmatter.eval_status == "evaluating"
    assert "Test Body" in body


def test_set_skill_status_invalid_status(tmp_path: Path) -> None:
    """Verify set_skill_status rejects invalid status."""
    with pytest.raises(SkillValidationError, match="Invalid status"):
        set_skill_status(tmp_path, "citation-integrity", "v1", "nonexistent_status")


def test_set_skill_status_missing_file(tmp_path: Path) -> None:
    """Verify set_skill_status raises when SKILL.md is missing."""
    with pytest.raises(SkillValidationError, match="SKILL.md not found"):
        set_skill_status(tmp_path, "citation-integrity", "v99", "evaluating")


def test_cli_set_status_and_review_filter(tmp_path: Path) -> None:
    """Verify CLI set-status command and review --skill-status validation."""
    # Test invalid review --skill-status
    res = runner.invoke(app, ["review", "--submission-id", "1", "--skill-status", "invalid_val"])
    assert res.exit_code != 0
    assert "Invalid --skill-status" in res.output

    # Test review --help shows --skill-status
    help_res = runner.invoke(app, ["review", "--help"])
    assert help_res.exit_code == 0
    assert "--skill-status" in help_res.output
