"""Unit test asserting error taxonomy conforms to ARCHITECTURE.md §8."""

import pytest

from compliance_review.errors import (
    ComplianceError,
    DatabaseError,
    DuplicateSubmissionError,
    EvidenceVerificationError,
    IngestError,
    ModelError,
    ModelSchemaError,
    NoActiveSkillError,
    RetrievalError,
    SkillValidationError,
)


def test_error_hierarchy() -> None:
    """Verify that all domain exceptions properly subclass ComplianceError."""
    assert issubclass(IngestError, ComplianceError)
    assert issubclass(DuplicateSubmissionError, IngestError)
    assert issubclass(SkillValidationError, ComplianceError)
    assert issubclass(NoActiveSkillError, ComplianceError)
    assert issubclass(RetrievalError, ComplianceError)
    assert issubclass(ModelError, ComplianceError)
    assert issubclass(ModelSchemaError, ModelError)
    assert issubclass(EvidenceVerificationError, ComplianceError)
    assert issubclass(DatabaseError, ComplianceError)


def test_exception_instantiation() -> None:
    """Verify exceptions can be raised and caught as ComplianceError."""
    with pytest.raises(ComplianceError):
        raise DuplicateSubmissionError("external_id exists")

    with pytest.raises(ModelError):
        raise ModelSchemaError("schema failed after retry")
