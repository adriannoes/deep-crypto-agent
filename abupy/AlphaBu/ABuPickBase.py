# -*- encoding:utf-8 -*-
"""
Timing and stock selection abstract base classes.

This module provides abstract base classes for timing and stock selection
operations in the ABU quantitative trading system.
"""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

from abc import ABCMeta, abstractmethod
from typing import Any

from ..CoreBu.ABuFixes import six
from ..CoreBu.ABuBase import AbuParamBase

__author__ = 'ABU'
__weixin__ = 'abu_quant'


class AbuPickTimeWorkBase(six.with_metaclass(ABCMeta, AbuParamBase)):
    """
    Timing abstract base class.
    
    This class defines the interface for timing operations, which determine
    when to enter and exit trades based on market conditions.
    
    Subclasses must implement:
    - fit(): Execute timing operations
    - init_sell_factors(): Initialize sell timing factors
    - init_buy_factors(): Initialize buy timing factors
    """

    @abstractmethod
    def fit(self, *args: Any, **kwargs: Any) -> Any:
        """
        Execute timing operations.
        
        In the entire project, fit means starting the most important work of the object.
        For timing objects, it means starting timing operations, or literally,
        starting to fit timing operations on trading data.
        
        Args:
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments
            
        Returns:
            Result of timing operations (type depends on implementation)
        """
        pass

    @abstractmethod
    def init_sell_factors(self, *args: Any, **kwargs: Any) -> None:
        """
        Initialize timing sell factors.
        
        Sets up the factors that determine when to sell positions.
        
        Args:
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments
        """
        pass

    @abstractmethod
    def init_buy_factors(self, *args: Any, **kwargs: Any) -> None:
        """
        Initialize timing buy factors.
        
        Sets up the factors that determine when to buy positions.
        
        Args:
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments
        """
        pass


class AbuPickStockWorkBase(six.with_metaclass(ABCMeta, AbuParamBase)):
    """
    Stock selection abstract base class.
    
    This class defines the interface for stock selection operations, which
    determine which stocks to include in the trading universe.
    
    Subclasses must implement:
    - fit(): Execute stock selection operations
    - init_stock_pickers(): Initialize stock selection factors
    """

    @abstractmethod
    def fit(self, *args: Any, **kwargs: Any) -> Any:
        """
        Execute stock selection operations.
        
        In the entire project, fit means starting the most important work of the object.
        For stock selection objects, it means starting stock selection operations, or literally,
        starting to fit stock selection operations on trading data.
        
        Args:
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments
            
        Returns:
            Result of stock selection operations (type depends on implementation)
        """
        pass

    @abstractmethod
    def init_stock_pickers(self, *args: Any, **kwargs: Any) -> None:
        """
        Initialize stock selection factors.
        
        Sets up the factors used to select stocks for trading.
        
        Args:
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments
        """
        pass
