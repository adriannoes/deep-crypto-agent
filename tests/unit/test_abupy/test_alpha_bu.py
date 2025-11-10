# -*- encoding:utf-8 -*-
"""
Testes unitários para o módulo AlphaBu
"""
import pytest
from abupy.AlphaBu.ABuPickBase import (
    AbuPickTimeWorkBase,
    AbuPickStockWorkBase,
)


class TestAbuPickTimeWorkBase:
    """Testes para a classe base de timing"""
    
    def test_abstract_class_cannot_be_instantiated(self):
        """Verifica que a classe abstrata não pode ser instanciada"""
        with pytest.raises(TypeError):
            AbuPickTimeWorkBase()


class TestAbuPickStockWorkBase:
    """Testes para a classe base de seleção de ações"""
    
    def test_abstract_class_cannot_be_instantiated(self):
        """Verifica que a classe abstrata não pode ser instanciada"""
        with pytest.raises(TypeError):
            AbuPickStockWorkBase()

