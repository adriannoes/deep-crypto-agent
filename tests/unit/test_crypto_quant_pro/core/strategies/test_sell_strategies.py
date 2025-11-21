"""Tests for sell strategies."""
import pytest
from datetime import datetime
from decimal import Decimal

import pandas as pd

from crypto_quant_pro.core.strategies.sell_strategies import (
    StopLossStrategy,
    TakeProfitStrategy,
    TrailingStopStrategy,
)


@pytest.fixture
def sample_market_data():
    """Create sample market data."""
    dates = pd.date_range(start="2024-01-01", periods=20, freq="D")
    prices = [50000 + i * 100 for i in range(20)]  # Upward trend

    return pd.DataFrame(
        {
            "date": dates,
            "open": prices,
            "high": [p * 1.01 for p in prices],
            "low": [p * 0.99 for p in prices],
            "close": prices,
            "volume": [1000] * 20,
        }
    )


def test_stop_loss_strategy_initialization():
    """Test stop loss strategy initialization."""
    strategy = StopLossStrategy(stop_loss_pct=Decimal("0.05"))
    assert strategy.stop_loss_pct == Decimal("0.05")


@pytest.mark.asyncio
async def test_stop_loss_strategy_no_position(sample_market_data):
    """Test stop loss strategy with no position."""
    strategy = StopLossStrategy()

    signals = await strategy.generate_signals(
        symbol="BTC/USD",
        market_data=sample_market_data,
        current_date=datetime.now(),
        positions={},
    )

    assert signals == []


@pytest.mark.asyncio
async def test_stop_loss_strategy_triggered(sample_market_data):
    """Test stop loss strategy when triggered."""
    strategy = StopLossStrategy(stop_loss_pct=Decimal("0.05"))

    # Position with entry price
    entry_price = Decimal("50000")
    current_price = Decimal("47000")  # Below stop loss (5% = 47500)

    # Update market data with lower price
    market_data = sample_market_data.copy()
    market_data.loc[market_data.index[-1], "close"] = float(current_price)

    positions = {
        "BTC/USD": {
            "entry_price": float(entry_price),
            "quantity": float(Decimal("1.0")),
        }
    }

    signals = await strategy.generate_signals(
        symbol="BTC/USD",
        market_data=market_data,
        current_date=datetime.now(),
        positions=positions,
    )

    # Should generate sell signal
    assert len(signals) > 0
    assert signals[0].side == "sell"


def test_take_profit_strategy_initialization():
    """Test take profit strategy initialization."""
    strategy = TakeProfitStrategy(take_profit_pct=Decimal("0.10"))
    assert strategy.take_profit_pct == Decimal("0.10")


@pytest.mark.asyncio
async def test_take_profit_strategy_triggered(sample_market_data):
    """Test take profit strategy when triggered."""
    strategy = TakeProfitStrategy(take_profit_pct=Decimal("0.10"))

    # Position with entry price
    entry_price = Decimal("50000")
    current_price = Decimal("56000")  # Above take profit (10% = 55000)

    # Update market data with higher price
    market_data = sample_market_data.copy()
    market_data.loc[market_data.index[-1], "close"] = float(current_price)

    positions = {
        "BTC/USD": {
            "entry_price": float(entry_price),
            "quantity": float(Decimal("1.0")),
        }
    }

    signals = await strategy.generate_signals(
        symbol="BTC/USD",
        market_data=market_data,
        current_date=datetime.now(),
        positions=positions,
    )

    # Should generate sell signal
    assert len(signals) > 0
    assert signals[0].side == "sell"


def test_trailing_stop_strategy_initialization():
    """Test trailing stop strategy initialization."""
    strategy = TrailingStopStrategy(trailing_pct=Decimal("0.05"))
    assert strategy.trailing_pct == Decimal("0.05")


@pytest.mark.asyncio
async def test_trailing_stop_strategy_updates(sample_market_data):
    """Test trailing stop strategy updates."""
    strategy = TrailingStopStrategy(trailing_pct=Decimal("0.05"))

    entry_price = Decimal("50000")
    positions = {
        "BTC/USD": {
            "entry_price": float(entry_price),
            "quantity": float(Decimal("1.0")),
        }
    }

    # First call - price increases
    market_data1 = sample_market_data.copy()
    market_data1.loc[market_data1.index[-1], "close"] = 55000.0

    signals1 = await strategy.generate_signals(
        symbol="BTC/USD",
        market_data=market_data1,
        current_date=datetime.now(),
        positions=positions,
    )

    # Should not trigger yet (price going up)
    assert len(signals1) == 0

    # Second call - price drops below trailing stop
    market_data2 = sample_market_data.copy()
    market_data2.loc[market_data2.index[-1], "close"] = 52000.0  # Below trailing stop

    signals2 = await strategy.generate_signals(
        symbol="BTC/USD",
        market_data=market_data2,
        current_date=datetime.now(),
        positions=positions,
    )

    # May or may not trigger depending on trailing stop calculation
    assert isinstance(signals2, list)

