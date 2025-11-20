"""Market data feed interface and base classes."""
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any, Optional

import pandas as pd


class MarketType(Enum):
    """Market type enumeration."""

    CRYPTO = "crypto"
    STOCK = "stock"
    FOREX = "forex"
    FUTURES = "futures"
    OPTIONS = "options"


class Timeframe(Enum):
    """Timeframe enumeration."""

    TICK = "tick"
    MINUTE_1 = "1m"
    MINUTE_5 = "5m"
    MINUTE_15 = "15m"
    MINUTE_30 = "30m"
    HOUR_1 = "1h"
    HOUR_4 = "4h"
    DAY_1 = "1d"
    WEEK_1 = "1w"
    MONTH_1 = "1M"


class MarketDataFeed(ABC):
    """
    Abstract base class for market data feeds.

    This class defines the interface that all market data providers must implement.
    It provides a unified API for accessing market data from different sources.
    """

    def __init__(self, market_type: MarketType, name: str):
        """
        Initialize market data feed.

        Args:
            market_type: Type of market (crypto, stock, etc.)
            name: Name identifier for this feed
        """
        self.market_type = market_type
        self.name = name
        self._connected = False

    @abstractmethod
    def connect(self) -> bool:
        """
        Establish connection to data source.

        Returns:
            True if connection successful, False otherwise
        """
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Close connection to data source."""
        pass

    @abstractmethod
    def get_symbols(self) -> list[str]:
        """
        Get list of available trading symbols.

        Returns:
            List of symbol strings (e.g., ['BTCUSDT', 'ETHUSDT'])
        """
        pass

    @abstractmethod
    def get_klines(
        self,
        symbol: str,
        timeframe: Timeframe,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        limit: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        Get OHLCV (Open, High, Low, Close, Volume) data.

        Args:
            symbol: Trading symbol (e.g., 'BTCUSDT')
            timeframe: Timeframe for the data
            start: Start datetime (optional)
            end: End datetime (optional)
            limit: Maximum number of candles to return (optional)

        Returns:
            DataFrame with columns: ['open', 'high', 'low', 'close', 'volume', 'timestamp']
        """
        pass

    @abstractmethod
    def get_ticker(self, symbol: str) -> dict[str, Any]:
        """
        Get current ticker information for a symbol.

        Args:
            symbol: Trading symbol

        Returns:
            Dictionary with ticker data (price, volume, etc.)
        """
        pass

    @abstractmethod
    def get_orderbook(self, symbol: str, depth: int = 20) -> dict[str, Any]:
        """
        Get order book data for a symbol.

        Args:
            symbol: Trading symbol
            depth: Number of price levels to return

        Returns:
            Dictionary with 'bids' and 'asks' lists
        """
        pass

    def is_connected(self) -> bool:
        """
        Check if feed is connected.

        Returns:
            True if connected, False otherwise
        """
        return self._connected

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()

    def __repr__(self) -> str:
        """String representation."""
        return f"{self.__class__.__name__}(market_type={self.market_type.value}, name={self.name})"
