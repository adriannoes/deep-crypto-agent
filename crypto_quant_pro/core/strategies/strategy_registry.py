"""Strategy registry for managing and discovering strategies."""
from typing import Any, Optional

from .base import BaseStrategy


class StrategyRegistry:
    """
    Registry for managing trading strategies.

    Provides a centralized way to register, discover, and retrieve strategies.
    """

    _strategies: dict[str, type[BaseStrategy]] = {}
    _instances: dict[str, BaseStrategy] = {}

    @classmethod
    def register(
        cls,
        name: Optional[str] = None,
        strategy_class: Optional[type[BaseStrategy]] = None,
    ) -> Any:
        """
        Register a strategy class.

        Can be used as a decorator or called directly.

        Args:
            name: Strategy name (defaults to class name)
            strategy_class: Strategy class to register

        Returns:
            Decorator function or the registered class

        Examples:
            @StrategyRegistry.register()
            class MyStrategy(BaseStrategy):
                ...

            # Or:
            StrategyRegistry.register("custom_name", MyStrategy)
        """
        if strategy_class is None:
            # Used as decorator
            def decorator(strategy: type[BaseStrategy]) -> type[BaseStrategy]:
                strategy_name = name or strategy.__name__
                cls._strategies[strategy_name] = strategy
                return strategy

            return decorator
        else:
            # Called directly
            strategy_name = name or strategy_class.__name__
            cls._strategies[strategy_name] = strategy_class
            return strategy_class

    @classmethod
    def get(cls, name: str, **kwargs: Any) -> BaseStrategy:
        """
        Get a strategy instance by name.

        Args:
            name: Strategy name
            **kwargs: Parameters to pass to strategy constructor

        Returns:
            Strategy instance

        Raises:
            KeyError: If strategy not found
        """
        if name not in cls._strategies:
            raise KeyError(f"Strategy '{name}' not found in registry")

        # Create instance if not cached or if kwargs provided
        cache_key = f"{name}_{hash(frozenset(kwargs.items()))}"
        if cache_key not in cls._instances or kwargs:
            strategy_class = cls._strategies[name]
            cls._instances[cache_key] = strategy_class(name=name, **kwargs)

        return cls._instances[cache_key]

    @classmethod
    def list_all(cls) -> list[str]:
        """
        List all registered strategy names.

        Returns:
            List of strategy names
        """
        return list(cls._strategies.keys())

    @classmethod
    def unregister(cls, name: str) -> None:
        """
        Unregister a strategy.

        Args:
            name: Strategy name to unregister
        """
        cls._strategies.pop(name, None)
        # Remove cached instances
        cls._instances = {k: v for k, v in cls._instances.items() if not k.startswith(f"{name}_")}

    @classmethod
    def clear(cls) -> None:
        """Clear all registered strategies and instances."""
        cls._strategies.clear()
        cls._instances.clear()

    @classmethod
    def exists(cls, name: str) -> bool:
        """
        Check if a strategy is registered.

        Args:
            name: Strategy name

        Returns:
            True if strategy exists, False otherwise
        """
        return name in cls._strategies

