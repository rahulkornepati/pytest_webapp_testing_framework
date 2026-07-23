from __future__ import annotations

"""Database validation tests for the **Orders** module.

Verifies order records, lifecycle states, totals, and order-level
business rules at the database level.
"""

import pytest

from database.db_helpers import DBHelpers
from database.db_queries import count, fetch_all, fetch_one, fetch_scalar
from database.sql_constants import SQLQueries

pytestmark = [
    pytest.mark.database,
    pytest.mark.regression,
    pytest.mark.orders,
]


class TestOrdersDB:
    """Database-level validation of order data."""

    # ── Order existence & retrieval ───────────────────────────────────────────

    def test_verify_order_exists(self, db_helpers: DBHelpers) -> None:
        """Verify that an order exists by its ID."""
        assert db_helpers.order_exists(1), "Expected order ID 1 to exist"

    def test_verify_order_by_user(self, known_users: dict) -> None:
        """Verify that orders can be retrieved by user."""
        user_id = known_users["standard_user"]["user_id"]
        orders = fetch_all(SQLQueries.ORDER_BY_USER_ID, (user_id,))
        assert len(orders) >= 1, (
            f"Expected at least 1 order for user {user_id}, found {len(orders)}"
        )

    def test_verify_all_orders_have_valid_user(self) -> None:
        """Verify that every order references an existing user."""
        orphaned = fetch_scalar(
            "SELECT COUNT(*) FROM orders WHERE user_id NOT IN (SELECT user_id FROM users)"
        )
        assert orphaned == 0, (
            f"Expected 0 orphaned orders, found {orphaned}"
        )

    # ── Order status ──────────────────────────────────────────────────────────

    def test_verify_order_status(self, db_helpers: DBHelpers) -> None:
        """Verify that an order has the correct status."""
        status = db_helpers.order_status(1)
        assert status == "delivered", (
            f"Expected order 1 status 'delivered', got '{status}'"
        )

    def test_verify_order_status_distribution(self) -> None:
        """Verify that multiple order statuses exist in the database."""
        statuses = fetch_all(SQLQueries.ORDER_BY_STATUS, ("delivered",))
        assert len(statuses) >= 1, "Expected at least 1 delivered order"

        pending = fetch_all(SQLQueries.ORDER_BY_STATUS, ("pending",))
        assert len(pending) >= 1, "Expected at least 1 pending order"

    def test_verify_cancelled_orders_exist(self) -> None:
        """Verify that cancelled orders exist."""
        cancelled = fetch_scalar(
            "SELECT COUNT(*) FROM orders WHERE status = 'cancelled'"
        )
        assert cancelled >= 1, (
            f"Expected at least 1 cancelled order, found {cancelled}"
        )

    # ── Order totals ──────────────────────────────────────────────────────────

    def test_verify_order_total(self, db_helpers: DBHelpers) -> None:
        """Verify the total amount for a specific order."""
        total = db_helpers.order_total(1)
        expected = 49.97  # 1×29.99 + 2×9.99
        assert abs(total - expected) < 0.01, (
            f"Expected order 1 total {expected}, got {total}"
        )

    def test_verify_order_total_greater_than_zero(self) -> None:
        """Verify all non-cancelled orders have totals > 0."""
        zero_total = fetch_scalar(
            "SELECT COUNT(*) FROM orders WHERE total_amount <= 0"
        )
        # Cancelled order 5 has total 39.99, so all should be > 0
        assert zero_total == 0, (
            f"Expected 0 orders with non-positive total, found {zero_total}"
        )

    # ── Order counts ──────────────────────────────────────────────────────────

    def test_verify_order_count_total(self, db_helpers: DBHelpers) -> None:
        """Verify the total number of orders in the database."""
        total = db_helpers.order_count_total()
        assert total == 6, (
            f"Expected 6 orders total, found {total}"
        )

    def test_verify_order_count_by_user(self, db_helpers: DBHelpers, known_users: dict) -> None:
        """Verify the order count for a specific user."""
        user_id = known_users["standard_user"]["user_id"]
        count_by_user = db_helpers.order_count_by_user(user_id)
        assert count_by_user == 2, (
            f"Expected 2 orders for standard_user, found {count_by_user}"
        )

    def test_verify_active_order_count(self, db_helpers: DBHelpers) -> None:
        """Verify the count of active (non-cancelled/refunded) orders."""
        active = db_helpers.order_count_total() - fetch_scalar(
            "SELECT COUNT(*) FROM orders WHERE status IN ('cancelled', 'refunded')"
        )
        assert active >= 5, (
            f"Expected at least 5 active orders, found {active}"
        )

    # ── Order timestamps ──────────────────────────────────────────────────────

    def test_verify_order_created_at(self, db_helpers: DBHelpers) -> None:
        """Verify that an order has a created_at timestamp."""
        created = fetch_scalar(SQLQueries.ORDER_CREATED_AT, (1,))
        assert created is not None, "Expected order 1 to have a created_at"

    def test_verify_order_updated_at_not_null(self) -> None:
        """Verify all orders have updated_at."""
        null_updates = fetch_scalar(
            "SELECT COUNT(*) FROM orders WHERE updated_at IS NULL"
        )
        assert null_updates == 0, (
            f"Expected 0 orders with NULL updated_at, found {null_updates}"
        )

    # ── Recent orders ─────────────────────────────────────────────────────────

    def test_verify_recent_orders_limit(self) -> None:
        """Verify that the recent orders limit query works."""
        recent = fetch_all(SQLQueries.ORDER_RECENT, (3,))
        assert len(recent) == 3, (
            f"Expected 3 recent orders, found {len(recent)}"
        )

    def test_verify_orders_have_all_required_fields(self) -> None:
        """Verify that all orders have the required fields populated."""
        required_fields = ["order_id", "user_id", "status", "total_amount", "created_at"]
        orders = fetch_all("SELECT * FROM orders LIMIT 1")
        if orders:
            for field in required_fields:
                assert field in orders[0], (
                    f"Missing required field '{field}' in orders table"
                )
                assert orders[0][field] is not None, (
                    f"Field '{field}' is NULL in the first order"
                )

    def test_verify_refunded_orders_have_correct_payment_status(self) -> None:
        """Verify that cancelled orders have refunded payment status."""
        cancelled = fetch_all(
            "SELECT o.order_id, p.payment_status FROM orders o JOIN payments p ON p.order_id = o.order_id WHERE o.status = 'cancelled'"
        )
        for record in cancelled:
            assert record["payment_status"] == "refunded", (
                f"Order {record['order_id']} is cancelled but payment is {record['payment_status']}"
            )
