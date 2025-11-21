"""Buy strategies for trading signals."""
from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

import pandas as pd

from .base import BaseStrategy, StrategyDirection, StrategySignal


class MovingAverageCrossStrategy(BaseStrategy):
    """
    Moving average crossover strategy.

    Generates buy signals when fast MA crosses above slow MA.
    """

    def __init__(
        self,
        fast_period: int = 10,
        slow_period: int = 30,
        **kwargs: Any,
    ):
        """
        Initialize moving average crossover strategy.

        Args:
            fast_period: Fast moving average period
            slow_period: Slow moving average period
            **kwargs: Additional base strategy parameters
        """
        name = kwargs.pop("name", f"MA_Cross_{fast_period}_{slow_period}")
        super().__init__(name=name, direction=StrategyDirection.CALL, **kwargs)
        self.fast_period = fast_period
        self.slow_period = slow_period

    async def generate_signals(
        self,
        symbol: str,
        market_data: pd.DataFrame,
        current_date: datetime,
        positions: dict[str, Any],
        **kwargs: Any,
    ) -> list[StrategySignal]:
        """
        Generate buy signals based on MA crossover.

        Args:
            symbol: Trading symbol
            market_data: Historical OHLCV data
            current_date: Current date
            positions: Current positions
            **kwargs: Additional context

        Returns:
            List of buy signals (empty if no signal)
        """
        if len(market_data) < self.slow_period:
            return []

        # Calculate moving averages
        close_prices = market_data["close"]
        fast_ma = close_prices.rolling(window=self.fast_period).mean()
        slow_ma = close_prices.rolling(window=self.slow_period).mean()

        # Check for crossover
        if len(fast_ma) < 2 or len(slow_ma) < 2:
            return []

        current_fast = fast_ma.iloc[-1]
        previous_fast = fast_ma.iloc[-2]
        current_slow = slow_ma.iloc[-1]
        previous_slow = slow_ma.iloc[-2]

        # Buy signal: fast MA crosses above slow MA
        if previous_fast <= previous_slow and current_fast > current_slow:
            current_price = Decimal(str(close_prices.iloc[-1]))
            portfolio_value = kwargs.get("portfolio_value", Decimal("10000"))

            # Calculate position size (use 10% of portfolio)
            position_size = portfolio_value * Decimal("0.1")
            quantity = position_size / current_price

            signal = StrategySignal(
                symbol=symbol,
                side="buy",
                quantity=quantity,
                price=current_price,
                confidence=Decimal("0.7"),
                metadata={
                    "strategy": self.name,
                    "fast_ma": float(current_fast),
                    "slow_ma": float(current_slow),
                    "crossover_type": "golden_cross",
                },
            )

            if self.validate_signal(signal):
                return [signal]

        return []

    def fit_day(
        self,
        today: pd.Series,
        market_data: pd.DataFrame,
        **kwargs: Any,
    ) -> Optional[StrategySignal]:
        """
        Evaluate strategy for a specific day (legacy compatibility).

        Args:
            today: Current day's market data
            market_data: Historical market data
            **kwargs: Additional context

        Returns:
            StrategySignal if buy signal, None otherwise
        """
        import asyncio

        symbol = kwargs.get("symbol", market_data.get("symbol", "UNKNOWN"))
        current_date = kwargs.get("current_date", datetime.now())
        positions = kwargs.get("positions", {})

        # Run async method synchronously for legacy compatibility
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        signals = loop.run_until_complete(
            self.generate_signals(
                symbol=symbol,
                market_data=market_data,
                current_date=current_date,
                positions=positions,
                **kwargs,
            )
        )

        return signals[0] if signals else None


class BreakoutStrategy(BaseStrategy):
    """
    Breakout strategy based on price breaking above resistance.

    Generates buy signals when price breaks above a resistance level.
    """

    def __init__(
        self,
        lookback_period: int = 20,
        breakout_threshold: Decimal = Decimal("0.02"),  # 2% above resistance
        **kwargs: Any,
    ):
        """
        Initialize breakout strategy.

        Args:
            lookback_period: Period to calculate resistance level
            breakout_threshold: Percentage above resistance to trigger buy
            **kwargs: Additional base strategy parameters
        """
        name = kwargs.pop("name", f"Breakout_{lookback_period}")
        super().__init__(name=name, direction=StrategyDirection.CALL, **kwargs)
        self.lookback_period = lookback_period
        self.breakout_threshold = breakout_threshold

    async def generate_signals(
        self,
        symbol: str,
        market_data: pd.DataFrame,
        current_date: datetime,
        positions: dict[str, Any],
        **kwargs: Any,
    ) -> list[StrategySignal]:
        """
        Generate buy signals based on price breakout.

        Args:
            symbol: Trading symbol
            market_data: Historical OHLCV data
            current_date: Current date
            positions: Current positions
            **kwargs: Additional context

        Returns:
            List of buy signals (empty if no signal)
        """
        if len(market_data) < self.lookback_period:
            return []

        # Calculate resistance level (highest high in lookback period)
        high_prices = market_data["high"]
        resistance = high_prices.rolling(window=self.lookback_period).max().iloc[-1]

        current_price = Decimal(str(market_data["close"].iloc[-1]))
        resistance_decimal = Decimal(str(resistance))

        # Check for breakout
        breakout_level = resistance_decimal * (Decimal("1") + self.breakout_threshold)

        if current_price > breakout_level:
            portfolio_value = kwargs.get("portfolio_value", Decimal("10000"))

            # Calculate position size
            position_size = portfolio_value * Decimal("0.1")
            quantity = position_size / current_price

            signal = StrategySignal(
                symbol=symbol,
                side="buy",
                quantity=quantity,
                price=current_price,
                confidence=Decimal("0.75"),
                stop_loss=resistance_decimal * Decimal("0.95"),  # 5% below resistance
                metadata={
                    "strategy": self.name,
                    "resistance": float(resistance),
                    "breakout_level": float(breakout_level),
                },
            )

            if self.validate_signal(signal):
                return [signal]

        return []

    def fit_day(
        self,
        today: pd.Series,
        market_data: pd.DataFrame,
        **kwargs: Any,
    ) -> Optional[StrategySignal]:
        """
        Evaluate strategy for a specific day (legacy compatibility).

        Args:
            today: Current day's market data
            market_data: Historical market data
            **kwargs: Additional context

        Returns:
            StrategySignal if buy signal, None otherwise
        """
        import asyncio

        symbol = kwargs.get("symbol", market_data.get("symbol", "UNKNOWN"))
        current_date = kwargs.get("current_date", datetime.now())
        positions = kwargs.get("positions", {})

        # Run async method synchronously for legacy compatibility
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        signals = loop.run_until_complete(
            self.generate_signals(
                symbol=symbol,
                market_data=market_data,
                current_date=current_date,
                positions=positions,
                **kwargs,
            )
        )

        return signals[0] if signals else None


