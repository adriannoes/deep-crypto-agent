"""Adapter for MarketBu legacy system compatibility."""
import logging
from typing import Any, Optional

import pandas as pd

from ..feeds import BinanceFeed, CoinbaseFeed, YahooFinanceFeed
from ..feeds.market_data_feed import MarketType, Timeframe
from ..processing.data_cleaner import DataCleaner

logger = logging.getLogger(__name__)


class AbuMarketAdapter:
    """
    Adapter to provide MarketBu-compatible interface using the new Data Layer.

    This adapter allows legacy abupy code to use the new market data feeds
    without requiring major changes to existing code.
    """

    def __init__(self):
        """Initialize adapter with default feed configurations."""
        self._feeds = {}
        self._default_feed = None

        # Initialize default feeds
        self._setup_default_feeds()

    def _setup_default_feeds(self):
        """Setup default market data feeds."""
        try:
            # Crypto feeds
            self._feeds["binance"] = BinanceFeed()
            self._feeds["coinbase"] = CoinbaseFeed()

            # Traditional market feeds
            self._feeds["yahoo"] = YahooFinanceFeed()

            # Set default feed (Binance for crypto, Yahoo for stocks)
            self._default_feed = self._feeds["binance"]

        except Exception as e:
            logger.warning(f"Failed to initialize some feeds: {e}")

    def all_symbol(self, index: bool = False) -> list[str]:
        """
        Get all available symbols (MarketBu compatibility).

        Args:
            index: If True, return only index symbols (not implemented)

        Returns:
            List of available symbols
        """
        if not self._default_feed:
            return []

        try:
            symbols = self._default_feed.get_symbols()
            return list(symbols)
        except Exception as e:
            logger.error(f"Failed to get symbols: {e}")
            return []

    def get_price(
        self,
        symbol: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        frequency: str = "1d",
        market: str = "crypto",
    ) -> Optional[pd.DataFrame]:
        """
        Get price data (MarketBu compatibility).

        Args:
            symbol: Trading symbol
            start_date: Start date (YYYY-MM-DD format)
            end_date: End date (YYYY-MM-DD format)
            frequency: Data frequency ('1d', '1h', '1m', etc.)
            market: Market type ('crypto', 'stock', 'forex')

        Returns:
            DataFrame with price data or None if failed
        """
        try:
            # Select appropriate feed based on market
            feed = self._select_feed(market)
            if not feed:
                logger.error(f"No suitable feed found for market: {market}")
                return None

            # Convert frequency to Timeframe enum
            timeframe = self._convert_frequency_to_timeframe(frequency)

            # Parse dates
            start = pd.to_datetime(start_date) if start_date else None
            end = pd.to_datetime(end_date) if end_date else None

            # Get data
            data = feed.get_klines(symbol, timeframe, start, end)

            if data is not None and not data.empty:
                # Clean and validate data
                data = DataCleaner.clean_ohlcv_data(data)

                # Convert to format expected by legacy code
                data = self._convert_to_legacy_format(data)

                return data

            return None

        except Exception as e:
            logger.error(f"Failed to get price data for {symbol}: {e}")
            return None

    def _select_feed(self, market: str) -> Optional[Any]:
        """
        Select appropriate feed based on market type.

        Args:
            market: Market type string

        Returns:
            MarketDataFeed instance or None
        """
        market = market.lower()

        if market in ["crypto", "cryptocurrency"]:
            # Try Binance first, then Coinbase
            for feed_name in ["binance", "coinbase"]:
                if feed_name in self._feeds:
                    return self._feeds[feed_name]
        elif market in ["stock", "equity"]:
            if "yahoo" in self._feeds:
                return self._feeds["yahoo"]
        elif market in ["forex", "currency"]:
            if "yahoo" in self._feeds:
                yahoo_feed = self._feeds["yahoo"]
                # Configure for forex market
                yahoo_feed.market_type = MarketType.FOREX
                return yahoo_feed

        # Default to first available feed
        if self._feeds:
            return list(self._feeds.values())[0]

        return None

    def _convert_frequency_to_timeframe(self, frequency: str) -> Timeframe:
        """
        Convert frequency string to Timeframe enum.

        Args:
            frequency: Frequency string (e.g., '1d', '1h', '1m')

        Returns:
            Timeframe enum value
        """
        freq_map = {
            "1m": Timeframe.MINUTE_1,
            "5m": Timeframe.MINUTE_5,
            "15m": Timeframe.MINUTE_15,
            "30m": Timeframe.MINUTE_30,
            "1h": Timeframe.HOUR_1,
            "4h": Timeframe.HOUR_4,
            "1d": Timeframe.DAY_1,
            "1w": Timeframe.WEEK_1,
            "1M": Timeframe.MONTH_1,
        }

        return freq_map.get(frequency.lower(), Timeframe.DAY_1)

    def _convert_to_legacy_format(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Convert data to format expected by legacy abupy code.

        Args:
            data: DataFrame from new data layer

        Returns:
            DataFrame in legacy format
        """
        if data.empty:
            return data

        df = data.copy()

        # Legacy abupy expects specific column names
        # The new format already uses: open, high, low, close, volume
        # which should be compatible with legacy code

        # Ensure datetime index
        if not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index)

        return df

    def get_market_data(
        self,
        symbol: str,
        market: str = "crypto",
        timeframe: str = "1d",
        limit: Optional[int] = None,
    ) -> Optional[dict[str, Any]]:
        """
        Get market data in a format compatible with legacy code.

        Args:
            symbol: Trading symbol
            market: Market type
            timeframe: Timeframe string
            limit: Maximum number of records

        Returns:
            Dictionary with market data
        """
        try:
            data = self.get_price(symbol, market=market, frequency=timeframe)

            if data is None or data.empty:
                return None

            if limit:
                data = data.tail(limit)

            # Convert to dictionary format sometimes used by legacy code
            result = {
                "symbol": symbol,
                "data": data,
                "market": market,
                "timeframe": timeframe,
                "count": len(data),
                "start_date": data.index.min().isoformat() if len(data) > 0 else None,
                "end_date": data.index.max().isoformat() if len(data) > 0 else None,
            }

            return result

        except Exception as e:
            logger.error(f"Failed to get market data: {e}")
            return None

    def get_current_price(self, symbol: str, market: str = "crypto") -> Optional[float]:
        """
        Get current price for a symbol.

        Args:
            symbol: Trading symbol
            market: Market type

        Returns:
            Current price or None if not available
        """
        try:
            feed = self._select_feed(market)
            if not feed:
                return None

            ticker_data = feed.get_ticker(symbol)

            if ticker_data and "price" in ticker_data:
                return float(ticker_data["price"])

            return None

        except Exception as e:
            logger.error(f"Failed to get current price for {symbol}: {e}")
            return None

    def is_market_open(self, market: str = "crypto") -> bool:
        """
        Check if market is currently open.

        Args:
            market: Market type

        Returns:
            True if market is open, False otherwise
        """
        # Simplified implementation - crypto markets are always "open"
        if market.lower() in ["crypto", "cryptocurrency"]:
            return True

        # For traditional markets, check current time
        # This is a basic implementation - could be enhanced
        from datetime import datetime

        now = datetime.now()

        if market.lower() in ["stock", "equity"]:
            # US stock market hours (simplified)
            weekday = now.weekday()  # 0=Monday, 6=Sunday
            if weekday >= 5:  # Weekend
                return False

            market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
            market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)

            return market_open <= now <= market_close

        return True  # Default to open for other markets


# Global instance for backward compatibility
_abu_market_adapter = AbuMarketAdapter()


def all_symbol(index: bool = False) -> list[str]:
    """
    Legacy MarketBu compatible function.

    Args:
        index: If True, return only index symbols

    Returns:
        List of symbols
    """
    return _abu_market_adapter.all_symbol(index)


# Create a module-level instance that mimics the old MarketMixin
class MarketMixin:
    """Mixin class that provides market data access methods."""

    def get_price(self, symbol: str, **kwargs) -> Optional[pd.DataFrame]:
        """Get price data for symbol."""
        return _abu_market_adapter.get_price(symbol, **kwargs)

    def get_current_price(self, symbol: str, market: str = "crypto") -> Optional[float]:
        """Get current price for symbol."""
        return _abu_market_adapter.get_current_price(symbol, market)

    def get_market_data(self, symbol: str, **kwargs) -> Optional[dict[str, Any]]:
        """Get market data for symbol."""
        return _abu_market_adapter.get_market_data(symbol, **kwargs)

    def is_market_open(self, market: str = "crypto") -> bool:
        """Check if market is open."""
        return _abu_market_adapter.is_market_open(market)


# Export for backward compatibility
__all__ = ["MarketMixin", "all_symbol", "AbuMarketAdapter"]
