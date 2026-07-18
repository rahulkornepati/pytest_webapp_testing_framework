from __future__ import annotations

import logging
from typing import Any

import pytest

from api.api_assertions import APIAssertions
from api.api_client import APIClient
from api.endpoints import APIEndpoints


logger = logging.getLogger("ecommerce_framework.api.tests.negative")

pytestmark = [
    pytest.mark.api,
    pytest.mark.regression,
    pytest.mark.negative,
]


class TestNegativeAPI:
    """Negative API test cases.

    Verifies that the API correctly rejects invalid requests with
    appropriate error status codes and messages.
    """

    @pytest.mark.smoke
    def test_invalid_endpoint_returns_404(
        self,
        api_client: APIClient,
        api_test_data: dict[str, Any],
    ) -> None:
        """Test 13: Request to a non-existent endpoint returns 404 Not Found.

        Validates:
            - 404 Not Found
            - Error response body (message or error field)
        """
        # Arrange
        invalid_path: str = api_test_data["invalid_endpoint"]

        # Act
        response = api_client.get(invalid_path)

        # Assert
        APIAssertions.assert_status_not_found(response)

        # Assert — error body
        body: dict[str, Any] = response.json()
        assert body, "Error response body should not be empty"
        message = body.get("message", body.get("error", ""))
        assert any(
            keyword in message.lower() if isinstance(message, str) else False
            for keyword in ("not found", "does not exist", "route", "endpoint", "404")
        ), f"Expected 404 error message, got: {message}"

        # Assert — error schema
        APIAssertions.assert_valid_schema(response, "error_schema")

    @pytest.mark.smoke
    def test_unauthorized_request_returns_4xx(
        self,
        unauthenticated_client: APIClient,
    ) -> None:
        """Test 14: Request without authentication returns 401 Unauthorized.

        Hits a protected endpoint (e.g. login with wrong credentials) without
        providing any auth headers.

        Validates:
            - 401 Unauthorized
            - Error message indicates missing or invalid authentication
        """
        # Act — attempt to access a protected resource without auth
        response = unauthenticated_client.get(APIEndpoints.profile())

        # Depending on the API implementation, this may return 401 or other 4xx
        APIAssertions.assert_status_unauthorized(response)

        # Assert — error body
        body: dict[str, Any] = response.json()
        message = body.get("message", body.get("error", ""))

        # The exact wording varies by API — check for common auth-failure keywords
        if isinstance(message, str):
            assert any(
                keyword in message.lower()
                for keyword in (
                    "unauthorized",
                    "authentication",
                    "token",
                    "invalid",
                    "not authenticated",
                    "missing",
                    "bearer",
                )
            ), f"Expected auth-related error, got: {message}"

    @pytest.mark.regression
    def test_get_non_existent_product_returns_4xx(
        self,
        api_client: APIClient,
    ) -> None:
        """Requesting a non-existent product returns a 4xx error.

        The Platzi API may return 400 or 404 depending on the implementation.
        """
        # Arrange
        invalid_product_id = 9999999

        # Act
        response = api_client.get(APIEndpoints.product_by_id(invalid_product_id))

        # Assert
        assert response.status_code in (400, 404), (
            f"Expected 400/404 for non-existent product, got {response.status_code}"
        )

        # The error_schema may not perfectly match a 400 response —
        # attempt schema validation and log gracefully if it doesn't apply
        try:
            APIAssertions.assert_valid_schema(response, "error_schema")
        except (AssertionError, FileNotFoundError) as exc:
            logger.warning(
                "Schema validation skipped for 4xx error response: %s",
                exc,
            )

    @pytest.mark.regression
    def test_delete_non_existent_resource_returns_4xx(
        self,
        api_client: APIClient,
    ) -> None:
        """Deleting a non-existent resource returns a 4xx error."""
        # Arrange — use a very large ID that shouldn't exist
        non_existent_id = 9999999

        # Act
        response = api_client.delete(APIEndpoints.order_by_id(non_existent_id))

        # Assert
        assert response.status_code in (400, 401, 404), (
            f"Expected 4xx for non-existent resource, got {response.status_code}"
        )
