"""Adapter for legacy ABU BetaBu compatibility."""
from typing import Any

from .position_manager import PositionManager


class AbuPositionAdapter:
    """
    Adapter to use new PositionManager as legacy AbuPositionBase.

    Allows new position management to work with legacy ABU backtesting system.
    """

    def __init__(
        self,
        position_manager: PositionManager,
        kl_pd_buy: Any,
        factor_name: str,
        symbol_name: str,
        bp: float,
        read_cash: float,
        **kwargs: Any,
    ):
        """
        Initialize adapter.

        Args:
            position_manager: PositionManager instance
            kl_pd_buy: Legacy trading data
            factor_name: Factor name
            symbol_name: Symbol name
            bp: Buy price
            read_cash: Available cash
            **kwargs: Additional parameters
        """
        self.position_manager = position_manager
        self.kl_pd_buy = kl_pd_buy
        self.factor_name = factor_name
        self.symbol_name = symbol_name
        self.bp = bp
        self.read_cash = read_cash
        self.kwargs = kwargs

    def fit_position(self, factor_object: Any) -> float:
        """
        Legacy compatibility method for position sizing.

        Args:
            factor_object: Legacy factor object

        Returns:
            Position size (quantity) as float
        """
        from decimal import Decimal

        # Calculate position size using new PositionManager
        quantity = self.position_manager.calculate_position_size(
            symbol=self.symbol_name,
            price=Decimal(str(self.bp)),
            portfolio_value=Decimal(str(self.read_cash)),
            available_cash=Decimal(str(self.read_cash)),
        )

        return float(quantity)

    def _init_self(self, **kwargs: Any) -> None:
        """
        Legacy compatibility method.

        Args:
            **kwargs: Additional parameters
        """
        pass
