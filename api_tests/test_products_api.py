from __future__ import annotations

from typing import Any

import pytest

from api.api_assertions import APIAssertions
from api.api_client import APIClient
from api.endpoints import APIEndpoints
from api.api_helpers import APIHelpers
from models.product import Product


pytestmark = [
    pytest.mark.api,
    pytest.mark.regression,
    pytest.mark.inventory,
    pytest.mark.products,
]


class TestProductsAPI:
    """Test product catalogue API endpoints.

    Covers listing all products, fetching a single product, and searching.
    """

    @pytest.mark.smoke
    def test_get_all_products(self, api_client: APIClient, api_test_data: dict[str, Any]) -> None:
        """Test 3: GET /products returns a list of products.

        Validates:
            - 200 OK
            - Response is a non-empty list
            - Each item contains required product fields
            - List length >= minimum expected count
            - Response time is acceptable
        """
        # Act
        response = api_client.get(APIEndpoints.products())

        # Assert — status code
        APIAssertions.assert_status_ok(response)

        # Assert — body is a non-empty list
        APIAssertions.assert_json_not_empty(response)
        APIAssertions.assert_list_length(response, min_length=api_test_data["min_products_expected"])

        # Assert — each product has the expected structure
        body: list[dict[str, Any]] = response.json()
        for product_data in body:
            product = Product.from_dict(product_data)
            assert product.id > 0, f"Product id must be positive, got {product.id}"
            assert product.title, f"Product title must not be empty for id={product.id}"
            assert product.price >= 0, f"Product price must be >= 0 for id={product.id}"

        # Assert — response time
        APIAssertions.assert_response_time_less_than(
            response,
            api_test_data["max_acceptable_response_time_seconds"],
        )

        # Assert — schema
        APIAssertions.assert_valid_schema(response, "products_list_schema")

    @pytest.mark.smoke
    def test_get_product_by_id(self, api_client: APIClient, api_test_data: dict[str, Any]) -> None:
        """Test 4: GET /products/:id returns a single product.

        Validates:
            - 200 OK
            - Response is a product object with matching ID
            - All required fields present
            - Conforms to product schema
        """
        # Arrange
        product_id: int = api_test_data["existing_product_id"]

        # Act
        response = api_client.get(APIEndpoints.product_by_id(product_id))

        # Assert — status code
        APIAssertions.assert_status_ok(response)

        # Assert — body structure
        APIAssertions.assert_json_not_empty(response)
        APIAssertions.assert_json_has_keys(response, ["id", "title", "price", "description", "category", "images"])
        APIAssertions.assert_json_value(response, "id", product_id)
        APIAssertions.assert_id_is_positive(response)

        # Assert — schema
        APIAssertions.assert_valid_schema(response, "product_schema")

        # Assert — response time
        APIAssertions.assert_response_time_less_than(
            response,
            api_test_data["max_acceptable_response_time_seconds"],
        )

    @pytest.mark.regression
    def test_search_products(self, api_client: APIClient, api_test_data: dict[str, Any]) -> None:
        """Test 5: Search products by keyword.

        The Platzi API supports title-based filtering via query params
        (e.g. ``/products?title=Classic``).

        Validates:
            - 200 OK
            - Response is a non-empty list
            - At least one result title contains the search keyword
        """
        # Arrange
        keyword = api_test_data["search_keyword"]

        # Act — note: this API uses query params, not a separate search endpoint
        response = api_client.get(APIEndpoints.products(), params={"title": keyword})

        # Assert
        APIAssertions.assert_status_ok(response)
        APIAssertions.assert_json_not_empty(response)
        APIAssertions.assert_list_length(response, min_length=1)

        body: list[dict[str, Any]] = response.json()
        titles = [p.get("title", "").lower() for p in body]
        assert any(keyword.lower() in title for title in titles), (
            f"Expected at least one product title containing '{keyword}', "
            f"found none. Titles: {titles[:5]}"
        )

        APIAssertions.assert_valid_schema(response, "products_list_schema")

    @pytest.mark.regression
    def test_get_products_with_pagination(self, api_client: APIClient) -> None:
        """GET /products supports pagination via offset & limit query params."""
        # Act
        response = api_client.get(APIEndpoints.products(), params={"offset": 0, "limit": 3})

        # Assert
        APIAssertions.assert_status_ok(response)
        body: list[dict[str, Any]] = response.json()
        assert len(body) <= 3, f"Expected <= 3 items with limit=3, got {len(body)}"
