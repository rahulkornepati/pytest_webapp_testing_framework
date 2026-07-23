from __future__ import annotations

"""Database validation tests for the **Products** module.

Verifies product data integrity, pricing, descriptions, category
mappings, and business rules at the database level.
"""

import pytest

from database.db_helpers import DBHelpers
from database.db_queries import count, fetch_all, fetch_one, fetch_scalar
from database.database_utils import DatabaseUtils
from database.sql_constants import SQLQueries

pytestmark = [
    pytest.mark.database,
    pytest.mark.regression,
    pytest.mark.products,
]


class TestProductsDB:
    """Database-level validation of product catalogue data."""

    # ── Existence & identity ──────────────────────────────────────────────────

    def test_verify_product_exists(self, db_helpers: DBHelpers) -> None:
        """Verify that a known product exists in the database."""
        assert db_helpers.product_exists("Sauce Labs Backpack"), (
            "Expected 'Sauce Labs Backpack' to exist in the products table"
        )

    def test_verify_product_price(self, db_helpers: DBHelpers) -> None:
        """Verify that a product has the expected price."""
        actual = db_helpers.product_price("Sauce Labs Backpack")
        expected = 29.99
        assert actual == expected, (
            f"Expected price {expected} for 'Sauce Labs Backpack', got {actual}"
        )

    def test_verify_product_description(self, db_helpers: DBHelpers) -> None:
        """Verify that a product has a non-empty description."""
        description = db_helpers.product_description("Sauce Labs Backpack")
        assert description and len(description) > 20, (
            f"Expected a meaningful description, got '{description}'"
        )

    # ── Category mapping ──────────────────────────────────────────────────────

    def test_verify_category_mapping(self, db_helpers: DBHelpers) -> None:
        """Verify that a product is mapped to the correct category."""
        cat_id = db_helpers.product_category_id("Sauce Labs Backpack")
        category_name = fetch_scalar(
            "SELECT name FROM categories WHERE category_id = ?",
            (cat_id,),
        )
        assert category_name is not None, (
            f"Category not found for category_id {cat_id}"
        )

    def test_verify_all_products_have_valid_category(self) -> None:
        """Verify every product has a valid category reference."""
        orphaned = fetch_scalar(
            "SELECT COUNT(*) FROM products WHERE category_id NOT IN (SELECT category_id FROM categories)"
        )
        assert orphaned == 0, (
            f"Expected 0 orphaned products, found {orphaned}"
        )

    # ── Active product checks ──────────────────────────────────────────────────

    def test_verify_active_products(self, db_helpers: DBHelpers) -> None:
        """Verify that most products are active."""
        active_count = db_helpers.active_product_count()
        total_count = db_helpers.product_count()
        assert active_count == total_count, (
            f"Expected {total_count} active products, found {active_count}"
        )

    def test_verify_duplicate_products(self) -> None:
        """Verify that no duplicate product names exist."""
        total = fetch_scalar("SELECT COUNT(*) FROM products")
        distinct = fetch_scalar("SELECT COUNT(DISTINCT name) FROM products")
        assert total == distinct, (
            f"Expected unique product names: {total} vs {distinct} distinct"
        )

    # ── Price validation ──────────────────────────────────────────────────────

    def test_verify_price_not_negative(self, db_helpers: DBHelpers) -> None:
        """Verify that no products have negative prices."""
        assert db_helpers.negative_price_count() == 0, (
            "Expected 0 products with negative prices"
        )

    def test_verify_all_prices_above_zero(self) -> None:
        """Verify that all active products have a price > 0."""
        free_products = fetch_scalar(
            "SELECT COUNT(*) FROM products WHERE price <= 0 AND is_active = 1"
        )
        assert free_products == 0, (
            f"Expected 0 active products with price <= 0, found {free_products}"
        )

    def test_verify_price_within_reasonable_range(self) -> None:
        """Verify that product prices are within a reasonable range."""
        max_price = fetch_scalar("SELECT MAX(price) FROM products")
        assert max_price <= 500, (
            f"Expected max product price <= 500, got {max_price}"
        )

    # ── Inventory link ─────────────────────────────────────────────────────────

    def test_verify_inventory_link(self, db_helpers: DBHelpers) -> None:
        """Verify that every product has an inventory record."""
        missing_inventory = fetch_scalar(
            "SELECT COUNT(*) FROM products p LEFT JOIN inventory i ON i.product_id = p.product_id WHERE i.inventory_id IS NULL"
        )
        assert missing_inventory == 0, (
            f"Expected 0 products without inventory records, found {missing_inventory}"
        )

    def test_verify_inventory_quantity_for_product(self, db_helpers: DBHelpers) -> None:
        """Verify inventory quantity for a specific product."""
        qty = db_helpers.inventory_quantity("Sauce Labs Backpack")
        assert qty > 0, (
            f"Expected positive inventory for Sauce Labs Backpack, got {qty}"
        )

    # ── Counting & listing ────────────────────────────────────────────────────

    def test_verify_product_count(self, db_helpers: DBHelpers) -> None:
        """Verify the total product count is greater than zero."""
        total = db_helpers.product_count()
        assert total > 0, "Expected at least 1 product in the database"
        assert total == 24, (
            f"Expected 24 products, found {total}"
        )

    def test_verify_product_images(self) -> None:
        """Verify that products have image URLs."""
        no_images = fetch_scalar(
            "SELECT COUNT(*) FROM products WHERE image_url IS NULL OR image_url = ''"
        )
        assert no_images == 0, (
            f"Expected 0 products without images, found {no_images}"
        )

    def test_verify_product_names_are_unique(self) -> None:
        """Verify product names are unique (case-insensitive check)."""
        duplicates = fetch_scalar(
            "SELECT COUNT(*) FROM (SELECT LOWER(name) AS name FROM products GROUP BY LOWER(name) HAVING COUNT(*) > 1)"
        )
        assert duplicates == 0, (
            f"Expected 0 case-insensitive duplicate product names, found {duplicates}"
        )

    def test_verify_all_product_names_non_empty(self) -> None:
        """Verify no products have empty or whitespace-only names."""
        empty_names = fetch_scalar(
            "SELECT COUNT(*) FROM products WHERE name IS NULL OR TRIM(name) = ''"
        )
        assert empty_names == 0, (
            f"Expected 0 products with empty names, found {empty_names}"
        )
