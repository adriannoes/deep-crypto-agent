"""Portfolio optimization for risk management."""
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Optional

import numpy as np
import pandas as pd


class OptimizationMethod(Enum):
    """Portfolio optimization methods."""

    EQUAL_WEIGHT = "equal_weight"  # Equal weight allocation
    MARKOWITZ = "markowitz"  # Mean-variance optimization
    RISK_PARITY = "risk_parity"  # Risk parity allocation
    MIN_VARIANCE = "min_variance"  # Minimum variance portfolio
    MAX_SHARPE = "max_sharpe"  # Maximum Sharpe ratio


@dataclass
class OptimizationConfig:
    """Configuration for portfolio optimization."""

    method: OptimizationMethod = OptimizationMethod.EQUAL_WEIGHT
    risk_free_rate: Decimal = Decimal("0.02")  # Risk-free rate
    target_return: Optional[Decimal] = None  # Target return (for Markowitz)
    max_weight: Decimal = Decimal("0.3")  # Maximum weight per asset
    min_weight: Decimal = Decimal("0.05")  # Minimum weight per asset
    rebalance_frequency: str = "monthly"  # Rebalance frequency


class PortfolioOptimizer:
    """
    Optimizes portfolio allocation based on risk and return objectives.

    Provides various optimization methods including Markowitz, risk parity, and equal weight.
    """

    def __init__(self, config: OptimizationConfig):
        """
        Initialize portfolio optimizer.

        Args:
            config: Optimization configuration
        """
        self.config = config

    def optimize_equal_weight(
        self,
        symbols: list[str],
        portfolio_value: Decimal,
    ) -> dict[str, Decimal]:
        """
        Equal weight allocation.

        Args:
            symbols: List of symbols
            portfolio_value: Total portfolio value

        Returns:
            Dictionary of symbol -> allocation amount
        """
        if not symbols:
            return {}

        weight_per_symbol = Decimal("1") / Decimal(str(len(symbols)))
        allocation_per_symbol = portfolio_value * weight_per_symbol

        return {symbol: allocation_per_symbol for symbol in symbols}

    def optimize_markowitz(
        self,
        symbols: list[str],
        expected_returns: pd.Series,
        covariance_matrix: pd.DataFrame,
        portfolio_value: Decimal,
    ) -> dict[str, Decimal]:
        """
        Markowitz mean-variance optimization.

        Args:
            symbols: List of symbols
            expected_returns: Expected returns for each symbol
            covariance_matrix: Covariance matrix
            portfolio_value: Total portfolio value

        Returns:
            Dictionary of symbol -> allocation amount
        """
        try:
            from scipy.optimize import minimize
        except ImportError:
            # Fallback to equal weight if scipy not available
            return self.optimize_equal_weight(symbols, portfolio_value)

        n_assets = len(symbols)

        # Objective function: minimize portfolio variance
        def objective(weights):
            return np.dot(weights.T, np.dot(covariance_matrix.values, weights))

        # Constraints
        constraints = [{"type": "eq", "fun": lambda w: np.sum(w) - 1}]

        # Bounds
        bounds = tuple(
            (float(self.config.min_weight), float(self.config.max_weight)) for _ in range(n_assets)
        )

        # Initial guess (equal weights)
        x0 = np.array([1.0 / n_assets] * n_assets)

        # Optimize
        result = minimize(objective, x0, method="SLSQP", bounds=bounds, constraints=constraints)

        if result.success:
            weights = result.x
        else:
            # Fallback to equal weight
            weights = np.array([1.0 / n_assets] * n_assets)

        # Calculate allocations
        allocations = {}
        for i, symbol in enumerate(symbols):
            allocations[symbol] = portfolio_value * Decimal(str(weights[i]))

        return allocations

    def optimize_risk_parity(
        self,
        symbols: list[str],
        covariance_matrix: pd.DataFrame,
        portfolio_value: Decimal,
    ) -> dict[str, Decimal]:
        """
        Risk parity allocation (equal risk contribution).

        Args:
            symbols: List of symbols
            covariance_matrix: Covariance matrix
            portfolio_value: Total portfolio value

        Returns:
            Dictionary of symbol -> allocation amount
        """
        try:
            from scipy.optimize import minimize
        except ImportError:
            return self.optimize_equal_weight(symbols, portfolio_value)

        n_assets = len(symbols)

        # Risk contribution function
        def risk_contribution(weights):
            portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(covariance_matrix.values, weights)))
            marginal_contrib = np.dot(covariance_matrix.values, weights) / portfolio_vol
            contrib = weights * marginal_contrib
            return contrib

        # Objective: minimize sum of squared differences from equal risk contribution
        def objective(weights):
            contrib = risk_contribution(weights)
            target_contrib = np.ones(n_assets) / n_assets
            return np.sum((contrib - target_contrib) ** 2)

        # Constraints
        constraints = [{"type": "eq", "fun": lambda w: np.sum(w) - 1}]

        # Bounds
        bounds = tuple(
            (float(self.config.min_weight), float(self.config.max_weight)) for _ in range(n_assets)
        )

        # Initial guess
        x0 = np.array([1.0 / n_assets] * n_assets)

        # Optimize
        result = minimize(objective, x0, method="SLSQP", bounds=bounds, constraints=constraints)

        if result.success:
            weights = result.x
        else:
            weights = np.array([1.0 / n_assets] * n_assets)

        allocations = {}
        for i, symbol in enumerate(symbols):
            allocations[symbol] = portfolio_value * Decimal(str(weights[i]))

        return allocations

    def optimize(
        self,
        symbols: list[str],
        portfolio_value: Decimal,
        expected_returns: Optional[pd.Series] = None,
        covariance_matrix: Optional[pd.DataFrame] = None,
    ) -> dict[str, Decimal]:
        """
        Optimize portfolio allocation.

        Args:
            symbols: List of symbols
            portfolio_value: Total portfolio value
            expected_returns: Optional expected returns
            covariance_matrix: Optional covariance matrix

        Returns:
            Dictionary of symbol -> allocation amount
        """
        if self.config.method == OptimizationMethod.EQUAL_WEIGHT:
            return self.optimize_equal_weight(symbols, portfolio_value)

        elif self.config.method == OptimizationMethod.MARKOWITZ:
            if expected_returns is None or covariance_matrix is None:
                return self.optimize_equal_weight(symbols, portfolio_value)
            return self.optimize_markowitz(
                symbols, expected_returns, covariance_matrix, portfolio_value
            )

        elif self.config.method == OptimizationMethod.RISK_PARITY:
            if covariance_matrix is None:
                return self.optimize_equal_weight(symbols, portfolio_value)
            return self.optimize_risk_parity(symbols, covariance_matrix, portfolio_value)

        elif self.config.method == OptimizationMethod.MIN_VARIANCE:
            if covariance_matrix is None:
                return self.optimize_equal_weight(symbols, portfolio_value)
            # Min variance is Markowitz with no return target
            return self.optimize_markowitz(
                symbols, pd.Series([0] * len(symbols)), covariance_matrix, portfolio_value
            )

        elif self.config.method == OptimizationMethod.MAX_SHARPE:
            if expected_returns is None or covariance_matrix is None:
                return self.optimize_equal_weight(symbols, portfolio_value)
            # Max Sharpe: optimize Sharpe ratio
            # This is a simplified version - full implementation would optimize Sharpe directly
            return self.optimize_markowitz(
                symbols, expected_returns, covariance_matrix, portfolio_value
            )

        else:
            return self.optimize_equal_weight(symbols, portfolio_value)
