"""
Model training system for ML models.

Provides utilities for training, validating, and saving
trading ML models.
"""

from dataclasses import dataclass
from decimal import Decimal
import logging
from pathlib import Path
import pickle
from typing import Any, Optional

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from ..models.price_predictor import PricePredictor
from ..models.strategy_optimizer import StrategyOptimizer

logger = logging.getLogger(__name__)


@dataclass
class TrainingConfig:
    """Configuration for model training."""

    test_size: float = 0.2
    validation_size: float = 0.1
    random_state: Optional[int] = None
    save_path: Optional[Path] = None
    early_stopping: bool = True
    min_samples: int = 100


@dataclass
class TrainingResult:
    """Result of model training."""

    train_score: float
    test_score: float
    validation_score: Optional[float] = None
    model_path: Optional[Path] = None
    training_samples: int = 0
    test_samples: int = 0


class ModelTrainer:
    """
    Train and validate ML models for trading.

    Handles data splitting, training, validation,
    and model persistence.
    """

    def __init__(self, config: Optional[TrainingConfig] = None):
        """
        Initialize model trainer.

        Args:
            config: Training configuration
        """
        self.config = config or TrainingConfig()
        self.models: dict[str, Any] = {}

    def train_price_predictor(
        self,
        ohlcv_data: pd.DataFrame,
        model_name: str = "price_predictor",
        target_horizon: int = 1,
        lookback_window: int = 20,
        **model_kwargs: Any,
    ) -> TrainingResult:
        """
        Train price prediction model.

        Args:
            ohlcv_data: Historical OHLCV data
            model_name: Name for saving model
            target_horizon: Days ahead to predict
            lookback_window: Lookback window for features
            **model_kwargs: Additional arguments for PricePredictor

        Returns:
            TrainingResult with scores and model path
        """
        # Validate data
        if len(ohlcv_data) < self.config.min_samples:
            raise ValueError(
                f"Need at least {self.config.min_samples} samples, got {len(ohlcv_data)}"
            )

        # Prepare features
        predictor = PricePredictor(**model_kwargs)
        df_features = predictor.prepare_features(ohlcv_data, lookback_window)

        if len(df_features) <= target_horizon:
            raise ValueError("Not enough data for target horizon")

        # Create target
        target = df_features["close"].shift(-target_horizon).dropna()
        features = df_features.iloc[:-target_horizon]

        # Align indices
        common_idx = features.index.intersection(target.index)
        features = features.loc[common_idx]
        target = target.loc[common_idx]

        # Select feature columns
        exclude_cols = ["open", "high", "low", "close", "volume"]
        feature_cols = [c for c in features.columns if c not in exclude_cols]

        x_features = features[feature_cols].values  # noqa: N806
        y = target.values

        # Split data
        x_train, x_temp, y_train, y_temp = train_test_split(  # noqa: N806
            x_features,
            y,
            test_size=self.config.test_size + self.config.validation_size,
            random_state=self.config.random_state,
        )

        val_size = self.config.validation_size / (
            self.config.test_size + self.config.validation_size
        )
        x_test, x_val, y_test, y_val = train_test_split(  # noqa: N806
            x_temp,
            y_temp,
            test_size=val_size,
            random_state=self.config.random_state,
        )

        # Train on full training set
        predictor.train(ohlcv_data, target_horizon, lookback_window)

        # Evaluate
        train_pred = predictor.model.predict(x_train)
        test_pred = predictor.model.predict(x_test)

        train_score = float(np.mean((train_pred - y_train) ** 2))
        test_score = float(np.mean((test_pred - y_test) ** 2))

        validation_score = None
        if len(x_val) > 0:
            val_pred = predictor.model.predict(x_val)
            validation_score = float(np.mean((val_pred - y_val) ** 2))

        # Save model
        model_path = None
        if self.config.save_path:
            save_dir = Path(self.config.save_path)
            save_dir.mkdir(parents=True, exist_ok=True)
            model_path = save_dir / f"{model_name}.pkl"

            with open(model_path, "wb") as f:
                pickle.dump(predictor, f)

            logger.info(f"Saved model to {model_path}")

        self.models[model_name] = predictor

        return TrainingResult(
            train_score=train_score,
            test_score=test_score,
            validation_score=validation_score,
            model_path=model_path,
            training_samples=len(x_train),
            test_samples=len(x_test),
        )

    def train_strategy_optimizer(
        self,
        parameter_sets: list[dict[str, Any]],
        performance_scores: list[Decimal],
        model_name: str = "strategy_optimizer",
        **model_kwargs: Any,
    ) -> TrainingResult:
        """
        Train strategy optimizer model.

        Args:
            parameter_sets: List of parameter dictionaries
            performance_scores: Corresponding performance scores
            model_name: Name for saving model
            **model_kwargs: Additional arguments for StrategyOptimizer

        Returns:
            TrainingResult with scores and model path
        """
        if len(parameter_sets) < self.config.min_samples:
            raise ValueError(
                f"Need at least {self.config.min_samples} samples, got {len(parameter_sets)}"
            )

        # Convert to arrays
        df_params = pd.DataFrame(parameter_sets)
        scores_array = np.array([float(s) for s in performance_scores])

        # Split data
        x_train, x_test, y_train, y_test = train_test_split(  # noqa: N806
            df_params.values,
            scores_array,
            test_size=self.config.test_size,
            random_state=self.config.random_state,
        )

        # Convert back to lists
        train_params = [dict(zip(df_params.columns, row)) for row in x_train]
        train_scores = [Decimal(str(s)) for s in y_train]

        test_params = [dict(zip(df_params.columns, row)) for row in x_test]

        # Train optimizer
        optimizer = StrategyOptimizer(**model_kwargs)
        optimizer.optimize(train_params, train_scores)

        # Evaluate on test set
        test_predictions = [optimizer.predict_performance(params) for params in test_params]
        test_pred_array = np.array([float(p) for p in test_predictions])

        train_score = float(np.mean((y_train - test_pred_array[: len(y_train)]) ** 2))
        test_score = float(np.mean((y_test - test_pred_array[-len(y_test) :]) ** 2))

        # Save model
        model_path = None
        if self.config.save_path:
            save_dir = Path(self.config.save_path)
            save_dir.mkdir(parents=True, exist_ok=True)
            model_path = save_dir / f"{model_name}.pkl"

            with open(model_path, "wb") as f:
                pickle.dump(optimizer, f)

            logger.info(f"Saved model to {model_path}")

        self.models[model_name] = optimizer

        return TrainingResult(
            train_score=train_score,
            test_score=test_score,
            model_path=model_path,
            training_samples=len(x_train),
            test_samples=len(x_test),
        )

    def load_model(self, model_path: Path) -> Any:
        """
        Load a trained model from disk.

        Args:
            model_path: Path to saved model

        Returns:
            Loaded model
        """
        with open(model_path, "rb") as f:
            model = pickle.load(f)

        logger.info(f"Loaded model from {model_path}")
        return model
