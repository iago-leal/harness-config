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

<!-- Preenchido pelo agente reverso quando `/reversa` rodar de novo. -->

## Arquivadas

<!-- Vazio. -->
