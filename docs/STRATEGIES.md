# Strategy System Documentation

## Overview

The strategy system in `crypto_quant_pro` provides a flexible and extensible framework for implementing trading strategies. It supports both modern async-based signal generation and legacy compatibility with the ABU quantitative trading framework.

## Architecture

### Core Components

1. **BaseStrategy** - Abstract base class for all strategies
2. **StrategySignal** - Data structure representing trading signals
3. **StrategyRegistry** - Central registry for strategy management
4. **Buy Strategies** - Strategies for generating buy signals
5. **Sell Strategies** - Strategies for generating sell signals
6. **Legacy Adapters** - Compatibility layer for ABU framework

## Base Strategy

### BaseStrategy Class

All strategies inherit from `BaseStrategy`, which provides:

- **Direction Support**: CALL (bullish) or PUT (bearish)
- **Signal Generation**: Async method for generating trading signals
- **Legacy Compatibility**: `fit_day()` method for ABU compatibility
- **Signal Validation**: Built-in validation for generated signals

```python
from crypto_quant_pro.core.strategies import BaseStrategy, StrategyDirection
from datetime import datetime
from decimal import Decimal
import pandas as pd

class MyStrategy(BaseStrategy):
    async def generate_signals(
        self,
        symbol: str,
        market_data: pd.DataFrame,
        current_date: datetime,
        positions: dict[str, Any],
        **kwargs: Any,
    ) -> list[StrategySignal]:
        # Implement signal generation logic
        return []

    def fit_day(
        self,
        today: pd.Series,
        market_data: pd.DataFrame,
        **kwargs: Any,
    ) -> Optional[StrategySignal]:
        # Legacy compatibility implementation
        return None
```

### StrategySignal

A `StrategySignal` represents a trading signal with the following attributes:

- `symbol`: Trading symbol (e.g., "BTC/USD")
- `side`: "buy" or "sell"
- `quantity`: Optional quantity to trade
- `price`: Optional price (None for market orders)
- `confidence`: Confidence level (0.0 to 1.0)
- `stop_loss`: Optional stop loss price
- `take_profit`: Optional take profit price
- `metadata`: Additional strategy-specific data

## Buy Strategies

### MovingAverageCrossStrategy

Generates buy signals when a fast moving average crosses above a slow moving average (golden cross).

**Parameters:**
- `fast_period` (int): Fast MA period (default: 10)
- `slow_period` (int): Slow MA period (default: 30)

**Example:**
```python
from crypto_quant_pro.core.strategies import MovingAverageCrossStrategy

strategy = MovingAverageCrossStrategy(
    fast_period=10,
    slow_period=30,
    name="MA_Cross_10_30"
)

signals = await strategy.generate_signals(
    symbol="BTC/USD",
    market_data=market_data_df,
    current_date=datetime.now(),
    positions={},
    portfolio_value=Decimal("10000")
)
```

### BreakoutStrategy

Generates buy signals when price breaks above a resistance level.

**Parameters:**
- `lookback_period` (int): Period to calculate resistance (default: 20)
- `breakout_threshold` (Decimal): Percentage above resistance to trigger (default: 0.02 = 2%)

**Example:**
```python
from crypto_quant_pro.core.strategies import BreakoutStrategy
from decimal import Decimal

strategy = BreakoutStrategy(
    lookback_period=20,
    breakout_threshold=Decimal("0.02"),
    name="Breakout_20"
)
```

### RSIStrategy

Generates buy signals when RSI crosses above oversold level.

**Parameters:**
- `period` (int): RSI calculation period (default: 14)
- `oversold_level` (Decimal): RSI level considered oversold (default: 30)
- `overbought_level` (Decimal): RSI level considered overbought (default: 70)

**Example:**
```python
from crypto_quant_pro.core.strategies import RSIStrategy

strategy = RSIStrategy(
    period=14,
    oversold_level=Decimal("30"),
    name="RSI_14"
)
```

## Sell Strategies

### StopLossStrategy

Generates sell signals when price falls below stop loss level.

**Parameters:**
- `stop_loss_pct` (Decimal): Stop loss percentage (default: 0.05 = 5%)

**Example:**
```python
from crypto_quant_pro.core.strategies import StopLossStrategy

strategy = StopLossStrategy(
    stop_loss_pct=Decimal("0.05"),
    name="StopLoss_5pct"
)
```

### TakeProfitStrategy

Generates sell signals when price reaches take profit level.

**Parameters:**
- `take_profit_pct` (Decimal): Take profit percentage (default: 0.10 = 10%)

**Example:**
```python
from crypto_quant_pro.core.strategies import TakeProfitStrategy

strategy = TakeProfitStrategy(
    take_profit_pct=Decimal("0.10"),
    name="TakeProfit_10pct"
)
```

### TrailingStopStrategy

Generates sell signals when price falls below trailing stop level. The stop level moves up as price increases but doesn't move down.

