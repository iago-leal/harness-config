# Legacy Impact — 004 estado de sessão unificado

> Data: 2026-06-23. O que a feature mexeu no legado mapeado em `_reversa_sdd/`.

## Tabela de impacto

| Arquivo afetado | Componente (`_reversa_sdd/`) | Tipo | Severidade | Justificativa |
|-----------------|------------------------------|------|------------|---------------|
| `harness-core/src/core/domain/models.py` | `SessionState` (`code-analysis.md#2.5`) | regra-alterada | MEDIUM | Ganha value-object `SessionNarrative`; campos-máquina intactos |
| `harness-core/src/core/commands/service.py` | módulo `commands` (`code-analysis.md#2.5`) | contrato-alterado | MEDIUM | `load/save_session` viram round-trip via serializer; `resume` passa a retornar a narrativa |
| `harness-core/src/core/session/` | — | componente-novo | LOW | Novo módulo: serializer (front-matter+corpo), sinks por-harness, erro nomeado |
| `harness-core/src/main.py` | CLI (`architecture.md#1`) | contrato-alterado | HIGH | `session_file` → `.harness/estado-da-sessao.md`; `resume` emite via sink (JSON no stdout). Afeta o contrato do `SessionStart` — validado por smoke test |
| `.harness/estado-da-sessao.md` | Sessão do Agente (`state-machines.md#1`) | delta-de-dados | MEDIUM | Novo arquivo canônico (front-matter YAML + corpo) |
| `.claude/ESTADO-DA-SESSAO.md` | Sessão do Agente (`domain.md#1.1`) | componente-extinto | MEDIUM | Removido; narrativa migrada para o canônico (conteúdo preservado em git) |
| `ESTADO-DA-SESSAO.md` (raiz) | Sessão do Agente | componente-extinto | LOW | Arquivo pobre gerado pela CLI; removido |
| `.gemini/settings.json` | — | delta-de-contrato-externo | MEDIUM | Gatilho `SessionStart` do Gemini → `./harness cmd resume` |
| `.agents/rules/estado-sessao.md` | — | componente-novo | LOW | Projeção do estado para o Antigravity (família B) |

## Diff conceitual por componente

- **`SessionState` / domínio:** aditivo. Os quatro campos-máquina (`commit_hash`, `active_feature`, `start_time`, `is_active`) permanecem; ganha `narrative: SessionNarrative`. A validação SHA-1 do commit é preservada e agora também blinda o parse (erro nomeado).
- **módulo `commands`:** o parse/render regex (que degradava em `None` silencioso) foi substituído por `core/session/serializer` com round-trip e `MalformedSessionStateError`. O `resume` deixa de imprimir uma linha de status e passa a devolver o corpo da narrativa mais o alerta de âncora; o envelope de entrega é aplicado na borda.
- **CLI (`main.py`):** `session_file` passa de `ESTADO-DA-SESSAO.md` (raiz) para `.harness/estado-da-sessao.md`; o `resume` resolve o sink por `active_harness` e entrega o estado pelo mecanismo do harness; erro de parse vira aviso não-bloqueante em stderr (não trava o boot).
- **Persistência:** dois arquivos (raiz pobre + `.claude/` rico) colapsam num único canônico versionado em `.harness/`.

## Preservadas (regras 🟢 de `domain.md` intactas)

- RN-01, RN-02 (sync/resiliência) — não tocadas.
- RN-03, RN-04, RN-05, RN-06 (formatação) — não tocadas.
- RN-08, RN-09, RN-10 (documentação) — não tocadas.
- RN-07 (alerta de divergência de âncora git) — **comportamento preservado**: o alerta continua sendo emitido no `resume`; apenas o arquivo lido mudou.

## Modificadas (regras 🟢 alteradas)

- **RN-07 (`domain.md#2.3`)** — mecanismo alterado: a âncora de fechamento agora é lida de `.harness/estado-da-sessao.md`; o alerta passa a integrar o contexto reinjetado. Comportamento (alertar na divergência) inalterado.
- **Máquina de estados da Sessão (`state-machines.md#1`)** — `INACTIVE↔ACTIVE` preservada; muda apenas o suporte de persistência (arquivo único `.harness/`).
- **Glossário (`domain.md#1.1`)** — "Sessão do Agente" e "Âncora Git de Sessão" deixam de citar `ESTADO-DA-SESSAO.md` e passam a `.harness/estado-da-sessao.md`.

## Observações (sem peso de regressão)

- Premissa do gatilho de boot do Antigravity (`agy`) segue aberta (🟡); a reinjeção passiva via `.agents/rules/estado-sessao.md` é o fallback.
- Bug latente pré-existente: `json` não está importado em `harness-core/src/main.py` (usado em `resolve_format_target`). Fora do escopo da 004 — sinalizado para correção à parte.
