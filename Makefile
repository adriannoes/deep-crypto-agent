.PHONY: help install install-dev test test-unit test-integration lint format type-check clean run-pre-commit

# Variáveis
PYTHON := python3
PIP := pip
VENV := venv
PYTEST := pytest
RUFF := ruff
MYPY := mypy

help: ## Mostra esta mensagem de ajuda
	@echo "Comandos disponíveis:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Instala dependências principais
	$(PIP) install -r requirements.txt

install-dev: ## Instala dependências de desenvolvimento
	$(PIP) install -r requirements-dev.txt
	pre-commit install

test: ## Roda todos os testes
	$(PYTEST) tests/ -v

test-unit: ## Roda apenas testes unitários
	$(PYTEST) tests/unit/ -v

test-integration: ## Roda apenas testes de integração
	$(PYTEST) tests/integration/ -v -m integration

test-cov: ## Roda testes com cobertura
	$(PYTEST) tests/ --cov=abupy --cov=crypto_quant_pro --cov-report=term-missing --cov-report=html

lint: ## Verifica código com ruff
	$(RUFF) check .

lint-fix: ## Corrige problemas de linting automaticamente
	$(RUFF) check . --fix

format: ## Formata código com ruff
	$(RUFF) format .

format-check: ## Verifica formatação sem modificar arquivos
	$(RUFF) format . --check

type-check: ## Verifica tipos com mypy
	$(MYPY) abupy/ crypto_quant_pro/

check: lint format-check type-check ## Roda todos os checks (lint, format, type)

run-pre-commit: ## Roda pre-commit em todos os arquivos
	pre-commit run --all-files

clean: ## Limpa arquivos temporários e caches
	find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -r {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -r {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -r {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete
	rm -rf dist/ build/ .ruff_cache/

venv: ## Cria ambiente virtual
	$(PYTHON) -m venv $(VENV)
	@echo "Ambiente virtual criado. Ative com: source $(VENV)/bin/activate"

setup: venv install-dev ## Setup completo do ambiente de desenvolvimento
	@echo "Setup completo! Ative o ambiente virtual com: source $(VENV)/bin/activate"

