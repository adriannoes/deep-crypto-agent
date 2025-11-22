"""
Strategy optimizer using machine learning.

Uses ML techniques to optimize trading strategy parameters
and select optimal configurations.
"""

from dataclasses import dataclass
from decimal import Decimal
import logging
from typing import Any, Optional

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)


@dataclass
class OptimizationResult:
    """Result of strategy optimization."""

    best_params: dict[str, Any]
    best_score: Decimal
    all_results: list[dict[str, Any]]
    feature_importance: Optional[dict[str, float]] = None


class StrategyOptimizer:
    """
    Optimize trading strategy parameters using machine learning.

    Uses Random Forest to learn the relationship between
    strategy parameters and performance metrics.
    """

    def __init__(
        self,
        n_estimators: int = 100,
        max_depth: Optional[int] = None,
        random_state: Optional[int] = None,
    ):
        """
        Initialize strategy optimizer.

        Args:
            n_estimators: Number of trees in random forest
            max_depth: Maximum depth of trees
            random_state: Random seed for reproducibility
        """
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.random_state = random_state
        self.model: Optional[RandomForestRegressor] = None
        self.scaler = StandardScaler()
        self.feature_names: list[str] = []

    def optimize(
        self,
        parameter_sets: list[dict[str, Any]],
        performance_scores: list[Decimal],
        metric: str = "sharpe_ratio",
    ) -> OptimizationResult:
        """
        Optimize strategy parameters using ML.

        Args:
            parameter_sets: List of parameter dictionaries to evaluate
            performance_scores: Corresponding performance scores
            metric: Performance metric name

        Returns:
            OptimizationResult with best parameters and scores
        """
        if len(parameter_sets) != len(performance_scores):
            raise ValueError("Parameter sets and scores must have same length")

        if len(parameter_sets) < 10:
            logger.warning("Few samples for optimization, results may be unreliable")

        # Convert to DataFrame
        df_params = pd.DataFrame(parameter_sets)
        self.feature_names = list(df_params.columns)

        # Convert scores to float
        scores_array = np.array([float(s) for s in performance_scores])

        # Scale features
        x_scaled = self.scaler.fit_transform(df_params)  # noqa: N806

        # Train model
        self.model = RandomForestRegressor(
            n_estimators=self.n_estimators,
            max_depth=self.max_depth,
            random_state=self.random_state,
            n_jobs=-1,
        )
        self.model.fit(x_scaled, scores_array)

        # Get feature importance
        feature_importance = dict(zip(self.feature_names, self.model.feature_importances_))

        # Find best from training data
        best_idx = np.argmax(scores_array)
        best_params = parameter_sets[best_idx]
        best_score = performance_scores[best_idx]

        # Prepare all results
        all_results = [
            {"params": params, "score": float(score)}
            for params, score in zip(parameter_sets, performance_scores)
        ]

        return OptimizationResult(
            best_params=best_params,
            best_score=best_score,
            all_results=all_results,
            feature_importance=feature_importance,
        )

    def predict_performance(self, parameter_set: dict[str, Any]) -> Decimal:
        """
        Predict performance for given parameter set.

        Args:
            parameter_set: Parameter dictionary

        Returns:
            Predicted performance score
        """
        if self.model is None:
            raise ValueError("Model not trained. Call optimize() first")

        # Convert to DataFrame
        df_params = pd.DataFrame([parameter_set])
        missing_cols = set(self.feature_names) - set(df_params.columns)
        if missing_cols:
            for col in missing_cols:
                df_params[col] = 0  # Fill missing with 0

        # Reorder columns
        df_params = df_params[self.feature_names]

        # Scale features
        x_scaled = self.scaler.transform(df_params)  # noqa: N806

        # Predict
        prediction = self.model.predict(x_scaled)[0]

        return Decimal(str(prediction))

    def cross_validate(
        self,
        parameter_sets: list[dict[str, Any]],
        performance_scores: list[Decimal],
        cv_folds: int = 5,
    ) -> dict[str, float]:
        """
        Perform cross-validation on optimization model.

        Args:
            parameter_sets: List of parameter dictionaries
            performance_scores: Corresponding performance scores
            cv_folds: Number of cross-validation folds

        Returns:
            Dictionary with CV metrics
        """
        if len(parameter_sets) < cv_folds:
            raise ValueError(f"Need at least {cv_folds} samples for CV")

        df_params = pd.DataFrame(parameter_sets)
        x_scaled = self.scaler.fit_transform(df_params)  # noqa: N806
        scores_array = np.array([float(s) for s in performance_scores])

        model = RandomForestRegressor(
            n_estimators=self.n_estimators,
            max_depth=self.max_depth,
            random_state=self.random_state,
            n_jobs=-1,
        )

        cv_scores = cross_val_score(model, x_scaled, scores_array, cv=cv_folds, scoring="r2")

        return {
            "mean_r2": float(cv_scores.mean()),
            "std_r2": float(cv_scores.std()),
            "min_r2": float(cv_scores.min()),
            "max_r2": float(cv_scores.max()),
        }
