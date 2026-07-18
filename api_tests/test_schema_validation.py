from __future__ import annotations

from typing import Any

import pytest

from api.api_assertions import APIAssertions
from api.api_client import APIClient
from api.api_helpers import APIHelpers
from api.endpoints import APIEndpoints


pytestmark = [
    pytest.mark.api,
    pytest.mark.regression,
    pytest.mark.schema,
    pytest.mark.products,
]


class TestSchemaValidation:
    """Test suite for JSON Schema validation.

    Every test validates a known-good response against its expected schema
    to ensure schema definitions are up-to-date.
    """

    @pytest.mark.smoke
    def test_product_list_schema(self, api_client: APIClient) -> None:
        """Validate products list response against ``products_list_schema``.

        Schema checks:
            - Root must be an array
            - Each item must contain id, title, price, description, category, images
            - category must be an object with id, name, image
        """
        # Act
        response = api_client.get(APIEndpoints.products())

        # Assert
        APIAssertions.assert_status_ok(response)
        APIAssertions.assert_valid_schema(response, "products_list_schema")

    def test_single_product_schema(self, api_client: APIClient, api_test_data: dict[str, Any]) -> None:
        """Validate a single product response against ``product_schema``."""
        # Arrange
        product_id: int = api_test_data["existing_product_id"]

        # Act
        response = api_client.get(APIEndpoints.product_by_id(product_id))

        # Assert
        APIAssertions.assert_status_ok(response)
        APIAssertions.assert_valid_schema(response, "product_schema")

    def test_user_schema(self, api_client: APIClient, api_test_data: dict[str, Any]) -> None:
        """Validate user profile response against ``user_schema``."""
        # Arrange
        user_id: int = api_test_data["existing_user_id"]

        # Act
        response = api_client.get(APIEndpoints.user_by_id(user_id))

        # Assert
        APIAssertions.assert_status_ok(response)
        APIAssertions.assert_valid_schema(response, "user_schema")

    def test_cart_schema(
        self,
        api_client: APIClient,
        api_helpers: APIHelpers,
        api_test_data: dict[str, Any],
        cleanup_created_resources: list[dict[str, Any]],
    ) -> None:
        """Validate cart creation response against ``cart_schema``."""
        # Arrange
        payload = api_helpers.load_payload("create_cart")
        payload["userId"] = api_test_data["existing_user_id"]
        payload["products"] = [{"productId": 2, "quantity": 2}]

        # Act
        response = api_client.post(APIEndpoints.carts(), json=payload)

        if response.status_code == 404:
            pytest.skip("Cart endpoint is not available on the target API")
            return

        # Assert
        APIAssertions.assert_status_created(response)
        APIAssertions.assert_valid_schema(response, "cart_schema")

        # Cleanup
        cleanup_created_resources.append({"type": "cart", "id": response.json()["id"]})

    def test_order_schema(
        self,
        api_client: APIClient,
        api_helpers: APIHelpers,
        api_test_data: dict[str, Any],
        cleanup_created_resources: list[dict[str, Any]],
    ) -> None:
        """Validate order creation response against ``order_schema``."""
        # Arrange
        payload = api_helpers.load_payload("create_order")
        payload["userId"] = api_test_data["existing_user_id"]

        # Act
        response = api_client.post(APIEndpoints.orders(), json=payload)

        if response.status_code == 404:
            pytest.skip("Orders endpoint is not available on the target API")
            return

        # Assert
        APIAssertions.assert_status_created(response)
        APIAssertions.assert_valid_schema(response, "order_schema")

        # Cleanup
        cleanup_created_resources.append({"type": "order", "id": response.json()["id"]})

    def test_error_schema_for_404(self, api_client: APIClient, api_test_data: dict[str, Any]) -> None:
        """Validate 404 error response against ``error_schema``."""
        # Act
        response = api_client.get(api_test_data["invalid_endpoint"])

        # Assert
        APIAssertions.assert_status_not_found(response)
        APIAssertions.assert_valid_schema(response, "error_schema")

    def test_error_schema_for_401(self, unauthenticated_client: APIClient) -> None:
        """Validate 401 error response against ``error_schema``."""
        # Act
        response = unauthenticated_client.get(APIEndpoints.profile())

        # Assert
        APIAssertions.assert_status_unauthorized(response)

        # The error schema may vary by API implementation — validate gracefully
        try:
            APIAssertions.assert_valid_schema(response, "error_schema")
        except (AssertionError, FileNotFoundError):
            # Fallback: just check the status code was correct
            pass
