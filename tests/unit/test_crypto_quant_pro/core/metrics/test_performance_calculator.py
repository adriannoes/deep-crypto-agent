"""Tests for PerformanceCalculator."""

from datetime import datetime, timedelta
from decimal import Decimal

import pytest

from crypto_quant_pro.core.metrics.performance_calculator import (
    PerformanceCalculator,
)


class TestPerformanceCalculator:
    """Test PerformanceCalculator class."""

    @pytest.fixture
    def sample_equity_curve(self):
        """Create sample equity curve."""
        base_value = Decimal("100000")
        returns = [Decimal("0.01"), Decimal("0.02"), Decimal("-0.01"), Decimal("0.03")]
        equity = [base_value]
        for ret in returns:
            equity.append(equity[-1] * (Decimal("1") + ret))
        # Ensure we have at least 2 values
        if len(equity) < 2:
            equity.append(equity[0] * Decimal("1.01"))
        return equity

    @pytest.fixture
    def sample_trades(self):
        """Create sample trades."""
        base_time = datetime(2023, 1, 1)
        return [
            {
                "entry_time": base_time,
                "exit_time": base_time + timedelta(days=5),
                "pnl": Decimal("100"),
            },
            {
                "entry_time": base_time + timedelta(days=10),
                "exit_time": base_time + timedelta(days=15),
                "pnl": Decimal("-50"),
            },
            {
                "entry_time": base_time + timedelta(days=20),
                "exit_time": base_time + timedelta(days=25),
                "pnl": Decimal("200"),
            },
        ]

    def test_initialization(self):
        """Test calculator initialization."""
        calc = PerformanceCalculator(risk_free_rate=Decimal("0.03"))
        assert calc.risk_free_rate == Decimal("0.03")

    def test_calculate_basic(self, sample_equity_curve):
        """Test basic performance calculation."""
        calc = PerformanceCalculator()
        metrics = calc.calculate(sample_equity_curve)

        assert metrics.total_return > 0
        assert metrics.volatility >= 0
        assert metrics.max_drawdown >= 0

    def test_calculate_with_trades(self, sample_equity_curve, sample_trades):
        """Test calculation with trades."""
        calc = PerformanceCalculator()
        metrics = calc.calculate(sample_equity_curve, trades=sample_trades)

        assert metrics.total_trades == 3
        assert metrics.winning_trades == 2
        assert metrics.losing_trades == 1
        assert metrics.win_rate > 0
        assert metrics.profit_factor > 0

    def test_calculate_with_timestamps(self, sample_equity_curve):
        """Test calculation with timestamps."""
        calc = PerformanceCalculator()
        timestamps = [
            datetime(2023, 1, 1) + timedelta(days=i) for i in range(len(sample_equity_curve))
        ]

        metrics = calc.calculate(sample_equity_curve, timestamps=timestamps)

        assert metrics.annualized_return >= 0
        assert metrics.max_drawdown_duration >= 0

    def test_empty_equity_curve(self):
        """Test with empty equity curve."""
        calc = PerformanceCalculator()
        with pytest.raises(ValueError):
            calc.calculate([Decimal("100000")])
