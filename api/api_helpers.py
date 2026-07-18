from __future__ import annotations

import logging
import random
import re
from typing import Any

from faker import Faker

from config.api_config import APIConfig
from utils.config_reader import read_json


logger = logging.getLogger("ecommerce_framework.api.helpers")
fake = Faker()

_RANDOM_PLACEHOLDER_RE = re.compile(r"\{\{random\}\}")


class APIHelpers:
    """Collection of reusable helper methods for API tests.

    Provides:
        - Payload builders that read from ``test_data/api_payloads.json``.
        - Randomised test data generation via Faker.
        - Response data extraction utilities.
        - Pagination helpers.
    """

    # ── Payload builders ──────────────────────────────────────────────────────

    @staticmethod
    def load_payload(payload_name: str, **overrides: Any) -> dict[str, Any]:
        """Load a payload template from ``test_data/api_payloads.json``,
        substitute ``{{random}}`` placeholders with unique values, and
        merge runtime overrides.

        Every occurrence of ``{{random}}`` in string values is replaced with
        a unique eight-character hex string, allowing the same payload
        template to be used across multiple test runs without collisions
        (e.g. on email fields).

        Args:
            payload_name: Key in the payloads JSON file.
            **overrides: Key-value pairs to override in the template.

        Returns:
            A complete payload dictionary.

        Raises:
            KeyError: If *payload_name* is not found.
        """
        payloads: dict[str, Any] = read_json("api_payloads.json")
        if payload_name not in payloads:
            msg = f"Payload '{payload_name}' not found in test_data/api_payloads.json"
            raise KeyError(msg)
        template = dict(payloads[payload_name])
        # Substitute {{random}} placeholders with a unique ID
        random_suffix = fake.hexify(text="^^^^^^^^")
        template = APIHelpers._substitute_random(template, random_suffix)
        template.update(overrides)
        return template

    @staticmethod
    def _substitute_random(value: Any, replacement: str) -> Any:
        """Recursively replace ``{{random}}`` placeholders in strings."""
        if isinstance(value, str):
            return _RANDOM_PLACEHOLDER_RE.sub(replacement, value)
        if isinstance(value, dict):
            return {k: APIHelpers._substitute_random(v, replacement) for k, v in value.items()}
        if isinstance(value, list):
            return [APIHelpers._substitute_random(item, replacement) for item in value]
        return value

    @staticmethod
    def load_test_data(data_key: str) -> Any:
        """Load a specific data entry from ``test_data/api_testdata.json``.

        Args:
            data_key: Key in the testdata JSON file.

        Returns:
            The corresponding data value.
        """
        testdata: dict[str, Any] = read_json("api_testdata.json")
        return testdata[data_key]

    # ── Randomised test data generators ───────────────────────────────────────

    @staticmethod
    def random_email() -> str:
        """Generate a random email address."""
        return fake.email()

    @staticmethod
    def random_name() -> str:
        """Generate a random full name."""
        return fake.name()

    @staticmethod
    def random_username() -> str:
        """Generate a random username."""
        return fake.user_name()

    @staticmethod
    def random_password(length: int = 12) -> str:
        """Generate a random password.

        Args:
            length: Character length of the password.

        Returns:
            A secure random password string.
        """
        return fake.password(length=length)

    @staticmethod
    def random_phone() -> str:
        """Generate a random phone number."""
        return fake.phone_number()

    @staticmethod
    def random_address() -> str:
        """Generate a random street address."""
        return fake.street_address()

    @staticmethod
    def random_city() -> str:
        """Generate a random city name."""
        return fake.city()

    @staticmethod
    def random_country() -> str:
        """Generate a random country name."""
        return fake.country()

    @staticmethod
    def random_zip_code() -> str:
        """Generate a random postal code."""
        return fake.postcode()

    @staticmethod
    def random_product_title() -> str:
        """Generate a random product / item title."""
        return fake.catch_phrase()

    @staticmethod
    def random_price(min_price: float = 1.0, max_price: float = 999.99) -> float:
        """Generate a random price within a range.

        Args:
            min_price: Minimum price (inclusive).
            max_price: Maximum price (inclusive).

        Returns:
            A price rounded to two decimal places.
        """
        return round(random.uniform(min_price, max_price), 2)

    @staticmethod
    def random_quantity(min_qty: int = 1, max_qty: int = 10) -> int:
        """Generate a random quantity.

        Args:
            min_qty: Minimum quantity (inclusive).
            max_qty: Maximum quantity (inclusive).

        Returns:
            A random integer within the range.
        """
        return random.randint(min_qty, max_qty)

    @staticmethod
    def random_category_id(category_ids: list[int] | None = None) -> int:
        """Return a random category ID from a provided list or a default set.

        Args:
            category_ids: Optional list of valid category IDs.

        Returns:
            A randomly selected category ID.
        """
        if category_ids:
            return random.choice(category_ids)
        return random.choice([1, 2, 3, 4, 5])

    # ── Response data extractors ──────────────────────────────────────────────

    @staticmethod
    def extract_id(response_json: dict[str, Any] | list[dict[str, Any]]) -> int | None:
        """Extract the ``id`` field from a JSON response.

        Args:
            response_json: Parsed JSON response (dict or list of dicts).

        Returns:
            The ID if found, else ``None``.
        """
        if isinstance(response_json, dict):
            return response_json.get("id")
        if isinstance(response_json, list) and response_json:
            return response_json[0].get("id")
        return None

    @staticmethod
    def extract_ids(response_json: list[dict[str, Any]]) -> list[int]:
        """Extract all ``id`` values from a list response.

        Args:
            response_json: A list of dictionaries.

        Returns:
            A list of integer IDs.
        """
        return [item["id"] for item in response_json if "id" in item]

    @staticmethod
    def find_item_by_field(
        items: list[dict[str, Any]],
        field: str,
        value: Any,
    ) -> dict[str, Any] | None:
        """Find the first item in a list whose *field* matches *value*.

        Args:
            items: List of dictionaries.
            field: Key to search on.
            value: Expected value.

        Returns:
            The matching dict, or ``None``.
        """
        for item in items:
            if item.get(field) == value:
                return item
        return None

    # ── Pagination helpers ────────────────────────────────────────────────────

    @staticmethod
    def pagination_params(
        page: int | None = None,
        limit: int | None = None,
    ) -> dict[str, int]:
        """Return query-string params for paginated endpoints.

        Args:
            page: Page number (default from ``APIConfig.DEFAULT_PAGE``).
            limit: Items per page (default from ``APIConfig.DEFAULT_PAGE_SIZE``).

        Returns:
            A dict with ``offset`` and ``limit`` (or ``page`` / ``per_page``).
        """
        return {
            "page": page or APIConfig.DEFAULT_PAGE,
            "limit": limit or APIConfig.DEFAULT_PAGE_SIZE,
        }
