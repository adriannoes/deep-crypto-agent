# Estratégia de Migração: ABU → Crypto Quant Pro

Este documento descreve a estratégia de migração do sistema legado ABU (`abupy/`) para a nova arquitetura (`crypto_quant_pro/`).

## Visão Geral

A migração será realizada em fases, mantendo compatibilidade durante a transição e permitindo migração gradual de funcionalidades.

## Fases da Migração

### Fase 1: Coexistência (Atual)

**Status**: Em andamento

- Ambos os sistemas coexistem
- `abupy/` continua funcional
- `crypto_quant_pro/` em desenvolvimento inicial
- Compatibilidade mantida através de adaptadores

**Objetivos**:
- ✅ Estrutura básica de `crypto_quant_pro/` criada
- 🚧 Adaptadores entre sistemas
- 🚧 Documentação de APIs

### Fase 2: Integração

**Status**: Planejado

- Migração gradual de módulos
- Adaptadores para compatibilidade
- Testes de regressão
- Documentação de migração

**Módulos Prioritários**:
1. Data feeds (MarketBu → data/feeds)
2. Core engine (CoreBu → core/engines)
3. Strategies (FactorBuyBu/FactorSellBu → core/strategies)

### Fase 3: Consolidação

**Status**: Futuro

- Deprecar código legado
- Remover adaptadores não utilizados
- Documentação final
- Otimizações

## Mapeamento de Módulos

| ABU (Legado) | Crypto Quant Pro (Novo) | Status |
|--------------|------------------------|--------|
| MarketBu | data/feeds | 🚧 Planejado |
| CoreBu | core/engines | 🚧 Planejado |
| FactorBuyBu | core/strategies/buy | 🚧 Planejado |
| FactorSellBu | core/strategies/sell | 🚧 Planejado |
| BetaBu | core/position | 🚧 Planejado |
| TradeBu | core/execution | 🚧 Planejado |
| MLBu | ml/ | 🚧 Planejado |
| MetricsBu | core/metrics | 🚧 Planejado |

## Estratégia de Compatibilidade

### Adaptadores

Criar adaptadores que permitam usar código legado na nova arquitetura:

```python
# Exemplo de adaptador
class ABUAdapter:
    """Adapta chamadas do ABU para nova arquitetura"""
    def __init__(self, abu_module):
        self.abu_module = abu_module
    
    def execute(self, *args, **kwargs):
        # Adapta chamadas
        return self.abu_module.run(*args, **kwargs)
```

### Wrappers

Wrappers para manter APIs compatíveis durante migração:

```python
# Manter API antiga funcionando
def run_loop_back(*args, **kwargs):
    """Wrapper para compatibilidade"""
    # Usar nova implementação quando disponível
    # Fallback para implementação legada
    pass
```

## Checklist de Migração por Módulo

Para cada módulo migrado:

- [ ] Criar estrutura equivalente em `crypto_quant_pro/`
- [ ] Implementar funcionalidade básica
- [ ] Criar testes unitários
- [ ] Criar testes de integração
- [ ] Criar adaptador de compatibilidade
- [ ] Documentar API
- [ ] Atualizar documentação de migração
- [ ] Marcar módulo legado como deprecated
- [ ] Remover código legado (após período de transição)

## Testes de Regressão

Durante a migração, manter suite de testes que valida:

- Compatibilidade de APIs
- Resultados idênticos entre sistemas
- Performance aceitável
- Sem regressões funcionais

## Timeline Estimado

- **Fase 1**: 3-6 meses
- **Fase 2**: 6-12 meses
- **Fase 3**: 3-6 meses

**Total estimado**: 12-24 meses

## Decisões Arquiteturais

### Por que migrar?

1. **Manutenibilidade**: Código mais limpo e organizado
2. **Extensibilidade**: Mais fácil adicionar novas funcionalidades
3. **Performance**: Otimizações modernas
4. **Testabilidade**: Melhor cobertura de testes

### Por que migração gradual?

1. **Risco**: Reduz risco de quebrar funcionalidades existentes
2. **Continuidade**: Permite desenvolvimento contínuo
3. **Validação**: Validação incremental de cada módulo
4. **Aprendizado**: Aprendizado contínuo durante migração

## Contribuindo para a Migração

Se quiser ajudar na migração:

1. Escolha um módulo da lista de prioridades
2. Crie uma issue descrevendo sua abordagem
3. Implemente a migração seguindo o checklist
4. Abra um PR com testes e documentação

## Recursos

- [Arquitetura do Sistema](ARCHITECTURE.md)
- [Guia de Contribuição](CONTRIBUTING.md)
- [Guia de Desenvolvimento](DEVELOPMENT.md)

