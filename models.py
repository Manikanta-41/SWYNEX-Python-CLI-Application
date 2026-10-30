"""Data model for a single expense."""
from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass
class Expense:
    id: int
    amount: Decimal
    category: str
    description: str
    date: date

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "amount": str(self.amount),  # string avoids float rounding errors
            "category": self.category,
            "description": self.description,
            "date": self.date.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Expense":
        """Raises KeyError/ValueError/InvalidOperation on malformed data."""
        return cls(
            id=int(data["id"]),
            amount=Decimal(data["amount"]),
            category=str(data["category"]),
            description=str(data["description"]),
            date=date.fromisoformat(data["date"]),
        )
