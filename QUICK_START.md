# 🚀 Quick Start Guide

Guia rápido para começar a desenvolver no projeto crypto-trading.

## ⚡ Setup Rápido (5 minutos)

### 1. Verificar Ambiente

```bash
# Verificar Python (3.9+)
python --version

# Verificar se venv existe
ls venv/
```

### 2. Ativar Ambiente Virtual

```bash
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

### 3. Instalar Dependências (se necessário)

```bash
make install-dev
# ou manualmente:
pip install -r requirements-dev.txt
pre-commit install
```

### 4. Verificar Instalação

```bash
# Rodar testes
make test

# Verificar código
make lint
```

## 📝 Desenvolvimento

### Criar Nova Feature

```bash
# 1. Criar branch
git checkout -b feature/nova-funcionalidade

# 2. Desenvolver
# ... fazer mudanças ...

# 3. Testar
make test

# 4. Verificar qualidade
make check

# 5. Commit (pre-commit roda automaticamente)
git add .
git commit -m "feat: adiciona nova funcionalidade"
```

### Estrutura de Commits

Use [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` Nova funcionalidade
- `fix:` Correção de bug
- `docs:` Documentação
- `test:` Testes
- `refactor:` Refatoração
- `chore:` Manutenção

## 🧪 Testes

### Rodar Todos os Testes

```bash
make test
```

### Rodar Testes Específicos

```bash
# Apenas unitários
pytest tests/unit/ -v

# Apenas integração
pytest tests/integration/ -v

# Arquivo específico
pytest tests/unit/test_abupy/test_alpha_bu.py -v
```

### Com Cobertura

```bash
pytest --cov=abupy --cov=crypto_quant_pro --cov-report=html
# Abrir htmlcov/index.html no navegador
```

## 🔍 Qualidade de Código

### Verificar Código

```bash
make lint          # Ruff check
make format-check  # Verificar formatação
make type-check    # MyPy
make check         # Todos os checks
```

### Corrigir Automaticamente

```bash
make lint-fix      # Corrigir problemas de linting
make format        # Formatar código
```

## 📚 Documentação

- **README.md** - Visão geral do projeto
- **docs/DEVELOPMENT.md** - Guia completo de desenvolvimento
- **docs/CONTRIBUTING.md** - Como contribuir
- **docs/ARCHITECTURE.md** - Arquitetura do sistema
- **docs/MIGRATION.md** - Estratégia de migração

## 🛠️ Comandos Úteis

```bash
make help          # Ver todos os comandos disponíveis
make clean         # Limpar arquivos temporários
make test-cov      # Testes com cobertura
```

## 🐛 Troubleshooting

### Problemas de Importação

```bash
# Certifique-se de estar no diretório raiz
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Pre-commit Falha

```bash
# Atualizar hooks
pre-commit autoupdate

# Rodar manualmente
pre-commit run --all-files
```

### Testes Falham

```bash
# Limpar caches
make clean
pytest --cache-clear
```

## 📞 Ajuda

- Abra uma [issue](https://github.com/adrianno/crypto-trading/issues) no GitHub
- Consulte `docs/DEVELOPMENT.md` para mais detalhes
- Veja `docs/CONTRIBUTING.md` para contribuir

---

**Boa sorte no desenvolvimento! 🚀**
