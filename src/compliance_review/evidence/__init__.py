"""Evidence verification subsystem."""

from compliance_review.evidence.verifier import (
    FUZZY_THRESHOLD,
    PREFIX_LEN,
    EvidenceResult,
    normalize_span,
    verify_evidence,
)

__all__ = [
    "verify_evidence",
    "EvidenceResult",
    "PREFIX_LEN",
    "FUZZY_THRESHOLD",
    "normalize_span",
]
