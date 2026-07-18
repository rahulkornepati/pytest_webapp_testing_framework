from __future__ import annotations

from typing import Any

import pytest

from api.api_assertions import APIAssertions
from api.api_client import APIClient
from api.api_helpers import APIHelpers
from api.endpoints import APIEndpoints
from models.cart import Cart


pytestmark = [
    pytest.mark.api,
    pytest.mark.regression,
    pytest.mark.cart,
    pytest.mark.products,
]


class TestCartAPI:
    """Test shopping cart API endpoints.

    Covers adding items, updating quantities, and removing items from a cart.
    Note: The Platzi Fake Store API (the default test target) does not expose
    cart endpoints, so these tests are expected to fail gracefully with 404.
    """

    @pytest.mark.smoke
    def test_add_product_to_cart(
        self,
        api_client: APIClient,
        api_helpers: APIHelpers,
        api_test_data: dict[str, Any],
        cleanup_created_resources: list[dict[str, Any]],
    ) -> None:
        """Test 6: Add a product to the cart.

        Validates:
            - 201 Created (or 404 if cart endpoint unavailable)
            - Response contains cart fields (id, userId, date, products)
            - Cart has at least one product
            - Created cart is queued for cleanup
        """
        # Arrange
        payload = api_helpers.load_payload("create_cart")
        payload["userId"] = api_test_data["existing_user_id"]
        payload["products"] = [
            {"productId": api_test_data["existing_product_id"], "quantity": 2}
        ]

        # Act
        response = api_client.post(APIEndpoints.carts(), json=payload)

        # The Platzi API may not expose a cart endpoint — handle gracefully
        if response.status_code == 404:
            pytest.skip("Cart endpoint is not available on the target API")
            return

        # Assert — status code
        APIAssertions.assert_status_created(response)

        # Assert — body structure
        APIAssertions.assert_json_not_empty(response)
        APIAssertions.assert_json_has_keys(response, ["id", "userId", "date", "products"])
        APIAssertions.assert_id_is_positive(response)

        # Assert — schema
        APIAssertions.assert_valid_schema(response, "cart_schema")

        # Business assertions
        body: dict[str, Any] = response.json()
        cart = Cart.from_dict(body)
        assert len(cart.products) > 0, "Cart should contain at least one product"
        assert cart.user_id == api_test_data["existing_user_id"], (
            f"Expected userId={api_test_data['existing_user_id']}, got {cart.user_id}"
        )

        # Track for cleanup
        cleanup_created_resources.append({"type": "cart", "id": cart.id})

    @pytest.mark.regression
    def test_update_cart_quantity(
        self,
        api_client: APIClient,
        api_helpers: APIHelpers,
        api_test_data: dict[str, Any],
        cleanup_created_resources: list[dict[str, Any]],
    ) -> None:
        """Test 7: Update the quantity of a product in the cart.

        Validates:
            - 200 OK or 201 Created on update
            - The response reflects the updated product quantity
        """
        # Arrange — create a cart first
        create_payload = api_helpers.load_payload("create_cart")
        create_payload["userId"] = api_test_data["existing_user_id"]
        create_payload["products"] = [
            {"productId": api_test_data["existing_product_id"], "quantity": 2}
        ]
        created = api_client.post(APIEndpoints.carts(), json=create_payload)

        if created.status_code == 404:
            pytest.skip("Cart endpoint is not available on the target API")
            return

        APIAssertions.assert_status_created(created)
        cart_id: int = created.json()["id"]
        cleanup_created_resources.append({"type": "cart", "id": cart_id})

        # Act — update the quantity
        update_payload = api_helpers.load_payload("update_cart_item")
        update_payload["userId"] = api_test_data["existing_user_id"]
        update_payload["products"] = [
            {"productId": api_test_data["existing_product_id"], "quantity": 5}
        ]
        response = api_client.put(APIEndpoints.cart_by_id(cart_id), json=update_payload)

        # Assert — status code
        assert response.status_code in (200, 201), (
            f"Expected 200/201 on update, got {response.status_code}"
        )

        # Assert — schema
        APIAssertions.assert_valid_schema(response, "cart_schema")

        # Business assertion — verify the quantity was updated
        body: dict[str, Any] = response.json()
        cart = Cart.from_dict(body)
        updated_item = next(
            (p for p in cart.products if p.product_id == api_test_data["existing_product_id"]),
            None,
        )
        assert updated_item is not None, "Expected the product to remain in the cart"
        assert updated_item.quantity == 5, (
            f"Expected quantity=5, got {updated_item.quantity}"
        )

    @pytest.mark.regression
    def test_remove_product_from_cart(
        self,
        api_client: APIClient,
        api_helpers: APIHelpers,
        api_test_data: dict[str, Any],
        cleanup_created_resources: list[dict[str, Any]],
    ) -> None:
        """Test 8: Remove a product from the cart (by replacing cart items).

        Validates:
            - 200 OK or 201 Created
            - The product is no longer present in the cart's product list
        """
        # Arrange — create a cart with two products
        create_payload = api_helpers.load_payload("create_cart")
        create_payload["userId"] = api_test_data["existing_user_id"]
        create_payload["products"] = [
            {"productId": 2, "quantity": 1},
            {"productId": 4, "quantity": 3},
        ]
        created = api_client.post(APIEndpoints.carts(), json=create_payload)

        if created.status_code == 404:
            pytest.skip("Cart endpoint is not available on the target API")
            return

        APIAssertions.assert_status_created(created)
        cart_id: int = created.json()["id"]
        cleanup_created_resources.append({"type": "cart", "id": cart_id})

        # Act — update with only the second product (effectively removing first)
        update_payload = api_helpers.load_payload("update_cart_item")
        update_payload["userId"] = api_test_data["existing_user_id"]
        update_payload["products"] = [
            {"productId": 4, "quantity": 3},
        ]
        response = api_client.put(APIEndpoints.cart_by_id(cart_id), json=update_payload)

        # Assert — status
        assert response.status_code in (200, 201)

        # Assert — the removed product is no longer present
        body: dict[str, Any] = response.json()
        cart = Cart.from_dict(body)
        product_ids_in_cart = [p.product_id for p in cart.products]
        assert 2 not in product_ids_in_cart, (
            f"Expected product #2 to be removed, still present: {product_ids_in_cart}"
        )
        assert 4 in product_ids_in_cart, "Expected product #4 to remain in the cart"
