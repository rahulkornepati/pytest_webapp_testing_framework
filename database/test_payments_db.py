from __future__ import annotations

"""Database validation tests for the **Payments** module.

Verifies payment records, statuses, methods, amounts, and
payment-related business rules at the database level.
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


class TestPaymentsDB:
    """Database-level validation of payment records."""

    # ── Payment existence ─────────────────────────────────────────────────────

    def test_verify_payment_exists_for_order(self) -> None:
        """Verify that a payment exists for a known order."""
        payment = fetch_one(SQLQueries.PAYMENT_BY_ORDER_ID, (1,))
        assert payment is not None, "Expected payment for order 1"

    def test_verify_payment_by_id(self) -> None:
        """Verify that a payment can be retrieved by its ID."""
        payment = fetch_one(SQLQueries.PAYMENT_BY_ID, (1,))
        assert payment is not None, "Expected payment with ID 1"
        assert payment["payment_id"] == 1

    def test_verify_all_orders_have_payments(self) -> None:
        """Verify that every order has an associated payment record."""
        no_payment = fetch_scalar(
            "SELECT COUNT(*) FROM orders o LEFT JOIN payments p ON p.order_id = o.order_id WHERE p.payment_id IS NULL"
        )
        assert no_payment == 0, (
            f"Expected 0 orders without payments, found {no_payment}"
        )

    # ── Payment status ────────────────────────────────────────────────────────

    def test_verify_payment_status(self, db_helpers: DBHelpers) -> None:
        """Verify that a delivered order has payment status 'completed'."""
        status = db_helpers.payment_status(1)
        assert status == "completed", (
            f"Expected payment status 'completed' for order 1, got '{status}'"
        )

    def test_verify_pending_order_has_pending_payment(self, db_helpers: DBHelpers) -> None:
        """Verify that a pending order has payment status 'pending'."""
        status = db_helpers.payment_status(4)
        assert status == "pending", (
            f"Expected payment status 'pending' for order 4, got '{status}'"
        )

    def test_verify_payment_status_valid_values(self) -> None:
        """Verify all payment statuses are from the allowed set."""
        valid_statuses = ("pending", "completed", "failed", "refunded")
        invalid = fetch_scalar(
            f"SELECT COUNT(*) FROM payments WHERE payment_status NOT IN {valid_statuses}"
        )
        assert invalid == 0, (
            f"Expected 0 payments with invalid status, found {invalid}"
        )

    # ── Payment method ────────────────────────────────────────────────────────

    def test_verify_payment_method(self, db_helpers: DBHelpers) -> None:
        """Verify that payments have a payment method recorded."""
        method = db_helpers.payment_method(1)
        assert method is not None and len(method) > 0, (
            f"Expected non-empty payment method, got '{method}'"
        )

    def test_verify_all_payments_have_method(self) -> None:
        """Verify that every payment has a payment method."""
        no_method = fetch_scalar(
            "SELECT COUNT(*) FROM payments WHERE payment_method IS NULL OR payment_method = ''"
        )
        assert no_method == 0, (
            f"Expected 0 payments without method, found {no_method}"
        )

    # ── Payment amount ────────────────────────────────────────────────────────

    def test_verify_payment_amount(self, db_helpers: DBHelpers) -> None:
        """Verify that the payment amount matches the order total."""
        amount = db_helpers.payment_amount(1)
        expected = 49.97
        assert abs(amount - expected) < 0.01, (
            f"Expected payment amount {expected} for order 1, got {amount}"
        )

    def test_verify_payment_amount_positive(self) -> None:
        """Verify that all payment amounts are positive."""
        negative = fetch_scalar(
            "SELECT COUNT(*) FROM payments WHERE amount <= 0"
        )
        assert negative == 0, (
            f"Expected 0 payments with non-positive amount, found {negative}"
        )

    def test_verify_payment_amount_matches_order_total(self) -> None:
        """Verify that every payment amount matches its order total."""
        mismatches = fetch_all(
            """SELECT p.payment_id, p.order_id, p.amount AS payment_amount, o.total_amount
               FROM payments p JOIN orders o ON o.order_id = p.order_id
               WHERE ABS(p.amount - o.total_amount) > 0.01"""
        )
        assert len(mismatches) == 0, (
            f"Expected 0 payment/order amount mismatches, found {len(mismatches)}: {mismatches}"
        )

    # ── Payment timing ────────────────────────────────────────────────────────

    def test_verify_completed_payment_has_paid_at(self) -> None:
        """Verify that completed payments have a paid_at timestamp."""
        null_paid_at = fetch_scalar(
            "SELECT COUNT(*) FROM payments WHERE payment_status = 'completed' AND paid_at IS NULL"
        )
        assert null_paid_at == 0, (
            f"Expected 0 completed payments without paid_at, found {null_paid_at}"
        )

    def test_verify_pending_payment_has_no_paid_at(self) -> None:
        """Verify that pending payments have NULL paid_at."""
        paid_pending = fetch_scalar(
            "SELECT COUNT(*) FROM payments WHERE payment_status = 'pending' AND paid_at IS NOT NULL"
        )
        assert paid_pending == 0, (
            f"Expected 0 pending payments with paid_at, found {paid_pending}"
        )

    # ── Revenue / aggregation ─────────────────────────────────────────────────

    def test_verify_total_revenue_positive(self, db_helpers: DBHelpers) -> None:
        """Verify that total revenue from completed payments is positive."""
        revenue = db_helpers.total_revenue()
        assert revenue > 0, (
            f"Expected positive revenue, got {revenue}"
        )

    def test_verify_payment_status_counts(self) -> None:
        """Verify the distribution of payment statuses."""
        status_counts = fetch_all(SQLQueries.PAYMENT_COUNT_BY_STATUS)
        status_map = {r["payment_status"]: r["count"] for r in status_counts}
        assert status_map.get("completed", 0) >= 4, (
            f"Expected at least 4 completed payments, found {status_map.get('completed', 0)}"
        )
        assert status_map.get("pending", 0) >= 1, (
            f"Expected at least 1 pending payment, found {status_map.get('pending', 0)}"
        )
        assert status_map.get("refunded", 0) >= 1, (
            f"Expected at least 1 refunded payment, found {status_map.get('refunded', 0)}"
        )

    # ── Transaction IDs ──────────────────────────────────────────────────────

    def test_verify_transaction_id_optional(self) -> None:
        """Verify that transaction_id is optional (can be NULL)."""
        has_transaction = fetch_scalar(
            "SELECT COUNT(*) FROM payments WHERE transaction_id IS NOT NULL"
        )
        no_transaction = fetch_scalar(
            "SELECT COUNT(*) FROM payments WHERE transaction_id IS NULL"
        )
        assert no_transaction >= 1, (
            "Expected at least 1 payment without transaction_id"
        )

    def test_verify_payment_created_at_not_null(self) -> None:
        """Verify that all payments have created_at."""
        null_dates = fetch_scalar(
            "SELECT COUNT(*) FROM payments WHERE created_at IS NULL"
        )
        assert null_dates == 0, (
            f"Expected 0 payments with NULL created_at, found {null_dates}"
        )
