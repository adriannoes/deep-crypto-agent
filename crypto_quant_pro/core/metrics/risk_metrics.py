"""
Risk metrics calculator for trading portfolios.

Calculates various risk metrics including VaR, CVaR,
beta, correlation, and stress testing.
"""

from dataclasses import dataclass
from decimal import Decimal
import logging
from typing import Any, Optional

import pandas as pd

from ..risk.risk_calculator import RiskCalculator

logger = logging.getLogger(__name__)


@dataclass
class PortfolioRiskMetrics:
    """Comprehensive portfolio risk metrics."""

    var_95: Decimal
    var_99: Decimal
    cvar_95: Decimal
    cvar_99: Decimal
    portfolio_volatility: Decimal
    beta: Decimal
    correlation_matrix: Any
    max_leverage: Optional[Decimal] = None
    concentration_risk: Optional[Decimal] = None


class RiskMetricsCalculator:
    """
    Calculate comprehensive risk metrics for portfolios.

    Provides detailed risk analysis including VaR, CVaR,
    beta, correlation, and concentration metrics.
    """

    def __init__(self):
        """Initialize risk metrics calculator."""
        self.risk_calculator = RiskCalculator()

    def calculate_portfolio_risk(
        self,
        portfolio_returns: pd.Series,
        market_returns: Optional[pd.Series] = None,
        positions: Optional[dict[str, Any]] = None,
    ) -> PortfolioRiskMetrics:
        """
        Calculate comprehensive portfolio risk metrics.

        Args:
            portfolio_returns: Series of portfolio returns
            market_returns: Optional market benchmark returns
            positions: Optional dictionary of positions

        Returns:
            PortfolioRiskMetrics with all risk metrics
        """
        if len(portfolio_returns) == 0:
            raise ValueError("Empty returns series")

        # VaR and CVaR
        var_95 = self.risk_calculator.calculate_var(
            portfolio_returns, confidence_level=Decimal("0.95")
        )
        var_99 = self.risk_calculator.calculate_var(
            portfolio_returns, confidence_level=Decimal("0.99")
        )
        cvar_95 = self.risk_calculator.calculate_cvar(
            portfolio_returns, confidence_level=Decimal("0.95")
        )
        cvar_99 = self.risk_calculator.calculate_cvar(
            portfolio_returns, confidence_level=Decimal("0.99")
        )

        # Portfolio volatility
        portfolio_volatility = self.risk_calculator.calculate_volatility(
            portfolio_returns, annualized=True
        )

        # Beta (if market returns provided)
        beta = Decimal("0")
        if market_returns is not None and len(market_returns) > 0:
            beta = self.risk_calculator.calculate_beta(portfolio_returns, market_returns)

        # Correlation matrix (if multiple assets)
        correlation_matrix = None
        if positions and len(positions) > 1:
            # Would need individual asset returns for correlation
            # For now, return None
            pass

        # Concentration risk
        concentration_risk = None
        if positions:
            concentration_risk = self._calculate_concentration_risk(positions)

        return PortfolioRiskMetrics(
            var_95=var_95,
            var_99=var_99,
            cvar_95=cvar_95,
            cvar_99=cvar_99,
            portfolio_volatility=portfolio_volatility,
            beta=beta,
            correlation_matrix=correlation_matrix,
            concentration_risk=concentration_risk,
        )

    def calculate_stress_scenarios(
        self,
        portfolio_returns: pd.Series,
        stress_levels: list[Decimal] = None,
    ) -> dict[str, Decimal]:
        """
        Calculate portfolio performance under stress scenarios.

        Args:
            portfolio_returns: Series of portfolio returns
            stress_levels: List of stress levels (e.g., -0.1 for -10%)

        Returns:
            Dictionary mapping stress levels to portfolio impacts
        """
        if stress_levels is None:
            stress_levels = [
                Decimal("-0.05"),
                Decimal("-0.10"),
                Decimal("-0.20"),
                Decimal("-0.30"),
            ]

        results = {}
        for stress_level in stress_levels:
            # Simulate stress: shift returns by stress level
            stressed_returns = portfolio_returns + float(stress_level)
            stressed_var = self.risk_calculator.calculate_var(
                pd.Series(stressed_returns), confidence_level=Decimal("0.95")
            )
            results[str(stress_level)] = stressed_var

        return results

    def calculate_leverage_metrics(
        self, positions: dict[str, Any], total_capital: Decimal
    ) -> dict[str, Decimal]:
        """
        Calculate leverage-related metrics.

        Args:
            positions: Dictionary of positions
            total_capital: Total capital available

        Returns:
            Dictionary with leverage metrics
        """
        total_position_value = sum(
            p.get("market_value", Decimal("0"))
            if isinstance(p.get("market_value"), Decimal)
            else Decimal(str(p.get("market_value", 0)))
            for p in positions.values()
        )

        leverage = total_position_value / total_capital if total_capital > 0 else Decimal("0")

        return {
            "total_leverage": leverage,
            "total_position_value": total_position_value,
            "available_capital": total_capital - total_position_value,
        }

    def _calculate_concentration_risk(self, positions: dict[str, Any]) -> Decimal:
        """
        Calculate concentration risk using Herfindahl-Hirschman Index.

        Args:
            positions: Dictionary of positions

        Returns:
            HHI concentration index (0-1, higher = more concentrated)
        """
        if not positions:
            return Decimal("0")

        total_value = sum(
            p.get("market_value", Decimal("0"))
            if isinstance(p.get("market_value"), Decimal)
            else Decimal(str(p.get("market_value", 0)))
            for p in positions.values()
        )

        if total_value == 0:
            return Decimal("0")

        # Calculate HHI
        hhi = Decimal("0")
        for position in positions.values():
            value = (
                position.get("market_value", Decimal("0"))
                if isinstance(position.get("market_value"), Decimal)
                else Decimal(str(position.get("market_value", 0)))
            )
            weight = value / total_value
            hhi += weight * weight

        return hhi
