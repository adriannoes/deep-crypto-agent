"""Tests for portfolio optimizer."""
from decimal import Decimal

import pandas as pd

from crypto_quant_pro.core.risk.portfolio_optimizer import (
    OptimizationConfig,
    OptimizationMethod,
    PortfolioOptimizer,
)


def test_portfolio_optimizer_initialization():
    """Test portfolio optimizer initialization."""
    config = OptimizationConfig(method=OptimizationMethod.EQUAL_WEIGHT)
    optimizer = PortfolioOptimizer(config)
    assert optimizer.config == config


def test_optimize_equal_weight():
    """Test equal weight optimization."""
    config = OptimizationConfig(method=OptimizationMethod.EQUAL_WEIGHT)
    optimizer = PortfolioOptimizer(config)

    symbols = ["BTC/USD", "ETH/USD", "LTC/USD"]
    allocations = optimizer.optimize_equal_weight(symbols, Decimal("100000"))

    assert len(allocations) == 3
    # Each should get 1/3 of portfolio
    expected_allocation = Decimal("100000") / Decimal("3")
    for allocation in allocations.values():
        assert allocation == expected_allocation


def test_optimize_equal_weight_empty():
    """Test equal weight optimization with empty symbols."""
    config = OptimizationConfig(method=OptimizationMethod.EQUAL_WEIGHT)
    optimizer = PortfolioOptimizer(config)

    allocations = optimizer.optimize_equal_weight([], Decimal("100000"))
    assert len(allocations) == 0


def test_optimize_markowitz():
    """Test Markowitz optimization."""
    config = OptimizationConfig(method=OptimizationMethod.MARKOWITZ)
    optimizer = PortfolioOptimizer(config)

    symbols = ["BTC/USD", "ETH/USD"]
    expected_returns = pd.Series([0.1, 0.15], index=symbols)
    covariance_matrix = pd.DataFrame([[0.04, 0.02], [0.02, 0.05]], index=symbols, columns=symbols)

    allocations = optimizer.optimize_markowitz(
        symbols, expected_returns, covariance_matrix, Decimal("100000")
    )

    assert len(allocations) == 2
    assert "BTC/USD" in allocations
    assert "ETH/USD" in allocations
    # Sum should be approximately portfolio value
    total = sum(allocations.values())
    assert abs(total - Decimal("100000")) < Decimal("1000")  # Allow small rounding


def test_optimize_risk_parity():
    """Test risk parity optimization."""
    config = OptimizationConfig(method=OptimizationMethod.RISK_PARITY)
    optimizer = PortfolioOptimizer(config)

    symbols = ["BTC/USD", "ETH/USD"]
    covariance_matrix = pd.DataFrame([[0.04, 0.02], [0.02, 0.05]], index=symbols, columns=symbols)

    allocations = optimizer.optimize_risk_parity(symbols, covariance_matrix, Decimal("100000"))

    assert len(allocations) == 2
    assert "BTC/USD" in allocations
    assert "ETH/USD" in allocations


def test_optimize_fallback():
    """Test optimization fallback when inputs missing."""
    config = OptimizationConfig(method=OptimizationMethod.MARKOWITZ)
    optimizer = PortfolioOptimizer(config)

    symbols = ["BTC/USD", "ETH/USD"]

    # Should fallback to equal weight when expected_returns missing
    allocations = optimizer.optimize(symbols, Decimal("100000"))
    assert len(allocations) == 2
    expected = Decimal("100000") / Decimal("2")
    assert allocations["BTC/USD"] == expected
    assert allocations["ETH/USD"] == expected
