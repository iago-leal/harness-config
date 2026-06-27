# Actions: encerrar-sessao autônomo — auto-reativa, regenera artefatos e commita o trabalho

> Identificador: `016-encerrar-sessao-autonomo`
> Data: `2026-06-27`
> Roadmap: `_reversa_forward/016-encerrar-sessao-autonomo/roadmap.md`

## Resumo

| Métrica                     | Valor                                       |
| --------------------------- | ------------------------------------------- |
| Total de ações              | 18                                          |
| Paralelizáveis (`[//]`)     | 11                                          |
| Maior cadeia de dependência | 6 (T001 → T010 → T013 → T014 → T016 → T018) |

## Fase 1, Preparação

| ID   | Descrição                                                                                                                              | Dependências | Paralelismo | Arquivo alvo                                                                               | Confidência | Status |
| ---- | -------------------------------------------------------------------------------------------------------------------------------------- | ------------ | ----------- | ------------------------------------------------------------------------------------------ | ----------- | ------ |
| T001 | Adicionar `RegenSection` (`command: Optional[str] = None`) e o campo `regen` em `HarnessConfig` (D-01)                                 | -            | `[//]`      | `src/core/domain/config.py`                                                                | 🟢          | `[X]`  |
| T002 | Incluir seção `[regen]` comentada (exemplo) no template de `harness.toml` gerado pelo `init` (D-01)                                    | -            | `[//]`      | `src/core/bootstrap/init_service.py`                                                       | 🟢          | `[X]`  |
| T003 | Bump de versão 1.2.52 → 1.2.53 nos três pontos sincronizados: `HarnessSection.version`, `current_version` e a asserção do teste (D-08) | T001, T002   | -           | `src/core/domain/config.py` (+ `src/core/bootstrap/init_service.py`, `tests/test_init.py`) | 🟢          | `[X]`  |

## Fase 2, Testes (TDD — devem falhar contra o código atual)

| ID   | Descrição                                                                                                                                                                                                                                                      | Dependências | Paralelismo | Arquivo alvo                            | Confidência | Status |
| ---- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ | ----------- | --------------------------------------- | ----------- | ------ |
| T004 | Teste: `load_config` parseia `[regen] command`; ausência → `regen.command is None`                                                                                                                                                                             | T001         | `[//]`      | `tests/test_config.py`                  | 🟢          | `[X]`  |
| T005 | Teste: `RegenService` — comando setado roda via `ProcessPort.run_command(["sh","-c",cmd], cwd)`; ausente → no-op (exit 0); falha do comando → erro/exit ≠ 0 (usar `ProcessPort` fake)                                                                          | T001         | `[//]`      | `tests/test_regen.py`                   | 🟢          | `[X]`  |
| T006 | Teste: `GitPort.list_dirty_paths` devolve os caminhos de `git status --porcelain` (repo temporário); árvore limpa → lista vazia                                                                                                                                | -            | `[//]`      | `tests/test_git_dirty.py`               | 🟢          | `[X]`  |
| T007 | Teste (serviço): `encerrar-sessao` sobre inativa → reativa + fecha + commit; ausente (`None`) → mensagem sem commit; ativa → inalterado; malformado → ainda levanta. **Adaptar** os testes da 015 que afirmavam `NoActiveSessionError` para ausente/inativa    | -            | `[//]`      | `tests/test_commands.py`                | 🟢          | `[X]`  |
| T008 | Teste (borda/CLI): inativa → exit 0 + anúncio de reativação; ausente → exit 0 sem commit; malformado → exit ≠ 0; trabalho solto → marker `[HARNESS:COMMIT_PENDENTE …]` e **não** fecha; `cmd regen` falho → exit ≠ 0. **Adaptar** asserções da 015 de exit ≠ 0 | -            | `[//]`      | `tests/test_cli.py`                     | 🟢          | `[X]`  |
| T009 | Teste: `materialize_claude_settings` cria `.claude/settings.json` com o hook de resume quando ausente; idempotente; preserva chaves e hooks de terceiros                                                                                                       | -            | `[//]`      | `tests/test_install_claude_settings.py` | 🟡          | `[X]`  |

## Fase 3, Núcleo

| ID   | Descrição                                                                                                                                                                                                                                                           | Dependências | Paralelismo | Arquivo alvo                                                 | Confidência | Status |
| ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ | ----------- | ------------------------------------------------------------ | ----------- | ------ |
| T010 | Implementar `RegenService(process)`: lê `config.regen.command`; ausente → no-op; executa via `ProcessPort` com `sh -c`; falha → exceção/saída barulhenta (D-02)                                                                                                     | T005, T001   | -           | `src/core/regen/service.py` (+ `__init__.py`)                | 🟢          | `[X]`  |
| T011 | Implementar `list_dirty_paths(repo_path) -> list[str]` no `GitPort` (abstrato) e no `SubprocessGitAdapter` (`git status --porcelain`, parse de caminhos) (D-04)                                                                                                     | T006         | `[//]`      | `src/core/ports/git.py` (+ `src/adapters/git/subprocess.py`) | 🟢          | `[X]`  |
| T012 | Reescrever o ramo `encerrar-sessao` em `CommandService`: ausente → mensagem "não havia sessão para encerrar" (sem commit); inativa → `start_session` (reativa) + `close_session` + commit; ativa → inalterado; recuar `NoActiveSessionError` nesses casos (D-03/D1) | T007         | `[//]`      | `src/core/commands/service.py`                               | 🟢          | `[X]`  |

