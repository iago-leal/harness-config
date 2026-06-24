# Actions: Reprodutibilidade e Configuração Viva de Formatação

> Identificador: `008-reprodutibilidade-e-config`
> Data: `2026-06-24`
> Roadmap: `_reversa_forward/008-reprodutibilidade-e-config/roadmap.md`

## Resumo

| Métrica | Valor |
|---------|-------|
| Total de ações | 10 |
| Paralelizáveis (`[//]`) | 5 |
| Maior cadeia de dependência | 5 (T004 → T005 → T007 → T009 → T010) |

## Fase 1, Preparação

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T001 | Criar o arquivo `harness-core/requirements.in` com as dependências de alto nível do projeto | - | `[//]` | `harness-core/requirements.in` | 🟢 | `[X]` |
| T002 | Compilar as dependências usando `uv pip compile` para gerar o `requirements.txt` travado | T001 | - | `harness-core/requirements.txt` | 🟢 | `[X]` |

## Fase 2, Testes

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T003 | Escrever testes automatizados em `tests/test_formatting.py` cobrindo opt-out dinâmico e exclusão de caminhos via glob/prefixos | - | `[//]` | `harness-core/tests/test_formatting.py` | 🟢 | `[X]` |

## Fase 3, Núcleo

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T004 | Atualizar o construtor de `FormattingService` para receber `config: Optional[HarnessConfig]` opcionalmente | - | `[//]` | `harness-core/src/core/formatting/service.py` | 🟢 | `[X]` |
| T005 | Implementar a busca do arquivo de opt-out dinâmico configurado em `config.formatting.opt_out_file` | T004 | - | `harness-core/src/core/formatting/service.py` | 🟢 | `[X]` |
| T006 | Implementar o filtro e exclusão de formatação para os caminhos e globs definidos em `config.formatting.exclude_paths` | T004 | - | `harness-core/src/core/formatting/service.py` | 🟢 | `[X]` |

## Fase 4, Integração

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T007 | Injetar a configuração tipada carregada ao instanciar o `FormattingService` na CLI e no servidor MCP | T005, T006 | - | `harness-core/src/main.py`, `harness-core/src/adapters/mcp/server.py` | 🟢 | `[X]` |
| T008 | Criar o pipeline de CI do GitHub Actions em `.github/workflows/ci.yml` configurado com `uv` | T002 | `[//]` | `.github/workflows/ci.yml` | 🟢 | `[X]` |

## Fase 5, Polimento

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T009 | Executar toda a suíte pytest no core original para confirmar estabilidade e corretude física | T003, T007, T008 | - | `harness-core/` | 🟢 | `[X]` |
| T010 | Recompilar a documentação HTML estática rodando o gerador local do Harness | T009 | `[//]` | `harness-docs.html` | 🟢 | `[X]` |

## Notas de execução

<!-- Reservado para /reversa-coding. -->

## Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-06-24 | Versão inicial gerada por `/reversa-to-do` | reversa |
