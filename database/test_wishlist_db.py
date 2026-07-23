from __future__ import annotations

"""Database validation tests for the **Wishlist** module.

Verifies wishlist entries, user-product associations, and
wishlist-related business rules at the database level.
"""

import pytest

from database.db_helpers import DBHelpers
from database.db_queries import count, fetch_all, fetch_one, fetch_scalar
from database.sql_constants import SQLQueries

pytestmark = [
    pytest.mark.database,
    pytest.mark.regression,
    pytest.mark.products,
]


class TestWishlistDB:
    """Database-level validation of wishlist data."""

    # ── Wishlist existence ────────────────────────────────────────────────────

    def test_verify_wishlist_exists_for_user(self) -> None:
        """Verify that a wishlist exists for a known user."""
        user = fetch_one(SQLQueries.USER_BY_USERNAME, ("standard_user",))
        items = fetch_all(SQLQueries.WISHLIST_BY_USER_ID, (user["user_id"],))
        assert len(items) >= 1, (
            f"Expected at least 1 wishlist item for standard_user, found {len(items)}"
        )

    def test_verify_wishlist_empty_for_new_user(self, known_users: dict) -> None:
        """Verify that a new user has no wishlist items."""
        user_id = known_users["new_user"]["user_id"]
        items = fetch_all(SQLQueries.WISHLIST_BY_USER_ID, (user_id,))
        assert len(items) == 0, (
            f"Expected 0 wishlist items for new_user, found {len(items)}"
        )

    # ── Wishlist items ────────────────────────────────────────────────────────

    def test_verify_wishlist_item_count(self, db_helpers: DBHelpers, known_users: dict) -> None:
        """Verify the number of items in a user's wishlist."""
        user_id = known_users["standard_user"]["user_id"]
        count = db_helpers.wishlist_item_count(user_id)
        assert count == 3, (
            f"Expected 3 wishlist items for standard_user, found {count}"
        )

    def test_verify_wishlist_item_exists(self, db_helpers: DBHelpers, known_users: dict, known_products: dict) -> None:
        """Verify that a specific product exists in a user's wishlist."""
        user_id = known_users["standard_user"]["user_id"]
        product_id = known_products["Sauce Labs Fleece Jacket"]
        assert db_helpers.wishlist_item_exists(user_id, product_id), (
            "Expected Fleece Jacket in standard_user's wishlist"
        )

    def test_verify_wishlist_item_not_exists(self, db_helpers: DBHelpers, known_users: dict, known_products: dict) -> None:
        """Verify that a product not in wishlist returns False."""
        user_id = known_users["standard_user"]["user_id"]
        product_id = known_products["Sauce Labs Bolt T-Shirt"]
        assert not db_helpers.wishlist_item_exists(user_id, product_id), (
            "Expected Bolt T-Shirt NOT in standard_user's wishlist"
        )

    # ── Product details in wishlist ───────────────────────────────────────────

    def test_verify_wishlist_product_details(self, known_users: dict) -> None:
        """Verify that wishlist items include full product details."""
        user_id = known_users["standard_user"]["user_id"]
        items = fetch_all(SQLQueries.WISHLIST_PRODUCT_DETAILS, (user_id,))
        for item in items:
            assert "name" in item and item["name"], (
                f"Expected product name in wishlist item: {item}"
            )
            assert item["price"] > 0, (
                f"Expected positive price in wishlist item: {item}"
            )

    def test_verify_wishlist_product_names(self, known_users: dict) -> None:
        """Verify that specific product names appear in the wishlist."""
        user_id = known_users["standard_user"]["user_id"]
        items = fetch_all(SQLQueries.WISHLIST_PRODUCT_DETAILS, (user_id,))
        names = [item["name"] for item in items]
        assert "Sauce Labs Fleece Jacket" in names, (
            f"Expected Fleece Jacket in wishlist, got {names}"
        )
        assert "Sauce Labs Wireless Earbuds" in names, (
            f"Expected Wireless Earbuds in wishlist, got {names}"
        )
        assert "Sauce Labs Yoga Mat" in names, (
            f"Expected Yoga Mat in wishlist, got {names}"
        )

    # ── Duplicate prevention ──────────────────────────────────────────────────

    def test_verify_no_duplicate_wishlist_items(self) -> None:
        """Verify that the UNIQUE constraint on (user_id, product_id) is enforced."""
        duplicates = fetch_scalar(
            """SELECT COUNT(*) FROM (SELECT user_id, product_id, COUNT(*)
               FROM wishlist GROUP BY user_id, product_id HAVING COUNT(*) > 1)"""
        )
        assert duplicates == 0, (
            f"Expected 0 duplicate wishlist entries, found {duplicates}"
        )

    def test_verify_duplicate_check(self, known_users: dict, known_products: dict) -> None:
        """Verify that duplicate check returns the correct count."""
        user_id = known_users["standard_user"]["user_id"]
        product_id = known_products["Sauce Labs Fleece Jacket"]
        duplicate_count = fetch_scalar(
            SQLQueries.WISHLIST_DUPLICATE_CHECK,
            (user_id, product_id),
        )
        assert duplicate_count == 1, (
            f"Expected 1 existing wishlist entry, found {duplicate_count}"
        )

    # ── Timestamps ────────────────────────────────────────────────────────────

    def test_verify_wishlist_added_at_timestamp(self) -> None:
        """Verify that all wishlist items have an added_at timestamp."""
        null_dates = fetch_scalar(
            "SELECT COUNT(*) FROM wishlist WHERE added_at IS NULL"
        )
        assert null_dates == 0, (
            f"Expected 0 wishlist items with NULL added_at, found {null_dates}"
        )

    # ── User-product linkage ──────────────────────────────────────────────────

    def test_verify_wishlist_user_exists(self) -> None:
        """Verify that all wishlist entries reference existing users."""
        orphaned = fetch_scalar(
            "SELECT COUNT(*) FROM wishlist WHERE user_id NOT IN (SELECT user_id FROM users)"
        )
        assert orphaned == 0, (
            f"Expected 0 wishlist entries with invalid user, found {orphaned}"
        )

    def test_verify_wishlist_product_exists(self) -> None:
        """Verify that all wishlist entries reference existing products."""
        orphaned = fetch_scalar(
            "SELECT COUNT(*) FROM wishlist WHERE product_id NOT IN (SELECT product_id FROM products)"
        )
        assert orphaned == 0, (
            f"Expected 0 wishlist entries with invalid product, found {orphaned}"
        )

    # ── Multiple user wishlists ───────────────────────────────────────────────

    def test_verify_multiple_users_have_wishlists(self) -> None:
        """Verify that multiple users have wishlist items."""
        users_with_wishlist = fetch_scalar(
            "SELECT COUNT(DISTINCT user_id) FROM wishlist"
        )
        assert users_with_wishlist >= 3, (
            f"Expected at least 3 users with wishlists, found {users_with_wishlist}"
        )

    def test_verify_wishlist_ordered_by_added_at(self, known_users: dict) -> None:
        """Verify that wishlist items are returned in descending order of added_at."""
        user_id = known_users["standard_user"]["user_id"]
        items = fetch_all(SQLQueries.WISHLIST_PRODUCT_DETAILS, (user_id,))
        if len(items) >= 2:
            timestamps = [item["added_at"] for item in items]
            assert timestamps == sorted(timestamps, reverse=True), (
                "Wishlist items are not sorted by added_at DESC"
            )

    # ── Wishlist count ────────────────────────────────────────────────────────

    def test_verify_total_wishlist_items(self) -> None:
        """Verify the total number of wishlist items in the database."""
        total = fetch_scalar("SELECT COUNT(*) FROM wishlist")
        assert total == 8, (
            f"Expected 8 wishlist items total, found {total}"
        )

    def test_verify_wishlist_item_image_url(self, known_users: dict) -> None:
        """Verify that wishlist items include image URLs."""
        user_id = known_users["standard_user"]["user_id"]
        items = fetch_all(SQLQueries.WISHLIST_PRODUCT_DETAILS, (user_id,))
        for item in items:
            assert "image_url" in item, (
                f"Expected image_url in wishlist item: {item}"
            )
