"""Tests for risk calculator."""
from decimal import Decimal

import numpy as np
import pandas as pd
import pytest

from crypto_quant_pro.core.risk.risk_calculator import RiskCalculator


@pytest.fixture
def sample_returns():
    """Create sample returns data."""
    np.random.seed(42)
    return pd.Series(np.random.randn(100) * 0.02)  # 2% daily volatility


def test_risk_calculator_initialization():
    """Test risk calculator initialization."""
    calculator = RiskCalculator()
    assert calculator is not None


def test_calculate_var(sample_returns):
    """Test VaR calculation."""
    calculator = RiskCalculator()
    var_95 = calculator.calculate_var(sample_returns, Decimal("0.95"))
    assert var_95 >= 0
    assert isinstance(var_95, Decimal)


def test_calculate_cvar(sample_returns):
    """Test CVaR calculation."""
    calculator = RiskCalculator()
    cvar_95 = calculator.calculate_cvar(sample_returns, Decimal("0.95"))
    assert cvar_95 >= 0
    assert isinstance(cvar_95, Decimal)


def test_calculate_volatility(sample_returns):
    """Test volatility calculation."""
    calculator = RiskCalculator()
    volatility = calculator.calculate_volatility(sample_returns, annualized=True)
    assert volatility >= 0
    assert isinstance(volatility, Decimal)


def test_calculate_sharpe_ratio(sample_returns):
    """Test Sharpe ratio calculation."""
    calculator = RiskCalculator()
    sharpe = calculator.calculate_sharpe_ratio(sample_returns, risk_free_rate=Decimal("0.02"))
    assert isinstance(sharpe, Decimal)


def test_calculate_sortino_ratio(sample_returns):
    """Test Sortino ratio calculation."""
    calculator = RiskCalculator()
    sortino = calculator.calculate_sortino_ratio(sample_returns, risk_free_rate=Decimal("0.02"))
    assert isinstance(sortino, Decimal)


def test_calculate_max_drawdown():
    """Test max drawdown calculation."""
    calculator = RiskCalculator()
    equity_curve = [
        Decimal("10000"),
        Decimal("11000"),
        Decimal("10500"),
        Decimal("12000"),
        Decimal("10000"),  # Drawdown
        Decimal("11000"),
    ]
    max_dd = calculator.calculate_max_drawdown(equity_curve)
    assert max_dd >= 0
    assert isinstance(max_dd, Decimal)


def test_calculate_beta():
    """Test beta calculation."""
    calculator = RiskCalculator()
    portfolio_returns = pd.Series([0.01, 0.02, -0.01, 0.03, 0.01])
    market_returns = pd.Series([0.01, 0.015, -0.005, 0.02, 0.01])
    beta = calculator.calculate_beta(portfolio_returns, market_returns)
    assert isinstance(beta, Decimal)


def test_calculate_correlation_matrix():
    """Test correlation matrix calculation."""
    calculator = RiskCalculator()
    returns_df = pd.DataFrame(
        {
            "BTC": [0.01, 0.02, -0.01, 0.03],
            "ETH": [0.015, 0.025, -0.005, 0.025],
            "LTC": [0.008, 0.018, -0.008, 0.028],
        }
    )
    corr_matrix = calculator.calculate_correlation_matrix(returns_df)
    assert isinstance(corr_matrix, pd.DataFrame)
    assert len(corr_matrix) == 3
