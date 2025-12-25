# Crypto Trading - Sistema de Trading Quantitativo

Sistema de trading quantitativo para criptomoedas baseado no framework ABU (ABU Quantitative System), com arquitetura moderna e extensível.

## 📋 Visão Geral

Este projeto combina o sistema legado ABU com uma nova arquitetura moderna (`crypto_quant_pro`) para criar uma plataforma completa de trading quantitativo. O sistema suporta:

- **Backtesting** de estratégias de trading
- **Análise técnica** quantitativa
- **Machine Learning** para otimização de estratégias
- **Gerenciamento de posições** e risco
- **Múltiplos mercados**: ações, futuros, opções e criptomoedas

## 🏗️ Estrutura do Projeto

```
crypto-trading/
├── abupy/                    # Sistema legado ABU (em migração)
│   ├── AlphaBu/             # Módulo de seleção e timing
│   ├── BetaBu/              # Gerenciamento de posições
│   ├── CoreBu/              # Núcleo do sistema
│   ├── FactorBuyBu/         # Fatores de compra
│   ├── FactorSellBu/        # Fatores de venda
│   ├── TradeBu/             # Módulo de trading
│   └── ...                  # Outros módulos
│
├── crypto_quant_pro/         # Nova arquitetura moderna (em desenvolvimento)
│   ├── api/                 # APIs GraphQL
│   ├── core/                # Engines e estratégias
│   ├── data/                # Feeds e processamento de dados
│   ├── ml/                  # Machine Learning
│   └── web/                 # Interface web
│
├── legacy/                   # Arquivos legados (referência histórica)
│   └── notebooks/          # Notebooks Jupyter originais
│
├── tests/                    # Testes automatizados
│   ├── unit/               # Testes unitários
│   └── integration/        # Testes de integração
│
├── docs/                     # Documentação
├── config/                   # Configurações
└── pyproject.toml          # Configuração e dependências Python
```

## 🚀 Instalação

### Pré-requisitos

- Python 3.9 ou superior
- pip ou poetry

### Instalação Básica

1. Clone o repositório:
```bash
git clone https://github.com/adrianno/crypto-trading.git
cd crypto-trading
```

2. Crie um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

3. Instale as dependências:
```bash
pip install -e .
```

### Instalação para Desenvolvimento

Para desenvolvimento, instale também as dependências de desenvolvimento:

```bash
pip install -e ".[dev]"
pre-commit install  # Instala hooks de pré-commit
```

## 📖 Uso Básico

### Exemplo de Backtesting

```python
from abupy import abu
from abupy.FactorBuyBu import AbuFactorBuyBreak
from abupy.FactorSellBu import AbuFactorAtrNStop

# Configurar fatores de compra e venda
buy_factors = [{'xd': 60, 'class': AbuFactorBuyBreak}]
sell_factors = [{'stop_loss_n': 0.5, 'stop_win_n': 3.0, 'class': AbuFactorAtrNStop}]

# Executar backtesting
result, kl_manager = abu.run_loop_back(
    read_cash=1000000,
    buy_factors=buy_factors,
    sell_factors=sell_factors,
    n_folds=2
)
```

### Atualizar Dados de Mercado

```python
from abupy import abu, EMarketTargetType

# Configurar mercado alvo
abupy.env.g_market_target = EMarketTargetType.E_MARKET_TARGET_US

# Atualizar dados históricos
abu.run_kl_update(n_folds=2)
```

## 🧪 Testes

Execute os testes com pytest:

```bash
# Todos os testes
pytest

# Apenas testes unitários
pytest tests/unit/

# Com cobertura
pytest --cov=abupy --cov=crypto_quant_pro
```

## 🛠️ Desenvolvimento

### Comandos Úteis

```bash
# Formatar código
ruff format .

# Verificar código
ruff check .

# Type checking
mypy abupy/

# Rodar todos os checks
make lint
```

### Estrutura de Commits

Este projeto segue [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` Nova funcionalidade
- `fix:` Correção de bug
- `docs:` Documentação
- `test:` Testes
- `refactor:` Refatoração
- `chore:` Manutenção

## 📚 Documentação

Documentação adicional disponível em:

- [Arquitetura](docs/ARCHITECTURE.md) - Visão geral da arquitetura do sistema
- [Guia de Contribuição](docs/CONTRIBUTING.md) - Como contribuir para o projeto
- [Guia de Desenvolvimento](docs/DEVELOPMENT.md) - Setup e desenvolvimento local
- [Estratégia de Migração](docs/MIGRATION.md) - Migração do ABU legado

## 🔄 Status do Projeto

### Sistema Legado (abupy/)
- ✅ Módulos base implementados
- ✅ Classes abstratas definidas
- ⚠️ Em processo de migração para nova arquitetura

### Nova Arquitetura (crypto_quant_pro/)
- 🚧 Estrutura definida
- 🚧 Em desenvolvimento ativo

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Leia o [Guia de Contribuição](docs/CONTRIBUTING.md)
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'feat: adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está licenciado sob a GPL-3.0 License - veja o arquivo LICENSE para detalhes.

## 🙏 Agradecimentos

Este projeto é baseado no [ABU Quantitative System](https://github.com/bbfamily/abu), um sistema quantitativo abrangente desenvolvido pela comunidade.

## 📞 Contato

Para questões e suporte, abra uma [issue](https://github.com/adrianno/crypto-trading/issues) no GitHub.

---

**Nota**: Este projeto está em desenvolvimento ativo. APIs podem mudar sem aviso prévio.
