from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class APIEndpoints:
    """Central repository of all API endpoint URL patterns.

    Every endpoint is derived from a base URL and expressed as a class method or
    a string template so tests never hard-code URLs.

    Usage:
        >>> APIEndpoints.login()
        'https://api.example.com/v1/auth/login'
        >>> APIEndpoints.product_by_id(5)
        'https://api.example.com/v1/products/5'
    """

    # ── Authentication ────────────────────────────────────────────────────────
    LOGIN: str = "/auth/login"
    REGISTER: str = "/auth/register"
    REFRESH_TOKEN: str = "/auth/refresh-token"
    PROFILE: str = "/auth/profile"
    LOGOUT: str = "/auth/logout"

    # ── Products / Catalogue ──────────────────────────────────────────────────
    PRODUCTS: str = "/products"
    PRODUCT_BY_ID: str = "/products/{product_id}"
    PRODUCTS_SEARCH: str = "/products/"
    CATEGORIES: str = "/categories"
    CATEGORY_BY_ID: str = "/categories/{category_id}"

    # ── Cart ──────────────────────────────────────────────────────────────────
    CART: str = "/carts"
    CART_BY_ID: str = "/carts/{cart_id}"
    CART_ITEM: str = "/carts/{cart_id}/items"
    CART_ITEM_BY_ID: str = "/carts/{cart_id}/items/{item_id}"

    # ── Orders ────────────────────────────────────────────────────────────────
    ORDERS: str = "/orders"
    ORDER_BY_ID: str = "/orders/{order_id}"
    USER_ORDERS: str = "/users/{user_id}/orders"

    # ── Users ─────────────────────────────────────────────────────────────────
    USERS: str = "/users"
    USER_BY_ID: str = "/users/{user_id}"
    USER_PROFILE: str = "/users/{user_id}/profile"

    # ── System / Health ───────────────────────────────────────────────────────
    HEALTH: str = "/health"
    STATUS: str = "/status"

    @classmethod
    def login(cls) -> str:
        """Full path for login endpoint."""
        return cls.LOGIN

    @classmethod
    def register(cls) -> str:
        """Full path for registration endpoint."""
        return cls.REGISTER

    @classmethod
    def refresh_token(cls) -> str:
        """Full path for token refresh endpoint."""
        return cls.REFRESH_TOKEN

    @classmethod
    def profile(cls) -> str:
        """Full path for user profile endpoint."""
        return cls.PROFILE

    @classmethod
    def logout(cls) -> str:
        """Full path for logout endpoint."""
        return cls.LOGOUT

    @classmethod
    def products(cls) -> str:
        """Full path for products listing / creation."""
        return cls.PRODUCTS

    @classmethod
    def product_by_id(cls, product_id: int) -> str:
        """Full path for a single product resource.

        Args:
            product_id: The numeric identifier of the product.

        Returns:
            Endpoint path with the ID substituted.
        """
        return cls.PRODUCT_BY_ID.format(product_id=product_id)

    @classmethod
    def products_search(cls) -> str:
        """Full path for product search endpoint."""
        return cls.PRODUCTS_SEARCH

    @classmethod
    def categories(cls) -> str:
        """Full path for categories listing."""
        return cls.CATEGORIES

    @classmethod
    def category_by_id(cls, category_id: int) -> str:
        """Full path for a single category.

        Args:
            category_id: The numeric identifier of the category.
        """
        return cls.CATEGORY_BY_ID.format(category_id=category_id)

    @classmethod
    def carts(cls) -> str:
        """Full path for cart listing / creation."""
        return cls.CART

    @classmethod
    def cart_by_id(cls, cart_id: int) -> str:
        """Full path for a single cart.

        Args:
            cart_id: The numeric identifier of the cart.
        """
        return cls.CART_BY_ID.format(cart_id=cart_id)

    @classmethod
    def cart_items(cls, cart_id: int) -> str:
        """Full path for items within a cart.

        Args:
            cart_id: The numeric identifier of the cart.
        """
        return cls.CART_ITEM.format(cart_id=cart_id)

    @classmethod
    def cart_item_by_id(cls, cart_id: int, item_id: int) -> str:
        """Full path for a single cart item.

        Args:
            cart_id: The numeric identifier of the cart.
            item_id: The numeric identifier of the item within the cart.
        """
        return cls.CART_ITEM_BY_ID.format(cart_id=cart_id, item_id=item_id)

    @classmethod
    def orders(cls) -> str:
        """Full path for order listing / creation."""
        return cls.ORDERS

    @classmethod
    def order_by_id(cls, order_id: int) -> str:
        """Full path for a single order.

        Args:
            order_id: The numeric identifier of the order.
        """
        return cls.ORDER_BY_ID.format(order_id=order_id)

    @classmethod
    def user_orders(cls, user_id: int) -> str:
        """Full path for orders belonging to a specific user.

        Args:
            user_id: The numeric identifier of the user.
        """
        return cls.USER_ORDERS.format(user_id=user_id)

    @classmethod
    def users(cls) -> str:
        """Full path for user listing / creation."""
        return cls.USERS

    @classmethod
    def user_by_id(cls, user_id: int) -> str:
        """Full path for a single user.

        Args:
            user_id: The numeric identifier of the user.
        """
        return cls.USER_BY_ID.format(user_id=user_id)

    @classmethod
    def user_profile(cls, user_id: int) -> str:
        """Full path for a user's profile.

        Args:
            user_id: The numeric identifier of the user.
        """
        return cls.USER_PROFILE.format(user_id=user_id)

    @classmethod
    def health(cls) -> str:
        """Full path for the health-check endpoint."""
        return cls.HEALTH

    @classmethod
    def status(cls) -> str:
        """Full path for the status endpoint."""
        return cls.STATUS
