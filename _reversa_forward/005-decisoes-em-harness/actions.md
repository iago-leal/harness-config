# Actions: Artefatos de decisão dentro de `.harness/`

> Identificador: `005-decisoes-em-harness`
> Data: `2026-06-23`
> Roadmap: `_reversa_forward/005-decisoes-em-harness/roadmap.md`

## Resumo

| Métrica | Valor |
|---------|-------|
| Total de ações | 8 |
| Paralelizáveis (`[//]`) | 4 |
| Maior cadeia de dependência | 3 (T003 → T005 → T007) |

## Fase 1, Preparação

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T001 | `git mv decisoes .harness/decisoes` e `git mv microdecisoes.md .harness/microdecisoes.md` (move MD-0001..0004 + `_cabecalho.md` + índice, preservando histórico) | - | `[//]` | `.harness/` | 🟢 | `[X]` |

## Fase 2, Testes

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T002 | Teste de `DecisionsSection`/`load_config`: defaults `.harness/decisoes`, `.harness/microdecisoes.md`, `.harness/decisoes/_cabecalho.md`; e override quando `[decisions]` está presente no toml | T003 | - | `harness-core/tests/test_domain.py` | 🟢 | `[X]` |

## Fase 3, Núcleo

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T003 | Criar `DecisionsSection` pydantic (campos `dir`, `index_file`, `header_file` com defaults `.harness/...`) e plugá-la em `HarnessConfig` | - | - | `harness-core/src/core/domain/config.py` | 🟢 | `[X]` |
| T004 | Adicionar seção `[decisions]` ao `harness.toml` com `dir`/`index_file`/`header_file` (chaves idênticas aos campos de T003) apontando para `.harness/...` | T003 | - | `harness-core/harness.toml` | 🟢 | `[X]` |
| T005 | No branch `decisions` do `main.py` (linhas 159-183), ler os 3 caminhos de `load_config(fs).decisions` em vez dos literais `"decisoes"`/`"microdecisoes.md"`/`"decisoes/_cabecalho.md"` | T003 | `[//]` | `harness-core/src/main.py` | 🟢 | `[X]` |
| T006 | No tool MCP `process_decisions` (`server.py:42-64`), tomar os defaults de `decisoes_dir`/`output_file` (e o `header_file` derivado) a partir de `load_config(fs).decisions` | T003 | `[//]` | `harness-core/src/adapters/mcp/server.py` | 🟢 | `[X]` |

## Fase 4, Integração

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T007 | Rodar `./harness decisions`: validar grafo com zero erros e regenerar `.harness/microdecisoes.md`; confirmar que o hook `Stop` (`.claude/settings.json`) opera sem mudança de comando e que a suíte (`pytest`) segue verde | T001, T005 | - | `.harness/microdecisoes.md` | 🟢 | `[X]` |

## Fase 5, Polimento

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T008 | Alinhar referências de documentação ao novo caminho: `src/core/install/template.md:42` cita `decisoes/MD-0001.md` (→ `.harness/decisoes/MD-0001.md`); varrer demais menções de doc à raiz | - | `[//]` | `harness-core/src/core/install/template.md` | 🟡 | `[X]` |

## Notas de execução

<!-- Reservado para /reversa-coding. -->

- Ordem crítica: T001 (move) deve preceder T007 (validação), senão `./harness decisions` gravaria um índice vazio sobre o novo local.
- T005 e T006 são `[//]` entre si (arquivos distintos, ambos dependem só de T003). Ao editá-los, ajustar asserts de caminho antigo em `tests/test_cli.py` / `tests/test_mcp.py` se existirem.

## Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-06-23 | Versão inicial gerada por `/reversa-to-do` | reversa |
