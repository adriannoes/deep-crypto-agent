"""Tests for StrategyOptimizer."""

from decimal import Decimal

from crypto_quant_pro.ml.models.strategy_optimizer import StrategyOptimizer


class TestStrategyOptimizer:
    """Test StrategyOptimizer class."""

    def test_initialization(self):
        """Test optimizer initialization."""
        optimizer = StrategyOptimizer(n_estimators=50, random_state=42)
        assert optimizer.n_estimators == 50
        assert optimizer.random_state == 42
        assert optimizer.model is None

    def test_optimize(self):
        """Test parameter optimization."""
        optimizer = StrategyOptimizer(n_estimators=10, random_state=42)

        parameter_sets = [
            {"param1": 1, "param2": 10},
            {"param1": 2, "param2": 20},
            {"param1": 3, "param2": 30},
            {"param1": 4, "param2": 40},
            {"param1": 5, "param2": 50},
        ] * 3  # 15 samples

        performance_scores = [
            Decimal("0.1"),
            Decimal("0.2"),
            Decimal("0.3"),
            Decimal("0.4"),
            Decimal("0.5"),
        ] * 3

        result = optimizer.optimize(parameter_sets, performance_scores)

        assert result.best_params is not None
        assert result.best_score > 0
        assert len(result.all_results) == 15
        assert result.feature_importance is not None

    def test_predict_performance(self):
        """Test performance prediction."""
        optimizer = StrategyOptimizer(n_estimators=10, random_state=42)

        parameter_sets = [
            {"param1": 1, "param2": 10},
            {"param1": 2, "param2": 20},
        ] * 5  # 10 samples

        performance_scores = [Decimal("0.1"), Decimal("0.2")] * 5

        optimizer.optimize(parameter_sets, performance_scores)

        prediction = optimizer.predict_performance({"param1": 3, "param2": 30})
        assert isinstance(prediction, Decimal)

    def test_cross_validate(self):
        """Test cross-validation."""
        optimizer = StrategyOptimizer(n_estimators=10, random_state=42)

        parameter_sets = [{"param1": i, "param2": i * 10} for i in range(1, 21)]  # 20 samples

        performance_scores = [Decimal(str(i * 0.01)) for i in range(1, 21)]

        cv_results = optimizer.cross_validate(parameter_sets, performance_scores, cv_folds=5)

        assert "mean_r2" in cv_results
        assert "std_r2" in cv_results
        assert cv_results["mean_r2"] <= 1.0
