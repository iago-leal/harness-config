# Regression Watch — 004 estado de sessão unificado

> O que precisa continuar verdadeiro nas próximas extrações reversas (`/reversa`).
> Itens derivados das regras 🟢 "Modificadas" em `legacy-impact.md`.

## Watch items

| ID   | Origem (arquivo, seção)                   | Regra esperada após a mudança                                                                       | Tipo de verificação | Sinal de violação                                                                                  |
| ---- | ----------------------------------------- | --------------------------------------------------------------------------------------------------- | ------------------- | -------------------------------------------------------------------------------------------------- |
| W001 | `_reversa_sdd/domain.md#2.3` (RN-07)      | No `resume`, se o HEAD diverge da âncora de fechamento, um alerta explícito é emitido               | presença            | A re-extração não encontra mais o alerta de divergência no fluxo de `resume`                       |
| W002 | `_reversa_sdd/state-machines.md#1`        | Estado de sessão persistido em `.harness/estado-da-sessao.md`; máquina `INACTIVE↔ACTIVE` preservada | presença            | Reaparece `ESTADO-DA-SESSAO.md` (raiz) ou `.claude/ESTADO-DA-SESSAO.md` como local de persistência |
| W003 | `_reversa_sdd/domain.md#1.1`              | "Sessão do Agente" / "Âncora Git" ancoradas em `.harness/estado-da-sessao.md`                       | redação             | Glossário volta a citar `ESTADO-DA-SESSAO.md` como local canônico                                  |
| W004 | `.harness/harness-core/src/main.py` (CLI) | `cmd resume` emite no stdout apenas o JSON `hookSpecificOutput.additionalContext` (Claude/Gemini)   | presença            | stdout do `resume` volta a conter texto solto, quebrando o parse do hook                           |

## Observações (sem peso de regressão — origem 🟡)

- Gatilho de boot do Antigravity (`agy`): premissa aberta; reinjeção passiva via `.agents/rules/estado-sessao.md` como fallback. Verificação manual no `onboarding.md`.
- Smoke test do boot vivo: validado no Claude (harness ativo). Gemini 0.47.0 (≥ 0.25, pré-requisito satisfeito) e `agy` presentes no ambiente, mas o boot vivo de cada um depende de sessão interativa — verificação manual pendente.
- Bug latente: `json` não importado em `main.py` — corrigir à parte.

## Histórico de re-extrações

### Re-extração 2026-06-25 14:32

> Rodada completa 001–012. Vereditos confirmados por leitura direta do código (greps), não só pelos artefatos `_reversa_sdd/`.

| ID   | Veredito | Observação                                                                                                                                                             |
| ---- | -------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| W001 | 🟢 verde | Alerta de divergência de âncora vivo em `core/commands/service.py:64-65` (`if session.commit_hash != current_commit: ⚠️ ALERTA ... diverge do commit âncora`).         |
| W002 | 🟢 verde | Estado em `.harness/estado-da-sessao.md` (arquivo presente); `grep ESTADO-DA-SESSAO.md` no `src/` = vazio; máquina `INACTIVE↔ACTIVE` preservada (`state-machines.md`). |
| W003 | 🟢 verde | `_reversa_sdd/domain.md` (linhas 14/38/83) ancora `.harness/estado-da-sessao.md` como canônico; `ESTADO-DA-SESSAO.md` citado só como origem legada.                    |
| W004 | 🟢 verde | `cmd resume` entrega via `core/session/sinks.py:38-40` (`hookSpecificOutput.additionalContext`), sem texto solto no stdout. Inalterado por 011/012.                    |

### Re-extração 2026-06-24 19:30 (pós-feature 010)

| ID   | Veredito | Observação                                                                                                                                   |
| ---- | -------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| W001 | 🟢 verde | Alerta de divergência de âncora no `resume` inalterado; a 010 não tocou o fluxo de retomada.                                                 |
| W002 | 🟢 verde | Estado em `.harness/estado-da-sessao.md`; a 010 não reintroduziu `ESTADO-DA-SESSAO.md`. O comando de IDE apenas delega ao `encerrar-sessao`. |
| W003 | 🟢 verde | Glossário canônico (`.harness/estado-da-sessao.md`) inalterado.                                                                              |
| W004 | 🟢 verde | `cmd resume` segue emitindo só o JSON `hookSpecificOutput.additionalContext` via sink.                                                       |

