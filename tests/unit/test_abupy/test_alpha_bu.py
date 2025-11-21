"""Unit tests for AlphaBu pick base classes."""
import pytest

from abupy.AlphaBu.ABuPickBase import AbuPickStockWorkBase, AbuPickTimeWorkBase


class TestAbuPickTimeWorkBase:
    """Tests for timing base class."""

    def test_abstract_class_cannot_be_instantiated(self):
        """Verify abstract class cannot be instantiated."""
            with pytest.raises(TypeError):
                AbuPickTimeWorkBase()

    def test_class_exists(self):
        """Verify class exists and is abstract."""
        assert AbuPickTimeWorkBase is not None
        assert hasattr(AbuPickTimeWorkBase, "__abstractmethods__")


class TestAbuPickStockWorkBase:
    """Tests for stock selection base class."""

    def test_abstract_class_cannot_be_instantiated(self):
        """Verify abstract class cannot be instantiated."""
            with pytest.raises(TypeError):
                AbuPickStockWorkBase()

    def test_class_exists(self):
        """Verify class exists and is abstract."""
        assert AbuPickStockWorkBase is not None
        assert hasattr(AbuPickStockWorkBase, "__abstractmethods__")