**Parameters:**
- `trailing_pct` (Decimal): Trailing stop percentage (default: 0.05 = 5%)

**Example:**
```python
from crypto_quant_pro.core.strategies import TrailingStopStrategy

strategy = TrailingStopStrategy(
    trailing_pct=Decimal("0.05"),
    name="TrailingStop_5pct"
)
```

## Strategy Registry

The `StrategyRegistry` provides a centralized way to register, discover, and retrieve strategies.

### Registering Strategies

**Using Decorator:**
```python
from crypto_quant_pro.core.strategies import StrategyRegistry, BaseStrategy

@StrategyRegistry.register()
class MyStrategy(BaseStrategy):
    # ... implementation
```

**Direct Registration:**
```python
from crypto_quant_pro.core.strategies import StrategyRegistry, MovingAverageCrossStrategy

StrategyRegistry.register("MA_Cross", MovingAverageCrossStrategy)
```

**With Custom Name:**
```python
@StrategyRegistry.register("custom_name")
class MyStrategy(BaseStrategy):
    # ... implementation
```

### Retrieving Strategies

```python
from crypto_quant_pro.core.strategies import StrategyRegistry

# Get strategy instance
strategy = StrategyRegistry.get("MA_Cross", fast_period=10, slow_period=30)

# List all registered strategies
all_strategies = StrategyRegistry.list_all()

# Check if strategy exists
if StrategyRegistry.exists("MA_Cross"):
    strategy = StrategyRegistry.get("MA_Cross")
```

## Legacy Compatibility

### AbuBuyFactorAdapter

Allows new strategies to work with the legacy ABU backtesting system.

```python
from crypto_quant_pro.core.strategies import AbuBuyFactorAdapter, MovingAverageCrossStrategy

# Create strategy
strategy = MovingAverageCrossStrategy(fast_period=10, slow_period=30)

# Wrap with adapter
adapter = AbuBuyFactorAdapter(
    strategy=strategy,
    capital=capital_object,
    kl_pd=market_data_df,
    combine_kl_pd=combined_data_df,
    benchmark=benchmark_object
)

# Use in legacy backtest
order = adapter.read_fit_day(today_data)
```

### AbuSellFactorAdapter

Allows new sell strategies to work with legacy sell factor system.

```python
from crypto_quant_pro.core.strategies import AbuSellFactorAdapter, StopLossStrategy

strategy = StopLossStrategy(stop_loss_pct=Decimal("0.05"))
adapter = AbuSellFactorAdapter(
    strategy=strategy,
    capital=capital_object,
    kl_pd=market_data_df,
    combine_kl_pd=combined_data_df,
    benchmark=benchmark_object
)

# Evaluate sell signal
should_sell = adapter.fit_sell(order, today_data)
```

## Usage Examples

### Basic Strategy Usage

```python
import asyncio
from datetime import datetime
from decimal import Decimal
import pandas as pd
from crypto_quant_pro.core.strategies import MovingAverageCrossStrategy

async def main():
    # Create strategy
    strategy = MovingAverageCrossStrategy(
        fast_period=10,
        slow_period=30
    )

    # Prepare market data
    market_data = pd.DataFrame({
        "date": pd.date_range("2024-01-01", periods=50, freq="D"),
        "open": [100 + i * 0.5 for i in range(50)],
        "high": [101 + i * 0.5 for i in range(50)],
        "low": [99 + i * 0.5 for i in range(50)],
        "close": [100 + i * 0.5 for i in range(50)],
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
        print(f"Signal: {signal.side} {signal.quantity} {signal.symbol} at {signal.price}")

asyncio.run(main())
```

### Using with Backtesting Engine

```python
from crypto_quant_pro.core.engines import BacktestingEngine, BacktestConfig
from crypto_quant_pro.core.strategies import MovingAverageCrossStrategy
from crypto_quant_pro.data.feeds import BinanceFeed
from datetime import datetime, timedelta
from decimal import Decimal

# Create strategy
strategy = MovingAverageCrossStrategy(fast_period=10, slow_period=30)

# Create backtest config
config = BacktestConfig(
    start_date=datetime.now() - timedelta(days=365),
    end_date=datetime.now(),
    initial_capital=Decimal("10000")
)

# Create data feed
data_feed = BinanceFeed()

# Create backtesting engine
engine = BacktestingEngine(config, data_feed)

# Define strategy function
async def strategy_func(engine, current_date):
    for symbol in ["BTC/USD", "ETH/USD"]:
        market_data = engine.market_data_cache.get(symbol)
        if market_data is not None:
            signals = await strategy.generate_signals(
                symbol=symbol,
                market_data=market_data,
                current_date=current_date,
                positions=engine.positions,
                portfolio_value=engine.portfolio_value
            )
            for signal in signals:
                if signal.side == "buy":
                    await engine.place_order(signal)

# Run backtest
result = await engine.run_backtest(strategy_func, ["BTC/USD", "ETH/USD"])
print(f"Total Return: {result.total_return:.2%}")
print(f"Sharpe Ratio: {result.sharpe_ratio:.2f}")
```

