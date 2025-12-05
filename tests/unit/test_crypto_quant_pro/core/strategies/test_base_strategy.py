"""Tests for base strategy classes."""
import pytest
from datetime import datetime
from decimal import Decimal

import pandas as pd

from crypto_quant_pro.core.strategies.base import BaseStrategy, StrategyDirection, StrategySignal


class MockStrategy(BaseStrategy):
    """Mock strategy implementation for testing."""

    async def generate_signals(self, symbol, market_data, current_date, positions, **kwargs):
        """Generate test signals."""
        return []

    def fit_day(self, today, market_data, **kwargs):
        """Fit day implementation."""
        return None


def test_base_strategy_initialization():
    """Test base strategy initialization."""
    strategy = MockStrategy(name="test_strategy", direction=StrategyDirection.CALL)
    assert strategy.name == "test_strategy"
    assert strategy.direction == StrategyDirection.CALL
    assert strategy.enabled is True


def test_strategy_direction_multiplier():
    """Test direction multiplier calculation."""
    call_strategy = MockStrategy(name="call", direction=StrategyDirection.CALL)
    put_strategy = MockStrategy(name="put", direction=StrategyDirection.PUT)

    assert call_strategy.get_direction_multiplier() == Decimal("1.0")
    assert put_strategy.get_direction_multiplier() == Decimal("-1.0")


def test_strategy_signal_validation():
    """Test signal validation."""
    strategy = MockStrategy(name="test")

    # Valid signal
    valid_signal = StrategySignal(
        symbol="BTC/USD",
        side="buy",
        quantity=Decimal("1.0"),
        price=Decimal("50000"),
    )
    assert strategy.validate_signal(valid_signal) is True

    # Invalid side
    invalid_signal = StrategySignal(symbol="BTC/USD", side="invalid")
    assert strategy.validate_signal(invalid_signal) is False

    # Invalid quantity
    invalid_signal2 = StrategySignal(symbol="BTC/USD", side="buy", quantity=Decimal("-1"))
    assert strategy.validate_signal(invalid_signal2) is False

    # Disabled strategy
    strategy.enabled = False
    assert strategy.validate_signal(valid_signal) is False


def test_strategy_signal_metadata():
    """Test signal metadata initialization."""
    signal = StrategySignal(symbol="BTC/USD", side="buy")
    assert signal.metadata == {}

    signal2 = StrategySignal(symbol="BTC/USD", side="buy", metadata={"key": "value"})
    assert signal2.metadata == {"key": "value"}

