from typing import Any, Dict, Iterable, List, Optional

from src.data_models.issue import Issue
from src.enums import IssueState, ProductType


class IssueService:
    def __init__(self) -> None:
        self._issues: Dict[str, Issue] = {}
        self._issues_by_user: Dict[str, List[str]] = {}
        self._issues_by_email: Dict[str, List[str]] = {}
        self._sequence = 0

    def _next_id(self) -> str:
        self._sequence += 1
        return f"I{self._sequence}"

    def create_issue(
        self,
        transaction_id: str,
        issue_type: Any,
        subject: str,
        description: str,
        user_id: str,
        user_email: str,
    ) -> str:
        issue_id = self._next_id()
        issue = Issue(
            issue_id=issue_id,
            transaction_id=transaction_id,
            issue_type=ProductType.from_value(issue_type),
            subject=subject,
            description=description,
            state=IssueState.CREATED,
            user_id=user_id,
            user_email=user_email,
        )
        self._issues[issue_id] = issue
        self._issues_by_user.setdefault(user_id, []).append(issue_id)
        self._issues_by_email.setdefault(user_email, []).append(issue_id)
        return issue_id

    def update_issue(self, issue_id: str, status: Any, resolution: Optional[str] = None) -> bool:
        issue = self._issues.get(issue_id)
        if not issue:
            return False
        issue.state = IssueState.from_value(status)
        if resolution is not None:
            issue.resolution = resolution
        return True

    def get_issue(self, filters: Optional[Dict[str, Any]] = None) -> List[Issue]:
        if not filters:
            return list(self._issues.values())

        def matches(issue: Issue) -> bool:
            for key, value in filters.items():
                if key in {"userId", "user_id"} and issue.user_id != value:
                    return False
                if key in {"email", "userEmail", "user_email"} and issue.user_email != value:
                    return False
                if key in {"issueType", "type"} and issue.issue_type != ProductType.from_value(value):
                    return False
                if key in {"status", "state"} and issue.state != IssueState.from_value(value):
                    return False
            return True

        return [issue for issue in self._issues.values() if matches(issue)]

    def assign_agent(self, issue_id: str, agent_id: str) -> bool:
        issue = self._issues.get(issue_id)
        if not issue:
            return False
        issue.state = IssueState.PENDING
        issue.agent_id = agent_id
        return True

    def resolve_issue(self, issue_id: str, resolution: str) -> bool:
        issue = self._issues.get(issue_id)
        if not issue:
            return False
        issue.state = IssueState.CLOSED
        issue.resolution = resolution
        return True

    def list_issues_for_user(self, user_id: str) -> List[Issue]:
        issue_ids = self._issues_by_user.get(user_id, [])
        return [self._issues[iid] for iid in issue_ids if iid in self._issues]

    def list_issues_for_email(self, email: str) -> List[Issue]:
        issue_ids = self._issues_by_email.get(email, [])
        return [self._issues[iid] for iid in issue_ids if iid in self._issues]

    def get_issue_by_id(self, issue_id: str) -> Optional[Issue]:
        return self._issues.get(issue_id)
