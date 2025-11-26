"""Event dispatcher for trading system coordination."""
import asyncio
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import logging
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


class EventType(Enum):
    """Types of events in the trading system."""

    # Market data events
    MARKET_DATA_UPDATE = "market_data_update"
    TICKER_UPDATE = "ticker_update"
    ORDERBOOK_UPDATE = "orderbook_update"

    # Trading events
    ORDER_PLACED = "order_placed"
    ORDER_FILLED = "order_filled"
    ORDER_CANCELLED = "order_cancelled"
    ORDER_REJECTED = "order_rejected"

    # Strategy events
    SIGNAL_BUY = "signal_buy"
    SIGNAL_SELL = "signal_sell"
    STRATEGY_UPDATE = "strategy_update"

    # Portfolio events
    POSITION_OPENED = "position_opened"
    POSITION_CLOSED = "position_closed"
    POSITION_UPDATED = "position_updated"

    # Risk management events
    RISK_LIMIT_EXCEEDED = "risk_limit_exceeded"
    STOP_LOSS_TRIGGERED = "stop_loss_triggered"

    # System events
    ENGINE_STARTED = "engine_started"
    ENGINE_STOPPED = "engine_stopped"
    ERROR_OCCURRED = "error_occurred"


@dataclass
class Event:
    """Trading system event."""

    type: EventType
    timestamp: datetime
    data: dict[str, Any]
    source: str
    priority: int = 1  # 1=low, 5=high

    def __post_init__(self):
        """Set timestamp if not provided."""
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


class EventHandler:
    """Handler for trading events."""

    def __init__(self, callback: Callable[[Event], Any], priority: int = 1):
        """
        Initialize event handler.

        Args:
            callback: Function to call when event occurs
            priority: Handler priority (higher = executed first)
        """
        self.callback = callback
        self.priority = priority

    def __call__(self, event: Event) -> Any:
        """Execute handler callback."""
        try:
            return self.callback(event)
        except Exception as e:
            logger.error(f"Error in event handler: {e}")
            return None


