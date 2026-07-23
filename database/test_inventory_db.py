from __future__ import annotations

"""Database validation tests for the **Inventory / Stock** module.

Verifies stock levels, reorder thresholds, warehouse locations,
and inventory data integrity.
"""

import pytest

from database.db_helpers import DBHelpers
from database.db_queries import count, fetch_all, fetch_one, fetch_scalar
from database.sql_constants import SQLQueries

pytestmark = [
    pytest.mark.database,
    pytest.mark.regression,
    pytest.mark.inventory,
]


class TestInventoryDB:
    """Database-level validation of inventory and stock data."""

    # ── Product-inventory linkage ─────────────────────────────────────────────

    def test_verify_inventory_record_exists(self) -> None:
        """Verify that inventory records exist for products."""
        total = fetch_scalar("SELECT COUNT(*) FROM inventory")
        assert total > 0, "Expected at least 1 inventory record"

    def test_verify_product_has_inventory(self) -> None:
        """Verify every product has exactly one inventory record."""
        products = fetch_scalar("SELECT COUNT(*) FROM products")
        inventory = fetch_scalar("SELECT COUNT(*) FROM inventory")
        assert products == inventory, (
            f"Expected {products} inventory records, found {inventory}"
        )

    def test_verify_inventory_by_product_name(self, db_helpers: DBHelpers) -> None:
        """Verify inventory can be looked up by product name."""
        qty = db_helpers.inventory_quantity("Sauce Labs Backpack")
        assert qty == 35, (
            f"Expected inventory quantity 35 for Sauce Labs Backpack, got {qty}"
        )

    # ── Stock levels ──────────────────────────────────────────────────────────

    def test_verify_stock_quantity_non_negative(self) -> None:
        """Verify that no inventory record has negative stock."""
        negative = fetch_scalar(SQLQueries.INVENTORY_NEGATIVE_QTY)
        assert negative == 0, (
            f"Expected 0 negative stock records, found {negative}"
        )

    def test_verify_out_of_stock_products_identified(self) -> None:
        """Verify that out-of-stock products are correctly identified."""
        out_of_stock = fetch_all(SQLQueries.INVENTORY_OUT_OF_STOCK)
        product_names = [row["name"] for row in out_of_stock]
        assert "Sauce Labs Phone Case" in product_names, (
            f"Expected 'Sauce Labs Phone Case' to be out of stock, got {product_names}"
        )

    def test_verify_low_stock_products_identified(self) -> None:
        """Verify that low-stock products are correctly identified.

        Low stock means quantity > 0 AND quantity <= reorder_level.
        The current test data has most products well-stocked; this test
        checks the logic works by verifying correct SQL filtering.
        """
        # Check that any product with qty <= reorder_level and qty > 0 is flagged
        low_stock = fetch_all(SQLQueries.INVENTORY_LOW_STOCK)
        # Verify each flagged product meets the criteria
        for item in low_stock:
            assert item["quantity"] <= (item.get("reorder_level", 10) or 10), (
                f"Product '{item['name']}' has qty {item['quantity']} but reorder level {item.get('reorder_level', 10)}"
            )
        # Verify that out-of-stock products are NOT included in low_stock
        zero_stock = fetch_scalar(
            "SELECT COUNT(*) FROM inventory WHERE quantity = 0"
        )
        for item in low_stock:
            assert item["quantity"] > 0, (
                f"Out-of-stock product '{item['name']}' should not appear in low stock"
            )

    # ── Reorder levels ────────────────────────────────────────────────────────

    def test_verify_reorder_levels_positive(self) -> None:
        """Verify that all reorder levels are positive integers."""
        invalid = fetch_scalar(
            "SELECT COUNT(*) FROM inventory WHERE reorder_level < 0"
        )
        assert invalid == 0, (
            f"Expected 0 records with negative reorder levels, found {invalid}"
        )

    def test_verify_reorder_needed_products(self) -> None:
        """Verify reorder-needed products are correctly identified."""
        reorder = fetch_all(SQLQueries.INVENTORY_REORDER_NEEDED)
        for item in reorder:
            assert item["quantity"] <= item["reorder_level"], (
                f"Product '{item['name']}' qty {item['quantity']} > reorder level {item['reorder_level']}"
            )

    def test_verify_stock_above_reorder_for_most_products(self) -> None:
        """Verify that most products have stock above reorder level."""
        total_products = fetch_scalar("SELECT COUNT(*) FROM inventory")
        reorder_needed = fetch_scalar(SQLQueries.INVENTORY_REORDER_NEEDED + " AND i.quantity > 0")
        above_reorder = total_products - (reorder_needed or 0)
        assert above_reorder > total_products / 2, (
            f"Expected most products above reorder level; only {above_reorder}/{total_products}"
        )

    # ── Warehouse / location ──────────────────────────────────────────────────

    def test_verify_warehouse_location_present(self) -> None:
        """Verify that all inventory records have a warehouse location."""
        no_location = fetch_scalar(
            "SELECT COUNT(*) FROM inventory WHERE location IS NULL OR location = ''"
        )
        assert no_location == 0, (
            f"Expected 0 records without location, found {no_location}"
        )

    def test_verify_inventory_sorted_by_product_name(self) -> None:
        """Verify that all inventory data can be retrieved sorted by product."""
        records = fetch_all(SQLQueries.INVENTORY_ALL)
        assert len(records) > 0, "Expected at least 1 inventory record"
        names = [r["name"] for r in records]
        assert names == sorted(names), (
            "Expected inventory records sorted alphabetically by product name"
        )

    # ── Stock count validation ────────────────────────────────────────────────

    def test_verify_total_stock_count_positive(self) -> None:
        """Verify the total stock across all products is positive."""
        total = fetch_scalar(SQLQueries.INVENTORY_TOTAL_STOCK)
        assert total is not None and total > 0, (
            f"Expected total stock > 0, got {total}"
        )

    def test_verify_zero_stock_products_exist(self) -> None:
        """Verify that at least one product has zero stock."""
        zero_stock = fetch_scalar(
            "SELECT COUNT(*) FROM inventory WHERE quantity = 0"
        )
        assert zero_stock >= 1, (
            f"Expected at least 1 product with zero stock, found {zero_stock}"
        )

    def test_verify_high_stock_products_exist(self) -> None:
        """Verify that high-stock products (quantity > 100) exist."""
        high_stock = fetch_scalar(
            "SELECT COUNT(*) FROM inventory WHERE quantity > 100"
        )
        assert high_stock >= 1, (
            f"Expected at least 1 product with stock > 100, found {high_stock}"
        )

    def test_verify_inventory_location_distribution(self) -> None:
        """Verify that inventory is distributed across multiple warehouses."""
        locations = fetch_scalar(
            "SELECT COUNT(DISTINCT SUBSTR(location, 1, INSTR(location, ',') - 1)) FROM inventory WHERE location IS NOT NULL"
        )
        assert locations >= 2, (
            f"Expected at least 2 warehouse locations, found {locations}"
        )
