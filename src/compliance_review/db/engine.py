"""SQLAlchemy Engine factory conforming to ARCHITECTURE.md §2.2."""

from typing import Any

from sqlalchemy import Engine, create_engine

from compliance_review.config import Settings


def get_engine(dsn: str | None = None) -> Engine:
    """Create a SQLAlchemy Core engine."""
    if dsn is None:
        # Settings reads cr_mysql_dsn from environment / .env.local
        settings = Settings()  # type: ignore[call-arg] # reason: pydantic-settings populates from env
        dsn = settings.cr_mysql_dsn

    # Support SSL for PyMySQL caching_sha2_password authentication
    # without external cryptography package
    connect_args: dict[str, Any] = {}
    if "pymysql" in dsn:
        connect_args["ssl"] = {}

    return create_engine(
        dsn,
        pool_pre_ping=True,
        echo=False,
        connect_args=connect_args,
    )
