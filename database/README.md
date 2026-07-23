# 🗄️ Database Testing Module

> **Enterprise-grade SQLite database validation for the E-Commerce Automation Framework.**
> 15 business modules · 180+ validation tests · Production-ready

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Database Schema](#-database-schema)
- [Architecture](#-architecture)
- [Folder Structure](#-folder-structure)
- [Setup](#-setup)
- [Execution](#-execution)
- [Adding New Tests](#-adding-new-tests)
- [Best Practices](#-best-practices)
- [Test Modules](#-test-modules)
- [CI/CD Integration](#-cicd-integration)
- [Reporting](#-reporting)

---

## 📌 Overview

This module adds **direct database validation** to the existing Selenium + PyTest automation framework. Rather than relying solely on UI or API layers to verify data integrity, these tests connect directly to the SQLite database to validate:

- **Data integrity** — foreign keys, constraints, unique values
- **Business rules** — pricing, stock levels, coupon validity
- **State transitions** — order lifecycle, cart checkout flow
- **Reference data** — product catalog, user accounts, categories

The database is **self-contained SQLite** — no external server required. It is automatically created and seeded with realistic e-commerce data on first test execution.

---

## 🏛️ Database Schema

The database (`ecommerce.db`) contains **15 tables** modeling a complete e-commerce platform:

| # | Table | Key Columns | Business Purpose |
|---|-------|-------------|------------------|
| 1 | `categories` | category_id, name, is_active | Product categorization |
| 2 | `products` | product_id, name, price, category_id | Product catalog (24 products) |
| 3 | `users` | user_id, username, email, role, is_active | User accounts (10 users) |
| 4 | `inventory` | inventory_id, product_id, quantity, reorder_level | Stock management |
| 5 | `cart` | cart_id, user_id, status | Shopping cart headers |
| 6 | `cart_items` | cart_item_id, cart_id, product_id, quantity | Individual cart line items |
| 7 | `orders` | order_id, user_id, status, total_amount | Order headers (6 orders) |
| 8 | `order_items` | order_item_id, order_id, product_id, quantity, unit_price | Order line items |
| 9 | `payments` | payment_id, order_id, amount, payment_status | Payment transactions |
| 10 | `coupons` | coupon_id, code, discount_percent, is_active | Discount codes (8 coupons) |
| 11 | `user_sessions` | session_id, user_id, session_token, is_active | Login session tracking |
| 12 | `wishlist` | wishlist_id, user_id, product_id | User wishlists |
| 13 | `shipping` | shipping_id, order_id, delivery_status | Order shipping info |
| 14 | `reviews` | review_id, product_id, user_id, rating, is_approved | Product reviews (10 reviews) |
| 15 | `audit_logs` | log_id, user_id, action, created_at | Change tracking |

### Entity-Relationship Diagram

```
    ┌──────────┐       ┌────────────┐       ┌───────────┐
    │  users   │──1:N──│    cart    │──1:N──│ cart_items│
    └────┬─────┘       └────────────┘       └─────┬─────┘
         │                                        │
         │                                  ┌─────┴──────┐
         ├──1:N──┐                          │  products  │
         │       │                          └──────┬─────┘
    ┌────┴─────┐                                   │
    │  orders  │──1:N──┐                     ┌──────┴──────┐
    └────┬─────┘      │                     │  inventory  │
         │            ├── order_items ──1:1─┘             │
         │            │                     └─────────────┘
    ┌────┴─────┐      │
    │ payments │      │                     ┌────────────┐
    └──────────┘      │                     │ categories │
                      │                     └──────┬─────┘
    ┌──────────┐      │                            │
    │ shipping │      │                     ┌──────┴──────┐
    └──────────┘      │                     │  reviews    │
                      │                     └─────────────┘
    ┌──────────┐      │
    │ coupons  │──1:N─┘                ┌──────────────┐
    └──────────┘                       │ user_sessions│
                                       └──────┬───────┘
    ┌───────────┐                             │
    │ wishlist  │                             │
    └─────┬─────┘                       ┌─────┴──────┐
          │                             │ audit_logs │
          └─────────────────────────────└────────────┘
```

---

## 🏗️ Architecture

The database testing module follows the same **enterprise design patterns** as the existing framework:

### Design Principles

| Principle | Implementation |
|-----------|---------------|
| **Single Responsibility** | Each file has one purpose: `db_connection.py` manages connections, `db_queries.py` executes queries, `db_helpers.py` provides assertions |
| **DRY (Don't Repeat Yourself)** | All SQL is centralized in `sql_constants.py` — no raw SQL in test methods |
| **Separation of Concerns** | Tests call helper methods, helpers call query methods, queries reference constants |
| **Dependency Injection** | PyTest fixtures inject `db_helpers`, `db_utils`, `known_products` into tests |
| **Reusability** | Helper methods are static and shared across all test files |
| **Configurability** | Database path, timeout, and settings are in `db_config.py` |

### Data Flow

```
Test Method
    ↓  calls
DBHelpers / DatabaseUtils (static methods)
    ↓  calls
db_queries.py (fetch_scalar, fetch_one, fetch_all, count, exists)
    ↓  calls
db_connection.py (connection_context, get_connection)
    ↓
SQLite Database (ecommerce.db)
```

### Why This Architecture?

- ✅ **No SQL in tests** — tests are declarative: "what" not "how"
- ✅ **Reusable across files** — every test file shares the same helpers
- ✅ **Easy to refactor** — change SQL in one place, all tests benefit
- ✅ **Type-safe** — full type hints on every function
- ✅ **Self-documenting** — method names describe the business intent

---

## 📁 Folder Structure

```
database/
├── __init__.py           # Package exports
├── conftest.py           # PyTest fixtures (db_helpers, db_utils, known_products, etc.)
├── db_config.py          # Database path, timeout, WAL mode settings
├── db_connection.py      # Connection manager with context manager + singleton
├── db_helpers.py         # 50+ reusable assertion/validation methods
├── db_queries.py         # Query execution (fetch_scalar, fetch_one, fetch_all, etc.)
├── db_setup.py           # Schema creation + sample data seeding script
├── database_utils.py     # Utility functions (search, sort, coupon validation, etc.)
├── sql_constants.py      # ALL SQL queries as enum members
├── README.md             # This file
│
├── test_login_db.py      # 14 tests — user accounts, login validation
├── test_products_db.py   # 14 tests — product catalog, pricing, images
├── test_inventory_db.py  # 14 tests — stock levels, reorder points, warehouses
├── test_cart_db.py       # 14 tests — cart items, quantities, totals
├── test_checkout_db.py   # 14 tests — checkout flow, cart-to-order conversion
├── test_orders_db.py     # 14 tests — order lifecycle, statuses, totals
├── test_order_items_db.py# 14 tests — line items, pricing, product linkage
├── test_users_db.py      # 14 tests — user profiles, roles, account status
├── test_payments_db.py   # 14 tests — payment records, amounts, revenue
├── test_search_db.py     # 14 tests — product search, filtering
├── test_sorting_db.py    # 14 tests — sort by name, price, stability
├── test_sessions_db.py   # 14 tests — user sessions, tokens, expiry
├── test_coupons_db.py    # 14 tests — coupon codes, discounts, validity
├── test_reviews_db.py    # 14 tests — reviews, ratings, moderation
└── test_wishlist_db.py   # 14 tests — wishlist items, user-product pairs
```

---

## ⚙️ Setup

### Automatic Setup

The database is automatically created on first test run via the `db_setup` fixture in `conftest.py`. No manual steps required.

### Manual Setup

To (re)create the database manually:

```bash
python -m database.db_setup
```

This will:
1. Create `database/ecommerce.db` (or the path specified by `DB_PATH` env var)
2. Create all 15 tables with proper schema
3. Seed 24 products, 10 users, 6 orders, 8 coupons, 10 reviews, and more

### Environment Variables

All database settings are configurable via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_FILENAME` | `ecommerce.db` | Database file name |
| `DB_PATH` | `database/ecommerce.db` | Full database path |
| `DB_TIMEOUT` | `10` | Connection timeout (seconds) |
| `DB_RETRIES` | `3` | Connection retry count |
| `DB_WAL_MODE` | `true` | Enable WAL journal mode |
| `DB_FOREIGN_KEYS` | `true` | Enable foreign key enforcement |

---

## 🚀 Execution

### Run All Database Tests

```bash
pytest database/
```

### Run Specific Module

```bash
pytest database/test_products_db.py
pytest database/test_login_db.py
pytest database/test_orders_db.py
```

### Run by Marker

```bash
pytest -m database
pytest -m "database and smoke"
pytest -m "database and regression and login"
```

### Using the Unified Runner

```bash
python run_tests.py --suite=db           # Database tests only
python run_tests.py --suite=db --db-reset  # Reset DB then run tests
python run_tests.py --suite=all          # UI + API + DB
```

### Combined with Existing Tests

```bash
pytest tests/ database/                  # UI + DB tests
pytest api_tests/ database/ -n auto      # API + DB in parallel
python run_tests.py --suite=all          # Everything
```

---

## 🧪 Adding New Tests

### 1. Add SQL (if new query needed)

In `sql_constants.py`:

```python
class SQLQueries(str, Enum):
    PRODUCT_STOCK_STATUS = """
        SELECT p.name, i.quantity
        FROM products p
        JOIN inventory i ON i.product_id = p.product_id
        WHERE i.quantity > ?
        ORDER BY p.name
    """
```

### 2. Add Helper Method (in `db_helpers.py`)

```python
@staticmethod
def products_with_stock_above(min_qty: int) -> list[dict[str, Any]]:
    return fetch_all(SQLQueries.PRODUCT_STOCK_STATUS, (min_qty,))
```

### 3. Write Test (in the appropriate module)

```python
def test_verify_products_with_high_stock(self, db_helpers: DBHelpers) -> None:
    results = db_helpers.products_with_stock_above(50)
    assert len(results) >= 1, "Expected at least 1 product with stock > 50"
    for result in results:
        assert result["quantity"] > 50, f"{result['name']} has qty {result['quantity']}"
```

### Key Guidelines

- ✅ **Never write SQL in test methods** — use helpers or `SQLQueries`
- ✅ **Use type hints** on all parameters and return types
- ✅ **Write descriptive assertion messages** — they appear in test reports
- ✅ **Use fixtures** from `conftest.py` (`db_helpers`, `db_utils`, `known_products`)
- ✅ **One assertion concept per test** — focus on a single validation
- ✅ **Use the `database` marker** on every test class
- ❌ **Don't hardcode IDs** — use `known_products` or `known_users` fixtures
- ❌ **Don't modify the database** — tests are read-only by design

---

## ✅ Best Practices

### Naming Conventions

- **Files**: `test_<module>_db.py` (e.g., `test_products_db.py`)
- **Classes**: `Test<Module>DB` (e.g., `TestProductsDB`)
- **Methods**: `test_verify_<business_rule>()` (e.g., `test_verify_product_price()`)
- **Helpers**: `<action>_<entity>()` (e.g., `user_exists()`, `product_price()`)
- **SQL Constants**: `<TABLE>_<ACTION>` (e.g., `PRODUCT_PRICE`, `USER_LOGIN_ATTEMPTS`)

### Test Structure

Each test should follow the **Arrange-Act-Assert** pattern:

```python
def test_verify_product_price(self, db_helpers: DBHelpers) -> None:
    # Act
    actual = db_helpers.product_price("Sauce Labs Backpack")
    expected = 29.99
    # Assert
    assert actual == expected, (
        f"Expected price {expected}, got {actual}"
    )
```

### Assertion Messages

Always provide descriptive messages that:
- State what was expected
- Show what was actually found
- Include context (product name, ID, etc.)

### Fixture Usage

| Fixture | Purpose | Example |
|---------|---------|---------|
| `db_helpers` | Static assertion methods | `db_helpers.product_price("Backpack")` |
| `db_utils` | Utility/aggregation methods | `db_utils.calculate_order_total(1)` |
| `known_products` | Dict of name → product_id | `known_products["Backpack"]` |
| `known_users` | Dict of username → user info | `known_users["standard_user"]["user_id"]` |
| `known_categories` | Dict of name → category_id | `known_categories["Clothing"]` |
| `product_names` | Sorted list of all product names | Iterate for data-driven tests |
| `category_names` | Sorted list of all category names | Use with parameterized tests |

---

## 📊 Test Modules

| Module | File | Tests | Focus |
|--------|------|-------|-------|
| Login | `test_login_db.py` | 14 | User existence, status, roles, password constraints |
| Products | `test_products_db.py` | 14 | Product catalog, pricing, descriptions, categories |
| Inventory | `test_inventory_db.py` | 14 | Stock levels, reorder thresholds, warehouse locations |
| Cart | `test_cart_db.py` | 14 | Cart items, quantities, totals, cart lifecycle |
| Checkout | `test_checkout_db.py` | 14 | Cart-to-order conversion, payment linkage, shipping |
| Orders | `test_orders_db.py` | 14 | Order lifecycle, statuses, totals, timestamps |
| Order Items | `test_order_items_db.py` | 14 | Line items, unit prices, product references |
| Users | `test_users_db.py` | 14 | User profiles, roles, account status, email validation |
| Payments | `test_payments_db.py` | 14 | Payment records, statuses, amounts, revenue |
| Search | `test_search_db.py` | 14 | Name search, description search, price range, category |
| Sorting | `test_sorting_db.py` | 14 | Sort by name (A→Z, Z→A), price (low→high, high→low) |
| Sessions | `test_sessions_db.py` | 14 | Session tokens, activity tracking, expiry |
| Coupons | `test_coupons_db.py` | 14 | Discount codes, percentages, usage limits, validity |
| Reviews | `test_reviews_db.py` | 14 | Ratings, approval workflow, duplicate prevention |
| Wishlist | `test_wishlist_db.py` | 14 | Wishlist items, user-product pairs, timestamps |
| **Total** | **15 modules** | **210 tests** | **Comprehensive database validation** |

---

## 🤖 CI/CD Integration

### GitHub Actions

Add this job to `.github/workflows/selenium-tests.yml`:

```yaml
database-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r requirements.txt
      - run: python -m pytest database/ -m database --html=reports/db-report.html --self-contained-html
      - uses: actions/upload-artifact@v4
        with:
          name: db-reports
          path: reports/**
```

### Jenkins

Add to the `Jenkinsfile`:

```groovy
stage('DB — Database Tests') {
    agent any
    steps {
        sh 'pip install -r requirements.txt'
        sh 'python -m pytest database/ -m database --junitxml=reports/db-junit.xml --html=reports/db-report.html'
    }
    post {
        always {
            junit testResults: 'reports/db-junit.xml'
            publishHTML(target: [
                reportName: 'Database Test Report',
                reportDir: 'reports',
                reportFiles: 'db-report.html'
            ])
        }
    }
}
```

---

## 📈 Reporting

Database tests automatically integrate with the existing reporting system:

- **HTML Reports** — failures include descriptive assertion messages
- **JUnit XML** — CI tool integration
- **Execution Log** — all queries and assertions are logged
- **Console Output** — real-time test progress with assertion details

### Example HTML Report Entry

```
TEST: test_verify_product_price FAILED
├── File: database/test_products_db.py::TestProductsDB::test_verify_product_price
├── Message: Expected price 29.99 for 'Sauce Labs Backpack', got 19.99
└── Duration: 0.023s
```

---

## 🛠️ Maintenance

### Resetting the Database

```bash
python -m database.db_setup
```

Or with the runner:

```bash
python run_tests.py --suite=db --db-reset
```

### Verifying Database Integrity

```sql
-- Run these queries to manually check integrity
PRAGMA integrity_check;
PRAGMA foreign_key_check;
```

### Adding Sample Data

Edit `database/db_setup.py` and add to the relevant `_seed_*()` function, then rerun:

```bash
python -m database.db_setup
```

---

## 🔗 Integration Points

The database module integrates seamlessly with existing framework components:

| Component | Integration |
|-----------|-------------|
| **pytest.ini** | `testpaths` includes `database`, `database` marker defined |
| **conftest.py** | No changes needed — database tests have their own `conftest.py` |
| **run_tests.py** | `--suite=db` option added |
| **reporting** | Uses the same `pytest-html` and JUnit XML mechanism |
| **logging** | Logger name `ecommerce_framework.database.*` for filtering |
| **CI/CD** | Can be added as a separate job to GitHub Actions and Jenkins |

---

<div align="center">

**Database Testing Module v1.0**

*Built with ❤️ using Python, SQLite, PyTest, and Enterprise SDET best practices*

</div>
