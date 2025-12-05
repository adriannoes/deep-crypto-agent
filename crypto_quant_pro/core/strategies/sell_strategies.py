"""Sell strategies for trading signals."""
from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

import pandas as pd

from .base import BaseStrategy, StrategyDirection, StrategySignal


class StopLossStrategy(BaseStrategy):
    """
    Stop loss strategy.

    Generates sell signals when price falls below stop loss level.
    """

    def __init__(
        self,
        stop_loss_pct: Decimal = Decimal("0.05"),  # 5% stop loss
        **kwargs: Any,
    ):
        """
        Initialize stop loss strategy.

        Args:
            stop_loss_pct: Stop loss percentage (e.g., 0.05 for 5%)
            **kwargs: Additional base strategy parameters
        """
        name = kwargs.pop("name", f"StopLoss_{stop_loss_pct}")
        super().__init__(name=name, direction=StrategyDirection.CALL, **kwargs)
        self.stop_loss_pct = stop_loss_pct

    async def generate_signals(
        self,
        symbol: str,
        market_data: pd.DataFrame,
        current_date: datetime,
        positions: dict[str, Any],
        **kwargs: Any,
    ) -> list[StrategySignal]:
        """
        Generate sell signals based on stop loss.

        Args:
            symbol: Trading symbol
            market_data: Historical OHLCV data
            current_date: Current date
            positions: Current positions
            **kwargs: Additional context

        Returns:
            List of sell signals (empty if no signal)
        """
        if symbol not in positions:
            return []

        position = positions[symbol]
        entry_price = Decimal(str(position.get("entry_price", 0)))
        quantity = Decimal(str(position.get("quantity", 0)))

        if entry_price <= 0 or quantity <= 0:
            return []

        current_price = Decimal(str(market_data["close"].iloc[-1]))
        stop_loss_price = entry_price * (Decimal("1") - self.stop_loss_pct)

        # Check if stop loss triggered
        if current_price <= stop_loss_price:
            signal = StrategySignal(
                symbol=symbol,
                side="sell",
                quantity=quantity,
                price=current_price,
                confidence=Decimal("1.0"),  # High confidence for stop loss
                metadata={
                    "strategy": self.name,
                    "entry_price": float(entry_price),
                    "stop_loss_price": float(stop_loss_price),
                    "loss_pct": float((entry_price - current_price) / entry_price),
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
            StrategySignal if sell signal, None otherwise
        """
        import asyncio

        symbol = kwargs.get("symbol", market_data.get("symbol", "UNKNOWN"))
        current_date = kwargs.get("current_date", datetime.now())
        positions = kwargs.get("positions", {})

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


class TakeProfitStrategy(BaseStrategy):
    """
    Take profit strategy.

    Generates sell signals when price reaches take profit level.
    """

    def __init__(
        self,
        take_profit_pct: Decimal = Decimal("0.10"),  # 10% take profit
        **kwargs: Any,
    ):
        """
        Initialize take profit strategy.

        Args:
            take_profit_pct: Take profit percentage (e.g., 0.10 for 10%)
            **kwargs: Additional base strategy parameters
        """
        name = kwargs.pop("name", f"TakeProfit_{take_profit_pct}")
        super().__init__(name=name, direction=StrategyDirection.CALL, **kwargs)
        self.take_profit_pct = take_profit_pct

    async def generate_signals(
        self,
        symbol: str,
        market_data: pd.DataFrame,
        current_date: datetime,
        positions: dict[str, Any],
        **kwargs: Any,
    ) -> list[StrategySignal]:
        """
        Generate sell signals based on take profit.

        Args:
            symbol: Trading symbol
            market_data: Historical OHLCV data
            current_date: Current date
            positions: Current positions
            **kwargs: Additional context

        Returns:
            List of sell signals (empty if no signal)
        """
        if symbol not in positions:
            return []

        position = positions[symbol]
        entry_price = Decimal(str(position.get("entry_price", 0)))
        quantity = Decimal(str(position.get("quantity", 0)))

        if entry_price <= 0 or quantity <= 0:
            return []

        current_price = Decimal(str(market_data["close"].iloc[-1]))
        take_profit_price = entry_price * (Decimal("1") + self.take_profit_pct)

        # Check if take profit triggered
        if current_price >= take_profit_price:
            signal = StrategySignal(
                symbol=symbol,
                side="sell",
                quantity=quantity,
                price=current_price,
                confidence=Decimal("0.9"),
                metadata={
                    "strategy": self.name,
                    "entry_price": float(entry_price),
                    "take_profit_price": float(take_profit_price),
                    "profit_pct": float((current_price - entry_price) / entry_price),
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
            StrategySignal if sell signal, None otherwise
        """
        import asyncio

        symbol = kwargs.get("symbol", market_data.get("symbol", "UNKNOWN"))
        current_date = kwargs.get("current_date", datetime.now())
        positions = kwargs.get("positions", {})

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


class TrailingStopStrategy(BaseStrategy):
    """
    Trailing stop strategy.

    Generates sell signals when price falls below trailing stop level.
    The stop level moves up as price increases but doesn't move down.
    """

    def __init__(
        self,
        trailing_pct: Decimal = Decimal("0.05"),  # 5% trailing stop
        **kwargs: Any,
    ):
        """
        Initialize trailing stop strategy.

        Args:
            trailing_pct: Trailing stop percentage (e.g., 0.05 for 5%)
            **kwargs: Additional base strategy parameters
        """
        name = kwargs.pop("name", f"TrailingStop_{trailing_pct}")
        super().__init__(name=name, direction=StrategyDirection.CALL, **kwargs)
        self.trailing_pct = trailing_pct
        self._trailing_stops: dict[str, Decimal] = {}  # Track trailing stops per symbol

    async def generate_signals(
        self,
        symbol: str,
        market_data: pd.DataFrame,
        current_date: datetime,
        positions: dict[str, Any],
        **kwargs: Any,
    ) -> list[StrategySignal]:
        """
        Generate sell signals based on trailing stop.

        Args:
            symbol: Trading symbol
            market_data: Historical OHLCV data
            current_date: Current date
            positions: Current positions
            **kwargs: Additional context

        Returns:
            List of sell signals (empty if no signal)
        """
        if symbol not in positions:
            # Clean up trailing stop if position closed
            self._trailing_stops.pop(symbol, None)
            return []

        position = positions[symbol]
        entry_price = Decimal(str(position.get("entry_price", 0)))
        quantity = Decimal(str(position.get("quantity", 0)))

        if entry_price <= 0 or quantity <= 0:
            return []

        current_price = Decimal(str(market_data["close"].iloc[-1]))

        # Initialize or update trailing stop
        if symbol not in self._trailing_stops:
            # Initialize trailing stop at entry price - trailing_pct
            self._trailing_stops[symbol] = entry_price * (Decimal("1") - self.trailing_pct)
        else:
            # Update trailing stop: move up if price increases, but don't move down
            current_trailing = self._trailing_stops[symbol]
            new_trailing = current_price * (Decimal("1") - self.trailing_pct)

            if new_trailing > current_trailing:
                # Only move trailing stop up
                self._trailing_stops[symbol] = new_trailing

        trailing_stop = self._trailing_stops[symbol]

        # Check if trailing stop triggered
        if current_price <= trailing_stop:
            signal = StrategySignal(
                symbol=symbol,
                side="sell",
                quantity=quantity,
                price=current_price,
                confidence=Decimal("0.95"),
                metadata={
                    "strategy": self.name,
                    "entry_price": float(entry_price),
                    "trailing_stop": float(trailing_stop),
                    "max_price": float(kwargs.get("max_price", current_price)),
                },
            )

            if self.validate_signal(signal):
                # Clean up trailing stop
                self._trailing_stops.pop(symbol, None)
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
            StrategySignal if sell signal, None otherwise
        """
        import asyncio

        symbol = kwargs.get("symbol", market_data.get("symbol", "UNKNOWN"))
        current_date = kwargs.get("current_date", datetime.now())
        positions = kwargs.get("positions", {})

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

