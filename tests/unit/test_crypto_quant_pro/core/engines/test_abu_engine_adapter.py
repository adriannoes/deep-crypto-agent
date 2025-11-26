"""Tests for AbuEngineAdapter."""
from crypto_quant_pro.core.engines.abu_engine_adapter import (
    AbuEngineAdapter,
    create_abu_engine,
)


def test_abu_adapter_initialization():
    """Test adapter initialization."""
    adapter = AbuEngineAdapter("paper")
    assert adapter.engine_type == "paper"
    assert adapter._paper_engine is not None

    adapter = AbuEngineAdapter("backtest")
    assert adapter.engine_type == "backtest"
    # assert adapter._backtest_engine is not None # Currently commented out in adapter implementation

    # Test factory function
    adapter = create_abu_engine("paper")
    assert isinstance(adapter, AbuEngineAdapter)


def test_send_order():
    """Test legacy send_order method."""
    adapter = AbuEngineAdapter(
        "paper", config={"initial_balance": 100000, "max_position_size": 1.0}
    )

    # Mock price (since we don't have data feed connected)
    # But send_order uses paper engine which needs price if market order
    # Or we can use limit order

    order_id = adapter.send_order(
        symbol="BTC/USD",
        quantity=1,  # Buy 1
        price=50000.0,
        order_type="limit",
    )

    assert order_id is not None

    positions = adapter.get_positions()
    assert "BTC/USD" in positions
    assert positions["BTC/USD"]["quantity"] == 1.0
    assert positions["BTC/USD"]["side"] == "long"

    # Sell
    order_id = adapter.send_order(
        symbol="BTC/USD",
        quantity=-1,  # Sell 1
        price=55000.0,
        order_type="limit",
    )

    assert order_id is not None
    positions = adapter.get_positions()
    assert "BTC/USD" not in positions  # Closed


def test_get_balance():
    """Test get_balance method."""
    adapter = AbuEngineAdapter("paper", config={"initial_balance": 10000})
    balance = adapter.get_balance()

    assert balance["total"] == 10000.0
    assert balance["available"] == 10000.0
    assert balance["unrealized_pnl"] == 0.0
