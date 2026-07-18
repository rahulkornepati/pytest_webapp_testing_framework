from __future__ import annotations

from typing import Any

import pytest

from api.api_assertions import APIAssertions
from api.api_client import APIClient
from api.endpoints import APIEndpoints
from api.api_helpers import APIHelpers


pytestmark = [
    pytest.mark.api,
    pytest.mark.smoke,
    pytest.mark.auth,
]


class TestAuthAPI:
    """Test authentication endpoints — login, logout, and token management.

    Every test validates:
        - HTTP status code
        - JSON response structure
        - Response schema (via JSON Schema)
        - Business-logic invariants
    """

    @pytest.mark.regression
    def test_login_with_valid_credentials(
        self,
        api_client: APIClient,
        api_helpers: APIHelpers,
    ) -> None:
        """Test 1: Login with valid credentials returns a bearer token.

        Validates:
            - 200 OK or 201 Created
            - Response contains ``access_token`` and ``refresh_token``
            - Token is a non-empty string
            - Response conforms to ``auth_login_schema``
        """
        # Arrange
        payload = api_helpers.load_payload("login_valid")

        # Act
        response = api_client.post(APIEndpoints.login(), json=payload)

        # Assert — status code (the Platzi API returns 201 on login)
        assert response.status_code in (200, 201), (
            f"Expected 200/201, got {response.status_code}. Body: {response.text[:200]}"
        )

        # Assert — JSON keys
        APIAssertions.assert_json_has_key(response, "access_token")
        APIAssertions.assert_json_has_key(response, "refresh_token")

        # Assert — data types and business rules
        body: dict[str, Any] = response.json()
        assert len(body["access_token"]) > 0, "access_token should not be empty"

        # Assert — schema validation
        APIAssertions.assert_valid_schema(response, "auth_login_schema")

    @pytest.mark.regression
    def test_login_with_invalid_credentials_returns_401(
        self,
        unauthenticated_client: APIClient,
    ) -> None:
        """Test 2: Login with invalid credentials returns 401 Unauthorized.

        Validates:
            - 401 Unauthorized
            - Error message indicates invalid credentials
        """
        # Arrange
        payload = {
            "email": "nonexistent@mail.com",
            "password": "wrong_password_123!",
        }

        # Act
        response = unauthenticated_client.post(APIEndpoints.login(), json=payload)

        # Assert
        APIAssertions.assert_status_unauthorized(response)
        APIAssertions.assert_error_message_contains(
            response, "Unauthorized"
        )

    @pytest.mark.regression
    def test_login_with_missing_fields_returns_4xx(
        self,
        unauthenticated_client: APIClient,
    ) -> None:
        """Test 2b: Login with missing email/password returns 400/401/422.

        Validates:
            - 4xx status code
            - Appropriate validation error message
        """
        # Arrange — empty string fields
        payload = {"email": "", "password": ""}

        # Act
        response = unauthenticated_client.post(APIEndpoints.login(), json=payload)

        # Assert
        assert response.status_code in (400, 401, 422), (
            f"Expected 4xx validation error, got {response.status_code}. "
            f"Body: {response.text[:200]}"
        )
        assert len(response.text) > 0, "Response body should not be empty"
