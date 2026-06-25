# Session (Estado de Sessão Unificado) — Requisitos (Requirements)

> Regenerado pelo Writer em 2026-06-24 (Re-extração; feature 004)
> Nível de Documentação: **Completo** · Escala: 🟢 CONFIRMADO · 🟡 INFERIDO · 🔴 LACUNA
> Rastreabilidade ao Legado: [`.harness/harness-core/src/core/session/`](file:///Users/iagoleal/dev/harness/.harness/harness-core/src/core/session/) — `serializer.py`, `sinks.py`, `errors.py`; modelos em `core/domain/models.py` (`SessionState`, `SessionNarrative`). Consumidor: `core/commands/service.py`. Drivers: `src/main.py:169` (CLI) e `src/adapters/mcp/server.py:94` (MCP), ambos lendo o caminho de `config.session.state_file` (`SessionSection` em `core/domain/config.py`, feature 006).

## Visão Geral

Esta unit persiste e reinjeta o estado da última sessão do agente entre boots. O artefato canônico é `.harness/estado-da-sessao.md` — **front-matter YAML** (header-máquina) + **corpo Markdown** (a narrativa). O serializer garante round-trip (`parse(render(x)) == x`); os _sinks_ entregam o estado ao contexto do agente conforme o `active_harness`, sem que o core conheça o harness (feature 004).

## Responsabilidades

- Serializar/desserializar `SessionState` ↔ Markdown com front-matter, preservando round-trip. 🟢
- Renderizar a `SessionNarrative` em quatro seções fixas, para reinjeção e persistência. 🟢
- Distinguir arquivo **ausente** (sessão nova normal) de arquivo **malformado** (falha barulhenta). 🟢
- Entregar o estado ao contexto do agente pela estratégia certa de _sink_, escolhida na borda por `active_harness`. 🟢

## Regras de Negócio

- **RN-N1 — Fonte canônica única do estado:** o estado vive num único artefato versionado `.harness/estado-da-sessao.md`. 🟢 O caminho deixou de ser chumbado e passou a ser lido de `config.session.state_file` (`SessionSection`, default `.harness/estado-da-sessao.md`), igualmente pela CLI (`main.py:169`) e pelo MCP (`server.py:94`) — feature 006. T2 (RESOLVIDO): o driver MCP não usa mais o literal `ESTADO-DA-SESSAO.md` na raiz; a divergência CLI×MCP foi eliminada por configuração. 🟢
- **RN-N2 — Invariante de round-trip:** `parse(render(x)) == x`. Corpo = 4 seções fixas mapeando a `SessionNarrative`. 🟢
- **RN-N3 — Narrativa preservada na retomada:** em `resume` sob sessão existente, `start_session` reativa **preservando a narrativa** escrita pelo agente; a CLI reinjeta o corpo, nunca o inventa. 🟢
- **RN-N4 — Ausente ≠ malformado:** ausente → `None`; malformado (sem `---`, YAML inválido, campo obrigatório ausente, commit não-SHA1) → `MalformedSessionStateError`. 🟢
- **RN-N5 — O core não conhece o harness:** o domínio produz texto puro; a seleção do mecanismo de entrega por `active_harness` vive na borda (`get_sink` + `main.py`). 🟢
- **RN-N6 — Reinjeção multi-harness por família:** _hook_ (Claude/Gemini, `hookSpecificOutput.additionalContext`) e _arquivo_ (Antigravity, `.agents/rules/estado-sessao.md`). Harness desconhecido → `ValueError`. 🟢
- **RN-N8 — Teto de contexto (Claude):** `HookContextSink` trunca o `additionalContext` em `MAX_CHARS = 10000`, anexando aviso. 🟢
- **RN-07 — Âncora Git:** ao retomar, HEAD ≠ `commit_hash` gravado → alerta `⚠️` que antecede a narrativa; reativa mesmo assim. 🟢 (regra exercida em `core/commands`, ver unit `comandos-customizados`).

## Requisitos Funcionais

| ID    | Requisito                            | Prioridade | Critério de Aceite                                                                                                |
| ----- | ------------------------------------ | ---------- | ----------------------------------------------------------------------------------------------------------------- |
| RF-01 | Round-trip do estado.                | Must       | `parse(render(state)) == state` para qualquer `SessionState` válido.                                              |
| RF-02 | Campos obrigatórios no front-matter. | Must       | Ausência de `commit`/`feature`/`start_time`/`status` → `MalformedSessionStateError`.                              |
| RF-03 | Render da narrativa em 4 seções.     | Must       | `render_narrative` emite `## O que foi feito`, `## Próximos passos`, `## Pendências / bloqueios`, `## Ponteiros`. |
| RF-04 | Sink por família de harness.         | Must       | `claude`/`gemini` → `HookContextSink`; `antigravity` → `FileProjectionSink`; desconhecido → `ValueError`.         |
| RF-05 | Truncamento no sink de hook.         | Should     | Contexto acima de 10000 chars é truncado com sufixo de aviso.                                                     |

## Requisitos Não Funcionais

| Tipo              | Requisito inferido                                                        | Evidência no código                          | Confiança |
| ----------------- | ------------------------------------------------------------------------- | -------------------------------------------- | --------- |
| Confiabilidade    | Round-trip garante que a memória de retomada não se corrompe entre boots. | `session/serializer.py`                      | 🟢        |
| Robustez          | Falha barulhenta em estado corrompido (distingue de ausente).             | `session/serializer.py`, `session/errors.py` | 🟢        |
| Baixo acoplamento | Core agnóstico a harness; seleção de sink na borda.                       | `session/sinks.py`, `main.py`                | 🟢        |
| Compatibilidade   | Teto de 10000 chars respeita o limite do Claude.                          | `session/sinks.py` (`MAX_CHARS`)             | 🟢        |

## Critérios de Aceitação

```gherkin
Dado um SessionState válido com narrativa
Quando aplico render e depois parse
Então o SessionState resultante é igual ao original (round-trip).

Dado um arquivo .harness/estado-da-sessao.md sem o separador `---`
Quando o serializer faz parse
Então um MalformedSessionStateError é levantado (não retorna None).

Dado o active_harness "antigravity"
Quando o estado é entregue pelo sink
Então o arquivo .agents/rules/estado-sessao.md é gravado com o texto do estado.

Dado o active_harness "claude" e um contexto acima de 10000 caracteres
Quando HookContextSink emite o additionalContext
Então o texto é truncado a 10000 chars com aviso anexado.
```

## Prioridade (MoSCoW)

| Requisito                        | MoSCoW | Justificativa                                                           |
| -------------------------------- | ------ | ----------------------------------------------------------------------- |
| Round-trip do serializer (RN-N2) | Must   | Salvaguarda central; sem ela a retomada corrompe.                       |
| Ausente ≠ malformado (RN-N4)     | Must   | Falha barulhenta evita degradação silenciosa do estado.                 |
| Sink por família (RN-N6)         | Must   | Único caminho de reinjeção no boot; varia por harness.                  |
| Truncamento Claude (RN-N8)       | Should | Importante para o Claude; degrada graciosamente em excesso de contexto. |

## Rastreabilidade de Código

| Arquivo                                                | Função / Classe                                                                                | Cobertura |
| ------------------------------------------------------ | ---------------------------------------------------------------------------------------------- | --------- |
| `core/session/serializer.py`                           | `parse`, `render`, `render_narrative`, `_coerce_datetime`                                      | 🟢        |
| `core/session/sinks.py`                                | `HookContextSink`, `FileProjectionSink`, `get_sink`, `_FAMILY_BY_HARNESS`                      | 🟢        |
| `core/session/errors.py`                               | `MalformedSessionStateError`                                                                   | 🟢        |
| `core/domain/models.py`                                | `SessionState`, `SessionNarrative`                                                             | 🟢        |
| `core/domain/config.py`                                | `SessionSection.state_file` (caminho do estado, default `.harness/estado-da-sessao.md`) ✨f006 | 🟢        |
| `src/main.py`                                          | resolve sink, caminho lido de `config.session.state_file` (`main.py:169`)                      | 🟢        |
| `src/adapters/mcp/server.py`                           | `session_command` lê o caminho de `config.session.state_file` (`server.py:94`) ✨f006          | 🟢        |
| `tests/test_session.py`, `tests/test_session_sinks.py` | Cobertura de teste                                                                             | 🟢        |
