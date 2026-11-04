"""Pydantic schemas for skills and retrieval conforming to ARCHITECTURE.md §5."""

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Capability = Literal["citation-integrity", "report-structure", "code-quality", "rai-disclosure"]
EvalStatus = Literal["draft", "evaluating", "active", "deprecated"]
Severity = Literal["low", "medium", "high", "critical"]


class ChecklistItem(BaseModel):
    """Single compliance checklist item within a skill."""

    id: str
    question: str
    severity: Severity
    evidence_requirement: str
    deterministic_only: bool = False
    advisory: bool = False
    false_positive_guardrails: list[str] = []
    model_config = ConfigDict(extra="forbid")


class SkillFrontmatter(BaseModel):
    """Frontmatter metadata for SKILL.md per ARCHITECTURE.md §5.1."""

    capability: Capability
    version: str
    description: str
    inputs: list[Literal["prose", "pdf", "code_repo", "disclosure_section"]]
    checklist: list[ChecklistItem] = Field(min_length=1)
    deterministic_preconditions: list[str] = []
    false_positive_guardrails: list[str] = []
    eval_status: EvalStatus
    owner: str
    created_at: date
    model_config = ConfigDict(extra="forbid")


class SelectionEntry(BaseModel):
    """Candidate or selected skill entry in retrieval."""

    capability: Capability
    version: str
    reason: str
    score: float
    stage: Literal["capability_gate", "faiss"]
    model_config = ConfigDict(extra="forbid")


class RetrievalDecision(BaseModel):
    """Record of capability gate and FAISS selection."""

    capability_set: dict[Capability, bool]
    candidates: list[SelectionEntry]
    selected: list[SelectionEntry]
    token_budget: int
    latency_ms: int
    model_config = ConfigDict(extra="forbid")


class ModelVerdict(BaseModel):
    """Individual verdict emitted by a model or deterministic check."""

    check_id: str
    verdict: Literal["pass", "flag", "not_applicable"]
    severity: Severity
    evidence_text: str | None = None
    evidence_location: str | None = None
    confidence: float = Field(ge=0.0, le=1.0)
    model_config = ConfigDict(extra="forbid")


class ModelOutput(BaseModel):
    """Structured output emitted for a capability."""

    capability: Capability
    verdicts: list[ModelVerdict]
    model_config = ConfigDict(extra="forbid")