class RSIStrategy(BaseStrategy):
    """
    RSI (Relative Strength Index) strategy.

    Generates buy signals when RSI crosses above oversold level.
    """

    def __init__(
        self,
        period: int = 14,
        oversold_level: Decimal = Decimal("30"),
        overbought_level: Decimal = Decimal("70"),
        **kwargs: Any,
    ):
        """
        Initialize RSI strategy.

        Args:
            period: RSI calculation period
            oversold_level: RSI level considered oversold (buy signal)
            overbought_level: RSI level considered overbought (sell signal)
            **kwargs: Additional base strategy parameters
        """
        name = kwargs.pop("name", f"RSI_{period}")
        super().__init__(name=name, direction=StrategyDirection.CALL, **kwargs)
        self.period = period
        self.oversold_level = oversold_level
        self.overbought_level = overbought_level

    def _calculate_rsi(self, prices: pd.Series, period: int) -> pd.Series:
        """Calculate RSI indicator."""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    async def generate_signals(
        self,
        symbol: str,
        market_data: pd.DataFrame,
        current_date: datetime,
        positions: dict[str, Any],
        **kwargs: Any,
    ) -> list[StrategySignal]:
        """
        Generate buy signals based on RSI indicator.

        Args:
            symbol: Trading symbol
            market_data: Historical OHLCV data
            current_date: Current date
            positions: Current positions
            **kwargs: Additional context

        Returns:
            List of buy signals (empty if no signal)
        """
        if len(market_data) < self.period + 1:
            return []

        close_prices = market_data["close"]
        rsi = self._calculate_rsi(close_prices, self.period)

        if len(rsi) < 2:
            return []

        current_rsi = Decimal(str(rsi.iloc[-1]))
        previous_rsi = Decimal(str(rsi.iloc[-2]))

        # Buy signal: RSI crosses above oversold level
        if previous_rsi <= self.oversold_level and current_rsi > self.oversold_level:
            current_price = Decimal(str(close_prices.iloc[-1]))
            portfolio_value = kwargs.get("portfolio_value", Decimal("10000"))

            # Calculate position size
            position_size = portfolio_value * Decimal("0.1")
            quantity = position_size / current_price

            # Confidence based on how oversold it was
            confidence = Decimal("0.6") + (self.oversold_level - previous_rsi) / Decimal(
                "30"
            ) * Decimal("0.2")
            confidence = min(confidence, Decimal("0.9"))

            signal = StrategySignal(
                symbol=symbol,
                side="buy",
                quantity=quantity,
                price=current_price,
                confidence=confidence,
                metadata={
                    "strategy": self.name,
                    "rsi": float(current_rsi),
                    "previous_rsi": float(previous_rsi),
                },
            )

            if self.validate_signal(signal):
                return [signal]

        return []

    def fit_day(
        self,
        today: pd.Series,
        market_data: pd.DataFrame,
        **kwargs: Any,
    ) -> Optional[StrategySignal]:
        """
        Evaluate strategy for a specific day (legacy compatibility).

        Args:
            today: Current day's market data
            market_data: Historical market data
            **kwargs: Additional context

        Returns:
            StrategySignal if buy signal, None otherwise
        """
        import asyncio

        symbol = kwargs.get("symbol", market_data.get("symbol", "UNKNOWN"))
        current_date = kwargs.get("current_date", datetime.now())
        positions = kwargs.get("positions", {})

        # Run async method synchronously for legacy compatibility
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        signals = loop.run_until_complete(
            self.generate_signals(
                symbol=symbol,
                market_data=market_data,
                current_date=current_date,
                positions=positions,
                **kwargs,
            )
        )

        return signals[0] if signals else None
