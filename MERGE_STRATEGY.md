# Estratégia de Merge Requests - Crypto Trading Project

## 📊 Análise da Situação Atual

### Branches Pendentes de Merge

1. **`feat/strategies`** (Phase 2.3)
   - **Base**: `355d0f8d` (test fixes commit)
   - **Arquivos**: 12 arquivos, +1,867 linhas
   - **Conteúdo**: Sistema completo de estratégias (buy/sell)
   - **Dependências**: Requer `feat/core-engine` (já mergeado)

2. **`feat/risk-management`** (Phase 3.1)
   - **Base**: `355d0f8d` (test fixes commit)
   - **Arquivos**: 12 arquivos, +1,563 linhas
   - **Conteúdo**: Gestão de risco, position manager, portfolio optimizer
   - **Dependências**: Requer `feat/core-engine` (já mergeado)

3. **`feat/ml-and-metrics`** (Phase 3.2 + 3.3)
   - **Base**: `355d0f8d` (test fixes commit)
   - **Arquivos**: 31 arquivos, +3,853 linhas
   - **Conteúdo**: ML modules + Metrics modules + **INCLUI risk-management**
   - **Dependências**: Requer `feat/core-engine` (já mergeado)
   - **⚠️ PROBLEMA**: Esta branch inclui os arquivos de `feat/risk-management`

### Conflitos Identificados

**Arquivo com conflito potencial**: `crypto_quant_pro/core/__init__.py`

- `feat/strategies` adiciona imports de `strategies`
- `feat/risk-management` adiciona imports de `risk`
- `feat/ml-and-metrics` adiciona imports de `risk`, `metrics` e `ml`

**⚠️ ATENÇÃO**: `feat/ml-and-metrics` já inclui os arquivos de `feat/risk-management`, então:
- Se mergear `feat/risk-management` primeiro, `feat/ml-and-metrics` terá conflitos
- Se mergear `feat/ml-and-metrics` primeiro, `feat/risk-management` se torna redundante

---

## 🎯 Estratégia Recomendada

### Opção 1: Merge Sequencial (Recomendada)

**Ordem de merge**:

1. **`feat/strategies`** → `main`
   - ✅ Sem conflitos (apenas adiciona módulo novo)
   - ✅ Resolve conflito em `core/__init__.py` adicionando strategies
   - **PR Title**: `feat(strategies): implement strategy system (Phase 2.3)`
   - **Descrição**: Sistema completo de estratégias de compra/venda com adaptadores legados

2. **`feat/risk-management`** → `main`
   - ⚠️ Conflito esperado em `core/__init__.py` (já tem strategies)
   - ✅ Resolve adicionando imports de risk ao arquivo existente
   - **PR Title**: `feat(risk): implement risk management system (Phase 3.1)`
   - **Descrição**: Gestão de risco, position manager, portfolio optimizer, stop-loss

3. **`feat/ml-and-metrics`** → `main`
   - ⚠️ Conflito esperado em `core/__init__.py` (já tem strategies + risk)
   - ⚠️ Conflito potencial com arquivos de risk (já mergeados)
   - ✅ Resolve adicionando imports de metrics e ml
   - ✅ Resolve conflitos de risk mantendo versão já mergeada
   - **PR Title**: `feat(ml,metrics): implement ML and metrics modules (Phase 3.2 + 3.3)`
   - **Descrição**: ML modules (strategy optimizer, price predictor) + Metrics modules (performance, risk metrics, reports)

**Vantagens**:
- ✅ Merge incremental, mais fácil de revisar
- ✅ Cada PR focado em uma funcionalidade
- ✅ Conflitos menores e mais gerenciáveis
- ✅ Histórico limpo e organizado

**Desvantagens**:
- ⚠️ Requer resolução manual de conflitos em `core/__init__.py`
- ⚠️ `feat/ml-and-metrics` terá arquivos duplicados de risk (precisa remover)

---

### Opção 2: Merge Direto de `feat/ml-and-metrics` (Alternativa)

**Ordem de merge**:

1. **`feat/strategies`** → `main`
   - ✅ Sem conflitos

2. **`feat/ml-and-metrics`** → `main`
   - ⚠️ Conflito em `core/__init__.py` (já tem strategies)
   - ✅ Inclui risk-management, metrics e ml de uma vez
   - ⚠️ PR grande (31 arquivos, +3,853 linhas)

