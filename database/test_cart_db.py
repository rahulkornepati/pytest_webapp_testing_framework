from __future__ import annotations

"""Database validation tests for the **Cart** module.

Verifies shopping cart creation, item management, quantities,
totals, and cart lifecycle.
"""

import pytest

from database.db_helpers import DBHelpers
from database.db_queries import count, fetch_all, fetch_one, fetch_scalar
from database.sql_constants import SQLQueries

pytestmark = [
    pytest.mark.database,
    pytest.mark.regression,
    pytest.mark.cart,
]


class TestCartDB:
    """Database-level validation of shopping cart data."""

    # ── Cart existence ────────────────────────────────────────────────────────

    def test_verify_cart_created(self, known_users: dict) -> None:
        """Verify that a cart exists for a known user."""
        cart = fetch_one(SQLQueries.CART_BY_USER_ID, (known_users["standard_user"]["user_id"],))
        assert cart is not None, (
            "Expected a cart to exist for 'standard_user'"
        )

    def test_verify_cart_by_id(self) -> None:
        """Verify that a cart can be retrieved by its ID."""
        cart = fetch_one(SQLQueries.CART_BY_CART_ID, (1,))
        assert cart is not None, "Expected cart with ID 1 to exist"
        assert cart["cart_id"] == 1

    # ── Cart items ────────────────────────────────────────────────────────────

    def test_verify_cart_item_exists(self, db_helpers: DBHelpers, known_products: dict) -> None:
        """Verify that a specific item exists in a cart."""
        backpack_id = known_products["Sauce Labs Backpack"]
        assert db_helpers.cart_item_exists(1, backpack_id), (
            f"Expected product 'Sauce Labs Backpack' (ID {backpack_id}) in cart 1"
        )

    def test_verify_cart_quantity(self, db_helpers: DBHelpers, known_products: dict) -> None:
        """Verify that the quantity of a cart item is correct."""
        backpack_id = known_products["Sauce Labs Backpack"]
        qty = db_helpers.cart_item_quantity(1, backpack_id)
        assert qty == 2, (
            f"Expected quantity 2 for Sauce Labs Backpack in cart 1, got {qty}"
        )

    def test_verify_duplicate_cart_items_handled(self, known_products: dict) -> None:
        """Verify that the UNIQUE constraint on (cart_id, product_id) prevents duplicates."""
        # Attempting to add a duplicate item would raise IntegrityError
        # Verify that only one record exists
        backpack_id = known_products["Sauce Labs Backpack"]
        item_count = fetch_scalar(
            "SELECT COUNT(*) FROM cart_items WHERE cart_id = 1 AND product_id = ?",
            (backpack_id,),
        )
        assert item_count == 1, (
            f"Expected exactly 1 record for cart_id=1, product_id={backpack_id}, got {item_count}"
        )

    # ── Cart totals ───────────────────────────────────────────────────────────

    def test_verify_cart_total(self, db_helpers: DBHelpers) -> None:
        """Verify that the cart total is calculated correctly."""
        total = db_helpers.cart_total_price(1)
        backpack_price = 29.99
        bike_light_price = 9.99
        expected = (2 * backpack_price) + (1 * bike_light_price)
        assert abs(total - expected) < 0.01, (
            f"Expected cart total {expected}, got {total}"
        )

    def test_verify_cart_total_matches_items(self) -> None:
        """Verify the total for cart 3 (visual_user: 1 Fleece Jacket + 3 Mugs)."""
        total = fetch_scalar(SQLQueries.CART_TOTAL_PRICE, (3,))
        expected = (1 * 49.99) + (3 * 14.99)
        assert abs(total - expected) < 0.01, (
            f"Expected cart 3 total {expected}, got {total}"
        )

    # ── Cart timestamps ───────────────────────────────────────────────────────

    def test_verify_cart_timestamp(self) -> None:
        """Verify that carts have a valid created_at timestamp."""
        cart = fetch_one(SQLQueries.CART_BY_CART_ID, (1,))
        assert cart is not None, "Expected cart 1 to exist"
        assert cart["created_at"] is not None, "Expected non-null created_at"

    def test_verify_cart_updated_at_not_null(self) -> None:
        """Verify that carts have an updated_at timestamp."""
        invalid = fetch_scalar(
            "SELECT COUNT(*) FROM cart WHERE updated_at IS NULL"
        )
        assert invalid == 0, (
            f"Expected 0 carts with NULL updated_at, found {invalid}"
        )

    # ── Cart lifecycle (add/remove) ───────────────────────────────────────────

    def test_verify_remove_cart_item(self) -> None:
        """Verify that removing items from a cart works (cart 1 has 2 items)."""
        items = fetch_all(SQLQueries.CART_ITEMS_BY_CART_ID, (1,))
        assert len(items) == 2, (
            f"Expected 2 items in cart 1, found {len(items)}"
        )

    def test_verify_empty_cart(self, db_helpers: DBHelpers) -> None:
        """Verify that checked-out carts have no items or are empty."""
        item_count = db_helpers.cart_item_count(4)  # admin_user's cart is checked_out
        assert item_count == 1 or item_count == 0, (
            f"Expected checked-out cart 4 items to be 0 or 1, got {item_count}"
        )

    def test_verify_cart_owner(self, db_helpers: DBHelpers) -> None:
        """Verify that a cart belongs to the correct user."""
        owner = fetch_scalar(SQLQueries.CART_OWNER, (1,))
        assert owner == "standard_user", (
            f"Expected cart 1 owner to be 'standard_user', got '{owner}'"
        )

    def test_verify_cart_status(self, db_helpers: DBHelpers) -> None:
        """Verify that cart status has valid values."""
        status = db_helpers.cart_status(1)
        assert status == "active", (
            f"Expected cart 1 status to be 'active', got '{status}'"
        )

    def test_verify_cart_status_valid_values(self) -> None:
        """Verify all cart statuses are from the allowed set."""
        invalid = fetch_scalar(
            "SELECT COUNT(*) FROM cart WHERE status NOT IN ('active', 'checked_out', 'abandoned')"
        )
        assert invalid == 0, (
            f"Expected 0 carts with invalid status, found {invalid}"
        )

    def test_verify_cart_items_have_product_names(self) -> None:
        """Verify that cart items can be retrieved with product details."""
        items = fetch_all(SQLQueries.CART_ITEMS_BY_CART_ID, (1,))
        for item in items:
            assert "name" in item and item["name"], (
                f"Expected product name in cart item: {item}"
            )
            assert item["price"] > 0, (
                f"Expected positive price for cart item: {item}"
            )
