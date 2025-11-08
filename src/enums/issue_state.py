from enum import Enum


class IssueState(Enum):
    CREATED = "created"
    PENDING = "pending"
    CLOSED = "closed"

    @classmethod
    def from_value(cls, value: "IssueState | str") -> "IssueState":
        if isinstance(value, cls):
            return value
        normalized = str(value).strip().lower()
        mapping = {
            "created": cls.CREATED,
            "open": cls.CREATED,
            "pending": cls.PENDING,
            "in progress": cls.PENDING,
            "waiting": cls.PENDING,
            "closed": cls.CLOSED,
            "resolved": cls.CLOSED,
        }
        if normalized in mapping:
            return mapping[normalized]
        raise ValueError(f"Unsupported issue state: {value}")
