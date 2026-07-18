from __future__ import annotations

from typing import Any

import pytest

from api.api_assertions import APIAssertions
from api.api_client import APIClient
from api.api_helpers import APIHelpers
from api.endpoints import APIEndpoints
from config.api_config import APIConfig


pytestmark = [
    pytest.mark.api,
    pytest.mark.regression,
    pytest.mark.performance,
]


class TestPerformanceAPI:
    """Test suite for API performance validation.

    Ensures critical endpoints respond within the configured time budget.
    """

    @pytest.mark.smoke
    def test_get_all_products_response_time(
        self,
        api_client: APIClient,
    ) -> None:
        """Test 15: Verify ``GET /products`` responds in < 2 seconds.

        Validates:
            - 200 OK
            - ``elapsed.total_seconds()`` <= ``MAX_ACCEPTABLE_RESPONSE_TIME_SECONDS``
        """
        # Act
        response = api_client.get(APIEndpoints.products())

        # Assert
        APIAssertions.assert_status_ok(response)
        APIAssertions.assert_response_time_less_than(
            response,
            APIConfig.MAX_ACCEPTABLE_RESPONSE_TIME_SECONDS,
        )

    def test_login_response_time(
        self,
        api_client: APIClient,
        api_helpers: APIHelpers,
    ) -> None:
        """Verify login endpoint response time is acceptable."""
        # Arrange
        payload = api_helpers.load_payload("login_valid")

        # Act
        response = api_client.post(APIEndpoints.login(), json=payload)

        # Assert
        assert response.status_code in (200, 201), (
            f"Expected 200/201, got {response.status_code}"
        )
        APIAssertions.assert_response_time_less_than(
            response,
            APIConfig.MAX_ACCEPTABLE_RESPONSE_TIME_SECONDS,
        )

    def test_get_product_by_id_response_time(
        self,
        api_client: APIClient,
        api_test_data: dict[str, Any],
    ) -> None:
        """Verify single product fetch is fast."""
        # Arrange
        product_id: int = api_test_data["existing_product_id"]

        # Act
        response = api_client.get(APIEndpoints.product_by_id(product_id))

        # Assert
        APIAssertions.assert_status_ok(response)
        APIAssertions.assert_response_time_less_than(
            response,
            APIConfig.MAX_ACCEPTABLE_RESPONSE_TIME_SECONDS,
        )

    def test_get_user_profile_response_time(
        self,
        api_client: APIClient,
        api_test_data: dict[str, Any],
    ) -> None:
        """Verify user profile fetch is fast."""
        # Arrange
        user_id: int = api_test_data["existing_user_id"]

        # Act
        response = api_client.get(APIEndpoints.user_by_id(user_id))

        # Assert
        APIAssertions.assert_status_ok(response)
        APIAssertions.assert_response_time_less_than(
            response,
            APIConfig.MAX_ACCEPTABLE_RESPONSE_TIME_SECONDS,
        )

    def test_consecutive_requests_performance(
        self,
        api_client: APIClient,
        api_test_data: dict[str, Any],
    ) -> None:
        """Verify the API handles a series of consecutive requests quickly.

        Makes three sequential calls and asserts each is under the limit.
        """
        # Arrange — a mix of endpoints
        endpoints = [
            APIEndpoints.products(),
            APIEndpoints.product_by_id(api_test_data["existing_product_id"]),
            APIEndpoints.user_by_id(api_test_data["existing_user_id"]),
        ]

        # Act & Assert
        for endpoint in endpoints:
            response = api_client.get(endpoint)
            APIAssertions.assert_status_ok(response)
            APIAssertions.assert_response_time_less_than(
                response,
                APIConfig.MAX_ACCEPTABLE_RESPONSE_TIME_SECONDS,
            )
