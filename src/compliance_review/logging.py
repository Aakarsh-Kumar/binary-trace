"""Structlog configuration emitting JSON logs conforming to ARCHITECTURE.md §11."""

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import structlog
from structlog.types import EventDict, WrappedLogger


def add_utc_timestamp(logger: WrappedLogger, method_name: str, event_dict: EventDict) -> EventDict:
    """Add ISO-8601 UTC timestamp as 'ts'."""
    event_dict["ts"] = datetime.now(timezone.utc).isoformat()
    return event_dict


def configure_logging(log_dir: Path | str = "data/logs") -> None:
    """Configure structlog to emit JSON to stdout and rotating log file."""
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    logfile = log_path / "compliance_review.log"

    processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        add_utc_timestamp,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer(),
    ]

    # Open logfile for appending JSON lines
    file_dest = open(logfile, "a", encoding="utf-8")

    structlog.configure(
        processors=processors,
        logger_factory=structlog.WriteLoggerFactory(file=file_dest),
        cache_logger_on_first_use=True,
    )


def get_logger(component: str = "cli") -> Any:
    """Return a bound structlog logger with component name."""
    return structlog.get_logger().bind(component=component)
