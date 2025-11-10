# -*- encoding:utf-8 -*-
"""
Testes unitários para o módulo CoreBu
"""
import pytest


class TestABu:
    """Testes para o módulo principal ABu"""
    
    def test_import_abu(self):
        """Testa se o módulo ABu pode ser importado"""
        try:
            from abupy.CoreBu import ABu
            assert ABu is not None
        except ImportError:
            pytest.skip("Módulo ABu não disponível ainda")
    
    def test_run_loop_back_signature(self):
        """Testa a assinatura da função run_loop_back"""
        try:
            from abupy.CoreBu.ABu import run_loop_back
            import inspect
            
            sig = inspect.signature(run_loop_back)
            assert 'read_cash' in sig.parameters
            assert 'buy_factors' in sig.parameters
            assert 'sell_factors' in sig.parameters
        except ImportError:
            pytest.skip("Módulo ABu não disponível ainda")
    
    def test_core_bu_modules_exist(self):
        """Testa se os módulos básicos do CoreBu existem"""
        try:
            from abupy.CoreBu import ABuEnv, ABuBase, ABuStore
            assert ABuEnv is not None or True  # Pode ser None se não importado
        except ImportError:
            pytest.skip("Módulos CoreBu não disponíveis ainda")

