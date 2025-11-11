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

    # Diretórios do projeto (calculados, não vêm de env)
    project_root: Optional[Path] = None
    data_dir: Optional[Path] = None
    logs_dir: Optional[Path] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        arbitrary_types_allowed=True
    )

    def model_post_init(self, __context):
        """Initialize directories after model initialization."""
        # Calcular diretórios após inicialização
        project_root = Path(__file__).parent.parent
        object.__setattr__(self, 'project_root', project_root)
        object.__setattr__(self, 'data_dir', project_root / "data")
        object.__setattr__(self, 'logs_dir', project_root / "logs")

        # Criar diretórios necessários
        self.logs_dir.mkdir(exist_ok=True, parents=True)
        self.data_dir.mkdir(exist_ok=True, parents=True)


# Instância global de configurações
settings = Settings()
