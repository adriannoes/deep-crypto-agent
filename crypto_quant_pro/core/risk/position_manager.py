"""Position management for risk control."""
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Optional

from ..engines.models import Position


class PositionLimit(Enum):
    """Position limit types."""

    PERCENTAGE = "percentage"  # Limit as % of portfolio
    ABSOLUTE = "absolute"  # Limit as absolute value
    FIXED_UNITS = "fixed_units"  # Limit as fixed number of units


@dataclass
class PositionConfig:
    """Configuration for position management."""

    max_position_size: Decimal = Decimal("0.1")  # Max 10% per position
    max_open_positions: int = 5  # Max number of open positions
    min_position_size: Decimal = Decimal("0.01")  # Min 1% per position
    position_limit_type: PositionLimit = PositionLimit.PERCENTAGE
    allow_partial_fills: bool = True


class PositionManager:
    """
    Manages trading positions and enforces position limits.

    Provides position sizing, limit enforcement, and position tracking.
    """

    def __init__(self, config: PositionConfig):
        """
        Initialize position manager.

        Args:
            config: Position management configuration
        """
        self.config = config
        self.positions: dict[str, Position] = {}

    def calculate_position_size(
        self,
        symbol: str,
        price: Decimal,
        portfolio_value: Decimal,
        available_cash: Decimal,
        risk_amount: Optional[Decimal] = None,
    ) -> Decimal:
        """
        Calculate position size based on risk parameters.

        Args:
            symbol: Trading symbol
            price: Entry price
            portfolio_value: Total portfolio value
            available_cash: Available cash for trading
            risk_amount: Optional risk amount (for risk-based sizing)

        Returns:
            Calculated position size (quantity)
        """
        # Check if we already have a position
        if symbol in self.positions:
            existing_position = self.positions[symbol]
            # For existing positions, calculate additional size
            current_value = existing_position.market_value
        else:
            current_value = Decimal("0")

        # Calculate maximum position value based on config
        if self.config.position_limit_type == PositionLimit.PERCENTAGE:
            max_position_value = portfolio_value * self.config.max_position_size
        elif self.config.position_limit_type == PositionLimit.ABSOLUTE:
            max_position_value = self.config.max_position_size
        else:  # FIXED_UNITS
            return self.config.max_position_size

        # Use risk amount if provided
        if risk_amount is not None:
            position_value = min(risk_amount, max_position_value - current_value)
        else:
            position_value = max_position_value - current_value

        # Ensure we don't exceed available cash
        position_value = min(position_value, available_cash)

        # Calculate quantity
        if price > 0:
            quantity = position_value / price
        else:
            quantity = Decimal("0")

        # Apply minimum position size check
        min_position_value = portfolio_value * self.config.min_position_size
        min_quantity = min_position_value / price if price > 0 else Decimal("0")

        if quantity < min_quantity:
            return Decimal("0")  # Position too small

        return quantity

    def can_open_position(self, symbol: str) -> bool:
        """
        Check if a new position can be opened.

        Args:
            symbol: Trading symbol

        Returns:
            True if position can be opened, False otherwise
        """
        # Check if position already exists
        if symbol in self.positions:
            return True  # Can add to existing position

        # Check max open positions limit
        active_positions = sum(1 for p in self.positions.values() if p.quantity != 0)
        if active_positions >= self.config.max_open_positions:
            return False

        return True

    def add_position(self, symbol: str, position: Position) -> None:
        """
        Add or update a position.

        Args:
            symbol: Trading symbol
            position: Position object
        """
        self.positions[symbol] = position

    def remove_position(self, symbol: str) -> Optional[Position]:
        """
        Remove a position.

        Args:
            symbol: Trading symbol

        Returns:
            Removed position or None
        """
        return self.positions.pop(symbol, None)

    def get_position(self, symbol: str) -> Optional[Position]:
        """
        Get position for a symbol.

        Args:
            symbol: Trading symbol

        Returns:
            Position or None
        """
        return self.positions.get(symbol)

    def get_all_positions(self) -> dict[str, Position]:
        """
        Get all positions.

        Returns:
            Dictionary of all positions
        """
        return self.positions.copy()

    def get_total_position_value(self) -> Decimal:
        """
        Calculate total value of all positions.

        Returns:
            Total position value
        """
        total = sum(p.market_value for p in self.positions.values())
        return Decimal(str(total)) if total != 0 else Decimal("0")

    def get_position_count(self) -> int:
        """
        Get number of active positions.

        Returns:
            Number of positions with non-zero quantity
        """
        return sum(1 for p in self.positions.values() if p.quantity != 0)

    def validate_position_size(
        self,
        symbol: str,
        quantity: Decimal,
        price: Decimal,
        portfolio_value: Decimal,
    ) -> bool:
        """
        Validate if a position size is within limits.

        Args:
            symbol: Trading symbol
            quantity: Position quantity
            price: Entry price
            portfolio_value: Total portfolio value

        Returns:
            True if position size is valid, False otherwise
        """
        position_value = quantity * price

        if self.config.position_limit_type == PositionLimit.PERCENTAGE:
            max_value = portfolio_value * self.config.max_position_size
            min_value = portfolio_value * self.config.min_position_size

            if position_value > max_value:
                return False
            if position_value < min_value and quantity > 0:
                return False

        elif self.config.position_limit_type == PositionLimit.ABSOLUTE:
            if position_value > self.config.max_position_size:
                return False

        return True

    def update_position_price(self, symbol: str, current_price: Decimal) -> None:
        """
        Update position with current market price.

        Args:
            symbol: Trading symbol
            current_price: Current market price
        """
        if symbol in self.positions:
            position = self.positions[symbol]
            position.current_price = current_price
            position.market_value = position.quantity * current_price
            position.unrealized_pnl = (current_price - position.entry_price) * position.quantity
