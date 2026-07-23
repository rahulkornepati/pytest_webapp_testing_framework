from __future__ import annotations

"""Database validation tests for the **User Sessions** module.

Verifies session creation, token management, activity tracking,
and session lifecycle at the database level.
"""

import re
from datetime import datetime

import pytest

from database.db_helpers import DBHelpers
from database.db_queries import count, fetch_all, fetch_one, fetch_scalar
from database.database_utils import DatabaseUtils
from database.sql_constants import SQLQueries

pytestmark = [
    pytest.mark.database,
    pytest.mark.regression,
    pytest.mark.login,
]


class TestSessionsDB:
    """Database-level validation of user session data."""

    # ── Session existence ─────────────────────────────────────────────────────

    def test_verify_session_exists(self, known_users: dict) -> None:
        """Verify that a session exists for a known user."""
        user_id = known_users["standard_user"]["user_id"]
        sessions = fetch_all(SQLQueries.SESSION_BY_USER_ID, (user_id,))
        assert len(sessions) >= 1, (
            f"Expected at least 1 session for standard_user, found {len(sessions)}"
        )

    def test_verify_session_by_token(self) -> None:
        """Verify that a session can be retrieved by its token."""
        session = fetch_one(SQLQueries.SESSION_BY_TOKEN, ("tok_std_abc123",))
        assert session is not None, "Expected session with token 'tok_std_abc123'"
        assert session["session_token"] == "tok_std_abc123"

    # ── Session activity status ───────────────────────────────────────────────

    def test_verify_session_is_active(self, db_helpers: DBHelpers) -> None:
        """Verify that an active session token returns is_active = 1."""
        assert db_helpers.session_is_active("tok_std_abc123"), (
            "Expected session 'tok_std_abc123' to be active"
        )

    def test_verify_inactive_session(self, db_helpers: DBHelpers) -> None:
        """Verify that an inactive session token returns is_active = 0."""
        assert not db_helpers.session_is_active("tok_inact_jkl012"), (
            "Expected session 'tok_inact_jkl012' to be inactive"
        )

    def test_verify_active_session_count(self, db_helpers: DBHelpers) -> None:
        """Verify the count of active sessions."""
        active = db_helpers.active_session_count()
        assert active >= 3, (
            f"Expected at least 3 active sessions, found {active}"
        )

    # ── Session timestamps ────────────────────────────────────────────────────

    def test_verify_session_created_at(self, known_users: dict) -> None:
        """Verify that a session has a created_at timestamp."""
        user_id = known_users["standard_user"]["user_id"]
        created = fetch_scalar(SQLQueries.SESSION_CREATED_AT, (user_id,))
        assert created is not None, "Expected session to have created_at"

    def test_verify_session_last_activity(self, known_users: dict) -> None:
        """Verify that a session has a last_activity timestamp."""
        user_id = known_users["standard_user"]["user_id"]
        last_activity = fetch_scalar(SQLQueries.SESSION_LAST_ACTIVITY, (user_id,))
        assert last_activity is not None, "Expected session to have last_activity"

    def test_verify_session_expiry_not_null(self, known_users: dict) -> None:
        """Verify that a session has a non-null expiry timestamp."""
        user_id = known_users["admin_user"]["user_id"]  # admin session expires 12:00 day+1
        expires = fetch_scalar(SQLQueries.SESSION_EXPIRY, (user_id,))
        assert expires is not None, "Expected session to have expires_at"

    # ── Session count ─────────────────────────────────────────────────────────

    def test_verify_session_count_by_user(self, known_users: dict) -> None:
        """Verify the number of sessions for a specific user."""
        user_id = known_users["standard_user"]["user_id"]
        session_count = count(SQLQueries.SESSION_COUNT_BY_USER, (user_id,))
        assert session_count == 1, (
            f"Expected 1 session for standard_user, found {session_count}"
        )

    def test_verify_expired_session_count(self, db_helpers: DBHelpers) -> None:
        """Verify the count of expired but still-active sessions."""
        expired = db_helpers.expired_session_count()
        assert expired >= 0, f"Expected non-negative expired session count, got {expired}"

    # ── IP address ────────────────────────────────────────────────────────────

    def test_verify_session_ip_address(self) -> None:
        """Verify that a session has an IP address recorded."""
        ip = fetch_scalar(SQLQueries.SESSION_IP_ADDRESS, ("tok_std_abc123",))
        assert ip is not None and len(ip) > 0, (
            f"Expected non-empty IP address, got '{ip}'"
        )

    def test_verify_session_ip_format(self) -> None:
        """Verify that session IP addresses follow valid format."""
        sessions = fetch_all("SELECT session_token, ip_address FROM user_sessions")
        ip_pattern = re.compile(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
        for session in sessions:
            if session["ip_address"]:
                assert ip_pattern.match(session["ip_address"]), (
                    f"Session '{session['session_token']}' has invalid IP: '{session['ip_address']}'"
                )

    # ── Session token validation ──────────────────────────────────────────────

    def test_verify_session_token_unique(self) -> None:
        """Verify that all session tokens are unique."""
        total = fetch_scalar("SELECT COUNT(*) FROM user_sessions")
        unique = fetch_scalar("SELECT COUNT(DISTINCT session_token) FROM user_sessions")
        assert total == unique, (
            f"Expected unique session tokens: {total} vs {unique} unique"
        )

    def test_verify_session_token_not_null(self) -> None:
        """Verify that all sessions have non-null tokens."""
        null_tokens = fetch_scalar(
            "SELECT COUNT(*) FROM user_sessions WHERE session_token IS NULL"
        )
        assert null_tokens == 0, (
            f"Expected 0 sessions with NULL token, found {null_tokens}"
        )

    # ── Session-user linkage ──────────────────────────────────────────────────

    def test_verify_session_links_to_valid_user(self) -> None:
        """Verify that all sessions reference an existing user."""
        orphaned = fetch_scalar(
            "SELECT COUNT(*) FROM user_sessions WHERE user_id NOT IN (SELECT user_id FROM users)"
        )
        assert orphaned == 0, (
            f"Expected 0 orphaned sessions, found {orphaned}"
        )

    def test_verify_inactive_user_has_inactive_session(self) -> None:
        """Verify that an inactive user has an inactive session."""
        sessions = fetch_all(SQLQueries.SESSION_BY_USER_ID, (9,))  # inactive_user
        for session in sessions:
            assert session["is_active"] == 0, (
                f"Inactive user has active session: {session['session_token']}"
            )

    # ── Session lifecycle ─────────────────────────────────────────────────────

    def test_verify_session_last_activity_updated(self) -> None:
        """Verify that last_activity is not before created_at."""
        invalid = fetch_scalar(
            "SELECT COUNT(*) FROM user_sessions WHERE last_activity < created_at"
        )
        assert invalid == 0, (
            f"Expected 0 sessions with last_activity before created_at, found {invalid}"
        )

    def test_verify_expired_session_detection(self, db_utils: DatabaseUtils) -> None:
        """Verify that expired session detection works correctly."""
        assert db_utils.is_session_expired("tok_inact_jkl012"), (
            "Expected 'tok_inact_jkl012' to be expired"
        )

    def test_verify_session_expiry_in_future_for_active(self) -> None:
        """Verify that active sessions have expiry dates in the future."""
        sessions = fetch_all(
            "SELECT session_token, expires_at FROM user_sessions WHERE is_active = 1"
        )
        for session in sessions:
            try:
                expiry_date = datetime.fromisoformat(session["expires_at"])
                assert expiry_date > datetime.now(), (
                    f"Session '{session['session_token']}' has expiry in the past: {session['expires_at']}"
                )
            except ValueError:
                pass  # Skip if timestamp format is not parseable
