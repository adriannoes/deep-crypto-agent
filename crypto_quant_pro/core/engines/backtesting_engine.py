"""Backtesting engine for historical trading simulation."""
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
import logging
from typing import Any, Callable, Optional

import pandas as pd

from ...data import DatabaseManager, DataCleaner, MarketDataFeed, Timeframe
from .event_dispatcher import Event, EventDispatcher, EventType

logger = logging.getLogger(__name__)


@dataclass
class BacktestConfig:
    """Configuration for backtesting engine."""

    # Time period
    start_date: datetime
    end_date: datetime

    # Trading parameters
    initial_capital: Decimal = Decimal("10000")
    commission: Decimal = Decimal("0.001")  # 0.1% commission
    slippage: Decimal = Decimal("0.0005")  # 0.05% slippage

    # Risk management
    max_position_size: Decimal = Decimal("0.1")  # Max position as % of portfolio
    max_open_positions: int = 5

    # Performance tracking
    benchmark_symbol: Optional[str] = None  # Symbol to compare against


@dataclass
class BacktestResult:
    """Results of a backtesting run."""

    total_return: Decimal
    annualized_return: Decimal
    volatility: Decimal
    sharpe_ratio: Decimal
    max_drawdown: Decimal
    win_rate: Decimal
    total_trades: int
    profitable_trades: int

    # Equity curve
    equity_curve: pd.Series

    # Trade history
    trades: list[dict[str, Any]]

    # Performance metrics
    portfolio_values: list[Decimal]
    timestamps: list[datetime]


