"""Strategy module for Crypto Quant Pro."""

from .base import BaseStrategy, StrategySignal, StrategyDirection
from .buy_strategies import (
    MovingAverageCrossStrategy,
    BreakoutStrategy,
    RSIStrategy,
)
from .sell_strategies import (
    StopLossStrategy,
    TakeProfitStrategy,
    TrailingStopStrategy,
)
from .strategy_registry import StrategyRegistry
from .abu_adapters import AbuBuyFactorAdapter, AbuSellFactorAdapter, register_legacy_strategies

__all__ = [
    "BaseStrategy",
    "StrategySignal",
    "StrategyDirection",
    "MovingAverageCrossStrategy",
    "BreakoutStrategy",
    "RSIStrategy",
    "StopLossStrategy",
    "TakeProfitStrategy",
    "TrailingStopStrategy",
    "StrategyRegistry",
    "AbuBuyFactorAdapter",
    "AbuSellFactorAdapter",
    "register_legacy_strategies",
]

