"""
Adapter for compatibility with legacy MetricsBu module.

Provides a bridge between the new metrics system and
the legacy ABU MetricsBu interface.
"""

from decimal import Decimal
import logging
from typing import Any, Optional

from .performance_calculator import PerformanceCalculator
from .report_generator import ReportGenerator
from .risk_metrics import RiskMetricsCalculator

logger = logging.getLogger(__name__)


class AbuMetricsAdapter:
    """
    Adapter to provide MetricsBu-compatible interface.

    Wraps the new metrics components to maintain compatibility
    with legacy ABU code.
    """

    def __init__(self, risk_free_rate: Decimal = Decimal("0.02")):
        """
        Initialize metrics adapter.

        Args:
            risk_free_rate: Annual risk-free rate
        """
        self.performance_calculator = PerformanceCalculator(risk_free_rate)
        self.risk_calculator = RiskMetricsCalculator()
        self.report_generator = ReportGenerator(risk_free_rate)

    def calculate_performance(
        self,
        equity_curve: list[Any],
        trades: Optional[list[dict[str, Any]]] = None,
        timestamps: Optional[list] = None,
    ) -> dict[str, Any]:
        """
        Calculate performance metrics (MetricsBu compatibility).

        Args:
            equity_curve: List of portfolio values
            trades: Optional list of trades
            timestamps: Optional list of timestamps

        Returns:
            Dictionary with performance metrics
        """
        # Convert to Decimal if needed
        equity_decimal = [
            Decimal(str(v)) if not isinstance(v, Decimal) else v for v in equity_curve
        ]

        metrics = self.performance_calculator.calculate(equity_decimal, trades, timestamps)

        return {
            "total_return": float(metrics.total_return),
            "annualized_return": float(metrics.annualized_return),
            "volatility": float(metrics.volatility),
            "sharpe_ratio": float(metrics.sharpe_ratio),
            "sortino_ratio": float(metrics.sortino_ratio),
            "calmar_ratio": float(metrics.calmar_ratio),
            "max_drawdown": float(metrics.max_drawdown),
            "max_drawdown_duration": metrics.max_drawdown_duration,
            "win_rate": float(metrics.win_rate),
            "profit_factor": float(metrics.profit_factor),
            "total_trades": metrics.total_trades,
            "winning_trades": metrics.winning_trades,
            "losing_trades": metrics.losing_trades,
        }

    def calculate_risk(
        self,
        portfolio_returns: Any,
        market_returns: Optional[Any] = None,
        positions: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Calculate risk metrics (MetricsBu compatibility).

        Args:
            portfolio_returns: Series of portfolio returns
            market_returns: Optional market benchmark returns
            positions: Optional dictionary of positions

        Returns:
            Dictionary with risk metrics
        """
        import pandas as pd

        if not isinstance(portfolio_returns, pd.Series):
            portfolio_returns = pd.Series(portfolio_returns)

        risk_metrics = self.risk_calculator.calculate_portfolio_risk(
            portfolio_returns, market_returns, positions
        )

        return {
            "var_95": float(risk_metrics.var_95),
            "var_99": float(risk_metrics.var_99),
            "cvar_95": float(risk_metrics.cvar_95),
            "cvar_99": float(risk_metrics.cvar_99),
            "portfolio_volatility": float(risk_metrics.portfolio_volatility),
            "beta": float(risk_metrics.beta),
            "concentration_risk": (
                float(risk_metrics.concentration_risk) if risk_metrics.concentration_risk else None
            ),
        }

    def generate_report(
        self,
        equity_curve: list[Any],
        portfolio_returns: Any,
        trades: Optional[list[dict[str, Any]]] = None,
        timestamps: Optional[list] = None,
        output_format: str = "text",
    ) -> str:
        """
        Generate performance report (MetricsBu compatibility).

        Args:
            equity_curve: List of portfolio values
            portfolio_returns: Series of portfolio returns
            trades: Optional list of trades
            timestamps: Optional list of timestamps
            output_format: Output format ('text', 'html', 'json')

        Returns:
            Formatted report string
        """
        self.report_generator.output_format = output_format

        equity_decimal = [
            Decimal(str(v)) if not isinstance(v, Decimal) else v for v in equity_curve
        ]

        return self.report_generator.generate_performance_report(equity_decimal, trades, timestamps)
