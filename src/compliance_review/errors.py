"""Exception taxonomy for compliance review.

All exceptions inherit from ComplianceError.
Conforms to ARCHITECTURE.md §8.
"""


class ComplianceError(Exception):
    """Base exception for all domain errors."""


class IngestError(ComplianceError):
    """Raised when ingestion of a submission fails."""


class DuplicateSubmissionError(IngestError):
    """Raised when a submission with an existing external_id is ingested (US-04)."""


class SkillValidationError(ComplianceError):
    """Raised when a skill or frontmatter fails validation (US-07)."""


class NoActiveSkillError(ComplianceError):
    """Raised when no active skill version exists for a required capability (US-15)."""


class RetrievalError(ComplianceError):
    """Raised when capability gating or version retrieval fails (US-13, US-14)."""


class ModelError(ComplianceError):
    """Raised when the Ollama model inference fails or model is missing (US-23)."""


class ModelSchemaError(ModelError):
    """Raised when model output fails JSON parsing or schema validation after retry (US-21)."""


class EvidenceVerificationError(ComplianceError):
    """Raised when evidence verification fails invariant constraints (US-24)."""


class DatabaseError(ComplianceError):
    """Raised when database operations fail."""
