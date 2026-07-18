from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(ROOT_DIR / ".env")


class APIConfig:
    """Centralized API configuration read from environment variables.

    All configuration values are loaded once from the ``.env`` file at the
    project root.  Sensible defaults are provided for development and local
    testing against the Platzi Fake Store API.

    Usage:
        >>> APIConfig.BASE_URL
        'https://api.escuelajs.co/api/v1'
        >>> APIConfig.DEFAULT_TIMEOUT
        30
    """

    # ── Base ──────────────────────────────────────────────────────────────────
    BASE_URL: str = os.getenv("API_BASE_URL", "https://api.escuelajs.co/api/v1")

    # ── Authentication ────────────────────────────────────────────────────────
    TOKEN: str = os.getenv("API_TOKEN", "")
    API_KEY: str = os.getenv("API_KEY", "")
    API_KEY_HEADER: str = os.getenv("API_KEY_HEADER", "X-API-Key")
    USERNAME: str = os.getenv("API_USERNAME", "john@mail.com")
    PASSWORD: str = os.getenv("API_PASSWORD", "changeme")

    # ── Request behaviour ─────────────────────────────────────────────────────
    DEFAULT_TIMEOUT: int = int(os.getenv("API_DEFAULT_TIMEOUT", "30"))
    MAX_RETRIES: int = int(os.getenv("API_MAX_RETRIES", "3"))
    RETRY_BACKOFF_FACTOR: float = float(os.getenv("API_RETRY_BACKOFF_FACTOR", "0.5"))
    RETRY_STATUS_CODES: tuple[int, ...] = tuple(
        int(c.strip()) for c in os.getenv("API_RETRY_STATUS_CODES", "429,500,502,503,504").split(",") if c.strip()
    )

    # ── Performance ───────────────────────────────────────────────────────────
    MAX_ACCEPTABLE_RESPONSE_TIME_SECONDS: float = float(os.getenv("API_MAX_RESPONSE_TIME", "2.0"))

    # ── Pagination defaults ───────────────────────────────────────────────────
    DEFAULT_PAGE_SIZE: int = int(os.getenv("API_DEFAULT_PAGE_SIZE", "10"))
    DEFAULT_PAGE: int = int(os.getenv("API_DEFAULT_PAGE", "1"))

    @classmethod
    def to_dict(cls) -> dict[str, object]:
        """Return the configuration as a plain dictionary (useful for logging / reports)."""
        return {
            "BASE_URL": cls.BASE_URL,
            "DEFAULT_TIMEOUT": cls.DEFAULT_TIMEOUT,
            "MAX_RETRIES": cls.MAX_RETRIES,
            "RETRY_BACKOFF_FACTOR": cls.RETRY_BACKOFF_FACTOR,
            "RETRY_STATUS_CODES": cls.RETRY_STATUS_CODES,
            "MAX_ACCEPTABLE_RESPONSE_TIME_SECONDS": cls.MAX_ACCEPTABLE_RESPONSE_TIME_SECONDS,
            "DEFAULT_PAGE_SIZE": cls.DEFAULT_PAGE_SIZE,
            "DEFAULT_PAGE": cls.DEFAULT_PAGE,
        }
