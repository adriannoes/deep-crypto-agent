"""
Adapter for compatibility with legacy MLBu module.

Provides a bridge between the new ML system and
the legacy ABU MLBu interface.
"""

import logging
from typing import Any, Optional

from .models.price_predictor import PricePredictor
from .models.strategy_optimizer import StrategyOptimizer
from .training.trainer import ModelTrainer

logger = logging.getLogger(__name__)


class AbuMLAdapter:
    """
    Adapter to provide MLBu-compatible interface.

    Wraps the new ML components to maintain compatibility
    with legacy ABU code.
    """

    def __init__(self):
        """Initialize ML adapter."""
        self.price_predictor: Optional[PricePredictor] = None
        self.strategy_optimizer: Optional[StrategyOptimizer] = None
        self.trainer = ModelTrainer()

    def create_price_predictor(self, **kwargs: Any) -> PricePredictor:
        """
        Create price predictor (MLBu compatibility).

        Args:
            **kwargs: Arguments for PricePredictor

        Returns:
            PricePredictor instance
        """
        self.price_predictor = PricePredictor(**kwargs)
        return self.price_predictor

    def create_strategy_optimizer(self, **kwargs: Any) -> StrategyOptimizer:
        """
        Create strategy optimizer (MLBu compatibility).

        Args:
            **kwargs: Arguments for StrategyOptimizer

        Returns:
            StrategyOptimizer instance
        """
        self.strategy_optimizer = StrategyOptimizer(**kwargs)
        return self.strategy_optimizer

    def predict_price(self, ohlcv_data: Any, **kwargs: Any) -> dict[str, Any]:
        """
        Predict price (MLBu compatibility).

        Args:
            ohlcv_data: OHLCV data
            **kwargs: Additional arguments

        Returns:
            Dictionary with prediction results
        """
        if self.price_predictor is None:
            self.price_predictor = PricePredictor()

        import pandas as pd

        if not isinstance(ohlcv_data, pd.DataFrame):
            ohlcv_data = pd.DataFrame(ohlcv_data)

        prediction = self.price_predictor.predict(ohlcv_data, **kwargs)

        return {
            "predicted_price": float(prediction.predicted_price),
            "confidence": float(prediction.confidence),
            "prediction_horizon": prediction.prediction_horizon,
            "features_used": prediction.features_used,
        }

    def optimize_strategy(
        self, parameter_sets: list[dict[str, Any]], performance_scores: list[Any]
    ) -> dict[str, Any]:
        """
        Optimize strategy (MLBu compatibility).

        Args:
            parameter_sets: List of parameter dictionaries
            performance_scores: Performance scores

        Returns:
            Dictionary with optimization results
        """
        if self.strategy_optimizer is None:
            self.strategy_optimizer = StrategyOptimizer()

        from decimal import Decimal

        scores = [Decimal(str(s)) if not isinstance(s, Decimal) else s for s in performance_scores]

        result = self.strategy_optimizer.optimize(parameter_sets, scores)

        return {
            "best_params": result.best_params,
            "best_score": float(result.best_score),
            "all_results": result.all_results,
            "feature_importance": result.feature_importance,
        }
