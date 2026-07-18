from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class OrderItem:
    """Data model representing a single item within an order."""

    product_id: int = 0
    quantity: int = 0
    price: float = 0.0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> OrderItem:
        """Create an OrderItem from an API response dictionary."""
        return cls(
            product_id=data.get("productId", 0),
            quantity=data.get("quantity", 0),
            price=float(data.get("price", 0)),
        )


@dataclass
class Order:
    """Data model representing an order resource."""

    id: int = 0
    user_id: int = 0
    date: str = ""
    products: list[OrderItem] = field(default_factory=list)
    total: float = 0.0
    status: str = "pending"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Order:
        """Create an Order instance from an API response dictionary.

        Args:
            data: JSON response data representing an order.

        Returns:
            A populated Order instance.
        """
        items = [OrderItem.from_dict(item) for item in data.get("products", [])]
        return cls(
            id=data.get("id", 0),
            user_id=data.get("userId", 0),
            date=data.get("date", ""),
            products=items,
            total=float(data.get("total", 0)),
            status=data.get("status", "pending"),
        )
