"""Traditional markets integration (stocks, forex, etc.)."""
from datetime import datetime
import logging
from typing import Any, Optional

import pandas as pd
import yfinance as yf

from .market_data_feed import MarketDataFeed, MarketType, Timeframe

logger = logging.getLogger(__name__)


class YahooFinanceFeed(MarketDataFeed):
    """
    Yahoo Finance data feed for traditional markets.

    Provides access to stock, forex, and other traditional market data
    through Yahoo Finance API.
    """

    # Mapping from our Timeframe enum to yfinance intervals
    TIMEFRAME_MAP = {
        Timeframe.MINUTE_1: "1m",
        Timeframe.MINUTE_5: "5m",
        Timeframe.MINUTE_15: "15m",
        Timeframe.MINUTE_30: "30m",
        Timeframe.HOUR_1: "1h",
        Timeframe.DAY_1: "1d",
        Timeframe.WEEK_1: "1wk",
        Timeframe.MONTH_1: "1mo",
    }

    def __init__(self, market_type: MarketType = MarketType.STOCK):
        """
        Initialize Yahoo Finance feed.

        Args:
            market_type: Type of market (STOCK, FOREX, etc.)
        """
        super().__init__(market_type, "yahoo_finance")
        self._symbols_cache: Optional[list[str]] = None

    def connect(self) -> bool:
        """Establish connection (Yahoo Finance doesn't require explicit connection)."""
        try:
            # Test with a common symbol
            test_symbol = "AAPL" if self.market_type == MarketType.STOCK else "EURUSD=X"
            ticker = yf.Ticker(test_symbol)
            _ = ticker.info  # Try to access info to verify connection
            self._connected = True
            logger.info("Connected to Yahoo Finance")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Yahoo Finance: {e}")
            self._connected = False
            return False

    def disconnect(self) -> None:
        """Close connection."""
        self._connected = False
        self._symbols_cache = None
        logger.info("Disconnected from Yahoo Finance")

    def get_symbols(self) -> list[str]:
        """
        Get list of available symbols.

        Note: Yahoo Finance doesn't provide a comprehensive symbol list API.
        This method returns a cached list of common symbols or empty list.
        """
        if self._symbols_cache:
            return self._symbols_cache

        # Return common symbols based on market type
        if self.market_type == MarketType.STOCK:
            self._symbols_cache = [
                "AAPL",
                "GOOGL",
                "MSFT",
                "AMZN",
                "TSLA",
                "META",
                "NVDA",
                "JPM",
                "V",
                "JNJ",
            ]
        elif self.market_type == MarketType.FOREX:
            self._symbols_cache = [
                "EURUSD=X",
                "GBPUSD=X",
                "USDJPY=X",
                "AUDUSD=X",
                "USDCAD=X",
            ]
        else:
            self._symbols_cache = []

        return self._symbols_cache

    def get_klines(
        self,
        symbol: str,
        timeframe: Timeframe,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        limit: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        Get OHLCV data from Yahoo Finance.

        Returns DataFrame with columns: ['open', 'high', 'low', 'close', 'volume', 'timestamp']
        """
        if not self._connected:
            self.connect()

        interval = self.TIMEFRAME_MAP.get(timeframe)
        if not interval:
            raise ValueError(f"Unsupported timeframe: {timeframe}")

        try:
            ticker = yf.Ticker(symbol)

            # Set period if start/end not provided
            if start and end:
                period = None
            else:
                period = "1mo" if timeframe == Timeframe.DAY_1 else "1d"

            # Download data
            df = ticker.history(
                start=start,
                end=end,
                interval=interval,
                period=period,
            )

            if df.empty:
                return pd.DataFrame()

            # Rename columns to match our standard
            df.rename(
                columns={
                    "Open": "open",
                    "High": "high",
                    "Low": "low",
                    "Close": "close",
                    "Volume": "volume",
                },
                inplace=True,
            )

            # Select only OHLCV columns
            df = df[["open", "high", "low", "close", "volume"]].copy()

            # Rename index to timestamp
            df.index.name = "timestamp"

            # Apply limit if specified
            if limit:
                df = df.tail(limit)

            return df

        except Exception as e:
            logger.error(f"Failed to get klines from Yahoo Finance: {e}")
            return pd.DataFrame()

    def get_ticker(self, symbol: str) -> dict[str, Any]:
        """Get current ticker information."""
        if not self._connected:
            self.connect()

        try:
            ticker = yf.Ticker(symbol)
            info: Any = ticker.info

            # Get current price
            hist = ticker.history(period="1d")
            current_price = hist["Close"].iloc[-1] if not hist.empty else None

            return {
                "symbol": symbol,
                "price": float(current_price) if current_price else None,
                "info": info,
            }
        except Exception as e:
            logger.error(f"Failed to get ticker from Yahoo Finance: {e}")
            return {}

    def get_orderbook(self, symbol: str, depth: int = 20) -> dict[str, Any]:
        """
        Get order book data.

        Note: Yahoo Finance doesn't provide order book data.
        Returns empty order book.
        """
        logger.warning("Yahoo Finance doesn't provide order book data")
        return {"bids": [], "asks": []}
