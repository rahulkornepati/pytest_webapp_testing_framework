from __future__ import annotations

import logging
import time
from typing import Any, Callable

import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from api.authentication import AuthenticationHandler
from config.api_config import APIConfig


logger = logging.getLogger("ecommerce_framework.api.client")


class APIClient:
    """Reusable HTTP client for REST API interactions.

    Features:
        - Logs every request (method, URL, headers, payload, response time).
        - Automatic retry on configurable status codes.
        - Pluggable authentication via :class:`AuthenticationHandler`.
        - Hooks (``before_request``, ``after_request``) for extensibility.

    Usage:
        >>> client = APIClient(base_url="https://api.example.com/v1")
        >>> response = client.get("/products")
        >>> response.status_code
        200
    """

    def __init__(
        self,
        base_url: str = "",
        auth_handler: AuthenticationHandler | None = None,
        default_headers: dict[str, str] | None = None,
        timeout: int = APIConfig.DEFAULT_TIMEOUT,
        max_retries: int = APIConfig.MAX_RETRIES,
        retry_backoff: float = APIConfig.RETRY_BACKOFF_FACTOR,
        retry_status_codes: tuple[int, ...] = APIConfig.RETRY_STATUS_CODES,
        logger_prefix: str = "API",
    ) -> None:
        """Initialise the API client.

        Args:
            base_url: Root URL of the API.  If empty, ``APIConfig.BASE_URL``
                is used.
            auth_handler: Optional authentication strategy.
            default_headers: Headers sent with every request.
            timeout: Default request timeout in seconds.
            max_retries: Maximum number of retries for failed requests.
            retry_backoff: Exponential backoff factor.
            retry_status_codes: HTTP status codes that trigger a retry.
            logger_prefix: Label used in log messages.
        """
        self.base_url = (base_url or APIConfig.BASE_URL).rstrip("/")
        self.auth_handler = auth_handler or AuthenticationHandler.no_auth()
        self.default_headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            **(default_headers or {}),
        }
        self.timeout = timeout
        self.logger_prefix = logger_prefix

        # -- Retry strategy ----------------------------------------------------
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=retry_backoff,
            status_forcelist=list(retry_status_codes),
            allowed_methods=frozenset({"GET", "PUT", "POST", "PATCH", "DELETE"}),
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)

        # -- Session -----------------------------------------------------------
        self._session: requests.Session = self.auth_handler.session
        self._session.headers.update(self.default_headers)
        self._session.mount("https://", adapter)
        self._session.mount("http://", adapter)

        # -- Hooks -------------------------------------------------------------
        self.before_request: Callable[..., None] | None = None
        self.after_request: Callable[..., None] | None = None

    # ── HTTP verb methods ─────────────────────────────────────────────────────

    def get(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> requests.Response:
        """Send a GET request.

        Args:
            endpoint: Path relative to ``base_url`` (e.g. ``/products``).
            params: Query-string parameters.
            headers: Additional headers for this request only.
            **kwargs: Passed through to ``requests.Session.get``.

        Returns:
            The server response.
        """
        return self._request("GET", endpoint, params=params, headers=headers, **kwargs)

    def post(
        self,
        endpoint: str,
        json: dict[str, Any] | list[Any] | None = None,
        data: Any = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> requests.Response:
        """Send a POST request.

        Args:
            endpoint: Path relative to ``base_url``.
            json: JSON-serializable request body.
            data: Raw request body (used when ``json`` is not set).
            params: Query-string parameters.
            headers: Additional headers for this request only.
            **kwargs: Passed through to ``requests.Session.post``.

        Returns:
            The server response.
        """
        return self._request("POST", endpoint, json=json, data=data, params=params, headers=headers, **kwargs)

    def put(
        self,
        endpoint: str,
        json: dict[str, Any] | list[Any] | None = None,
        data: Any = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> requests.Response:
        """Send a PUT request.

        Args:
            endpoint: Path relative to ``base_url``.
            json: JSON-serializable request body.
            data: Raw request body.
            params: Query-string parameters.
            headers: Additional headers.
            **kwargs: Passed through to ``requests.Session.put``.

        Returns:
            The server response.
        """
        return self._request("PUT", endpoint, json=json, data=data, params=params, headers=headers, **kwargs)

    def patch(
        self,
        endpoint: str,
        json: dict[str, Any] | list[Any] | None = None,
        data: Any = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> requests.Response:
        """Send a PATCH request.

        Args:
            endpoint: Path relative to ``base_url``.
            json: JSON-serializable request body.
            data: Raw request body.
            params: Query-string parameters.
            headers: Additional headers.
            **kwargs: Passed through to ``requests.Session.patch``.

        Returns:
            The server response.
        """
        return self._request("PATCH", endpoint, json=json, data=data, params=params, headers=headers, **kwargs)

    def delete(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> requests.Response:
        """Send a DELETE request.

        Args:
            endpoint: Path relative to ``base_url``.
            params: Query-string parameters.
            headers: Additional headers.
            **kwargs: Passed through to ``requests.Session.delete``.

        Returns:
            The server response.
        """
        return self._request("DELETE", endpoint, params=params, headers=headers, **kwargs)

    # ── Internal request dispatcher ───────────────────────────────────────────

    def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs: Any,
    ) -> requests.Response:
        """Core request dispatcher — logs, sends, measures, returns.

        Args:
            method: HTTP method (GET, POST, PUT, PATCH, DELETE).
            endpoint: Path relative to ``base_url``.
            **kwargs: Additional arguments for ``requests.Session.request``.

        Returns:
            The server response.
        """
        url = f"{self.base_url}{endpoint}"
        merged_headers = {
            **self.default_headers,
            **self.auth_handler.get_headers(),
            **(kwargs.pop("headers", {}) or {}),
        }

        # -- before_request hook -----------------------------------------------
        if self.before_request:
            self.before_request(method=method, url=url, headers=merged_headers, **kwargs)

        # -- Log request -------------------------------------------------------
        log_payload = kwargs.get("json") or kwargs.get("data") or {}
        logger.info(
            "[%s] >>> %s %s | headers=%s | payload=%s",
            self.logger_prefix,
            method,
            url,
            _sanitise_headers(merged_headers),
            _truncate(str(log_payload)),
        )

        # -- Execute -----------------------------------------------------------
        start_time = time.perf_counter()
        try:
            response: requests.Response = self._session.request(
                method=method,
                url=url,
                headers=merged_headers,
                timeout=self.timeout,
                **kwargs,
            )
        except requests.ConnectionError:
            logger.exception("[%s] ConnectionError for %s %s", self.logger_prefix, method, url)
            raise
        except requests.Timeout:
            logger.exception("[%s] Timeout for %s %s (timeout=%ss)", self.logger_prefix, method, url, self.timeout)
            raise

        elapsed = time.perf_counter() - start_time

        # -- Log response ------------------------------------------------------
        try:
            response_body = response.json()
        except (ValueError, requests.JSONDecodeError):
            response_body = response.text

        logger.info(
            "[%s] <<< %s %s | status=%d | time=%.3fs | response=%s",
            self.logger_prefix,
            method,
            url,
            response.status_code,
            elapsed,
            _truncate(str(response_body)),
        )

        # -- after_request hook ------------------------------------------------
        if self.after_request:
            self.after_request(
                method=method,
                url=url,
                response=response,
                elapsed=elapsed,
                **kwargs,
            )

        return response

    # ── Session management ────────────────────────────────────────────────────

    def close(self) -> None:
        """Close the underlying ``requests.Session``."""
        self._session.close()
        logger.info("[%s] Session closed", self.logger_prefix)

    def reset_session(self) -> None:
        """Close and recreate the underlying session (e.g. after auth logout)."""
        self._session.close()
        self._session = self.auth_handler.session
        self._session.headers.update(self.default_headers)
        logger.info("[%s] Session reset", self.logger_prefix)


# ── Internal helpers ──────────────────────────────────────────────────────────────


def _sanitise_headers(headers: dict[str, str]) -> dict[str, str]:
    """Mask sensitive header values (Authorization, X-API-Key, etc.) for logging."""
    SENSITIVE_KEYS = {"authorization", "x-api-key", "api-key", "token", "cookie"}
    sanitised: dict[str, str] = {}
    for key, value in headers.items():
        if key.lower() in SENSITIVE_KEYS and value:
            sanitised[key] = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else "***"
        else:
            sanitised[key] = value
    return sanitised


def _truncate(text: str, max_length: int = 500) -> str:
    """Truncate long strings for log readability."""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "... (truncated)"
