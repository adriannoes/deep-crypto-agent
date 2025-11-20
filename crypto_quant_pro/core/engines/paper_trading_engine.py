"""Paper trading engine for risk-free trading simulation."""
import asyncio
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
import logging
from typing import Any, Optional

from ...data import DatabaseManager, MarketDataFeed
from .event_dispatcher import Event, EventDispatcher, EventType
from .trading_engine import Order, Position

logger = logging.getLogger(__name__)


@dataclass
class PaperTradingConfig:
    """Configuration for paper trading engine."""

    # Account settings
    initial_balance: Decimal = Decimal("10000")
    enable_margin: bool = False
    max_leverage: Decimal = Decimal("1")  # 1x for spot trading

    # Trading costs
    commission_maker: Decimal = Decimal("0.001")  # 0.1% maker fee
    commission_taker: Decimal = Decimal("0.001")  # 0.1% taker fee
    slippage: Decimal = Decimal("0.0005")  # 0.05% slippage

    # Risk management
    max_position_size: Decimal = Decimal("0.1")  # Max position as % of balance
    max_daily_loss: Decimal = Decimal("0.05")  # Max daily loss as % of balance

    # Simulation settings
    execution_delay: float = 0.1  # Seconds to simulate execution
    enable_partial_fills: bool = False


