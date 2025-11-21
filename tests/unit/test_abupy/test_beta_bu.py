"""Unit tests for BetaBu position management module."""
from unittest.mock import MagicMock

import pytest

from abupy.BetaBu.ABuPositionBase import (
    AbuPositionBase,
    g_deposit_rate,
    g_pos_max,
)


class ConcretePosition(AbuPositionBase):
    """Concrete implementation for testing."""

    def _init_self(self, **kwargs):
        """Initialize concrete position."""
        self.custom_param = kwargs.get("custom_param", None)

    def fit_position(self, factor_object):
        """Calculate position size."""
        return 100.0


class TestAbuPositionBase:
    """Tests for AbuPositionBase abstract class."""

    def test_abstract_class_cannot_be_instantiated(self):
        """Verify abstract class cannot be instantiated."""
            with pytest.raises(TypeError):
                AbuPositionBase(None, None, None, None, None)

    def test_concrete_implementation(self):
        """Test concrete implementation of position base."""
        kl_pd = MagicMock()
        position = ConcretePosition(
            kl_pd_buy=kl_pd,
            factor_name="test_factor",
            symbol_name="usAAPL",
            bp=150.0,
            read_cash=100000.0,
        )

        assert position.factor_name == "test_factor"
        assert position.symbol_name == "usAAPL"
        assert position.bp == 150.0
        assert position.read_cash == 100000.0
        assert position.pos_max == g_pos_max
        assert position.deposit_rate == g_deposit_rate

    def test_custom_position_max(self):
        """Test custom position max parameter."""
        kl_pd = MagicMock()
        position = ConcretePosition(
            kl_pd_buy=kl_pd,
            factor_name="test_factor",
            symbol_name="usAAPL",
            bp=150.0,
            read_cash=100000.0,
            pos_max=0.5,
        )

        assert position.pos_max == 0.5

    def test_custom_deposit_rate(self):
        """Test custom deposit rate parameter."""
        kl_pd = MagicMock()
        position = ConcretePosition(
            kl_pd_buy=kl_pd,
            factor_name="test_factor",
            symbol_name="usAAPL",
            bp=150.0,
            read_cash=100000.0,
            deposit_rate=0.8,
        )

        assert position.deposit_rate == 0.8

    def test_fit_position_returns_float(self):
        """Test fit_position returns float."""
        kl_pd = MagicMock()
        position = ConcretePosition(
            kl_pd_buy=kl_pd,
            factor_name="test_factor",
            symbol_name="usAAPL",
            bp=150.0,
            read_cash=100000.0,
        )

        factor_object = MagicMock()
        result = position.fit_position(factor_object)

        assert isinstance(result, float)
        assert result == 100.0

    def test_str_representation(self):
        """Test string representation."""
        kl_pd = MagicMock()
        position = ConcretePosition(
            kl_pd_buy=kl_pd,
            factor_name="test_factor",
            symbol_name="usAAPL",
            bp=150.0,
            read_cash=100000.0,
        )

        str_repr = str(position)
        assert "ConcretePosition" in str_repr
        assert "test_factor" in str_repr
        assert "usAAPL" in str_repr
        assert "100000.0" in str_repr

    def test_global_position_max(self):
        """Test global position max configuration."""
        # This test verifies the global variable exists and can be accessed
        assert isinstance(g_pos_max, float)
        assert 0.0 <= g_pos_max <= 1.0

    def test_global_deposit_rate(self):
        """Test global deposit rate configuration."""
        assert isinstance(g_deposit_rate, float)
        assert g_deposit_rate >= 0.0

    def test_custom_init_params(self):
        """Test custom initialization parameters."""
        kl_pd = MagicMock()
        position = ConcretePosition(
            kl_pd_buy=kl_pd,
            factor_name="test_factor",
            symbol_name="usAAPL",
            bp=150.0,
            read_cash=100000.0,
            custom_param="test_value",
        )

        assert position.custom_param == "test_value"
