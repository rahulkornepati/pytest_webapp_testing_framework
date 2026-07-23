from __future__ import annotations

import logging
import sqlite3
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Generator, Iterator

from database.db_config import DBConfig

logger = logging.getLogger("ecommerce_framework.database.connection")


class DatabaseConnection:
    """Thread-safe database connection manager with context manager support.

    This class provides an enterprise-grade connection wrapper around SQLite,
    supporting context managers, retry logic, and automatic WAL mode.

    Usage:
        >>> db = DatabaseConnection()
        >>> with db.connect() as conn:
        ...     cursor = conn.execute("SELECT COUNT(*) FROM products")
        ...     count = cursor.fetchone()[0]

    Singleton pattern ensures a single shared instance across the test suite
    unless explicitly overridden.
    """

    _instance: DatabaseConnection | None = None

    def __init__(
        self,
        database_path: Path | None = None,
        timeout: int | None = None,
    ) -> None:
        """Initialize the database connection manager.

        Args:
            database_path: Path to the SQLite database file. Defaults to
                           ``DBConfig.DATABASE_PATH``.
            timeout: Connection timeout in seconds. Defaults to
                     ``DBConfig.CONNECTION_TIMEOUT``.
        """
        self._database_path: Path = database_path or DBConfig.DATABASE_PATH
        self._timeout: int = timeout or DBConfig.CONNECTION_TIMEOUT
        self._connection: sqlite3.Connection | None = None

    @classmethod
    def get_instance(
        cls,
        database_path: Path | None = None,
        timeout: int | None = None,
    ) -> DatabaseConnection:
        """Return the shared singleton instance.

        Args:
            database_path: Optional database path override (used only on first
                           creation).
            timeout: Optional timeout override (used only on first creation).

        Returns:
            The singleton ``DatabaseConnection`` instance.
        """
        if cls._instance is None:
            cls._instance = cls(
                database_path=database_path or DBConfig.DATABASE_PATH,
                timeout=timeout or DBConfig.CONNECTION_TIMEOUT,
            )
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """Reset the singleton instance (useful between test suites)."""
        if cls._instance is not None:
            cls._instance.close()
            cls._instance = None

    @property
    def database_path(self) -> Path:
        """Return the path to the database file."""
        return self._database_path

    # ── Connection lifecycle ──────────────────────────────────────────────────

    def connect(self) -> sqlite3.Connection:
        """Open (or return an existing) connection to the SQLite database.

        The first invocation creates the connection; subsequent calls return
        the same connection until :meth:`close` is called.

        Returns:
            An open ``sqlite3.Connection``.

        Raises:
            sqlite3.Error: If the connection cannot be established after
                           retries.
        """
        if self._connection is not None:
            return self._connection

        last_exception: Exception | None = None
        for attempt in range(1, DBConfig.CONNECTION_RETRIES + 1):
            try:
                self._connection = sqlite3.connect(
                    str(self._database_path),
                    timeout=self._timeout,
                )
                self._connection.row_factory = sqlite3.Row
                if DBConfig.ENABLE_WAL_MODE:
                    self._connection.execute("PRAGMA journal_mode = WAL")
                if DBConfig.ENABLE_FOREIGN_KEYS:
                    self._connection.execute("PRAGMA foreign_keys = ON")
                logger.debug(
                    "Database connection established (attempt %d/%d): %s",
                    attempt,
                    DBConfig.CONNECTION_RETRIES,
                    self._database_path,
                )
                return self._connection
            except sqlite3.Error as exc:
                last_exception = exc
                logger.warning(
                    "Connection attempt %d/%d failed: %s",
                    attempt,
                    DBConfig.CONNECTION_RETRIES,
                    exc,
                )
                if attempt < DBConfig.CONNECTION_RETRIES:
                    time.sleep(DBConfig.CONNECTION_RETRY_DELAY)

        raise sqlite3.Error(
            f"Could not connect to database after {DBConfig.CONNECTION_RETRIES} "
            f"attempts: {last_exception}"
        ) from last_exception

    def close(self) -> None:
        """Close the database connection if open."""
        if self._connection is not None:
            try:
                self._connection.close()
                logger.debug("Database connection closed: %s", self._database_path)
            except sqlite3.Error as exc:
                logger.warning("Error closing database connection: %s", exc)
            finally:
                self._connection = None

    def is_connected(self) -> bool:
        """Check whether the database connection is currently open.

        Returns:
            ``True`` if a connection exists, ``False`` otherwise.
        """
        if self._connection is None:
            return False
        try:
            self._connection.execute("SELECT 1")
            return True
        except sqlite3.Error:
            return False

    # ── Context manager ───────────────────────────────────────────────────────

    @contextmanager
    def connection_context(self) -> Generator[sqlite3.Connection, None, None]:
        """Context manager that yields a connection and closes it on exit.

        Yields:
            An open ``sqlite3.Connection``.
        """
        conn = self.connect()
        try:
            yield conn
        finally:
            self.close()

    @contextmanager
    def transaction_context(self) -> Generator[sqlite3.Connection, None, None]:
        """Context manager for atomic transactions.

        Commits on success, rolls back on exception.

        Yields:
            An open ``sqlite3.Connection`` inside a transaction.
        """
        conn = self.connect()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            logger.exception("Transaction rolled back")
            raise

    def __enter__(self) -> sqlite3.Connection:
        """Enter context manager — returns the open connection."""
        return self.connect()

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object | None,
    ) -> None:
        """Exit context manager — closes the connection."""
        self.close()


# ── Convenience functions ──────────────────────────────────────────────────────


def get_connection(
    database_path: Path | None = None,
    timeout: int | None = None,
) -> sqlite3.Connection:
    """Get a database connection (convenience function).

    Uses the singleton pattern so that multiple calls within the same test
    session reuse the same connection.

    Args:
        database_path: Optional override for the database file path.
        timeout: Optional timeout override.

    Returns:
        An open ``sqlite3.Connection``.
    """
    return DatabaseConnection.get_instance(
        database_path=database_path,
        timeout=timeout,
    ).connect()


def close_connection() -> None:
    """Close the singleton database connection if open.

    Safe to call even if no connection has been established.
    """
    DatabaseConnection.reset_instance()
