from __future__ import annotations

"""Database setup and seed-data population script.

Run this module directly to create (or reset) the SQLite database::

    python -m database.db_setup

It is safe to re-run — existing tables are dropped and recreated with
fresh sample data.
"""

import logging
import sqlite3
from pathlib import Path
from typing import Any

from database.db_config import DBConfig

logger = logging.getLogger("ecommerce_framework.database.setup")


# ── Schema DDL ─────────────────────────────────────────────────────────────────


SCHEMA_SQL = """
-- ============================================================================
-- E-Commerce Database Schema
-- ============================================================================

PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

-- 1. Categories
CREATE TABLE IF NOT EXISTS categories (
    category_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    name           TEXT    NOT NULL UNIQUE,
    description    TEXT,
    is_active      INTEGER NOT NULL DEFAULT 1,
    created_at     TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- 2. Products
CREATE TABLE IF NOT EXISTS products (
    product_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    name           TEXT    NOT NULL,
    description    TEXT,
    price          REAL    NOT NULL CHECK (price >= 0),
    category_id    INTEGER NOT NULL,
    image_url      TEXT,
    is_active      INTEGER NOT NULL DEFAULT 1,
    created_at     TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (category_id) REFERENCES categories(category_id)
);

-- 3. Users
CREATE TABLE IF NOT EXISTS users (
    user_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    username        TEXT    NOT NULL UNIQUE,
    email           TEXT    NOT NULL UNIQUE,
    password_hash   TEXT    NOT NULL,
    first_name      TEXT,
    last_name       TEXT,
    role            TEXT    NOT NULL DEFAULT 'customer' CHECK (role IN ('admin', 'customer', 'manager')),
    is_active       INTEGER NOT NULL DEFAULT 1,
    account_locked  INTEGER NOT NULL DEFAULT 0,
    login_attempts  INTEGER NOT NULL DEFAULT 0,
    last_login      TEXT,
    created_at      TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- 4. Inventory
CREATE TABLE IF NOT EXISTS inventory (
    inventory_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id     INTEGER NOT NULL UNIQUE,
    quantity       INTEGER NOT NULL DEFAULT 0 CHECK (quantity >= 0),
    reorder_level  INTEGER NOT NULL DEFAULT 10,
    location       TEXT,
    last_restocked TEXT,
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- 5. Cart
CREATE TABLE IF NOT EXISTS cart (
    cart_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL,
    status      TEXT    NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'checked_out', 'abandoned')),
    created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at  TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- 6. Cart Items
CREATE TABLE IF NOT EXISTS cart_items (
    cart_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    cart_id      INTEGER NOT NULL,
    product_id   INTEGER NOT NULL,
    quantity     INTEGER NOT NULL DEFAULT 1 CHECK (quantity > 0),
    added_at     TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (cart_id) REFERENCES cart(cart_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    UNIQUE(cart_id, product_id)
);

-- 7. Orders
CREATE TABLE IF NOT EXISTS orders (
    order_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id       INTEGER NOT NULL,
    status        TEXT    NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled', 'refunded')),
    total_amount  REAL    NOT NULL DEFAULT 0.0,
    coupon_id     INTEGER,
    discount_amount REAL DEFAULT 0.0,
    created_at    TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at    TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (coupon_id) REFERENCES coupons(coupon_id)
);

-- 8. Order Items
CREATE TABLE IF NOT EXISTS order_items (
    order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id      INTEGER NOT NULL,
    product_id    INTEGER NOT NULL,
    quantity      INTEGER NOT NULL CHECK (quantity > 0),
    unit_price    REAL    NOT NULL CHECK (unit_price >= 0),
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- 9. Payments
CREATE TABLE IF NOT EXISTS payments (
    payment_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id        INTEGER NOT NULL,
    amount          REAL    NOT NULL CHECK (amount >= 0),
    payment_method  TEXT    NOT NULL DEFAULT 'credit_card',
    payment_status  TEXT    NOT NULL DEFAULT 'pending' CHECK (payment_status IN ('pending', 'completed', 'failed', 'refunded')),
    transaction_id  TEXT,
    paid_at         TEXT,
    created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);

-- 10. Coupons
CREATE TABLE IF NOT EXISTS coupons (
    coupon_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    code              TEXT    NOT NULL UNIQUE,
    discount_percent  INTEGER NOT NULL CHECK (discount_percent BETWEEN 0 AND 100),
    min_order_amount  REAL    DEFAULT 0.0,
    max_uses          INTEGER DEFAULT NULL,
    usage_count       INTEGER NOT NULL DEFAULT 0,
    is_active         INTEGER NOT NULL DEFAULT 1,
    expiry_date       TEXT,
    created_at        TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- 11. User Sessions
CREATE TABLE IF NOT EXISTS user_sessions (
    session_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id       INTEGER NOT NULL,
    session_token TEXT    NOT NULL UNIQUE,
    ip_address    TEXT,
    is_active     INTEGER NOT NULL DEFAULT 1,
    created_at    TEXT    NOT NULL DEFAULT (datetime('now')),
    last_activity TEXT    NOT NULL DEFAULT (datetime('now')),
    expires_at    TEXT    NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- 12. Wishlist
CREATE TABLE IF NOT EXISTS wishlist (
    wishlist_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id      INTEGER NOT NULL,
    product_id   INTEGER NOT NULL,
    added_at     TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE,
    UNIQUE(user_id, product_id)
);

-- 13. Shipping
CREATE TABLE IF NOT EXISTS shipping (
    shipping_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id           INTEGER NOT NULL UNIQUE,
    address_line1      TEXT    NOT NULL,
    address_line2      TEXT,
    city               TEXT    NOT NULL,
    state              TEXT,
    postal_code        TEXT    NOT NULL,
    country            TEXT    NOT NULL DEFAULT 'USA',
    shipping_method    TEXT    NOT NULL DEFAULT 'standard',
    tracking_number    TEXT,
    delivery_status    TEXT    NOT NULL DEFAULT 'pending' CHECK (delivery_status IN ('pending', 'shipped', 'in_transit', 'delivered', 'failed')),
    estimated_delivery TEXT,
    shipped_at         TEXT,
    delivered_at       TEXT,
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);

-- 14. Reviews
CREATE TABLE IF NOT EXISTS reviews (
    review_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id   INTEGER NOT NULL,
    user_id      INTEGER NOT NULL,
    rating       INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
    title        TEXT,
    review_text  TEXT,
    is_approved  INTEGER NOT NULL DEFAULT 0,
    created_at   TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    UNIQUE(user_id, product_id)
);

-- 15. Audit Logs
CREATE TABLE IF NOT EXISTS audit_logs (
    log_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER,
    action      TEXT    NOT NULL,
    entity_type TEXT,
    entity_id   INTEGER,
    old_value   TEXT,
    new_value   TEXT,
    ip_address  TEXT,
    created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
"""


