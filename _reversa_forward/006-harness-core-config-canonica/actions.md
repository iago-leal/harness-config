# Actions: harness-core como módulo per-projeto autocontido

> Identificador: `006-harness-core-config-canonica`
> Data: `2026-06-24`
> Roadmap: `_reversa_forward/006-harness-core-config-canonica/roadmap.md`

## Resumo

| Métrica                     | Valor                         |
| --------------------------- | ----------------------------- |
| Total de ações              | 11                            |
| Paralelizáveis (`[//]`)     | 6                             |
| Maior cadeia de dependência | 4 (T007 → T008 → T005 → T011) |

## Fase 1, Preparação

| ID   | Descrição                                                                                       | Dependências | Paralelismo | Arquivo alvo                | Confidência | Status |
| ---- | ----------------------------------------------------------------------------------------------- | ------------ | ----------- | --------------------------- | ----------- | ------ |
| T001 | Adicionar seção `[session]` ao `harness.toml` com `state_file = ".harness/estado-da-sessao.md"` | -            | `[//]`      | `harness-core/harness.toml` | 🟢          | `[X]`  |

## Fase 2, Testes

| ID   | Descrição                                                                                                                                                                                                                          | Dependências | Paralelismo | Arquivo alvo                           | Confidência | Status |
| ---- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ | ----------- | -------------------------------------- | ----------- | ------ |
| T002 | Criar duplo `RecordingFileSystem` (Spy de `FileSystemPort` que captura `write_file`/`write_file_atomic`/`makedirs`/`remove`)                                                                                                       | -            | `[//]`      | `harness-core/tests/helpers.py`        | 🟡          | `[X]`  |
| T003 | Teste de `SessionSection`/`load_config`: default `.harness/estado-da-sessao.md` e override quando `[session]` está presente no toml                                                                                                | T007         | -           | `harness-core/tests/test_domain.py`    | 🟢          | `[X]`  |
| T004 | Teste do contrato de footprint: exercitar `decisions`/sessão/`bootstrap` com `RecordingFileSystem` e afirmar que toda escrita cai dentro da raiz do repo; falha barulhenta se mirar `~/.claude`, `~/.agent-memory` ou fora do repo | T002         | -           | `harness-core/tests/test_footprint.py` | 🟡          | `[X]`  |
| T005 | Teste CLI: branch `cmd` lê o caminho de sessão de `config.session.state_file` e `active_harness` via `load_config`; confirmar que `load_harness_config` não é mais usado                                                           | T008         | -           | `harness-core/tests/test_cli.py`       | 🟢          | `[X]`  |
| T006 | Teste MCP: `session_command` lê o caminho de sessão de `config.session.state_file` (default idêntico ao literal anterior)                                                                                                          | T009         | -           | `harness-core/tests/test_mcp.py`       | 🟢          | `[X]`  |

## Fase 3, Núcleo

| ID   | Descrição                                                                                                                                                                       | Dependências | Paralelismo | Arquivo alvo                             | Confidência | Status |
| ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ | ----------- | ---------------------------------------- | ----------- | ------ |
| T007 | Criar `SessionSection` pydantic (campo `state_file`, default `.harness/estado-da-sessao.md`) e plugá-la em `HarnessConfig` (espelha `DecisionsSection`)                         | -            | `[//]`      | `harness-core/src/core/domain/config.py` | 🟢          | `[X]`  |
| T008 | Refactor `main.py`: remover `load_harness_config` (linhas 22-42 e o uso na 143); branch `cmd` lê `active_harness` (linha 214) e `session_file` (linha 193) de `load_config(fs)` | T007         | `[//]`      | `harness-core/src/main.py`               | 🟢          | `[X]`  |

## Fase 4, Integração

| ID   | Descrição                                                                                                                                                | Dependências | Paralelismo | Arquivo alvo                              | Confidência | Status |
| ---- | -------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ | ----------- | ----------------------------------------- | ----------- | ------ |
| T009 | No tool MCP `session_command` (`server.py:91-101`), tomar o `session_file` de `load_config(fs).session.state_file` em vez do literal chumbado (linha 93) | T007         | `[//]`      | `harness-core/src/adapters/mcp/server.py` | 🟢          | `[X]`  |

## Fase 5, Polimento

| ID   | Descrição                                                                                                                                            | Dependências                             | Paralelismo | Arquivo alvo                   | Confidência | Status |
| ---- | ---------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------- | ----------- | ------------------------------ | ----------- | ------ |
| T010 | Escrever `MD-NNNN` revertendo o `MD-0004` (decisão: `harness-core` é módulo per-projeto, não substituto da config global), com backlink ao `MD-0004` | -                                        | `[//]`      | `.harness/decisoes/MD-00NN.md` | 🟢          | `[X]`  |
| T011 | Rodar `./harness decisions` (valida o grafo com zero erros e reindexa `.harness/microdecisoes.md` incluindo o `MD-NNNN`) e `pytest` (suíte verde)    | T003, T004, T005, T006, T008, T009, T010 | -           | `harness-core/` (verificação)  | 🟢          | `[X]`  |

## Notas de execução

<!-- Reservado para /reversa-coding. -->

- Ordem crítica: `[session]` no toml (T001) e `SessionSection` (T007) com o **mesmo default** do literal atual (`.harness/estado-da-sessao.md`), para não exigir migração nem quebrar o estado existente.
- T008 e T009 são `[//]` entre si (arquivos distintos, ambos dependem só de T007). Ao editá-los, ajustar asserts de caminho de sessão em `test_cli.py`/`test_mcp.py` (T005/T006).
- T010 deve preceder T011: o `MD-NNNN` precisa existir antes de `./harness decisions` para entrar no índice.
- O contrato de footprint (T004) deve **logar** quais serviços foram exercitados, para não dar falsa cobertura (sem corte silencioso).

## Histórico de alterações

| Data       | Alteração                                                                                         | Autor   |
| ---------- | ------------------------------------------------------------------------------------------------- | ------- |
| 2026-06-24 | Versão inicial gerada por `/reversa-to-do`                                                        | reversa |
| 2026-06-24 | Todas as 11 ações executadas por `/reversa-coding` (suíte 63 verde; grafo validado com `MD-0005`) | reversa |
