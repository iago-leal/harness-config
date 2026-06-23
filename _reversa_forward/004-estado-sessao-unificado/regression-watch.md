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

<!-- Preenchido pelo agente reverso quando `/reversa` rodar de novo. -->

## Arquivadas

<!-- Vazio. -->
