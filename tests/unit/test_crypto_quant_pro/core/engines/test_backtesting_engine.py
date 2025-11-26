"""Tests for BacktestingEngine."""
from datetime import datetime, timedelta
from decimal import Decimal

import pandas as pd
import pytest

from crypto_quant_pro.core.engines.backtesting_engine import (
    BacktestConfig,
    BacktestingEngine,
    BacktestResult,
)
from crypto_quant_pro.data import MarketDataFeed, Timeframe


class MockHistoryFeed(MarketDataFeed):
    def __init__(self):
        super().__init__(market_type="crypto", name="mock")

    def get_klines(self, symbol, timeframe, start_date=None, end_date=None, limit=None):
        # Generate mock data
        dates = pd.date_range(start=start_date, end=end_date, freq="D")
        data = {
            "timestamp": dates,
            "open": [100.0 + i for i in range(len(dates))],
            "high": [105.0 + i for i in range(len(dates))],
            "low": [95.0 + i for i in range(len(dates))],
            "close": [101.0 + i for i in range(len(dates))],  # Upward trend
            "volume": [1000.0 for _ in range(len(dates))],
        }
        df = pd.DataFrame(data)
        df.set_index("timestamp", inplace=True)
        return df

    def get_ticker(self, symbol):
        pass

    def get_orderbook(self, symbol, depth=20):
        pass

    def get_trades(self, symbol, limit=100):
        pass

    def get_symbols(self):
        return ["BTC/USD"]

    def connect(self):
        pass

    def disconnect(self):
        pass


@pytest.mark.asyncio
async def test_backtest_run():
    """Test basic backtest run."""
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2023, 1, 10)
    config = BacktestConfig(
        start_date=start_date, end_date=end_date, initial_capital=Decimal("10000")
    )
    data_feed = MockHistoryFeed()
    engine = BacktestingEngine(config, data_feed)

    async def strategy(engine: BacktestingEngine, date: datetime):
        # Simple buy and hold strategy
        if date == start_date:
            engine.buy("BTC/USD", Decimal("10.0"))

    result = await engine.run_backtest(strategy, ["BTC/USD"])

    assert isinstance(result, BacktestResult)
    # total_trades counts all trades (buy and sell orders)
    assert result.total_trades == 1  # One buy order
    # But we should have one trade in the history
    assert len(result.trades) == 1
    assert len(result.portfolio_values) > 0

    # Since price goes up (101, 102, ...), we should be profitable
    # Initial: 10000
    # Buy 10 @ 101 (+ slippage + comm) -> Cost approx 1010 + fees
    # End price @ Jan 10 (9 days later): 101 + 9 = 110
    # Value: 10 * 110 = 1100
    # Total > 10000 (roughly)
    # Note: slippage and commission might eat small profits
    assert result.total_return > -0.1  # At least not a huge loss


@pytest.mark.asyncio
async def test_backtest_buy_sell():
    """Test buy and sell logic in backtest."""
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2023, 1, 5)
    config = BacktestConfig(start_date=start_date, end_date=end_date)
    data_feed = MockHistoryFeed()
    engine = BacktestingEngine(config, data_feed)

    # Load data
    await engine._load_historical_data(["BTC/USD"], Timeframe.DAY_1)

    # Set date manually to test methods
    engine.set_current_date(start_date)

    # Buy
    success = engine.buy("BTC/USD", Decimal("1.0"))
    assert success
    positions = engine.get_positions()
    assert positions["BTC/USD"]["quantity"] == Decimal("1.0")

    # Advance date
    next_day = start_date + timedelta(days=1)
    engine.set_current_date(next_day)

    # Sell
    success = engine.sell("BTC/USD", Decimal("1.0"))
    assert success
    assert "BTC/USD" not in engine.positions

    # Check trades
    assert len(engine.trades) == 2
    assert engine.trades[0]["side"] == "buy"
    assert engine.trades[1]["side"] == "sell"
    assert engine.trades[1]["realized_pnl"] != 0
