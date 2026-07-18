from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class CartItem:
    """Data model representing a single item within a cart."""

    product_id: int = 0
    quantity: int = 0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CartItem:
        """Create a CartItem from an API response dictionary."""
        return cls(
            product_id=data.get("productId", 0),
            quantity=data.get("quantity", 0),
        )


@dataclass
class Cart:
    """Data model representing a cart resource with its items."""

    id: int = 0
    user_id: int = 0
    date: str = ""
    products: list[CartItem] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Cart:
        """Create a Cart instance from an API response dictionary.

        Args:
            data: JSON response data representing a cart.

        Returns:
            A populated Cart instance.
        """
        items = [CartItem.from_dict(item) for item in data.get("products", [])]
        return cls(
            id=data.get("id", 0),
            user_id=data.get("userId", 0),
            date=data.get("date", ""),
            products=items,
        )
