"""Risk calculation and metrics."""
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Optional

import numpy as np
import pandas as pd

from ..engines.models import Position


@dataclass
class RiskMetrics:
    """Risk metrics for a portfolio or position."""

    var_95: Decimal  # Value at Risk (95% confidence)
    var_99: Decimal  # Value at Risk (99% confidence)
    cvar_95: Decimal  # Conditional VaR (95% confidence)
    portfolio_volatility: Decimal  # Portfolio volatility
    max_drawdown: Decimal  # Maximum drawdown
    sharpe_ratio: Decimal  # Sharpe ratio
    sortino_ratio: Decimal  # Sortino ratio
    beta: Decimal  # Beta (market correlation)
    correlation_matrix: Any  # Correlation matrix


class RiskCalculator:
    """
    Calculate risk metrics for positions and portfolios.

    Provides various risk calculations including VaR, CVaR, volatility, and drawdown.
    """

    def __init__(self):
        """Initialize risk calculator."""
        pass

    def calculate_var(
        self,
        returns: pd.Series,
        confidence_level: Decimal = Decimal("0.95"),
    ) -> Decimal:
        """
        Calculate Value at Risk (VaR).

        Args:
            returns: Series of returns
            confidence_level: Confidence level (e.g., 0.95 for 95%)

        Returns:
            VaR value
        """
        if len(returns) == 0:
            return Decimal("0")

        var_value = np.percentile(returns, float((1 - confidence_level) * 100))
        return Decimal(str(abs(var_value)))

    def calculate_cvar(
        self,
        returns: pd.Series,
        confidence_level: Decimal = Decimal("0.95"),
    ) -> Decimal:
        """
        Calculate Conditional Value at Risk (CVaR).

        Args:
            returns: Series of returns
            confidence_level: Confidence level (e.g., 0.95 for 95%)

        Returns:
            CVaR value
        """
        if len(returns) == 0:
            return Decimal("0")

        var_value = np.percentile(returns, float((1 - confidence_level) * 100))
        cvar_value = returns[returns <= var_value].mean()
        return Decimal(str(abs(cvar_value)))

    def calculate_volatility(self, returns: pd.Series, annualized: bool = True) -> Decimal:
        """
        Calculate volatility (standard deviation of returns).

        Args:
            returns: Series of returns
            annualized: Whether to annualize the volatility

        Returns:
            Volatility value
        """
        if len(returns) == 0:
            return Decimal("0")

        volatility = returns.std()
        if annualized:
            # Annualize assuming 252 trading days
            volatility = volatility * np.sqrt(252)

        return Decimal(str(volatility))

    def calculate_sharpe_ratio(
        self,
        returns: pd.Series,
        risk_free_rate: Decimal = Decimal("0.02"),  # 2% risk-free rate
    ) -> Decimal:
        """
        Calculate Sharpe ratio.

        Args:
            returns: Series of returns
            risk_free_rate: Risk-free rate (annualized)

        Returns:
            Sharpe ratio
        """
        if len(returns) == 0:
            return Decimal("0")

        mean_return = returns.mean()
        volatility = self.calculate_volatility(returns, annualized=True)

        if volatility == 0:
            return Decimal("0")

        # Annualize mean return
        annualized_return = mean_return * 252
        sharpe = (Decimal(str(annualized_return)) - risk_free_rate) / volatility

        return Decimal(str(sharpe))

    def calculate_sortino_ratio(
        self,
        returns: pd.Series,
        risk_free_rate: Decimal = Decimal("0.02"),
    ) -> Decimal:
        """
        Calculate Sortino ratio (downside deviation only).

        Args:
            returns: Series of returns
            risk_free_rate: Risk-free rate (annualized)

        Returns:
            Sortino ratio
        """
        if len(returns) == 0:
            return Decimal("0")

        mean_return = returns.mean()
        downside_returns = returns[returns < 0]
        downside_std = downside_returns.std() if len(downside_returns) > 0 else Decimal("0.001")

        if downside_std == 0:
            return Decimal("0")

        # Annualize
        annualized_return = mean_return * 252
        sortino = (Decimal(str(annualized_return)) - risk_free_rate) / (
            Decimal(str(downside_std)) * Decimal(str(np.sqrt(252)))
        )

        return Decimal(str(sortino))

    def calculate_max_drawdown(self, equity_curve: list[Decimal]) -> Decimal:
        """
        Calculate maximum drawdown.

        Args:
            equity_curve: List of portfolio values over time

        Returns:
            Maximum drawdown as percentage
        """
        if len(equity_curve) < 2:
            return Decimal("0")

        equity_array = np.array([float(v) for v in equity_curve])
        peak = np.maximum.accumulate(equity_array)
        drawdown = (equity_array - peak) / peak
        max_dd = abs(np.min(drawdown))

        return Decimal(str(max_dd))

    def calculate_beta(
        self,
        portfolio_returns: pd.Series,
        market_returns: pd.Series,
    ) -> Decimal:
        """
        Calculate beta (market correlation).

        Args:
            portfolio_returns: Portfolio returns
            market_returns: Market benchmark returns

        Returns:
            Beta value
        """
        if len(portfolio_returns) == 0 or len(market_returns) == 0:
            return Decimal("1.0")

        # Align series
        aligned = pd.DataFrame({"portfolio": portfolio_returns, "market": market_returns}).dropna()

        if len(aligned) < 2:
            return Decimal("1.0")

        covariance = aligned["portfolio"].cov(aligned["market"])
        market_variance = aligned["market"].var()

        if market_variance == 0:
            return Decimal("1.0")

        beta = covariance / market_variance
        return Decimal(str(beta))

    def calculate_correlation_matrix(self, returns_df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate correlation matrix for multiple assets.

        Args:
            returns_df: DataFrame with returns for multiple assets

        Returns:
            Correlation matrix
        """
        return returns_df.corr()

    def calculate_portfolio_risk_metrics(
        self,
        positions: dict[str, Position],
        historical_returns: dict[str, pd.Series],
        equity_curve: list[Decimal],
        market_returns: Optional[pd.Series] = None,
    ) -> RiskMetrics:
        """
        Calculate comprehensive risk metrics for a portfolio.

        Args:
            positions: Dictionary of positions
            historical_returns: Historical returns for each symbol
            equity_curve: Portfolio equity curve
            market_returns: Optional market benchmark returns

        Returns:
            RiskMetrics object
        """
        # Calculate portfolio returns
        if len(equity_curve) < 2:
            portfolio_returns = pd.Series([Decimal("0")])
        else:
            portfolio_values = [float(v) for v in equity_curve]
            portfolio_returns = pd.Series(portfolio_values).pct_change().dropna()

        # Calculate VaR
        var_95 = self.calculate_var(portfolio_returns, Decimal("0.95"))
        var_99 = self.calculate_var(portfolio_returns, Decimal("0.99"))

        # Calculate CVaR
        cvar_95 = self.calculate_cvar(portfolio_returns, Decimal("0.95"))

        # Calculate volatility
        portfolio_volatility = self.calculate_volatility(portfolio_returns)

        # Calculate max drawdown
        max_drawdown = self.calculate_max_drawdown(equity_curve)

        # Calculate Sharpe ratio
        sharpe_ratio = self.calculate_sharpe_ratio(portfolio_returns)

        # Calculate Sortino ratio
        sortino_ratio = self.calculate_sortino_ratio(portfolio_returns)

        # Calculate beta
        if market_returns is not None:
            beta = self.calculate_beta(portfolio_returns, market_returns)
        else:
            beta = Decimal("1.0")

        # Calculate correlation matrix
        if historical_returns:
            returns_df = pd.DataFrame(historical_returns)
            correlation_matrix = self.calculate_correlation_matrix(returns_df)
        else:
            correlation_matrix = pd.DataFrame()

        return RiskMetrics(
            var_95=var_95,
            var_99=var_99,
            cvar_95=cvar_95,
            portfolio_volatility=portfolio_volatility,
            max_drawdown=max_drawdown,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            beta=beta,
            correlation_matrix=correlation_matrix,
        )
