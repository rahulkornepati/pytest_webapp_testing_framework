from __future__ import annotations

"""Database validation tests for the **Order Items** module.

Verifies line-item data within orders, pricing, quantities, and
product associations.
"""

import pytest

from database.db_helpers import DBHelpers
from database.db_queries import count, fetch_all, fetch_one, fetch_scalar
from database.database_utils import DatabaseUtils
from database.sql_constants import SQLQueries

pytestmark = [
    pytest.mark.database,
    pytest.mark.regression,
    pytest.mark.orders,
]


class TestOrderItemsDB:
    """Database-level validation of order items (line items)."""

    # ── Item existence ────────────────────────────────────────────────────────

    def test_verify_order_has_items(self) -> None:
        """Verify that an order has at least one line item."""
        items = fetch_all(SQLQueries.ORDER_ITEMS_BY_ORDER_ID, (1,))
        assert len(items) > 0, (
            f"Expected order 1 to have items, found {len(items)}"
        )

    def test_verify_order_item_count(self) -> None:
        """Verify the correct number of items in an order."""
        item_count = fetch_scalar(SQLQueries.ORDER_ITEM_COUNT_BY_ORDER, (1,))
        assert item_count == 2, (
            f"Expected 2 items in order 1, found {item_count}"
        )

    def test_verify_all_orders_have_items(self) -> None:
        """Verify that every order has at least one item."""
        empty_orders = fetch_scalar(
            """SELECT COUNT(*) FROM orders o
               LEFT JOIN order_items oi ON oi.order_id = o.order_id
               WHERE oi.order_item_id IS NULL"""
        )
        assert empty_orders == 0, (
            f"Expected 0 orders without items, found {empty_orders}"
        )

    # ── Pricing ───────────────────────────────────────────────────────────────

    def test_verify_unit_price_positive(self) -> None:
        """Verify that all order items have positive unit prices."""
        invalid_prices = fetch_scalar(
            "SELECT COUNT(*) FROM order_items WHERE unit_price <= 0"
        )
        assert invalid_prices == 0, (
            f"Expected 0 items with non-positive prices, found {invalid_prices}"
        )

    def test_verify_unit_price_matches_product_price(self) -> None:
        """Verify that the unit price in order_items matches the product price at time of order."""
        items = fetch_all(SQLQueries.ORDER_ITEMS_BY_ORDER_ID, (1,))
        for item in items:
            product_price = fetch_scalar(
                "SELECT price FROM products WHERE product_id = ?",
                (item["product_id"],),
            )
            assert item["unit_price"] == product_price, (
                f"Item {item['order_item_id']}: expected unit_price {product_price}, got {item['unit_price']}"
            )

    # ── Quantity validation ────────────────────────────────────────────────────

    def test_verify_quantity_positive(self) -> None:
        """Verify that all order items have positive quantities."""
        zero_qty = fetch_scalar(
            "SELECT COUNT(*) FROM order_items WHERE quantity <= 0"
        )
        assert zero_qty == 0, (
            f"Expected 0 items with non-positive quantities, found {zero_qty}"
        )

    def test_verify_quantity_reasonable(self) -> None:
        """Verify that item quantities are within a reasonable range."""
        excessive = fetch_scalar(
            "SELECT COUNT(*) FROM order_items WHERE quantity > 100"
        )
        assert excessive == 0, (
            f"Expected 0 items with quantity > 100, found {excessive}"
        )

    # ── Product linkage ───────────────────────────────────────────────────────

    def test_verify_item_product_exists(self) -> None:
        """Verify that every order item references an existing product."""
        invalid_products = fetch_scalar(
            """SELECT COUNT(*) FROM order_items oi
               LEFT JOIN products p ON p.product_id = oi.product_id
               WHERE p.product_id IS NULL"""
        )
        assert invalid_products == 0, (
            f"Expected 0 items with invalid product references, found {invalid_products}"
        )

    def test_verify_item_product_details(self) -> None:
        """Verify that order items can be retrieved with product names."""
        items = fetch_all(SQLQueries.ORDER_ITEM_PRODUCT_DETAILS, (1,))
        for item in items:
            assert "name" in item and item["name"], (
                f"Expected product name for order item: {item}"
            )

    # ── Total calculation ─────────────────────────────────────────────────────

    def test_verify_order_item_total_matches_order_total(self, db_utils: DatabaseUtils) -> None:
        """Verify that the sum of item totals matches the order total."""
        for order_id in range(1, 7):
            order_total = fetch_scalar(SQLQueries.ORDER_TOTAL, (order_id,))
            items_total = db_utils.calculate_order_total(order_id)
            assert abs(order_total - items_total) < 0.01, (
                f"Order {order_id}: expected total {order_total}, items sum {items_total}"
            )

    def test_verify_item_subtotal_calculation(self) -> None:
        """Verify individual item subtotal (quantity × unit_price)."""
        items = fetch_all(SQLQueries.ORDER_ITEMS_BY_ORDER_ID, (1,))
        for item in items:
            expected = item["quantity"] * item["unit_price"]
            assert expected > 0, (
                f"Expected positive subtotal for item {item['order_item_id']}"
            )

    # ── Data integrity ────────────────────────────────────────────────────────

    def test_verify_no_duplicate_order_items(self) -> None:
        """Verify that there are no duplicate (order_id, product_id) combinations."""
        duplicates = fetch_scalar(
            """SELECT COUNT(*) FROM (SELECT order_id, product_id, COUNT(*)
               FROM order_items GROUP BY order_id, product_id HAVING COUNT(*) > 1)"""
        )
        assert duplicates == 0, (
            f"Expected 0 duplicate order items, found {duplicates}"
        )

    def test_verify_item_count_across_orders(self) -> None:
        """Verify total number of order items across all orders."""
        total_items = fetch_scalar("SELECT COUNT(*) FROM order_items")
        assert total_items >= 10, (
            f"Expected at least 10 order items total, found {total_items}"
        )

    def test_verify_items_have_valid_foreign_keys(self) -> None:
        """Verify that all order items have valid order_id references."""
        orphaned = fetch_scalar(
            """SELECT COUNT(*) FROM order_items oi
               LEFT JOIN orders o ON o.order_id = oi.order_id
               WHERE o.order_id IS NULL"""
        )
        assert orphaned == 0, (
            f"Expected 0 orphaned order items, found {orphaned}"
        )