### Re-extração 2026-06-24 10:06

| ID   | Veredito | Observação                                                                                                                                                                                                                 |
| ---- | -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| W001 | 🟢 verde | Alerta de divergência de âncora preservado em `core/commands/service.py`. Inalterado.                                                                                                                                      |
| W002 | 🟢 verde | Estado em `.harness/estado-da-sessao.md`; a 006 parametrizou o caminho via `SessionSection` (default = mesmo caminho), lido por CLI e MCP. Não reaparece `ESTADO-DA-SESSAO.md` raiz; máquina `INACTIVE↔ACTIVE` preservada. |
| W003 | 🟢 verde | `_reversa_sdd/domain.md` mantém `.harness/estado-da-sessao.md` como local canônico.                                                                                                                                        |
| W004 | 🟢 verde | `cmd resume` emite só o JSON `hookSpecificOutput.additionalContext` via sink; T3 corrigido (`cf73980`). Sem texto solto no stdout.                                                                                         |

### Re-extração 2026-06-24 08:10

| ID   | Veredito | Observação                                                                                                                                                                         |
| ---- | -------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| W001 | 🟢 verde | Alerta de divergência de âncora Git presente em service.py:63-64 (`if session.commit_hash != current_commit: warning_msg = ...`). Regra mantida.                                   |
| W002 | 🟢 verde | Bug T2 corrigido (cf73980): adapters/mcp/server.py:93 agora usa `.harness/estado-da-sessao.md` (antes era ESTADO-DA-SESSAO.md na raiz). CLI e MCP sincronizados. Regra verdadeira. |
| W003 | 🟢 verde | Documentação em \_reversa_sdd/domain.md mantém `.harness/estado-da-sessao.md` como local canônico. Nenhuma regressão detectada no glossário.                                       |
| W004 | 🟢 verde | Bug T3 corrigido (cf73980): `json` importado em main.py:5. Comando `resume` entrega via sink.emit() → JSON puro em stdout (line 215). Sem texto solto. Regra verdadeira.           |

### Re-extração 2026-06-23 21:58

| ID   | Veredito   | Observação                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| ---- | ---------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| W001 | 🟢 verde   | Alerta de divergência de âncora implementado em `core/commands/service.py:63-64` (`if session.commit_hash != current_commit: ⚠️ ALERTA...`) e observado disparando no `SessionStart` desta própria sessão.                                                                                                                                                                                                                                                       |
| W002 | 🟡 amarelo | Regra principal 🟢 — estado persistido em `.harness/estado-da-sessao.md` (CLI `main.py:192`, `serializer.py`, hook) e máquina `INACTIVE↔ACTIVE` preservada. PORÉM o sinal "reaparece `ESTADO-DA-SESSAO.md` (raiz)" disparou no driver MCP: `adapters/mcp/server.py:92` mantém `session_file = "ESTADO-DA-SESSAO.md"` (bug T2). Via canônica correta; driver MCP divergente. Aguarda julgamento humano (corrigir T2 ou confirmar que o MCP de sessão é dormente). |
| W003 | 🟢 verde   | `_reversa_sdd/domain.md` ancora `.harness/estado-da-sessao.md` como local canônico (glossário + tabela de locais); o caminho legado `ESTADO-DA-SESSAO.md`/`.claude/` é citado apenas como origem. T2 registrado como ressalva 🟡.                                                                                                                                                                                                                                |
| W004 | 🟢 verde   | `cmd resume` entrega via `sink.emit()` → `hookSpecificOutput.additionalContext` (JSON) em `core/session/sinks.py:38-40`; os demais comandos imprimem normal. Sem texto solto no stdout do resume.                                                                                                                                                                                                                                                                |

## Arquivadas

<!-- Vazio. -->
