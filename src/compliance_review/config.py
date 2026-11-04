"""Configuration settings conforming to ARCHITECTURE.md §13."""

from pathlib import Path

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from compliance_review.errors import ComplianceError


class Settings(BaseSettings):
    """Runtime configuration read from environment and .env.local."""

    cr_mysql_dsn: str
    cr_ollama_host: str = "http://127.0.0.1:11434"
    cr_ollama_model: str = "qwen3:4b"
    cr_k_runs: int = 3
    cr_fuzzy_threshold: float = 0.92
    cr_stability_threshold: float = 0.85
    cr_min_candidate_score: float = 0.30
    cr_vector_index_path: Path = Path("data/vector_index/skills.faiss")
    cr_embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    cr_log_dir: Path = Path("data/logs")
    cr_cache_dir: Path = Path("data/cache")

    model_config = SettingsConfigDict(env_file=".env.local", extra="forbid")

    @model_validator(mode="after")
    def verify_frozen_thresholds(self) -> "Settings":
        """Assert cr_fuzzy_threshold matches §7.1 and cr_stability_threshold matches PRD §6.3."""
        if self.cr_fuzzy_threshold != 0.92:
            raise ComplianceError(
                f"Frozen invariant violation: cr_fuzzy_threshold must be 0.92, "
                f"got {self.cr_fuzzy_threshold}"
            )
        if self.cr_stability_threshold != 0.85:
            raise ComplianceError(
                f"Frozen invariant violation: cr_stability_threshold must be 0.85, "
                f"got {self.cr_stability_threshold}"
            )
        return self