3. **Pular `feat/risk-management`** (já incluído em ml-and-metrics)

**Vantagens**:
- ✅ Menos merges totais
- ✅ Risk-management já incluído

**Desvantagens**:
- ⚠️ PR muito grande (difícil revisar)
- ⚠️ Mistura duas fases (3.2 + 3.3 + 3.1)
- ⚠️ Histórico menos granular

---

## 📝 Detalhamento dos Merge Requests

### PR #1: `feat/strategies` → `main`

**Branch**: `feat/strategies`
**Target**: `main`
**Tipo**: Feature
**Fase**: 2.3

**Arquivos modificados**:
- `crypto_quant_pro/core/__init__.py` (adiciona exports de strategies)
- `crypto_quant_pro/core/strategies/` (novo módulo completo)
- `tests/unit/test_crypto_quant_pro/core/strategies/` (testes)

**Conflitos esperados**: Nenhum (primeiro a modificar `core/__init__.py`)

**Checklist de merge**:
- [ ] Verificar que `feat/core-engine` está mergeado
- [ ] Resolver conflitos em `core/__init__.py` (se houver)
- [ ] Executar testes: `pytest tests/unit/test_crypto_quant_pro/core/strategies/`
- [ ] Verificar linting: `ruff check crypto_quant_pro/core/strategies/`
- [ ] Verificar type checking: `mypy crypto_quant_pro/core/strategies/`

---

### PR #2: `feat/risk-management` → `main`

**Branch**: `feat/risk-management`
**Target**: `main`
**Tipo**: Feature
**Fase**: 3.1

**Arquivos modificados**:
- `crypto_quant_pro/core/__init__.py` (adiciona exports de risk)
- `crypto_quant_pro/core/risk/` (novo módulo completo)
- `tests/unit/test_crypto_quant_pro/core/risk/` (testes)

**Conflitos esperados**:
- ⚠️ `crypto_quant_pro/core/__init__.py` (já tem strategies)

**Resolução de conflitos**:
```python
# Manter imports de strategies E adicionar imports de risk
from .strategies import (...)
from .risk import (...)
```

**Checklist de merge**:
- [ ] Verificar que `feat/strategies` está mergeado
- [ ] Resolver conflitos em `core/__init__.py` (adicionar risk aos imports existentes)
- [ ] Executar testes: `pytest tests/unit/test_crypto_quant_pro/core/risk/`
- [ ] Verificar linting: `ruff check crypto_quant_pro/core/risk/`
- [ ] Verificar type checking: `mypy crypto_quant_pro/core/risk/`

---

### PR #3: `feat/ml-and-metrics` → `main`

**Branch**: `feat/ml-and-metrics`
**Target**: `main`
**Tipo**: Feature
**Fase**: 3.2 + 3.3

