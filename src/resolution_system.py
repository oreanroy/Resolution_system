from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional

from src.data_models.agent import Agent
from src.enums import IssueState, ProductType, StrategyType
from src.data_models.issue import Issue
from src.services import AgentService, IssueService, RoutingStrategyService, UserService


class ResolutionSystem:
    def __init__(self) -> None:
        self.user_service = UserService()
        self.agent_service = AgentService()
        self.issue_service = IssueService()
        self.strategy_service = RoutingStrategyService()

        # Initial strategies setup
        default_strategy_id = self.strategy_service.create_strategy(StrategyType.FCFS)
        self.strategy_service.create_strategy(StrategyType.RATING)
        self.strategy_service.set_active_strategy(default_strategy_id)

        self._pending_issues: List[str] = []
        self._resolved_issues: List[str] = []

    # User functions
    def create_user(self, name: str, email: str, active_products: Iterable[Any]) -> str:
        user_id = self.user_service.create_user(name, email, active_products)
        return user_id

    def delete_user(self, user_id: str) -> bool:
        return self.user_service.delete_user(user_id)

    def get_user_details(self, user_id: str):
        return self.user_service.get_user_details(user_id)

    # Agent functions
    def create_agent(self, agent_email: str, agent_name: str, issue_types: Iterable[Any]) -> str:
        agent_id = self.agent_service.add_agent(agent_email, agent_name, issue_types)
        return agent_id

    def update_agent(self, agent_id: str, *, issue_types: Optional[Iterable[Any]] = None, ratings: Optional[Dict[Any, float]] = None) -> bool:
        return self.agent_service.update_agent(agent_id, issue_types=issue_types, ratings=ratings)

    # Issue functions
    def create_issue(self, transaction_id: str, issue_type: Any, subject: str, description: str, email: str) -> str:
        user = self.user_service.get_user_details(email)
        if user is None:
            user_id = self.user_service.create_user(name=email, email=email, active_products=[issue_type])
        else:
            user_id = user.user_id

        issue_id = self.issue_service.create_issue(transaction_id, issue_type, subject, description, user_id, email)
        issue = self.issue_service.get_issue_by_id(issue_id)
        if issue:
            self.user_service.add_issue(issue)
        self._pending_issues.append(issue_id)
        return issue_id

    def update_issue(self, issue_id: str, status: Any, resolution: Optional[str] = None) -> bool:
        issue = self.issue_service.get_issue_by_id(issue_id)
        if not issue:
            return False
        target_state = IssueState.from_value(status)
        if target_state == IssueState.CLOSED and not issue.agent_id:
            return False
        updated = self.issue_service.update_issue(issue_id, status, resolution)
        if not updated:
            return False
        issue = self.issue_service.get_issue_by_id(issue_id)
        if issue and issue.state == IssueState.CLOSED:
            self._mark_issue_closed(issue)
        return True

    def resolve_issue(self, issue_id: str, resolution: str) -> bool:
        issue = self.issue_service.get_issue_by_id(issue_id)
        if not issue or not issue.agent_id:
            return False
        resolved = self.issue_service.resolve_issue(issue_id, resolution)
        if not resolved:
            return False
        issue = self.issue_service.get_issue_by_id(issue_id)
        if issue:
            self._mark_issue_closed(issue)
        return True

    def assign_issue(self, issue_id: str) -> str:
        issue = self.issue_service.get_issue_by_id(issue_id)
        if not issue:
            return f"Issue {issue_id} not found"
        if issue.agent_id:
            return f"Issue {issue_id} is already assigned to agent {issue.agent_id}"

        agent_map = self.agent_service.list_agents()
        agent_id = self.strategy_service.assign_agent(issue, agent_map.values())
        if agent_id:
            agent = agent_map.get(agent_id)
            if agent:
                agent.record_assignment(issue_id)
            self.issue_service.assign_agent(issue_id, agent_id)
            if issue_id not in self._pending_issues:
                self._pending_issues.append(issue_id)
            return f"Issue {issue_id} assigned to agent {agent_id}"

        supporting_agents = [
            agent for agent in agent_map.values() if issue.issue_type in agent.supported_issue_types
        ]
        if not supporting_agents:
            return f"No agent available to handle issue type {issue.issue_type.value}"

        supporting_agents.sort(key=lambda agent: (len(agent.waitlist), agent.agent_id))
        chosen_agent = supporting_agents[0]
        chosen_agent.enqueue_issue(issue_id)
        self.issue_service.mark_waitlisted(issue_id)
        return f"Issue {issue_id} added to waitlist of Agent {chosen_agent.agent_id}"

    def get_issues(self, filters: Optional[Dict[str, Any]] = None) -> List[Issue]:
        return self.issue_service.get_issue(filters)

    def view_agents_work_history(self) -> Dict[str, List[str]]:
        return self.agent_service.view_agents_work_history()

    @property
    def pending_issues(self) -> List[str]:
        return list(self._pending_issues)

    @property
    def resolved_issues(self) -> List[str]:
        return list(self._resolved_issues)

    def _mark_issue_closed(self, issue: Issue) -> None:
        issue_id = issue.issue_id
        self._pending_issues = [iid for iid in self._pending_issues if iid != issue_id]
        if issue_id not in self._resolved_issues:
            self._resolved_issues.append(issue_id)
        self.user_service.close_issue(issue_id)
        if issue.agent_id:
            agent = self.agent_service.get_agent(issue.agent_id)
            if agent:
                agent.record_resolution(issue_id)
                self._assign_next_from_waitlist(agent)

    def _assign_next_from_waitlist(self, agent: Agent) -> None:
        next_issue_id = agent.take_next_from_waitlist()
        if not next_issue_id:
            return
        next_issue = self.issue_service.get_issue_by_id(next_issue_id)
        if not next_issue:
            return
        agent.record_assignment(next_issue_id)
        self.issue_service.assign_agent(next_issue_id, agent.agent_id)
        if next_issue_id not in self._pending_issues:
            self._pending_issues.append(next_issue_id)

    @staticmethod
    def main() -> None:
        system = ResolutionSystem()

        print("=== Resolution System Demo ===")

        # Create users
        user1 = system.create_user("Alice", "alice@example.com", [ProductType.GOLD])
        user2 = system.create_user("Bob", "bob@example.com", [ProductType.MUTUAL_FUND])
        print(f"Users created: {user1}, {user2}")

        # Create agents
        agent1 = system.create_agent("agent1@example.com", "Agent 1", [ProductType.GOLD, ProductType.INSURANCE])
        agent2 = system.create_agent("agent2@example.com", "Agent 2", [ProductType.MUTUAL_FUND])
        system.update_agent(agent1, ratings={ProductType.GOLD: 4.5, ProductType.INSURANCE: 4.8})
        print(f"Agents created: {agent1}, {agent2}")

        # Create issues
        issue1 = system.create_issue("T1", ProductType.GOLD, "Gold payment failed", "Amount debited but not received", "alice@example.com")
        issue2 = system.create_issue("T2", ProductType.MUTUAL_FUND, "Mutual fund purchase failed", "Unable to invest", "bob@example.com")
        issue3 = system.create_issue("T3", ProductType.GOLD, "Gold purchase pending", "Payment stuck in pending", "bob@example.com")
        print(f"Issues created: {issue1}, {issue2}, {issue3}")

        # Assign issues
        print("Assigning issues...")
        print(system.assign_issue(issue1))
        print(system.assign_issue(issue2))
        print(system.assign_issue(issue3))

        # Resolve first issue to free up agent capacity
        system.resolve_issue(issue1, "Payment auto-reconciled")
        print(f"Issue {issue1} resolved")

        # Update issue
        system.update_issue(issue3, "In Progress", "Waiting for confirmation")
        print(f"Issue {issue3} updated to In Progress")

        # Resolve issue
        system.resolve_issue(issue3, "Payment reversed")
        print(f"Issue {issue3} resolved")

        # View agent history
        print("Agent work history:")
        for agent_id, history in system.view_agents_work_history().items():
            print(agent_id, history)

        print("Pending issues:", system.pending_issues)
        print("Resolved issues:", system.resolved_issues)


if __name__ == "__main__":
    ResolutionSystem.main()
