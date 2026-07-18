from __future__ import annotations

from typing import Any

import pytest

from api.api_assertions import APIAssertions
from api.api_client import APIClient
from api.api_helpers import APIHelpers
from api.endpoints import APIEndpoints
from models.user import User


pytestmark = [
    pytest.mark.api,
    pytest.mark.regression,
    pytest.mark.users,
]


class TestUsersAPI:
    """Test user management API endpoints.

    Covers fetching and updating user profiles.
    """

    @pytest.mark.smoke
    def test_get_user_profile(
        self,
        api_client: APIClient,
        api_test_data: dict[str, Any],
    ) -> None:
        """Test 11: GET /users/:id returns the user profile.

        Validates:
            - 200 OK
            - Response contains user profile fields (id, email, name, role, avatar)
            - Fields have correct types
            - Conforms to user schema
        """
        # Arrange
        user_id: int = api_test_data["existing_user_id"]

        # Act
        response = api_client.get(APIEndpoints.user_by_id(user_id))

        # Assert — status
        APIAssertions.assert_status_ok(response)

        # Assert — body structure
        APIAssertions.assert_json_not_empty(response)
        APIAssertions.assert_json_has_keys(response, ["id", "email", "name", "role", "avatar"])
        APIAssertions.assert_json_value(response, "id", user_id)

        # Assert — data types
        APIAssertions.assert_json_type(response, "email", str)
        APIAssertions.assert_json_type(response, "name", str)
        APIAssertions.assert_json_type(response, "role", str)

        # Assert — schema
        APIAssertions.assert_valid_schema(response, "user_schema")

        # Business assertions
        body: dict[str, Any] = response.json()
        user = User.from_dict(body)
        assert user.id == user_id, f"Expected user ID={user_id}, got {user.id}"
        assert "@" in user.email, f"Invalid email format: {user.email}"

        # Assert — response time
        APIAssertions.assert_response_time_less_than(
            response,
            api_test_data["max_acceptable_response_time_seconds"],
        )

    @pytest.mark.regression
    def test_update_user_profile(
        self,
        api_client: APIClient,
        api_helpers: APIHelpers,
        api_test_data: dict[str, Any],
    ) -> None:
        """Test 12: Update the user profile.

        Note: The Platzi API only allows updating your own authenticated user.
        If the request is unauthenticated or for a different user, it returns 401.

        Validates:
            - 200 OK or 401 Unauthorized (depending on auth state)
            - If 200, the response reflects the updated fields
        """
        # Arrange
        user_id: int = api_test_data["existing_user_id"]
        payload = api_helpers.load_payload("update_user_profile")

        # Act
        response = api_client.put(APIEndpoints.user_by_id(user_id), json=payload)

        # The API may return 401 if not authenticated as the target user
        if response.status_code == 401:
            pytest.skip("Cannot update user profile without proper auth credentials")
            return

        # Assert — status
        assert response.status_code in (200, 201), (
            f"Expected 200/201 on update, got {response.status_code}. "
            f"Body: {response.text[:200]}"
        )

        # Assert — body structure
        APIAssertions.assert_json_not_empty(response)
        APIAssertions.assert_json_has_keys(response, ["id", "email", "name"])
        APIAssertions.assert_json_value(response, "id", user_id)

        # Assert the updated name
        body: dict[str, Any] = response.json()
        user = User.from_dict(body)
        assert user.name == payload["name"], (
            f"Expected name='{payload['name']}', got '{user.name}'"
        )
        assert user.id == user_id, "User ID should not change after update"

        # Assert — schema
        APIAssertions.assert_valid_schema(response, "user_schema")
