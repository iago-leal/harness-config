# Session (Estado de Sessão Unificado) — Tarefas de Implementação

> Regenerado pelo Writer em 2026-06-24 (Re-extração; feature 004)
> Sequência executável para reimplementar a unit a partir do legado, com rastreabilidade ao código original.

## Pré-requisitos

- [ ] `SessionState` e `SessionNarrative` definidos em `core/domain/models.py`.
- [ ] `PyYAML` disponível.
- [ ] `FileSystemPort` disponível (para o sink de arquivo).

## Tarefas

- [ ] T-01, Implementar `serializer.parse`
  - Origem no legado: `core/session/serializer.py`
  - Critério de pronto: separa front-matter (`_FRONTMATTER_RE`) do corpo; valida `_REQUIRED_META`; converte `ValueError` do domínio em `MalformedSessionStateError`; ausência de `---`/YAML inválido → erro.
  - Confiança: 🟢

- [ ] T-02, Implementar `serializer.render` e `render_narrative`
  - Origem no legado: `core/session/serializer.py`
  - Critério de pronto: `render` produz meta YAML (`sort_keys=False`) + corpo; `render_narrative` emite as 4 seções fixas; invariante `parse(render(x)) == x`.
  - Confiança: 🟢

- [ ] T-03, Implementar `_coerce_datetime`
  - Origem no legado: `core/session/serializer.py`
  - Critério de pronto: aceita `datetime` ou ISO (`Z`→`+00:00`); naive vira UTC.
  - Confiança: 🟢

- [ ] T-04, Implementar `MalformedSessionStateError`
  - Origem no legado: `core/session/errors.py`
  - Critério de pronto: subclasse de `Exception` que distingue "corrompido" de "ausente" (RN-N4).
  - Confiança: 🟢

- [ ] T-05, Implementar `HookContextSink` (Claude/Gemini)
  - Origem no legado: `core/session/sinks.py`
  - Critério de pronto: imprime envelope `hookSpecificOutput.additionalContext` no stdout; trunca em `MAX_CHARS=10000` com aviso.
  - Confiança: 🟢

- [ ] T-06, Implementar `FileProjectionSink` (Antigravity)
  - Origem no legado: `core/session/sinks.py`
  - Critério de pronto: grava o estado em `.agents/rules/estado-sessao.md`, criando o diretório-pai.
  - Confiança: 🟢

- [ ] T-07, Implementar `get_sink` (seleção por família)
  - Origem no legado: `core/session/sinks.py`
  - Critério de pronto: `_FAMILY_BY_HARNESS` → claude/gemini=hook, antigravity=file; desconhecido → `ValueError`.
  - Confiança: 🟢

- [ ] T-08, Integrar nos drivers (CLI e MCP)
  - Origem no legado: `src/main.py:169`, `src/adapters/mcp/server.py:94`
  - Critério de pronto: o caminho do estado vem de `config.session.state_file` (`SessionSection`, default `.harness/estado-da-sessao.md`) — lido igualmente pela CLI e pelo MCP, sem literal chumbado; resolve o sink por `active_harness`. ✨f006
  - Confiança: 🟢

## Tarefas de Teste

- [ ] TT-01, Round-trip: `parse(render(state)) == state` para estado com narrativa.
- [ ] TT-02, Caso de erro: arquivo sem `---` / campo obrigatório ausente → `MalformedSessionStateError`.
- [ ] TT-03, Sink: `antigravity` grava `.agents/rules/estado-sessao.md`; `claude` emite envelope JSON; harness inválido → `ValueError`.
- [ ] TT-04, Truncamento: contexto > 10000 chars truncado com aviso.
  - Cobertura existente: `tests/test_session.py`, `tests/test_session_sinks.py`.

## Ordem Sugerida

1. T-04 (erro) e T-03 (coerção) primeiro — base para o serializer.
2. T-01/T-02 (serializer) antes dos sinks.
3. T-05/T-06/T-07 (sinks) e por fim T-08 (integração CLI).

## Lacunas Pendentes (🔴)

- Nenhuma 🔴. **T2 RESOLVIDO** (feature 006): o caminho do estado de sessão passou a vir de `config.session.state_file` (`SessionSection`), lido igualmente por CLI e MCP. A divergência CLI×MCP, antes documentada como bug latente, foi eliminada por configuração. 🟢
