from __future__ import annotations

"""Database validation tests for the **Coupons / Discounts** module.

Verifies coupon codes, discount percentages, usage tracking,
expiry dates, and discount-related business rules.
"""

import pytest

from database.db_helpers import DBHelpers
from database.db_queries import count, fetch_all, fetch_one, fetch_scalar
from database.database_utils import DatabaseUtils
from database.sql_constants import SQLQueries

pytestmark = [
    pytest.mark.database,
    pytest.mark.regression,
    pytest.mark.checkout,
]


class TestCouponsDB:
    """Database-level validation of coupon / discount data."""

    # ── Coupon existence ──────────────────────────────────────────────────────

    def test_verify_coupon_exists(self, db_helpers: DBHelpers) -> None:
        """Verify that a coupon code exists in the database."""
        assert db_helpers.coupon_exists("WELCOME10"), (
            "Expected coupon code 'WELCOME10' to exist"
        )

    def test_verify_coupon_not_exists(self, db_helpers: DBHelpers) -> None:
        """Verify that a non-existent coupon code returns False."""
        assert not db_helpers.coupon_exists("NONEXISTENT"), (
            "Expected 'NONEXISTENT' coupon to not exist"
        )

    # ── Coupon activity status ────────────────────────────────────────────────

    def test_verify_coupon_active(self, db_helpers: DBHelpers) -> None:
        """Verify that an active coupon is correctly marked."""
        assert db_helpers.coupon_is_active("WELCOME10"), (
            "Expected coupon 'WELCOME10' to be active"
        )

    def test_verify_coupon_inactive(self, db_helpers: DBHelpers) -> None:
        """Verify that an inactive coupon is correctly marked."""
        assert not db_helpers.coupon_is_active("MAXEDOUT"), (
            "Expected coupon 'MAXEDOUT' to be inactive"
        )

    def test_verify_expired_coupon_detected(self, db_helpers: DBHelpers, db_utils: DatabaseUtils) -> None:
        """Verify that an expired coupon is correctly detected."""
        assert db_helpers.coupon_exists("EXPIRED10"), (
            "Expected 'EXPIRED10' to exist"
        )
        is_valid, reason = db_utils.coupon_is_valid("EXPIRED10")
        assert not is_valid, (
            f"Expected 'EXPIRED10' to be invalid, got: {reason}"
        )
        assert "expired" in reason.lower() or "inactive" in reason.lower(), (
            f"Expected expiry-related rejection message, got: {reason}"
        )

    # ── Discount validation ───────────────────────────────────────────────────

    def test_verify_discount_percent(self, db_helpers: DBHelpers) -> None:
        """Verify that a coupon has the expected discount percentage."""
        discount = db_helpers.coupon_discount("WELCOME10")
        assert discount == 10, (
            f"Expected discount 10% for 'WELCOME10', got {discount}%"
        )

    def test_verify_discount_percent_range(self) -> None:
        """Verify that all discount percentages are between 0 and 100."""
        invalid = fetch_scalar(
            "SELECT COUNT(*) FROM coupons WHERE discount_percent < 0 OR discount_percent > 100"
        )
        assert invalid == 0, (
            f"Expected 0 coupons with invalid discount percent, found {invalid}"
        )

    def test_verify_discount_50_percent_coupon(self, db_helpers: DBHelpers) -> None:
        """Verify that HALFOFF coupon has 50% discount."""
        discount = db_helpers.coupon_discount("HALFOFF")
        assert discount == 50, (
            f"Expected discount 50% for 'HALFOFF', got {discount}%"
        )

    # ── Minimum order amount ──────────────────────────────────────────────────

    def test_verify_min_order_amount(self) -> None:
        """Verify that coupons with min order amount have it recorded."""
        coupons_with_min = fetch_all(
            "SELECT code, min_order_amount FROM coupons WHERE min_order_amount > 0"
        )
        assert len(coupons_with_min) >= 3, (
            f"Expected at least 3 coupons with min_order_amount, found {len(coupons_with_min)}"
        )

    def test_verify_min_order_amount_non_negative(self) -> None:
        """Verify that all min_order_amount values are non-negative."""
        negative = fetch_scalar(
            "SELECT COUNT(*) FROM coupons WHERE min_order_amount < 0"
        )
        assert negative == 0, (
            f"Expected 0 coupons with negative min_order_amount, found {negative}"
        )

    # ── Usage tracking ────────────────────────────────────────────────────────

    def test_verify_usage_count(self, db_helpers: DBHelpers) -> None:
        """Verify that a coupon's usage count is tracked."""
        usage = db_helpers.coupon_usage_count("WELCOME10")
        assert usage >= 0, (
            f"Expected non-negative usage count, got {usage}"
        )

    def test_verify_max_uses_enforcement(self) -> None:
        """Verify that a coupon with max_uses reached is correctly marked."""
        usage = fetch_scalar(SQLQueries.COUPON_USAGE_COUNT, ("MAXEDOUT",))
        max_uses = fetch_scalar(SQLQueries.COUPON_MAX_USES, ("MAXEDOUT",))
        assert max_uses is not None and usage >= max_uses, (
            f"Coupon 'MAXEDOUT' usage {usage} < max_uses {max_uses}"
        )

    # ── Expiry dates ──────────────────────────────────────────────────────────

    def test_verify_coupon_expiry_date(self) -> None:
        """Verify that coupons with future expiry dates are active."""
        active_future = fetch_all(SQLQueries.COUPON_ALL_ACTIVE)
        active_codes = [r["code"] for r in active_future]
        assert "WELCOME10" in active_codes, (
            f"Expected 'WELCOME10' in active coupons, got {active_codes}"
        )

    def test_verify_expired_coupons_exist(self) -> None:
        """Verify that expired coupons exist in the database."""
        expired = fetch_all(SQLQueries.COUPON_EXPIRED)
        expired_codes = [r["code"] for r in expired]
        assert "EXPIRED10" in expired_codes, (
            f"Expected 'EXPIRED10' in expired coupons, got {expired_codes}"
        )

    # ── Coupon validity (utility) ─────────────────────────────────────────────

    def test_verify_coupon_validity_valid(self, db_utils: DatabaseUtils) -> None:
        """Verify that a valid coupon passes all checks."""
        is_valid, reason = db_utils.coupon_is_valid("WELCOME10")
        assert is_valid, (
            f"Expected 'WELCOME10' to be valid, got: {reason}"
        )

    def test_verify_coupon_validity_expired(self, db_utils: DatabaseUtils) -> None:
        """Verify that an expired coupon fails validity checks."""
        is_valid, reason = db_utils.coupon_is_valid("EXPIRED10")
        assert not is_valid, (
            "Expected 'EXPIRED10' to be invalid"
        )

    def test_verify_coupon_validity_inactive(self, db_utils: DatabaseUtils) -> None:
        """Verify that an inactive coupon fails validity checks."""
        is_valid, reason = db_utils.coupon_is_valid("MAXEDOUT")
        assert not is_valid, (
            "Expected 'MAXEDOUT' to be invalid"
        )

    def test_verify_coupon_validity_non_existent(self, db_utils: DatabaseUtils) -> None:
        """Verify that a non-existent coupon fails validity checks."""
        is_valid, reason = db_utils.coupon_is_valid("DOESNOTEXIST")
        assert not is_valid, (
            "Expected 'DOESNOTEXIST' to be invalid"
        )

    # ── Data integrity ────────────────────────────────────────────────────────

    def test_verify_coupon_code_unique(self) -> None:
        """Verify that all coupon codes are unique."""
        total = fetch_scalar("SELECT COUNT(*) FROM coupons")
        distinct = fetch_scalar("SELECT COUNT(DISTINCT code) FROM coupons")
        assert total == distinct, (
            f"Expected unique coupon codes: {total} vs {distinct} distinct"
        )

    def test_verify_coupon_code_not_empty(self) -> None:
        """Verify that no coupon codes are empty."""
        empty = fetch_scalar(
            "SELECT COUNT(*) FROM coupons WHERE code IS NULL OR TRIM(code) = ''"
        )
        assert empty == 0, (
            f"Expected 0 coupons with empty codes, found {empty}"
        )

    def test_verify_all_coupons_have_discount(self) -> None:
        """Verify that all coupons have a positive discount percent."""
        no_discount = fetch_scalar(
            "SELECT COUNT(*) FROM coupons WHERE discount_percent IS NULL OR discount_percent <= 0"
        )
        assert no_discount == 0, (
            f"Expected 0 coupons without discount, found {no_discount}"
        )
