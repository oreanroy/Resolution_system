from enum import Enum


class StrategyType(Enum):
    FCFS = "fcfs"
    RATING = "rating"

    @classmethod
    def from_value(cls, value: "StrategyType | str") -> "StrategyType":
        if isinstance(value, cls):
            return value
        normalized = str(value).strip().lower()
        for member in cls:
            if member.value == normalized or member.name.lower() == normalized:
                return member
        raise ValueError(f"Unsupported strategy type: {value}")
