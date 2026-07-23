from __future__ import annotations

"""PyTest fixtures for the database test suite.

Provides reusable fixtures for database connections, helpers, and
common test data references.  All database tests should import
fixtures from this module or use the ``db_*`` fixtures.
"""

import logging
from pathlib import Path
from typing import Any, Generator

import pytest

from database.db_config import DBConfig
from database.db_connection import DatabaseConnection, close_connection, get_connection
from database.db_helpers import DBHelpers
from database.db_queries import fetch_one, fetch_scalar
from database.db_setup import create_database
from database.database_utils import DatabaseUtils

logger = logging.getLogger("ecommerce_framework.database.conftest")


# ── Session-scoped fixtures ────────────────────────────────────────────────────


@pytest.fixture(scope="session", autouse=True)
def db_setup() -> Generator[Path, None, None]:
    """Ensure the database exists before any database tests run.

    Creates the database with schema and sample data if it does not
    already exist.  The database connection is closed after the session
    finishes.
    """
    db_path = DBConfig.DATABASE_PATH
    if not db_path.exists():
        logger.info("Database not found — creating: %s", db_path)
        create_database(db_path)
    else:
        logger.info("Database exists: %s", db_path)

    yield db_path

    close_connection()


@pytest.fixture(scope="session")
def db_connection() -> Generator[sqlite3.Connection, None, None]:
    """Provide a database connection for the test session.

    Yields:
        An open ``sqlite3.Connection``.
    """
    conn = get_connection()
    yield conn
    # Connection is closed by ``db_setup`` teardown


@pytest.fixture(scope="session")
def db_helpers() -> DBHelpers:
    """Provide the ``DBHelpers`` static utility class.

    Returns:
        The ``DBHelpers`` class itself (all methods are static).
    """
    return DBHelpers


@pytest.fixture(scope="session")
def db_utils() -> DatabaseUtils:
    """Provide the ``DatabaseUtils`` static utility class.

    Returns:
        The ``DatabaseUtils`` class itself (all methods are static).
    """
    return DatabaseUtils


# ── Test data fixtures ─────────────────────────────────────────────────────────


@pytest.fixture(scope="session")
def product_names() -> list[str]:
    """Return a sorted list of all product names from the database.

    Returns:
        Alphabetically sorted list of product names.
    """
    from database.db_queries import fetch_column

    return fetch_column("SELECT name FROM products ORDER BY name")


@pytest.fixture(scope="session")
def category_names() -> list[str]:
    """Return a sorted list of all category names from the database.

    Returns:
        Alphabetically sorted list of category names.
    """
    from database.db_queries import fetch_column

    return fetch_column("SELECT name FROM categories ORDER BY name")


@pytest.fixture(scope="session")
def user_names() -> list[str]:
    """Return a list of all usernames from the database.

    Returns:
        List of usernames.
    """
    from database.db_queries import fetch_column

    return fetch_column("SELECT username FROM users ORDER BY username")


@pytest.fixture(scope="session")
def known_products() -> dict[str, int]:
    """Return a mapping of product name → product_id for known products.

    Returns:
        Dictionary mapping product names to their IDs.
    """
    from database.db_queries import fetch_all

    rows = fetch_all("SELECT product_id, name FROM products")
    return {row["name"]: row["product_id"] for row in rows}


@pytest.fixture(scope="session")
def known_users() -> dict[str, dict[str, Any]]:
    """Return a mapping of username → user info for known users.

    Returns:
        Dictionary mapping usernames to user detail dicts.
    """
    from database.db_queries import fetch_all

    rows = fetch_all(
        "SELECT user_id, username, email, role, is_active FROM users"
    )
    return {
        row["username"]: {
            "user_id": row["user_id"],
            "email": row["email"],
            "role": row["role"],
            "is_active": row["is_active"],
        }
        for row in rows
    }


@pytest.fixture(scope="session")
def known_categories() -> dict[str, int]:
    """Return a mapping of category name → category_id.

    Returns:
        Dictionary mapping category names to their IDs.
    """
    from database.db_queries import fetch_all

    rows = fetch_all("SELECT category_id, name FROM categories")
    return {row["name"]: row["category_id"] for row in rows}


# ── Function-scoped fixtures ───────────────────────────────────────────────────


@pytest.fixture
def db_cleanup(request: pytest.FixtureRequest) -> Generator[None, None, None]:
    """Ensure database state is clean after a test that makes modifications.

    This fixture wraps a test function and verifies that the database
    connection is still alive afterwards.  For tests that modify data,
    the calling test should handle its own cleanup.
    """
    yield
    # Verify connection is still alive
    try:
        get_connection().execute("SELECT 1")
    except Exception:
        logger.warning("Database connection lost after test — reconnecting")
        close_connection()
        get_connection()
