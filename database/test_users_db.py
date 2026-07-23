from __future__ import annotations

"""Database validation tests for the **Users** module.

Verifies user profile data, roles, account status, and user-level
business rules at the database level.
"""

import pytest

from database.db_helpers import DBHelpers
from database.db_queries import count, fetch_all, fetch_one, fetch_scalar
from database.sql_constants import SQLQueries

pytestmark = [
    pytest.mark.database,
    pytest.mark.regression,
    pytest.mark.users,
]


class TestUsersDB:
    """Database-level validation of user profile data."""

    # ── User existence & profile ──────────────────────────────────────────────

    def test_verify_user_exists_in_db(self, known_users: dict) -> None:
        """Verify that all known usernames exist in the database."""
        for username in known_users:
            user = fetch_one(SQLQueries.USER_BY_USERNAME, (username,))
            assert user is not None, (
                f"Expected user '{username}' to exist in the database"
            )

    def test_verify_user_email(self, known_users: dict) -> None:
        """Verify that a user has the correct email address."""
        user = fetch_one(SQLQueries.USER_BY_USERNAME, ("standard_user",))
        expected_email = known_users["standard_user"]["email"]
        assert user["email"] == expected_email, (
            f"Expected email '{expected_email}', got '{user['email']}'"
        )

    def test_verify_user_has_full_name(self) -> None:
        """Verify that users have first and last names."""
        no_name = fetch_scalar(
            "SELECT COUNT(*) FROM users WHERE first_name IS NULL OR last_name IS NULL"
        )
        assert no_name == 0, (
            f"Expected 0 users without full names, found {no_name}"
        )

    # ── Role validation ───────────────────────────────────────────────────────

    def test_verify_user_role_customer(self, db_helpers: DBHelpers) -> None:
        """Verify that standard users have the 'customer' role."""
        assert db_helpers.user_role("standard_user") == "customer"

    def test_verify_user_role_admin(self, db_helpers: DBHelpers) -> None:
        """Verify that admin users have the 'admin' role."""
        assert db_helpers.user_role("admin_user") == "admin"

    def test_verify_user_role_manager(self, db_helpers: DBHelpers) -> None:
        """Verify that manager users have the 'manager' role."""
        assert db_helpers.user_role("manager_user") == "manager"

    def test_verify_role_counts(self) -> None:
        """Verify the count of users by role."""
        role_counts = fetch_all(
            "SELECT role, COUNT(*) AS cnt FROM users GROUP BY role ORDER BY role"
        )
        role_map = {r["role"]: r["cnt"] for r in role_counts}
        assert role_map.get("customer", 0) >= 8, (
            f"Expected at least 8 customers, found {role_map.get('customer', 0)}"
        )
        assert role_map.get("admin", 0) >= 1, (
            f"Expected at least 1 admin, found {role_map.get('admin', 0)}"
        )
        assert role_map.get("manager", 0) >= 1, (
            f"Expected at least 1 manager, found {role_map.get('manager', 0)}"
        )

    # ── Account status ────────────────────────────────────────────────────────

    def test_verify_account_locked_status(self) -> None:
        """Verify that only the locked_out_user has account_locked = 1."""
        locked = fetch_scalar(
            "SELECT COUNT(*) FROM users WHERE account_locked = 1"
        )
        assert locked >= 1, (
            f"Expected at least 1 locked account, found {locked}"
        )

    def test_verify_active_user_count(self, db_helpers: DBHelpers) -> None:
        """Verify the count of active users."""
        active = db_helpers.active_user_count()
        assert active >= 8, (
            f"Expected at least 8 active users, found {active}"
        )

    def test_verify_inactive_users_have_locked_or_no_login(self) -> None:
        """Verify that inactive users either have account_locked=1 or no last_login.

        Note: 'locked_out_user' is inactive (is_active=0) but may have a
        last_login timestamp because they attempted login before being locked.
        """
        inactive_users = fetch_all(
            "SELECT username, is_active, account_locked, last_login FROM users WHERE is_active = 0"
        )
        assert len(inactive_users) >= 1, "Expected at least 1 inactive user"
        for user in inactive_users:
            # Inactive users should either be locked or have no recent login
            assert user["account_locked"] == 1 or user["last_login"] is None, (
                f"Inactive user '{user['username']}' is not locked and has a last_login"
            )

    # ── Email validation ──────────────────────────────────────────────────────

    def test_verify_email_format(self) -> None:
        """Verify that all user emails contain '@' and '.'."""
        invalid_emails = fetch_scalar(
            "SELECT COUNT(*) FROM users WHERE email NOT LIKE '%@%.%'"
        )
        assert invalid_emails == 0, (
            f"Expected 0 users with invalid email format, found {invalid_emails}"
        )

    def test_verify_email_unique_constraint(self) -> None:
        """Verify that the email column is unique."""
        duplicates = fetch_scalar(
            "SELECT COUNT(*) FROM (SELECT email FROM users GROUP BY email HAVING COUNT(*) > 1)"
        )
        assert duplicates == 0, (
            f"Expected 0 duplicate emails, found {duplicates}"
        )

    # ── Creation timestamps ───────────────────────────────────────────────────

    def test_verify_user_created_at_not_null(self) -> None:
        """Verify that all users have a created_at timestamp."""
        null_dates = fetch_scalar(
            "SELECT COUNT(*) FROM users WHERE created_at IS NULL"
        )
        assert null_dates == 0, (
            f"Expected 0 users with NULL created_at, found {null_dates}"
        )

    def test_verify_new_user_has_no_last_login(self) -> None:
        """Verify that a newly created user has NULL last_login."""
        user = fetch_one(SQLQueries.USER_BY_USERNAME, ("new_user",))
        assert user is not None, "Expected 'new_user' to exist"
        assert user["last_login"] is None, (
            f"Expected new_user last_login to be NULL, got '{user['last_login']}'"
        )

    # ── Password validation ───────────────────────────────────────────────────

    def test_verify_password_hash_not_empty(self) -> None:
        """Verify that all users have non-empty password hashes."""
        empty_hashes = fetch_scalar(
            "SELECT COUNT(*) FROM users WHERE password_hash IS NULL OR password_hash = ''"
        )
        assert empty_hashes == 0, (
            f"Expected 0 users with empty password_hash, found {empty_hashes}"
        )

    def test_verify_password_hash_length(self) -> None:
        """Verify that all password hashes have a minimum length."""
        short_hashes = fetch_scalar(
            "SELECT COUNT(*) FROM users WHERE LENGTH(password_hash) < 8"
        )
        assert short_hashes == 0, (
            f"Expected 0 users with short password_hash, found {short_hashes}"
        )

    def test_verify_user_login_attempts_non_negative(self) -> None:
        """Verify that all login_attempts values are non-negative."""
        negative_attempts = fetch_scalar(
            "SELECT COUNT(*) FROM users WHERE login_attempts < 0"
        )
        assert negative_attempts == 0, (
            f"Expected 0 users with negative login_attempts, found {negative_attempts}"
        )
