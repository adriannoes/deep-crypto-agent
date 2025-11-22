"""Tests for PricePredictor."""


import numpy as np
import pandas as pd
import pytest

from crypto_quant_pro.ml.models.price_predictor import PricePredictor


class TestPricePredictor:
    """Test PricePredictor class."""

    @pytest.fixture
    def sample_ohlcv_data(self):
        """Create sample OHLCV data."""
        dates = pd.date_range("2023-01-01", periods=100, freq="D")
        np.random.seed(42)
        prices = 100 + np.cumsum(np.random.randn(100) * 0.5)

        return pd.DataFrame(
            {
                "open": prices + np.random.randn(100) * 0.1,
                "high": prices + np.abs(np.random.randn(100) * 0.2),
                "low": prices - np.abs(np.random.randn(100) * 0.2),
                "close": prices,
                "volume": np.random.randint(1000, 10000, 100),
            },
            index=dates,
        )

    def test_initialization(self):
        """Test predictor initialization."""
        predictor = PricePredictor(n_estimators=50, random_state=42)
        assert predictor.n_estimators == 50
        assert predictor.random_state == 42
        assert predictor.model is None

    def test_prepare_features(self, sample_ohlcv_data):
        """Test feature preparation."""
        predictor = PricePredictor()
        features = predictor.prepare_features(sample_ohlcv_data)

        assert len(features) > 0
        assert "returns" in features.columns
        assert "sma_20" in features.columns
        assert "rsi" in features.columns

    def test_train(self, sample_ohlcv_data):
        """Test model training."""
        predictor = PricePredictor(n_estimators=10, random_state=42)
        predictor.train(sample_ohlcv_data, target_horizon=1)

        assert predictor.model is not None
        assert len(predictor.feature_names) > 0

    def test_predict(self, sample_ohlcv_data):
        """Test price prediction."""
        predictor = PricePredictor(n_estimators=10, random_state=42)
        predictor.train(sample_ohlcv_data, target_horizon=1)

        prediction = predictor.predict(sample_ohlcv_data)

        assert prediction.predicted_price > 0
        assert 0 <= prediction.confidence <= 1
        assert len(prediction.features_used) > 0

    def test_get_feature_importance(self, sample_ohlcv_data):
        """Test feature importance."""
        predictor = PricePredictor(n_estimators=10, random_state=42)
        predictor.train(sample_ohlcv_data, target_horizon=1)

        importance = predictor.get_feature_importance()
        assert len(importance) > 0
        assert all(v >= 0 for v in importance.values())
