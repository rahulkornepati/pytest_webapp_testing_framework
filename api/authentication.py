from __future__ import annotations

import base64
import logging
import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any

import requests

from config.api_config import APIConfig


logger = logging.getLogger("ecommerce_framework.api.auth")


class AuthType(Enum):
    """Supported authentication mechanisms."""

    BEARER_TOKEN = auto()
    BASIC_AUTH = auto()
    API_KEY = auto()
    SESSION = auto()
    NO_AUTH = auto()


@dataclass
class AuthenticationHandler:
    """Factory & manager for HTTP authentication strategies.

    Supports Bearer Token, Basic Auth, API Key, and Session-based
    authentication.  Can automatically refresh an expired token when a
    refresh token endpoint is provided.

    Usage:
        >>> auth = AuthenticationHandler(
        ...     auth_type=AuthType.BEARER_TOKEN,
        ...     token="my.jwt.token",
        ...     refresh_endpoint="/auth/refresh"
        ... )
        >>> headers = auth.get_headers()
        >>> headers["Authorization"]
        'Bearer my.jwt.token'
    """

    auth_type: AuthType = AuthType.BEARER_TOKEN
    token: str = ""
    username: str = ""
    password: str = ""
    api_key: str = ""
    api_key_header: str = "X-API-Key"
    refresh_endpoint: str = ""
    base_url: str = ""
    timeout: int = APIConfig.DEFAULT_TIMEOUT

    _session: requests.Session = field(default_factory=requests.Session, repr=False)
    _token_expires_at: float = 0.0
    _token_buffer_seconds: int = 60

    # ── Factory constructors ──────────────────────────────────────────────────

    @classmethod
    def with_bearer_token(
        cls,
        token: str,
        refresh_endpoint: str = "",
        base_url: str = "",
    ) -> AuthenticationHandler:
        """Create a handler that uses Bearer Token authentication.

        Args:
            token: The JWT or opaque bearer token.
            refresh_endpoint: Optional endpoint to refresh an expired token.
            base_url: Base URL used when calling the refresh endpoint.

        Returns:
            A configured AuthenticationHandler instance.
        """
        return cls(
            auth_type=AuthType.BEARER_TOKEN,
            token=token,
            refresh_endpoint=refresh_endpoint,
            base_url=base_url,
        )

    @classmethod
    def with_basic_auth(
        cls,
        username: str,
        password: str,
        base_url: str = "",
    ) -> AuthenticationHandler:
        """Create a handler that uses HTTP Basic Authentication.

        Args:
            username: Basic auth username.
            password: Basic auth password.
            base_url: Base URL for the API.

        Returns:
            A configured AuthenticationHandler instance.
        """
        return cls(
            auth_type=AuthType.BASIC_AUTH,
            username=username,
            password=password,
            base_url=base_url,
        )

    @classmethod
    def with_api_key(
        cls,
        api_key: str,
        header_name: str = "X-API-Key",
        base_url: str = "",
    ) -> AuthenticationHandler:
        """Create a handler that uses an API key in a custom header.

        Args:
            api_key: The API key value.
            header_name: The header name that carries the key.
            base_url: Base URL for the API.

        Returns:
            A configured AuthenticationHandler instance.
        """
        return cls(
            auth_type=AuthType.API_KEY,
            api_key=api_key,
            api_key_header=header_name,
            base_url=base_url,
        )

    @classmethod
    def with_session(
        cls,
        username: str,
        password: str,
        login_endpoint: str,
        base_url: str,
        timeout: int = APIConfig.DEFAULT_TIMEOUT,
    ) -> AuthenticationHandler:
        """Create a handler that authenticates via a session cookie.

        Performs a POST to *login_endpoint* with the credentials, extracts
        the session cookie from the response, and attaches it to every
        subsequent request.

        Args:
            username: Login username / email.
            password: Login password.
            login_endpoint: Path to the login endpoint.
            base_url: Base URL for the API.
            timeout: Request timeout in seconds.

        Returns:
            A configured AuthenticationHandler instance with an active session.
        """
        handler = cls(
            auth_type=AuthType.SESSION,
            username=username,
            password=password,
            base_url=base_url,
            timeout=timeout,
        )
        handler._authenticate_session(login_endpoint)
        return handler

    @classmethod
    def no_auth(cls) -> AuthenticationHandler:
        """Create a handler that sends no credentials (public endpoints).

        Returns:
            A no-authentication handler.
        """
        return cls(auth_type=AuthType.NO_AUTH)

    # ── Public API ────────────────────────────────────────────────────────────

    def get_headers(self) -> dict[str, str]:
        """Return the authentication headers for the configured auth type.

        For Bearer Token auth, the token is refreshed automatically if it
        has expired (or is close to expiring).

        Returns:
            A dictionary of header key-value pairs.

        Raises:
            RuntimeError: If the token has expired and no refresh endpoint
                is available.
        """
        if self.auth_type == AuthType.BEARER_TOKEN:
            self._ensure_token_fresh()
            return {"Authorization": f"Bearer {self.token}"}

        if self.auth_type == AuthType.BASIC_AUTH:
            encoded = base64.b64encode(f"{self.username}:{self.password}".encode()).decode()
            return {"Authorization": f"Basic {encoded}"}

        if self.auth_type == AuthType.API_KEY:
            return {self.api_key_header: self.api_key}

        if self.auth_type == AuthType.SESSION:
            return {}

        return {}

    @property
    def session(self) -> requests.Session:
        """Return the underlying ``requests.Session`` (used by APIClient)."""
        return self._session

    def update_token(self, new_token: str, expires_in: int = 3600) -> None:
        """Update the bearer token and its expiry time.

        Args:
            new_token: The new token value.
            expires_in: Seconds until the token expires (default 1 hour).
        """
        self.token = new_token
        self._token_expires_at = time.time() + expires_in
        logger.info("Bearer token updated — expires in %d seconds", expires_in)

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _authenticate_session(self, login_endpoint: str) -> None:
        """POST credentials to the login endpoint to establish a session."""
        url = f"{self.base_url.rstrip('/')}/{login_endpoint.lstrip('/')}"
        payload: dict[str, str] = {"email": self.username, "password": self.password}
        logger.info("Authenticating session at %s", url)

        response = self._session.post(url, json=payload, timeout=self.timeout)
        response.raise_for_status()
        logger.info("Session established — status=%d", response.status_code)

    def _ensure_token_fresh(self) -> None:
        """Refresh the bearer token if it has expired (or is about to)."""
        if not self.token:
            raise RuntimeError(
                "No bearer token available. "
                "Provide a token or configure a refresh endpoint."
            )

        if self._token_expires_at == 0.0:
            return  # Token never expires (static / long-lived)

        if time.time() < (self._token_expires_at - self._token_buffer_seconds):
            return  # Still fresh

        logger.info("Bearer token expired or near expiry — attempting refresh")
        if not self.refresh_endpoint:
            raise RuntimeError(
                "Bearer token has expired and no refresh endpoint is configured."
            )

        self._refresh_token()

    def _refresh_token(self) -> None:
        """Call the refresh endpoint to obtain a new token."""
        url = f"{self.base_url.rstrip('/')}/{self.refresh_endpoint.lstrip('/')}"
        headers = {"Authorization": f"Bearer {self.token}"}

        response = requests.post(url, headers=headers, timeout=self.timeout)
        response.raise_for_status()

        data: dict[str, Any] = response.json()
        new_token = data.get("access_token") or data.get("token") or data.get("accessToken", "")
        expires_in = data.get("expires_in", 3600)

        if new_token:
            self.update_token(new_token, expires_in)
        else:
            logger.error("Refresh response did not contain a new token: %s", data)
            raise RuntimeError("Token refresh failed — no token in response")
