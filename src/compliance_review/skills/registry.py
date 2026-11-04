"""In-memory skill registry, read-only after load."""

from pathlib import Path

from compliance_review.skills.loader import load_all_skills
from compliance_review.skills.schema import Capability, SkillFrontmatter


class SkillRegistry:
    """Registry maintaining loaded skill versions."""

    def __init__(self) -> None:
        self._skills: dict[tuple[str, str], SkillFrontmatter] = {}
        self._loaded: bool = False

    def load(self, root: Path | str = "skills") -> None:
        """Load skills from disk."""
        self._skills = load_all_skills(root)
        self._loaded = True

    def get(self, capability: str, version: str) -> SkillFrontmatter | None:
        """Get frontmatter for a specific capability version."""
        return self._skills.get((capability, version))

    def list_by_capability(self, capability: Capability) -> list[SkillFrontmatter]:
        """List all versions of a given capability."""
        return [s for (cap, _), s in self._skills.items() if cap == capability]

    def list_all(self) -> list[SkillFrontmatter]:
        """List all loaded skills."""
        return list(self._skills.values())


registry = SkillRegistry()
