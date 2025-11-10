# -*- encoding:utf-8 -*-
"""
Testes unitários para o módulo CoreBu
"""
import pytest


class TestABu:
    """Testes para o módulo principal ABu"""
    
    def test_import_abu(self):
        """Testa se o módulo ABu pode ser importado"""
        from abupy.CoreBu import ABu
        assert ABu is not None
    
    def test_run_loop_back_signature(self):
        """Testa a assinatura da função run_loop_back"""
        from abupy.CoreBu.ABu import run_loop_back
        import inspect
        
        sig = inspect.signature(run_loop_back)
        assert 'read_cash' in sig.parameters
        assert 'buy_factors' in sig.parameters
        assert 'sell_factors' in sig.parameters

