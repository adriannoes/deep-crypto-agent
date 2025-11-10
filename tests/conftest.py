# -*- encoding:utf-8 -*-
"""
Configuração compartilhada do pytest para todos os testes
"""
import sys
from pathlib import Path

# Adiciona o diretório raiz ao path para imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest


@pytest.fixture
def sample_kl_data():
    """Fixture com dados de exemplo de K-line para testes"""
    import pandas as pd
    import numpy as np
    
    dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
    data = {
        'date': dates,
        'open': np.random.uniform(100, 200, 100),
        'high': np.random.uniform(200, 300, 100),
        'low': np.random.uniform(50, 100, 100),
        'close': np.random.uniform(100, 200, 100),
        'volume': np.random.uniform(1000, 10000, 100),
    }
    df = pd.DataFrame(data)
    df.set_index('date', inplace=True)
    return df


@pytest.fixture
def sample_capital():
    """Fixture com capital de exemplo para testes"""
    return 1000000.0


@pytest.fixture
def sample_benchmark():
    """Fixture com benchmark de exemplo para testes"""
    # Mock benchmark object - será implementado quando necessário
    class MockBenchmark:
        def __init__(self):
            self.name = "TEST_BENCHMARK"
    
    return MockBenchmark()

