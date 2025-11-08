from enum import Enum


class ProductType(Enum):
    GOLD = "gold"
    FIXED_DEPOSIT = "fd"
    INSURANCE = "insurance"
    MUTUAL_FUND = "mutual-fund"

    @classmethod
    def from_value(cls, value: "ProductType | str") -> "ProductType":
        if isinstance(value, cls):
            return value
        normalized = str(value).strip().lower()
        for member in cls:
            if member.value == normalized or member.name.lower() == normalized:
                return member
        raise ValueError(f"Unsupported product type: {value}")
