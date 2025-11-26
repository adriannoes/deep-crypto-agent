"""Database layer for market data persistence."""
from contextlib import contextmanager
from datetime import datetime
import logging
from typing import Any, Optional

from sqlalchemy import Column, DateTime, Float, Integer, String, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)

Base = declarative_base()


class MarketData(Base):  # type: ignore[misc,valid-type]
    """Market data table for OHLCV data."""

    __tablename__ = "market_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(50), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    open_price = Column(Float, nullable=False)
    high_price = Column(Float, nullable=False)
    low_price = Column(Float, nullable=False)
    close_price = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    market_type = Column(String(20), nullable=False)
    source = Column(String(50), nullable=False)

    def __repr__(self) -> str:
        return f"MarketData(symbol={self.symbol}, timestamp={self.timestamp}, close={self.close_price})"


class TickerData(Base):  # type: ignore[misc,valid-type]
    """Ticker data table."""

    __tablename__ = "ticker_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(50), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    price = Column(Float, nullable=False)
    volume_24h = Column(Float, nullable=True)
    price_change_24h = Column(Float, nullable=True)
    price_change_percent_24h = Column(Float, nullable=True)
    market_type = Column(String(20), nullable=False)
    source = Column(String(50), nullable=False)
    raw_data = Column(Text, nullable=True)  # JSON string for additional data

    def __repr__(self) -> str:
        return f"TickerData(symbol={self.symbol}, price={self.price}, timestamp={self.timestamp})"


