from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import jsonschema
import requests

from config.api_config import APIConfig


logger = logging.getLogger("ecommerce_framework.api.assertions")

SCHEMA_DIR = Path(__file__).resolve().parents[1] / "schemas"


class APIAssertions:
    """Collection of reusable assertion methods for API test validation.

    Every method raises ``AssertionError`` on failure with a descriptive
    message, keeping test code clean and DRY.
    """

    # ── Status code assertions ────────────────────────────────────────────────

    @staticmethod
    def assert_status_code(response: requests.Response, expected: int) -> None:
        """Assert the HTTP response status code matches the expected value.

        Args:
            response: The server response.
            expected: Expected HTTP status code.

        Raises:
            AssertionError: If status codes differ.
        """
        actual = response.status_code
        assert actual == expected, (
            f"Expected status code {expected}, got {actual}. "
            f"Response body: {_safe_body(response)}"
        )

    @staticmethod
    def assert_status_ok(response: requests.Response) -> None:
        """Assert the response status code is in the 200 range.

        Args:
            response: The server response.

        Raises:
            AssertionError: If status is not 2xx.
        """
        assert 200 <= response.status_code < 300, (
            f"Expected 2xx status code, got {response.status_code}. "
            f"Response body: {_safe_body(response)}"
        )

    @staticmethod
    def assert_status_created(response: requests.Response) -> None:
        """Assert the response status code is 201 Created.

        Args:
            response: The server response.

        Raises:
            AssertionError: If status is not 201.
        """
        APIAssertions.assert_status_code(response, 201)

    @staticmethod
    def assert_status_no_content(response: requests.Response) -> None:
        """Assert the response status code is 204 No Content.

        Args:
            response: The server response.

        Raises:
            AssertionError: If status is not 204.
        """
        APIAssertions.assert_status_code(response, 204)

    @staticmethod
    def assert_status_unauthorized(response: requests.Response) -> None:
        """Assert the response status code is 401 Unauthorized.

        Args:
            response: The server response.

        Raises:
            AssertionError: If status is not 401.
        """
        APIAssertions.assert_status_code(response, 401)

    @staticmethod
    def assert_status_forbidden(response: requests.Response) -> None:
        """Assert the response status code is 403 Forbidden.

        Args:
            response: The server response.

        Raises:
            AssertionError: If status is not 403.
        """
        APIAssertions.assert_status_code(response, 403)

    @staticmethod
    def assert_status_not_found(response: requests.Response) -> None:
        """Assert the response status code is 404 Not Found.

        Args:
            response: The server response.

        Raises:
            AssertionError: If status is not 404.
        """
        APIAssertions.assert_status_code(response, 404)

    # ── JSON body assertions ──────────────────────────────────────────────────

    @staticmethod
    def assert_json_has_key(response: requests.Response, key: str) -> None:
        """Assert the JSON response body contains a specific key.

        Args:
            response: The server response.
            key: The expected key name.

        Raises:
            AssertionError: If the key is absent.
        """
        body = response.json()
        assert key in body, f"Response JSON does not contain key '{key}'. Body: {body}"

    @staticmethod
    def assert_json_has_keys(response: requests.Response, keys: list[str]) -> None:
        """Assert the JSON response body contains all specified keys.

        Args:
            response: The server response.
            keys: List of expected key names.

        Raises:
            AssertionError: If any key is absent.
        """
        body = response.json()
        missing = [k for k in keys if k not in body]
        assert not missing, f"Response JSON missing keys: {missing}. Body: {body}"

    @staticmethod
    def assert_json_value(
        response: requests.Response,
        key: str,
        expected: Any,
    ) -> None:
        """Assert a specific key in the JSON response equals the expected value.

        Args:
            response: The server response.
            key: The key to check.
            expected: The expected value.

        Raises:
            AssertionError: If the value does not match.
        """
        body = response.json()
        actual = body.get(key)
        assert actual == expected, (
            f"Expected '{key}' = {expected!r}, got {actual!r}. Body: {body}"
        )

    @staticmethod
    def assert_json_type(response: requests.Response, key: str, expected_type: type) -> None:
        """Assert the type of a JSON value matches the expected type.

        Args:
            response: The server response.
            key: The key to check.
            expected_type: The expected Python type (e.g. ``int``, ``str``, ``list``).

        Raises:
            AssertionError: If the type does not match.
        """
        body = response.json()
        actual = body.get(key)
        assert isinstance(actual, expected_type), (
            f"Expected '{key}' to be of type {expected_type.__name__}, "
            f"got {type(actual).__name__} (value: {actual!r})"
        )

    @staticmethod
    def assert_json_not_empty(response: requests.Response) -> None:
        """Assert the JSON response body is not empty.

        Args:
            response: The server response.

        Raises:
            AssertionError: If the body is empty.
        """
        body = response.json()
        assert body, f"Expected non-empty JSON response, got empty. Status: {response.status_code}"

    @staticmethod
    def assert_list_length(response: requests.Response, min_length: int = 1) -> None:
        """Assert a JSON list response has at least *min_length* items.

        Args:
            response: The server response.
            min_length: Minimum expected number of items.

        Raises:
            AssertionError: If the list is shorter than expected.
        """
        body = response.json()
        assert isinstance(body, list), f"Expected JSON list, got {type(body).__name__}"
        assert len(body) >= min_length, (
            f"Expected list length >= {min_length}, got {len(body)}"
        )

    @staticmethod
    def assert_error_message_contains(response: requests.Response, substring: str) -> None:
        """Assert the JSON error response contains a substring.

        Looks in common error fields: ``message``, ``error``, ``detail``.

        Args:
            response: The server response.
            substring: Expected text fragment.

        Raises:
            AssertionError: If no error field contains the substring.
        """
        body = response.json()
        for field in ("message", "error", "detail", "statusMessage"):
            value = body.get(field, "")
            if isinstance(value, str) and substring in value:
                return
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, str) and substring in item:
                        return
        raise AssertionError(
            f"No error field contains {substring!r}. Body: {body}"
        )

    # ── Schema validation ─────────────────────────────────────────────────────

    @staticmethod
    def assert_valid_schema(
        response: requests.Response,
        schema_name: str,
    ) -> None:
        """Validate the JSON response against a JSON Schema file.

        Schema files are stored in ``schemas/<schema_name>.json``.

        Args:
            response: The server response.
            schema_name: Name of the schema file (without ``.json``).

        Raises:
            AssertionError: If validation fails.
            FileNotFoundError: If the schema file does not exist.
        """
        schema_path = SCHEMA_DIR / f"{schema_name}.json"
        if not schema_path.exists():
            raise FileNotFoundError(f"Schema file not found: {schema_path}")

        with schema_path.open(encoding="utf-8") as f:
            schema: dict[str, Any] = json.load(f)

        body = response.json()
        try:
            jsonschema.validate(instance=body, schema=schema)
        except jsonschema.ValidationError as exc:
            raise AssertionError(
                f"JSON Schema validation failed for '{schema_name}':\n"
                f"  Path:    {exc.json_path}\n"
                f"  Reason:  {exc.message}\n"
                f"  Body:    {_safe_body(response)}"
            ) from exc

    # ── Header assertions ─────────────────────────────────────────────────────

    @staticmethod
    def assert_header_present(response: requests.Response, header: str) -> None:
        """Assert a specific HTTP header is present in the response.

        Args:
            response: The server response.
            header: Header name.

        Raises:
            AssertionError: If the header is absent.
        """
        assert header in response.headers, (
            f"Response header '{header}' not found. "
            f"Available headers: {list(response.headers.keys())}"
        )

    @staticmethod
    def assert_content_type(response: requests.Response, expected: str = "application/json") -> None:
        """Assert the response Content-Type header matches the expected value.

        Args:
            response: The server response.
            expected: Expected Content-Type value.

        Raises:
            AssertionError: If the Content-Type is different.
        """
        actual = response.headers.get("Content-Type", "")
        assert expected in actual, (
            f"Expected Content-Type containing '{expected}', got '{actual}'"
        )

    # ── Response time assertion ───────────────────────────────────────────────

    @staticmethod
    def assert_response_time_less_than(
        response: requests.Response,
        max_seconds: float = APIConfig.MAX_ACCEPTABLE_RESPONSE_TIME_SECONDS,
    ) -> None:
        """Assert the response was received within a time budget.

        Args:
            response: The server response.
            max_seconds: Maximum acceptable response time.

        Raises:
            AssertionError: If the response took longer than *max_seconds*.
        """
        elapsed = response.elapsed.total_seconds()
        assert elapsed <= max_seconds, (
            f"Response time {elapsed:.3f}s exceeded max of {max_seconds}s "
            f"for {response.request.method} {response.request.url}"
        )

    # ── Business-logic assertions ─────────────────────────────────────────────

    @staticmethod
    def assert_id_is_positive(response: requests.Response) -> None:
        """Assert the JSON body contains a positive integer ``id`` field.

        Args:
            response: The server response.

        Raises:
            AssertionError: If ``id`` is missing, not an int, or not positive.
        """
        body = response.json()
        item_id = body.get("id")
        assert item_id is not None, f"Response has no 'id' field. Body: {body}"
        assert isinstance(item_id, int), f"Expected 'id' to be int, got {type(item_id).__name__}"
        assert item_id > 0, f"Expected positive 'id', got {item_id}"

    @staticmethod
    def assert_pagination(response: requests.Response) -> None:
        """Assert the response has pagination metadata in its body.

        Expects keys like ``total``, ``page``, ``per_page``, or ``pages``.

        Args:
            response: The server response.

        Raises:
            AssertionError: If no pagination fields are found.
        """
        body = response.json()
        pagination_keys = {"total", "page", "per_page", "pages", "offset", "limit", "count"}
        found = [k for k in pagination_keys if k in body]
        assert found, (
            f"No pagination fields found in response. "
            f"Expected at least one of {pagination_keys}. Body: {_safe_body(response)}"
        )


# ── Internal helper ─────────────────────────────────────────────────────────────


def _safe_body(response: requests.Response, max_length: int = 500) -> str:
    """Return a truncated string representation of the response body."""
    try:
        text = response.text
    except Exception:
        return "<unreadable body>"
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."
