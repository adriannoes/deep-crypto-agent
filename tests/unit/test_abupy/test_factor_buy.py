from unittest.mock import MagicMock

import pytest

from abupy.FactorBuyBu.ABuFactorBuyBase import AbuFactorBuyBase, BuyCallMixin, BuyPutMixin


class TestBuyMixins:
    def test_buy_call_mixin(self):
        """Test BuyCallMixin behavior"""
        mixin = BuyCallMixin()
        assert mixin.buy_type_str() == "call"
        assert mixin.expect_direction() == 1.0

    def test_buy_put_mixin(self):
        """Test BuyPutMixin behavior"""
        mixin = BuyPutMixin()
        assert mixin.buy_type_str() == "put"
        assert mixin.expect_direction() == -1.0


class ConcreteFactorBuy(AbuFactorBuyBase, BuyCallMixin):
    """Concrete implementation for testing"""

    def _init_self(self, **kwargs):
        pass


class TestAbuFactorBuyBase:
    @pytest.fixture
    def mock_capital(self):
        return MagicMock()

    @pytest.fixture
    def mock_benchmark(self):
        return MagicMock()

    def test_initialization(self, mock_capital, mock_benchmark):
        """Test basic initialization of factor buy base"""
        kl_pd = MagicMock()
        combine_kl_pd = MagicMock()

        factor = ConcreteFactorBuy(
            capital=mock_capital, kl_pd=kl_pd, combine_kl_pd=combine_kl_pd, benchmark=mock_benchmark
        )

        assert factor.capital == mock_capital
        assert factor.benchmark == mock_benchmark
        assert factor.skip_days == 0
        assert factor.lock_factor is False
        assert factor.factor_name == "ConcreteFactorBuy"
