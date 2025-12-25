# Guia de Contribuição

Obrigado por considerar contribuir para o projeto crypto-trading! Este documento fornece diretrizes para contribuições.

## Como Contribuir

### Reportando Bugs

Se você encontrou um bug:

1. Verifique se o bug já não foi reportado nas [Issues](https://github.com/adrianno/crypto-trading/issues)
2. Se não foi reportado, crie uma nova issue com:
   - Descrição clara do problema
   - Passos para reproduzir
   - Comportamento esperado vs. atual
   - Versão do Python e dependências
   - Logs relevantes (se houver)

### Sugerindo Melhorias

Para sugerir novas funcionalidades:

1. Abra uma issue descrevendo a funcionalidade
2. Explique o caso de uso e benefícios
3. Discuta a implementação proposta (se aplicável)

### Enviando Pull Requests

1. **Fork o repositório**

2. **Crie uma branch para sua feature**
   ```bash
   git checkout -b feature/nova-funcionalidade
   ```

3. **Faça suas alterações**
   - Siga o estilo de código do projeto
   - Adicione testes para novas funcionalidades
   - Atualize documentação se necessário

4. **Commit suas mudanças**
   ```bash
   git commit -m "feat: adiciona nova funcionalidade"
   ```

   Use [Conventional Commits](https://www.conventionalcommits.org/):
   - `feat:` Nova funcionalidade
   - `fix:` Correção de bug
   - `docs:` Documentação
   - `test:` Testes
   - `refactor:` Refatoração
   - `chore:` Manutenção

5. **Push para sua branch**
   ```bash
   git push origin feature/nova-funcionalidade
   ```

6. **Abra um Pull Request**
   - Descreva suas mudanças
   - Referencie issues relacionadas
   - Aguarde revisão

## Padrões de Código

### Estilo de Código

- Siga PEP 8
- Use `ruff` para linting e formatação
- Linha máxima: 100 caracteres
- Use type hints quando possível

### Testes

- Adicione testes para novas funcionalidades
- Mantenha cobertura de código alta
- Testes devem ser rápidos e isolados

### Documentação

- Adicione docstrings seguindo Google ou NumPy style
- Atualize README.md se necessário
- Documente APIs públicas

## Ambiente de Desenvolvimento

### Setup Inicial

```bash
# Clone o repositório
git clone https://github.com/adrianno/crypto-trading.git
cd crypto-trading

# Crie ambiente virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instale dependências de desenvolvimento
make install-dev

# Ou manualmente:
pip install -e ".[dev]"
pre-commit install
```

### Comandos Úteis

```bash
# Rodar testes
make test

# Verificar código
make lint

# Formatar código
make format

# Type checking
make type-check

# Todos os checks
make check
```

## Processo de Revisão

1. **Revisão de Código**: Todas as PRs são revisadas
2. **Testes**: PRs devem passar em todos os testes
3. **Linting**: Código deve passar em todas as verificações
4. **Aprovação**: Pelo menos uma aprovação necessária

## Perguntas?

Se tiver dúvidas, abra uma issue ou entre em contato com os mantenedores.

Obrigado por contribuir! 🎉
