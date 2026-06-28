# Regression Watch: encerrar-sessao autônomo (feature 016)

> Identificador: `016-encerrar-sessao-autonomo`
> Data: `2026-06-27`
> Itens a manter verdadeiros nas próximas extrações reversas e features.

## Watch items

| ID   | Origem (arquivo, seção)                                          | Regra esperada após a mudança                                                                                             | Tipo de verificação | Sinal de violação                                                                    |
| ---- | ---------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- | ------------------- | ------------------------------------------------------------------------------------ |
| W001 | `src/core/commands/service.py` (ramo encerrar)                   | Sessão **inativa** → reativa + fecha + commit, exit 0, anunciando a reativação                                            | presença            | `encerrar-sessao` sobre inativa volta a sair com exit ≠ 0                            |
| W002 | `src/core/commands/service.py` · `src/main.py`                   | Sessão **ausente** → no-op ruidoso (exit 0), sem commit de encerramento                                                   | presença            | ausente volta a falhar barulhento ou cria commit indevido                            |
| W003 | `src/main.py` (except Malformed)                                 | Estado **malformado** em comando explícito → exit ≠ 0 (RN-N4)                                                             | presença            | malformado passa a sair com exit 0                                                   |
| W004 | `src/core/commands/service.py` (RN-N31/N32)                      | Commit de fechamento versiona **só** o `state_file`, via `git add -- <path>`                                              | presença            | commit de encerramento arrasta outros caminhos ou usa `git add -A`                   |
| W005 | `src/core/commands/service.py` (RN-07)                           | Âncora = HEAD de **trabalho**, capturada antes de escrever; nunca o commit de fechamento                                  | presença            | âncora aponta para o commit de encerramento                                          |
| W006 | `src/core/regen/service.py` · `src/main.py` (`cmd regen`)        | regen falho (exit ≠ 0) **não** fecha; ausente → no-op exit 0                                                              | presença            | regen falho fecha a sessão, ou ausente vira erro                                     |
| W007 | `src/main.py` (`pending_work_paths`, marker)                     | Trabalho solto fora de `.harness/` → marker `[HARNESS:COMMIT_PENDENTE …]` e **não** fecha                                 | presença            | fecha com working tree suja fora de `.harness/`, ou o core faz `git add` do trabalho |
| W008 | `src/core/install/claude_settings.py` · `local_apply.py` (RN-05) | `init`/`upgrade` (claude) plantam o `SessionStart→resume` no `.claude/settings.json`, idempotente e preservando terceiros | presença            | `settings.json` não recebe o hook, ou apaga chaves/hooks de terceiros                |
| W009 | `src/core/commands/errors.py`                                    | `NoActiveSessionError` permanece **removida** (ausente/inativa não são mais erro)                                         | ausência            | a exceção reaparece e volta a ser levantada no encerrar                              |

## Observações (itens 🟡, sem peso de regressão)

- W008 nasce 🟡: a segurança do merge no `.claude/settings.json` depende de não substituir a chave `hooks` inteira. A estratégia atual garante os três eventos do harness e preserva os demais; reavaliar se um usuário tiver um `SessionStart` próprio que queira manter (hoje o evento é do harness por convenção).
- A dualidade TTY do marker `COMMIT_PENDENTE` (W007) hoje, no caminho TTY, **lista e aborta** (não auto-commita), divergindo do `[s/N]` sugerido no brief — escolha consciente para não commitar com mensagem genérica.

## Histórico de re-extrações

### Re-extração 2026-06-28 09:45

> Primeira verificação dos watch da 016. A feature 018 **moveu** o pré-check de pendência e as ofertas da borda `main.py` para `SessionCloseFlow` (core), e o regen para o script da skill — comportamento **preservado**, não alterado (helpers reexportados por `src.main`, suíte 212 verde). O `CommandService`/`RegenService` ficaram intactos. Verificação factual: suíte 212 passed.

| ID   | Veredito | Observação                                                                                                                                                                                                                   |
| ---- | -------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| W001 | 🟢 verde | Sessão inativa → reativa+fecha+commit (exit 0): `CommandService` inalterado; `SessionCloseFlow.run` invoca `execute_command`.                                                                                                |
| W002 | 🟢 verde | Sessão ausente → no-op ruidoso (exit 0): `close_flow.run` pula o pré-check (`sessao_existente is None`), chama `execute_command` e devolve 0.                                                                                |
| W003 | 🟢 verde | Malformado em comando explícito → exit ≠ 0: `SessionCloseFlow._abort_malformed` retorna 1 (RN-N4) — antes em `main.py`, agora no core, comportamento idêntico.                                                               |
| W004 | 🟢 verde | Commit de fechamento versiona só o `state_file` via `git add -- <path>`: `CommandService` inalterado (RN-N31/N32).                                                                                                           |
| W005 | 🟢 verde | Âncora = HEAD de trabalho, capturada antes de escrever: inalterado.                                                                                                                                                          |
| W006 | 🟢 verde | `cmd regen` segue intacto (`main.py:296-299`, `RegenService`); regen falho não fecha. O encadeamento regen→fechar migrou para o script da skill (`encerrar_sessao.py`: regen, se exit≠0 aborta antes de `SessionCloseFlow`). |
| W007 | 🟢 verde | Trabalho solto fora de `.harness/` → marker `[HARNESS:COMMIT_PENDENTE …]` sem fechar: `pending_work_paths` + `conduct_commit_pendente` migraram para `close_flow.py` (return 0 sem fechar), comportamento idêntico.          |
| W008 | 🟢 verde | `init`/`upgrade` (claude) plantam `SessionStart→resume` no `.claude/settings.json`: `local_apply.py` chama `materialize_claude_settings` quando `active_harness == "claude"` — inalterado pela 018.                          |
| W009 | 🟢 verde | `NoActiveSessionError` permanece removida: ausência confirmada em `errors.py`.                                                                                                                                               |

## Arquivadas

<!-- Vazio. -->
