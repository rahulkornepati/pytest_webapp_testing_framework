from __future__ import annotations

"""Reusable helper functions for database test assertions.

These helpers provide clean, readable assertion patterns so that
individual test methods focus on **what** is being tested rather than
**how** to query the database.
"""

import logging
from typing import Any

from database.db_queries import count, exists, fetch_all, fetch_column, fetch_one, fetch_scalar
from database.sql_constants import SQLQueries

logger = logging.getLogger("ecommerce_framework.database.helpers")


class DBHelpers:
    """Static helper methods for common database validation patterns.

    Every method follows a consistent pattern:
        1. Execute a query from ``SQLQueries``.
        2. Perform business-logic validation.
        3. Return a ``bool`` and a descriptive ``str`` message.
    """

    # ==========================================================================
    # User helpers
    # ==========================================================================

    @staticmethod
    def user_exists(username: str) -> bool:
        """Check if a user exists by username."""
        return fetch_scalar("SELECT COUNT(*) FROM users WHERE username = ?", (username,)) > 0

    @staticmethod
    def email_exists(email: str) -> bool:
        """Check if a user with the given email exists."""
        return fetch_scalar("SELECT COUNT(*) FROM users WHERE email = ?", (email,)) > 0

    @staticmethod
    def user_is_active(username: str) -> bool:
        """Check if a user's account is active."""
        result = fetch_scalar(SQLQueries.USER_STATUS, (username,))
        return bool(result) if result is not None else False

    @staticmethod
    def user_is_locked(username: str) -> bool:
        """Check if a user's account is locked."""
        result = fetch_scalar(SQLQueries.USER_LOCKED_STATUS, (username,))
        return bool(result) if result is not None else False

    @staticmethod
    def user_has_login_attempts(username: str) -> int:
        """Get the login attempt count for a user."""
        result = fetch_scalar(SQLQueries.USER_LOGIN_ATTEMPTS, (username,))
        return result if result is not None else 0

    @staticmethod
    def user_role(username: str) -> str:
        """Get the role of a user."""
        result = fetch_scalar(SQLQueries.USER_ROLE, (username,))
        return result if result is not None else ""

    @staticmethod
    def user_last_login(username: str) -> str | None:
        """Get the last login timestamp for a user."""
        return fetch_scalar(SQLQueries.USER_LAST_LOGIN, (username,))

    @staticmethod
    def active_user_count() -> int:
        """Get the total number of active users."""
        return count(SQLQueries.USER_ACTIVE_COUNT)

    # ==========================================================================
    # Product helpers
    # ==========================================================================

    @staticmethod
    def product_exists(product_name: str) -> bool:
        """Check if a product exists by name."""
        return exists(SQLQueries.PRODUCT_BY_NAME, (product_name,))

    @staticmethod
    def product_price(product_name: str) -> float | None:
        """Get the price of a product."""
        return fetch_scalar(SQLQueries.PRODUCT_PRICE, (product_name,))

    @staticmethod
    def product_description(product_name: str) -> str:
        """Get the description of a product."""
        result = fetch_scalar(SQLQueries.PRODUCT_DESCRIPTION, (product_name,))
        return result if result is not None else ""

    @staticmethod
    def product_category_id(product_name: str) -> int:
        """Get the category ID of a product."""
        result = fetch_scalar(SQLQueries.PRODUCT_CATEGORY_ID, (product_name,))
        return result if result is not None else 0

    @staticmethod
    def product_count() -> int:
        """Get the total number of products."""
        return count(SQLQueries.PRODUCT_COUNT)

    @staticmethod
    def active_product_count() -> int:
        """Get the number of active products."""
        return count(SQLQueries.PRODUCT_ACTIVE_COUNT)

    @staticmethod
    def negative_price_count() -> int:
        """Get count of products with negative prices."""
        return count(SQLQueries.PRODUCT_NEGATIVE_PRICE)

    @staticmethod
    def inventory_quantity(product_name: str) -> int:
        """Get the inventory quantity for a product."""
        result = fetch_scalar(SQLQueries.PRODUCT_INVENTORY_QTY, (product_name,))
        return result if result is not None else 0

    # ==========================================================================
    # Cart helpers
    # ==========================================================================

    @staticmethod
    def cart_exists(cart_id: int) -> bool:
        """Check if a cart exists."""
        return exists(SQLQueries.CART_BY_CART_ID, (cart_id,))

    @staticmethod
    def cart_item_exists(cart_id: int, product_id: int) -> bool:
        """Check if a specific item exists in a cart."""
        result = fetch_scalar(SQLQueries.CART_ITEM_EXISTS, (cart_id, product_id))
        return (result or 0) > 0

    @staticmethod
    def cart_item_quantity(cart_id: int, product_id: int) -> int:
        """Get the quantity of a specific item in a cart."""
        result = fetch_scalar(SQLQueries.CART_ITEM_QUANTITY, (cart_id, product_id))
        return result if result is not None else 0

    @staticmethod
    def cart_total_price(cart_id: int) -> float:
        """Calculate the total price of all items in a cart."""
        result = fetch_scalar(SQLQueries.CART_TOTAL_PRICE, (cart_id,))
        return float(result) if result is not None else 0.0

    @staticmethod
    def cart_item_count(cart_id: int) -> int:
        """Get the number of items in a cart."""
        return count(SQLQueries.CART_EMPTY_CHECK, (cart_id,))

    @staticmethod
    def cart_status(cart_id: int) -> str:
        """Get the status of a cart."""
        result = fetch_scalar(SQLQueries.CART_STATUS, (cart_id,))
        return result if result is not None else ""

    # ==========================================================================
    # Order helpers
    # ==========================================================================

    @staticmethod
    def order_exists(order_id: int) -> bool:
        """Check if an order exists."""
        return exists(SQLQueries.ORDER_BY_ID, (order_id,))

    @staticmethod
    def order_status(order_id: int) -> str:
        """Get the status of an order."""
        result = fetch_scalar(SQLQueries.ORDER_STATUS, (order_id,))
        return result if result is not None else ""

    @staticmethod
    def order_total(order_id: int) -> float:
        """Get the total amount of an order."""
        result = fetch_scalar(SQLQueries.ORDER_TOTAL, (order_id,))
        return float(result) if result is not None else 0.0

    @staticmethod
    def order_count_total() -> int:
        """Get the total number of orders."""
        return count(SQLQueries.ORDER_COUNT_TOTAL)

    @staticmethod
    def order_count_by_user(user_id: int) -> int:
        """Get the number of orders for a user."""
        return count(SQLQueries.ORDER_COUNT_BY_USER, (user_id,))

    # ==========================================================================
    # Payment helpers
    # ==========================================================================

    @staticmethod
    def payment_status(order_id: int) -> str:
        """Get the payment status for an order."""
        result = fetch_scalar(SQLQueries.PAYMENT_STATUS, (order_id,))
        return result if result is not None else ""

    @staticmethod
    def payment_method(order_id: int) -> str:
        """Get the payment method for an order."""
        result = fetch_scalar(SQLQueries.PAYMENT_METHOD, (order_id,))
        return result if result is not None else ""

    @staticmethod
    def payment_amount(order_id: int) -> float:
        """Get the payment amount for an order."""
        result = fetch_scalar(SQLQueries.PAYMENT_AMOUNT, (order_id,))
        return float(result) if result is not None else 0.0

    @staticmethod
    def total_revenue() -> float:
        """Get total revenue from completed payments."""
        result = fetch_scalar(SQLQueries.PAYMENT_TOTAL_REVENUE)
        return float(result) if result is not None else 0.0

    # ==========================================================================
    # Coupon helpers
    # ==========================================================================

    @staticmethod
    def coupon_exists(code: str) -> bool:
        """Check if a coupon code exists."""
        return exists(SQLQueries.COUPON_BY_CODE, (code,))

    @staticmethod
    def coupon_is_active(code: str) -> bool:
        """Check if a coupon is active."""
        result = fetch_scalar(SQLQueries.COUPON_IS_ACTIVE, (code,))
        return bool(result) if result is not None else False

    @staticmethod
    def coupon_discount(code: str) -> int:
        """Get the discount percent for a coupon."""
        result = fetch_scalar(SQLQueries.COUPON_DISCOUNT_PERCENT, (code,))
        return result if result is not None else 0

    @staticmethod
    def coupon_usage_count(code: str) -> int:
        """Get the current usage count of a coupon."""
        result = fetch_scalar(SQLQueries.COUPON_USAGE_COUNT, (code,))
        return result if result is not None else 0

    # ==========================================================================
    # Session helpers
    # ==========================================================================

    @staticmethod
    def session_is_active(session_token: str) -> bool:
        """Check if a session is active."""
        result = fetch_scalar(SQLQueries.SESSION_IS_ACTIVE, (session_token,))
        return bool(result) if result is not None else False

    @staticmethod
    def active_session_count() -> int:
        """Get the number of active sessions."""
        return count(SQLQueries.SESSION_COUNT_ACTIVE)

    @staticmethod
    def expired_session_count() -> int:
        """Get the number of expired sessions that are still marked active."""
        return count(SQLQueries.SESSION_EXPIRED_COUNT)

    # ==========================================================================
    # Wishlist helpers
    # ==========================================================================

    @staticmethod
    def wishlist_item_count(user_id: int) -> int:
        """Get the number of wishlist items for a user."""
        return count(SQLQueries.WISHLIST_COUNT_BY_USER, (user_id,))

    @staticmethod
    def wishlist_item_exists(user_id: int, product_id: int) -> bool:
        """Check if a product exists in a user's wishlist."""
        result = fetch_scalar(SQLQueries.WISHLIST_ITEM_EXISTS, (user_id, product_id))
        return (result or 0) > 0

    # ==========================================================================
    # Review helpers
    # ==========================================================================

    @staticmethod
    def average_rating(product_id: int) -> float:
        """Get the average rating for a product."""
        result = fetch_scalar(SQLQueries.REVIEW_AVERAGE_RATING, (product_id,))
        return float(result) if result is not None else 0.0

    @staticmethod
    def review_count_by_product(product_id: int) -> int:
        """Get the number of reviews for a product."""
        return count(SQLQueries.REVIEW_COUNT_BY_PRODUCT, (product_id,))

    @staticmethod
    def review_is_approved(review_id: int) -> bool:
        """Check if a review is approved."""
        result = fetch_scalar(SQLQueries.REVIEW_MODERATION_STATUS, (review_id,))
        return bool(result) if result is not None else False

    # ==========================================================================
    # Search / sort helpers
    # ==========================================================================

    @staticmethod
    def search_products_by_name(search_term: str) -> list[dict[str, Any]]:
        """Search for products by partial name match."""
        return fetch_all(SQLQueries.SEARCH_PRODUCTS_BY_NAME, (f"%{search_term}%",))

    @staticmethod
    def products_in_stock() -> list[dict[str, Any]]:
        """Get all active products that are in stock."""
        return fetch_all(SQLQueries.SEARCH_PRODUCTS_IN_STOCK)

    @staticmethod
    def sorted_product_names(ascending: bool = True) -> list[str]:
        """Get product names sorted alphabetically."""
        query = SQLQueries.PRODUCTS_NAME_ASC if ascending else SQLQueries.PRODUCTS_NAME_DESC
        return fetch_column(query)

    @staticmethod
    def sorted_product_prices(ascending: bool = True) -> list[tuple[str, float]]:
        """Get product name/price pairs sorted by price."""
        query = SQLQueries.PRODUCTS_PRICE_ASC if ascending else SQLQueries.PRODUCTS_PRICE_DESC
        rows = fetch_all(query)
        return [(r["name"], r["price"]) for r in rows]