class EventDispatcher:
    """
    Central event dispatcher for the trading system.

    Provides publish-subscribe pattern for coordinating between
    different components of the trading engine.
    """

    def __init__(self):
        """Initialize event dispatcher."""
        self._handlers: dict[EventType, list[EventHandler]] = {}
        self._async_handlers: dict[EventType, list[EventHandler]] = {}
        self._event_queue: Optional[asyncio.Queue[Event]] = None
        self._running = False
        self._task: Optional[asyncio.Task] = None

    def subscribe(
        self, event_type: EventType, callback: Callable[[Event], None], priority: int = 1
    ) -> None:
        """
        Subscribe to an event type.

        Args:
            event_type: Type of event to listen for
            callback: Function to call when event occurs
            priority: Handler priority (higher = executed first)
        """
        if event_type not in self._handlers:
            self._handlers[event_type] = []

        handler = EventHandler(callback, priority)
        self._handlers[event_type].append(handler)

        # Sort handlers by priority (highest first)
        self._handlers[event_type].sort(key=lambda h: h.priority, reverse=True)

        logger.debug(f"Subscribed handler for {event_type.value}")

    def unsubscribe(self, event_type: EventType, callback: Callable[[Event], None]) -> None:
        """
        Unsubscribe from an event type.

        Args:
            event_type: Event type to unsubscribe from
            callback: Callback function to remove
        """
        if event_type in self._handlers:
            self._handlers[event_type] = [
                h for h in self._handlers[event_type] if h.callback != callback
            ]

            if not self._handlers[event_type]:
                del self._handlers[event_type]

            logger.debug(f"Unsubscribed handler for {event_type.value}")

    async def subscribe_async(
        self, event_type: EventType, callback: Callable[[Event], None], priority: int = 1
    ) -> None:
        """
        Subscribe to an event type with async handler.

        Args:
            event_type: Type of event to listen for
            callback: Async function to call when event occurs
            priority: Handler priority
        """
        if event_type not in self._async_handlers:
            self._async_handlers[event_type] = []

        handler = EventHandler(callback, priority)
        self._async_handlers[event_type].append(handler)

        # Sort handlers by priority (highest first)
        self._async_handlers[event_type].sort(key=lambda h: h.priority, reverse=True)

        logger.debug(f"Subscribed async handler for {event_type.value}")

    def publish(self, event: Event) -> None:
        """
        Publish an event to all subscribers.

        Args:
            event: Event to publish
        """
        if self._running and self._event_queue:
            # If running async, add to queue
            try:
                self._event_queue.put_nowait(event)
            except asyncio.QueueFull:
                logger.warning("Event queue full, dropping event")
        else:
            # Synchronous processing
            self._process_event(event)

    async def publish_async(self, event: Event) -> None:
        """
        Publish an event asynchronously.

        Args:
            event: Event to publish
        """
        if self._event_queue:
            await self._event_queue.put(event)
        else:
            self._process_event(event)

    def _process_event(self, event: Event) -> None:
        """
        Process a single event by calling all handlers.

        Args:
            event: Event to process
        """
        logger.debug(f"Processing event: {event.type.value} from {event.source}")

        # Call synchronous handlers
        if event.type in self._handlers:
            for handler in self._handlers[event.type]:
                try:
                    handler(event)
                except Exception as e:
                    logger.error(f"Error in event handler for {event.type.value}: {e}")

        # Call async handlers (if any are registered)
        if event.type in self._async_handlers:
            for handler in self._async_handlers[event.type]:
                try:
                    # For now, call synchronously - could be made async later
                    handler(event)
                except Exception as e:
                    logger.error(f"Error in async event handler for {event.type.value}: {e}")

    async def start(self) -> None:
        """Start the event dispatcher."""
        if self._running:
            return

        self._event_queue = asyncio.Queue()
        self._running = True
        self._task = asyncio.create_task(self._process_events())

        # Publish startup event
        startup_event = Event(
            type=EventType.ENGINE_STARTED,
            timestamp=datetime.utcnow(),
            data={"component": "event_dispatcher"},
            source="event_dispatcher",
        )
        await self.publish_async(startup_event)

        logger.info("Event dispatcher started")

    async def stop(self) -> None:
        """Stop the event dispatcher."""
        if not self._running:
            return

        self._running = False

        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

        # Publish shutdown event
        shutdown_event = Event(
            type=EventType.ENGINE_STOPPED,
            timestamp=datetime.utcnow(),
            data={"component": "event_dispatcher"},
            source="event_dispatcher",
        )
        # Don't use queue for shutdown event
        self._process_event(shutdown_event)

        logger.info("Event dispatcher stopped")

    async def _process_events(self) -> None:
        """Main event processing loop."""
        while self._running and self._event_queue:
            try:
                # Wait for next event with timeout
                event = await asyncio.wait_for(self._event_queue.get(), timeout=1.0)
                await self._process_event_async(event)
                self._event_queue.task_done()

            except asyncio.TimeoutError:
                # No events, continue loop
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error processing events: {e}")
                continue

    async def _process_event_async(self, event: Event) -> None:
        """
        Process a single event asynchronously by calling all handlers.

        Args:
            event: Event to process
        """
        logger.debug(f"Processing event: {event.type.value} from {event.source}")

        # Call synchronous handlers
        if event.type in self._handlers:
            for handler in self._handlers[event.type]:
                handler(event)

        # Call async handlers
        if event.type in self._async_handlers:
            for handler in self._async_handlers[event.type]:
                try:
                    result = handler(event)
                    if asyncio.iscoroutine(result):
                        await result
                except Exception as e:
                    logger.error(f"Error in async event handler for {event.type.value}: {e}")

    def get_subscriber_count(self, event_type: Optional[EventType] = None) -> int:
        """
        Get number of subscribers for an event type.

        Args:
            event_type: Event type to check, or None for total count

        Returns:
            Number of subscribers
        """
        if event_type:
            sync_count = len(self._handlers.get(event_type, []))
            async_count = len(self._async_handlers.get(event_type, []))
            return sync_count + async_count

        total = sum(len(handlers) for handlers in self._handlers.values())
        total += sum(len(handlers) for handlers in self._async_handlers.values())
        return total

    def clear_all_handlers(self) -> None:
        """Remove all event handlers."""
        self._handlers.clear()
        self._async_handlers.clear()
        logger.info("Cleared all event handlers")

    # Convenience methods for common events
    def on_market_data_update(self, callback: Callable[[Event], None]) -> None:
        """Subscribe to market data updates."""
        self.subscribe(EventType.MARKET_DATA_UPDATE, callback)

    def on_order_filled(self, callback: Callable[[Event], None]) -> None:
        """Subscribe to order filled events."""
        self.subscribe(EventType.ORDER_FILLED, callback)

    def on_position_opened(self, callback: Callable[[Event], None]) -> None:
        """Subscribe to position opened events."""
        self.subscribe(EventType.POSITION_OPENED, callback)

    def publish_error(self, error: Exception, source: str) -> None:
        """Publish an error event."""
        error_event = Event(
            type=EventType.ERROR_OCCURRED,
            timestamp=datetime.utcnow(),
            data={
                "error_type": type(error).__name__,
                "error_message": str(error),
                "traceback": str(error.__traceback__) if hasattr(error, "__traceback__") else None,
            },
            source=source,
            priority=5,  # High priority
        )
        self.publish(error_event)
