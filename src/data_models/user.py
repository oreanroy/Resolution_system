from dataclasses import dataclass, field
from typing import List, Set

from src.enums import ProductType


@dataclass
class User:
    user_id: str
    name: str
    email: str
    active_products: Set[ProductType] = field(default_factory=set)
    active_issue_ids: Set[str] = field(default_factory=set)
    created_issue_ids: List[str] = field(default_factory=list)
