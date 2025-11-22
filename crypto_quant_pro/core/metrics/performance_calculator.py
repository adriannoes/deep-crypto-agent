"""
Performance metrics calculator for trading strategies.

Calculates comprehensive performance metrics including
returns, Sharpe ratio, drawdown, and more.
"""

from dataclasses import dataclass
import decimal
from decimal import Decimal
import logging
from typing import Any, Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Comprehensive performance metrics."""

    total_return: Decimal
    annualized_return: Decimal
    volatility: Decimal
    sharpe_ratio: Decimal
    sortino_ratio: Decimal
    calmar_ratio: Decimal
    max_drawdown: Decimal
    max_drawdown_duration: int  # Days
    win_rate: Decimal
    profit_factor: Decimal
    average_win: Decimal
    average_loss: Decimal
    total_trades: int
    winning_trades: int
    losing_trades: int
    average_trade_duration: Optional[Decimal] = None  # Days


class PerformanceCalculator:
    """
    Calculate comprehensive performance metrics.

    Provides detailed analysis of trading strategy performance
    including risk-adjusted returns and trade statistics.
    """

    def __init__(self, risk_free_rate: Decimal = Decimal("0.02")):
        """
        Initialize performance calculator.

        Args:
            risk_free_rate: Annual risk-free rate (default 2%)
        """
        self.risk_free_rate = risk_free_rate

    def calculate(
        self,
        equity_curve: list[Decimal],
        trades: Optional[list[dict[str, Any]]] = None,
        timestamps: Optional[list] = None,
    ) -> PerformanceMetrics:
        """
        Calculate comprehensive performance metrics.

        Args:
            equity_curve: List of portfolio values over time
            trades: Optional list of trade dictionaries
            timestamps: Optional list of timestamps

        Returns:
            PerformanceMetrics with all calculated metrics
        """
        if len(equity_curve) < 2:
            raise ValueError("Need at least 2 equity values")

        # Convert to pandas Series for easier calculations
        equity_floats = [float(e) for e in equity_curve]
        equity_series = pd.Series(equity_floats)

        if timestamps:
            equity_series.index = timestamps[: len(equity_series)]

        # Calculate returns
        returns = equity_series.pct_change().dropna()

        # Total return
        initial_value = equity_curve[0]
        final_value = equity_curve[-1]
        total_return = (final_value - initial_value) / initial_value

        # Annualized return

        if timestamps and len(timestamps) > 1:
            try:
                days = (timestamps[-1] - timestamps[0]).days
                if days > 0 and total_return != Decimal("-1"):
                    # Use float for exponentiation, then convert back
                    annualized_float = (1.0 + float(total_return)) ** (365.0 / days) - 1.0
                    annualized_return = Decimal(str(annualized_float))
                else:
                    annualized_return = Decimal("0")
            except (TypeError, AttributeError, ValueError):
                # Fallback if timestamp calculation fails
                periods = len(equity_curve) - 1
                if periods > 0 and total_return != Decimal("-1"):
                    annualized_float = (1.0 + float(total_return)) ** (365.0 / periods) - 1.0
                    annualized_return = Decimal(str(annualized_float))
                else:
                    annualized_return = Decimal("0")
        else:
            # Estimate from number of periods (assume daily)
            periods = len(equity_curve) - 1
            if periods > 0 and total_return != Decimal("-1"):
                try:
                    annualized_float = (1.0 + float(total_return)) ** (365.0 / periods) - 1.0
                    annualized_return = Decimal(str(annualized_float))
                except (ValueError, OverflowError):
                    annualized_return = total_return  # Fallback
            else:
                annualized_return = Decimal("0")

        # Volatility (annualized)
        if len(returns) > 0:
            volatility = Decimal(str(returns.std() * np.sqrt(252)))
        else:
            volatility = Decimal("0")

        # Sharpe ratio
        if volatility > 0:
            sharpe_ratio = (annualized_return - self.risk_free_rate) / volatility
        else:
            sharpe_ratio = Decimal("0")

        # Sortino ratio (downside deviation)
        downside_returns = returns[returns < 0]
        if len(downside_returns) > 0:
            try:
                downside_std_val = downside_returns.std() * np.sqrt(252)
                if not np.isnan(downside_std_val) and downside_std_val > 0:
                    downside_std = Decimal(str(downside_std_val))
                    sortino_ratio = (annualized_return - self.risk_free_rate) / downside_std
                else:
                    sortino_ratio = Decimal("0")
            except (ValueError, decimal.InvalidOperation):
                sortino_ratio = Decimal("0")
        else:
            sortino_ratio = Decimal("0")

        # Maximum drawdown
        rolling_max = equity_series.expanding().max()
        drawdowns = (equity_series - rolling_max) / rolling_max
        max_drawdown = Decimal(str(abs(drawdowns.min())))

        # Max drawdown duration
        max_drawdown_duration = self._calculate_drawdown_duration(equity_series, drawdowns)

        # Calmar ratio
        try:
            if max_drawdown > 0:
                calmar_ratio = annualized_return / max_drawdown
            else:
                calmar_ratio = Decimal("0")
        except (ZeroDivisionError, decimal.InvalidOperation):
            calmar_ratio = Decimal("0")

        # Trade statistics
        if trades:
            trade_stats = self._calculate_trade_stats(trades)
            win_rate = trade_stats["win_rate"]
            profit_factor = trade_stats["profit_factor"]
            average_win = trade_stats["average_win"]
            average_loss = trade_stats["average_loss"]
            total_trades = trade_stats["total_trades"]
            winning_trades = trade_stats["winning_trades"]
            losing_trades = trade_stats["losing_trades"]
            avg_duration = trade_stats.get("average_duration")
        else:
            win_rate = Decimal("0")
            profit_factor = Decimal("0")
            average_win = Decimal("0")
            average_loss = Decimal("0")
            total_trades = 0
            winning_trades = 0
            losing_trades = 0
            avg_duration = None

        return PerformanceMetrics(
            total_return=total_return,
            annualized_return=annualized_return,
            volatility=volatility,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            calmar_ratio=calmar_ratio,
            max_drawdown=max_drawdown,
            max_drawdown_duration=max_drawdown_duration,
            win_rate=win_rate,
            profit_factor=profit_factor,
            average_win=average_win,
            average_loss=average_loss,
            total_trades=total_trades,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            average_trade_duration=avg_duration,
        )

    def _calculate_drawdown_duration(self, equity_series: pd.Series, drawdowns: pd.Series) -> int:
        """Calculate maximum drawdown duration in days."""
        if len(drawdowns) == 0:
            return 0

        max_duration = 0
        current_duration = 0

        for dd in drawdowns:
            if dd < 0:
                current_duration += 1
                max_duration = max(max_duration, current_duration)
            else:
                current_duration = 0

        return max_duration

    def _calculate_trade_stats(self, trades: list[dict[str, Any]]) -> dict[str, Any]:
        """Calculate statistics from trade list."""
        if not trades:
            return {
                "win_rate": Decimal("0"),
                "profit_factor": Decimal("0"),
                "average_win": Decimal("0"),
                "average_loss": Decimal("0"),
                "total_trades": 0,
                "winning_trades": 0,
                "losing_trades": 0,
            }

        total_trades = len(trades)
        winning_trades = 0
        losing_trades = 0
        total_profit = Decimal("0")
        total_loss = Decimal("0")
        wins = []
        losses = []

        for trade in trades:
            pnl = trade.get("pnl", Decimal("0"))
            if not isinstance(pnl, Decimal):
                pnl = Decimal(str(pnl))

            if pnl > 0:
                winning_trades += 1
                total_profit += pnl
                wins.append(float(pnl))
            elif pnl < 0:
                losing_trades += 1
                total_loss += abs(pnl)
                losses.append(float(abs(pnl)))

        win_rate = (
            Decimal(str(winning_trades)) / Decimal(str(total_trades))
            if total_trades > 0
            else Decimal("0")
        )

        average_win = Decimal(str(np.mean(wins))) if wins else Decimal("0")
        average_loss = Decimal(str(np.mean(losses))) if losses else Decimal("0")

        profit_factor = total_profit / total_loss if total_loss > 0 else Decimal("0")

        # Calculate average trade duration if available
        durations = []
        for trade in trades:
            if "entry_time" in trade and "exit_time" in trade:
                duration = (trade["exit_time"] - trade["entry_time"]).days
                durations.append(duration)

        avg_duration = Decimal(str(np.mean(durations))) if durations else None

        return {
            "win_rate": win_rate,
            "profit_factor": profit_factor,
            "average_win": average_win,
            "average_loss": average_loss,
            "total_trades": total_trades,
            "winning_trades": winning_trades,
            "losing_trades": losing_trades,
            "average_duration": avg_duration,
        }