class DatabaseManager:
    """
    Database manager for market data operations.

    Provides a unified interface for storing and retrieving market data
    using SQLAlchemy and PostgreSQL.
    """

    def __init__(self, connection_string: str):
        """
        Initialize database manager.

        Args:
            connection_string: SQLAlchemy connection string
        """
        self.engine = create_engine(connection_string, echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self._create_tables()

    def _create_tables(self) -> None:
        """Create all database tables."""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create database tables: {e}")
            raise

    @contextmanager
    def get_session(self):
        """Get database session with automatic cleanup."""
        session = self.SessionLocal()
        try:
            yield session
        finally:
            session.close()

    def save_market_data(
        self,
        symbol: str,
        data: Any,
        market_type: str,
        source: str,
    ) -> bool:
        """
        Save market data (OHLCV) to database.

        Args:
            symbol: Trading symbol
            data: DataFrame or dict containing market data
            market_type: Type of market (crypto, stock, etc.)
            source: Data source name

        Returns:
            True if successful, False otherwise
        """
        try:
            with self.get_session() as session:
                if hasattr(data, "iterrows"):  # DataFrame
                    records = []
                    for _, row in data.iterrows():
                        record = MarketData(
                            symbol=symbol,
                            timestamp=row.name,  # Assuming timestamp is index
                            open_price=float(row["open"]),
                            high_price=float(row["high"]),
                            low_price=float(row["low"]),
                            close_price=float(row["close"]),
                            volume=float(row["volume"]),
                            market_type=market_type,
                            source=source,
                        )
                        records.append(record)

                    session.bulk_save_objects(records)

                elif isinstance(data, dict):
                    # Single record
                    record = MarketData(
                        symbol=symbol,
                        timestamp=data.get("timestamp"),
                        open_price=float(data["open"]),
                        high_price=float(data["high"]),
                        low_price=float(data["low"]),
                        close_price=float(data["close"]),
                        volume=float(data["volume"]),
                        market_type=market_type,
                        source=source,
                    )
                    session.add(record)

                session.commit()
                logger.info(f"Saved market data for {symbol} from {source}")
                return True

        except Exception as e:
            logger.error(f"Failed to save market data: {e}")
            return False

    def save_ticker_data(
        self,
        symbol: str,
        ticker_data: dict[str, Any],
        market_type: str,
        source: str,
    ) -> bool:
        """
        Save ticker data to database.

        Args:
            symbol: Trading symbol
            ticker_data: Ticker information
            market_type: Type of market
            source: Data source name

        Returns:
            True if successful, False otherwise
        """
        try:
            with self.get_session() as session:
                record = TickerData(
                    symbol=symbol,
                    price=float(ticker_data.get("price", 0)),
                    volume_24h=float(ticker_data.get("volume_24h", 0)),
                    price_change_24h=float(ticker_data.get("price_change_24h", 0)),
                    price_change_percent_24h=float(ticker_data.get("price_change_percent_24h", 0)),
                    market_type=market_type,
                    source=source,
                    raw_data=str(ticker_data),  # Store full data as JSON string
                )
                session.add(record)
                session.commit()
                logger.info(f"Saved ticker data for {symbol} from {source}")
                return True

        except Exception as e:
            logger.error(f"Failed to save ticker data: {e}")
            return False

    def get_market_data(
        self,
        symbol: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: Optional[int] = None,
    ) -> Any:
        """
        Retrieve market data from database.

        Args:
            symbol: Trading symbol
            start_date: Start date filter
            end_date: End date filter
            limit: Maximum number of records

        Returns:
            DataFrame with market data
        """
        try:
            with self.get_session() as session:
                query = session.query(MarketData).filter(MarketData.symbol == symbol)

                if start_date:
                    query = query.filter(MarketData.timestamp >= start_date)
                if end_date:
                    query = query.filter(MarketData.timestamp <= end_date)

                query = query.order_by(MarketData.timestamp.desc())

                if limit:
                    query = query.limit(limit)

                records = query.all()

                if not records:
                    return None

                # Convert to DataFrame
                data = {
                    "timestamp": [r.timestamp for r in reversed(records)],
                    "open": [r.open_price for r in reversed(records)],
                    "high": [r.high_price for r in reversed(records)],
                    "low": [r.low_price for r in reversed(records)],
                    "close": [r.close_price for r in reversed(records)],
                    "volume": [r.volume for r in reversed(records)],
                }

                import pandas as pd

                df = pd.DataFrame(data)
                df.set_index("timestamp", inplace=True)

                return df

        except Exception as e:
            logger.error(f"Failed to retrieve market data: {e}")
            return None

    def get_latest_ticker(self, symbol: str) -> Optional[dict[str, Any]]:
        """
        Get latest ticker data for symbol.

        Args:
            symbol: Trading symbol

        Returns:
            Latest ticker data or None if not found
        """
        try:
            with self.get_session() as session:
                record = (
                    session.query(TickerData)
                    .filter(TickerData.symbol == symbol)
                    .order_by(TickerData.timestamp.desc())
                    .first()
                )

                if record:
                    return {
                        "symbol": record.symbol,
                        "price": record.price,
                        "volume_24h": record.volume_24h,
                        "price_change_24h": record.price_change_24h,
                        "price_change_percent_24h": record.price_change_percent_24h,
                        "timestamp": record.timestamp,
                        "source": record.source,
                    }

                return None

        except Exception as e:
            logger.error(f"Failed to retrieve ticker data: {e}")
            return None

    def get_symbols(self) -> list[str]:
        """
        Get list of all symbols in database.

        Returns:
            List of unique symbols
        """
        try:
            with self.get_session() as session:
                symbols = session.query(MarketData.symbol).distinct().all()
                return [s[0] for s in symbols]

        except Exception as e:
            logger.error(f"Failed to retrieve symbols: {e}")
            return []

    def cleanup_old_data(self, days_to_keep: int = 365) -> int:
        """
        Remove old market data.

        Args:
            days_to_keep: Number of days of data to keep

        Returns:
            Number of records deleted
        """
        try:
            cutoff_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            cutoff_date = cutoff_date.replace(day=cutoff_date.day - days_to_keep)

            with self.get_session() as session:
                deleted_count = (
                    session.query(MarketData).filter(MarketData.timestamp < cutoff_date).delete()
                )

                session.commit()
                logger.info(f"Cleaned up {deleted_count} old market data records")
                return int(deleted_count)

        except Exception as e:
            logger.error(f"Failed to cleanup old data: {e}")
            return 0
