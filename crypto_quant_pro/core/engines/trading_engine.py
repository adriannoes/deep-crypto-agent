"""Main trading engine for live trading execution."""
import asyncio
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
import logging
from typing import Optional

from ...data import DatabaseManager, MarketDataFeed
from .event_dispatcher import Event, EventDispatcher, EventType
from .models import Order, Position
from .paper_trading_engine import PaperTradingEngine

logger = logging.getLogger(__name__)


@dataclass
class TradingConfig:
    """Configuration for trading engine."""

    # Risk management
    max_position_size: Decimal = Decimal("0.1")  # Max position as % of portfolio
    max_daily_loss: Decimal = Decimal("0.05")  # Max daily loss as % of portfolio
    max_open_positions: int = 5

    # Trading parameters
    default_slippage: Decimal = Decimal("0.001")  # 0.1% default slippage
    min_order_size: Decimal = Decimal("10")  # Minimum order size in USD
    max_order_size: Decimal = Decimal("10000")  # Maximum order size in USD

    # Market data
    update_interval: float = 1.0  # Seconds between market data updates

    # Paper trading mode
    paper_trading: bool = True  # Start in paper trading mode by default


class TradingEngine:
    """
    Main trading engine for live trading execution.

    Coordinates between market data feeds, order execution,
    risk management, and strategy signals.
    """

    def __init__(
        self,
        config: TradingConfig,
        data_feed: MarketDataFeed,
        database: Optional[DatabaseManager] = None,
    ):
        """
        Initialize trading engine.

        Args:
            config: Trading configuration
            data_feed: Market data feed instance
            database: Optional database manager
        """
        self.config = config
        self.data_feed = data_feed
        self.database = database

        # Core components
        self.event_dispatcher = EventDispatcher()
        self.paper_engine = PaperTradingEngine() if config.paper_trading else None

        # Trading state
        self.positions: dict[str, Position] = {}
        self.orders: dict[str, Order] = {}
        self.portfolio_value = Decimal("10000")  # Starting portfolio value
        self.cash = self.portfolio_value

        # Control flags
        self.running = False
        self._market_data_task: Optional[asyncio.Task] = None
        self._risk_monitor_task: Optional[asyncio.Task] = None

        # Setup event handlers
        self._setup_event_handlers()

        logger.info("Trading engine initialized")

    def _setup_event_handlers(self) -> None:
        """Setup internal event handlers."""
        # Market data updates
        self.event_dispatcher.subscribe(
            EventType.MARKET_DATA_UPDATE, self._handle_market_data_update
        )

        # Order events
        self.event_dispatcher.subscribe(EventType.ORDER_PLACED, self._handle_order_placed)

        self.event_dispatcher.subscribe(EventType.ORDER_FILLED, self._handle_order_filled)

    async def start(self) -> None:
        """Start the trading engine."""
        if self.running:
            return

        self.running = True

        # Start event dispatcher
        await self.event_dispatcher.start()

        # Start background tasks
        self._market_data_task = asyncio.create_task(self._market_data_loop())
        self._risk_monitor_task = asyncio.create_task(self._risk_monitor_loop())

        # Publish startup event
        event = Event(
            type=EventType.ENGINE_STARTED,
            timestamp=datetime.utcnow(),
            data={"engine_type": "trading"},
            source="trading_engine",
        )
        self.event_dispatcher.publish(event)

        logger.info("Trading engine started")

    async def stop(self) -> None:
        """Stop the trading engine."""
        if not self.running:
            return

        self.running = False

        # Cancel background tasks
        if self._market_data_task:
            self._market_data_task.cancel()
        if self._risk_monitor_task:
            self._risk_monitor_task.cancel()

        # Stop event dispatcher
        await self.event_dispatcher.stop()

        # Close all positions (emergency)
        await self._close_all_positions()

        logger.info("Trading engine stopped")

    async def _market_data_loop(self) -> None:
        """Main market data update loop."""
        while self.running:
            try:
                # Get current market data for tracked symbols
                symbols = list(self.positions.keys()) + list(self.orders.keys())
                if symbols:
                    for symbol in symbols:
                        ticker_data = self.data_feed.get_ticker(symbol)
                        if ticker_data:
                            # Publish market data update
                            event = Event(
                                type=EventType.TICKER_UPDATE,
                                timestamp=datetime.utcnow(),
                                data={
                                    "symbol": symbol,
                                    "price": ticker_data.get("price"),
                                    "volume_24h": ticker_data.get("volume_24h"),
                                },
                                source="trading_engine",
                            )
                            self.event_dispatcher.publish(event)

                await asyncio.sleep(self.config.update_interval)

            except Exception as e:
                logger.error(f"Error in market data loop: {e}")
                await asyncio.sleep(1)  # Brief pause before retry

    async def _risk_monitor_loop(self) -> None:
        """Risk monitoring loop."""
        while self.running:
            try:
                await self._check_risk_limits()
                await asyncio.sleep(10)  # Check every 10 seconds

            except Exception as e:
                logger.error(f"Error in risk monitor: {e}")
                await asyncio.sleep(1)

    async def place_order(
        self, symbol: str, side: str, quantity: Decimal, price: Optional[Decimal] = None, **kwargs
    ) -> Optional[str]:
        """
        Place a trading order.

        Args:
            symbol: Trading symbol
            side: 'buy' or 'sell'
            quantity: Order quantity
            price: Limit price (None for market order)
            **kwargs: Additional order parameters

        Returns:
            Order ID if successful, None otherwise
        """
        try:
            # Validate order
            if not self._validate_order(symbol, side, quantity, price):
                return None

            # Create order
            order = Order(symbol=symbol, side=side, quantity=quantity, price=price, **kwargs)

            self.orders[order.id] = order

            # Publish order placed event
            event = Event(
                type=EventType.ORDER_PLACED,
                timestamp=datetime.utcnow(),
                data=order.to_dict(),
                source="trading_engine",
            )
            self.event_dispatcher.publish(event)

            # Execute order (paper trading or live)
            if self.config.paper_trading and self.paper_engine:
                await self.paper_engine.execute_order(order)
            else:
                await self._execute_live_order(order)

            return order.id

        except Exception as e:
            logger.error(f"Error placing order: {e}")
            return None

    def _validate_order(
        self, symbol: str, side: str, quantity: Decimal, price: Optional[Decimal]
    ) -> bool:
        """
        Validate order parameters.

        Args:
            symbol: Trading symbol
            side: Order side
            quantity: Order quantity
            price: Order price

        Returns:
            True if valid, False otherwise
        """
        # Basic validations
        if side not in ["buy", "sell"]:
            logger.error(f"Invalid order side: {side}")
            return False

        if quantity <= 0:
            logger.error(f"Invalid quantity: {quantity}")
            return False

        # Check order value (notional)
        order_value = quantity * (price or Decimal("0"))
        # If price is None (market order) and we can't easily estimate, we might skip this check
        # or require price to be passed for validation.
        # For now, if price is present, check value. If not, check quantity as fallback?
        # Better: assume min_order_size is strictly USD value.

        if price:
            if order_value < self.config.min_order_size:
                logger.error(f"Order value too small: {order_value} < {self.config.min_order_size}")
                return False

            if order_value > self.config.max_order_size:
                logger.error(f"Order value too large: {order_value} > {self.config.max_order_size}")
                return False
        else:
            # For market orders without price, we skip value check or need to fetch price
            # Just logging warning for now
            pass

        # Check position limits
        if len(self.positions) >= self.config.max_open_positions:
            logger.warning("Maximum open positions reached")
            return False

        return True

    async def cancel_order(self, order_id: str) -> bool:
        """
        Cancel a pending order.

        Args:
            order_id: Order ID to cancel

        Returns:
            True if cancelled, False otherwise
        """
        if order_id not in self.orders:
            return False

        order = self.orders[order_id]
        if order.status != "pending":
            return False

        order.status = "cancelled"

        # Publish cancellation event
        event = Event(
            type=EventType.ORDER_CANCELLED,
            timestamp=datetime.utcnow(),
            data={"order_id": order_id},
            source="trading_engine",
        )
        self.event_dispatcher.publish(event)

        return True

    async def _execute_live_order(self, order: Order) -> None:
        """
        Execute order in live trading (placeholder).

        Args:
            order: Order to execute
        """
        # This would integrate with actual broker APIs
        # For now, simulate execution
        logger.warning("Live trading execution not implemented - using simulation")

        # Simulate fill after delay
        await asyncio.sleep(0.1)
        order.status = "filled"
        order.filled_quantity = order.quantity
        order.filled_price = order.price or Decimal("100")  # Placeholder price

        # Update positions
        await self._update_positions_from_order(order)

    async def _update_positions_from_order(self, order: Order) -> None:
        """
        Update positions based on filled order.

        Args:
            order: Filled order
        """
        if order.status != "filled":
            return

        symbol = order.symbol
        quantity = order.filled_quantity if order.side == "buy" else -order.filled_quantity
        price = order.filled_price

        if symbol in self.positions:
            # Update existing position
            position = self.positions[symbol]
            total_quantity = position.quantity + quantity
            total_cost = (position.quantity * position.entry_price) + (quantity * price)

            if total_quantity == 0:
                # Position closed
                self.positions.pop(symbol)

                # Publish position closed event
                event = Event(
                    type=EventType.POSITION_CLOSED,
                    timestamp=datetime.utcnow(),
                    data={"symbol": symbol, "pnl": position.unrealized_pnl},
                    source="trading_engine",
                )
                self.event_dispatcher.publish(event)
            else:
                # Update position
                position.quantity = total_quantity
                position.entry_price = total_cost / abs(total_quantity)
                position.current_price = price
                position.market_value = abs(total_quantity) * price
                position.unrealized_pnl = (price - position.entry_price) * total_quantity

        else:
            # New position
            self.positions[symbol] = Position(
                symbol=symbol,
                quantity=quantity,
                entry_price=price,
                current_price=price,
                market_value=abs(quantity) * price,
                unrealized_pnl=Decimal("0"),
            )

            # Publish position opened event
            event = Event(
                type=EventType.POSITION_OPENED,
                timestamp=datetime.utcnow(),
                data={"symbol": symbol, "quantity": quantity, "price": price},
                source="trading_engine",
            )
            self.event_dispatcher.publish(event)

    async def _check_risk_limits(self) -> None:
        """Check and enforce risk limits."""
        # Calculate current portfolio value
        total_value = self.cash
        for position in self.positions.values():
            total_value += position.market_value

        # Check daily loss limit
        daily_pnl = total_value - self.portfolio_value
        daily_loss_pct = daily_pnl / self.portfolio_value

        if daily_loss_pct <= -self.config.max_daily_loss:
            logger.warning(f"Daily loss limit exceeded: {daily_loss_pct:.2%}")
            await self._emergency_stop()

    async def _emergency_stop(self) -> None:
        """Emergency stop - close all positions."""
        logger.warning("Emergency stop triggered - closing all positions")

        for symbol in list(self.positions.keys()):
            # Place market sell orders for all positions
            position = self.positions[symbol]
            if position.quantity > 0:
                await self.place_order(symbol, "sell", position.quantity)

    async def _close_all_positions(self) -> None:
        """Close all open positions."""
        for symbol, position in self.positions.items():
            if position.quantity > 0:
                await self.place_order(symbol, "sell", position.quantity)
            elif position.quantity < 0:
                await self.place_order(symbol, "buy", -position.quantity)

    def _handle_market_data_update(self, event: Event) -> None:
        """Handle market data update events."""
        # Update position prices
        for symbol, position in self.positions.items():
            if symbol == event.data.get("symbol"):
                new_price = Decimal(str(event.data.get("price", 0)))
                if new_price > 0:
                    position.current_price = new_price
                    position.market_value = abs(position.quantity) * new_price
                    position.unrealized_pnl = (new_price - position.entry_price) * position.quantity

    def _handle_order_placed(self, event: Event) -> None:
        """Handle order placed events."""
        logger.info(f"Order placed: {event.data}")

    def _handle_order_filled(self, event: Event) -> None:
        """Handle order filled events."""
        logger.info(f"Order filled: {event.data}")

    # Public interface methods
    def get_positions(self) -> dict[str, Position]:
        """Get current positions."""
        return self.positions.copy()

    def get_orders(self) -> dict[str, Order]:
        """Get current orders."""
        return self.orders.copy()

    def get_portfolio_value(self) -> Decimal:
        """Get current portfolio value."""
        total_value = self.cash
        for position in self.positions.values():
            total_value += position.market_value
        return total_value

    def get_pnl(self) -> Decimal:
        """Get current unrealized P&L."""
        pnl = sum(position.unrealized_pnl for position in self.positions.values())
        return Decimal(str(pnl)) if pnl != 0 else Decimal("0")
