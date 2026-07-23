from __future__ import annotations

"""Database validation tests for the **Checkout / Order Creation** module.

Verifies the checkout flow at the database level — cart-to-order
conversion, customer data integrity, and order lifecycle transitions.
"""

import pytest

from database.db_helpers import DBHelpers
from database.db_queries import count, fetch_all, fetch_one, fetch_scalar
from database.sql_constants import SQLQueries

pytestmark = [
    pytest.mark.database,
    pytest.mark.regression,
    pytest.mark.checkout,
]


class TestCheckoutDB:
    """Database-level validation of checkout and order creation."""

    # ── Checkout data availability ────────────────────────────────────────────

    def test_verify_user_has_cart_for_checkout(self, known_users: dict) -> None:
        """Verify that a user has an active cart before checkout."""
        cart = fetch_one(
            SQLQueries.CHECKOUT_USER_CART,
            (known_users["standard_user"]["user_id"],),
        )
        assert cart is not None, (
            "Expected 'standard_user' to have an active cart"
        )
        assert cart["status"] == "active", (
            f"Expected active cart, got status '{cart['status']}'"
        )

    def test_verify_cart_has_items(self, known_users: dict) -> None:
        """Verify that the cart has items before checkout."""
        user_id = known_users["standard_user"]["user_id"]
        cart = fetch_one(SQLQueries.CHECKOUT_USER_CART, (user_id,))
        assert cart is not None, "Expected active cart"
        item_count = fetch_scalar(
            SQLQueries.CHECKOUT_CART_ITEMS_COUNT,
            (cart["cart_id"],),
        )
        assert item_count > 0, (
            f"Expected cart {cart['cart_id']} to have items, found {item_count}"
        )

    # ── Order placement verification ──────────────────────────────────────────

    def test_verify_order_created_after_checkout(self, known_users: dict) -> None:
        """Verify that orders exist for users who have completed checkout."""
        user_id = known_users["admin_user"]["user_id"]
        recent_orders = fetch_scalar(
            "SELECT COUNT(*) FROM orders WHERE user_id = ? AND status != 'cancelled'",
            (user_id,),
        )
        assert recent_orders > 0, (
            f"Expected at least 1 active order for admin_user, found {recent_orders}"
        )

    def test_verify_order_has_correct_user(self, known_users: dict) -> None:
        """Verify that orders are correctly linked to the user who placed them."""
        user_id = known_users["standard_user"]["user_id"]
        orders = fetch_all(
            "SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,),
        )
        for order in orders:
            assert order["user_id"] == user_id, (
                f"Expected order user_id {user_id}, got {order['user_id']}"
            )

    # ── Order status validation ───────────────────────────────────────────────

    def test_verify_order_status_valid(self) -> None:
        """Verify all order statuses are from the allowed set."""
        valid_statuses = ("pending", "confirmed", "processing", "shipped", "delivered", "cancelled", "refunded")
        invalid = fetch_scalar(
            f"SELECT COUNT(*) FROM orders WHERE status NOT IN {valid_statuses}"
        )
        assert invalid == 0, (
            f"Expected 0 orders with invalid status, found {invalid}"
        )

    def test_verify_order_status_transitions(self) -> None:
        """Verify that delivered orders have completed payments."""
        delivered_payments = fetch_all(
            "SELECT o.order_id, o.total_amount, p.payment_status, p.payment_method "
            "FROM orders o "
            "JOIN payments p ON p.order_id = o.order_id "
            "WHERE o.status = 'delivered'"
        )
        for record in delivered_payments:
            assert record["payment_status"] == "completed", (
                f"Order {record['order_id']} is delivered but payment is {record['payment_status']}"
            )

    # ── Total validation ──────────────────────────────────────────────────────

    def test_verify_order_total_positive(self) -> None:
        """Verify all non-cancelled orders have positive totals."""
        zero_total = fetch_scalar(
            "SELECT COUNT(*) FROM orders WHERE total_amount <= 0 AND status NOT IN ('cancelled', 'refunded')"
        )
        assert zero_total == 0, (
            f"Expected 0 active orders with zero/negative total, found {zero_total}"
        )

    def test_verify_order_total_matches_items(self) -> None:
        """Verify that order#1 total matches its items (1×29.99 + 2×9.99 = 49.97)."""
        total = fetch_scalar(SQLQueries.ORDER_TOTAL, (1,))
        expected = 29.99 + (2 * 9.99)
        assert abs(total - expected) < 0.01, (
            f"Expected order 1 total {expected}, got {total}"
        )

    # ── Payment linkage ───────────────────────────────────────────────────────

    def test_verify_payment_linked_to_order(self) -> None:
        """Verify that every order has an associated payment record."""
        no_payment = fetch_scalar(
            "SELECT COUNT(*) FROM orders o LEFT JOIN payments p ON p.order_id = o.order_id WHERE p.payment_id IS NULL"
        )
        assert no_payment == 0, (
            f"Expected 0 orders without payments, found {no_payment}"
        )

    def test_verify_shipping_linked_to_order(self) -> None:
        """Verify that shipped/delivered orders have shipping info."""
        no_shipping = fetch_scalar(
            """SELECT COUNT(*) FROM orders o
               LEFT JOIN shipping s ON s.order_id = o.order_id
               WHERE o.status IN ('shipped', 'delivered', 'processing')
               AND s.shipping_id IS NULL"""
        )
        assert no_shipping == 0, (
            f"Expected 0 shipped orders without shipping records, found {no_shipping}"
        )

    # ── Discount validation ───────────────────────────────────────────────────

    def test_verify_order_discount_applied(self) -> None:
        """Verify that discount_amount is non-negative for all orders."""
        negative_discount = fetch_scalar(
            "SELECT COUNT(*) FROM orders WHERE discount_amount < 0"
        )
        assert negative_discount == 0, (
            f"Expected 0 orders with negative discount, found {negative_discount}"
        )

    def test_verify_coupon_reference_valid(self) -> None:
        """Verify that any coupon_id references in orders exist in the coupons table."""
        invalid_coupon = fetch_scalar(
            """SELECT COUNT(*) FROM orders
               WHERE coupon_id IS NOT NULL
               AND coupon_id NOT IN (SELECT coupon_id FROM coupons)"""
        )
        assert invalid_coupon == 0, (
            f"Expected 0 orders with invalid coupon references, found {invalid_coupon}"
        )

    # ── Timestamps ────────────────────────────────────────────────────────────

    def test_verify_order_timestamp_not_null(self) -> None:
        """Verify that every order has a created_at timestamp."""
        null_dates = fetch_scalar(
            "SELECT COUNT(*) FROM orders WHERE created_at IS NULL"
        )
        assert null_dates == 0, (
            f"Expected 0 orders with NULL created_at, found {null_dates}"
        )

    def test_verify_order_timestamps_are_recent(self) -> None:
        """Verify that orders have reasonable creation dates."""
        future_orders = fetch_scalar(
            "SELECT COUNT(*) FROM orders WHERE created_at > datetime('now', '+1 day')"
        )
        assert future_orders == 0, (
            f"Expected 0 orders with future created_at, found {future_orders}"
        )