class PaperTradingEngine:
    """
    Paper trading engine for risk-free strategy testing.

    Simulates real trading with virtual money, including
    commissions, slippage, and market impact.
    """

    def __init__(
        self,
        config: Optional[PaperTradingConfig] = None,
        data_feed: Optional[MarketDataFeed] = None,
        database: Optional[DatabaseManager] = None,
    ):
        """
        Initialize paper trading engine.

        Args:
            config: Paper trading configuration
            data_feed: Market data feed for price data
            database: Optional database for persistence
        """
        self.config = config or PaperTradingConfig()
        self.data_feed = data_feed
        self.database = database

        # Account state
        self.balance = self.config.initial_balance
        self.available_balance = self.balance
        self.total_pnl = Decimal("0")
        self.unrealized_pnl = Decimal("0")

        # Trading state
        self.positions: dict[str, Position] = {}
        self.orders: dict[str, Order] = {}
        self.order_history: list[dict[str, Any]] = []

        # Daily tracking
        self.daily_start_balance = self.balance
        self.daily_pnl = Decimal("0")

        # Event dispatcher
        self.event_dispatcher = EventDispatcher()

        # Setup event handlers
        self._setup_event_handlers()

        logger.info(f"Paper trading engine initialized with ${self.balance} balance")

    def _setup_event_handlers(self) -> None:
        """Setup internal event handlers."""
        # Market data updates
        self.event_dispatcher.subscribe(EventType.TICKER_UPDATE, self._handle_ticker_update)

    async def execute_order(self, order: Order) -> bool:
        """
        Execute order in paper trading simulation.

        Args:
            order: Order to execute

        Returns:
            True if executed, False otherwise
        """
        try:
            # Validate order
            if not self._validate_order(order):
                order.status = "rejected"
                return False

            # Simulate execution delay
            await asyncio.sleep(self.config.execution_delay)

            # Get execution price
            execution_price = await self._get_execution_price(order)

            if execution_price is None:
                logger.warning(f"Could not get execution price for {order.symbol}")
                order.status = "rejected"
                return False

            # Apply commissions and fees
            commission = self._calculate_commission(order, execution_price)

            # Update order details
            order.status = "filled"
            order.filled_quantity = order.quantity
            order.filled_price = execution_price
            order.fees = commission

            # Update account and positions
            await self._update_account_from_order(order)

            # Record order
            self.order_history.append(order.to_dict())

            # Publish events
            self.event_dispatcher.publish(
                Event(
                    type=EventType.ORDER_FILLED,
                    timestamp=datetime.utcnow(),
                    data=order.to_dict(),
                    source="paper_trading_engine",
                )
            )

            logger.info(
                f"Paper order executed: {order.side} {order.quantity} {order.symbol} @ ${execution_price}"
            )
            return True

        except Exception as e:
            logger.error(f"Error executing paper order: {e}")
            order.status = "rejected"
            return False

    def _validate_order(self, order: Order) -> bool:
        """
        Validate order parameters.

        Args:
            order: Order to validate

        Returns:
            True if valid, False otherwise
        """
        # Check order size limits
        if order.quantity <= 0:
            return False

        # Check position size limits
        max_position_value = self.balance * self.config.max_position_size
        if order.price:
            order_value = order.quantity * order.price
        else:
            # Estimate with current price
            current_price = self._get_current_price_sync(order.symbol)
            if current_price:
                order_value = order.quantity * current_price
            else:
                return False

        if order_value > max_position_value:
            logger.warning(
                f"Order value ${order_value} exceeds max position size ${max_position_value}"
            )
            return False

        # Check available balance for buy orders
        if order.side == "buy":
            estimated_cost = order_value * (1 + self.config.commission_taker)
            if estimated_cost > self.available_balance:
                logger.warning(
                    f"Insufficient balance: ${self.available_balance} < ${estimated_cost}"
                )
                return False

        # Check position exists for sell orders
        elif order.side == "sell":
            if order.symbol not in self.positions:
                logger.warning(f"No position to sell for {order.symbol}")
                return False

            position = self.positions[order.symbol]
            if position.quantity < order.quantity:
                logger.warning(f"Cannot sell {order.quantity}, only {position.quantity} available")
                return False

        return True

    async def _get_execution_price(self, order: Order) -> Optional[Decimal]:
        """
        Get execution price for order.

        Args:
            order: Order to get price for

        Returns:
            Execution price or None if not available
        """
        try:
            # For limit orders, use specified price
            if order.price:
                execution_price = order.price
            else:
                # For market orders, get current market price
                current_price = await self._get_current_price(order.symbol)
                if current_price is None:
                    return None
                execution_price = current_price

            # Apply slippage
            if order.side == "buy":
                execution_price *= 1 + self.config.slippage
            else:  # sell
                execution_price *= 1 - self.config.slippage

            return execution_price

        except Exception as e:
            logger.error(f"Error getting execution price: {e}")
            return None

    async def _get_current_price(self, symbol: str) -> Optional[Decimal]:
        """
        Get current market price for symbol.

        Args:
            symbol: Trading symbol

        Returns:
            Current price or None
        """
        try:
            if self.data_feed:
                ticker_data = self.data_feed.get_ticker(symbol)
                if ticker_data and "price" in ticker_data:
                    return Decimal(str(ticker_data["price"]))

            # Fallback to database
            if self.database:
                latest_ticker = self.database.get_latest_ticker(symbol)
                if latest_ticker:
                    return Decimal(str(latest_ticker["price"]))

        except Exception as e:
            logger.error(f"Error getting current price for {symbol}: {e}")

        return None

    def _get_current_price_sync(self, symbol: str) -> Optional[Decimal]:
        """
        Synchronous version of get_current_price.

        Args:
            symbol: Trading symbol

        Returns:
            Current price or None
        """
        try:
            # Create event loop if needed
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # Cannot use asyncio.run() in running loop
                    return None
            except RuntimeError:
                pass

            # Run async function
            return asyncio.run(self._get_current_price(symbol))

        except Exception:
            return None

    def _calculate_commission(self, order: Order, execution_price: Decimal) -> Decimal:
        """
        Calculate trading commission for order.

        Args:
            order: Order being executed
            execution_price: Execution price

        Returns:
            Commission amount
        """
        order_value = order.quantity * execution_price

        # Use maker/taker fees based on order type
        if order.order_type == "limit":
            commission_rate = self.config.commission_maker
        else:
            commission_rate = self.config.commission_taker

        return order_value * commission_rate

    async def _update_account_from_order(self, order: Order) -> None:
        """
        Update account balance and positions from filled order.

        Args:
            order: Filled order
        """
        symbol = order.symbol
        quantity = order.filled_quantity
        price = order.filled_price
        commission = order.fees

        if order.side == "buy":
            # Debit account
            cost = (quantity * price) + commission
            self.available_balance -= cost

            # Update position
            if symbol not in self.positions:
                self.positions[symbol] = Position(
                    symbol=symbol,
                    quantity=Decimal("0"),
                    entry_price=Decimal("0"),
                    current_price=price,
                    market_value=Decimal("0"),
                    unrealized_pnl=Decimal("0"),
                )

            position = self.positions[symbol]
            total_quantity = position.quantity + quantity
            total_cost = (position.quantity * position.entry_price) + (quantity * price)

            position.quantity = total_quantity
            position.entry_price = total_cost / total_quantity
            position.current_price = price
            position.market_value = total_quantity * price
            position.unrealized_pnl = (price - position.entry_price) * total_quantity

        else:  # sell
            # Credit account
            proceeds = (quantity * price) - commission
            self.available_balance += proceeds

            # Update position
            if symbol in self.positions:
                position = self.positions[symbol]
                sell_quantity = quantity

                if sell_quantity >= position.quantity:
                    # Close position
                    realized_pnl = (price - position.entry_price) * position.quantity
                    self.total_pnl += realized_pnl
                    self.daily_pnl += realized_pnl

                    # Remove position
                    del self.positions[symbol]

                    # Publish position closed event
                    self.event_dispatcher.publish(
                        Event(
                            type=EventType.POSITION_CLOSED,
                            timestamp=datetime.utcnow(),
                            data={"symbol": symbol, "pnl": realized_pnl},
                            source="paper_trading_engine",
                        )
                    )
                else:
                    # Partial close
                    realized_pnl = (price - position.entry_price) * sell_quantity
                    self.total_pnl += realized_pnl
                    self.daily_pnl += realized_pnl

                    # Update position
                    position.quantity -= sell_quantity
                    position.market_value = position.quantity * price
                    position.unrealized_pnl = (price - position.entry_price) * position.quantity

    def _handle_ticker_update(self, event) -> None:
        """Handle ticker price updates."""
        symbol = event.data.get("symbol")
        price = event.data.get("price")

        if symbol and price and symbol in self.positions:
            position = self.positions[symbol]
            position.current_price = Decimal(str(price))
            position.market_value = position.quantity * position.current_price
            position.unrealized_pnl = (
                position.current_price - position.entry_price
            ) * position.quantity

            # Update total unrealized P&L
            pnl_sum = sum(p.unrealized_pnl for p in self.positions.values())
            self.unrealized_pnl = Decimal(str(pnl_sum)) if pnl_sum != 0 else Decimal("0")

    async def reset_account(self) -> None:
        """Reset account to initial state."""
        self.balance = self.config.initial_balance
        self.available_balance = self.balance
        self.total_pnl = Decimal("0")
        self.unrealized_pnl = Decimal("0")
        self.positions.clear()
        self.orders.clear()
        self.order_history.clear()
        self.daily_start_balance = self.balance
        self.daily_pnl = Decimal("0")

        logger.info("Paper trading account reset")

    def check_daily_loss_limit(self) -> bool:
        """
        Check if daily loss limit has been exceeded.

        Returns:
            True if limit exceeded, False otherwise
        """
        daily_loss_pct = -self.daily_pnl / self.daily_start_balance
        return daily_loss_pct >= self.config.max_daily_loss

    # Public interface methods
    def get_balance(self) -> Decimal:
        """Get current account balance."""
        return self.balance

    def get_available_balance(self) -> Decimal:
        """Get available balance for trading."""
        return self.available_balance

    def get_total_pnl(self) -> Decimal:
        """Get total realized P&L."""
        return self.total_pnl

    def get_unrealized_pnl(self) -> Decimal:
        """Get current unrealized P&L."""
        return self.unrealized_pnl

    def get_positions(self) -> dict[str, Position]:
        """Get current positions."""
        return self.positions.copy()

    def get_portfolio_value(self) -> Decimal:
        """Get total portfolio value."""
        total_value = self.available_balance
        for position in self.positions.values():
            total_value += position.market_value
        return total_value

    def get_order_history(self) -> list[dict[str, Any]]:
        """Get order history."""
        return self.order_history.copy()

    def get_performance_stats(self) -> dict[str, Any]:
        """
        Get performance statistics.

        Returns:
            Dictionary with performance metrics
        """
        total_trades = len(self.order_history)
        winning_trades = sum(
            1
            for order in self.order_history
            if order.get("side") == "sell" and order.get("realized_pnl", 0) > 0
        )

        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        portfolio_value = self.get_portfolio_value()
        total_return = (portfolio_value - self.config.initial_balance) / self.config.initial_balance

        return {
            "total_trades": total_trades,
            "winning_trades": winning_trades,
            "win_rate": win_rate,
            "total_return": float(total_return),
            "total_pnl": float(self.total_pnl),
            "portfolio_value": float(portfolio_value),
            "unrealized_pnl": float(self.unrealized_pnl),
            "open_positions": len(self.positions),
        }
