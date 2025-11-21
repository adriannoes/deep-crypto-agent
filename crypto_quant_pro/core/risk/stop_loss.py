"""Stop loss management for risk control."""
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Optional


class StopLossType(Enum):
    """Stop loss types."""

    PERCENTAGE = "percentage"  # Percentage below entry price
    ABSOLUTE = "absolute"  # Absolute price level
    ATR = "atr"  # Based on Average True Range
    TRAILING = "trailing"  # Trailing stop loss


@dataclass
class StopLossConfig:
    """Configuration for stop loss."""

    stop_loss_type: StopLossType = StopLossType.PERCENTAGE
    stop_loss_value: Decimal = Decimal("0.05")  # 5% for percentage, absolute value for absolute
    atr_multiplier: Decimal = Decimal("2.0")  # For ATR-based stops
    trailing_percent: Decimal = Decimal("0.05")  # For trailing stops
    enable_stop_loss: bool = True


class StopLossManager:
    """
    Manages stop loss orders for positions.

    Provides stop loss calculation, monitoring, and execution.
    """

    def __init__(self, config: StopLossConfig):
        """
        Initialize stop loss manager.

        Args:
            config: Stop loss configuration
        """
        self.config = config
        self.stop_loss_levels: dict[str, Decimal] = {}

    def calculate_stop_loss(
        self,
        symbol: str,
        entry_price: Decimal,
        current_price: Decimal,
        atr: Optional[Decimal] = None,
    ) -> Decimal:
        """
        Calculate stop loss price for a position.

        Args:
            symbol: Trading symbol
            entry_price: Entry price
            current_price: Current market price
            atr: Optional ATR value for ATR-based stops

        Returns:
            Stop loss price
        """
        if not self.config.enable_stop_loss:
            return Decimal("0")

        if self.config.stop_loss_type == StopLossType.PERCENTAGE:
            stop_loss = entry_price * (Decimal("1") - self.config.stop_loss_value)
        elif self.config.stop_loss_type == StopLossType.ABSOLUTE:
            stop_loss = self.config.stop_loss_value
        elif self.config.stop_loss_type == StopLossType.ATR:
            if atr is None:
                # Fallback to percentage if ATR not available
                stop_loss = entry_price * (Decimal("1") - self.config.stop_loss_value)
            else:
                stop_loss = entry_price - (atr * self.config.atr_multiplier)
        else:  # TRAILING
            # Trailing stop: moves up but not down
            if symbol in self.stop_loss_levels:
                current_stop = self.stop_loss_levels[symbol]
                new_stop = current_price * (Decimal("1") - self.config.trailing_percent)
                stop_loss = max(current_stop, new_stop)  # Only move up
            else:
                stop_loss = current_price * (Decimal("1") - self.config.trailing_percent)

        # Store stop loss level
        self.stop_loss_levels[symbol] = stop_loss

        return stop_loss

    def check_stop_loss(self, symbol: str, current_price: Decimal) -> bool:
        """
        Check if stop loss has been triggered.

        Args:
            symbol: Trading symbol
            current_price: Current market price

        Returns:
            True if stop loss triggered, False otherwise
        """
        if symbol not in self.stop_loss_levels:
            return False

        stop_loss_level = self.stop_loss_levels[symbol]
        return current_price <= stop_loss_level

    def update_stop_loss(
        self,
        symbol: str,
        entry_price: Decimal,
        current_price: Decimal,
        atr: Optional[Decimal] = None,
    ) -> Decimal:
        """
        Update stop loss level for a position.

        Args:
            symbol: Trading symbol
            entry_price: Entry price
            current_price: Current market price
            atr: Optional ATR value

        Returns:
            Updated stop loss price
        """
        return self.calculate_stop_loss(symbol, entry_price, current_price, atr)

    def remove_stop_loss(self, symbol: str) -> None:
        """
        Remove stop loss for a position.

        Args:
            symbol: Trading symbol
        """
        self.stop_loss_levels.pop(symbol, None)

    def get_stop_loss(self, symbol: str) -> Optional[Decimal]:
        """
        Get stop loss level for a position.

        Args:
            symbol: Trading symbol

        Returns:
            Stop loss price or None
        """
        return self.stop_loss_levels.get(symbol)

    def get_all_stop_losses(self) -> dict[str, Decimal]:
        """
        Get all stop loss levels.

        Returns:
            Dictionary of stop loss levels
        """
        return self.stop_loss_levels.copy()
