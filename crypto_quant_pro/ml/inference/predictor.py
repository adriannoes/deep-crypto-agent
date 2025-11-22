"""
Inference system for ML models.

Provides utilities for loading models and making predictions
in production environments.
"""

from decimal import Decimal
import logging
from pathlib import Path
from typing import Any, Optional

import pandas as pd

from ..models.price_predictor import PricePrediction, PricePredictor
from ..models.strategy_optimizer import StrategyOptimizer

logger = logging.getLogger(__name__)


class InferencePredictor:
    """
    Make predictions using trained ML models.

    Handles model loading and inference for production use.
    """

    def __init__(self, models_dir: Optional[Path] = None):
        """
        Initialize inference predictor.

        Args:
            models_dir: Directory containing saved models
        """
        self.models_dir = models_dir or Path("models")
        self.loaded_models: dict[str, Any] = {}

    def load_price_predictor(
        self, model_path: Optional[Path] = None, model_name: str = "price_predictor"
    ) -> PricePredictor:
        """
        Load price prediction model.

        Args:
            model_path: Path to model file
            model_name: Name of model to load

        Returns:
            Loaded PricePredictor model
        """
        if model_path is None:
            model_path = self.models_dir / f"{model_name}.pkl"

        if not model_path.exists():
            raise FileNotFoundError(f"Model not found: {model_path}")

        import pickle

        with open(model_path, "rb") as f:
            model = pickle.load(f)

        if not isinstance(model, PricePredictor):
            raise ValueError("Loaded model is not a PricePredictor")

        self.loaded_models[model_name] = model
        logger.info(f"Loaded price predictor from {model_path}")

        return model

    def load_strategy_optimizer(
        self,
        model_path: Optional[Path] = None,
        model_name: str = "strategy_optimizer",
    ) -> StrategyOptimizer:
        """
        Load strategy optimizer model.

        Args:
            model_path: Path to model file
            model_name: Name of model to load

        Returns:
            Loaded StrategyOptimizer model
        """
        if model_path is None:
            model_path = self.models_dir / f"{model_name}.pkl"

        if not model_path.exists():
            raise FileNotFoundError(f"Model not found: {model_path}")

        import pickle

        with open(model_path, "rb") as f:
            model = pickle.load(f)

        if not isinstance(model, StrategyOptimizer):
            raise ValueError("Loaded model is not a StrategyOptimizer")

        self.loaded_models[model_name] = model
        logger.info(f"Loaded strategy optimizer from {model_path}")

        return model

    def predict_price(
        self,
        ohlcv_data: pd.DataFrame,
        model_name: str = "price_predictor",
        lookback_window: int = 20,
    ) -> PricePrediction:
        """
        Predict future price using loaded model.

        Args:
            ohlcv_data: Recent OHLCV data
            model_name: Name of model to use
            lookback_window: Lookback window for features

        Returns:
            PricePrediction with predicted price
        """
        if model_name not in self.loaded_models:
            self.load_price_predictor(model_name=model_name)

        predictor = self.loaded_models[model_name]
        if not isinstance(predictor, PricePredictor):
            raise ValueError(f"Model {model_name} is not a PricePredictor")

        return predictor.predict(ohlcv_data, lookback_window)

    def optimize_strategy(
        self,
        parameter_set: dict[str, Any],
        model_name: str = "strategy_optimizer",
    ) -> Decimal:
        """
        Predict strategy performance using loaded model.

        Args:
            parameter_set: Strategy parameters
            model_name: Name of model to use

        Returns:
            Predicted performance score
        """
        if model_name not in self.loaded_models:
            self.load_strategy_optimizer(model_name=model_name)

        optimizer = self.loaded_models[model_name]
        if not isinstance(optimizer, StrategyOptimizer):
            raise ValueError(f"Model {model_name} is not a StrategyOptimizer")

        return optimizer.predict_performance(parameter_set)
