# -*- encoding:utf-8 -*-
"""
Risk control position management base.

This module provides the abstract base class for position management strategies,
which control how much capital to allocate to each trade.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from abc import ABCMeta, abstractmethod
from typing import Any, Optional

from ..CoreBu.ABuFixes import six
from ..MarketBu.ABuMarket import MarketMixin

# Maximum position ratio setting for each trade.
# External can modify the maximum position ratio for each trade through,
# e.g.: abupy.beta.position.g_pos_max = 0.5, default 75%
g_pos_max: float = 0.75

# Minimum margin ratio, default 1, meaning no margin trading, will not trigger Margin Call.
# In futures data, there is a minimum margin ratio for each commodity, which can be set.
# External can modify through, e.g.: abupy.beta.position.g_deposit_rate = 0.5
g_deposit_rate: float = 1.0

# Global default position management class for buy factors. When default is None,
# AbuAtrPosition will be used as the default position management class.
#
# Unlike sell factors and stock selection factors, a buy factor can correspond to multiple
# sell factors and multiple stock selection factors, but a buy factor can only correspond
# to one position management class, which can be a global position management or a unique
# attached position management class for the buy factor.
g_default_pos_class: Optional[Any] = None


class AbuPositionBase(six.with_metaclass(ABCMeta, MarketMixin)):
    """
    Position management abstract base class.
    
    This class defines the interface for position management strategies, which
    determine how much capital to allocate to each trade based on risk parameters.
    
    Subclasses must implement:
    - _init_self(): Initialize subclass-specific parameters
    - fit_position(): Calculate position size for a given trade
    """

    def __init__(
        self,
        kl_pd_buy: Any,
        factor_name: str,
        symbol_name: str,
        bp: float,
        read_cash: float,
        **kwargs: Any
    ) -> None:
        """
        Initialize position management base class.
        
        Args:
            kl_pd_buy: Trading data for the trading day (pandas DataFrame)
            factor_name: Factor name identifier
            symbol_name: Symbol code (e.g., 'usAAPL')
            bp: Buy price
            read_cash: Initial capital available
            **kwargs: Additional parameters including:
                - pos_max: Maximum position ratio (default: g_pos_max)
                - deposit_rate: Margin ratio (default: g_deposit_rate)
        """
        self.kl_pd_buy = kl_pd_buy
        self.factor_name = factor_name
        self.symbol_name = symbol_name
        self.bp = bp
        self.read_cash = read_cash

        # If there is a global maximum position setting, base class handles it
        self.pos_max = kwargs.pop('pos_max', g_pos_max)
        # If there is a global minimum margin ratio setting, base class handles it
        self.deposit_rate = kwargs.pop('deposit_rate', g_deposit_rate)

        # Subclass continues to complete its own construction
        self._init_self(**kwargs)

    def __str__(self) -> str:
        """
        String representation of the object.
        
        Returns:
            String showing class name, factor_name, symbol_name, read_cash, deposit_rate
        """
        return '{}: factor_name:{}, symbol_name:{}, read_cash:{}, deposit_rate:{}'.format(
            self.__class__.__name__,
            self.factor_name,
            self.symbol_name,
            self.read_cash,
            self.deposit_rate
        )

    __repr__ = __str__

    @abstractmethod
    def _init_self(self, **kwargs: Any) -> None:
        """
        Subclass position management initialization for extensible parameters.
        
        This method should be overridden by subclasses to initialize
        subclass-specific parameters.
        
        Args:
            **kwargs: Additional parameters specific to the subclass
        """
        pass

    @abstractmethod
    def fit_position(self, factor_object: Any) -> float:
        """
        Calculate position size for a trade.
        
        The result of fit_position calculation is how many units to buy
        (shares, lots, contracts). Specific calculation is implemented by subclasses.
        
        Args:
            factor_object: ABuFactorBuyBase instance object
            
        Returns:
            Number of units to buy (shares, lots, contracts) as float
        """
        pass
