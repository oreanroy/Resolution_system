from collections import deque
from dataclasses import dataclass, field
from typing import Deque, Dict, List, Optional, Set

from src.enums import ProductType


@dataclass
class Agent:
    agent_id: str
    name: str
    email: str
    supported_issue_types: Set[ProductType]
    ratings: Dict[ProductType, float] = field(default_factory=dict)
    resolved_issue_ids: List[str] = field(default_factory=list)
    active_issue_id: Optional[str] = None
    is_occupied: bool = False
    waitlist: Deque[str] = field(default_factory=deque)

    def is_available_for(self, issue_type: ProductType) -> bool:
        return not self.is_occupied and self.active_issue_id is None and issue_type in self.supported_issue_types

    def record_assignment(self, issue_id: str) -> None:
        try:
            self.waitlist.remove(issue_id)
        except ValueError:
            pass
        self.active_issue_id = issue_id
        self.is_occupied = True

    def record_resolution(self, issue_id: str) -> None:
        if issue_id not in self.resolved_issue_ids:
            self.resolved_issue_ids.append(issue_id)
        self.active_issue_id = None
        self.is_occupied = False

    def enqueue_issue(self, issue_id: str) -> None:
        if issue_id not in self.waitlist and issue_id != self.active_issue_id:
            self.waitlist.append(issue_id)

    def take_next_from_waitlist(self) -> Optional[str]:
        if not self.waitlist:
            return None
        return self.waitlist.popleft()