# ── Sample Data ────────────────────────────────────────────────────────────────


def _seed_categories(cursor: sqlite3.Cursor) -> dict[str, int]:
    """Insert sample categories and return a name→id mapping."""
    categories = [
        ("Electronics", "Electronic devices and accessories"),
        ("Clothing", "Apparel, shoes, and fashion accessories"),
        ("Books", "Physical and digital books across all genres"),
        ("Home & Garden", "Home improvement, furniture, and garden supplies"),
        ("Sports", "Sports equipment, gear, and activewear"),
        ("Food & Beverages", "Gourmet food, beverages, and specialty items"),
        ("Toys & Games", "Children's toys, board games, and puzzles"),
        ("Health & Beauty", "Personal care, cosmetics, and wellness products"),
        ("Automotive", "Car parts, accessories, and maintenance products"),
        ("Office Supplies", "Office equipment, stationery, and supplies"),
    ]
    cursor.executemany(
        "INSERT INTO categories (name, description) VALUES (?, ?)",
        categories,
    )
    return {name: idx + 1 for idx, (name, _) in enumerate(categories)}


def _seed_products(cursor: sqlite3.Cursor, cat: dict[str, int]) -> dict[str, int]:
    """Insert sample products and return a name→id mapping.

    Products mirror the SauceDemo inventory names so DB tests can cross-reference
    with existing UI test constants.
    """
    products = [
        ("Sauce Labs Backpack", "Carry all your essentials with the sleek Sauce Labs Backpack. Durable fabric with padded straps.", 29.99, cat["Clothing"], "backpack.jpg"),
        ("Sauce Labs Bike Light", "A waterproof bike light that keeps you visible in low-light conditions.", 9.99, cat["Sports"], "bike_light.jpg"),
        ("Sauce Labs Bolt T-Shirt", "Premium cotton T-shirt with the Sauce Labs logo. Comfortable and stylish.", 15.99, cat["Clothing"], "bolt_tshirt.jpg"),
        ("Sauce Labs Fleece Jacket", "Warm fleece jacket perfect for cool weather. Lightweight yet insulating.", 49.99, cat["Clothing"], "fleece_jacket.jpg"),
        ("Sauce Labs Onesie", "Ultimate comfort meets style. Perfect for lounging or casual outings.", 29.99, cat["Clothing"], "onesie.jpg"),
        ("Sauce Labs Power Supply", "Universal power supply with multiple adapters. 65W fast charging supported.", 34.99, cat["Electronics"], "power_supply.jpg"),
        ("Sauce Labs Backpack (Kids)", "Mini version of the classic backpack, sized for children ages 5-12.", 19.99, cat["Clothing"], "kids_backpack.jpg"),
        ("Sauce Labs Mug", "15oz ceramic mug with heat-resistant grip. Microwave and dishwasher safe.", 14.99, cat["Home & Garden"], "mug.jpg"),
        ("Sauce Labs Notebook", "Hardcover ruled notebook with 200 pages. Lay-flat binding.", 9.99, cat["Office Supplies"], "notebook.jpg"),
        ("Sauce Labs Running Shorts", "Breathable moisture-wicking shorts with zippered pocket.", 24.99, cat["Sports"], "running_shorts.jpg"),
        ("Test.allTheThings() T-Shirt (Red)", "Classic red tee for developers. Pre-shrunk cotton with screen-printed logo.", 15.99, cat["Clothing"], "test_all_things_red.jpg"),
        ("Sauce Labs Yoga Mat", "Non-slip yoga mat with alignment lines. Includes carrying strap.", 22.99, cat["Sports"], "yoga_mat.jpg"),
        ("Sauce Labs Water Bottle", "Insulated stainless steel water bottle. Keeps drinks cold for 24 hours.", 18.99, cat["Sports"], "water_bottle.jpg"),
        ("Sauce Labs Cookbook", "Collection of 50+ easy recipes from the Sauce Labs team.", 24.99, cat["Books"], "cookbook.jpg"),
        ("Sauce Labs Phone Case", "Shockproof silicone phone case with card holder. Compatible with most phones.", 12.99, cat["Electronics"], "phone_case.jpg"),
        ("Sauce Labs Wireless Earbuds", "True wireless earbuds with active noise cancellation. 8hr battery life.", 79.99, cat["Electronics"], "earbuds.jpg"),
        ("Sauce Labs Hoodie", "Comfortable pullover hoodie with kangaroo pocket and adjustable drawstring.", 39.99, cat["Clothing"], "hoodie.jpg"),
        ("Sauce Labs Desk Lamp", "LED desk lamp with adjustable brightness and color temperature. USB charging port.", 32.99, cat["Office Supplies"], "desk_lamp.jpg"),
        ("Sauce Labs Protein Bar Pack", "Box of 12 protein bars. 20g protein per bar. Chocolate chip flavor.", 22.99, cat["Food & Beverages"], "protein_bars.jpg"),
        ("Sauce Labs Mouse Pad", "Extended mouse pad with stitched edges. Non-slip rubber base.", 9.99, cat["Office Supplies"], "mouse_pad.jpg"),
        ("Sauce Labs Cap", "Adjustable baseball cap with embroidered logo. One size fits most.", 14.99, cat["Clothing"], "cap.jpg"),
        ("Sauce Labs Tumbler", "Vacuum-insulated tumbler with lid and straw. Fits standard cup holders.", 21.99, cat["Home & Garden"], "tumbler.jpg"),
        ("Sauce Labs Bluetooth Speaker", "Portable waterproof Bluetooth speaker. 12hr playtime with deep bass.", 44.99, cat["Electronics"], "speaker.jpg"),
        ("Sauce Labs Stress Ball", "Squeeze away stress with this Sauce Labs branded stress ball.", 4.99, cat["Office Supplies"], "stress_ball.jpg"),
    ]
    cursor.executemany(
        "INSERT INTO products (name, description, price, category_id, image_url) VALUES (?, ?, ?, ?, ?)",
        products,
    )
    return {name: idx + 1 for idx, (name, _, _, _, _) in enumerate(products)}


