# Regression Watch: Versionar o estado da sessão ao encerrar

> Identificador: `013-commit-encerrar-sessao`
> Data: `2026-06-26`
> Gerado por `/reversa-coding`. Itens derivados da seção "Modificadas" de `legacy-impact.md`.

## Watch items

| ID   | Origem (arquivo, seção)                                 | Regra esperada após a mudança                                                                                                                                 | Tipo de verificação | Sinal de violação                                                                                     |
| ---- | ------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------- | ----------------------------------------------------------------------------------------------------- |
| W001 | `src/core/commands/service.py` (ramo `encerrar-sessao`) | O `encerrar-sessao` cria um commit contendo **exclusivamente** o `state_file` (nunca `git add -A`).                                                           | presença            | O estado volta a ficar pendente no working tree, ou o commit inclui arquivos alheios.                 |
| W002 | `src/core/commands/service.py`; `domain.md#2.3` (RN-07) | A âncora gravada/exibida é o HEAD **pré-commit** (último commit de trabalho); o commit de encerramento fica por cima.                                         | redação             | A âncora passa a apontar para o próprio commit de encerramento.                                       |
| W003 | `src/core/ports/git.py`; `domain.md#RN-N5`              | O domínio commita **apenas** pela porta `GitPort.commit_paths`; nenhum `subprocess`/`git` direto no `CommandService`.                                         | presença            | Chamada a `subprocess`/`git` dentro da camada de domínio de comandos.                                 |
| W004 | `src/core/commands/errors.py`; `domain.md#RN-N4`        | Falha ao criar o commit levanta `SessionCommitError` (erro nomeado, exit ≠ 0) e **preserva** o `state_file` salvo.                                            | presença            | Mensagem de sucesso sobre commit falho, ou estado revertido/ausente após a falha.                     |
| W005 | `src/core/commands/service.py`                          | A saída do `encerrar-sessao` reporta **dois** hashes: âncora e commit de encerramento.                                                                        | redação             | A saída volta a citar apenas a âncora.                                                                |
| W006 | `src/core/install/harness_profiles.py`                  | Os `session_command_artifact` (Claude e Antigravity) descrevem o commit de registro por cima do trabalho; o texto rematerializa não-stale após o bump 1.2.49. | redação             | O texto antigo "gravando o commit-âncora" reaparece, ou o `upgrade` distribui o materializador stale. |

## Observações (confidência 🟡 / 🔴 — sem peso de regressão)

- O comportamento de runtime do **workflow do Antigravity** (execução de shell embutida vs. instrução ao agente) não é verificável localmente; o texto do artefato é verificável (🟢), o efeito no agente real permanece 🟡 — alinhado ao amarelo herdado de 009/W009.
- Forçar a falha do commit em smoke local exige isolar a identidade git (`user.useConfigOnly=true` + `GIT_CONFIG_GLOBAL/SYSTEM` neutralizados), pois o git auto-detecta uma identidade do sistema por padrão. O caminho de falha tem cobertura determinística no teste de unidade (`test_execute_encerrar_sessao_falha_commit_preserva_estado`).

## Histórico de re-extrações

### Re-extração 2026-06-28 09:45

> Re-verificação pós-feature 018. As regras de versionamento do encerramento (RN-N31/N32) seguem no `CommandService`, intactas — `SessionCloseFlow` apenas o invoca. Único ajuste: W006 referia o `session_command_artifact`, **removido** pela 018. Verificação factual: suíte 212 passed.

| ID   | Veredito   | Observação                                                                                                                                                                                                                                                                                                                                                                                                          |
| ---- | ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| W001 | 🟢 verde   | Commit isola o `state_file` (`git add -- <paths>`, nunca `-A`): `CommandService` inalterado.                                                                                                                                                                                                                                                                                                                        |
| W002 | 🟢 verde   | Âncora = HEAD pré-commit; commit de encerramento por cima: RN-07 preservada.                                                                                                                                                                                                                                                                                                                                        |
| W003 | 🟢 verde   | Domínio commita só pela porta `GitPort.commit_paths`: inalterado (RN-N5/N32).                                                                                                                                                                                                                                                                                                                                       |
| W004 | 🟢 verde   | Falha de commit → `SessionCommitError` (exit 1) preservando o estado: inalterado; `SessionCloseFlow` reporta o erro sem fechar.                                                                                                                                                                                                                                                                                     |
| W005 | 🟢 verde   | Saída reporta os dois hashes (âncora + encerramento): `CommandService.execute_command` inalterado.                                                                                                                                                                                                                                                                                                                  |
| W006 | 🟡 amarelo | **Superado pela 018:** o `session_command_artifact` foi **removido** (não há mais artefato `.md` por-perfil descrevendo o commit). A descrição do commit de registro por cima do trabalho migrou para o `SKILL.md` da skill ("commit de registro por cima do último commit de trabalho, com a âncora seguindo apontando para o trabalho"). Propriedade preservada na nova forma; watch da forma antiga, aposentado. |

### Re-extração 2026-06-26 11:02

> Primeira verificação da 013, na mesma sessão da implementação. Vereditos por evidência factual: suíte **153 passed**, smoke end-to-end (caso feliz + negativo) e greps de invariante. Reconciliado em `_reversa_sdd/domain.md#2.14` (RN-N31/RN-N32), `architecture.md` (✨f013) e `comandos-customizados/requirements.md` (✨f013).

| ID   | Veredito | Observação                                                                                                                                                                                                                    |
| ---- | -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| W001 | 🟢 verde | Commit isola o `state_file` (`git add -- <paths>`, nunca `-A`) — `test_subprocess_git_adapter_commit_paths_isola_arquivo` + smoke (commit lista só `.harness/estado-da-sessao.md`; `AGENTS.md`/`CLAUDE.md` seguem untracked). |
| W002 | 🟢 verde | Âncora = HEAD pré-commit; `HEAD~1 == âncora` no smoke; `test_execute_encerrar_sessao`. RN-07 preservada.                                                                                                                      |
| W003 | 🟢 verde | Domínio commita só pela porta `GitPort.commit_paths`; nenhum `subprocess`/`git` no `CommandService` (RN-N5/RN-N32).                                                                                                           |
| W004 | 🟢 verde | Falha de commit → `SessionCommitError` (exit 1, sem "sucesso"), estado preservado — `test_execute_encerrar_sessao_falha_commit_preserva_estado` + smoke negativo.                                                             |
| W005 | 🟢 verde | Saída reporta os dois hashes (âncora + encerramento) — asserção em `test_execute_encerrar_sessao` e smoke.                                                                                                                    |
| W006 | 🟢 verde | Materializadores descrevem o commit de registro; rematerialização não-stale confirmada em sandbox (claude + antigravity) pós-bump 1.2.49 — `test_session_command_profiles.py`.                                                |

## Arquivadas

<!-- Vazia. -->
