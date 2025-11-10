# -*- encoding:utf-8 -*-
"""
Configurações centralizadas do projeto usando variáveis de ambiente.

Este módulo utiliza pydantic-settings para gerenciar configurações do projeto,
permitindo carregamento de variáveis de ambiente e arquivo .env.
"""
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Configurações do projeto.
    
    Todas as configurações podem ser definidas via variáveis de ambiente
    ou arquivo .env. Valores padrão são fornecidos para desenvolvimento.
    """
    
    # Configurações de Mercado
    market_target: str = "US"
    data_fetch_mode: str = "LOCAL"
    
    # Configurações de Trading
    initial_capital: float = 1000000.0
    commission_rate: float = 0.001
    
    # Configurações de Logging
    log_level: str = "INFO"
    log_file: str = "logs/crypto_trading.log"
    
    # Configurações de API (opcional)
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    api_base_url: Optional[str] = None
    
    # Configurações de Banco de Dados (opcional)
    database_url: Optional[str] = None
    
    # Configurações de Desenvolvimento
    debug: bool = False
    testing: bool = False
    
    # Diretórios do projeto (não vêm de env, calculados)
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    def __init__(self, **kwargs):
        """Initialize settings and create necessary directories."""
        super().__init__(**kwargs)
        # Calcular diretórios após inicialização
        project_root = Path(__file__).parent.parent
        self.project_root: Path = project_root
        self.data_dir: Path = project_root / "data"
        self.logs_dir: Path = project_root / "logs"
        
        # Criar diretórios necessários
        self.logs_dir.mkdir(exist_ok=True, parents=True)
        self.data_dir.mkdir(exist_ok=True, parents=True)


# Instância global de configurações
settings = Settings()