def _seed_users(cursor: sqlite3.Cursor) -> dict[str, dict[str, Any]]:
    """Insert sample users and return a username→info mapping.

    Includes users that match UI test data for cross-referencing.
    """
    user_data = [
        ("standard_user", "standard@example.com", "$2b$12$LJ3m4ys3Lk0TSwHlXfM", "John", "Doe", "customer", 1, 0, 0, "2026-07-22 14:30:00"),
        ("locked_out_user", "locked@example.com", "$2b$12$LJ3m4ys3Lk0TSwHlXfN", "Jane", "Smith", "customer", 0, 1, 5, "2026-07-20 09:15:00"),
        ("problem_user", "problem@example.com", "$2b$12$LJ3m4ys3Lk0TSwHlXfO", "Bob", "Johnson", "customer", 1, 0, 2, "2026-07-21 11:00:00"),
        ("performance_glitch_user", "glitch@example.com", "$2b$12$LJ3m4ys3Lk0TSwHlXfP", "Alice", "Williams", "customer", 1, 0, 0, "2026-07-22 08:45:00"),
        ("error_user", "error@example.com", "$2b$12$LJ3m4ys3Lk0TSwHlXfQ", "Charlie", "Brown", "customer", 1, 0, 1, "2026-07-21 16:30:00"),
        ("visual_user", "visual@example.com", "$2b$12$LJ3m4ys3Lk0TSwHlXfR", "Diana", "Prince", "customer", 1, 0, 0, "2026-07-22 10:00:00"),
        ("admin_user", "admin@example.com", "$2b$12$LJ3m4ys3Lk0TSwHlXfS", "Bruce", "Wayne", "admin", 1, 0, 0, "2026-07-22 12:00:00"),
        ("manager_user", "manager@example.com", "$2b$12$LJ3m4ys3Lk0TSwHlXfT", "Clark", "Kent", "manager", 1, 0, 0, "2026-07-22 13:00:00"),
        ("inactive_user", "inactive@example.com", "$2b$12$LJ3m4ys3Lk0TSwHlXfU", "Peter", "Parker", "customer", 0, 0, 0, None),
        ("new_user", "new@example.com", "$2b$12$LJ3m4ys3Lk0TSwHlXfV", "Tony", "Stark", "customer", 1, 0, 0, None),
    ]
    cursor.executemany(
        """INSERT INTO users (username, email, password_hash, first_name, last_name, role, is_active, account_locked, login_attempts, last_login)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        user_data,
    )
    return {row[0]: {"id": idx + 1, "email": row[1], "role": row[5]} for idx, row in enumerate(user_data)}


def _seed_inventory(cursor: sqlite3.Cursor, products: dict[str, int]) -> None:
    """Insert stock levels for every product."""
    stock_data = [
        ("Sauce Labs Backpack", 35, 10, "Warehouse A, Aisle 3"),
        ("Sauce Labs Bike Light", 50, 15, "Warehouse A, Aisle 7"),
        ("Sauce Labs Bolt T-Shirt", 120, 20, "Warehouse B, Aisle 1"),
        ("Sauce Labs Fleece Jacket", 25, 10, "Warehouse A, Aisle 5"),
        ("Sauce Labs Onesie", 60, 15, "Warehouse B, Aisle 2"),
        ("Sauce Labs Power Supply", 40, 10, "Warehouse C, Aisle 4"),
        ("Sauce Labs Backpack (Kids)", 15, 10, "Warehouse A, Aisle 3"),
        ("Sauce Labs Mug", 200, 30, "Warehouse B, Aisle 6"),
        ("Sauce Labs Notebook", 150, 25, "Warehouse B, Aisle 8"),
        ("Sauce Labs Running Shorts", 45, 10, "Warehouse A, Aisle 6"),
        ("Test.allTheThings() T-Shirt (Red)", 80, 15, "Warehouse B, Aisle 1"),
        ("Sauce Labs Yoga Mat", 30, 10, "Warehouse A, Aisle 9"),
        ("Sauce Labs Water Bottle", 75, 20, "Warehouse A, Aisle 7"),
        ("Sauce Labs Cookbook", 55, 10, "Warehouse B, Aisle 5"),
        ("Sauce Labs Phone Case", 0, 10, "Warehouse C, Aisle 2"),
        ("Sauce Labs Wireless Earbuds", 20, 5, "Warehouse C, Aisle 1"),
        ("Sauce Labs Hoodie", 40, 10, "Warehouse A, Aisle 4"),
        ("Sauce Labs Desk Lamp", 18, 10, "Warehouse C, Aisle 3"),
        ("Sauce Labs Protein Bar Pack", 100, 20, "Warehouse B, Aisle 7"),
        ("Sauce Labs Mouse Pad", 90, 15, "Warehouse B, Aisle 8"),
        ("Sauce Labs Cap", 65, 10, "Warehouse A, Aisle 2"),
        ("Sauce Labs Tumbler", 35, 10, "Warehouse A, Aisle 5"),
        ("Sauce Labs Bluetooth Speaker", 12, 10, "Warehouse C, Aisle 1"),
        ("Sauce Labs Stress Ball", 250, 50, "Warehouse B, Aisle 9"),
    ]
    for name, qty, reorder, location in stock_data:
        pid = products[name]
        cursor.execute(
            "INSERT INTO inventory (product_id, quantity, reorder_level, location) VALUES (?, ?, ?, ?)",
            (pid, qty, reorder, location),
        )


def _seed_carts(cursor: sqlite3.Cursor, users: dict[str, Any], products: dict[str, int]) -> None:
    """Insert sample carts for a subset of users."""
    cart_data = [
        ("standard_user", "active", [("Sauce Labs Backpack", 2), ("Sauce Labs Bike Light", 1)]),
        ("problem_user", "active", [("Sauce Labs Bolt T-Shirt", 1)]),
        ("visual_user", "active", [("Sauce Labs Fleece Jacket", 1), ("Sauce Labs Mug", 3)]),
        ("admin_user", "checked_out", [("Sauce Labs Notebook", 5)]),
    ]
    for username, status, items in cart_data:
        uid = users[username]["id"]
        cursor.execute(
            "INSERT INTO cart (user_id, status) VALUES (?, ?)",
            (uid, status),
        )
        cart_id = cursor.lastrowid
        for product_name, qty in items:
            pid = products[product_name]
            cursor.execute(
                "INSERT INTO cart_items (cart_id, product_id, quantity) VALUES (?, ?, ?)",
                (cart_id, pid, qty),
            )


def _seed_orders(
    cursor: sqlite3.Cursor,
    users: dict[str, Any],
    products: dict[str, int],
    coupons: list[dict] | None = None,
) -> None:
    """Insert sample orders with items, payments, and shipping."""
    order_defs = [
        ("standard_user", "delivered", 1, [
            ("Sauce Labs Backpack", 1, 29.99),
            ("Sauce Labs Bike Light", 2, 9.99),
        ]),
        ("standard_user", "processing", 2, [
            ("Sauce Labs Bolt T-Shirt", 3, 15.99),
        ]),
        ("admin_user", "delivered", 1, [
            ("Sauce Labs Notebook", 10, 9.99),
            ("Sauce Labs Mouse Pad", 5, 9.99),
        ]),
        ("visual_user", "pending", 1, [
            ("Sauce Labs Yoga Mat", 1, 22.99),
            ("Sauce Labs Water Bottle", 2, 18.99),
        ]),
        ("problem_user", "cancelled", 1, [
            ("Sauce Labs Hoodie", 1, 39.99),
        ]),
        ("manager_user", "shipped", 1, [
            ("Sauce Labs Wireless Earbuds", 1, 79.99),
            ("Sauce Labs Stress Ball", 5, 4.99),
        ]),
    ]
    for username, status, coupon_id, items in order_defs:
        uid = users[username]["id"]
        total = round(sum(qty * price for _, qty, price in items), 2)
        cursor.execute(
            "INSERT INTO orders (user_id, status, total_amount, created_at) VALUES (?, ?, ?, datetime('now', ? || ' days', '-1 day'))",
            (uid, status, total, str(-len(items))),
        )
        oid = cursor.lastrowid

        for product_name, qty, price in items:
            pid = products[product_name]
            cursor.execute(
                "INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (?, ?, ?, ?)",
                (oid, pid, qty, price),
            )

        # Payment
        pay_status = "completed" if status in ("delivered", "processing", "shipped") else ("pending" if status == "pending" else "refunded" if status == "cancelled" else "pending")
        cursor.execute(
            "INSERT INTO payments (order_id, amount, payment_method, payment_status, paid_at) VALUES (?, ?, 'credit_card', ?, CASE WHEN ? = 'completed' THEN datetime('now', '-1 hour') ELSE NULL END)",
            (oid, total, pay_status, pay_status),
        )

        # Shipping
        if status != "cancelled":
            cursor.execute(
                """INSERT INTO shipping (order_id, address_line1, city, state, postal_code, country,
                   shipping_method, tracking_number, delivery_status, estimated_delivery)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now', '+5 days'))""",
                (oid, f"{123 + oid} Main Street", "San Francisco", "CA", f"941{0o5 + oid:02d}", "USA",
                 "standard", f"1Z{oid:09d}US", "delivered" if status == "delivered" else ("shipped" if status in ("processing", "shipped") else "pending")),
            )


