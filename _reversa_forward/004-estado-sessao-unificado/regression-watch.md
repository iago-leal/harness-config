# Regression Watch — 004 estado de sessão unificado

> O que precisa continuar verdadeiro nas próximas extrações reversas (`/reversa`).
> Itens derivados das regras 🟢 "Modificadas" em `legacy-impact.md`.

## Watch items

| ID | Origem (arquivo, seção) | Regra esperada após a mudança | Tipo de verificação | Sinal de violação |
|----|--------------------------|-------------------------------|---------------------|-------------------|
| W001 | `_reversa_sdd/domain.md#2.3` (RN-07) | No `resume`, se o HEAD diverge da âncora de fechamento, um alerta explícito é emitido | presença | A re-extração não encontra mais o alerta de divergência no fluxo de `resume` |
| W002 | `_reversa_sdd/state-machines.md#1` | Estado de sessão persistido em `.harness/estado-da-sessao.md`; máquina `INACTIVE↔ACTIVE` preservada | presença | Reaparece `ESTADO-DA-SESSAO.md` (raiz) ou `.claude/ESTADO-DA-SESSAO.md` como local de persistência |
| W003 | `_reversa_sdd/domain.md#1.1` | "Sessão do Agente" / "Âncora Git" ancoradas em `.harness/estado-da-sessao.md` | redação | Glossário volta a citar `ESTADO-DA-SESSAO.md` como local canônico |
| W004 | `harness-core/src/main.py` (CLI) | `cmd resume` emite no stdout apenas o JSON `hookSpecificOutput.additionalContext` (Claude/Gemini) | presença | stdout do `resume` volta a conter texto solto, quebrando o parse do hook |

## Observações (sem peso de regressão — origem 🟡)

- Gatilho de boot do Antigravity (`agy`): premissa aberta; reinjeção passiva via `.agents/rules/estado-sessao.md` como fallback. Verificação manual no `onboarding.md`.
- Smoke test do boot vivo: validado no Claude (harness ativo). Gemini 0.47.0 (≥ 0.25, pré-requisito satisfeito) e `agy` presentes no ambiente, mas o boot vivo de cada um depende de sessão interativa — verificação manual pendente.
- Bug latente: `json` não importado em `main.py` — corrigir à parte.

## Histórico de re-extrações

### Re-extração 2026-06-23 21:58

| ID | Veredito | Observação |
|----|----------|------------|
| W001 | 🟢 verde | Alerta de divergência de âncora implementado em `core/commands/service.py:63-64` (`if session.commit_hash != current_commit: ⚠️ ALERTA...`) e observado disparando no `SessionStart` desta própria sessão. |
| W002 | 🟡 amarelo | Regra principal 🟢 — estado persistido em `.harness/estado-da-sessao.md` (CLI `main.py:192`, `serializer.py`, hook) e máquina `INACTIVE↔ACTIVE` preservada. PORÉM o sinal "reaparece `ESTADO-DA-SESSAO.md` (raiz)" disparou no driver MCP: `adapters/mcp/server.py:92` mantém `session_file = "ESTADO-DA-SESSAO.md"` (bug T2). Via canônica correta; driver MCP divergente. Aguarda julgamento humano (corrigir T2 ou confirmar que o MCP de sessão é dormente). |
| W003 | 🟢 verde | `_reversa_sdd/domain.md` ancora `.harness/estado-da-sessao.md` como local canônico (glossário + tabela de locais); o caminho legado `ESTADO-DA-SESSAO.md`/`.claude/` é citado apenas como origem. T2 registrado como ressalva 🟡. |
| W004 | 🟢 verde | `cmd resume` entrega via `sink.emit()` → `hookSpecificOutput.additionalContext` (JSON) em `core/session/sinks.py:38-40`; os demais comandos imprimem normal. Sem texto solto no stdout do resume. |

## Arquivadas

<!-- Vazio. -->
