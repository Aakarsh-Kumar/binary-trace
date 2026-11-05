"""Skill loader and frontmatter validator conforming to ARCHITECTURE.md §5.1 and US-06/US-07."""

from pathlib import Path
from typing import Any

import yaml  # type: ignore[import-untyped]  # reason: types-PyYAML not pinned in ARCHITECTURE.md §2
from pydantic import ValidationError

from compliance_review.errors import SkillValidationError
from compliance_review.skills.schema import SkillFrontmatter


def parse_skill_markdown(content: str) -> tuple[dict[str, Any], str]:
    """Extract YAML frontmatter and markdown body from SKILL.md content."""
    lines = content.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        raise SkillValidationError("SKILL.md missing opening '---' frontmatter delimiter")

    frontmatter_lines: list[str] = []
    body_start_idx = -1
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            body_start_idx = i + 1
            break
        frontmatter_lines.append(lines[i])

    if body_start_idx == -1:
        raise SkillValidationError("SKILL.md missing closing '---' frontmatter delimiter")

    raw_yaml = "".join(frontmatter_lines)
    try:
        data = yaml.safe_load(raw_yaml)
        if not isinstance(data, dict):
            raise SkillValidationError("SKILL.md frontmatter must be a YAML mapping")
    except yaml.YAMLError as exc:
        raise SkillValidationError(f"Invalid YAML in SKILL.md: {exc}") from exc

    body = "".join(lines[body_start_idx:])
    return data, body


def load_skill(skill_file: Path | str) -> tuple[SkillFrontmatter, str]:
    """Load and validate a single SKILL.md file."""
    path = Path(skill_file)
    if not path.is_file():
        raise SkillValidationError(f"Skill file not found: {path}")

    content = path.read_text(encoding="utf-8")
    raw_data, body = parse_skill_markdown(content)

    # US-06 constraint: parent directory structure must be skills/<capability>/<version>/SKILL.md
    version_folder = path.parent.name
    capability_folder = path.parent.parent.name

    try:
        frontmatter = SkillFrontmatter.model_validate(raw_data)
    except ValidationError as exc:
        raise SkillValidationError(f"Schema validation error in {path}: {exc}") from exc

    if frontmatter.capability != capability_folder:
        raise SkillValidationError(
            f"Capability mismatch in {path}: frontmatter declares '{frontmatter.capability}', "
            f"but parent directory is '{capability_folder}'"
        )

    if frontmatter.version != version_folder:
        raise SkillValidationError(
            f"Version mismatch in {path}: frontmatter declares '{frontmatter.version}', "
            f"but directory is '{version_folder}'"
        )

    return frontmatter, body


def load_all_skills(skills_root: Path | str = "skills") -> dict[tuple[str, str], SkillFrontmatter]:
    """Discover and validate all SKILL.md files under root directory."""
    root = Path(skills_root)
    if not root.is_dir():
        raise SkillValidationError(f"Skills root directory not found: {root}")

    skills: dict[tuple[str, str], SkillFrontmatter] = {}
    for skill_path in root.glob("**/SKILL.md"):
        frontmatter, _ = load_skill(skill_path)
        key = (frontmatter.capability, frontmatter.version)
        skills[key] = frontmatter

    return skills


def set_skill_status(
    skills_root: Path | str,
    capability: str,
    version: str,
    status: str,
) -> Path:
    """Update eval_status in a SKILL.md frontmatter (US-08, D-014)."""
    valid_statuses = {"draft", "evaluating", "active", "deprecated"}
    if status not in valid_statuses:
        raise SkillValidationError(f"Invalid status '{status}'. Must be one of {valid_statuses}")

    skill_path = Path(skills_root) / capability / version / "SKILL.md"
    if not skill_path.is_file():
        raise SkillValidationError(f"SKILL.md not found at {skill_path}")

    content = skill_path.read_text(encoding="utf-8")
    raw_data, body = parse_skill_markdown(content)
    raw_data["eval_status"] = status

    # Validate updated frontmatter conforms to schema
    try:
        SkillFrontmatter.model_validate(raw_data)
    except ValidationError as exc:
        raise SkillValidationError(f"Schema validation error after updating status: {exc}") from exc

    new_yaml = yaml.dump(raw_data, sort_keys=False, default_flow_style=False)
    new_content = f"---\n{new_yaml}---\n{body.lstrip()}"
    skill_path.write_text(new_content, encoding="utf-8")
    return skill_path
