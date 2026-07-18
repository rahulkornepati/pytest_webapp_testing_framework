from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any, Generator

import pytest
from dotenv import load_dotenv

from api.api_client import APIClient
from api.api_helpers import APIHelpers
from api.authentication import AuthenticationHandler, AuthType
from api.endpoints import APIEndpoints
from config.api_config import APIConfig
from utils.config_reader import read_json


ROOT_DIR = Path(__file__).resolve().parents[1]

# Ensure .env is loaded for API tests too
load_dotenv(ROOT_DIR / ".env")


# ── Fixtures ─────────────────────────────────────────────────────────────────────


@pytest.fixture(scope="session")
def api_base_url() -> str:
    """Return the base URL for the API under test.

    Reads from environment variable ``API_BASE_URL``, falling back to the
    default in ``APIConfig``.

    Returns:
        The API base URL string.
    """
    return os.getenv("API_BASE_URL", APIConfig.BASE_URL)


@pytest.fixture(scope="session")
def api_timeout() -> int:
    """Return the default request timeout for API tests.

    Returns:
        Timeout value in seconds.
    """
    return APIConfig.DEFAULT_TIMEOUT


@pytest.fixture(scope="session")
def api_default_headers() -> dict[str, str]:
    """Return default headers sent with every API request.

    Returns:
        A dictionary of header key-value pairs.
    """
    return {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }


@pytest.fixture(scope="session")
def api_helpers() -> APIHelpers:
    """Provide the APIHelpers utility instance.

    Returns:
        An ``APIHelpers`` instance.
    """
    return APIHelpers()


@pytest.fixture(scope="session")
def auth_handler(api_base_url: str) -> AuthenticationHandler:
    """Create an authenticated session for API tests.

    Attempts to log in with the configured credentials and returns an
    ``AuthenticationHandler`` with an active bearer token.

    Falls back to ``NO_AUTH`` if no credentials are configured.

    Args:
        api_base_url: The base URL from the session fixture.

    Returns:
        An ``AuthenticationHandler`` configured for authenticated requests.
    """
    email = os.getenv("API_USERNAME", APIConfig.USERNAME)
    password = os.getenv("API_PASSWORD", APIConfig.PASSWORD)
    token = os.getenv("API_TOKEN", APIConfig.TOKEN)
    api_key = os.getenv("API_KEY", APIConfig.API_KEY)

    if token:
        return AuthenticationHandler.with_bearer_token(
            token=token,
            base_url=api_base_url,
        )

    if api_key:
        return AuthenticationHandler.with_api_key(
            api_key=api_key,
            base_url=api_base_url,
        )

    if email and password:
        try:
            client = APIClient(
                base_url=api_base_url,
                auth_handler=AuthenticationHandler.no_auth(),
                timeout=APIConfig.DEFAULT_TIMEOUT,
            )
            response = client.post(APIEndpoints.login(), json={"email": email, "password": password})
            if response.status_code == 200:
                data: dict[str, Any] = response.json()
                token = data.get("access_token") or data.get("token", "")
                if token:
                    return AuthenticationHandler.with_bearer_token(
                        token=token,
                        refresh_endpoint=APIEndpoints.refresh_token(),
                        base_url=api_base_url,
                    )
        except Exception:
            logger = logging.getLogger("ecommerce_framework.api.conftest")
            logger.warning("Could not authenticate API test session — falling back to NO_AUTH")

    return AuthenticationHandler.no_auth()


@pytest.fixture(scope="session")
def api_client(
    api_base_url: str,
    auth_handler: AuthenticationHandler,
    api_default_headers: dict[str, str],
    api_timeout: int,
) -> APIClient:
    """Provide a reusable ``APIClient`` instance configured for API tests.

    The client is constructed once per test session and used across all
    test functions.

    Args:
        api_base_url: Base URL from the session fixture.
        auth_handler: Authenticated handler from the session fixture.
        api_default_headers: Default headers from the session fixture.
        api_timeout: Timeout from the session fixture.

    Returns:
        An ``APIClient`` ready to make HTTP requests.
    """
    return APIClient(
        base_url=api_base_url,
        auth_handler=auth_handler,
        default_headers=api_default_headers,
        timeout=api_timeout,
    )


@pytest.fixture(scope="function")
def unauthenticated_client(
    api_base_url: str,
    api_default_headers: dict[str, str],
    api_timeout: int,
) -> APIClient:
    """Provide a **non-authenticated** ``APIClient`` (for negative auth tests).

    Returns:
        An ``APIClient`` **without** any authentication headers.
    """
    return APIClient(
        base_url=api_base_url,
        auth_handler=AuthenticationHandler.no_auth(),
        default_headers=api_default_headers,
        timeout=api_timeout,
    )


@pytest.fixture(scope="session")
def api_test_data() -> dict[str, Any]:
    """Provide the full API test data dictionary.

    Returns:
        The parsed contents of ``test_data/api_testdata.json``.
    """
    return read_json("api_testdata.json")


@pytest.fixture(scope="function")
def cleanup_created_resources(
    api_client: APIClient,
) -> Generator[list[dict[str, Any]], None, None]:
    """Track and clean up resources created during a test.

    Yields a mutable list that tests can append resource descriptors to.
    After the test completes, each resource is deleted in reverse order.

    Example:
        >>> def test_something(cleanup_created_resources):
        ...     resp = client.post("/products", json={...})
        ...     cleanup_created_resources.append({"type": "product", "id": resp.json()["id"]})
    """
    created: list[dict[str, Any]] = []
    yield created
    logger = logging.getLogger("ecommerce_framework.api.conftest")
    for resource in reversed(created):
        resource_type = resource.get("type", "")
        resource_id = resource.get("id")
        if resource_type and resource_id:
            try:
                delete_map = {
                    "product": APIEndpoints.product_by_id(resource_id),
                    "cart": APIEndpoints.cart_by_id(resource_id),
                    "order": APIEndpoints.order_by_id(resource_id),
                    "user": APIEndpoints.user_by_id(resource_id),
                }
                endpoint = delete_map.get(resource_type)
                if endpoint:
                    resp = api_client.delete(endpoint)
                    logger.info(
                        "Cleanup: deleted %s #%s — status=%d",
                        resource_type,
                        resource_id,
                        resp.status_code,
                    )
            except Exception:
                logger.exception("Cleanup failed for %s #%s", resource_type, resource_id)
