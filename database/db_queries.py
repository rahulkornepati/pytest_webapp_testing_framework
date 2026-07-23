from __future__ import annotations

"""Reusable query-execution functions.

All public functions in this module accept a ``SQLQueries`` enum member (or a
raw SQL string) and return typed, processed results.  Tests must never call
``cursor.execute()`` directly — always delegate to this module.
"""

import logging
from typing import Any

from database.db_connection import get_connection
from database.sql_constants import SQLQueries

logger = logging.getLogger("ecommerce_framework.database.queries")


# ── Scalar queries (single value) ──────────────────────────────────────────────


def fetch_scalar(query: SQLQueries | str, params: tuple[Any, ...] = ()) -> Any:
    """Execute a query and return the first column of the first row.

    Args:
        query: A ``SQLQueries`` enum member or raw SQL string.
        params: Tuple of parameter values for the query placeholder ``?``.

    Returns:
        The scalar value, or ``None`` if no rows are found.

    Example:
        >>> fetch_scalar(SQLQueries.PRODUCT_COUNT)
        24
    """
    conn = get_connection()
    cursor = conn.execute(str(query), params)
    row = cursor.fetchone()
    return row[0] if row else None


def fetch_one(query: SQLQueries | str, params: tuple[Any, ...] = ()) -> dict[str, Any] | None:
    """Execute a query and return the first row as a dictionary.

    Args:
        query: A ``SQLQueries`` enum member or raw SQL string.
        params: Tuple of parameter values for the query placeholder ``?``.

    Returns:
        A dictionary of (column_name → value), or ``None`` if no rows.

    Example:
        >>> fetch_one(SQLQueries.PRODUCT_BY_NAME, ("Sauce Labs Backpack",))
        {'product_id': 1, 'name': 'Sauce Labs Backpack', ...}
    """
    conn = get_connection()
    cursor = conn.execute(str(query), params)
    row = cursor.fetchone()
    return dict(row) if row else None


def fetch_all(query: SQLQueries | str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
    """Execute a query and return all result rows as dictionaries.

    Args:
        query: A ``SQLQueries`` enum member or raw SQL string.
        params: Tuple of parameter values for the query placeholder ``?``.

    Returns:
        A list of dictionaries, each mapping column names to values.

    Example:
        >>> fetch_all(SQLQueries.PRODUCTS_PRICE_ASC)
        [{'name': 'Sauce Labs Stress Ball', 'price': 4.99}, ...]
    """
    conn = get_connection()
    cursor = conn.execute(str(query), params)
    rows = cursor.fetchall()
    return [dict(row) for row in rows]


def fetch_column(query: SQLQueries | str, params: tuple[Any, ...] = ()) -> list[Any]:
    """Execute a query and return the first column from every row.

    Args:
        query: A ``SQLQueries`` enum member or raw SQL string.
        params: Tuple of parameter values for the query placeholder ``?``.

    Returns:
        A list of scalar values from the first column of each result row.

    Example:
        >>> fetch_column(SQLQueries.PRODUCTS_NAME_ASC)
        ['Sauce Labs Backpack', 'Sauce Labs Bike Light', ...]
    """
    conn = get_connection()
    cursor = conn.execute(str(query), params)
    return [row[0] for row in cursor.fetchall()]


# ── Write operations ───────────────────────────────────────────────────────────


def execute_write(query: SQLQueries | str, params: tuple[Any, ...] = ()) -> int:
    """Execute a write query (INSERT, UPDATE, DELETE) and return the row count.

    Args:
        query: A ``SQLQueries`` enum member or raw SQL string.
        params: Tuple of parameter values for the query placeholder ``?``.

    Returns:
        The number of rows affected.

    Example:
        >>> execute_write(SQLQueries.CART_ITEM_DELETE, (1, 2))
        1
    """
    conn = get_connection()
    cursor = conn.execute(str(query), params)
    conn.commit()
    logger.debug("Write query executed: %s — %d rows affected", query, cursor.rowcount)
    return cursor.rowcount


def execute_write_many(query: SQLQueries | str, param_list: list[tuple[Any, ...]]) -> int:
    """Execute a write query with multiple parameter sets.

    Args:
        query: A ``SQLQueries`` enum member or raw SQL string.
        param_list: A list of parameter tuples.

    Returns:
        The total number of rows affected across all executions.
    """
    conn = get_connection()
    cursor = conn.executemany(str(query), param_list)
    conn.commit()
    logger.debug("Bulk write: %s — %d rows affected", query, cursor.rowcount)
    return cursor.rowcount


# ── Existence / validation helpers ─────────────────────────────────────────────


def exists(query: SQLQueries | str, params: tuple[Any, ...] = ()) -> bool:
    """Check whether a query returns any rows.

    Args:
        query: A ``SQLQueries`` enum member or raw SQL string.
        params: Tuple of parameter values.

    Returns:
        ``True`` if at least one row exists, ``False`` otherwise.
    """
    conn = get_connection()
    cursor = conn.execute(str(query), params)
    return cursor.fetchone() is not None


def count(query: SQLQueries | str, params: tuple[Any, ...] = ()) -> int:
    """Execute a COUNT query and return the integer result.

    Args:
        query: A ``SQLQueries`` enum member or raw SQL string.
        params: Tuple of parameter values.

    Returns:
        The count value (always 0 or positive).

    Example:
        >>> count(SQLQueries.USER_ACTIVE_COUNT)
        8
    """
    result = fetch_scalar(query, params)
    return result if result is not None else 0
