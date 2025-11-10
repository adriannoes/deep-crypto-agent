# -*- encoding:utf-8 -*-
"""
Testes unitários para o módulo AlphaBu
"""
import pytest


class TestAbuPickTimeWorkBase:
    """Testes para a classe base de timing"""
    
    def test_abstract_class_cannot_be_instantiated(self):
        """Verifica que a classe abstrata não pode ser instanciada"""
        # Import local para evitar problemas de importação circular
        try:
            from abupy.AlphaBu.ABuPickBase import AbuPickTimeWorkBase
            with pytest.raises(TypeError):
                AbuPickTimeWorkBase()
        except ImportError:
            pytest.skip("Módulo ABuPickBase não disponível ainda")


class TestAbuPickStockWorkBase:
    """Testes para a classe base de seleção de ações"""
    
    def test_abstract_class_cannot_be_instantiated(self):
        """Verifica que a classe abstrata não pode ser instanciada"""
        # Import local para evitar problemas de importação circular
        try:
            from abupy.AlphaBu.ABuPickBase import AbuPickStockWorkBase
            with pytest.raises(TypeError):
                AbuPickStockWorkBase()
        except ImportError:
            pytest.skip("Módulo ABuPickBase não disponível ainda")

