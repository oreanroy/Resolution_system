from typing import Dict, Iterable, List, Optional

from src.data_models.user import User
from src.data_models.issue import Issue
from src.enums import ProductType


class UserService:
    def __init__(self) -> None:
        self._users: Dict[str, User] = {}
        self._users_by_email: Dict[str, str] = {}
        self._sequence = 0
        self._issues: Dict[str, Issue] = {}

    def _next_id(self) -> str:
        self._sequence += 1
        return f"U{self._sequence}"

    def create_user(self, name: str, email: str, active_products: Iterable[str]) -> str:
        if email in self._users_by_email:
            return self._users_by_email[email]
        user_id = self._next_id()
        products = {ProductType.from_value(product) for product in active_products}
        user = User(user_id=user_id, name=name, email=email, active_products=products)
        self._users[user_id] = user
        self._users_by_email[email] = user_id
        return user_id

    def delete_user(self, user_id: str) -> bool:
        user = self._users.pop(user_id, None)
        if not user:
            return False
        self._users_by_email.pop(user.email, None)
        for issue_id in list(user.active_issue_ids):
            self._issues.pop(issue_id, None)
        return True

    def get_user_details(self, user_id: str) -> Optional[User]:
        return self._users.get(user_id)

    def get_issues(self, user_identifier: str) -> List[Issue]:
        user_id = self._users_by_email.get(user_identifier, user_identifier)
        user = self._users.get(user_id)
        if not user:
            return []
        return [self._issues[issue_id] for issue_id in user.created_issue_ids if issue_id in self._issues]

    def add_issue(self, issue: Issue) -> None:
        self._issues[issue.issue_id] = issue
        user = self._users.get(issue.user_id)
        if user:
            user.created_issue_ids.append(issue.issue_id)
            user.active_issue_ids.add(issue.issue_id)

    def close_issue(self, issue_id: str) -> None:
        issue = self._issues.get(issue_id)
        if not issue:
            return
        user = self._users.get(issue.user_id)
        if user:
            user.active_issue_ids.discard(issue_id)
