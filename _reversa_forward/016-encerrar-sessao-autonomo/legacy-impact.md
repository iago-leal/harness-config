# Legacy Impact: encerrar-sessao autônomo (feature 016)

> Identificador: `016-encerrar-sessao-autonomo`
> Data: `2026-06-27`
> Suíte após a mudança: **201 passed** (baseline 015 = 185).

## 1. Arquivos afetados

| Arquivo afetado                                                 | Componente (`_reversa_sdd/`)                   | Tipo                        | Severidade | Justificativa                                                                |
| --------------------------------------------------------------- | ---------------------------------------------- | --------------------------- | ---------- | ---------------------------------------------------------------------------- |
| `src/core/domain/config.py`                                     | `architecture.md` · config tipada (RN-N16)     | regra-alterada              | LOW        | Nova seção `[regen]` opcional; bump 1.2.53                                   |
| `src/core/bootstrap/init_service.py`                            | bootstrap (RN-N18/N19)                         | regra-alterada              | LOW        | `current_version` 1.2.53; `[regen]` comentado no template                    |
| `src/core/regen/service.py` (novo)                              | —                                              | componente-novo             | MEDIUM     | `RegenService` dispara o regen via `ProcessPort`                             |
| `src/core/ports/git.py` · `src/adapters/git/subprocess.py`      | `GitPort` (RN-N5)                              | contrato-alterado           | LOW        | Novo verbo read-only `list_dirty_paths`                                      |
| `src/core/commands/service.py`                                  | encerramento (RN-N31/N32, RN-07; contrato 015) | regra-alterada              | HIGH       | Tolerância a ausente/inativa (D1/D3); reverte parte da 015                   |
| `src/core/commands/errors.py`                                   | erros de sessão (RN-N4)                        | regra-removida              | MEDIUM     | `NoActiveSessionError` removida (ausente/inativa não são mais erro)          |
| `src/main.py`                                                   | dispatch CLI (RN-N5; markers feature 014)      | regra-nova + regra-alterada | MEDIUM     | `cmd regen`; pré-check + marker `COMMIT_PENDENTE`; remoção do `except` morto |
| `src/core/install/claude_settings.py` (novo) · `local_apply.py` | materializadores (RN-N28/N30)                  | componente-novo             | MEDIUM     | Planta o `SessionStart→resume` no `.claude/settings.json` (raiz do RN-05)    |
| `src/core/install/harness_profiles.py`                          | superfície de comando (RN-N29)                 | regra-alterada              | LOW        | Slash command sequencia regen→encerrar e trata o marker                      |

## 2. Diff conceitual por componente

- **Encerramento (`CommandService`).** Antes (015): ausente∪inativa → `NoActiveSessionError` (exit ≠ 0). Agora (016): ausente → no-op ruidoso (exit 0, sem commit); inativa → `start_session` (reativa, preserva narrativa) + `close_session` + commit, anunciando a reativação. Malformado permanece barulhento. Os invariantes do fechamento (só `state_file`, `git add -- <path>`, âncora no trabalho) não mudaram.
- **Regen (`RegenService` + `cmd regen`).** Componente novo, coeso e desacoplado: lê `config.regen.command` e executa via `ProcessPort` com `sh -c`. Ausente → no-op; falha → exit ≠ 0 (barulhento), bloqueando o fechamento no fluxo "faz tudo".
- **Trabalho pendente (`GitPort.list_dirty_paths` + borda).** Pré-check lista a working tree suja, filtra `.harness/` e, havendo trabalho solto, emite o marker `[HARNESS:COMMIT_PENDENTE …]` (sem TTY) ou lista (TTY) e não fecha. O core nunca faz `git add` do trabalho do usuário.
- **Materialização do Claude (`claude_settings.py`).** Fecha a raiz do RN-05: `init`/`upgrade` passam a garantir o hook de resume no `.claude/settings.json` por merge idempotente, preservando chaves e hooks de terceiros.
- **Superfície de comando (`harness_profiles.py`).** O slash command de encerramento agora orquestra regen → encerrar e instrui o agente a tratar o marker, mantendo RN-N29 (conteúdo encapsulado no perfil).

## 3. Preservadas (regras 🟢 de `_reversa_sdd/domain.md` intactas)

- **RN-07** (âncora capturada antes de qualquer escrita; nunca o commit de fechamento) — intacta.
- **RN-N31** (encerramento versiona exclusivamente o `state_file`, commit isolado) — intacta.
- **RN-N32** (commit pela porta; `git add -- <path>`, nunca `-A`; `SessionCommitError` barulhento sem reverter estado) — intacta.
- **RN-N4** (ausente ≠ malformado; malformado é falha barulhenta) — intacta e reforçada: malformado segue sendo o único caso barulhento no encerrar.
- **RN-N3** (narrativa preservada na reativação via `start_session`) — intacta.
- **RN-N5** (o core não conhece o harness; seleção de mecanismo na borda) — intacta: regen via porta, markers na borda.
- **RN-N16/N17** (config tipada por via única; footprint global zero) — intactas e estendidas.
- **RN-N28/N30** (materialização incondicional dos comandos; função única, upgrade via subprocesso) — intactas; o `settings.json` do Claude entrou pela mesma porta (`apply_local_materializers`).

## 4. Modificadas (regras 🟢 alteradas ou removidas)

- **Contrato de saída da 015** (`_reversa_forward/015-corrige-encerrar-sessao-noop/interfaces/session-command-exit-contract.md`): a parte "sessão ausente ou inativa → exit ≠ 0 barulhento" foi **revertida** para tolerância (D1/D3). A parte "malformado → exit ≠ 0" foi **mantida**.
- **`NoActiveSessionError`** (`src/core/commands/errors.py`): **removida**. Nenhum caminho a levanta após a 016.
- **RN-N29** (superfície de comando do encerrar): conteúdo **alterado** para sequenciar regen→encerrar e tratar o marker `COMMIT_PENDENTE`.
