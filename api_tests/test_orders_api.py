from __future__ import annotations

from typing import Any

import pytest

from api.api_assertions import APIAssertions
from api.api_client import APIClient
from api.api_helpers import APIHelpers
from api.endpoints import APIEndpoints
from models.order import Order


pytestmark = [
    pytest.mark.api,
    pytest.mark.regression,
    pytest.mark.checkout,
    pytest.mark.orders,
]


class TestOrdersAPI:
    """Test order management API endpoints.

    Covers order creation and retrieval.
    Note: The Platzi Fake Store API does not expose dedicated order endpoints,
    so these tests act as both functional tests and interface-documentation
    examples that work against any ecommerce API that supports orders.
    """

    @pytest.mark.smoke
    def test_create_order(
        self,
        api_client: APIClient,
        api_helpers: APIHelpers,
        api_test_data: dict[str, Any],
        cleanup_created_resources: list[dict[str, Any]],
    ) -> None:
        """Test 9: Create a new order.

        Validates:
            - 201 Created
            - Response contains order fields (id, userId, date, products, total)
            - ID is a positive integer
            - At least one product is attached
            - Conforms to order schema
        """
        # Arrange
        payload = api_helpers.load_payload("create_order")
        payload["userId"] = api_test_data["existing_user_id"]

        # Act
        response = api_client.post(APIEndpoints.orders(), json=payload)

        # The Platzi API may not expose the orders endpoint
        if response.status_code == 404:
            pytest.skip("Orders endpoint is not available on the target API")
            return

        # Assert — status
        APIAssertions.assert_status_created(response)

        # Assert — body structure
        APIAssertions.assert_json_not_empty(response)
        APIAssertions.assert_json_has_keys(response, ["id", "userId", "date", "products"])
        APIAssertions.assert_id_is_positive(response)

        # Assert — schema
        APIAssertions.assert_valid_schema(response, "order_schema")

        # Business assertions
        body: dict[str, Any] = response.json()
        order = Order.from_dict(body)
        assert len(order.products) >= 1, "Order must contain at least one product"
        assert order.user_id == api_test_data["existing_user_id"], (
            f"Expected userId={api_test_data['existing_user_id']}, got {order.user_id}"
        )

        # Track for cleanup
        cleanup_created_resources.append({"type": "order", "id": order.id})

    @pytest.mark.regression
    def test_get_order_details(
        self,
        api_client: APIClient,
        api_helpers: APIHelpers,
        api_test_data: dict[str, Any],
        cleanup_created_resources: list[dict[str, Any]],
    ) -> None:
        """Test 10: Retrieve order details by order ID.

        Validates:
            - 200 OK
            - Order fields match those from creation
            - Products are listed correctly
            - Conforms to order schema
        """
        # Arrange — attempt to create an order first
        create_payload = api_helpers.load_payload("create_order")
        create_payload["userId"] = api_test_data["existing_user_id"]
        create_payload["products"] = [
            {"productId": 2, "quantity": 1},
            {"productId": 4, "quantity": 2},
        ]
        created = api_client.post(APIEndpoints.orders(), json=create_payload)

        if created.status_code == 404:
            pytest.skip("Orders endpoint is not available on the target API")
            return

        APIAssertions.assert_status_created(created)
        order_id: int = created.json()["id"]
        cleanup_created_resources.append({"type": "order", "id": order_id})

        # Act — fetch the order by ID
        response = api_client.get(APIEndpoints.order_by_id(order_id))

        # Assert — status
        APIAssertions.assert_status_ok(response)

        # Assert — body structure
        APIAssertions.assert_json_not_empty(response)
        APIAssertions.assert_json_has_keys(response, ["id", "userId", "date", "products"])

        # Assert — schema
        APIAssertions.assert_valid_schema(response, "order_schema")

        # Business assertions — verify order ID matches
        body: dict[str, Any] = response.json()
        order = Order.from_dict(body)
        assert order.id == order_id, f"Expected order ID={order_id}, got {order.id}"
        assert len(order.products) == 2, f"Expected 2 products, got {len(order.products)}"
        assert order.user_id == api_test_data["existing_user_id"]

        # Assert — response time
        APIAssertions.assert_response_time_less_than(
            response,
            api_test_data["max_acceptable_response_time_seconds"],
        )
