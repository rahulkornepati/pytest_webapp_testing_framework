from __future__ import annotations

"""Utility functions for database testing.

Provides reusable helpers for data comparisons, formatting, and
common validation patterns used across the database test suite.
"""

import logging
from typing import Any

from database.db_queries import fetch_all, fetch_scalar
from database.sql_constants import SQLQueries

logger = logging.getLogger("ecommerce_framework.database.utils")


class DatabaseUtils:
    """Static utility methods supporting database test operations."""

    # ==========================================================================
    # Product utilities
    # ==========================================================================

    @staticmethod
    def get_product_names() -> list[str]:
        """Return a sorted list of all product names from the database.

        Returns:
            Alphabetically sorted list of product names.
        """
        rows = fetch_all("SELECT name FROM products ORDER BY name")
        return [row["name"] for row in rows]

    @staticmethod
    def get_products_by_category(category_name: str) -> list[dict[str, Any]]:
        """Return all products belonging to a specific category.

        Args:
            category_name: The category name to filter by.

        Returns:
            List of product dictionaries.
        """
        return fetch_all(SQLQueries.SEARCH_PRODUCTS_BY_CATEGORY, (f"%{category_name}%",))

    @staticmethod
    def get_products_in_price_range(min_price: float, max_price: float) -> list[dict[str, Any]]:
        """Return all products within a given price range.

        Args:
            min_price: Minimum price (inclusive).
            max_price: Maximum price (inclusive).

        Returns:
            List of product dictionaries sorted by price.
        """
        return fetch_all(SQLQueries.SEARCH_PRODUCTS_BY_PRICE_RANGE, (min_price, max_price))

    @staticmethod
    def verify_product_field(product_name: str, field: str, expected: Any) -> tuple[bool, str]:
        """Generic helper to verify a product field matches an expected value.

        Args:
            product_name: Name of the product to check.
            field: Column name to verify.
            expected: Expected value.

        Returns:
            Tuple of ``(is_match, message)``.
        """
        row = fetch_scalar(
            f"SELECT {field} FROM products WHERE name = ?",
            (product_name,),
        )
        if row is None:
            return False, f"Product '{product_name}' not found"
        if row != expected:
            return False, f"Product '{product_name}'.{field}: expected '{expected}', got '{row}'"
        return True, f"Product '{product_name}'.{field} matches expected value '{expected}'"

    # ==========================================================================
    # Order utilities
    # ==========================================================================

    @staticmethod
    def get_order_items(order_id: int) -> list[dict[str, Any]]:
        """Return all items for a given order.

        Args:
            order_id: The order ID.

        Returns:
            List of order item dictionaries with product details.
        """
        return fetch_all(SQLQueries.ORDER_ITEMS_BY_ORDER_ID, (order_id,))

    @staticmethod
    def calculate_order_total(order_id: int) -> float:
        """Calculate the expected total for an order from its items.

        Args:
            order_id: The order ID.

        Returns:
            The calculated total (quantity × unit_price).
        """
        total = fetch_scalar(SQLQueries.ORDER_ITEMS_TOTAL, (order_id,))
        return float(total) if total is not None else 0.0

    # ==========================================================================
    # Category utilities
    # ==========================================================================

    @staticmethod
    def get_category_names() -> list[str]:
        """Return a sorted list of all category names.

        Returns:
            Alphabetically sorted list of category names.
        """
        rows = fetch_all("SELECT name FROM categories ORDER BY name")
        return [row["name"] for row in rows]

    @staticmethod
    def get_category_product_counts() -> list[dict[str, Any]]:
        """Return category names with associated product counts.

        Returns:
            List of dicts: ``{'name': ..., 'product_count': ...}``.
        """
        return fetch_all(SQLQueries.CATEGORY_PRODUCT_COUNT)

    # ==========================================================================
    # Data integrity utilities
    # ==========================================================================

    @staticmethod
    def check_orphaned_records(table: str, foreign_key: str, parent_table: str) -> int:
        """Check for orphaned records where the foreign key doesn't exist in the parent.

        Args:
            table: The table to check (e.g., ``'products'``).
            foreign_key: The FK column name (e.g., ``'category_id'``).
            parent_table: The parent table (e.g., ``'categories'``).

        Returns:
            Count of orphaned records.
        """
        result = fetch_scalar(
            f"""SELECT COUNT(*) FROM {table} t
                WHERE t.{foreign_key} IS NOT NULL
                AND t.{foreign_key} NOT IN (SELECT {foreign_key} FROM {parent_table})""",
        )
        return result if result is not None else 0

    @staticmethod
    def verify_not_null(column: str, table: str, condition_column: str, condition_value: Any) -> tuple[bool, str]:
        """Verify that a specific column is NOT NULL for a given record.

        Args:
            column: Column name to check for NULL.
            table: Table name.
            condition_column: Column for the WHERE clause.
            condition_value: Value for the WHERE clause.

        Returns:
            Tuple of ``(is_not_null, message)``.
        """
        result = fetch_scalar(
            f"SELECT {column} FROM {table} WHERE {condition_column} = ?",
            (condition_value,),
        )
        if result is None:
            return False, f"Record not found: {table}.{condition_column} = {condition_value}"
        if result is None or (isinstance(result, str) and not result.strip()):
            return False, f"{table}.{column} is NULL or empty for {condition_column} = {condition_value}"
        return True, f"{table}.{column} is NOT NULL for {condition_column} = {condition_value}"

    # ==========================================================================
    # Aggregation utilities
    # ==========================================================================

    @staticmethod
    def get_top_selling_products(limit: int = 5) -> list[dict[str, Any]]:
        """Return the top-selling products by total quantity sold.

        Args:
            limit: Number of top products to return.

        Returns:
            List of dicts: ``{'name': ..., 'total_sold': ...}``.
        """
        return fetch_all(SQLQueries.REPORT_TOP_PRODUCTS, (limit,))

    @staticmethod
    def get_category_sales_report() -> list[dict[str, Any]]:
        """Return total sales grouped by category.

        Returns:
            List of dicts sorted by total_sales descending.
        """
        return fetch_all(SQLQueries.REPORT_CATEGORY_SALES)

    @staticmethod
    def get_daily_sales() -> list[dict[str, Any]]:
        """Return daily sales revenue.

        Returns:
            List of dicts: ``{'sale_date': ..., 'revenue': ...}``.
        """
        return fetch_all(SQLQueries.REPORT_DAILY_SALES)

    # ==========================================================================
    # Session utilities
    # ==========================================================================

    @staticmethod
    def is_session_expired(session_token: str) -> bool:
        """Check if a session token has expired.

        Args:
            session_token: The session token string.

        Returns:
            ``True`` if the session has expired, ``False`` otherwise.
        """
        from datetime import datetime

        row = fetch_scalar(
            "SELECT expires_at FROM user_sessions WHERE session_token = ?",
            (session_token,),
        )
        if row is None:
            return True
        expires = datetime.fromisoformat(row)
        return expires < datetime.now()

    # ==========================================================================
    # Coupon utilities
    # ==========================================================================

    @staticmethod
    def coupon_is_valid(code: str) -> tuple[bool, str]:
        """Comprehensive check whether a coupon is valid for use.

        Args:
            code: The coupon code.

        Returns:
            Tuple of ``(is_valid, reason)``. If valid, reason is empty.
        """
        coupon = fetch_scalar(SQLQueries.COUPON_BY_CODE, (code,))
        if coupon is None:
            return False, "Coupon code does not exist"

        from datetime import datetime

        active = fetch_scalar(SQLQueries.COUPON_IS_ACTIVE, (code,))
        if not active:
            return False, "Coupon is inactive"

        expiry = fetch_scalar(SQLQueries.COUPON_EXPIRY, (code,))
        if expiry:
            try:
                expiry_date = datetime.fromisoformat(expiry).date()
                if expiry_date < datetime.now().date():
                    return False, f"Coupon expired on {expiry}"
            except ValueError:
                pass

        max_uses = fetch_scalar(SQLQueries.COUPON_MAX_USES, (code,))
        usage_count = fetch_scalar(SQLQueries.COUPON_USAGE_COUNT, (code,))
        if max_uses is not None and (usage_count or 0) >= max_uses:
            return False, f"Coupon usage limit reached ({usage_count}/{max_uses})"

        return True, "Coupon is valid"
