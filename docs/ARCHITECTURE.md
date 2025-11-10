# Arquitetura do Sistema

## Visão Geral

O projeto crypto-trading é composto por duas arquiteturas principais:

1. **abupy/** - Sistema legado baseado no ABU Quantitative System
2. **crypto_quant_pro/** - Nova arquitetura moderna em desenvolvimento

## Arquitetura Legada (abupy/)

### Estrutura Modular

O sistema ABU é organizado em módulos funcionais (Bu = Business Unit):

- **AlphaBu**: Seleção de ações e timing de entrada
- **BetaBu**: Gerenciamento de posições e risco
- **CoreBu**: Núcleo do sistema, funções principais
- **FactorBuyBu**: Fatores de compra (estratégias de entrada)
- **FactorSellBu**: Fatores de venda (estratégias de saída)
- **TradeBu**: Execução de ordens e gerenciamento de capital
- **MarketBu**: Acesso a dados de mercado
- **MetricsBu**: Métricas de performance
- **MLBu**: Machine Learning
- **UtilBu**: Utilitários diversos

### Fluxo de Execução

```
1. Configuração inicial (capital, fatores, mercado)
   ↓
2. Seleção de ações (AlphaBu)
   ↓
3. Coleta de dados históricos (MarketBu)
   ↓
4. Aplicação de fatores de compra (FactorBuyBu)
   ↓
5. Gerenciamento de posição (BetaBu)
   ↓
6. Execução de ordens (TradeBu)
   ↓
7. Aplicação de fatores de venda (FactorSellBu)
   ↓
8. Cálculo de métricas (MetricsBu)
```

### Classes Base

- `AbuFactorBuyBase`: Base para fatores de compra
- `AbuPositionBase`: Base para gerenciamento de posições
- `AbuPickTimeWorkBase`: Base para timing
- `AbuPickStockWorkBase`: Base para seleção de ações

## Nova Arquitetura (crypto_quant_pro/)

### Estrutura Planejada

```
crypto_quant_pro/
├── api/              # APIs GraphQL
├── core/             # Engines e estratégias
│   ├── engines/      # Motores de execução
│   └── strategies/   # Estratégias de trading
├── data/             # Dados e processamento
│   ├── feeds/        # Fontes de dados
│   ├── processing/  # Processamento de dados
│   └── storage/      # Armazenamento
├── ml/               # Machine Learning
│   ├── models/       # Modelos ML
│   ├── training/     # Treinamento
│   └── inference/    # Inferência
└── web/              # Interface web
    └── frontend/     # Frontend React/Vue
```

### Princípios de Design

1. **Separação de Responsabilidades**: Cada módulo tem uma responsabilidade clara
2. **Extensibilidade**: Fácil adicionar novas estratégias e fontes de dados
3. **Testabilidade**: Código testável com mocks e interfaces claras
4. **Performance**: Otimizado para processamento paralelo

## Estratégia de Migração

### Fase 1: Coexistência
- Manter ambos os sistemas funcionando
- Migrar módulos gradualmente
- Manter compatibilidade de API

### Fase 2: Integração
- Criar adaptadores entre sistemas
- Migrar funcionalidades críticas primeiro
- Testes de regressão

### Fase 3: Consolidação
- Deprecar código legado
- Documentar migração completa
- Remover código não utilizado

## Decisões de Arquitetura

### Por que manter abupy/?
- Código funcional e testado
- Base de usuários existente
- Migração gradual reduz riscos

### Por que criar crypto_quant_pro/?
- Arquitetura moderna e extensível
- Melhor separação de responsabilidades
- Facilita testes e manutenção
- Suporte a tecnologias modernas (GraphQL, async, etc.)

## Tecnologias Utilizadas

### Backend
- Python 3.9+
- NumPy, Pandas para análise de dados
- Scikit-learn para ML
- Pydantic para validação de dados

### Frontend (planejado)
- React/Vue.js
- GraphQL para APIs
- Chart.js/D3.js para visualizações

### Infraestrutura
- Docker (planejado)
- CI/CD com GitHub Actions
- Logging estruturado

## Próximos Passos

1. Completar estrutura básica de crypto_quant_pro/
2. Implementar adaptadores entre sistemas
3. Migrar funcionalidades críticas
4. Documentar APIs e interfaces

