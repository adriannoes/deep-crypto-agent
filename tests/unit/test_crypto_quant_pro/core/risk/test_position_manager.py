"""Tests for position manager."""
from decimal import Decimal

from crypto_quant_pro.core.engines.models import Position
from crypto_quant_pro.core.risk.position_manager import (
    PositionConfig,
    PositionLimit,
    PositionManager,
)


def test_position_manager_initialization():
    """Test position manager initialization."""
    config = PositionConfig(
        max_position_size=Decimal("0.1"),
        max_open_positions=5,
    )
    manager = PositionManager(config)
    assert manager.config == config
    assert len(manager.positions) == 0


def test_calculate_position_size_percentage():
    """Test position size calculation with percentage limit."""
    config = PositionConfig(
        max_position_size=Decimal("0.1"),  # 10%
        position_limit_type=PositionLimit.PERCENTAGE,
    )
    manager = PositionManager(config)

    quantity = manager.calculate_position_size(
        symbol="BTC/USD",
        price=Decimal("50000"),
        portfolio_value=Decimal("100000"),
        available_cash=Decimal("50000"),
    )

    # Should be 10% of portfolio = 10000 / 50000 = 0.2 BTC
    expected = Decimal("10000") / Decimal("50000")
    assert quantity == expected


def test_calculate_position_size_absolute():
    """Test position size calculation with absolute limit."""
    config = PositionConfig(
        max_position_size=Decimal("5000"),  # Absolute value
        position_limit_type=PositionLimit.ABSOLUTE,
    )
    manager = PositionManager(config)

    quantity = manager.calculate_position_size(
        symbol="BTC/USD",
        price=Decimal("50000"),
        portfolio_value=Decimal("100000"),
        available_cash=Decimal("10000"),
    )

    # Should be min(5000, 10000) / 50000 = 0.1 BTC
    expected = Decimal("5000") / Decimal("50000")
    assert quantity == expected


def test_can_open_position():
    """Test position opening checks."""
    config = PositionConfig(max_open_positions=2)
    manager = PositionManager(config)

    # Should be able to open first position
    assert manager.can_open_position("BTC/USD") is True

    # Add a position
    position = Position(
        symbol="BTC/USD",
        quantity=Decimal("1"),
        entry_price=Decimal("50000"),
        current_price=Decimal("50000"),
        market_value=Decimal("50000"),
        unrealized_pnl=Decimal("0"),
    )
    manager.add_position("BTC/USD", position)

    # Should still be able to open (existing position)
    assert manager.can_open_position("BTC/USD") is True

    # Add another position
    position2 = Position(
        symbol="ETH/USD",
        quantity=Decimal("10"),
        entry_price=Decimal("3000"),
        current_price=Decimal("3000"),
        market_value=Decimal("30000"),
        unrealized_pnl=Decimal("0"),
    )
    manager.add_position("ETH/USD", position2)

    # Should not be able to open new position (max reached)
    assert manager.can_open_position("LTC/USD") is False


def test_add_and_remove_position():
    """Test adding and removing positions."""
    config = PositionConfig()
    manager = PositionManager(config)

    position = Position(
        symbol="BTC/USD",
        quantity=Decimal("1"),
        entry_price=Decimal("50000"),
        current_price=Decimal("50000"),
        market_value=Decimal("50000"),
        unrealized_pnl=Decimal("0"),
    )

    manager.add_position("BTC/USD", position)
    assert "BTC/USD" in manager.positions

    removed = manager.remove_position("BTC/USD")
    assert removed == position
    assert "BTC/USD" not in manager.positions


def test_get_total_position_value():
    """Test total position value calculation."""
    config = PositionConfig()
    manager = PositionManager(config)

    position1 = Position(
        symbol="BTC/USD",
        quantity=Decimal("1"),
        entry_price=Decimal("50000"),
        current_price=Decimal("50000"),
        market_value=Decimal("50000"),
        unrealized_pnl=Decimal("0"),
    )

    position2 = Position(
        symbol="ETH/USD",
        quantity=Decimal("10"),
        entry_price=Decimal("3000"),
        current_price=Decimal("3000"),
        market_value=Decimal("30000"),
        unrealized_pnl=Decimal("0"),
    )

    manager.add_position("BTC/USD", position1)
    manager.add_position("ETH/USD", position2)

    total_value = manager.get_total_position_value()
    assert total_value == Decimal("80000")


def test_validate_position_size():
    """Test position size validation."""
    config = PositionConfig(
        max_position_size=Decimal("0.1"),  # 10%
        min_position_size=Decimal("0.01"),  # 1%
        position_limit_type=PositionLimit.PERCENTAGE,
    )
    manager = PositionManager(config)

    # Valid position (5% of portfolio)
    assert (
        manager.validate_position_size(
            symbol="BTC/USD",
            quantity=Decimal("1"),
            price=Decimal("5000"),
            portfolio_value=Decimal("100000"),
        )
        is True
    )

    # Invalid position (too large - 20% of portfolio)
    assert (
        manager.validate_position_size(
            symbol="BTC/USD",
            quantity=Decimal("4"),
            price=Decimal("5000"),
            portfolio_value=Decimal("100000"),
        )
        is False
    )


def test_update_position_price():
    """Test updating position price."""
    config = PositionConfig()
    manager = PositionManager(config)

    position = Position(
        symbol="BTC/USD",
        quantity=Decimal("1"),
        entry_price=Decimal("50000"),
        current_price=Decimal("50000"),
        market_value=Decimal("50000"),
        unrealized_pnl=Decimal("0"),
    )

    manager.add_position("BTC/USD", position)
    manager.update_position_price("BTC/USD", Decimal("55000"))

    updated_position = manager.get_position("BTC/USD")
    assert updated_position.current_price == Decimal("55000")
    assert updated_position.market_value == Decimal("55000")
    assert updated_position.unrealized_pnl == Decimal("5000")
