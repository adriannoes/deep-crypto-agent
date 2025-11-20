"""Crypto exchange integrations."""
from datetime import datetime
import logging
from typing import Any, Optional

import pandas as pd
import requests  # type: ignore[import-untyped]

from .market_data_feed import MarketDataFeed, MarketType, Timeframe

logger = logging.getLogger(__name__)


class BinanceFeed(MarketDataFeed):
    """
    Binance cryptocurrency exchange data feed.

    Provides access to Binance market data through their public API.
    """

    BASE_URL = "https://api.binance.com/api/v3"

    # Mapping from our Timeframe enum to Binance intervals
    TIMEFRAME_MAP = {
        Timeframe.MINUTE_1: "1m",
        Timeframe.MINUTE_5: "5m",
        Timeframe.MINUTE_15: "15m",
        Timeframe.MINUTE_30: "30m",
        Timeframe.HOUR_1: "1h",
        Timeframe.HOUR_4: "4h",
        Timeframe.DAY_1: "1d",
        Timeframe.WEEK_1: "1w",
        Timeframe.MONTH_1: "1M",
    }

    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None):
        """
        Initialize Binance feed.

        Args:
            api_key: Binance API key (optional for public data)
            api_secret: Binance API secret (optional for public data)
        """
        super().__init__(MarketType.CRYPTO, "binance")
        self.api_key = api_key
        self.api_secret = api_secret
        self.session = requests.Session()

    def connect(self) -> bool:
        """Establish connection to Binance API."""
        try:
            # Test connection with a simple API call
            response = self.session.get(f"{self.BASE_URL}/ping", timeout=5)
            response.raise_for_status()
            self._connected = True
            logger.info("Connected to Binance API")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Binance: {e}")
            self._connected = False
            return False

    def disconnect(self) -> None:
        """Close connection."""
        self.session.close()
        self._connected = False
        logger.info("Disconnected from Binance API")

    def get_symbols(self) -> list[str]:
        """Get list of available trading symbols."""
        try:
            response = self.session.get(f"{self.BASE_URL}/exchangeInfo", timeout=10)
            response.raise_for_status()
            data = response.json()
            symbols = [s["symbol"] for s in data.get("symbols", []) if s["status"] == "TRADING"]
            return symbols
        except Exception as e:
            logger.error(f"Failed to get symbols from Binance: {e}")
            return []

    def get_klines(
        self,
        symbol: str,
        timeframe: Timeframe,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        limit: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        Get OHLCV data from Binance.

        Returns DataFrame with columns: ['open', 'high', 'low', 'close', 'volume', 'timestamp']
        """
        if not self._connected:
            self.connect()

        interval = self.TIMEFRAME_MAP.get(timeframe)
        if not interval:
            raise ValueError(f"Unsupported timeframe: {timeframe}")

        params: dict[str, Any] = {"symbol": symbol, "interval": interval}

        if start:
            params["startTime"] = int(start.timestamp() * 1000)
        if end:
            params["endTime"] = int(end.timestamp() * 1000)
        if limit:
            params["limit"] = min(limit, 1000)  # Binance max is 1000

        try:
            response = self.session.get(f"{self.BASE_URL}/klines", params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if not data:
                return pd.DataFrame()

            # Convert to DataFrame
            df = pd.DataFrame(
                data,
                columns=[
                    "timestamp",
                    "open",
                    "high",
                    "low",
                    "close",
                    "volume",
                    "close_time",
                    "quote_volume",
                    "trades",
                    "taker_buy_base",
                    "taker_buy_quote",
                    "ignore",
                ],
            )

            # Convert types
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
            for col in ["open", "high", "low", "close", "volume"]:
                df[col] = df[col].astype(float)

            # Select and rename columns
            df = df[["timestamp", "open", "high", "low", "close", "volume"]].copy()
            df.set_index("timestamp", inplace=True)

            return df

        except Exception as e:
            logger.error(f"Failed to get klines from Binance: {e}")
            return pd.DataFrame()

    def get_ticker(self, symbol: str) -> dict[str, Any]:
        """Get current ticker information."""
        if not self._connected:
            self.connect()

        try:
            response = self.session.get(
                f"{self.BASE_URL}/ticker/24hr", params={"symbol": symbol}, timeout=10
            )
            response.raise_for_status()
            return response.json()  # type: ignore[no-any-return]
        except Exception as e:
            logger.error(f"Failed to get ticker from Binance: {e}")
            return {}

    def get_orderbook(self, symbol: str, depth: int = 20) -> dict[str, Any]:
        """Get order book data."""
        if not self._connected:
            self.connect()

        try:
            params = {"symbol": symbol, "limit": min(depth, 5000)}  # Binance max is 5000
            response = self.session.get(f"{self.BASE_URL}/depth", params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return {"bids": data.get("bids", []), "asks": data.get("asks", [])}
        except Exception as e:
            logger.error(f"Failed to get orderbook from Binance: {e}")
            return {"bids": [], "asks": []}


class CoinbaseFeed(MarketDataFeed):
    """
    Coinbase Pro cryptocurrency exchange data feed.

    Provides access to Coinbase Pro market data through their public API.
    """

    BASE_URL = "https://api.exchange.coinbase.com"

    # Mapping from our Timeframe enum to Coinbase granularity (in seconds)
    TIMEFRAME_MAP = {
        Timeframe.MINUTE_1: 60,
        Timeframe.MINUTE_5: 300,
        Timeframe.MINUTE_15: 900,
        Timeframe.MINUTE_30: 1800,
        Timeframe.HOUR_1: 3600,
        Timeframe.HOUR_4: 14400,
        Timeframe.DAY_1: 86400,
    }

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        passphrase: Optional[str] = None,
    ):
        """
        Initialize Coinbase feed.

        Args:
            api_key: Coinbase API key (optional for public data)
            api_secret: Coinbase API secret (optional for public data)
            passphrase: Coinbase API passphrase (optional for public data)
        """
        super().__init__(MarketType.CRYPTO, "coinbase")
        self.api_key = api_key
        self.api_secret = api_secret
        self.passphrase = passphrase
        self.session = requests.Session()

    def connect(self) -> bool:
        """Establish connection to Coinbase API."""
        try:
            response = self.session.get(f"{self.BASE_URL}/time", timeout=5)
            response.raise_for_status()
            self._connected = True
            logger.info("Connected to Coinbase API")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Coinbase: {e}")
            self._connected = False
            return False

    def disconnect(self) -> None:
        """Close connection."""
        self.session.close()
        self._connected = False
        logger.info("Disconnected from Coinbase API")

    def get_symbols(self) -> list[str]:
        """Get list of available trading symbols."""
        try:
            response = self.session.get(f"{self.BASE_URL}/products", timeout=10)
            response.raise_for_status()
            products = response.json()
            symbols = [p["id"] for p in products if p.get("status") == "online"]
            return symbols
        except Exception as e:
            logger.error(f"Failed to get symbols from Coinbase: {e}")
            return []

    def get_klines(
        self,
        symbol: str,
        timeframe: Timeframe,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        limit: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        Get OHLCV data from Coinbase.

        Returns DataFrame with columns: ['open', 'high', 'low', 'close', 'volume', 'timestamp']
        """
        if not self._connected:
            self.connect()

        granularity = self.TIMEFRAME_MAP.get(timeframe)
        if not granularity:
            raise ValueError(f"Unsupported timeframe: {timeframe}")

        params: dict[str, Any] = {"granularity": granularity}

        if start:
            params["start"] = start.isoformat()
        if end:
            params["end"] = end.isoformat()

        try:
            endpoint = f"{self.BASE_URL}/products/{symbol}/candles"
            response = self.session.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if not data:
                return pd.DataFrame()

            # Coinbase returns: [time, low, high, open, close, volume]
            df = pd.DataFrame(
                data,
                columns=["timestamp", "low", "high", "open", "close", "volume"],
            )

            # Convert timestamp
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")

            # Convert types
            for col in ["open", "high", "low", "close", "volume"]:
                df[col] = df[col].astype(float)

            # Reorder columns
            df = df[["timestamp", "open", "high", "low", "close", "volume"]].copy()
            df.set_index("timestamp", inplace=True)
            df.sort_index(inplace=True)

            # Apply limit if specified
            if limit:
                df = df.tail(limit)

            return df

        except Exception as e:
            logger.error(f"Failed to get klines from Coinbase: {e}")
            return pd.DataFrame()

    def get_ticker(self, symbol: str) -> dict[str, Any]:
        """Get current ticker information."""
        if not self._connected:
            self.connect()

        try:
            endpoint = f"{self.BASE_URL}/products/{symbol}/ticker"
            response = self.session.get(endpoint, timeout=10)
            response.raise_for_status()
            return response.json()  # type: ignore[no-any-return]
        except Exception as e:
            logger.error(f"Failed to get ticker from Coinbase: {e}")
            return {}

    def get_orderbook(self, symbol: str, depth: int = 20) -> dict[str, Any]:
        """Get order book data."""
        if not self._connected:
            self.connect()

        try:
            level = 2 if depth <= 50 else 3
            endpoint = f"{self.BASE_URL}/products/{symbol}/book"
            params = {"level": level}
            response = self.session.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return {"bids": data.get("bids", []), "asks": data.get("asks", [])}
        except Exception as e:
            logger.error(f"Failed to get orderbook from Coinbase: {e}")
            return {"bids": [], "asks": []}
