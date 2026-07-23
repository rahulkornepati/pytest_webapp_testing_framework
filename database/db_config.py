from __future__ import annotations

import os
from pathlib import Path
from typing import ClassVar


class DBConfig:
    """Centralized database configuration for SQLite.

    All configuration values are loaded once from environment variables
    with sensible defaults for local development and CI execution.

    Usage:
        >>> DBConfig.DATABASE_PATH
        PosixPath('/project/root/database/ecommerce.db')
        >>> DBConfig.CONNECTION_TIMEOUT
        10
    """

    # ── Project paths ─────────────────────────────────────────────────────────
    ROOT_DIR: ClassVar[Path] = Path(__file__).resolve().parents[1]
    DATABASE_DIR: ClassVar[Path] = ROOT_DIR / "database"

    # ── Database file ─────────────────────────────────────────────────────────
    DATABASE_FILENAME: ClassVar[str] = os.getenv("DB_FILENAME", "ecommerce.db")
    DATABASE_PATH: ClassVar[Path] = Path(
        os.getenv("DB_PATH", str(DATABASE_DIR / DATABASE_FILENAME))
    )

    # ── Connection settings ───────────────────────────────────────────────────
    CONNECTION_TIMEOUT: ClassVar[int] = int(os.getenv("DB_TIMEOUT", "10"))
    CONNECTION_RETRIES: ClassVar[int] = int(os.getenv("DB_RETRIES", "3"))
    CONNECTION_RETRY_DELAY: ClassVar[float] = float(os.getenv("DB_RETRY_DELAY", "0.5"))

    # ── Pool / performance ────────────────────────────────────────────────────
    ENABLE_WAL_MODE: ClassVar[bool] = os.getenv("DB_WAL_MODE", "true").lower() == "true"
    ENABLE_FOREIGN_KEYS: ClassVar[bool] = os.getenv("DB_FOREIGN_KEYS", "true").lower() == "true"

    # ── Test suite defaults ───────────────────────────────────────────────────
    DEFAULT_PAGE_SIZE: ClassVar[int] = int(os.getenv("DB_PAGE_SIZE", "20"))
    MAX_QUERY_RETRIES: ClassVar[int] = int(os.getenv("DB_QUERY_RETRIES", "3"))

    @classmethod
    def to_dict(cls) -> dict[str, object]:
        """Return configuration as a plain dictionary (useful for logging / reports)."""
        return {
            "database_path": str(cls.DATABASE_PATH),
            "connection_timeout": cls.CONNECTION_TIMEOUT,
            "connection_retries": cls.CONNECTION_RETRIES,
            "wal_mode": cls.ENABLE_WAL_MODE,
            "foreign_keys": cls.ENABLE_FOREIGN_KEYS,
        }
