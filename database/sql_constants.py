from __future__ import annotations

from enum import Enum, auto


class SQLQueries(str, Enum):
    """Centralized repository of all SQL query constants.

    Every SQL query used across the database test suite is defined here
    as an enum member.  Tests must never embed raw SQL strings —
    always reference ``SQLQueries.<NAME>``.

    Naming convention:  ``<TABLE>_<ACTION>`` or ``<TABLE>_<ACTION>_<MODIFIER>``
    """

    # ==========================================================================
    # Users
    # ==========================================================================
    USER_BY_USERNAME = "SELECT * FROM users WHERE username = ?"
    USER_BY_EMAIL = "SELECT * FROM users WHERE email = ?"
    USER_BY_ID = "SELECT * FROM users WHERE user_id = ?"
    USER_ROLE = "SELECT role FROM users WHERE username = ?"
    USER_STATUS = "SELECT is_active FROM users WHERE username = ?"
    USER_LAST_LOGIN = "SELECT last_login FROM users WHERE username = ?"
    USER_PASSWORD_HASH = "SELECT password_hash FROM users WHERE username = ?"
    USER_LOGIN_ATTEMPTS = "SELECT login_attempts FROM users WHERE username = ?"
    USER_ACTIVE_COUNT = "SELECT COUNT(*) FROM users WHERE is_active = 1"
    USER_DUPLICATE_CHECK = "SELECT COUNT(*) FROM users WHERE email = ?"
    USER_LOCKED_STATUS = "SELECT account_locked FROM users WHERE username = ?"

    # ==========================================================================
    # Categories
    # ==========================================================================
    CATEGORY_BY_ID = "SELECT * FROM categories WHERE category_id = ?"
    CATEGORY_BY_NAME = "SELECT * FROM categories WHERE name = ?"
    CATEGORY_ACTIVE_COUNT = "SELECT COUNT(*) FROM categories WHERE is_active = 1"
    CATEGORY_ALL = "SELECT * FROM categories ORDER BY name"
    CATEGORY_PRODUCT_COUNT = """
        SELECT c.name, COUNT(p.product_id) AS product_count
        FROM categories c
        LEFT JOIN products p ON p.category_id = c.category_id
        GROUP BY c.category_id
        ORDER BY c.name
    """

    # ==========================================================================
    # Products
    # ==========================================================================
    PRODUCT_BY_NAME = "SELECT * FROM products WHERE name = ?"
    PRODUCT_BY_ID = "SELECT * FROM products WHERE product_id = ?"
    PRODUCT_PRICE = "SELECT price FROM products WHERE name = ?"
    PRODUCT_DESCRIPTION = "SELECT description FROM products WHERE name = ?"
    PRODUCT_CATEGORY_ID = "SELECT category_id FROM products WHERE name = ?"
    PRODUCT_COUNT = "SELECT COUNT(*) FROM products"
    PRODUCT_ACTIVE_COUNT = "SELECT COUNT(*) FROM products WHERE is_active = 1"
    PRODUCT_IMAGES = "SELECT image_url FROM products WHERE name = ?"
    PRODUCT_DUPLICATE_CHECK = "SELECT COUNT(*) FROM products WHERE name = ?"
    PRODUCT_NEGATIVE_PRICE = "SELECT COUNT(*) FROM products WHERE price < 0"
    PRODUCTS_PRICE_ASC = "SELECT name, price FROM products ORDER BY price ASC"
    PRODUCTS_PRICE_DESC = "SELECT name, price FROM products ORDER BY price DESC"
    PRODUCTS_NAME_ASC = "SELECT name FROM products ORDER BY name ASC"
    PRODUCTS_NAME_DESC = "SELECT name FROM products ORDER BY name DESC"
    PRODUCT_INVENTORY_QTY = """
        SELECT i.quantity
        FROM inventory i
        JOIN products p ON p.product_id = i.product_id
        WHERE p.name = ?
    """

    # ==========================================================================
    # Inventory
    # ==========================================================================
    INVENTORY_BY_PRODUCT_ID = "SELECT * FROM inventory WHERE product_id = ?"
    INVENTORY_BY_PRODUCT_NAME = """
        SELECT i.* FROM inventory i
        JOIN products p ON p.product_id = i.product_id
        WHERE p.name = ?
    """
    INVENTORY_LOW_STOCK = """
        SELECT p.name, i.quantity FROM inventory i
        JOIN products p ON p.product_id = i.product_id
        WHERE i.quantity <= i.reorder_level AND i.quantity > 0
    """
    INVENTORY_OUT_OF_STOCK = """
        SELECT p.name FROM inventory i
        JOIN products p ON p.product_id = i.product_id
        WHERE i.quantity = 0
    """
    INVENTORY_REORDER_NEEDED = """
        SELECT p.name, i.quantity, i.reorder_level
        FROM inventory i
        JOIN products p ON p.product_id = i.product_id
        WHERE i.quantity <= i.reorder_level
    """
    INVENTORY_ALL = """
        SELECT p.name, i.quantity, i.reorder_level, i.location
        FROM inventory i
        JOIN products p ON p.product_id = i.product_id
        ORDER BY p.name
    """
    INVENTORY_NEGATIVE_QTY = "SELECT COUNT(*) FROM inventory WHERE quantity < 0"
    INVENTORY_TOTAL_STOCK = "SELECT SUM(quantity) FROM inventory"

    # ==========================================================================
    # Cart
    # ==========================================================================
    CART_BY_USER_ID = "SELECT * FROM cart WHERE user_id = ?"
    CART_BY_CART_ID = "SELECT * FROM cart WHERE cart_id = ?"
    CART_ITEMS_BY_CART_ID = """
        SELECT ci.*, p.name, p.price
        FROM cart_items ci
        JOIN products p ON p.product_id = ci.product_id
        WHERE ci.cart_id = ?
    """
    CART_ITEM_EXISTS = """
        SELECT COUNT(*) FROM cart_items
        WHERE cart_id = ? AND product_id = ?
    """
    CART_ITEM_QUANTITY = """
        SELECT quantity FROM cart_items
        WHERE cart_id = ? AND product_id = ?
    """
    CART_TOTAL_PRICE = """
        SELECT SUM(ci.quantity * p.price) AS total
        FROM cart_items ci
        JOIN products p ON p.product_id = ci.product_id
        WHERE ci.cart_id = ?
    """
    CART_CREATED_AT = "SELECT created_at FROM cart WHERE cart_id = ?"
    CART_OWNER = """
        SELECT u.username FROM users u
        JOIN cart c ON c.user_id = u.user_id
        WHERE c.cart_id = ?
    """
    CART_STATUS = "SELECT status FROM cart WHERE cart_id = ?"
    CART_EMPTY_CHECK = "SELECT COUNT(*) FROM cart_items WHERE cart_id = ?"

    # ==========================================================================
    # Orders
    # ==========================================================================
    ORDER_BY_ID = "SELECT * FROM orders WHERE order_id = ?"
    ORDER_BY_USER_ID = "SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC"
    ORDER_STATUS = "SELECT status FROM orders WHERE order_id = ?"
    ORDER_TOTAL = "SELECT total_amount FROM orders WHERE order_id = ?"
    ORDER_CREATED_AT = "SELECT created_at FROM orders WHERE order_id = ?"
    ORDER_COUNT_BY_USER = "SELECT COUNT(*) FROM orders WHERE user_id = ?"
    ORDER_COUNT_TOTAL = "SELECT COUNT(*) FROM orders"
    ORDER_ACTIVE_COUNT = "SELECT COUNT(*) FROM orders WHERE status NOT IN ('cancelled', 'refunded')"
    ORDER_BY_STATUS = "SELECT * FROM orders WHERE status = ? ORDER BY created_at DESC"
    ORDER_RECENT = "SELECT * FROM orders ORDER BY created_at DESC LIMIT ?"
    ORDER_WITH_PAYMENT = """
        SELECT o.order_id, o.total_amount, p.payment_status, p.payment_method
        FROM orders o
        JOIN payments p ON p.order_id = o.order_id
        WHERE o.order_id = ?
    """
    ORDER_SHIPPING_INFO = """
        SELECT o.order_id, s.*
        FROM orders o
        JOIN shipping s ON s.order_id = o.order_id
        WHERE o.order_id = ?
    """

    # ==========================================================================
    # Order Items
    # ==========================================================================
    ORDER_ITEMS_BY_ORDER_ID = """
        SELECT oi.*, p.name, p.price AS current_price
        FROM order_items oi
        JOIN products p ON p.product_id = oi.product_id
        WHERE oi.order_id = ?
    """
    ORDER_ITEM_COUNT_BY_ORDER = "SELECT COUNT(*) FROM order_items WHERE order_id = ?"
    ORDER_ITEMS_TOTAL = """
        SELECT SUM(oi.quantity * oi.unit_price) AS total
        FROM order_items oi
        WHERE oi.order_id = ?
    """
    ORDER_ITEM_PRODUCT_DETAILS = """
        SELECT oi.product_id, p.name, oi.quantity, oi.unit_price
        FROM order_items oi
        JOIN products p ON p.product_id = oi.product_id
        WHERE oi.order_id = ?
    """

    # ==========================================================================
    # Payments
    # ==========================================================================
    PAYMENT_BY_ORDER_ID = "SELECT * FROM payments WHERE order_id = ?"
    PAYMENT_BY_ID = "SELECT * FROM payments WHERE payment_id = ?"
    PAYMENT_STATUS = "SELECT payment_status FROM payments WHERE order_id = ?"
    PAYMENT_METHOD = "SELECT payment_method FROM payments WHERE order_id = ?"
    PAYMENT_AMOUNT = "SELECT amount FROM payments WHERE order_id = ?"
    PAYMENT_COUNT_BY_STATUS = """
        SELECT payment_status, COUNT(*) AS count
        FROM payments GROUP BY payment_status
    """
    PAYMENT_TOTAL_REVENUE = "SELECT SUM(amount) FROM payments WHERE payment_status = 'completed'"

    # ==========================================================================
    # Coupons
    # ==========================================================================
    COUPON_BY_CODE = "SELECT * FROM coupons WHERE code = ?"
    COUPON_DISCOUNT_PERCENT = "SELECT discount_percent FROM coupons WHERE code = ?"
    COUPON_EXPIRY = "SELECT expiry_date FROM coupons WHERE code = ?"
    COUPON_IS_ACTIVE = "SELECT is_active FROM coupons WHERE code = ?"
    COUPON_MIN_ORDER = "SELECT min_order_amount FROM coupons WHERE code = ?"
    COUPON_USAGE_COUNT = "SELECT usage_count FROM coupons WHERE code = ?"
    COUPON_MAX_USES = "SELECT max_uses FROM coupons WHERE code = ?"
    COUPON_ALL_ACTIVE = "SELECT * FROM coupons WHERE is_active = 1 AND (expiry_date IS NULL OR expiry_date >= DATE('now'))"
    COUPON_EXPIRED = "SELECT * FROM coupons WHERE expiry_date < DATE('now')"

    # ==========================================================================
    # User Sessions
    # ==========================================================================
    SESSION_BY_USER_ID = "SELECT * FROM user_sessions WHERE user_id = ?"
    SESSION_BY_TOKEN = "SELECT * FROM user_sessions WHERE session_token = ?"
    SESSION_IS_ACTIVE = "SELECT is_active FROM user_sessions WHERE session_token = ?"
    SESSION_CREATED_AT = "SELECT created_at FROM user_sessions WHERE user_id = ?"
    SESSION_LAST_ACTIVITY = "SELECT last_activity FROM user_sessions WHERE user_id = ?"
    SESSION_EXPIRY = "SELECT expires_at FROM user_sessions WHERE user_id = ?"
    SESSION_COUNT_BY_USER = "SELECT COUNT(*) FROM user_sessions WHERE user_id = ?"
    SESSION_COUNT_ACTIVE = "SELECT COUNT(*) FROM user_sessions WHERE is_active = 1"
    SESSION_EXPIRED_COUNT = "SELECT COUNT(*) FROM user_sessions WHERE expires_at < datetime('now') AND is_active = 1"
    SESSION_IP_ADDRESS = "SELECT ip_address FROM user_sessions WHERE session_token = ?"

    # ==========================================================================
    # Wishlist
    # ==========================================================================
    WISHLIST_BY_USER_ID = "SELECT * FROM wishlist WHERE user_id = ?"
    WISHLIST_ITEM_EXISTS = """
        SELECT COUNT(*) FROM wishlist
        WHERE user_id = ? AND product_id = ?
    """
    WISHLIST_COUNT_BY_USER = "SELECT COUNT(*) FROM wishlist WHERE user_id = ?"
    WISHLIST_PRODUCT_DETAILS = """
        SELECT w.wishlist_id, p.name, p.price, p.image_url, w.added_at
        FROM wishlist w
        JOIN products p ON p.product_id = w.product_id
        WHERE w.user_id = ?
        ORDER BY w.added_at DESC
    """
    WISHLIST_DUPLICATE_CHECK = """
        SELECT COUNT(*) FROM wishlist
        WHERE user_id = ? AND product_id = ?
    """

    # ==========================================================================
    # Shipping
    # ==========================================================================
    SHIPPING_BY_ORDER_ID = "SELECT * FROM shipping WHERE order_id = ?"
    SHIPPING_BY_ID = "SELECT * FROM shipping WHERE shipping_id = ?"
    SHIPPING_METHOD = "SELECT shipping_method FROM shipping WHERE order_id = ?"
    SHIPPING_TRACKING = "SELECT tracking_number FROM shipping WHERE order_id = ?"
    SHIPPING_STATUS = "SELECT delivery_status FROM shipping WHERE order_id = ?"
    SHIPPING_ADDRESS = """
        SELECT address_line1, city, state, postal_code, country
        FROM shipping WHERE order_id = ?
    """
    SHIPPING_ESTIMATED_DATE = "SELECT estimated_delivery FROM shipping WHERE order_id = ?"

    # ==========================================================================
    # Reviews
    # ==========================================================================
    REVIEW_BY_ID = "SELECT * FROM reviews WHERE review_id = ?"
    REVIEWS_BY_PRODUCT_ID = "SELECT * FROM reviews WHERE product_id = ? ORDER BY created_at DESC"
    REVIEWS_BY_USER_ID = "SELECT * FROM reviews WHERE user_id = ? ORDER BY created_at DESC"
    REVIEW_RATING = "SELECT rating FROM reviews WHERE review_id = ?"
    REVIEW_AVERAGE_RATING = "SELECT AVG(rating) FROM reviews WHERE product_id = ?"
    REVIEW_COUNT_BY_PRODUCT = "SELECT COUNT(*) FROM reviews WHERE product_id = ?"
    REVIEW_MODERATION_STATUS = "SELECT is_approved FROM reviews WHERE review_id = ?"
    REVIEW_DUPLICATE_CHECK = """
        SELECT COUNT(*) FROM reviews
        WHERE user_id = ? AND product_id = ?
    """

    # ==========================================================================
    # Audit Logs
    # ==========================================================================
    AUDIT_LOG_BY_ID = "SELECT * FROM audit_logs WHERE log_id = ?"
    AUDIT_LOGS_BY_USER = "SELECT * FROM audit_logs WHERE user_id = ? ORDER BY created_at DESC"
    AUDIT_LOGS_BY_ACTION = """
        SELECT * FROM audit_logs
        WHERE action = ? ORDER BY created_at DESC LIMIT ?
    """
    AUDIT_LOG_COUNT = "SELECT COUNT(*) FROM audit_logs"
    AUDIT_LOGS_RECENT = "SELECT * FROM audit_logs ORDER BY created_at DESC LIMIT ?"

    # ==========================================================================
    # Search / Sort helpers
    # ==========================================================================
    SEARCH_PRODUCTS_BY_NAME = "SELECT * FROM products WHERE name LIKE ? ORDER BY name"
    SEARCH_PRODUCTS_BY_DESCRIPTION = "SELECT * FROM products WHERE description LIKE ? ORDER BY name"
    SEARCH_PRODUCTS_BY_CATEGORY = """
        SELECT p.* FROM products p
        JOIN categories c ON c.category_id = p.category_id
        WHERE c.name LIKE ? ORDER BY p.name
    """
    SEARCH_PRODUCTS_BY_PRICE_RANGE = """
        SELECT * FROM products
        WHERE price >= ? AND price <= ?
        ORDER BY price
    """
    SEARCH_PRODUCTS_IN_STOCK = """
        SELECT p.* FROM products p
        JOIN inventory i ON i.product_id = p.product_id
        WHERE i.quantity > 0 AND p.is_active = 1
    """

    # ==========================================================================
    # Reporting / aggregation
    # ==========================================================================
    REPORT_CATEGORY_SALES = """
        SELECT c.name, SUM(oi.quantity * oi.unit_price) AS total_sales
        FROM categories c
        JOIN products p ON p.category_id = c.category_id
        JOIN order_items oi ON oi.product_id = p.product_id
        JOIN orders o ON o.order_id = oi.order_id
        WHERE o.status NOT IN ('cancelled', 'refunded')
        GROUP BY c.category_id
        ORDER BY total_sales DESC
    """
    REPORT_TOP_PRODUCTS = """
        SELECT p.name, SUM(oi.quantity) AS total_sold
        FROM products p
        JOIN order_items oi ON oi.product_id = p.product_id
        JOIN orders o ON o.order_id = oi.order_id
        WHERE o.status NOT IN ('cancelled', 'refunded')
        GROUP BY p.product_id
        ORDER BY total_sold DESC
        LIMIT ?
    """
    REPORT_DAILY_SALES = """
        SELECT DATE(o.created_at) AS sale_date, SUM(oi.quantity * oi.unit_price) AS revenue
        FROM orders o
        JOIN order_items oi ON oi.order_id = o.order_id
        WHERE o.status NOT IN ('cancelled', 'refunded')
        GROUP BY DATE(o.created_at)
        ORDER BY sale_date
    """

    # ==========================================================================
    # Checkout / Order validation helpers
    # ==========================================================================
    CHECKOUT_USER_CART = """
        SELECT c.cart_id, c.status
        FROM cart c
        WHERE c.user_id = ? AND c.status = 'active'
    """
    CHECKOUT_CART_ITEMS_COUNT = """
        SELECT COUNT(*) FROM cart_items ci
        JOIN cart c ON c.cart_id = ci.cart_id
        WHERE c.cart_id = ?
    """
    CHECKOUT_ORDER_CREATED = """
        SELECT COUNT(*) FROM orders
        WHERE user_id = ? AND status = 'pending'
        AND created_at >= datetime('now', '-1 hour')
    """
    CHECKOUT_PAYMENT_LINKED = """
        SELECT COUNT(*) FROM payments p
        JOIN orders o ON o.order_id = p.order_id
        WHERE o.user_id = ? AND p.payment_status = 'pending'
    """

    def __str__(self) -> str:
        """Return the raw SQL string when the enum is used in a string context."""
        return self.value
