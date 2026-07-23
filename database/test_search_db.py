from __future__ import annotations

"""Database validation tests for **Search / Product Discovery**.

Verifies product search by name, description, category, price range,
and availability at the database level.
"""

import pytest

from database.db_helpers import DBHelpers
from database.db_queries import count, fetch_all, fetch_one, fetch_scalar
from database.database_utils import DatabaseUtils
from database.sql_constants import SQLQueries

pytestmark = [
    pytest.mark.database,
    pytest.mark.regression,
    pytest.mark.products,
]


class TestSearchDB:
    """Database-level validation of product search functionality."""

    # ── Search by name ────────────────────────────────────────────────────────

    def test_verify_search_by_full_name(self, db_helpers: DBHelpers) -> None:
        """Verify that searching by full product name returns the matching products.

        Note: 'Backpack' matches both 'Sauce Labs Backpack' and 'Sauce Labs Backpack (Kids)'
        because both contain 'Backpack' in their name.
        """
        results = db_helpers.search_products_by_name("Sauce Labs Backpack")
        # Both 'Sauce Labs Backpack' and 'Sauce Labs Backpack (Kids)' contain 'Backpack'
        assert len(results) >= 1, (
            f"Expected at least 1 result for exact name search, found {len(results)}"
        )
        names = [r["name"] for r in results]
        assert "Sauce Labs Backpack" in names, (
            f"Expected 'Sauce Labs Backpack' in results, got {names}"
        )

    def test_verify_search_by_partial_name(self, db_helpers: DBHelpers) -> None:
        """Verify that searching by partial name returns matching products."""
        results = db_helpers.search_products_by_name("Backpack")
        assert len(results) >= 2, (
            f"Expected at least 2 results for 'Backpack', found {len(results)}"
        )

    def test_verify_search_by_single_word(self) -> None:
        """Verify search by a single common word."""
        results = fetch_all(SQLQueries.SEARCH_PRODUCTS_BY_NAME, ("%Labs%",))
        assert len(results) >= 20, (
            f"Expected at least 20 products matching 'Labs', found {len(results)}"
        )

    def test_verify_search_no_results(self, db_helpers: DBHelpers) -> None:
        """Verify that searching for a non-existent product returns no results."""
        results = db_helpers.search_products_by_name("NonExistentProductXYZ")
        assert len(results) == 0, (
            f"Expected 0 results for non-existent product, found {len(results)}"
        )

    # ── Search by description ─────────────────────────────────────────────────

    def test_verify_search_by_description_keyword(self) -> None:
        """Verify that searching by a description keyword returns results."""
        results = fetch_all(SQLQueries.SEARCH_PRODUCTS_BY_DESCRIPTION, ("%waterproof%",))
        assert len(results) >= 1, (
            f"Expected at least 1 result for 'waterproof', found {len(results)}"
        )

    def test_verify_search_by_description_with_multiple_matches(self) -> None:
        """Verify that common description words return multiple products."""
        results = fetch_all(SQLQueries.SEARCH_PRODUCTS_BY_DESCRIPTION, ("%comfortable%",))
        assert len(results) >= 1, (
            f"Expected at least 1 result for 'comfortable', found {len(results)}"
        )

    # ── Search by category ────────────────────────────────────────────────────

    def test_verify_search_by_category(self, db_utils: DatabaseUtils, known_categories: dict) -> None:
        """Verify that searching products by category returns correct results."""
        electronics = db_utils.get_products_by_category("Electronics")
        assert len(electronics) >= 4, (
            f"Expected at least 4 Electronics products, found {len(electronics)}"
        )
        electronics_cat_id = known_categories["Electronics"]
        for product in electronics:
            assert product["category_id"] == electronics_cat_id, (
                f"Product '{product['name']}' has category_id {product['category_id']}, "
                f"expected {electronics_cat_id} (Electronics)"
            )

    def test_verify_clothing_category_has_products(self, db_utils: DatabaseUtils) -> None:
        """Verify that Clothing category has multiple products."""
        clothing = db_utils.get_products_by_category("Clothing")
        assert len(clothing) >= 5, (
            f"Expected at least 5 Clothing products, found {len(clothing)}"
        )

    # ── Search by price range ─────────────────────────────────────────────────

    def test_verify_search_by_price_range(self, db_utils: DatabaseUtils) -> None:
        """Verify that searching products by price range returns correct results."""
        budget_products = db_utils.get_products_in_price_range(0, 10.00)
        assert len(budget_products) >= 4, (
            f"Expected at least 4 products under $10, found {len(budget_products)}"
        )
        for product in budget_products:
            assert product["price"] <= 10.00, (
                f"Product '{product['name']}' has price {product['price']} > $10"
            )

    def test_verify_search_by_mid_range_price(self, db_utils: DatabaseUtils) -> None:
        """Verify that searching mid-range prices returns correct results."""
        mid_range = db_utils.get_products_in_price_range(10.01, 30.00)
        assert len(mid_range) >= 8, (
            f"Expected at least 8 products in $10-$30 range, found {len(mid_range)}"
        )

    def test_verify_search_by_premium_price(self, db_utils: DatabaseUtils) -> None:
        """Verify that searching premium-priced products returns results."""
        premium = db_utils.get_products_in_price_range(50.00, 1000.00)
        assert len(premium) >= 1, (
            f"Expected at least 1 product over $50, found {len(premium)}"
        )

    # ── Search by availability (in stock) ─────────────────────────────────────

    def test_verify_search_in_stock_products(self, db_helpers: DBHelpers) -> None:
        """Verify that searching for in-stock products returns available products."""
        in_stock = db_helpers.products_in_stock()
        assert len(in_stock) >= 20, (
            f"Expected at least 20 in-stock products, found {len(in_stock)}"
        )

    def test_verify_in_stock_products_have_positive_quantity(self) -> None:
        """Verify that in-stock search only returns products with positive quantity."""
        in_stock = fetch_all(SQLQueries.SEARCH_PRODUCTS_IN_STOCK)
        for product in in_stock:
            qty = fetch_scalar(
                "SELECT quantity FROM inventory WHERE product_id = ?",
                (product["product_id"],),
            )
            assert qty > 0, (
                f"Product '{product['name']}' is in stock but has quantity {qty}"
            )

    # ── Complex / combined search ─────────────────────────────────────────────

    def test_verify_search_case_insensitive(self) -> None:
        """Verify that product search is case-insensitive."""
        results_upper = fetch_all(SQLQueries.SEARCH_PRODUCTS_BY_NAME, ("%BACKPACK%",))
        results_lower = fetch_all(SQLQueries.SEARCH_PRODUCTS_BY_NAME, ("%backpack%",))
        assert len(results_upper) == len(results_lower), (
            f"Case-insensitive search mismatch: upper={len(results_upper)}, lower={len(results_lower)}"
        )

    def test_verify_search_by_description_non_existent(self) -> None:
        """Verify that searching for a non-existent description returns no results."""
        results = fetch_all(
            SQLQueries.SEARCH_PRODUCTS_BY_DESCRIPTION,
            ("%zzz_nonexistent_zzz%",),
        )
        assert len(results) == 0, (
            f"Expected 0 results for non-existent description, found {len(results)}"
        )

    def test_verify_search_returns_all_required_fields(self) -> None:
        """Verify that search results contain all required product fields."""
        results = fetch_all(SQLQueries.SEARCH_PRODUCTS_BY_NAME, ("%Backpack%",))
        for result in results:
            for field in ("product_id", "name", "price", "description", "category_id"):
                assert field in result, (
                    f"Search result missing field '{field}': {result}"
                )

    def test_verify_search_special_characters_safe(self) -> None:
        """Verify that special characters in search terms are handled safely."""
        results = fetch_all(SQLQueries.SEARCH_PRODUCTS_BY_NAME, ("%T-Shirt%",))
        assert len(results) >= 1, (
            f"Expected at least 1 result for 'T-Shirt', found {len(results)}"
        )
