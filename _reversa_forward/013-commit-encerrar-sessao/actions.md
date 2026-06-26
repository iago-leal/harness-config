# Actions: Versionar o estado da sessão ao encerrar

> Identificador: `013-commit-encerrar-sessao`
> Data: `2026-06-26`
> Roadmap: `_reversa_forward/013-commit-encerrar-sessao/roadmap.md`

## Resumo

| Métrica                     | Valor                                                     |
| --------------------------- | --------------------------------------------------------- |
| Total de ações              | 13                                                        |
| Paralelizáveis (`[//]`)     | 8                                                         |
| Maior cadeia de dependência | 8 (T002 → T004 → T005 → T008 → T010 → T011 → T012 → T013) |

Todos os caminhos têm raiz em `.harness/harness-core/`.

## Fase 1, Preparação

| ID   | Descrição                                                                                                                                                                    | Dependências | Paralelismo | Arquivo alvo                  | Confidência | Status |
| ---- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ | ----------- | ----------------------------- | ----------- | ------ |
| T001 | Criar módulo de erros de comandos com `SessionCommitError` (subclasse de `Exception`, docstring de falha barulhenta no espírito de `MalformedSessionStateError`) (D-05)      | -            | `[//]`      | `src/core/commands/errors.py` | 🟢          | `[X]`  |
| T002 | Adicionar ao `GitPort` o método abstrato `commit_paths(repo_path, paths, message) -> str` (contrato: adiciona só os caminhos dados, cria commit, devolve o novo HEAD) (D-01) | -            | `[//]`      | `src/core/ports/git.py`       | 🟢          | `[X]`  |

## Fase 2, Testes

| ID   | Descrição                                                                                                                                                                                                                                                      | Dependências | Paralelismo | Arquivo alvo                             | Confidência | Status |
| ---- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ | ----------- | ---------------------------------------- | ----------- | ------ |
| T003 | Teste de `SubprocessGitAdapter.commit_paths` num repo git temporário: commita **apenas** o caminho informado e devolve o novo HEAD; um arquivo alheio pendente **não** entra no commit (RF-01/RF-03/D-04)                                                      | T002         | `[//]`      | `tests/test_adapters.py`                 | 🟢          | `[X]`  |
| T004 | Reescrever `test_execute_encerrar_sessao` com um **Git fake explícito** que avança o HEAD ao commitar: asserir que a âncora = HEAD pré-commit, que `commit_paths` recebe **só** `[session_filepath]`, e que a saída reporta os dois hashes (RF-04/RF-05/RF-07) | T001, T002   | `[//]`      | `tests/test_commands.py`                 | 🟢          | `[X]`  |
| T005 | Acrescentar teste de falha barulhenta: quando `commit_paths` levanta, `execute_command` levanta `SessionCommitError`, não devolve sucesso e o estado salvo é preservado (`save_session` foi chamado antes) (RF-06/RN-05)                                       | T004         | -           | `tests/test_commands.py`                 | 🟢          | `[X]`  |
| T006 | Teste dos materializadores: a `description`/corpo de `session_command_artifact` de `ClaudeProfile` e `AntigravityProfile` descreve o commit de encerramento por cima do trabalho, consistente entre os perfis (RF-08)                                          | -            | `[//]`      | `tests/test_session_command_profiles.py` | 🟢          | `[X]`  |

## Fase 3, Núcleo

| ID   | Descrição                                                                                                                                                                                                                                                                                                                                                                             | Dependências           | Paralelismo | Arquivo alvo                     | Confidência | Status |
| ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------- | ----------- | -------------------------------- | ----------- | ------ |
| T007 | Implementar `commit_paths` no `SubprocessGitAdapter`: `git add -- <paths>` + `git commit -m <message>`, devolvendo o HEAD resultante; traduzir `CalledProcessError` em `RuntimeError` (padrão do adapter); nunca `add -A` (D-01/D-04)                                                                                                                                                 | T002, T003             | `[//]`      | `src/adapters/git/subprocess.py` | 🟢          | `[X]`  |
| T008 | Alterar o ramo `encerrar-sessao` de `execute_command`: manter a captura da âncora **antes** das escritas; após `save_session`, chamar `commit_paths(repo_path, [session_filepath], "chore(sessao): encerrar sessão <feature>; âncora <ancora>")`; montar retorno com os **dois** hashes; envolver falha do commit em `SessionCommitError` sem reverter o estado (D-02/D-03/D-06/D-07) | T001, T002, T004, T005 | `[//]`      | `src/core/commands/service.py`   | 🟢          | `[X]`  |

## Fase 4, Integração

| ID   | Descrição                                                                                                                                                                                                                                                      | Dependências     | Paralelismo | Arquivo alvo                                                      | Confidência | Status |
| ---- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------- | ----------- | ----------------------------------------------------------------- | ----------- | ------ |
| T009 | Reescrever a `description`/corpo de `session_command_artifact` em `ClaudeProfile` e `AntigravityProfile` para descrever que o encerramento cria um commit de registro por cima do último commit de trabalho, de forma consistente entre os perfis (D-08/RF-08) | T006             | `[//]`      | `src/core/install/harness_profiles.py`                            | 🟢          | `[X]`  |
| T010 | Bump de versão 1.2.48 → 1.2.49 em `config.py` (`version`) e `init_service.py` (`current_version`) — gate da rematerialização não-stale (D-08)                                                                                                                  | T007, T008, T009 | -           | `src/core/domain/config.py`, `src/core/bootstrap/init_service.py` | 🟢          | `[X]`  |

## Fase 5, Polimento

| ID   | Descrição                                                                                                                                                                                                             | Dependências                 | Paralelismo | Arquivo alvo                                                                  | Confidência | Status |
| ---- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------- | ----------- | ----------------------------------------------------------------------------- | ----------- | ------ |
| T011 | Rodar a suíte `pytest` completa e confirmar verde sem regressão (commands, adapters, profiles, materializador de session commands, footprint, sync, cli e os testes novos)                                            | T005, T006, T007, T008, T010 | -           | `tests/`                                                                      | 🟢          | `[X]`  |
| T012 | Rematerializar os artefatos locais (`.claude/commands/encerrar-sessao.md`, `.agents/workflows/encerrar-sessao.md`) a partir do código pós-bump e confirmar que o texto novo aparece (não confiar na cópia em memória) | T010, T011                   | -           | `.claude/commands/encerrar-sessao.md`, `.agents/workflows/encerrar-sessao.md` | 🟡          | `[X]`  |
| T013 | Smoke conforme `onboarding.md`: encerrar versiona só o `state_file`, âncora = commit de trabalho, dois hashes na saída, e o teste negativo de falha barulhenta preservando o estado                                   | T011, T012                   | -           | (verificação)                                                                 | 🟢          | `[X]`  |

## Notas de execução

<!-- Reservado para /reversa-coding. -->

- Lembrete (memória do projeto): ao editar Python do core, adicionar import **e** uso no mesmo edit — a venv local pode mascarar `NameError` que o CI em 3.12/3.13 pega.

## Histórico de alterações

| Data       | Alteração                                  | Autor   |
| ---------- | ------------------------------------------ | ------- |
| 2026-06-26 | Versão inicial gerada por `/reversa-to-do` | reversa |
