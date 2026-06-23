# Estado da sessão — harness

> Última atualização: 23/06/2026. Gravado à mão (o `/encerrar-sessao` global foi desabilitado nesta sessão).
> Âncora git: `5c01999` em `main`, sincronizado com `origin/main`.

## ⚠️ Leia primeiro — o carregamento de estado mudou
- O `SessionStart` foi cortado para `./harness cmd resume` (CLI Python). Ele **ainda não reinjeta este arquivo no contexto** — regressão aceita, registrada em `decisoes/MD-0001.md`, a ser fechada na **feature 004**. Portanto: **leia este arquivo manualmente ao retomar**.
- O slash command global `/encerrar-sessao` foi **desabilitado** (`~/.claude/commands/encerrar-sessao.md` → `…/.md.disabled`), porque o script dele recriaria o hook shell legado `carregar-estado-sessao.sh` e reverteria o corte. Para reabilitar: renomear de volta para `.md`.

## O que foi feito nesta sessão
- **Diagnóstico** do `harness-core` (hexagonal); apontadas dívidas: config decorativo, modo shadow sem oráculo, hooks vivos quebrados.
- **Purga do legado morto**: removidos o modo shadow/coexistência do `BootstrapService`, `test_parity` (verde-falso), `LegacyDecisionImporter`, refs a `harness-config`/`claude-config`. → `5624f78`.
- **Corte total dos hooks vivos** para a CLI: `SessionStart→cmd resume`, `PostToolUse→format` (com leitura de stdin), `Stop→decisions`; aposentado `carregar-estado-sessao.sh`. Regressão aceita do `SessionStart` → `MD-0001`. → `5624f78`.
- **Feature 003 (instalação por prompt)**: ciclo Reversa completo (requirements→clarify→plan→to-do→coding). Novo módulo `core/install/` (`InstallPromptService` por introspecção + Strategy de perfis por harness), subcomando `install-prompt`, `load_config` ativa o `HarnessConfig` ocioso. → `b2adcf4`.
- **Fix do `doc-gen`**: `extract_commands` passa a usar o `help` do parser pai (antes todos os comandos saíam "Sem descrição."); `harness-docs.html` regenerado. → `82ae110`.
- **Artefatos do Reversa** (re-extração + forwards 001/002) commitados → `5c01999`. Tudo pushado para `origin` (`iago-leal/harness-config`). Suíte: **41 verde**.

## Estado atual
- Working tree **limpo**; `main` em `5c01999`, sincronizada com `origin/main`.
- Hooks do projeto (`.claude/settings.json`) apontam para `./harness` (CLI Python).
- `/encerrar-sessao` global desabilitado.

## Próximos passos
- **Feature 004**: portar a reinjeção de contexto do `SessionStart` para a CLI, fechando `MD-0001` (e, idealmente, unificar os dois formatos de `ESTADO-DA-SESSAO`). Abrir com `/reversa-requirements`.
- Decidir o destino definitivo do `/encerrar-sessao`: reescrever para a CLI nova (`./harness cmd encerrar-sessao`) ou reabilitar.
- Opcional: rodar `/reversa` (re-extração) para preencher o histórico dos `regression-watch.md`.

## Pendências / bloqueios
- Regressão conhecida do `SessionStart` (`MD-0001`): não auto-carrega estado até a 004.

## Ponteiros
- `decisoes/MD-0001.md` — purga + corte + regressão aceita.
- `_reversa_forward/003-instalacao-por-prompt/` — feature 003 completa (inclui `legacy-impact.md` e `regression-watch.md`).
- `~/.claude/commands/encerrar-sessao.md.disabled` — comando global desabilitado (renomear p/ `.md` para reativar).
