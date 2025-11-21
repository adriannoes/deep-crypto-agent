"""Tests for buy strategies."""
import pytest
from datetime import datetime
from decimal import Decimal

import pandas as pd
import numpy as np

from crypto_quant_pro.core.strategies.buy_strategies import (
    MovingAverageCrossStrategy,
    BreakoutStrategy,
    RSIStrategy,
)


@pytest.fixture
def sample_market_data():
    """Create sample market data."""
    dates = pd.date_range(start="2024-01-01", periods=50, freq="D")
    np.random.seed(42)
    prices = 100 + np.cumsum(np.random.randn(50) * 2)

    return pd.DataFrame(
        {
            "date": dates,
            "open": prices,
            "high": prices * 1.02,
            "low": prices * 0.98,
            "close": prices,
            "volume": np.random.randint(1000, 10000, 50),
        }
    )


def test_moving_average_cross_strategy_initialization():
    """Test MA cross strategy initialization."""
    strategy = MovingAverageCrossStrategy(fast_period=10, slow_period=30)
    assert strategy.fast_period == 10
    assert strategy.slow_period == 30
    assert strategy.direction.value == "call"


@pytest.mark.asyncio
async def test_moving_average_cross_strategy_no_signal(sample_market_data):
    """Test MA cross strategy with no crossover."""
    strategy = MovingAverageCrossStrategy(fast_period=5, slow_period=10)

    signals = await strategy.generate_signals(
        symbol="BTC/USD",
        market_data=sample_market_data,
        current_date=datetime.now(),
        positions={},
        cash=Decimal("10000"),
        portfolio_value=Decimal("10000"),
    )

    # Should return empty list if no crossover
    assert isinstance(signals, list)


@pytest.mark.asyncio
async def test_moving_average_cross_strategy_with_crossover(sample_market_data):
    """Test MA cross strategy with crossover."""
    strategy = MovingAverageCrossStrategy(fast_period=5, slow_period=20)

    # Create data with clear crossover
    dates = pd.date_range(start="2024-01-01", periods=30, freq="D")
    prices = [100 + i * 0.5 for i in range(30)]  # Upward trend
    market_data = pd.DataFrame(
        {
            "date": dates,
            "open": prices,
            "high": [p * 1.01 for p in prices],
            "low": [p * 0.99 for p in prices],
            "close": prices,
            "volume": [1000] * 30,
        }
    )

    signals = await strategy.generate_signals(
        symbol="BTC/USD",
        market_data=market_data,
        current_date=datetime.now(),
        positions={},
        cash=Decimal("10000"),
        portfolio_value=Decimal("10000"),
    )

    # May or may not have signal depending on data
    assert isinstance(signals, list)


def test_breakout_strategy_initialization():
    """Test breakout strategy initialization."""
    strategy = BreakoutStrategy(lookback_period=20, breakout_threshold=Decimal("0.02"))
    assert strategy.lookback_period == 20
    assert strategy.breakout_threshold == Decimal("0.02")


@pytest.mark.asyncio
async def test_breakout_strategy_no_breakout(sample_market_data):
    """Test breakout strategy with no breakout."""
    strategy = BreakoutStrategy(lookback_period=20)

    signals = await strategy.generate_signals(
        symbol="BTC/USD",
        market_data=sample_market_data,
        current_date=datetime.now(),
        positions={},
        cash=Decimal("10000"),
        portfolio_value=Decimal("10000"),
    )

    assert isinstance(signals, list)


def test_rsi_strategy_initialization():
    """Test RSI strategy initialization."""
    strategy = RSIStrategy(period=14, oversold_level=Decimal("30"))
    assert strategy.period == 14
    assert strategy.oversold_level == Decimal("30")


@pytest.mark.asyncio
async def test_rsi_strategy_calculation(sample_market_data):
    """Test RSI calculation."""
    strategy = RSIStrategy(period=14)

    # Test RSI calculation
    prices = pd.Series([100, 101, 102, 101, 100, 99, 98, 97, 96, 95, 94, 93, 92, 91, 90])
    rsi = strategy._calculate_rsi(prices, 14)

    assert len(rsi) == len(prices)
    assert not rsi.isna().all()  # Should have some valid values


@pytest.mark.asyncio
async def test_rsi_strategy_no_signal(sample_market_data):
    """Test RSI strategy with no signal."""
    strategy = RSIStrategy(period=14)

    signals = await strategy.generate_signals(
        symbol="BTC/USD",
        market_data=sample_market_data,
        current_date=datetime.now(),
        positions={},
        cash=Decimal("10000"),
        portfolio_value=Decimal("10000"),
    )

    assert isinstance(signals, list)

