"""Tests for strategy registry."""
import pytest

from crypto_quant_pro.core.strategies.base import BaseStrategy, StrategyDirection
from crypto_quant_pro.core.strategies.strategy_registry import StrategyRegistry
from crypto_quant_pro.core.strategies.buy_strategies import MovingAverageCrossStrategy


class MockStrategyForRegistry(BaseStrategy):
    """Mock strategy for registry tests."""

    async def generate_signals(self, symbol, market_data, current_date, positions, **kwargs):
        """Generate test signals."""
        return []

    def fit_day(self, today, market_data, **kwargs):
        """Fit day implementation."""
        return None


def test_strategy_registry_register():
    """Test strategy registration."""
    StrategyRegistry.clear()

    @StrategyRegistry.register()
    class MyStrategy(BaseStrategy):
        async def generate_signals(self, symbol, market_data, current_date, positions, **kwargs):
            return []

        def fit_day(self, today, market_data, **kwargs):
            return None

    assert "MyStrategy" in StrategyRegistry.list_all()


def test_strategy_registry_register_with_name():
    """Test strategy registration with custom name."""
    StrategyRegistry.clear()

    StrategyRegistry.register("custom_name", MockStrategyForRegistry)
    assert "custom_name" in StrategyRegistry.list_all()


def test_strategy_registry_get():
    """Test getting strategy from registry."""
    StrategyRegistry.clear()
    StrategyRegistry.register("test", MockStrategyForRegistry)

    strategy = StrategyRegistry.get("test", fast_period=10)
    assert isinstance(strategy, MockStrategyForRegistry)
    assert strategy.name == "test"


def test_strategy_registry_get_not_found():
    """Test getting non-existent strategy."""
    StrategyRegistry.clear()

    with pytest.raises(KeyError):
        StrategyRegistry.get("nonexistent")


def test_strategy_registry_list_all():
    """Test listing all strategies."""
    StrategyRegistry.clear()

    StrategyRegistry.register("strategy1", MockStrategyForRegistry)
    StrategyRegistry.register("strategy2", MovingAverageCrossStrategy)

    strategies = StrategyRegistry.list_all()
    assert "strategy1" in strategies
    assert "strategy2" in strategies


def test_strategy_registry_unregister():
    """Test unregistering strategy."""
    StrategyRegistry.clear()

    StrategyRegistry.register("test", MockStrategyForRegistry)
    assert "test" in StrategyRegistry.list_all()

    StrategyRegistry.unregister("test")
    assert "test" not in StrategyRegistry.list_all()


def test_strategy_registry_clear():
    """Test clearing registry."""
    StrategyRegistry.clear()

    StrategyRegistry.register("test1", MockStrategyForRegistry)
    StrategyRegistry.register("test2", MockStrategyForRegistry)

    assert len(StrategyRegistry.list_all()) == 2

    StrategyRegistry.clear()
    assert len(StrategyRegistry.list_all()) == 0


def test_strategy_registry_exists():
    """Test checking if strategy exists."""
    StrategyRegistry.clear()

    StrategyRegistry.register("test", MockStrategyForRegistry)
    assert StrategyRegistry.exists("test") is True
    assert StrategyRegistry.exists("nonexistent") is False

