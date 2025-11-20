"""Adapter for Abu legacy engine compatibility."""
from decimal import Decimal
import logging
from typing import Any, Callable, Optional

from ...data.adapters.abu_adapter import AbuMarketAdapter
from .backtesting_engine import BacktestingEngine
from .paper_trading_engine import PaperTradingConfig, PaperTradingEngine
from .trading_engine import TradingEngine

logger = logging.getLogger(__name__)


class AbuEngineAdapter:
    """
    Adapter to provide Abu-compatible trading interface.

    Allows legacy Abu strategies to work with the new engine architecture
    through a compatible API layer.
    """

    def __init__(
        self,
        engine_type: str = "paper",  # "paper", "backtest", or "live"
        config: Optional[dict[str, Any]] = None,
    ):
        """
        Initialize Abu engine adapter.

        Args:
            engine_type: Type of engine to use
            config: Configuration dictionary
        """
        self.engine_type = engine_type
        self.config = config or {}

        # Market data adapter
        self.market_adapter = AbuMarketAdapter()

        # Engine instances
        self._trading_engine: Optional[TradingEngine] = None
        self._paper_engine: Optional[PaperTradingEngine] = None
        self._backtest_engine: Optional[BacktestingEngine] = None

        # Initialize appropriate engine
        self._initialize_engine()

        logger.info(f"Abu engine adapter initialized with {engine_type} engine")

    def _initialize_engine(self) -> None:
        """Initialize the appropriate trading engine."""
        if self.engine_type == "live":
            # Note: Would need actual data feed and database for live trading
            # trading_config = TradingConfig(
            #     max_position_size=Decimal(str(self.config.get("max_position_size", 0.1))),
            #     max_daily_loss=Decimal(str(self.config.get("max_daily_loss", 0.05))),
            #     max_open_positions=self.config.get("max_open_positions", 5),
            #     paper_trading=False,
            # )
            # self._trading_engine = TradingEngine(trading_config, data_feed, database)
            pass

        elif self.engine_type == "paper":
            paper_config = PaperTradingConfig(
                initial_balance=Decimal(str(self.config.get("initial_balance", 10000))),
                commission_maker=Decimal(str(self.config.get("commission", 0.001))),
                commission_taker=Decimal(str(self.config.get("commission", 0.001))),
                max_position_size=Decimal(str(self.config.get("max_position_size", 0.1))),
            )
            self._paper_engine = PaperTradingEngine(paper_config)

        elif self.engine_type == "backtest":
            # Note: Would need data feed for backtesting
            # backtest_config = BacktestConfig(
            #     start_date=self.config.get("start_date", datetime(2020, 1, 1)),
            #     end_date=self.config.get("end_date", datetime(2023, 12, 31)),
            #     initial_capital=Decimal(str(self.config.get("initial_balance", 10000))),
            #     commission=Decimal(str(self.config.get("commission", 0.001))),
            # )
            # self._backtest_engine = BacktestingEngine(backtest_config, data_feed)
            pass

    # Abu-compatible trading methods
    def send_order(
        self,
        symbol: str,
        quantity: int,
        price: Optional[float] = None,
        order_type: str = "market",
        **kwargs,
    ) -> Optional[str]:
        """
        Send trading order (Abu-compatible interface).

        Args:
            symbol: Trading symbol
            quantity: Order quantity (positive for buy, negative for sell)
            price: Limit price (None for market order)
            order_type: Order type
            **kwargs: Additional parameters

        Returns:
            Order ID if successful, None otherwise
        """
        try:
            if quantity > 0:
                side = "buy"
                qty = Decimal(str(quantity))
            else:
                side = "sell"
                qty = Decimal(str(abs(quantity)))

            price_decimal = Decimal(str(price)) if price else None

            if self._paper_engine:
                # Create order object
                from .trading_engine import Order

                order = Order(
                    symbol=symbol,
                    side=side,
                    quantity=qty,
                    price=price_decimal,
                    order_type=order_type,
                    **kwargs,
                )

                # Execute in paper trading
                import asyncio

                result = asyncio.run(self._paper_engine.execute_order(order))
                return order.id if result else None

            elif self._backtest_engine:
                # Execute in backtest
                if side == "buy":
                    return str(self._backtest_engine.buy(symbol, qty, price_decimal))
                else:
                    return str(self._backtest_engine.sell(symbol, qty, price_decimal))

            elif self._trading_engine:
                # Execute in live trading
                import asyncio

                return asyncio.run(
                    self._trading_engine.place_order(symbol, side, qty, price_decimal, **kwargs)
                )

        except Exception as e:
            logger.error(f"Error sending order: {e}")
            return None

        return None

    def cancel_order(self, order_id: str) -> bool:
        """
        Cancel pending order.

        Args:
            order_id: Order ID to cancel

        Returns:
            True if cancelled, False otherwise
        """
        try:
            if self._trading_engine:
                import asyncio

                return asyncio.run(self._trading_engine.cancel_order(order_id))
            elif self._paper_engine:
                # Paper engine doesn't support order cancellation yet
                return False
        except Exception as e:
            logger.error(f"Error cancelling order {order_id}: {e}")
            return False

        return False

    def get_positions(self) -> dict[str, dict[str, Any]]:
        """
        Get current positions (Abu-compatible format).

        Returns:
            Dictionary of positions
        """
        positions: dict[str, dict[str, Any]] = {}

        try:
            if self._paper_engine:
                paper_positions = self._paper_engine.get_positions()
                for symbol, position in paper_positions.items():
                    positions[symbol] = {
                        "symbol": position.symbol,
                        "quantity": float(position.quantity),
                        "avg_price": float(position.entry_price),
                        "current_price": float(position.current_price),
                        "market_value": float(position.market_value),
                        "unrealized_pnl": float(position.unrealized_pnl),
                        "side": position.side,
                    }

            elif self._backtest_engine:
                backtest_positions = self._backtest_engine.get_positions()
                for symbol, position in backtest_positions.items():  # type: ignore[assignment]
                    positions[symbol] = {
                        "symbol": symbol,
                        "quantity": float(position["quantity"]),  # type: ignore[index]
                        "avg_price": float(position["avg_price"]),  # type: ignore[index]
                        "unrealized_pnl": float(position["unrealized_pnl"]),  # type: ignore[index]
                    }

            elif self._trading_engine:
                trading_positions = self._trading_engine.get_positions()
                for symbol, position in trading_positions.items():
                    positions[symbol] = {
                        "symbol": position.symbol,
                        "quantity": float(position.quantity),
                        "avg_price": float(position.entry_price),
                        "current_price": float(position.current_price),
                        "market_value": float(position.market_value),
                        "unrealized_pnl": float(position.unrealized_pnl),
                        "side": position.side,
                    }

        except Exception as e:
            logger.error(f"Error getting positions: {e}")

        return positions

    def get_balance(self) -> dict[str, float]:
        """
        Get account balance information.

        Returns:
            Dictionary with balance information
        """
        try:
            if self._paper_engine:
                return {
                    "total": float(self._paper_engine.get_portfolio_value()),
                    "available": float(self._paper_engine.get_available_balance()),
                    "unrealized_pnl": float(self._paper_engine.get_unrealized_pnl()),
                    "realized_pnl": float(self._paper_engine.get_total_pnl()),
                }

            elif self._backtest_engine:
                return {
                    "total": float(self._backtest_engine.get_portfolio_value()),
                    "available": float(self._backtest_engine.get_cash()),
                    "unrealized_pnl": 0.0,  # Backtest engine tracks differently
                    "realized_pnl": 0.0,
                }

            elif self._trading_engine:
                portfolio_value = self._trading_engine.get_portfolio_value()
                pnl = self._trading_engine.get_pnl()
                return {
                    "total": float(portfolio_value),
                    "available": float(portfolio_value - pnl),  # Approximation
                    "unrealized_pnl": float(pnl),
                    "realized_pnl": 0.0,  # Trading engine doesn't track separately
                }

        except Exception as e:
            logger.error(f"Error getting balance: {e}")

        return {"total": 0.0, "available": 0.0, "unrealized_pnl": 0.0, "realized_pnl": 0.0}

    def get_current_price(self, symbol: str) -> Optional[float]:
        """
        Get current price for symbol.

        Args:
            symbol: Trading symbol

        Returns:
            Current price or None
        """
        return self.market_adapter.get_current_price(symbol, market="crypto")  # type: ignore[no-any-return]

    def get_historical_data(
        self, symbol: str, start_date: str, end_date: str, frequency: str = "1d"
    ) -> Optional[dict[str, Any]]:
        """
        Get historical data for symbol.

        Args:
            symbol: Trading symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            frequency: Data frequency

        Returns:
            Historical data dictionary or None
        """
        return self.market_adapter.get_market_data(  # type: ignore[no-any-return]
            symbol=symbol, market="crypto", timeframe=frequency
        )

    # Strategy integration methods
    def register_strategy(self, strategy_func: Callable[..., None]) -> None:
        """
        Register strategy function for execution.

        Args:
            strategy_func: Strategy function to execute
        """
        # Store strategy for execution
        self._strategy_func = strategy_func

    def run_strategy(self, symbols: list[str], **kwargs) -> Optional[dict[str, Any]]:
        """
        Run registered strategy.

        Args:
            symbols: List of symbols to trade
            **kwargs: Strategy parameters

        Returns:
            Strategy results or None
        """
        try:
            if not hasattr(self, "_strategy_func"):
                logger.error("No strategy registered")
                return None

            if self._backtest_engine:
                # Run backtest
                import asyncio

                result = asyncio.run(
                    self._backtest_engine.run_backtest(self._strategy_func, symbols)
                )

                return {
                    "total_return": float(result.total_return),
                    "annualized_return": float(result.annualized_return),
                    "sharpe_ratio": float(result.sharpe_ratio),
                    "max_drawdown": float(result.max_drawdown),
                    "win_rate": float(result.win_rate),
                    "total_trades": result.total_trades,
                    "portfolio_values": [float(v) for v in result.portfolio_values],
                }

            elif self._paper_engine or self._trading_engine:
                # For live/paper trading, strategy would run continuously
                # This is a simplified implementation
                logger.info("Strategy execution for live/paper trading not fully implemented")
                return None

        except Exception as e:
            logger.error(f"Error running strategy: {e}")
            return None

        return None

    # Utility methods
    def reset(self) -> None:
        """Reset engine state."""
        try:
            if self._paper_engine:
                import asyncio

                asyncio.run(self._paper_engine.reset_account())
            elif self._backtest_engine:
                # Backtest engine would need reset method
                pass
            logger.info("Engine reset completed")
        except Exception as e:
            logger.error(f"Error resetting engine: {e}")

    def get_performance_stats(self) -> dict[str, Any]:
        """
        Get performance statistics.

        Returns:
            Dictionary with performance metrics
        """
        try:
            if self._paper_engine:
                return self._paper_engine.get_performance_stats()
            elif self._backtest_engine:
                return {
                    "portfolio_value": float(self._backtest_engine.get_portfolio_value()),
                    "total_trades": len(self._backtest_engine.trades),
                }
            elif self._trading_engine:
                return {
                    "portfolio_value": float(self._trading_engine.get_portfolio_value()),
                    "open_positions": len(self._trading_engine.get_positions()),
                    "pnl": float(self._trading_engine.get_pnl()),
                }
        except Exception as e:
            logger.error(f"Error getting performance stats: {e}")

        return {}


# Convenience functions for Abu compatibility
def create_abu_engine(engine_type: str = "paper", **config) -> AbuEngineAdapter:
    """
    Create Abu-compatible trading engine.

    Args:
        engine_type: Type of engine ("paper", "backtest", "live")
        **config: Engine configuration

    Returns:
        AbuEngineAdapter instance
    """
    return AbuEngineAdapter(engine_type, config)


# Global engine instance for backward compatibility
_default_engine: Optional[AbuEngineAdapter] = None


def get_default_engine() -> AbuEngineAdapter:
    """Get default Abu engine instance."""
    global _default_engine
    if _default_engine is None:
        _default_engine = AbuEngineAdapter("paper")
    return _default_engine


def init_engine(engine_type: str = "paper", **config) -> None:
    """
    Initialize default Abu engine.

    Args:
        engine_type: Type of engine to initialize
        **config: Engine configuration
    """
    global _default_engine
    _default_engine = AbuEngineAdapter(engine_type, config)


# Export for backward compatibility
__all__ = ["AbuEngineAdapter", "create_abu_engine", "get_default_engine", "init_engine"]
