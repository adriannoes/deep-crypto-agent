"""Data models for trading engines."""
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any, Optional


class Order:
    """Trading order representation."""

    def __init__(
        self,
        symbol: str,
        side: str,  # 'buy' or 'sell'
        quantity: Decimal,
        price: Optional[Decimal] = None,  # Market order if None
        order_type: str = "market",
        stop_loss: Optional[Decimal] = None,
        take_profit: Optional[Decimal] = None,
    ):
        self.id = f"order_{int(datetime.utcnow().timestamp() * 1000)}"
        self.symbol = symbol
        self.side = side
        self.quantity = quantity
        self.price = price
        self.order_type = order_type
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.status = "pending"
        self.timestamp = datetime.utcnow()
        self.filled_quantity = Decimal("0")
        self.filled_price = Decimal("0")
        self.fees = Decimal("0")

    def to_dict(self) -> dict[str, Any]:
        """Convert order to dictionary."""
        return {
            "id": self.id,
            "symbol": self.symbol,
            "side": self.side,
            "quantity": str(self.quantity),
            "price": str(self.price) if self.price else None,
            "order_type": self.order_type,
            "stop_loss": str(self.stop_loss) if self.stop_loss else None,
            "take_profit": str(self.take_profit) if self.take_profit else None,
            "status": self.status,
            "timestamp": self.timestamp.isoformat(),
            "filled_quantity": str(self.filled_quantity),
            "filled_price": str(self.filled_price),
            "fees": str(self.fees),
        }


@dataclass
class Position:
    """Trading position representation."""

    symbol: str
    quantity: Decimal
    entry_price: Decimal
    current_price: Decimal
    market_value: Decimal
    unrealized_pnl: Decimal
    stop_loss: Optional[Decimal] = None
    take_profit: Optional[Decimal] = None

    @property
    def side(self) -> str:
        """Get position side (long/short)."""
        return "long" if self.quantity > 0 else "short"
