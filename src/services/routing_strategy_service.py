from collections import OrderedDict
from typing import Dict, Iterable, Optional

from src.data_models.agent import Agent
from src.data_models.issue import Issue
from src.data_models.strategy import Strategy
from src.enums import StrategyType


class RoutingStrategyService:
    def __init__(self) -> None:
        self._strategies: Dict[str, Strategy] = OrderedDict()
        self._sequence = 0
        self._active_strategy_id: Optional[str] = None

    def _next_id(self) -> str:
        self._sequence += 1
        return f"S{self._sequence}"

    def create_strategy(self, strategy_type: StrategyType) -> str:
        strategy_id = self._next_id()
        strategy = Strategy(strategy_id=strategy_id, strategy_type=strategy_type)
        self._strategies[strategy_id] = strategy
        if self._active_strategy_id is None:
            self._active_strategy_id = strategy_id
        return strategy_id

    def update_strategy(self, strategy_id: str, strategy_type: StrategyType) -> bool:
        if strategy_id not in self._strategies:
            return False
        self._strategies[strategy_id] = Strategy(strategy_id=strategy_id, strategy_type=strategy_type)
        return True

    def set_active_strategy(self, strategy_id: str) -> bool:
        if strategy_id not in self._strategies:
            return False
        self._active_strategy_id = strategy_id
        return True

    def get_active_strategy(self) -> Optional[Strategy]:
        if not self._active_strategy_id:
            return None
        return self._strategies.get(self._active_strategy_id)

    def assign_agent(self, issue: Issue, agents: Iterable[Agent]) -> Optional[str]:
        strategy = self.get_active_strategy()
        if not strategy:
            return None

        candidates = [agent for agent in agents if agent.is_available_for(issue.issue_type)]
        if not candidates:
            return None

        if strategy.strategy_type == StrategyType.RATING:
            best_agent = None
            best_score = float("-inf")
            for agent in candidates:
                score = agent.ratings.get(issue.issue_type, 0.0)
                if score > best_score:
                    best_score = score
                    best_agent = agent
            return best_agent.agent_id if best_agent else None

        return candidates[0].agent_id

    def list_strategies(self) -> Dict[str, Strategy]:
        return self._strategies.copy()
