"""
Price prediction models for cryptocurrency markets.

Provides ML models for predicting future price movements
and trends.
"""

from dataclasses import dataclass
from decimal import Decimal
import logging
from typing import Optional

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)


@dataclass
class PricePrediction:
    """Price prediction result."""

    predicted_price: Decimal
    confidence: Decimal
    prediction_horizon: int  # Days ahead
    features_used: list[str]


class PricePredictor:
    """
    Predict future cryptocurrency prices using machine learning.

    Uses gradient boosting to learn price patterns from
    historical OHLCV data and technical indicators.
    """

    def __init__(
        self,
        n_estimators: int = 100,
        learning_rate: float = 0.1,
        max_depth: int = 5,
        random_state: Optional[int] = None,
    ):
        """
        Initialize price predictor.

        Args:
            n_estimators: Number of boosting stages
            learning_rate: Learning rate
            max_depth: Maximum depth of trees
            random_state: Random seed
        """
        self.n_estimators = n_estimators
        self.learning_rate = learning_rate
        self.max_depth = max_depth
        self.random_state = random_state
        self.model: Optional[GradientBoostingRegressor] = None
        self.scaler = StandardScaler()
        self.feature_names: list[str] = []

    def prepare_features(self, ohlcv_data: pd.DataFrame, lookback_window: int = 20) -> pd.DataFrame:
        """
        Prepare features from OHLCV data.

        Args:
            ohlcv_data: DataFrame with OHLCV columns
            lookback_window: Number of periods for technical indicators

        Returns:
            DataFrame with features
        """
        df = ohlcv_data.copy()

        # Ensure required columns exist
        required_cols = ["open", "high", "low", "close", "volume"]
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

        # Price features
        df["returns"] = df["close"].pct_change()
        df["log_returns"] = np.log(df["close"] / df["close"].shift(1))

        # Moving averages
        df["sma_5"] = df["close"].rolling(window=5).mean()
        df["sma_20"] = df["close"].rolling(window=lookback_window).mean()
        df["ema_12"] = df["close"].ewm(span=12).mean()

        # Volatility
        df["volatility"] = df["returns"].rolling(window=lookback_window).std()

        # RSI-like momentum
        delta = df["close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df["rsi"] = 100 - (100 / (1 + rs))

        # Volume features
        df["volume_sma"] = df["volume"].rolling(window=lookback_window).mean()
        df["volume_ratio"] = df["volume"] / df["volume_sma"]

        # Price position in range
        df["high_low_ratio"] = (df["close"] - df["low"]) / (df["high"] - df["low"] + 1e-10)

        # Drop NaN rows
        df = df.dropna()

        return df

    def train(
        self,
        ohlcv_data: pd.DataFrame,
        target_horizon: int = 1,
        lookback_window: int = 20,
    ) -> None:
        """
        Train price prediction model.

        Args:
            ohlcv_data: Historical OHLCV data
            target_horizon: Days ahead to predict
            lookback_window: Lookback window for features
        """
        # Prepare features
        df_features = self.prepare_features(ohlcv_data, lookback_window)

        # Create target (future price)
        if len(df_features) <= target_horizon:
            raise ValueError("Not enough data for target horizon")

        target = df_features["close"].shift(-target_horizon).dropna()
        features = df_features.iloc[:-target_horizon]

        # Align indices
        common_idx = features.index.intersection(target.index)
        features = features.loc[common_idx]
        target = target.loc[common_idx]

        if len(features) == 0:
            raise ValueError("No valid training samples after alignment")

        # Select feature columns (exclude OHLCV and target)
        exclude_cols = ["open", "high", "low", "close", "volume"]
        feature_cols = [c for c in features.columns if c not in exclude_cols]
        self.feature_names = feature_cols

        x_features = features[feature_cols].values  # noqa: N806
        y = target.values

        # Scale features
        x_scaled = self.scaler.fit_transform(x_features)  # noqa: N806

        # Train model
        self.model = GradientBoostingRegressor(
            n_estimators=self.n_estimators,
            learning_rate=self.learning_rate,
            max_depth=self.max_depth,
            random_state=self.random_state,
        )
        self.model.fit(x_scaled, y)

        logger.info(f"Trained price predictor with {len(features)} samples")

    def predict(self, ohlcv_data: pd.DataFrame, lookback_window: int = 20) -> PricePrediction:
        """
        Predict future price.

        Args:
            ohlcv_data: Recent OHLCV data
            lookback_window: Lookback window for features

        Returns:
            PricePrediction with predicted price and confidence
        """
        if self.model is None:
            raise ValueError("Model not trained. Call train() first")

        # Prepare features
        df_features = self.prepare_features(ohlcv_data, lookback_window)

        if len(df_features) == 0:
            raise ValueError("No features extracted from data")

        # Get latest features
        latest_features = df_features[self.feature_names].iloc[-1:].values

        # Scale
        x_scaled = self.scaler.transform(latest_features)  # noqa: N806

        # Predict
        prediction = self.model.predict(x_scaled)[0]

        # Estimate confidence (using prediction intervals from ensemble)
        # Simple approach: use std of individual tree predictions
        try:
            tree_predictions = np.array(
                [tree.predict(x_scaled.reshape(1, -1))[0] for tree in self.model.estimators_]
            )
            std_prediction = float(np.std(tree_predictions))
            confidence = Decimal("1.0") - Decimal(
                str(min(std_prediction / (abs(prediction) + 1e-10), 1.0))
            )
        except Exception:
            # Fallback if tree predictions fail
            confidence = Decimal("0.5")

        return PricePrediction(
            predicted_price=Decimal(str(prediction)),
            confidence=max(confidence, Decimal("0")),
            prediction_horizon=1,
            features_used=self.feature_names,
        )

    def get_feature_importance(self) -> dict[str, float]:
        """
        Get feature importance from trained model.

        Returns:
            Dictionary mapping feature names to importance scores
        """
        if self.model is None:
            raise ValueError("Model not trained")

        return dict(zip(self.feature_names, self.model.feature_importances_))
