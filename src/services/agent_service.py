from typing import Any, Dict, Iterable, Optional

from src.data_models.agent import Agent
from src.enums import ProductType


class AgentService:
    def __init__(self) -> None:
        self._agents: Dict[str, Agent] = {}
        self._agents_by_email: Dict[str, str] = {}
        self._sequence = 0

    def _next_id(self) -> str:
        self._sequence += 1
        return f"A{self._sequence}"

    def add_agent(self, agent_email: str, agent_name: str, issue_types: Iterable[Any]) -> str:
        if agent_email in self._agents_by_email:
            return self._agents_by_email[agent_email]
        agent_id = self._next_id()
        supported = {ProductType.from_value(issue_type) for issue_type in issue_types}
        agent = Agent(agent_id=agent_id, name=agent_name, email=agent_email, supported_issue_types=supported)
        self._agents[agent_id] = agent
        self._agents_by_email[agent_email] = agent_id
        return agent_id

    def update_agent(
        self,
        agent_id: str,
        *,
        issue_types: Optional[Iterable[Any]] = None,
        ratings: Optional[Dict[Any, float]] = None,
    ) -> bool:
        agent = self._agents.get(agent_id)
        if not agent:
            return False
        if issue_types is not None:
            agent.supported_issue_types = {ProductType.from_value(issue_type) for issue_type in issue_types}
        if ratings:
            for issue_type, score in ratings.items():
                agent.ratings[ProductType.from_value(issue_type)] = float(score)
        return True

    def get_agent(self, agent_id: str) -> Optional[Agent]:
        return self._agents.get(agent_id)

    def list_agents(self) -> Dict[str, Agent]:
        return self._agents.copy()

    def view_agents_work_history(self) -> Dict[str, list[str]]:
        return {agent_id: agent.resolved_issue_ids.copy() for agent_id, agent in self._agents.items()}