class BacktestingEngine:
    """
    Historical backtesting engine for trading strategies.

    Simulates trading over historical data to evaluate strategy performance.
    """

    def __init__(
        self,
        config: BacktestConfig,
        data_feed: MarketDataFeed,
        database: Optional[DatabaseManager] = None,
    ):
        """
        Initialize backtesting engine.

        Args:
            config: Backtesting configuration
            data_feed: Market data feed for historical data
            database: Optional database for caching
        """
        self.config = config
        self.data_feed = data_feed
        self.database = database

        # Backtesting state
        self.current_date = config.start_date
        self.portfolio_value = config.initial_capital
        self.cash = config.initial_capital
        self.positions: dict[str, dict[str, Any]] = {}

        # Results tracking
        self.equity_curve: list[Decimal] = [config.initial_capital]
        self.portfolio_history: list[Decimal] = [config.initial_capital]
        self.timestamps: list[datetime] = [config.start_date]
        self.trades: list[dict[str, Any]] = []

        # Market data cache
        self.market_data_cache: dict[str, pd.DataFrame] = {}

        # Event dispatcher for strategy integration
        self.event_dispatcher = EventDispatcher()

        logger.info(f"Backtesting engine initialized for {config.start_date} to {config.end_date}")

    async def run_backtest(
        self,
        strategy_func: Callable[..., None],
        symbols: list[str],
        timeframe: Timeframe = Timeframe.DAY_1,
    ) -> BacktestResult:
        """
        Run backtest with given strategy.

        Args:
            strategy_func: Strategy function to execute
            symbols: List of symbols to trade
            timeframe: Timeframe for backtesting

        Returns:
            BacktestResult with performance metrics
        """
        logger.info(f"Starting backtest for symbols: {symbols}")

        # Load historical data
        await self._load_historical_data(symbols, timeframe)

        # Initialize strategy
        await self.event_dispatcher.start()

        # Run backtest loop
        current_date = self.config.start_date
        while current_date <= self.config.end_date:
            # Update market data for current date
            await self._update_market_data(current_date, symbols)

            # Execute strategy
            try:
                strategy_func(self, current_date)
            except Exception as e:
                logger.error(f"Strategy error on {current_date}: {e}")

            # Update portfolio value
            self._update_portfolio_value(current_date)

            # Move to next period
            if timeframe == Timeframe.DAY_1:
                current_date += timedelta(days=1)
            elif timeframe == Timeframe.HOUR_1:
                current_date += timedelta(hours=1)
            elif timeframe == Timeframe.MINUTE_1:
                current_date += timedelta(minutes=1)

        # Finalize results
        await self.event_dispatcher.stop()
        result = self._calculate_results()

        logger.info(f"Backtest completed. Total return: {result.total_return:.2%}")
        return result

    async def _load_historical_data(self, symbols: list[str], timeframe: Timeframe) -> None:
        """
        Load historical data for backtesting period.

        Args:
            symbols: List of symbols to load
            timeframe: Data timeframe
        """
        for symbol in symbols:
            try:
                # Try database first
                if self.database:
                    data = self.database.get_market_data(
                        symbol=symbol,
                        start_date=self.config.start_date,
                        end_date=self.config.end_date,
                    )
                    if data is not None:
                        self.market_data_cache[symbol] = data
                        continue

                # Fallback to data feed
                data = self.data_feed.get_klines(
                    symbol=symbol,
                    timeframe=timeframe,
                    start_date=self.config.start_date,
                    end_date=self.config.end_date,
                )

                if data is not None:
                    # Clean and cache data
                    data = DataCleaner.clean_ohlcv_data(data)
                    self.market_data_cache[symbol] = data

                    # Store in database for future use
                    if self.database:
                        self.database.save_market_data(
                            symbol=symbol,
                            data=data,
                            market_type=self.data_feed.market_type,
                            source=self.data_feed.__class__.__name__,
                        )

                logger.info(f"Loaded {len(data) if data is not None else 0} records for {symbol}")

            except Exception as e:
                logger.error(f"Failed to load data for {symbol}: {e}")

    async def _update_market_data(self, date: datetime, symbols: list[str]) -> None:
        """
        Update market data for current backtest date.

        Args:
            date: Current backtest date
            symbols: Symbols to update
        """
        for symbol in symbols:
            if symbol in self.market_data_cache:
                data = self.market_data_cache[symbol]

                # Find data for current date
                if isinstance(data.index, pd.DatetimeIndex):
                    # Get data up to current date
                    current_data = data[data.index <= date]

                    if not current_data.empty:
                        latest_row = current_data.iloc[-1]

                        # Publish market data event
                        self.event_dispatcher.publish(
                            Event(
                                type=EventType.MARKET_DATA_UPDATE,
                                timestamp=date,
                                data={
                                    "symbol": symbol,
                                    "open": float(latest_row["open"]),
                                    "high": float(latest_row["high"]),
                                    "low": float(latest_row["low"]),
                                    "close": float(latest_row["close"]),
                                    "volume": float(latest_row["volume"]),
                                    "date": date.isoformat(),
                                },
                                source="backtesting_engine",
                            )
                        )

    def buy(self, symbol: str, quantity: Decimal, price: Optional[Decimal] = None) -> bool:
        """
        Execute buy order in backtest.

        Args:
            symbol: Symbol to buy
            quantity: Quantity to buy
            price: Price (None for market order)

        Returns:
            True if order executed, False otherwise
        """
        try:
            if price is None:
                # Market order - use current price
                price = self._get_current_price(symbol)
                if price is None:
                    return False

            # Apply slippage and commission
            execution_price = price * (1 + self.config.slippage)
            cost = quantity * execution_price
            commission = cost * self.config.commission

            # Check if we have enough cash
            total_cost = cost + commission
            if total_cost > self.cash:
                logger.warning(f"Insufficient cash for {symbol} buy order")
                return False

            # Execute order
            self.cash -= total_cost

            # Update position
            if symbol not in self.positions:
                self.positions[symbol] = {
                    "quantity": Decimal("0"),
                    "avg_price": Decimal("0"),
                    "unrealized_pnl": Decimal("0"),
                }

            position = self.positions[symbol]
            total_quantity = position["quantity"] + quantity
            total_cost_basis = (position["quantity"] * position["avg_price"]) + (
                quantity * execution_price
            )

            position["quantity"] = total_quantity
            position["avg_price"] = total_cost_basis / total_quantity

            # Record trade
            trade = {
                "timestamp": self.current_date,
                "symbol": symbol,
                "side": "buy",
                "quantity": quantity,
                "price": execution_price,
                "commission": commission,
                "type": "market" if price is None else "limit",
            }
            self.trades.append(trade)

            # Publish order event
            self.event_dispatcher.publish(
                Event(
                    type=EventType.ORDER_FILLED,
                    timestamp=self.current_date,
                    data=trade,
                    source="backtesting_engine",
                )
            )

            logger.debug(f"Executed buy order: {symbol} {quantity} @ {execution_price}")
            return True

        except Exception as e:
            logger.error(f"Error executing buy order: {e}")
            return False

    def sell(
        self, symbol: str, quantity: Optional[Decimal] = None, price: Optional[Decimal] = None
    ) -> bool:
        """
        Execute sell order in backtest.

        Args:
            symbol: Symbol to sell
            quantity: Quantity to sell (None for all)
            price: Price (None for market order)

        Returns:
            True if order executed, False otherwise
        """
        try:
            if symbol not in self.positions or self.positions[symbol]["quantity"] <= 0:
                logger.warning(f"No position to sell for {symbol}")
                return False

            position = self.positions[symbol]
            sell_quantity = quantity or position["quantity"]

            if sell_quantity > position["quantity"]:
                logger.warning(
                    f"Cannot sell {sell_quantity} of {symbol}, only {position['quantity']} available"
                )
                return False

            if price is None:
                # Market order - use current price
                price = self._get_current_price(symbol)
                if price is None:
                    return False

            # Apply slippage
            execution_price = price * (1 - self.config.slippage)
            proceeds = sell_quantity * execution_price
            commission = proceeds * self.config.commission

            # Execute order
            net_proceeds = proceeds - commission
            self.cash += net_proceeds

            # Update position
            remaining_quantity = position["quantity"] - sell_quantity
            if remaining_quantity <= 0:
                # Close position
                realized_pnl = (execution_price - position["avg_price"]) * position["quantity"]
                self.positions.pop(symbol)
            else:
                # Partial close
                realized_pnl = (execution_price - position["avg_price"]) * sell_quantity
                position["quantity"] = remaining_quantity

            # Record trade
            trade = {
                "timestamp": self.current_date,
                "symbol": symbol,
                "side": "sell",
                "quantity": sell_quantity,
                "price": execution_price,
                "commission": commission,
                "realized_pnl": realized_pnl,
                "type": "market" if price is None else "limit",
            }
            self.trades.append(trade)

            # Publish order event
            self.event_dispatcher.publish(
                Event(
                    type=EventType.ORDER_FILLED,
                    timestamp=self.current_date,
                    data=trade,
                    source="backtesting_engine",
                )
            )

            logger.debug(f"Executed sell order: {symbol} {sell_quantity} @ {execution_price}")
            return True

        except Exception as e:
            logger.error(f"Error executing sell order: {e}")
            return False

    def _get_current_price(self, symbol: str) -> Optional[Decimal]:
        """
        Get current price for symbol.

        Args:
            symbol: Trading symbol

        Returns:
            Current price or None if not available
        """
        try:
            if symbol in self.market_data_cache:
                data = self.market_data_cache[symbol]
                if not data.empty:
                    # Get latest data up to current date
                    current_data = data[data.index <= self.current_date]
                    if not current_data.empty:
                        return Decimal(str(current_data.iloc[-1]["close"]))
        except Exception as e:
            logger.error(f"Error getting current price for {symbol}: {e}")

        return None

    def _update_portfolio_value(self, date: datetime) -> None:
        """
        Update portfolio value for current date.

        Args:
            date: Current date
        """
        total_value = self.cash

        # Add unrealized P&L from positions
        for symbol, position in self.positions.items():
            current_price = self._get_current_price(symbol)
            if current_price:
                market_value = position["quantity"] * current_price
                total_value += market_value

                # Update unrealized P&L
                position["unrealized_pnl"] = (current_price - position["avg_price"]) * position[
                    "quantity"
                ]

        self.portfolio_value = total_value
        self.portfolio_history.append(total_value)
        self.timestamps.append(date)

    def _calculate_results(self) -> BacktestResult:
        """
        Calculate backtest performance metrics.

        Returns:
            BacktestResult with all metrics
        """
        if not self.portfolio_history:
            return BacktestResult(
                total_return=Decimal("0"),
                annualized_return=Decimal("0"),
                volatility=Decimal("0"),
                sharpe_ratio=Decimal("0"),
                max_drawdown=Decimal("0"),
                win_rate=Decimal("0"),
                total_trades=0,
                profitable_trades=0,
                equity_curve=pd.Series(),
                trades=[],
                portfolio_values=[],
                timestamps=[],
            )

        # Basic metrics
        initial_value = self.config.initial_capital
        final_value = self.portfolio_history[-1]
        total_return = (final_value - initial_value) / initial_value

        # Annualized return
        days = (self.config.end_date - self.config.start_date).days
        if days > 0:
            annualized_return = (Decimal("1") + total_return) ** (
                Decimal("365") / Decimal(str(days))
            ) - Decimal("1")
        else:
            annualized_return = Decimal("0")

        # Volatility (daily returns)
        portfolio_series = pd.Series(self.portfolio_history, index=self.timestamps)
        daily_returns = portfolio_series.pct_change().dropna()
        volatility = Decimal(str(daily_returns.std() * (252**0.5)))  # Annualized

        # Sharpe ratio
        risk_free_rate = Decimal("0.02")  # 2% annual risk-free rate
        if volatility > 0:
            sharpe_ratio = (annualized_return - risk_free_rate) / volatility
        else:
            sharpe_ratio = Decimal("0")

        # Maximum drawdown
        rolling_max = portfolio_series.expanding().max()
        drawdowns = (portfolio_series - rolling_max) / rolling_max
        max_drawdown = Decimal(str(abs(drawdowns.min())))

        # Win rate
        profitable_trades = sum(1 for trade in self.trades if trade.get("realized_pnl", 0) > 0)
        total_trades = len([t for t in self.trades if "realized_pnl" in t])
        win_rate = (
            Decimal(str(profitable_trades / total_trades)) if total_trades > 0 else Decimal("0")
        )

        return BacktestResult(
            total_return=total_return,
            annualized_return=annualized_return,
            volatility=volatility,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
            win_rate=win_rate,
            total_trades=total_trades,
            profitable_trades=profitable_trades,
            equity_curve=portfolio_series,
            trades=self.trades,
            portfolio_values=self.portfolio_history,
            timestamps=self.timestamps,
        )

    # Public interface methods
    def get_portfolio_value(self) -> Decimal:
        """Get current portfolio value."""
        return self.portfolio_value

    def get_positions(self) -> dict[str, dict[str, Any]]:
        """Get current positions."""
        return self.positions.copy()

    def get_cash(self) -> Decimal:
        """Get available cash."""
        return self.cash

    def get_current_date(self) -> datetime:
        """Get current backtest date."""
        return self.current_date

    def set_current_date(self, date: datetime) -> None:
        """Set current backtest date (for strategy testing)."""
        self.current_date = date
