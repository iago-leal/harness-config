# Actions: Upgrade resiliente do harness-core

> Identificador: `012-corrige-upgrade-stale`
> Data: `2026-06-25`
> Roadmap: `_reversa_forward/012-corrige-upgrade-stale/roadmap.md`

## Resumo

| Métrica                     | Valor |
| --------------------------- | ----- |
| Total de ações              | 19    |
| Paralelizáveis (`[//]`)     | 8     |
| Maior cadeia de dependência | 8     |

## Fase 1, Preparação

| ID   | Descrição                                                                                                                                                                                      | Dependências | Paralelismo | Arquivo alvo                                      | Confidência | Status |
| ---- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ | ----------- | ------------------------------------------------- | ----------- | ------ |
| T001 | Em `layout.py`, adicionar a fonte única dos caminhos-candidato do `config.py`: `CORE_CONFIG_CANDIDATE_RELPATHS` (canônico `.harness/harness-core/...` + legado raiz `harness-core/...`) (D-03) | -            | `[//]`      | `.harness/harness-core/src/core/domain/layout.py` | 🟢          | `[X]`  |

## Fase 2, Testes

| ID   | Descrição                                                                                                                                                                                                      | Dependências | Paralelismo | Arquivo alvo                                             | Confidência | Status |
| ---- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ | ----------- | -------------------------------------------------------- | ----------- | ------ |
| T002 | Teste de `_get_upstream_version` resiliente: resolve via candidato canônico, via candidato legado, e **levanta erro** quando nenhum existe (não retorna `current_version`) (D-02)                              | T001         | `[//]`      | `.harness/harness-core/tests/test_init.py`               | 🟢          | `[X]`  |
| T003 | Criar `test_upgrade_resilience.py` com o teste do Modo 1: montar upstream com materializador alterado + bump, rodar `upgrade` num alvo e asserir que o artefato é o **novo** (materialização não-stale) (D-01) | T001         | `[//]`      | `.harness/harness-core/tests/test_upgrade_resilience.py` | 🟢          | `[X]`  |
| T004 | Acrescentar teste do abort barulhento: versão do upstream indeterminada → `upgrade` falha (erro + exit ≠ 0), não imprime "Sucesso" e não copia (D-02)                                                          | T003         | -           | `.harness/harness-core/tests/test_upgrade_resilience.py` | 🟢          | `[X]`  |
| T005 | Acrescentar teste de `--force`: com versões iguais, `upgrade --force` recopia o core e rematerializa, sem encerrar por igualdade de versão (D-04)                                                              | T004         | -           | `.harness/harness-core/tests/test_upgrade_resilience.py` | 🟢          | `[X]`  |
| T006 | Teste de `SyncService.check_version_update` lendo a versão por caminhos-candidato (resolve via legado), mantendo a tolerância a erro não-bloqueante (D-05)                                                     | T001         | `[//]`      | `.harness/harness-core/tests/test_sync.py`               | 🟡          | `[X]`  |
| T007 | Teste do parser: o subcomando `upgrade` aceita a flag `--force` (default `False`) (D-04)                                                                                                                       | -            | `[//]`      | `.harness/harness-core/tests/test_cli.py`                | 🟢          | `[X]`  |

## Fase 3, Núcleo

