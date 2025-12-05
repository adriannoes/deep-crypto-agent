"""Core module for Crypto Quant Pro."""

from .engines import (
    BacktestingEngine,
    EventDispatcher,
    PaperTradingEngine,
    TradingEngine,
)
from .engines.abu_engine_adapter import AbuEngineAdapter
from .strategies import (
    BaseStrategy,
    StrategySignal,
    StrategyDirection,
    StrategyRegistry,
    MovingAverageCrossStrategy,
    BreakoutStrategy,
    RSIStrategy,
    StopLossStrategy,
    TakeProfitStrategy,
    TrailingStopStrategy,
    AbuBuyFactorAdapter,
    AbuSellFactorAdapter,
    register_legacy_strategies,
)

__all__ = [
    "TradingEngine",
    "BacktestingEngine",
    "PaperTradingEngine",
    "EventDispatcher",
    "AbuEngineAdapter",
    "BaseStrategy",
    "StrategySignal",
    "StrategyDirection",
    "StrategyRegistry",
    "MovingAverageCrossStrategy",
    "BreakoutStrategy",
    "RSIStrategy",
    "StopLossStrategy",
    "TakeProfitStrategy",
    "TrailingStopStrategy",
    "AbuBuyFactorAdapter",
    "AbuSellFactorAdapter",
    "register_legacy_strategies",
]
