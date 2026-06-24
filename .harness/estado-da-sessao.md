---
commit: 8f8a381
feature: 008-reprodutibilidade-e-config
start_time: "2026-06-24T16:57:44+00:00"
status: active
---

## O que foi feito

- **Feature 007 — `bootstrap-harness-init`** codada e commitada (`67c50cc`). Expõe `./harness init <destino> [--harness ...]` e `./harness upgrade`: o `InitializationService` copia o núcleo, o wrapper e `.harness/` para o destino, cria a venv e instala os hooks; `HarnessSection` ganhou `upstream_path` e `version`, e `SyncService.check_version_update` dispara aviso passivo de nova versão. Portas/adapters ganharam `is_dir` (fs) e `run_command` (process). Comandos documentados em `CLAUDE.md`/`GEMINI.md`.
- **Feature 008 — `reprodutibilidade-e-config`** codada e commitada (`8c136af`). Lock determinístico (`requirements.in` → `requirements.txt`), CI no GitHub Actions (`.github/workflows/ci.yml`), e `FormattingService` passando a respeitar o `harness.toml` em runtime — opt-out com nome configurável e exclusão por glob (`fnmatch`) —, pagando as dívidas **T4** e **T6**.
- **Re-extração reversa cirúrgica pós-008 + regression-check** commitada (`8f8a381`). 8 features, 24 watch items: **23 🟢, 1 🟡, 0 🔴**. ADRs **0014** (bootstrap) e **0015** (reprodutibilidade). Mini-site em `.reversa/documentation/`; backup timestampado descartável passou a ser ignorado.
- **Suíte verde: 69 passed** (`python -m pytest` a partir de `harness-core/` — `pytest` direto não acha `src`). O `main.py` entrelaçava as duas features; foi separado em dois commits via patch (split 007/008 validado, `main.py` final bit a bit idêntico ao working tree original).

## Próximos passos

- **Empurrar os três commits** (`67c50cc`, `8c136af`, `8f8a381`): estão locais em `main`, ainda não empurrados.
- `003/W003` segue **🟡** — defasagem só documental no `template.md` (SessionStart já pago pela 004), mantida por decisão do mantenedor.
- Premissa aberta da 004: validar o gatilho de boot do Antigravity (`agy`).

## Pendências / bloqueios

- Inconsistência menor não corrigida: no MCP, `process_decisions` deriva `header_file` de `os.path.join(dir, "_cabecalho.md")` e ignora o override `config.decisions.header_file`.
- **001/W001–W003** acumulam 3 vereditos verdes consecutivos (limiar `archive-after=3`): candidatos a arquivamento. O Reversa não move a tabela principal; ação manual do mantenedor.

## Ponteiros

- Commits desta sessão: `67c50cc` (feat 007), `8c136af` (feat 008), `8f8a381` (re-extração + mini-site). Todos em `main`, **locais (não empurrados)**.
- Artefatos forward: `_reversa_forward/007-bootstrap-harness-init/`, `_reversa_forward/008-reprodutibilidade-e-config/`.
- `_reversa_sdd/adrs/0014`, `0015`; `_reversa_sdd/confidence-report.md`, `gaps.md`, `questions.md`.
- Mini-site: `.reversa/documentation/` (regeneráveis via `.reversa/scripts/`).
