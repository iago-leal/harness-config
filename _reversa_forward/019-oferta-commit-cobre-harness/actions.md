# Actions: oferta de commit pendente cobre o vão de `.harness/`

> Identificador: `019-oferta-commit-cobre-harness`
> Data: `2026-06-30`
> Roadmap: `_reversa_forward/019-oferta-commit-cobre-harness/roadmap.md`

## Resumo

| Métrica                     | Valor                                |
| --------------------------- | ------------------------------------ |
| Total de ações              | 10                                   |
| Paralelizáveis (`[//]`)     | 4                                    |
| Maior cadeia de dependência | 5 (T001 → T003 → T006 → T007 → T009) |

## Fase 1, Preparação

| ID   | Descrição                                                                                                       | Dependências | Paralelismo | Arquivo alvo                                      | Confidência | Status |
| ---- | --------------------------------------------------------------------------------------------------------------- | ------------ | ----------- | ------------------------------------------------- | ----------- | ------ |
| T001 | Definir a constante `SYNC_CACHE_GITIGNORE_ENTRY = ".harness/sync-cache.json"` ao lado de `CORE_GITIGNORE_ENTRY` | -            | `[//]`      | `.harness/harness-core/src/core/domain/layout.py` | 🟢          | `[X]`  |

## Fase 2, Testes

| ID   | Descrição                                                                                                                                                                                                                                    | Dependências | Paralelismo | Arquivo alvo                                     | Confidência | Status |
| ---- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ | ----------- | ------------------------------------------------ | ----------- | ------ |
| T002 | Testes (red) de `pending_work_paths`: `.harness/decisoes/MD-*.md` e `.harness/microdecisoes.md` entram no conjunto; `.harness/estado-da-sessao.md` como único sujo → conjunto vazio; trabalho fora de `.harness/` preservado (regressão 016) | -            | `[//]`      | `.harness/harness-core/tests/test_close_flow.py` | 🟢          | `[X]`  |
| T003 | Teste (red) da salvaguarda gitignore: `init` garante `.harness/sync-cache.json` no `.gitignore` (além de `.harness/harness-core/`), idempotente                                                                                              | T001         | -           | `.harness/harness-core/tests/test_init.py`       | 🟢          | `[X]`  |
| T004 | Atualizar a asserção de versão para `1.2.56` (red contra 1.2.55)                                                                                                                                                                             | -            | -           | `.harness/harness-core/tests/test_init.py`       | 🟢          | `[X]`  |

## Fase 3, Núcleo

| ID   | Descrição                                                                                                                                                                                                                                                                  | Dependências | Paralelismo | Arquivo alvo                                                                        | Confidência | Status |
| ---- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ | ----------- | ----------------------------------------------------------------------------------- | ----------- | ------ |
| T005 | Estreitar `pending_work_paths`: substituir a exclusão do diretório `.harness/` por `p != session_file`; atualizar a docstring para refletir "exceto o arquivo de estado"                                                                                                   | T002         | `[//]`      | `.harness/harness-core/src/core/session/close_flow.py`                              | 🟢          | `[X]`  |
| T006 | Garantir `.harness/sync-cache.json` no `.gitignore` do alvo, chamando `_ensure_gitignore_entry` com `SYNC_CACHE_GITIGNORE_ENTRY` nos dois pontos (`initialize_project` in-process e `upgrade_project`)                                                                     | T001, T003   | `[//]`      | `.harness/harness-core/src/core/bootstrap/init_service.py`                          | 🟢          | `[X]`  |
| T007 | Bump `1.2.55 → 1.2.56` em lockstep nos pontos de produção: `version` em `config.py` e `current_version` em `init_service.py`                                                                                                                                               | T004, T006   | -           | `.harness/harness-core/src/core/domain/config.py` + `.../bootstrap/init_service.py` | 🟢          | `[X]`  |
| T010 | **(descoberta na execução)** Expandir `list_dirty_paths` com `--untracked-files=all` para granularidade de arquivo em subdiretórios não rastreados, com teste no adapter real; sem isso o porcelain colapsa `.harness/` numa linha e o filtro não separa o estado do resto | T005         | -           | `.harness/harness-core/src/adapters/git/subprocess.py` + `tests/test_git_dirty.py`  | 🟢          | `[X]`  |

## Fase 4, Integração

| ID   | Descrição                                                                                                                                                                                               | Dependências | Paralelismo | Arquivo alvo                                           | Confidência | Status |
| ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ | ----------- | ------------------------------------------------------ | ----------- | ------ |
| T008 | Alinhar os textos de borda à nova semântica: mensagem TTY de `conduct_commit_pendente` ("exceto o estado de sessão", não "fora de .harness/") e ponteiro de contrato de `render_commit_pendente_marker` | T005         | -           | `.harness/harness-core/src/core/session/close_flow.py` | 🟢          | `[X]`  |

## Fase 5, Polimento

| ID   | Descrição                                                                                                                                            | Dependências                 | Paralelismo | Arquivo alvo                   | Confidência | Status |
| ---- | ---------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------- | ----------- | ------------------------------ | ----------- | ------ |
| T009 | Executar a suíte do core e o smoke dos cenários A–D do `onboarding.md`; confirmar verde (`pending_work_paths`, gitignore idempotente, versão 1.2.56) | T005, T006, T007, T008, T010 | -           | `.harness/harness-core/tests/` | 🟢          | `[X]`  |

## Notas de execução

- **T010 nasceu do smoke real.** A suíte com `FakeGit` entregava `list_dirty_paths` já expandido em arquivos, mascarando que o `git status --porcelain` (sem `--untracked-files=all`) **colapsa subdiretórios não rastreados** numa única linha (ex.: `.harness/`). Com isso, `pending_work_paths` veria o diretório inteiro — não conseguindo separar o `estado-da-sessao.md`. O smoke num repo git real pegou `['.gitignore', '.harness/', 'src/']`; a correção (`-uall`) restaurou a granularidade. Lição: o oráculo real revela o que o mock esconde.
- Escopo deliberadamente **fora** desta feature (faxina futura): a divergência de nome do cache — `.harness/sync-cache.json` (hífen, em `close_flow.py`/`main.py`) vs `.harness/sync_cache.json` (underscore, em `adapters/mcp/server.py`). T006 ignora apenas o nome canônico do fluxo de encerramento (hífen).

## Histórico de alterações

| Data       | Alteração                                                                | Autor   |
| ---------- | ------------------------------------------------------------------------ | ------- |
| 2026-06-30 | Versão inicial gerada por `/reversa-to-do`                               | reversa |
| 2026-06-30 | Execução completa (T001–T010, `[X]`); T010 acrescentada na implementação | reversa |
