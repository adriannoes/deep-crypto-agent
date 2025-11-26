"""Tests for PaperTradingEngine."""
from datetime import datetime
from decimal import Decimal

import pytest

from crypto_quant_pro.core.engines.event_dispatcher import Event, EventType
from crypto_quant_pro.core.engines.models import Order
from crypto_quant_pro.core.engines.paper_trading_engine import (
    PaperTradingConfig,
    PaperTradingEngine,
)


@pytest.mark.asyncio
async def test_paper_trading_initialization():
    """Test paper trading engine initialization."""
    config = PaperTradingConfig(initial_balance=Decimal("5000"))
    engine = PaperTradingEngine(config)

    assert engine.get_balance() == Decimal("5000")
    assert engine.get_available_balance() == Decimal("5000")
    assert len(engine.get_positions()) == 0


@pytest.mark.asyncio
async def test_paper_trading_execution():
    """Test paper trading order execution."""
    # Re-setup with enough balance
    config = PaperTradingConfig(
        initial_balance=Decimal("100000"), max_position_size=Decimal("1.0"), slippage=Decimal("0")
    )
    engine = PaperTradingEngine(config)

    # Simulate market data update so we have a price
    # Or we can use limit orders

    # Limit Buy Order
    order = Order(
        symbol="BTC/USD",
        side="buy",
        quantity=Decimal("1.0"),
        price=Decimal("50000"),
        order_type="limit",
    )

    success = await engine.execute_order(order)

    assert success
    assert order.status == "filled"
    assert engine.get_positions()["BTC/USD"].quantity == Decimal("1.0")

    # Wait, default initial is 10000. 50050 is > 10000. Should fail?
    # Let's check default config.

    # Re-setup with enough balance
    config = PaperTradingConfig(
        initial_balance=Decimal("100000"), max_position_size=Decimal("1.0"), slippage=Decimal("0")
    )
    engine = PaperTradingEngine(config)

    success = await engine.execute_order(order)
    assert success

    positions = engine.get_positions()
    assert "BTC/USD" in positions
    assert positions["BTC/USD"].quantity == Decimal("1.0")

    # Check commission
    commission = Decimal("50000") * config.commission_maker
    expected_avail = Decimal("100000") - Decimal("50000") - commission
    assert engine.get_available_balance() == expected_avail


@pytest.mark.asyncio
async def test_paper_trading_sell():
    """Test paper trading sell execution."""
    config = PaperTradingConfig(
        initial_balance=Decimal("100000"), max_position_size=Decimal("1.0"), slippage=Decimal("0")
    )
    engine = PaperTradingEngine(config)

    # Buy first
    buy_order = Order(
        symbol="ETH/USD",
        side="buy",
        quantity=Decimal("10.0"),
        price=Decimal("3000"),
        order_type="limit",
    )
    await engine.execute_order(buy_order)

    # Sell half
    sell_order = Order(
        symbol="ETH/USD",
        side="sell",
        quantity=Decimal("5.0"),
        price=Decimal("4000"),  # Profit!
        order_type="limit",
    )

    success = await engine.execute_order(sell_order)
    assert success

    positions = engine.get_positions()
    assert positions["ETH/USD"].quantity == Decimal("5.0")

    # Check PnL
    # Bought 10 @ 3000. Sold 5 @ 4000.
    # Realized PnL on 5 units: (4000 - 3000) * 5 = 5000
    # Slippage disabled in config.
    assert engine.get_total_pnl() == Decimal("5000")


@pytest.mark.asyncio
async def test_ticker_update():
    """Test handling of ticker updates."""
    config = PaperTradingConfig(
        initial_balance=Decimal("100000"), max_position_size=Decimal("1.0"), slippage=Decimal("0")
    )
    engine = PaperTradingEngine(config)

    # Open position
    order = Order(
        symbol="BTC/USD",
        side="buy",
        quantity=Decimal("1.0"),
        price=Decimal("50000"),
        order_type="limit",
    )
    # Need enough balance
    engine.balance = Decimal("100000")
    engine.available_balance = Decimal("100000")

    await engine.execute_order(order)

    # Publish ticker update
    event = Event(
        type=EventType.TICKER_UPDATE,
        timestamp=datetime.utcnow(),
        data={"symbol": "BTC/USD", "price": 55000},
        source="test",
    )

    # We need to manually trigger the handler or use dispatcher publish if connected
    # The engine subscribes to its own dispatcher.
    # We can call the handler directly for unit testing private method logic
    engine._handle_ticker_update(event)

    position = engine.get_positions()["BTC/USD"]
    # Buy 1 @ 50000. No slippage.
    # Current price 55000.
    # Unrealized PnL = (55000 - 50000) * 1 = 5000.
    assert position.current_price == Decimal("55000")
    assert position.unrealized_pnl == Decimal("5000")
    assert engine.get_unrealized_pnl() == Decimal("5000")
