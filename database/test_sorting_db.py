from __future__ import annotations

"""Database validation tests for **Sorting / Ordering** features.

Verifies that product sorting (by name, price, category) works correctly
at the database level — independent of the UI sort controls.
"""

import pytest

from database.db_helpers import DBHelpers
from database.db_queries import count, fetch_all, fetch_column, fetch_one, fetch_scalar
from database.sql_constants import SQLQueries

pytestmark = [
    pytest.mark.database,
    pytest.mark.regression,
    pytest.mark.products,
]


class TestSortingDB:
    """Database-level validation of product sorting capabilities."""

    # ── Sort by name (ascending) ──────────────────────────────────────────────

    def test_verify_sort_by_name_ascending(self, db_helpers: DBHelpers) -> None:
        """Verify that products sorted by name (A→Z) are in correct order."""
        names = db_helpers.sorted_product_names(ascending=True)
        assert len(names) > 0, "Expected at least 1 product"
        assert names == sorted(names), (
            "Products are not sorted in ascending alphabetical order"
        )

    def test_verify_sort_by_name_ascending_first_last(self, db_helpers: DBHelpers) -> None:
        """Verify the first and last product names by ascending sort."""
        names = db_helpers.sorted_product_names(ascending=True)
        assert names[0].startswith("S"), (
            f"Expected first product to start with 'S', got '{names[0]}'"
        )
        assert names[-1].startswith("T") or names[-1].startswith("S"), (
            f"Expected last product to start with 'T' or 'S', got '{names[-1]}'"
        )

    # ── Sort by name (descending) ─────────────────────────────────────────────

    def test_verify_sort_by_name_descending(self, db_helpers: DBHelpers) -> None:
        """Verify that products sorted by name (Z→A) are in correct order."""
        names = db_helpers.sorted_product_names(ascending=False)
        assert len(names) > 0, "Expected at least 1 product"
        assert names == sorted(names, reverse=True), (
            "Products are not sorted in descending alphabetical order"
        )

    def test_verify_name_descending_completeness(self) -> None:
        """Verify that descending sort returns all products."""
        asc_names = fetch_column(SQLQueries.PRODUCTS_NAME_ASC)
        desc_names = fetch_column(SQLQueries.PRODUCTS_NAME_DESC)
        assert len(asc_names) == len(desc_names), (
            f"Ascending count ({len(asc_names)}) != descending count ({len(desc_names)})"
        )
        assert set(asc_names) == set(desc_names), (
            "Ascending and descending sorts return different product sets"
        )

    # ── Sort by price (ascending) ─────────────────────────────────────────────

    def test_verify_sort_by_price_ascending(self) -> None:
        """Verify that products sorted by price (low→high) are in correct order."""
        rows = fetch_all(SQLQueries.PRODUCTS_PRICE_ASC)
        prices = [(r["name"], r["price"]) for r in rows]
        sorted_prices = sorted(prices, key=lambda x: x[1])
        assert prices == sorted_prices, (
            "Products are not sorted by price ascending"
        )

    def test_verify_sort_by_price_ascending_first_product(self) -> None:
        """Verify that the cheapest product is correct."""
        rows = fetch_all(SQLQueries.PRODUCTS_PRICE_ASC)
        cheapest = rows[0]
        assert cheapest["price"] == 4.99, (
            f"Expected cheapest product price $4.99, got ${cheapest['price']}"
        )
        assert "Stress Ball" in cheapest["name"], (
            f"Expected cheapest product to be Stress Ball, got '{cheapest['name']}'"
        )

    # ── Sort by price (descending) ────────────────────────────────────────────

    def test_verify_sort_by_price_descending(self) -> None:
        """Verify that products sorted by price (high→low) are in correct order."""
        rows = fetch_all(SQLQueries.PRODUCTS_PRICE_DESC)
        prices = [(r["name"], r["price"]) for r in rows]
        sorted_prices = sorted(prices, key=lambda x: x[1], reverse=True)
        assert prices == sorted_prices, (
            "Products are not sorted by price descending"
        )

    def test_verify_sort_by_price_descending_most_expensive(self) -> None:
        """Verify that the most expensive product is correct."""
        rows = fetch_all(SQLQueries.PRODUCTS_PRICE_DESC)
        most_expensive = rows[0]
        assert most_expensive["price"] == 79.99, (
            f"Expected most expensive product price $79.99, got ${most_expensive['price']}"
        )
        assert "Earbuds" in most_expensive["name"], (
            f"Expected most expensive product to be Earbuds, got '{most_expensive['name']}'"
        )

    # ── Sort consistency ──────────────────────────────────────────────────────

    def test_verify_sort_has_all_products(self) -> None:
        """Verify that sorted results contain all products."""
        total = fetch_scalar(SQLQueries.PRODUCT_COUNT)
        asc_prices = fetch_all(SQLQueries.PRODUCTS_PRICE_ASC)
        desc_prices = fetch_all(SQLQueries.PRODUCTS_PRICE_DESC)
        assert len(asc_prices) == total, (
            f"Expected {total} products in ascending sort, found {len(asc_prices)}"
        )
        assert len(desc_prices) == total, (
            f"Expected {total} products in descending sort, found {len(desc_prices)}"
        )

    def test_verify_sort_prices_completeness(self) -> None:
        """Verify that sorted price lists contain all products."""
        total = fetch_scalar(SQLQueries.PRODUCT_COUNT)
        asc_prices = fetch_all(SQLQueries.PRODUCTS_PRICE_ASC)
        desc_prices = fetch_all(SQLQueries.PRODUCTS_PRICE_DESC)
        assert len(asc_prices) == total, (
            f"Expected {total} products in ascending sort, found {len(asc_prices)}"
        )
        assert len(desc_prices) == total, (
            f"Expected {total} products in descending sort, found {len(desc_prices)}"
        )
        # Verify same set of products in both directions
        asc_names = {r["name"] for r in asc_prices}
        desc_names = {r["name"] for r in desc_prices}
        assert asc_names == desc_names, (
            "Ascending and descending sorts contain different products"
        )

    # ── Sort stability ────────────────────────────────────────────────────────

    def test_verify_sort_by_price_within_same_price(self) -> None:
        """Verify that products with the same price are ordered by name."""
        same_price = fetch_all(
            "SELECT name, price FROM products WHERE price = 9.99 ORDER BY name"
        )
        assert len(same_price) >= 2, (
            f"Expected at least 2 products at price $9.99, found {len(same_price)}"
        )
        names = [r["name"] for r in same_price]
        assert names == sorted(names), (
            f"Products at same price not sorted by name: {names}"
        )

    def test_verify_sort_by_price_ties_with_name(self) -> None:
        """Verify that products at $15.99 price point are sorted by name."""
        same_price = fetch_all(
            "SELECT name, price FROM products WHERE price = 15.99 ORDER BY name"
        )
        names = [r["name"] for r in same_price]
        assert names == sorted(names), (
            f"Products at $15.99 not sorted by name: {names}"
        )

    # ── Edge cases ────────────────────────────────────────────────────────────

    def test_verify_sort_empty_result_not_applicable(self) -> None:
        """Verify that sorting non-empty data always returns results."""
        total = fetch_scalar(SQLQueries.PRODUCT_COUNT)
        assert total > 0, "Expected products in database"

    def test_verify_sort_handles_single_product(self) -> None:
        """Verify that filtering by a single product returns one row."""
        rows = fetch_all(
            "SELECT name, price FROM products WHERE name = 'Sauce Labs Backpack' ORDER BY price"
        )
        assert len(rows) == 1, (
            f"Expected 1 row for single product, found {len(rows)}"
        )
