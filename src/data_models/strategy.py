from dataclasses import dataclass

from src.enums import StrategyType


@dataclass
class Strategy:
    strategy_id: str
    strategy_type: StrategyType
