# -*- encoding:utf-8 -*-
"""
Testes unitários para o módulo BetaBu
"""
import pytest
from abupy.BetaBu.ABuPositionBase import AbuPositionBase


class TestAbuPositionBase:
    """Testes para a classe base de gerenciamento de posição"""
    
    def test_abstract_class_cannot_be_instantiated(self):
        """Verifica que a classe abstrata não pode ser instanciada"""
        with pytest.raises(TypeError):
            AbuPositionBase(None, None, None, None, None)
    
    def test_global_position_max(self):
        """Testa a configuração global de posição máxima"""
        from abupy.BetaBu import ABuPositionBase as pos_module
        original_max = pos_module.g_pos_max
        try:
            pos_module.g_pos_max = 0.5
            assert pos_module.g_pos_max == 0.5
        finally:
            pos_module.g_pos_max = original_max