**Arquivos modificados**:
- `crypto_quant_pro/core/__init__.py` (adiciona exports de metrics)
- `crypto_quant_pro/core/metrics/` (novo módulo)
- `crypto_quant_pro/core/risk/` (⚠️ duplicado, já mergeado em PR #2)
- `crypto_quant_pro/ml/` (novo módulo)
- Testes correspondentes

**Conflitos esperados**:
- ⚠️ `crypto_quant_pro/core/__init__.py` (já tem strategies + risk)
- ⚠️ `crypto_quant_pro/core/risk/` (arquivos já existem em main)

**Resolução de conflitos**:
1. **`core/__init__.py`**: Adicionar imports de metrics e ml aos existentes
2. **`core/risk/`**: **IGNORAR** arquivos de risk desta branch (manter versão já mergeada)
   - Usar `git checkout --theirs` para arquivos de risk
   - Ou remover arquivos de risk antes do merge

**Checklist de merge**:
- [ ] Verificar que `feat/risk-management` está mergeado
- [ ] Resolver conflitos em `core/__init__.py` (adicionar metrics + ml)
- [ ] **IMPORTANTE**: Ignorar arquivos de `core/risk/` desta branch (manter versão mergeada)
- [ ] Executar testes:
  - `pytest tests/unit/test_crypto_quant_pro/core/metrics/`
  - `pytest tests/unit/test_crypto_quant_pro/ml/`
- [ ] Verificar linting:
  - `ruff check crypto_quant_pro/core/metrics/`
  - `ruff check crypto_quant_pro/ml/`
- [ ] Verificar type checking:
  - `mypy crypto_quant_pro/core/metrics/`
  - `mypy crypto_quant_pro/ml/`

---

## 🔧 Comandos Úteis para Resolução de Conflitos

### Verificar conflitos antes do merge:
```bash
git checkout main
git merge --no-commit --no-ff feat/strategies
git merge --abort  # Se houver conflitos, abortar e resolver manualmente
```

### Resolver conflito em `core/__init__.py`:
```bash
# Manter ambas as seções de imports
# Estrutura final esperada:
from .engines import (...)
from .engines.abu_engine_adapter import AbuEngineAdapter
from .strategies import (...)  # Adicionado por feat/strategies
from .risk import (...)        # Adicionado por feat/risk-management
from .metrics import (...)     # Adicionado por feat/ml-and-metrics
from .ml import (...)          # Adicionado por feat/ml-and-metrics
```

### Ignorar arquivos duplicados de risk em `feat/ml-and-metrics`:
```bash
# Opção 1: Remover arquivos de risk antes do merge
git checkout feat/ml-and-metrics
git rm -r crypto_quant_pro/core/risk/
git commit -m "chore: remove risk files (already merged)"

# Opção 2: Durante merge, usar theirs para risk
git checkout --theirs crypto_quant_pro/core/risk/*
git add crypto_quant_pro/core/risk/
```

---

## 📋 Ordem Final Recomendada

### Sequência de Merge Requests no GitHub:

1. **PR #1**: `feat/strategies` → `main`
   - Título: `feat(strategies): implement strategy system (Phase 2.3)`
   - Labels: `feature`, `phase-2.3`
   - Reviewers: Atribuir revisores

2. **PR #2**: `feat/risk-management` → `main`
   - Título: `feat(risk): implement risk management system (Phase 3.1)`
   - Labels: `feature`, `phase-3.1`
   - Depende de: PR #1 (pode usar "depends on" no GitHub)

3. **PR #3**: `feat/ml-and-metrics` → `main`
   - Título: `feat(ml,metrics): implement ML and metrics modules (Phase 3.2 + 3.3)`
   - Labels: `feature`, `phase-3.2`, `phase-3.3`
   - Depende de: PR #2
   - **⚠️ ATENÇÃO**: Remover arquivos de `core/risk/` antes do merge ou resolver conflitos mantendo versão de main

---

## ✅ Checklist Final

Antes de criar os PRs no GitHub:

- [ ] Todas as branches estão atualizadas com `main`
- [ ] Testes passando em todas as branches
- [ ] Linting passando em todas as branches
- [ ] Type checking passando em todas as branches
- [ ] Documentação atualizada
- [ ] Commits seguem Conventional Commits

Durante o merge no GitHub:

- [ ] Usar "Squash and merge" ou "Create a merge commit" (não "Rebase and merge")
- [ ] Manter mensagens de commit descritivas
- [ ] Verificar que CI/CD passa antes de mergear
- [ ] Resolver conflitos conforme estratégia acima

Após o merge:

- [ ] Verificar que `main` compila sem erros
- [ ] Executar suite completa de testes
- [ ] Verificar que não há regressões
- [ ] Atualizar documentação se necessário

---

## 🚨 Problemas Conhecidos e Soluções

### Problema 1: `feat/ml-and-metrics` inclui risk-management

**Solução**:
- Opção A: Remover arquivos de risk de `feat/ml-and-metrics` antes do merge
- Opção B: Durante merge, usar `--theirs` para arquivos de risk (manter versão de main)

### Problema 2: Conflitos em `core/__init__.py`

**Solução**:
- Manter todas as seções de imports
- Ordem: engines → strategies → risk → metrics → ml
- Verificar que `__all__` inclui todos os exports

### Problema 3: Histórico de commits

**Solução**:
- Usar "Create a merge commit" no GitHub para preservar histórico
- Não usar "Squash and merge" (perde granularidade)
- Não usar "Rebase and merge" (pode causar problemas)

---

## 📚 Referências

- [GitHub Merge Strategies](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/incorporating-changes-from-a-pull-request/about-pull-request-merges)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Project Roadmap](./cursor-plan://ffae8201-91a5-49b2-8fe2-5997b8ff2a5c/Codebase Translation and Cleanup.plan.md)

---

**Última atualização**: 2024-12-19
**Autor**: AI Assistant
**Status**: Pronto para implementação
