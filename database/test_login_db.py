from __future__ import annotations

"""Database validation tests for the **Users / Login** module.

Verifies user account integrity, authentication constraints,
and login-related business rules at the database level.
"""

import pytest

from database.db_helpers import DBHelpers
from database.db_queries import fetch_one, fetch_scalar
from database.sql_constants import SQLQueries

pytestmark = [
    pytest.mark.database,
    pytest.mark.smoke,
    pytest.mark.login,
]


class TestLoginDB:
    """Database-level validation of user accounts and login logic."""

    # ── Positive validation ────────────────────────────────────────────────────

    def test_verify_user_exists(self, db_helpers: DBHelpers) -> None:
        """Verify that a known user exists in the database."""
        assert db_helpers.user_exists("standard_user"), (
            "Expected 'standard_user' to exist in the users table"
        )

    def test_verify_account_active(self, db_helpers: DBHelpers) -> None:
        """Verify that active users have ``is_active = 1``."""
        assert db_helpers.user_is_active("standard_user"), (
            "Expected 'standard_user' to have is_active = 1"
        )

    def test_verify_last_login_updated(self, db_helpers: DBHelpers) -> None:
        """Verify that active users have a recent ``last_login`` timestamp."""
        last_login = db_helpers.user_last_login("standard_user")
        assert last_login is not None, (
            "Expected 'standard_user' to have a last_login timestamp"
        )
        assert isinstance(last_login, str) and len(last_login) > 0, (
            f"Expected non-empty last_login, got '{last_login}'"
        )

    def test_verify_user_role(self, db_helpers: DBHelpers) -> None:
        """Verify that a standard user has the 'customer' role."""
        role = db_helpers.user_role("standard_user")
        assert role == "customer", (
            f"Expected role 'customer' for standard_user, got '{role}'"
        )

    def test_verify_admin_role(self, db_helpers: DBHelpers) -> None:
        """Verify that an admin user has the 'admin' role."""
        role = db_helpers.user_role("admin_user")
        assert role == "admin", (
            f"Expected role 'admin' for admin_user, got '{role}'"
        )

    # ── Negative validation ────────────────────────────────────────────────────

    def test_verify_invalid_user_does_not_exist(self, db_helpers: DBHelpers) -> None:
        """Verify that a non-existent user is not found."""
        assert not db_helpers.user_exists("nonexistent_user"), (
            "Expected 'nonexistent_user' to NOT exist in the database"
        )

    def test_verify_locked_out_user_account_locked(self, db_helpers: DBHelpers) -> None:
        """Verify that the locked-out user has ``account_locked = 1``."""
        assert db_helpers.user_is_locked("locked_out_user"), (
            "Expected 'locked_out_user' to have account_locked = 1"
        )

    def test_verify_locked_out_user_not_active(self, db_helpers: DBHelpers) -> None:
        """Verify that the locked-out user is not active."""
        assert not db_helpers.user_is_active("locked_out_user"), (
            "Expected 'locked_out_user' to have is_active = 0"
        )

    # ── Constraint validation ──────────────────────────────────────────────────

    def test_verify_duplicate_users(self, db_helpers: DBHelpers) -> None:
        """Verify that no duplicate email addresses exist in the users table."""
        duplicate_count = fetch_scalar(
            "SELECT COUNT(*) FROM (SELECT email FROM users GROUP BY email HAVING COUNT(*) > 1)"
        )
        assert duplicate_count == 0, (
            f"Expected no duplicate email addresses, found {duplicate_count}"
        )

    def test_verify_login_attempts_tracked(self, db_helpers: DBHelpers) -> None:
        """Verify that login attempt counts are tracked for known users."""
        attempts = db_helpers.user_has_login_attempts("locked_out_user")
        assert attempts >= 5, (
            f"Expected 'locked_out_user' to have >= 5 login attempts, got {attempts}"
        )

    def test_verify_password_not_null(self) -> None:
        """Verify that every user has a non-null password_hash."""
        users = fetch_scalar(
            "SELECT COUNT(*) FROM users WHERE password_hash IS NULL OR password_hash = ''"
        )
        assert users == 0, (
            f"Expected 0 users with NULL/empty password_hash, found {users}"
        )

    def test_verify_email_unique(self) -> None:
        """Verify that the ``email`` column enforces uniqueness."""
        total_users = fetch_scalar("SELECT COUNT(*) FROM users")
        unique_emails = fetch_scalar("SELECT COUNT(DISTINCT email) FROM users")
        assert total_users == unique_emails, (
            f"Expected unique emails: {total_users} users vs {unique_emails} unique emails"
        )

    def test_verify_username_unique(self) -> None:
        """Verify that the ``username`` column enforces uniqueness."""
        total_users = fetch_scalar("SELECT COUNT(*) FROM users")
        unique_usernames = fetch_scalar("SELECT COUNT(DISTINCT username) FROM users")
        assert total_users == unique_usernames, (
            f"Expected unique usernames: {total_users} users vs {unique_usernames} unique usernames"
        )

    # ── User status validation ─────────────────────────────────────────────────

    def test_verify_user_status(self, db_helpers: DBHelpers) -> None:
        """Verify that the user status field has valid values."""
        statuses = fetch_scalar(
            "SELECT COUNT(*) FROM users WHERE is_active NOT IN (0, 1)"
        )
        assert statuses == 0, (
            f"Expected all users to have is_active IN (0, 1), found {statuses} with invalid values"
        )

    def test_verify_inactive_user_count(self, db_helpers: DBHelpers) -> None:
        """Verify that the count of inactive users is correct."""
        inactive = fetch_scalar("SELECT COUNT(*) FROM users WHERE is_active = 0")
        assert inactive == 2, (
            f"Expected 2 inactive users, found {inactive}"
        )

    def test_verify_role_values_are_valid(self) -> None:
        """Verify that all user roles are from the allowed set."""
        invalid_roles = fetch_scalar(
            "SELECT COUNT(*) FROM users WHERE role NOT IN ('admin', 'customer', 'manager')"
        )
        assert invalid_roles == 0, (
            f"Expected 0 users with invalid roles, found {invalid_roles}"
        )
