---
commit: 83d12bf190b1f6b6ee053ddc09d1d7e04117aea3
feature: saneamento do T7 (cache de sync com fonte única em layout.py)
start_time: '2026-07-05T21:21:05.817121+00:00'
status: inactive
---

## O que foi feito
- **G-05 fechada** (commit `83d12bf`): os ADRs 0002 e 0003 receberam nota de superação no padrão já usado nos pares 0001→0012 e 0004→0010 — status atualizado + blockquote datado distinguindo a decisão de fundo (que permanece) do mecanismo shell (superado).
- **ADR 0002** agora aponta o `FormattingService` (`src/core/formatting/service.py`), invocado por `harness format` a partir do JSON do hook PostToolUse (e, no Antigravity, pelo adaptador de borda em `.agents/`, ADR 0016); salvaguardas e opt-out migrados do `.no-autoformat` para exclusões no `harness.toml` (ADR 0015, feature 008).
- **ADR 0003** agora aponta o `SyncService` (`src/core/sync/service.py`), acionado no `resume`: mantém `ls-remote` read-only com TTL de 24h, mas com cache por projeto em `.harness/sync-cache.json` (fonte única `SYNC_CACHE_REL_PATH` de `layout.py`, MD-0013) em vez do `$STATE_DIR` global; registra também a absorção da checagem passiva de versão do upstream (`check_version_update`/`check_version_update_remote`, features 012 e 014).
- **`gaps.md` reconciliado no mesmo passo:** G-05 marcada RESOLVIDO (2026-07-05) na tabela e na síntese; das inconsistências entre artefatos resta apenas G-11 (migração não auditada, dívida consciente). As notas foram escritas após leitura direta de `service.py` — descrevem o comportamento real, não o suposto.
- Nenhum outro artefato registrava G-05 como aberta (verificado por grep em `_reversa_sdd/` e `.harness/`); a menção no estado-da-sessão anterior é substituída por esta narrativa.

## Próximos passos
- **Descontinuação de `sync`/`upgrade`/oferta-014:** segue como feature futura, ainda não numerada (022+) — não reabrir sem necessidade concreta.
- **`harness migrate` real:** ainda não executado nos ~17 projetos com layout copiado; ação separada e deliberada do mantenedor, com execução manual (`!`), pois o auto-mode bloqueia destruição em massa fora do repo.
- **Mini-site (`.reversa/documentation/`):** as páginas de `sync-check` ainda citam o literal antigo do cache; regenerar via `/reversa-docs` quando houver próxima rodada de documentação visual (não vale rodada própria só para isso).
- **G-11:** artefatos de `_reversa_sdd/migration/` seguem não auditados — auditar apenas se o Time de Migração voltar a ser usado.

## Pendências / bloqueios
- Sem bloqueios. O repositório `~/.claude` tinha 1 alteração não-commitada apontada pelo sync-check desta sessão; tratar lá, não aqui.

## Ponteiros
- Notas de superação: `_reversa_sdd/adrs/0002-formatacao-automatica-post-tool-use.md` e `_reversa_sdd/adrs/0003-sincronizacao-nao-bloqueante-session-start.md` (blockquotes de 2026-07-05).
- Lacuna fechada: `_reversa_sdd/gaps.md#G-05` (tabela §Moderado e §Resumo).
- Serviços citados: `.harness/harness-core/src/core/formatting/service.py` e `src/core/sync/service.py`; constante do cache em `src/core/domain/layout.py:24`.
