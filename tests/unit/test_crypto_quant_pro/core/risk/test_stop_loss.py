"""Tests for stop loss manager."""
from decimal import Decimal

from crypto_quant_pro.core.risk.stop_loss import StopLossConfig, StopLossManager, StopLossType


def test_stop_loss_manager_initialization():
    """Test stop loss manager initialization."""
    config = StopLossConfig(
        stop_loss_type=StopLossType.PERCENTAGE,
        stop_loss_value=Decimal("0.05"),
    )
    manager = StopLossManager(config)
    assert manager.config == config


def test_calculate_stop_loss_percentage():
    """Test stop loss calculation with percentage."""
    config = StopLossConfig(
        stop_loss_type=StopLossType.PERCENTAGE,
        stop_loss_value=Decimal("0.05"),  # 5%
    )
    manager = StopLossManager(config)

    stop_loss = manager.calculate_stop_loss(
        symbol="BTC/USD",
        entry_price=Decimal("50000"),
        current_price=Decimal("50000"),
    )

    # Should be 50000 * (1 - 0.05) = 47500
    expected = Decimal("47500")
    assert stop_loss == expected


def test_calculate_stop_loss_absolute():
    """Test stop loss calculation with absolute value."""
    config = StopLossConfig(
        stop_loss_type=StopLossType.ABSOLUTE,
        stop_loss_value=Decimal("45000"),
    )
    manager = StopLossManager(config)

    stop_loss = manager.calculate_stop_loss(
        symbol="BTC/USD",
        entry_price=Decimal("50000"),
        current_price=Decimal("50000"),
    )

    assert stop_loss == Decimal("45000")


def test_calculate_stop_loss_atr():
    """Test stop loss calculation with ATR."""
    config = StopLossConfig(
        stop_loss_type=StopLossType.ATR,
        atr_multiplier=Decimal("2.0"),
    )
    manager = StopLossManager(config)

    stop_loss = manager.calculate_stop_loss(
        symbol="BTC/USD",
        entry_price=Decimal("50000"),
        current_price=Decimal("50000"),
        atr=Decimal("1000"),
    )

    # Should be 50000 - (1000 * 2) = 48000
    expected = Decimal("48000")
    assert stop_loss == expected


def test_check_stop_loss():
    """Test stop loss check."""
    config = StopLossConfig(stop_loss_type=StopLossType.PERCENTAGE, stop_loss_value=Decimal("0.05"))
    manager = StopLossManager(config)

    # Calculate stop loss
    manager.calculate_stop_loss(
        symbol="BTC/USD",
        entry_price=Decimal("50000"),
        current_price=Decimal("50000"),
    )

    # Price above stop loss - should not trigger
    assert manager.check_stop_loss("BTC/USD", Decimal("48000")) is False

    # Price at stop loss - should trigger
    assert manager.check_stop_loss("BTC/USD", Decimal("47500")) is True

    # Price below stop loss - should trigger
    assert manager.check_stop_loss("BTC/USD", Decimal("47000")) is True


def test_remove_stop_loss():
    """Test removing stop loss."""
    config = StopLossConfig()
    manager = StopLossManager(config)

    manager.calculate_stop_loss(
        symbol="BTC/USD",
        entry_price=Decimal("50000"),
        current_price=Decimal("50000"),
    )

    assert "BTC/USD" in manager.stop_loss_levels

    manager.remove_stop_loss("BTC/USD")
    assert "BTC/USD" not in manager.stop_loss_levels
