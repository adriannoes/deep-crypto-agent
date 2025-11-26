"""Tests for EventDispatcher."""
import asyncio
from datetime import datetime

import pytest

from crypto_quant_pro.core.engines.event_dispatcher import (
    Event,
    EventDispatcher,
    EventType,
)


@pytest.mark.asyncio
async def test_event_dispatcher_subscription():
    """Test event subscription and publishing."""
    dispatcher = EventDispatcher()
    received_events = []

    def handler(event: Event):
        received_events.append(event)

    # Subscribe
    dispatcher.subscribe(EventType.MARKET_DATA_UPDATE, handler)
    assert dispatcher.get_subscriber_count(EventType.MARKET_DATA_UPDATE) == 1

    # Publish event
    event = Event(
        type=EventType.MARKET_DATA_UPDATE,
        timestamp=datetime.utcnow(),
        data={"price": 100},
        source="test",
    )

    # Start dispatcher to process events (if async) but for sync handler we can just process
    # The current implementation of publish checks if running.
    # If not running, it calls _process_event directly which calls sync handlers.
    dispatcher.publish(event)

    assert len(received_events) == 1
    assert received_events[0].data["price"] == 100
    assert received_events[0].source == "test"

    # Unsubscribe
    dispatcher.unsubscribe(EventType.MARKET_DATA_UPDATE, handler)
    assert dispatcher.get_subscriber_count(EventType.MARKET_DATA_UPDATE) == 0


@pytest.mark.asyncio
async def test_event_dispatcher_async():
    """Test async event processing."""
    dispatcher = EventDispatcher()
    received_events = []

    async def async_handler(event: Event):
        received_events.append(event)

    # Subscribe async
    await dispatcher.subscribe_async(EventType.ORDER_FILLED, async_handler)
    assert dispatcher.get_subscriber_count(EventType.ORDER_FILLED) == 1

    # Start dispatcher
    await dispatcher.start()

    # Publish event
    event = Event(
        type=EventType.ORDER_FILLED,
        timestamp=datetime.utcnow(),
        data={"order_id": "123"},
        source="test",
    )

    await dispatcher.publish_async(event)

    # Wait a bit for processing
    await asyncio.sleep(0.1)

    assert len(received_events) >= 1  # Might include startup event if we subscribed to it? No.
    # Check the specific event
    found = False
    for e in received_events:
        if e.type == EventType.ORDER_FILLED and e.data.get("order_id") == "123":
            found = True
            break
    assert found

    await dispatcher.stop()


@pytest.mark.asyncio
async def test_event_priority():
    """Test event handler priority."""
    dispatcher = EventDispatcher()
    execution_order = []

    def handler_low(event):
        execution_order.append("low")

    def handler_high(event):
        execution_order.append("high")

    # Subscribe with priorities
    dispatcher.subscribe(EventType.TICKER_UPDATE, handler_low, priority=1)
    dispatcher.subscribe(EventType.TICKER_UPDATE, handler_high, priority=10)

    event = Event(type=EventType.TICKER_UPDATE, timestamp=datetime.utcnow(), data={}, source="test")

    dispatcher.publish(event)

    assert execution_order == ["high", "low"]
