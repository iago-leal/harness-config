---
commit: 0196819456076bc8ae31c8d77a3e19a87bb22a01
feature: reversa-forward (roteamento) + brief da feature 015
start_time: '2026-07-05T20:02:34.674385+00:00'
status: inactive
---

## O que foi feito
- **`/reversa` rodado como re-extração de reconciliação completa** (Scout → Archaeologist → Detective → Architect → Writer → Reviewer → regression-check), encadeado sem parar nos gates de CONTINUAR (autonomia pedida pelo usuário). Motivação: a sessão anterior (feature 021) apontou que `_reversa_sdd/` precisava reconciliar com 019/020/021, e uma defasagem estrutural mais antiga (inventory.md, code-analysis.md, c4-components.md, spec-impact-matrix.md **congelados desde a feature 009**, sem sequer refletir a relocação do core da feature 011).
- **Agentes Independentes reavaliados:** Visor/Data Master/Design System/Tracer marcados `N/A` no plano — harness é CLI pura, sem BD/UI/processo de longa duração.
- **Scout + Archaeologist + Architect (re-extração estrutural ampla):** `inventory.md`, `dependencies.md`, `surface.json`, `code-analysis.md`, `data-dictionary.md`, `modules.json`, `c4-context.md`, `c4-containers.md` (redesenhado com o split shim/upstream da fonte única), `c4-components.md`, `erd-complete.md`, `traceability/spec-impact-matrix.md` — todos reconciliados com o estado atual do código (13ª unidade `core/migrate`; `core/session` expandido com `close_flow.py`/`resume_context.py`; dependência direta `fastmcp`, não `mcp`).
- **Detective (reconciliação incremental 019-021):** `domain.md` §2.16-2.18 (RN-N34 a RN-N41), `state-machines.md`, `permissions.md` + **3 ADRs retroativas novas** (0019 pré-check restrito ao estado, 0020 fonte única + `harness migrate`, 0021 resume ancorado).
- **Writer:** nova unit `migrate/{requirements,design,tasks}.md` (nunca existira); `comandos-customizados/` estendida com o pré-check restrito (f019), o gate de narrativa (f018) e o apêndice de decisões no resume (f021); `traceability/code-spec-matrix.md` reconciliado.
- **Reviewer:** `confidence-report.md`/`gaps.md`/`questions.md` atualizados; fechou G-04 antigo (Protocols→ABC em `inventory.md`); registrou **T7 novo** (dívida técnica em aberto) e o desescopo da 020 (decisão documentada, não lacuna) como G-12/G-13.
- **Regression-check completo (não só 019-021): as 21 features do `_reversa_forward/` verificadas** — 99 watch items, **90 verdes, 9 amarelos (supersessões deliberadas já documentadas), zero vermelhos**. Feature **015 verificada pela primeira vez** nesta sessão (histórico estava vazio desde sempre).
- **Achado novo T7:** `adapters/mcp/server.py:42` grava o cache de sync em `.harness/sync_cache.json` (underscore); a CLI usa `.harness/sync-cache.json` (hífen) — o nome que o `.gitignore` do `init` realmente cobre. O cache do MCP escapa do `.gitignore` e, desde a feature 019, seria ofertado para commit por engano. Documentado (`architecture.md` §5, `erd-complete.md` §3, `gaps.md#G-12`); **não corrigido** (Reviewer documenta, não mexe em código de produto).
- **Desescopo da 020 confirmado, não é lacuna:** `upgrade_project`/`SyncService`/`version` **não foram removidos** — decisão deliberada do mantenedor (2026-07-01) porque sustentam a `UpgradeOffer` do encerramento (feature 014); RN-N19 revisada/substituída por RN-N36, RN-N20/RN-N21 seguem ativas.
- `.reversa/plan.md` e `.reversa/state.json` atualizados com o escopo completo desta re-extração (`last_reextraction`).

## Próximos passos
- **T7 (fix trivial, não urgente):** alinhar o literal do cache de sync em `adapters/mcp/server.py` ao de `main.py`/`layout.py` (ou centralizar numa constante única em `layout.py`).
- **G-05 pendente (fora do escopo desta rodada):** ADRs 0002/0003 ainda sem nota de superação apontando para os serviços Python que substituíram os scripts shell.
- **Descontinuação de `sync`/`upgrade`/oferta-014:** segue como feature **futura, ainda não numerada** (022+) — não reabrir sem necessidade concreta, já está documentada como decisão consciente.
- **`harness migrate` real:** ainda não executado nos ~17 projetos que usam o layout copiado; ação separada e deliberada do mantenedor, fora do escopo do Reversa.

## Pendências / bloqueios
- Sem bloqueios. Nenhuma pergunta pendente ao usuário — toda a reconciliação foi confirmada por leitura direta do código atual, sem necessidade de decisão humana nesta rodada.
- Trabalho desta sessão ainda **não commitado** até este ponto do encerramento (será commitado e pushado no fechamento).

## Ponteiros
- Re-extração desta sessão: `.reversa/state.json#last_reextraction` (escopo completo, método por agente, regression_check com 99 watch items).
- ADRs novas: `_reversa_sdd/adrs/0019-precheck-pendencia-restrito-ao-estado.md`, `0020-fonte-unica-execucao-e-migrate.md`, `0021-resume-ancorado-indice-decisoes.md`.
- Unit nova: `_reversa_sdd/migrate/` (requirements, design, tasks) — cobre `core/migrate/service.py`.
- Achado T7: `_reversa_sdd/architecture.md` §5 (tabela de dívidas técnicas), `_reversa_sdd/gaps.md#G-12`.
- Regression-watch atualizados: `_reversa_forward/{015,019,020,021}-*/regression-watch.md` (histórico novo, datado 2026-07-05).
