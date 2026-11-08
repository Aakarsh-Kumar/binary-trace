"""Upload and review handler for dashboard submissions.

Conforms to ARCHITECTURE.md §10.5 and US-39.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from compliance_review.errors import (
    ComplianceError,
    DuplicateSubmissionError,
    IngestError,
    ModelError,
    NoActiveSkillError,
)

MAX_UPLOAD_SIZE = 50 * 1024 * 1024  # 50 MB


def handle_upload(
    file_bytes: bytes,
    filename: str,
    submission_type: str,
    ingest_fn: Callable[..., int],
    review_fn: Callable[..., Any],
) -> tuple[bool, str | None, str | None]:
    """Handle upload bytes, write to data/incoming, ingest and review.

    Returns (success, external_id, error_message).
    """
    if len(file_bytes) > MAX_UPLOAD_SIZE:
        return (False, None, "File exceeds 50 MB limit")

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    safe_name = re.sub(r"[^A-Za-z0-9._-]", "_", filename)
    basename_no_ext = Path(safe_name).stem
    external_id = f"upload-{ts}-{basename_no_ext}"
    incoming_dir = Path("data/incoming")
    incoming_dir.mkdir(parents=True, exist_ok=True)
    incoming_path = incoming_dir / f"{ts}_{safe_name}"

    incoming_path.write_bytes(file_bytes)

    try:
        sub_id = ingest_fn(
            source=incoming_path,
            submission_type=submission_type,
            external_id=external_id,
        )
        review_fn(submission_id=sub_id, skill_status="evaluating")
        return (True, external_id, None)
    except DuplicateSubmissionError:
        return (
            False,
            None,
            "A submission with this id already exists. Rename the file and try again.",
        )
    except IngestError as e:
        return (False, None, f"Ingestion failed: {e}")
    except ModelError as e:
        return (False, None, f"Review failed at model stage: {e}")
    except NoActiveSkillError as e:
        return (False, None, f"No evaluating skill for this submission: {e}")
    except ComplianceError as e:
        return (False, None, f"{type(e).__name__}: {e}")
    except Exception as e:
        return (False, None, f"Unexpected error: {e}")
