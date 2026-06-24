# Data Delta: Comando de IDE para encerrar a sessão

> Identificador: `010-command-encerrar-sessao`
> Data: `2026-06-24`
> Base: modelo extraído em `_reversa_sdd/erd-complete.md` e `_reversa_sdd/domain.md`

## Resumo

Esta feature **não altera nenhum modelo de dados**. O harness-core não tem banco relacional (`_reversa_sdd/architecture.md#3`); a persistência é em arquivos versionados. A mudança introduz **dois novos arquivos de artefato** no projeto-alvo, sem tocar configuração, estado de sessão ou grafo de decisões.

## Novos artefatos (arquivos no disco do projeto-alvo)

| Caminho (relativo ao projeto-alvo)     | Tipo                            | Produtor                                                | Conteúdo                                                                                                                   |
| -------------------------------------- | ------------------------------- | ------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| `.claude/commands/encerrar-sessao.md`  | Markdown (slash command Claude) | `materialize_session_commands` via `ClaudeProfile`      | Invoca `./harness cmd encerrar-sessao` (relativo à raiz; `${CLAUDE_PROJECT_DIR}` não expande em slash commands — ver D-04) |
| `.agents/workflows/encerrar-sessao.md` | Markdown (workflow Antigravity) | `materialize_session_commands` via `AntigravityProfile` | Invoca `<command_path>/harness cmd encerrar-sessao`                                                                        |

## Campos novos / removidos

- Nenhum campo novo em `harness.toml` (seções `[harness]`, `[session]`, `[decisions]`, `[formatting]` inalteradas).
- Nenhuma mudança no front-matter de `.harness/estado-da-sessao.md` (`commit`, `feature`, `start_time`, `status`).
- Nenhuma mudança no schema das fichas de microdecisão (`MD-*.md`).

## Máquina de estados

- A máquina de estados da sessão (`_reversa_sdd/state-machines.md`) **não muda**: o comando apenas aciona a transição de fechamento já existente (`close_session`), sem novos estados nem novas transições.

## Migração necessária

- **Retroativa**: nenhuma transformação de dados. Projetos já instalados ganham os dois arquivos na próxima execução de `./harness init`/`upgrade`.
- **Idempotência**: reexecutar gera o mesmo conteúdo; o `upgrade` reescreve o caminho absoluto do Antigravity se o repositório foi movido.