## Fase 4, Integração

| ID   | Descrição                                                                                                                                                                                                                                                                                | Dependências     | Paralelismo | Arquivo alvo                                                                | Confidência | Status |
| ---- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------- | ----------- | --------------------------------------------------------------------------- | ----------- | ------ |
| T013 | Dispatch CLI: novo subcomando `cmd regen` (constrói `RegenService(process)`, lê `config.regen.command`, mapeia exit codes: ausente→0, falha→≠0) (D-02)                                                                                                                                   | T010             | -           | `src/main.py`                                                               | 🟢          | `[X]`  |
| T014 | Dispatch CLI: pré-check da working tree no `encerrar-sessao` — `git.list_dirty_paths`, filtrar `.harness/`, emitir marker `COMMIT_PENDENTE` (sem TTY) / perguntar (TTY) e early-return sem fechar; reconciliar o tratamento de exit agora que ausente/inativa são tolerantes (D-04/D-07) | T011, T012, T013 | -           | `src/main.py`                                                               | 🟢          | `[X]`  |
| T015 | `materialize_claude_settings(fs, project_path)` idempotente (merge não-destrutivo do hook de resume no `.claude/settings.json`) e ligá-lo em `apply_local_materializers` com gate `active_harness == "claude"` (D-05)                                                                    | T009             | `[//]`      | `src/core/install/claude_settings.py` (+ `src/core/install/local_apply.py`) | 🟡          | `[X]`  |
| T016 | Atualizar o conteúdo do slash command `encerrar-sessao` nos perfis (`ClaudeProfile`, `AntigravityProfile`): sequenciar `cmd regen` → `cmd encerrar-sessao` e instruir o agente a tratar o marker `COMMIT_PENDENTE` (D-06)                                                                | T012, T013, T014 | `[//]`      | `src/core/install/harness_profiles.py`                                      | 🟢          | `[X]`  |

## Fase 5, Polimento

| ID   | Descrição                                                                                                                                         | Dependências                             | Paralelismo | Arquivo alvo                     | Confidência | Status |
| ---- | ------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------- | ----------- | -------------------------------- | ----------- | ------ |
| T017 | Suíte do core verde: testes novos (T004–T009) + os da 015 adaptados; revisar mensagens barulhentas/observáveis (reativação, no-op, regen falho)   | T010, T011, T012, T013, T014, T015, T016 | `[//]`      | (verificação; sem arquivo único) | 🟢          | `[X]`  |
| T018 | Smoke end-to-end dos cenários do `onboarding.md` (A–F) + rematerialização em sandbox (claude) confirmando o hook de resume plantado e idempotente | T014, T015, T016                         | `[//]`      | (verificação; sem arquivo único) | 🟡          | `[X]`  |

## Notas de execução

- TDD respeitado: a Fase 2 foi escrita primeiro e confirmada vermelha (coleta falhava por `ModuleNotFoundError` de `src.core.regen` e `src.core.install.claude_settings`) antes do núcleo.
- Suíte final: **201 passed** (baseline 015 = 185; +16). `ruff check`/`format` limpos nos 21 arquivos da 016; as 2 marcações restantes do ruff (`parser_decisions`, `NotAGitRepositoryError` em `main.py`) são dívida pré-existente fora do escopo.
- `NoActiveSessionError` removida (dívida): ausente/inativa deixaram de ser falha barulhenta; só o estado malformado segue barulhento (`MalformedSessionStateError`, RN-N4).
- Armadilha do ruff entre edits (memória `ruff-remove-import-entre-edits`): o import de `materialize_claude_settings` foi removido pelo formatador entre dois edits e precisou ser re-adicionado junto do uso.
- Smoke real do ponto 🟡 (T015): `materialize` planta o `SessionStart→resume` no `.claude/settings.json`, preserva `model`/`PreToolUse` de terceiros e é idempotente.

## Histórico de alterações

| Data       | Alteração                                                        | Autor   |
| ---------- | ---------------------------------------------------------------- | ------- |
| 2026-06-27 | Versão inicial gerada por `/reversa-to-do`                       | reversa |
| 2026-06-27 | Execução completa (T001–T018) por `/reversa-coding`; suíte verde | reversa |
