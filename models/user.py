from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class User:
    """Data model representing a user resource."""

    id: int = 0
    email: str = ""
    name: str = ""
    role: str = "customer"
    avatar: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> User:
        """Create a User instance from an API response dictionary.

        Args:
            data: JSON response data representing a user.

        Returns:
            A populated User instance.
        """
        return cls(
            id=data.get("id", 0),
            email=data.get("email", ""),
            name=data.get("name", ""),
            role=data.get("role", "customer"),
            avatar=data.get("avatar", ""),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert the User instance back to a dictionary.

        Returns:
            A dictionary suitable for API payloads.
        """
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "role": self.role,
            "avatar": self.avatar,
        }