### Combining Buy and Sell Strategies

```python
from crypto_quant_pro.core.strategies import (
    MovingAverageCrossStrategy,
    StopLossStrategy,
    TakeProfitStrategy
)

# Create strategies
buy_strategy = MovingAverageCrossStrategy(fast_period=10, slow_period=30)
stop_loss = StopLossStrategy(stop_loss_pct=Decimal("0.05"))
take_profit = TakeProfitStrategy(take_profit_pct=Decimal("0.10"))

# In your trading loop
async def trading_loop():
    # Check for buy signals
    buy_signals = await buy_strategy.generate_signals(...)

    # Check for sell signals on existing positions
    for symbol, position in positions.items():
        stop_loss_signals = await stop_loss.generate_signals(
            symbol=symbol,
            market_data=market_data,
            current_date=current_date,
            positions={symbol: position}
        )

        take_profit_signals = await take_profit.generate_signals(
            symbol=symbol,
            market_data=market_data,
            current_date=current_date,
            positions={symbol: position}
        )

        # Execute sell if either signal triggered
        if stop_loss_signals or take_profit_signals:
            # Execute sell order
            pass
```

## Creating Custom Strategies

### Example: Simple Momentum Strategy

```python
from crypto_quant_pro.core.strategies import BaseStrategy, StrategySignal, StrategyDirection
from datetime import datetime
from decimal import Decimal
import pandas as pd
from typing import Any, Optional

class MomentumStrategy(BaseStrategy):
    """Simple momentum strategy based on price change."""

    def __init__(self, lookback_period: int = 5, threshold: Decimal = Decimal("0.02"), **kwargs):
        name = kwargs.pop("name", f"Momentum_{lookback_period}")
        super().__init__(name=name, direction=StrategyDirection.CALL, **kwargs)
        self.lookback_period = lookback_period
        self.threshold = threshold

    async def generate_signals(
        self,
        symbol: str,
        market_data: pd.DataFrame,
        current_date: datetime,
        positions: dict[str, Any],
        **kwargs: Any,
    ) -> list[StrategySignal]:
        if len(market_data) < self.lookback_period:
            return []

        # Calculate price change over lookback period
        current_price = Decimal(str(market_data["close"].iloc[-1]))
        past_price = Decimal(str(market_data["close"].iloc[-self.lookback_period]))
        price_change = (current_price - past_price) / past_price

        # Generate buy signal if momentum is strong
        if price_change >= self.threshold:
            portfolio_value = kwargs.get("portfolio_value", Decimal("10000"))
            position_size = portfolio_value * Decimal("0.1")
            quantity = position_size / current_price

            signal = StrategySignal(
                symbol=symbol,
                side="buy",
                quantity=quantity,
                price=current_price,
                confidence=Decimal("0.7"),
                metadata={
                    "strategy": self.name,
                    "price_change": float(price_change),
                    "lookback_period": self.lookback_period
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

## Best Practices

1. **Always validate signals**: Use `validate_signal()` before executing trades
2. **Use Decimal for financial calculations**: Avoid floating-point precision issues
3. **Handle edge cases**: Check for sufficient data before calculations
4. **Document strategy parameters**: Clearly document what each parameter does
5. **Test strategies thoroughly**: Write unit tests for your strategies
6. **Use confidence levels**: Set appropriate confidence levels for signals
7. **Include metadata**: Add useful metadata to signals for debugging and analysis

## Testing

All strategies should include comprehensive unit tests. See `tests/unit/test_crypto_quant_pro/core/strategies/` for examples.

Example test structure:
```python
import pytest
from datetime import datetime
from decimal import Decimal
import pandas as pd
from crypto_quant_pro.core.strategies import MyStrategy

@pytest.mark.asyncio
async def test_my_strategy():
    strategy = MyStrategy(param1=10, param2=20)

    market_data = create_test_market_data()

    signals = await strategy.generate_signals(
        symbol="BTC/USD",
        market_data=market_data,
        current_date=datetime.now(),
        positions={}
    )

    assert isinstance(signals, list)
    # Add more assertions
```

## Performance Considerations

1. **Cache calculations**: Cache expensive calculations when possible
2. **Vectorize operations**: Use pandas/numpy vectorized operations
3. **Limit data lookback**: Only use necessary historical data
4. **Async operations**: Use async for I/O-bound operations
5. **Profile strategies**: Profile strategies to identify bottlenecks

## Troubleshooting

### Common Issues

1. **No signals generated**: Check if market data has sufficient length
2. **Invalid signals**: Ensure signal validation passes
3. **Legacy compatibility**: Use adapters for ABU compatibility
4. **Async errors**: Ensure proper event loop handling in `fit_day()`

### Debug Tips

- Enable logging to see strategy execution
- Check signal metadata for debugging information
- Validate market data format before processing
- Test strategies with known data sets
