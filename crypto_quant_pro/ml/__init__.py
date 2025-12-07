"""
Machine Learning module for crypto trading.

Provides ML models for strategy optimization, price prediction,
training, and inference.
"""

from .inference.predictor import InferencePredictor
from .models.price_predictor import PricePredictor
from .models.strategy_optimizer import StrategyOptimizer
from .training.trainer import ModelTrainer

__all__ = [
    "StrategyOptimizer",
    "PricePredictor",
    "ModelTrainer",
    "InferencePredictor",
]
