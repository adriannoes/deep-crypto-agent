"""Adapters for compatibility with legacy ABU strategy system."""
from typing import Any, Optional

import pandas as pd

from .base import BaseStrategy, StrategySignal
from .strategy_registry import StrategyRegistry


class AbuBuyFactorAdapter:
    """
    Adapter to use new BaseStrategy as legacy AbuFactorBuyBase.

    Allows new strategies to work with legacy backtesting system.
    """

    def __init__(self, strategy: BaseStrategy, capital: Any, kl_pd: pd.DataFrame, combine_kl_pd: pd.DataFrame, benchmark: Any, **kwargs: Any):
        """
        Initialize adapter.

        Args:
            strategy: BaseStrategy instance
            capital: Legacy capital object
            kl_pd: Market data DataFrame
            combine_kl_pd: Combined market data DataFrame
            benchmark: Legacy benchmark object
            **kwargs: Additional parameters
        """
        self.strategy = strategy
        self.capital = capital
        self.kl_pd = kl_pd
        self.combine_kl_pd = combine_kl_pd
        self.benchmark = benchmark
        self.kwargs = kwargs

        # Legacy compatibility attributes
        self.factor_name = strategy.name
        self.today_ind = 0
        self.lock_factor = False
        self.skip_days = 0

    def read_fit_day(self, today: pd.Series) -> Optional[Any]:
        """
        Legacy compatibility method for day-by-day evaluation.

        Args:
            today: Current day's market data

        Returns:
            Order object or None
        """
        if self.skip_days > 0:
            self.skip_days -= 1
            return None

        self.today_ind = int(today.key) if hasattr(today, "key") else len(self.kl_pd) - 1

        # Ignore last trading day in backtest
        if self.today_ind >= self.kl_pd.shape[0] - 1:
            return None

        if self.lock_factor:
            return None

        # Call strategy's fit_day method
        signal = self.strategy.fit_day(today, self.kl_pd, symbol=self.kl_pd.name if hasattr(self.kl_pd, "name") else "UNKNOWN")

        if signal is None:
            return None

        # Convert StrategySignal to legacy AbuOrder
        return self._signal_to_order(signal, today)

    def fit_day(self, today: pd.Series) -> Optional[Any]:
        """
        Legacy compatibility method.

        Args:
            today: Current day's market data

        Returns:
            Order object or None
        """
        return self.read_fit_day(today)

    def _signal_to_order(self, signal: StrategySignal, today: pd.Series) -> Any:
        """
        Convert StrategySignal to legacy AbuOrder.

        Args:
            signal: Strategy signal
            today: Current day's data

        Returns:
            Legacy order object
        """
        # Import here to avoid circular dependency
        from abupy.TradeBu.ABuOrder import AbuOrder

        order = AbuOrder()
        order.buy_symbol = signal.symbol
        order.buy_date = self.today_ind + 1  # Next day for execution
        order.buy_factor = self.strategy.name
        order.buy_factor_class = self.strategy.__class__.__name__
        order.buy_price = float(signal.price) if signal.price else float(today.close)
        order.buy_cnt = float(signal.quantity) if signal.quantity else 0
        order.buy_type_str = self.strategy.direction.value
        order.expect_direction = float(self.strategy.get_direction_multiplier())
        order.order_deal = True

        return order

    def buy_tomorrow(self) -> Optional[Any]:
        """
        Legacy compatibility method for buying tomorrow.

        Returns:
            Order object or None
        """
        if self.today_ind >= self.kl_pd.shape[0] - 1:
            return None

        today = self.kl_pd.iloc[self.today_ind]
        signal = self.strategy.fit_day(today, self.kl_pd, symbol=self.kl_pd.name if hasattr(self.kl_pd, "name") else "UNKNOWN")

        if signal is None:
            return None

        return self._signal_to_order(signal, today)

    def buy_today(self) -> Optional[Any]:
        """
        Legacy compatibility method for buying today.

        Returns:
            Order object or None
        """
        if self.today_ind < 1:
            return None

        yesterday = self.kl_pd.iloc[self.today_ind - 1]
        signal = self.strategy.fit_day(yesterday, self.kl_pd, symbol=self.kl_pd.name if hasattr(self.kl_pd, "name") else "UNKNOWN")

        if signal is None:
            return None

        return self._signal_to_order(signal, yesterday)


class AbuSellFactorAdapter:
    """
    Adapter to use new BaseStrategy as legacy sell factor.

    Allows new sell strategies to work with legacy backtesting system.
    """

    def __init__(self, strategy: BaseStrategy, capital: Any, kl_pd: pd.DataFrame, combine_kl_pd: pd.DataFrame, benchmark: Any, **kwargs: Any):
        """
        Initialize adapter.

        Args:
            strategy: BaseStrategy instance (sell strategy)
            capital: Legacy capital object
            kl_pd: Market data DataFrame
            combine_kl_pd: Combined market data DataFrame
            benchmark: Legacy benchmark object
            **kwargs: Additional parameters
        """
        self.strategy = strategy
        self.capital = capital
        self.kl_pd = kl_pd
        self.combine_kl_pd = combine_kl_pd
        self.benchmark = benchmark
        self.kwargs = kwargs

        # Legacy compatibility attributes
        self.factor_name = strategy.name

    def fit_sell(self, order: Any, today: pd.Series) -> bool:
        """
        Legacy compatibility method for sell evaluation.

        Args:
            order: Legacy order object
            today: Current day's market data

        Returns:
            True if should sell, False otherwise
        """
        if not hasattr(order, "buy_symbol"):
            return False

        symbol = order.buy_symbol
        positions = {symbol: {"entry_price": order.buy_price, "quantity": order.buy_cnt}}

        signal = self.strategy.fit_day(
            today,
            self.kl_pd,
            symbol=symbol,
            positions=positions,
            current_date=today.date if hasattr(today, "date") else None,
        )

        return signal is not None and signal.side == "sell"


def register_legacy_strategies() -> None:
    """Register strategies with legacy ABU system compatibility."""
    from .buy_strategies import BreakoutStrategy, MovingAverageCrossStrategy, RSIStrategy
    from .sell_strategies import StopLossStrategy, TakeProfitStrategy, TrailingStopStrategy

    # Register buy strategies
    StrategyRegistry.register("MA_Cross", MovingAverageCrossStrategy)
    StrategyRegistry.register("Breakout", BreakoutStrategy)
    StrategyRegistry.register("RSI", RSIStrategy)

    # Register sell strategies
    StrategyRegistry.register("StopLoss", StopLossStrategy)
    StrategyRegistry.register("TakeProfit", TakeProfitStrategy)
    StrategyRegistry.register("TrailingStop", TrailingStopStrategy)

