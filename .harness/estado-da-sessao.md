---
commit: edaf8bb3798ebbf68ed28629f55ff3b415925daa
feature: saneamento do T7 (cache de sync com fonte única em layout.py)
start_time: '2026-07-05T20:59:58.363426+00:00'
status: inactive
---

## O que foi feito
- **T7 saneado (MD-0013), pelo rito de correção leve TDD-direto** (fora do pipeline forward): o servidor MCP (`adapters/mcp/server.py:42`) gravava o cache de sincronia em `.harness/sync_cache.json` (underscore), enquanto CLI e `close_flow` usavam `.harness/sync-cache.json` (hífen) — o único nome coberto pelo `.gitignore` que o `init` grava. Desde a feature 019, o cache do MCP seria ofertado para commit por engano.
- **Fix por fonte única, não por alinhamento de literal:** nova constante `SYNC_CACHE_REL_PATH` em `core/domain/layout.py`, da qual `SYNC_CACHE_GITIGNORE_ENTRY` passa a derivar; os três consumidores (`main.py`, `core/session/close_flow.py`, `adapters/mcp/server.py`) leem a constante. Elimina a classe do erro, não só a instância.
- **TDD:** `test_mcp_check_repository_sync_usa_cache_canonico` (em `tests/test_mcp.py`) escrito antes do fix — vermelho por `ImportError` da constante, verde após. Suíte completa: **257 passed**. Ruff limpo nos arquivos tocados (resta só o F841 pré-existente de `main.py:96`, dívida tolerada).
- **Bump 2.0.0 → 2.0.1** em `config.py` para que os projetos vendorados percebam o fix pelo alerta passivo de versão.
- **Artefatos do Reversa reconciliados no mesmo passo** — todos os que afirmavam T7 "EM ABERTO" agora registram RESOLVIDO (2026-07-05, MD-0013): `architecture.md` §5 (tabela T1-T7 toda verde), `gaps.md#G-12`, `erd-complete.md` §3, `confidence-report.md`, `data-dictionary.md` §3, `c4-containers.md` (nós do cache unificados no diagrama e na tabela), `traceability/spec-impact-matrix.md`, unit `sync-check/` (requirements, design, tasks, contracts). Registros históricos (`_reversa_forward/019`, `state.json#last_reextraction`, HTML gerado do mini-site) preservados como fotografias datadas.
- **MD-0013** gravada em `.harness/decisoes/` (relaciona MD-0012) e índice `microdecisoes.md` regenerado via `./harness decisions` (grafo validado, zero erros).

## Próximos passos
- **G-05 pendente:** ADRs 0002/0003 ainda sem nota de superação apontando para os serviços Python que substituíram os scripts shell.
- **Descontinuação de `sync`/`upgrade`/oferta-014:** segue como feature futura, ainda não numerada (022+) — não reabrir sem necessidade concreta.
- **`harness migrate` real:** ainda não executado nos ~17 projetos com layout copiado; ação separada e deliberada do mantenedor.
- **Mini-site (`.reversa/documentation/`):** as páginas de `sync-check` ainda citam o literal antigo; regenerar via `/reversa-docs` quando houver próxima rodada de documentação visual (não vale rodada própria só para isso).

## Pendências / bloqueios
- Sem bloqueios. Caches `sync_cache.json` órfãos que o MCP possa ter criado em projetos são efêmeros e inócuos — decisão explícita de não varrê-los (MD-0013, descarte 3).

## Ponteiros
- Ficha da decisão: `.harness/decisoes/MD-0013.md` (D · PORQUÊ · DESCARTADO · ESTADO completos).
- Fix: `.harness/harness-core/src/core/domain/layout.py` (constante), `src/adapters/mcp/server.py`, `src/main.py`, `src/core/session/close_flow.py`, `src/core/domain/config.py` (bump), `tests/test_mcp.py` (teste novo).
- T7 fechado nos artefatos: `_reversa_sdd/architecture.md` §5, `_reversa_sdd/gaps.md#G-12`.
