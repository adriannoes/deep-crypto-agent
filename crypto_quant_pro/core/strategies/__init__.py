"""Strategy module for Crypto Quant Pro."""

from .abu_adapters import AbuBuyFactorAdapter, AbuSellFactorAdapter, register_legacy_strategies
from .base import BaseStrategy, StrategyDirection, StrategySignal
from .buy_strategies import (
    BreakoutStrategy,
    MovingAverageCrossStrategy,
    RSIStrategy,
)
from .sell_strategies import (
    StopLossStrategy,
    TakeProfitStrategy,
    TrailingStopStrategy,
)
from .strategy_registry import StrategyRegistry

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

