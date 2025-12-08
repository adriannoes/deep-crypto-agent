# Strategy Examples

This document provides practical examples of using the strategy system.

## Table of Contents

1. [Basic Strategy Usage](#basic-strategy-usage)
2. [Backtesting with Strategies](#backtesting-with-strategies)
3. [Paper Trading with Strategies](#paper-trading-with-strategies)
4. [Combining Multiple Strategies](#combining-multiple-strategies)
5. [Custom Strategy Implementation](#custom-strategy-implementation)
6. [Legacy ABU Integration](#legacy-abu-integration)

## Basic Strategy Usage

### Simple Buy Signal Generation

```python
import asyncio
from datetime import datetime
from decimal import Decimal
import pandas as pd
from crypto_quant_pro.core.strategies import MovingAverageCrossStrategy

async def main():
    # Initialize strategy
    strategy = MovingAverageCrossStrategy(
        fast_period=10,
        slow_period=30,
        name="MA_Cross_10_30"
    )

    # Create sample market data
    dates = pd.date_range("2024-01-01", periods=50, freq="D")
    prices = [100 + i * 0.5 for i in range(50)]

    market_data = pd.DataFrame({
        "date": dates,
        "open": prices,
        "high": [p * 1.01 for p in prices],
        "low": [p * 0.99 for p in prices],
        "close": prices,
        "volume": [1000] * 50
    })

    # Generate signals
    signals = await strategy.generate_signals(
        symbol="BTC/USD",
        market_data=market_data,
        current_date=datetime.now(),
        positions={},
        portfolio_value=Decimal("10000")
    )

    # Process signals
    for signal in signals:
        print(f"{signal.side.upper()}: {signal.quantity} {signal.symbol} @ {signal.price}")
        print(f"Confidence: {signal.confidence}")
        print(f"Metadata: {signal.metadata}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Backtesting with Strategies

### Complete Backtest Example

```python
import asyncio
from datetime import datetime, timedelta
from decimal import Decimal
from crypto_quant_pro.core.engines import BacktestingEngine, BacktestConfig
from crypto_quant_pro.core.strategies import (
    MovingAverageCrossStrategy,
    StopLossStrategy,
    TakeProfitStrategy
)
from crypto_quant_pro.data.feeds import BinanceFeed

async def run_backtest():
    # Initialize strategies
    buy_strategy = MovingAverageCrossStrategy(fast_period=10, slow_period=30)
    stop_loss = StopLossStrategy(stop_loss_pct=Decimal("0.05"))
    take_profit = TakeProfitStrategy(take_profit_pct=Decimal("0.10"))

    # Create backtest configuration
    config = BacktestConfig(
        start_date=datetime.now() - timedelta(days=365),
        end_date=datetime.now(),
        initial_capital=Decimal("10000"),
        commission=Decimal("0.001"),  # 0.1% commission
        slippage=Decimal("0.0005")    # 0.05% slippage
    )

    # Initialize data feed
    data_feed = BinanceFeed()
    await data_feed.connect()

    # Create backtesting engine
    engine = BacktestingEngine(config, data_feed)

    # Define strategy function
    async def strategy_func(engine, current_date):
        symbols = ["BTC/USD", "ETH/USD"]

        for symbol in symbols:
            # Get market data
            market_data = engine.market_data_cache.get(symbol)
            if market_data is None:
                continue

            # Generate buy signals
            buy_signals = await buy_strategy.generate_signals(
                symbol=symbol,
                market_data=market_data,
                current_date=current_date,
                positions=engine.positions,
                portfolio_value=engine.portfolio_value
            )

            # Execute buy orders
            for signal in buy_signals:
                if signal.side == "buy":
                    # Place order through engine
                    print(f"Buy signal: {signal.symbol} @ {signal.price}")

            # Check sell signals for existing positions
            if symbol in engine.positions:
                position = engine.positions[symbol]

                # Check stop loss
                stop_signals = await stop_loss.generate_signals(
                    symbol=symbol,
                    market_data=market_data,
                    current_date=current_date,
                    positions={symbol: position}
                )

                # Check take profit
                profit_signals = await take_profit.generate_signals(
                    symbol=symbol,
                    market_data=market_data,
                    current_date=current_date,
                    positions={symbol: position}
                )

                # Execute sell if triggered
                if stop_signals or profit_signals:
                    sell_signal = (stop_signals + profit_signals)[0]
                    print(f"Sell signal: {sell_signal.symbol} @ {sell_signal.price}")

    # Run backtest
    result = await engine.run_backtest(strategy_func, ["BTC/USD", "ETH/USD"])

    # Print results
    print("\n=== Backtest Results ===")
    print(f"Total Return: {result.total_return:.2%}")
    print(f"Annualized Return: {result.annualized_return:.2%}")
    print(f"Sharpe Ratio: {result.sharpe_ratio:.2f}")
    print(f"Max Drawdown: {result.max_drawdown:.2%}")
    print(f"Win Rate: {result.win_rate:.2%}")
    print(f"Total Trades: {result.total_trades}")

    await data_feed.disconnect()

if __name__ == "__main__":
    asyncio.run(run_backtest())
```

## Paper Trading with Strategies

### Live Paper Trading Example

```python
import asyncio
from datetime import datetime
from decimal import Decimal
from crypto_quant_pro.core.engines import TradingEngine, TradingConfig
from crypto_quant_pro.core.strategies import MovingAverageCrossStrategy, TrailingStopStrategy
from crypto_quant_pro.data.feeds import BinanceFeed

async def paper_trading():
    # Initialize strategies
    buy_strategy = MovingAverageCrossStrategy(fast_period=10, slow_period=30)
    trailing_stop = TrailingStopStrategy(trailing_pct=Decimal("0.05"))

    # Create trading configuration
    config = TradingConfig(
        paper_trading=True,  # Enable paper trading
        max_position_size=Decimal("0.2"),  # Max 20% per position
        max_open_positions=5
    )

    # Initialize data feed
    data_feed = BinanceFeed()
    await data_feed.connect()

    # Create trading engine
    engine = TradingEngine(config, data_feed)
    await engine.start()

    # Trading loop
    try:
        while True:
            symbols = ["BTC/USD", "ETH/USD"]

            for symbol in symbols:
                # Get current market data
                ticker = await data_feed.get_ticker(symbol)
                if not ticker:
                    continue

                # Get historical data for strategy
                klines = await data_feed.get_klines(
                    symbol=symbol,
                    timeframe=Timeframe.HOUR_1,
                    limit=50
                )

                if klines is None or len(klines) < 30:
                    continue

                # Generate buy signals
                buy_signals = await buy_strategy.generate_signals(
                    symbol=symbol,
                    market_data=klines,
                    current_date=datetime.now(),
                    positions=engine.positions,
                    portfolio_value=engine.portfolio_value,
                    cash=engine.cash
                )

                # Execute buy orders
                for signal in buy_signals:
                    if signal.side == "buy" and symbol not in engine.positions:
                        order = await engine.place_order(
                            symbol=signal.symbol,
                            side="buy",
                            quantity=signal.quantity,
                            order_type="market"
                        )
                        print(f"Placed buy order: {order.id}")

                # Check trailing stop for existing positions
                if symbol in engine.positions:
                    position = engine.positions[symbol]

                    # Update market data with current price
                    current_price = Decimal(str(ticker["last_price"]))
                    klines.loc[klines.index[-1], "close"] = float(current_price)

                    sell_signals = await trailing_stop.generate_signals(
                        symbol=symbol,
                        market_data=klines,
                        current_date=datetime.now(),
                        positions={symbol: position}
                    )

                    # Execute sell if trailing stop triggered
                    for signal in sell_signals:
                        if signal.side == "sell":
                            order = await engine.place_order(
                                symbol=signal.symbol,
                                side="sell",
                                quantity=signal.quantity,
                                order_type="market"
                            )
                            print(f"Placed sell order (trailing stop): {order.id}")

            # Wait before next iteration
            await asyncio.sleep(60)  # Check every minute

    except KeyboardInterrupt:
        print("Stopping trading engine...")
    finally:
        await engine.stop()
        await data_feed.disconnect()

if __name__ == "__main__":
    asyncio.run(paper_trading())
```

## Combining Multiple Strategies

### Multi-Strategy Portfolio

```python
import asyncio
from datetime import datetime
from decimal import Decimal
from crypto_quant_pro.core.strategies import (
    MovingAverageCrossStrategy,
    BreakoutStrategy,
    RSIStrategy,
    StopLossStrategy,
    TakeProfitStrategy
)

class MultiStrategyPortfolio:
    """Portfolio manager using multiple strategies."""

    def __init__(self):
        # Buy strategies
        self.buy_strategies = [
            MovingAverageCrossStrategy(fast_period=10, slow_period=30),
            BreakoutStrategy(lookback_period=20),
            RSIStrategy(period=14)
        ]

        # Sell strategies
        self.sell_strategies = [
            StopLossStrategy(stop_loss_pct=Decimal("0.05")),
            TakeProfitStrategy(take_profit_pct=Decimal("0.10"))
        ]

    async def evaluate_buy_signals(self, symbol, market_data, positions, **kwargs):
        """Evaluate all buy strategies and aggregate signals."""
        all_signals = []

        for strategy in self.buy_strategies:
            signals = await strategy.generate_signals(
                symbol=symbol,
                market_data=market_data,
                current_date=datetime.now(),
                positions=positions,
                **kwargs
            )
            all_signals.extend(signals)

        # Aggregate signals (e.g., take average quantity, highest confidence)
        if all_signals:
            # Simple aggregation: use signal with highest confidence
            best_signal = max(all_signals, key=lambda s: s.confidence)
            return [best_signal]

        return []

    async def evaluate_sell_signals(self, symbol, market_data, positions, **kwargs):
        """Evaluate all sell strategies."""
        all_signals = []

        for strategy in self.sell_strategies:
            signals = await strategy.generate_signals(
                symbol=symbol,
                market_data=market_data,
                current_date=datetime.now(),
                positions=positions,
                **kwargs
            )
            all_signals.extend(signals)

        return all_signals

# Usage
async def main():
    portfolio = MultiStrategyPortfolio()

    # Evaluate buy signals
    buy_signals = await portfolio.evaluate_buy_signals(
        symbol="BTC/USD",
        market_data=market_data_df,
        positions={},
        portfolio_value=Decimal("10000")
    )

    # Evaluate sell signals
    sell_signals = await portfolio.evaluate_sell_signals(
        symbol="BTC/USD",
        market_data=market_data_df,
        positions={"BTC/USD": {"entry_price": 50000, "quantity": 1.0}},
        portfolio_value=Decimal("10000")
    )

asyncio.run(main())
```

## Custom Strategy Implementation

### Mean Reversion Strategy

```python
from crypto_quant_pro.core.strategies import BaseStrategy, StrategySignal, StrategyDirection
from datetime import datetime
from decimal import Decimal
import pandas as pd
import numpy as np
from typing import Any, Optional

class MeanReversionStrategy(BaseStrategy):
    """Mean reversion strategy based on Bollinger Bands."""

    def __init__(
        self,
        period: int = 20,
        std_dev: Decimal = Decimal("2.0"),
        **kwargs
    ):
        name = kwargs.pop("name", f"MeanReversion_{period}")
        super().__init__(name=name, direction=StrategyDirection.CALL, **kwargs)
        self.period = period
        self.std_dev = std_dev

    def _calculate_bollinger_bands(self, prices: pd.Series):
        """Calculate Bollinger Bands."""
        sma = prices.rolling(window=self.period).mean()
        std = prices.rolling(window=self.period).std()

        upper_band = sma + (std * float(self.std_dev))
        lower_band = sma - (std * float(self.std_dev))

        return sma, upper_band, lower_band

    async def generate_signals(
        self,
        symbol: str,
        market_data: pd.DataFrame,
        current_date: datetime,
        positions: dict[str, Any],
        **kwargs: Any,
    ) -> list[StrategySignal]:
        if len(market_data) < self.period:
            return []

        close_prices = market_data["close"]
        sma, upper_band, lower_band = self._calculate_bollinger_bands(close_prices)

        current_price = Decimal(str(close_prices.iloc[-1]))
        current_lower = Decimal(str(lower_band.iloc[-1]))
        current_upper = Decimal(str(upper_band.iloc[-1]))

        # Buy signal: price touches or goes below lower band
        if current_price <= current_lower:
            portfolio_value = kwargs.get("portfolio_value", Decimal("10000"))
            position_size = portfolio_value * Decimal("0.1")
            quantity = position_size / current_price

            # Calculate how far below lower band (for confidence)
            deviation = (current_lower - current_price) / current_lower
            confidence = min(Decimal("0.9"), Decimal("0.5") + deviation * Decimal("2"))

            signal = StrategySignal(
                symbol=symbol,
                side="buy",
                quantity=quantity,
                price=current_price,
                confidence=confidence,
                take_profit=Decimal(str(sma.iloc[-1])),  # Target mean
                stop_loss=current_price * Decimal("0.95"),  # 5% stop loss
                metadata={
                    "strategy": self.name,
                    "lower_band": float(current_lower),
                    "sma": float(sma.iloc[-1]),
                    "deviation": float(deviation)
                }
            )

            if self.validate_signal(signal):
                return [signal]

        return []

    def fit_day(
        self,
        today: pd.Series,
        market_data: pd.DataFrame,
        **kwargs: Any,
    ) -> Optional[StrategySignal]:
        import asyncio

        symbol = kwargs.get("symbol", "UNKNOWN")
        current_date = kwargs.get("current_date", datetime.now())
        positions = kwargs.get("positions", {})

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        signals = loop.run_until_complete(
            self.generate_signals(
                symbol=symbol,
                market_data=market_data,
                current_date=current_date,
                positions=positions,
                **kwargs
            )
        )

        return signals[0] if signals else None
```

## Legacy ABU Integration

### Using Strategies with Legacy ABU System

```python
from crypto_quant_pro.core.strategies import (
    MovingAverageCrossStrategy,
    AbuBuyFactorAdapter,
    StopLossStrategy,
    AbuSellFactorAdapter
)
from abupy import run_loop_back

# Create new strategies
buy_strategy = MovingAverageCrossStrategy(fast_period=10, slow_period=30)
sell_strategy = StopLossStrategy(stop_loss_pct=Decimal("0.05"))

# Wrap with adapters for legacy compatibility
def create_buy_factor(capital, kl_pd, combine_kl_pd, benchmark, **kwargs):
    return AbuBuyFactorAdapter(
        strategy=buy_strategy,
        capital=capital,
        kl_pd=kl_pd,
        combine_kl_pd=combine_kl_pd,
        benchmark=benchmark,
        **kwargs
    )

def create_sell_factor(capital, kl_pd, combine_kl_pd, benchmark, **kwargs):
    return AbuSellFactorAdapter(
        strategy=sell_strategy,
        capital=capital,
        kl_pd=kl_pd,
        combine_kl_pd=combine_kl_pd,
        benchmark=benchmark,
        **kwargs
    )

# Use in legacy backtest
buy_factors = [{"class": create_buy_factor}]
sell_factors = [{"class": create_sell_factor}]

result = run_loop_back(
    read_cash=100000,
    buy_factors=buy_factors,
    sell_factors=sell_factors,
    choice_symbols=["BTC/USD", "ETH/USD"]
)
```

## Strategy Registry Usage

### Registering and Using Custom Strategies

```python
from crypto_quant_pro.core.strategies import StrategyRegistry
from crypto_quant_pro.core.strategies.base import BaseStrategy

# Register custom strategy
@StrategyRegistry.register("my_custom_strategy")
class MyCustomStrategy(BaseStrategy):
    # ... implementation

# Or register directly
StrategyRegistry.register("momentum", MomentumStrategy)

# Retrieve and use
strategy = StrategyRegistry.get("my_custom_strategy", param1=10, param2=20)

# List all strategies
all_strategies = StrategyRegistry.list_all()
print(f"Available strategies: {all_strategies}")

# Check if strategy exists
if StrategyRegistry.exists("momentum"):
    strategy = StrategyRegistry.get("momentum")
```
