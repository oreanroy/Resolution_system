from dataclasses import dataclass
from typing import Optional

from src.enums import IssueState, ProductType


@dataclass
class Issue:
    issue_id: str
    transaction_id: str
    issue_type: ProductType
    subject: str
    description: str
    state: IssueState
    user_id: str
    user_email: str
    agent_id: Optional[str] = None
    resolution: Optional[str] = None
