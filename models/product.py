from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Product:
    """Data model representing an ecommerce product resource."""

    id: int = 0
    title: str = ""
    price: float = 0.0
    description: str = ""
    category_id: int = 0
    category_name: str = ""
    images: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Product:
        """Create a Product instance from an API response dictionary.

        Args:
            data: JSON response data representing a product.

        Returns:
            A populated Product instance.
        """
        category = data.get("category", {})
        return cls(
            id=data.get("id", 0),
            title=data.get("title", ""),
            price=float(data.get("price", 0)),
            description=data.get("description", ""),
            category_id=category.get("id", 0) if isinstance(category, dict) else 0,
            category_name=category.get("name", "") if isinstance(category, dict) else str(category),
            images=data.get("images", []),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert the Product instance back to a dictionary.

        Returns:
            A dictionary suitable for API payloads.
        """
        return {
            "id": self.id,
            "title": self.title,
            "price": self.price,
            "description": self.description,
            "categoryId": self.category_id,
            "images": self.images,
        }
