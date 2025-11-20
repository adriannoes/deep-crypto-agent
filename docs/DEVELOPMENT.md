# Guia de Desenvolvimento

Este guia fornece instruções detalhadas para configurar e trabalhar no ambiente de desenvolvimento.

## Pré-requisitos

- Python 3.10 ou superior (recomendado 3.11)
- pip ou poetry
- git
- Docker e Docker Compose (opcional, mas recomendado)
- (Opcional) pyenv para gerenciar versões do Python

## Configuração do Ambiente

### Opção 1: Usando Docker (Recomendado)

A forma mais fácil de começar é usando Docker:

```bash
# Clone o repositório
git clone https://github.com/adriannoes/crypto-trading.git
cd crypto-trading

# Construa e inicie os containers
docker-compose up -d

# Execute comandos dentro do container
docker-compose exec app pytest tests/
docker-compose exec app ruff check .

# Para parar os containers
docker-compose down
```

**Vantagens do Docker:**
- Ambiente isolado e consistente
- Não precisa instalar dependências localmente
- Banco de dados PostgreSQL e Redis incluídos
- Fácil de resetar o ambiente

### Opção 2: Instalação Local

#### 1. Clone o Repositório

```bash
git clone https://github.com/adriannoes/crypto-trading.git
cd crypto-trading
```

#### 2. Configure o Ambiente Virtual

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# Linux/Mac:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

#### 3. Instale as Dependências

```bash
# Instalação completa (recomendado)
make setup

# Ou manualmente:
pip install -r requirements.txt
pip install -r requirements-dev.txt
pre-commit install
```

### 4. Configure Variáveis de Ambiente

```bash
# Copie o arquivo de exemplo (se existir)
cp .env.example .env

# Edite .env com suas configurações
```

## Estrutura do Projeto

```
crypto-trading/
├── abupy/              # Sistema legado
├── crypto_quant_pro/   # Nova arquitetura
├── tests/              # Testes
├── docs/               # Documentação
├── config/             # Configurações
└── legacy/             # Arquivos legados
```

## Comandos de Desenvolvimento

### Testes

**Com Docker:**
```bash
# Todos os testes
docker-compose exec app pytest

# Apenas unitários
docker-compose exec app pytest tests/unit/

# Com cobertura
docker-compose exec app pytest --cov=abupy --cov=crypto_quant_pro

# Testes específicos
docker-compose exec app pytest tests/unit/test_abupy/test_core_bu.py
```

**Localmente:**
```bash
# Todos os testes
pytest

# Apenas unitários
pytest tests/unit/

# Com cobertura
pytest --cov=abupy --cov=crypto_quant_pro

# Testes específicos
pytest tests/unit/test_abupy/test_core_bu.py
```

### Qualidade de Código

**Com Docker:**
```bash
# Linting
docker-compose exec app ruff check .

# Formatação
docker-compose exec app ruff format .

# Type checking
docker-compose exec app mypy abupy/

# Todos os checks
docker-compose exec app make check
```

**Localmente:**
```bash
# Linting
ruff check .

# Formatação
ruff format .

# Type checking
mypy abupy/

# Todos os checks
make check
```

### Pre-commit Hooks

Os hooks são executados automaticamente antes de cada commit. Para rodar manualmente:

```bash
pre-commit run --all-files
```

## Workflow de Desenvolvimento

### 1. Criar uma Branch

```bash
git checkout -b feature/nome-da-feature
```

### 2. Desenvolver

- Escreva código
- Adicione testes
- Execute testes localmente
- Verifique qualidade do código

### 3. Commit

```bash
git add .
git commit -m "feat: descrição da mudança"
```

### 4. Push e PR

```bash
git push origin feature/nome-da-feature
```

Depois abra um Pull Request no GitHub.

## Debugging

### Logging

O projeto usa logging estruturado. Configure em `config/logging.yaml`:

```python
import logging
from config.settings import settings

# Configurar logging
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)
```

### Testes de Debug

```bash
# Rodar com output detalhado
pytest -v -s

# Parar no primeiro erro
pytest -x

# Rodar apenas testes que falharam anteriormente
pytest --lf
```

## Dicas

### Performance

- Use `pytest --profile` para identificar testes lentos
- Use `cProfile` para profiling de código Python

### Dependências

- Atualize `requirements.txt` ao adicionar novas dependências
- Use `pip freeze > requirements.txt` com cuidado (pode incluir dependências indesejadas)

### Documentação

- Atualize docstrings ao modificar funções
- Adicione exemplos de uso quando apropriado

## Troubleshooting

### Problemas Comuns

**Erro de importação:**
```bash
# Certifique-se de estar no diretório raiz
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

**Pre-commit falha:**
```bash
# Atualize hooks
pre-commit autoupdate
```

**Testes falham:**
```bash
# Limpe caches
make clean
pytest --cache-clear
```

## Recursos Adicionais

- [Documentação do Python](https://docs.python.org/3/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [Conventional Commits](https://www.conventionalcommits.org/)