def _seed_coupons(cursor: sqlite3.Cursor) -> list[dict]:
    """Insert sample coupon codes."""
    coupons = [
        ("WELCOME10", 10, 20.0, 1000, 0, 1, "2027-12-31"),
        ("SAVE20", 20, 50.0, 500, 0, 1, "2027-12-31"),
        ("FREESHIP", 5, 0.0, 100, 0, 1, "2027-06-30"),
        ("HALFOFF", 50, 100.0, 50, 0, 1, "2026-12-31"),
        ("EXCLUSIVE25", 25, 75.0, 200, 0, 1, "2027-09-30"),
        ("EXPIRED10", 10, 0.0, None, 5, 1, "2025-01-01"),
        ("MAXEDOUT", 15, 25.0, 100, 100, 0, "2027-12-31"),
        ("WELCOME5", 5, 10.0, 500, 150, 1, "2027-12-31"),
    ]
    cursor.executemany(
        """INSERT INTO coupons (code, discount_percent, min_order_amount, max_uses, usage_count, is_active, expiry_date)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        coupons,
    )
    return [{"code": c[0], "discount": c[1]} for c in coupons]


def _seed_sessions(cursor: sqlite3.Cursor, users: dict[str, Any]) -> None:
    """Insert sample user sessions.

    Active sessions use ``datetime('now', '+1 day')`` so they always have
    future expiry dates regardless of when the DB is seeded.
    """
    sessions = [
        ("standard_user", "tok_std_abc123", "192.168.1.10", 1, "datetime('now', '-1 day')", "datetime('now', '-1 day')", "datetime('now', '+1 day')"),
        ("problem_user", "tok_prob_def456", "192.168.1.20", 1, "datetime('now', '-2 days')", "datetime('now', '-2 days')", "datetime('now', '+1 day')"),
        ("admin_user", "tok_admin_ghi789", "10.0.0.1", 1, "datetime('now', '-1 day')", "datetime('now', '-1 day')", "datetime('now', '+2 days')"),
        ("inactive_user", "tok_inact_jkl012", "192.168.1.30", 0, "datetime('now', '-4 days')", "datetime('now', '-4 days')", "datetime('now', '-3 days')"),
        ("error_user", "tok_err_mno345", "192.168.1.40", 1, "datetime('now', '-2 days')", "datetime('now', '-2 days')", "datetime('now', '+1 day')"),
    ]
    for username, token, ip, active, created, last, expires in sessions:
        uid = users[username]["id"]
        cursor.execute(
            f"INSERT INTO user_sessions (user_id, session_token, ip_address, is_active, created_at, last_activity, expires_at) "
            f"VALUES (?, ?, ?, ?, {created}, {last}, {expires})",
            (uid, token, ip, active),
        )


def _seed_wishlist(cursor: sqlite3.Cursor, users: dict[str, Any], products: dict[str, int]) -> None:
    """Insert sample wishlist entries."""
    wishlist_data = [
        ("standard_user", "Sauce Labs Fleece Jacket"),
        ("standard_user", "Sauce Labs Wireless Earbuds"),
        ("standard_user", "Sauce Labs Yoga Mat"),
        ("visual_user", "Sauce Labs Backpack"),
        ("visual_user", "Sauce Labs Hoodie"),
        ("problem_user", "Sauce Labs Bluetooth Speaker"),
        ("performance_glitch_user", "Sauce Labs Cookbook"),
        ("performance_glitch_user", "Sauce Labs Desk Lamp"),
    ]
    for username, product_name in wishlist_data:
        uid = users[username]["id"]
        pid = products[product_name]
        cursor.execute(
            "INSERT OR IGNORE INTO wishlist (user_id, product_id) VALUES (?, ?)",
            (uid, pid),
        )


def _seed_reviews(cursor: sqlite3.Cursor, users: dict[str, Any], products: dict[str, int]) -> None:
    """Insert sample product reviews."""
    reviews = [
        ("standard_user", "Sauce Labs Backpack", 5, "Great backpack!", "Spacious and durable. Highly recommend.", 1),
        ("standard_user", "Sauce Labs Bike Light", 4, "Good light", "Bright enough for night rides. Battery lasts long.", 1),
        ("problem_user", "Sauce Labs Backpack", 2, "Not great", "Zipper broke after a week.", 0),
        ("visual_user", "Sauce Labs Fleece Jacket", 5, "Love it!", "Super warm and comfortable. Great fit.", 1),
        ("visual_user", "Sauce Labs Mug", 4, "Nice mug", "Keeps coffee hot. Design could be better.", 1),
        ("admin_user", "Sauce Labs Notebook", 5, "Perfect notebook", "Great quality paper. Love the hardcover.", 1),
        ("admin_user", "Sauce Labs Mouse Pad", 4, "Good mouse pad", "Large enough for gaming. Stitching is clean.", 1),
        ("error_user", "Sauce Labs Bolt T-Shirt", 3, "Decent shirt", "Fabric is soft but runs slightly small.", 0),
        ("performance_glitch_user", "Sauce Labs Water Bottle", 5, "Excellent bottle", "Keeps water cold all day. No leaks.", 1),
        ("performance_glitch_user", "Sauce Labs Power Supply", 4, "Works well", "Charges all my devices. Compact design.", 1),
    ]
    for username, product_name, rating, title, text, approved in reviews:
        uid = users[username]["id"]
        pid = products[product_name]
        cursor.execute(
            "INSERT OR IGNORE INTO reviews (product_id, user_id, rating, title, review_text, is_approved) VALUES (?, ?, ?, ?, ?, ?)",
            (pid, uid, rating, title, text, approved),
        )


def _seed_audit_logs(cursor: sqlite3.Cursor, users: dict[str, Any]) -> None:
    """Insert sample audit log entries."""
    logs = [
        ("admin_user", "USER_LOGIN", "user", None, None, "192.168.1.1"),
        ("admin_user", "PRODUCT_CREATE", "product", "Sauce Labs Hoodie", None, "192.168.1.1"),
        ("standard_user", "USER_LOGIN", "user", None, None, "192.168.1.10"),
        ("standard_user", "ORDER_CREATE", "order", None, None, "192.168.1.10"),
        ("standard_user", "CART_UPDATE", "cart", None, None, "192.168.1.10"),
        ("problem_user", "USER_LOGIN", "user", None, None, "192.168.1.20"),
        ("problem_user", "LOGIN_FAILED", "user", None, None, "192.168.1.20"),
        ("admin_user", "USER_UPDATE", "user", "standard_user", "role: customer->manager", "10.0.0.1"),
        ("visual_user", "USER_LOGIN", "user", None, None, "192.168.1.30"),
        ("visual_user", "WISHLIST_ADD", "wishlist", "Sauce Labs Backpack", None, "192.168.1.30"),
        ("admin_user", "COUPON_CREATE", "coupon", "WELCOME10", None, "10.0.0.1"),
        ("error_user", "USER_LOGIN", "user", None, None, "192.168.1.40"),
        ("error_user", "LOGIN_FAILED", "user", None, None, "192.168.1.40"),
    ]
    for username, action, entity_type, entity_id, new_value, ip in logs:
        uid = users[username]["id"]
        cursor.execute(
            "INSERT INTO audit_logs (user_id, action, entity_type, entity_id, new_value, ip_address) VALUES (?, ?, ?, ?, ?, ?)",
            (uid, action, entity_type, entity_id, new_value, ip),
        )


# ── Main Orchestration ─────────────────────────────────────────────────────────


def create_database(database_path: Path | None = None) -> Path:
    """Create the SQLite database with full schema and sample data.

    Args:
        database_path: Optional override for the database file path.
                       Defaults to ``DBConfig.DATABASE_PATH``.

    Returns:
        The path to the created database file.

    Raises:
        sqlite3.Error: If any database operation fails.
    """
    db_path = database_path or DBConfig.DATABASE_PATH
    db_path.parent.mkdir(parents=True, exist_ok=True)

    logger.info("Creating database at: %s", db_path)

    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA foreign_keys = ON")

    try:
        cursor = conn.cursor()

        # ── Create schema ─────────────────────────────────────────────────────
        logger.info("Creating schema tables...")
        cursor.executescript(SCHEMA_SQL)
        conn.commit()

        # ── Seed data ─────────────────────────────────────────────────────────
        logger.info("Seeding sample data...")

        categories = _seed_categories(cursor)
        logger.info("  ✓ %d categories seeded", len(categories))

        products = _seed_products(cursor, categories)
        logger.info("  ✓ %d products seeded", len(products))

        users = _seed_users(cursor)
        logger.info("  ✓ %d users seeded", len(users))

        _seed_inventory(cursor, products)
        logger.info("  ✓ Inventory seeded for %d products", len(products))

        _seed_coupons(cursor)
        logger.info("  ✓ Coupons seeded")

        _seed_carts(cursor, users, products)
        logger.info("  ✓ Cart data seeded")

        _seed_orders(cursor, users, products)
        logger.info("  ✓ Orders, payments, and shipping seeded")

        _seed_sessions(cursor, users)
        logger.info("  ✓ User sessions seeded")

        _seed_wishlist(cursor, users, products)
        logger.info("  ✓ Wishlist data seeded")

        _seed_reviews(cursor, users, products)
        logger.info("  ✓ Reviews seeded")

        _seed_audit_logs(cursor, users)
        logger.info("  ✓ Audit logs seeded")

        conn.commit()
        logger.info("Database setup complete: %s", db_path)

    except sqlite3.Error:
        conn.rollback()
        logger.exception("Database setup failed — transaction rolled back")
        raise
    finally:
        conn.close()

    return db_path


def reset_database(database_path: Path | None = None) -> Path:
    """Drop and recreate the database with fresh sample data.

    This deletes the existing database file, then runs :func:`create_database`.

    Args:
        database_path: Optional override for the database file path.

    Returns:
        The path to the recreated database file.
    """
    db_path = database_path or DBConfig.DATABASE_PATH
    if db_path.exists():
        db_path.unlink()
        logger.info("Existing database deleted: %s", db_path)
    return create_database(db_path)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    )
    reset_database()