| ID   | Descrição                                                                                                                                                                                                                                                                                                                | Dependências     | Paralelismo | Arquivo alvo                                               | Confidência | Status |
| ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------- | ----------- | ---------------------------------------------------------- | ----------- | ------ |
| T008 | Reescrever `_get_upstream_version` para varrer `CORE_CONFIG_CANDIDATE_RELPATHS` e **levantar erro** (ex.: `ValueError` com instrução de `init`) quando nenhum candidato resolve; remover o fallback `return self.current_version` (D-02)                                                                                 | T001             | -           | `.harness/harness-core/src/core/bootstrap/init_service.py` | 🟢          | `[X]`  |
| T009 | Criar módulo de materialização local com `apply_local_materializers(fs, project_path, command_path, active_harness)`: chama `materialize_session_commands` sempre e `materialize_hooks_json` quando `active_harness == "antigravity"` — função única (D-01)                                                              | -                | `[//]`      | `.harness/harness-core/src/core/install/local_apply.py`    | 🟢          | `[X]`  |
| T012 | Adicionar subcomando interno na CLI (ex.: `materialize`) que constrói os adaptadores, lê `active_harness` via `load_config` e `command_path = abspath(cwd)`, e chama `apply_local_materializers` (D-01)                                                                                                                  | T009             | -           | `.harness/harness-core/src/main.py`                        | 🟢          | `[X]`  |
| T011 | Em `initialize_project`, trocar as chamadas diretas dos dois materializadores pela função única `apply_local_materializers` (in-process; código já fresco no `init`) (D-01)                                                                                                                                              | T008, T009       | -           | `.harness/harness-core/src/core/bootstrap/init_service.py` | 🟢          | `[X]`  |
| T010 | Em `upgrade_project`, deixar o erro de versão indeterminada propagar (abort barulhento) e substituir as chamadas in-process dos materializadores por invocação do subcomando via subprocesso do python de destino (`[dst_python, dst_main, materialize]`, `cwd=target`), com guarda de presença da venv (D-01/D-02/D-06) | T008, T009, T012 | -           | `.harness/harness-core/src/core/bootstrap/init_service.py` | 🟢          | `[X]`  |
| T014 | Implementar `force` em `upgrade_project(target, force=False)`: quando `force`, pular a comparação de versão e converter o abort por versão indeterminada em aviso, sempre copiando + rematerializando; manter `version` se indeterminado (D-04)                                                                          | T010             | -           | `.harness/harness-core/src/core/bootstrap/init_service.py` | 🟢          | `[X]`  |
| T013 | Adicionar `--force` (`action="store_true"`) ao subparser `upgrade` e propagar para `service.upgrade_project(os.getcwd(), force=args.force)` no dispatch (D-04)                                                                                                                                                           | T012, T014       | -           | `.harness/harness-core/src/main.py`                        | 🟢          | `[X]`  |

## Fase 4, Integração

| ID   | Descrição                                                                                                                                                                                             | Dependências                                                                       | Paralelismo | Arquivo alvo                                     | Confidência | Status |
| ---- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- | ----------- | ------------------------------------------------ | ----------- | ------ |
| T015 | Em `SyncService.check_version_update`, ler a versão do upstream pelos caminhos-candidato (mesmo helper de `layout.py`), preservando o comportamento não-bloqueante e tolerante a erro (RN-N21) (D-05) | T001                                                                               | `[//]`      | `.harness/harness-core/src/core/sync/service.py` | 🟡          | `[X]`  |
| T016 | Rodar a suíte `pytest` completa e confirmar verde: init/upgrade, footprint, sync, cli, materializadores e os novos testes de resiliência do `upgrade`, sem regressão                                  | T002, T003, T004, T005, T006, T007, T008, T009, T010, T011, T012, T013, T014, T015 | -           | `.harness/harness-core/tests/`                   | 🟢          | `[X]`  |

## Fase 5, Polimento

| ID   | Descrição                                                                                                                                                                                          | Dependências | Paralelismo | Arquivo alvo                                                                                                  | Confidência | Status |
| ---- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ | ----------- | ------------------------------------------------------------------------------------------------------------- | ----------- | ------ |
| T017 | Bump de versão `1.2.47 → 1.2.48` em `config.py` e em `InitializationService.current_version` (D-08)                                                                                                | T016         | -           | `.harness/harness-core/src/core/domain/config.py`, `.harness/harness-core/src/core/bootstrap/init_service.py` | 🟢          | `[X]`  |
| T018 | Documentar a recuperação do layout antigo (`init` do upstream por caminho absoluto + remoção do `harness-core/` órfão) e a flag `upgrade --force` no material de instalação/uso (D-07)             | T014         | `[//]`      | `.harness/harness-core/src/core/install/template.md`                                                          | 🟡          | `[X]`  |
| T019 | Smoke conforme `onboarding.md` (Modo 1, abort, `--force`, recuperação) e **regenerar** os artefatos materializados a partir do código já corrigido pós-bump (mitiga o risco de distribuir o stale) | T017         | -           | (verificação)                                                                                                 | 🟡          | `[X]`  |

## Notas de execução

<!--
Reservado para /reversa-coding registrar avisos ou observações que surgiram durante a execução.
Não use isso para corrigir ações, edits manuais ficam fora desse arquivo, vão direto no código.
-->

## Histórico de alterações

| Data       | Alteração                                  | Autor   |
| ---------- | ------------------------------------------ | ------- |
| 2026-06-25 | Versão inicial gerada por `/reversa-to-do` | reversa |
