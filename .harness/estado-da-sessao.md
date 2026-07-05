---
commit: cc19d588f39ab04f18e698e0f1bebce2cac73896
feature: reversa-forward (roteamento) + brief da feature 015
start_time: '2026-07-05T19:14:41.288432+00:00'
status: inactive
---

## O que foi feito
- **Feature 021 (`hook-busca-ancorada`) — pipeline forward COMPLETO** (requirements → clarify → plan → to-do → coding), encadeado sem parar nos gates de CONTINUAR (autonomia pedida pelo usuário). Objetivo: o hook `SessionStart → cmd resume` no Claude passa a **anexar o índice `.harness/microdecisoes.md`** ao contexto reinjetado, ancorando a busca do agente antes de varreduras amplas — poupa tokens e acelera a orientação.
- **Refinamento do usuário incorporado (decisivo):** injetar o **índice** `microdecisoes.md` (~1,7 KB), NÃO a pasta `decisoes/` (~31 KB, ~18× maior) — que estouraria o teto de 10 KB do `HookContextSink` (RN-N8). As fichas `MD-NNNN` ficam como aprofundamento sob demanda via ponteiros do índice.
- **Decisões do `/reversa-clarify`:** mecanismo = estender o `cmd resume` (uma injeção por sessão, reusa sink + teto); escopo = **Claude-first** (Gemini/Antigravity adiados, "Won't this time"); default = **ligado**, desativável por `session.inject_decisions_index`.
- **Delta implementado em TDD (suíte 256 verde; +10 testes; smoke real dos 4 cenários):** campo `SessionSection.inject_decisions_index` (default `True`, retrocompatível); função pura `build_decisions_appendix` (novo `session/resume_context.py`, agnóstica ao harness, RN-N5); fiação gated a Claude em `main.py` (`enabled = active_harness=="claude" and flag`), não-bloqueante (índice ausente → aviso em `stderr` + exit 0); `execute_command` (compartilhada com o MCP) **intocada**.
- **Roteamento:** feature **020 tratada como concluída** (desescopo dos 5 `[ ]` — T008/T009/T013/T015/T016 — confirmado por decisão do usuário); `active-requirements.json` → 021, `paused-features` vazio, pasta da 020 intocada.
- **Commit `cc19d58`** (`feat(resume): ancora a busca no índice de decisões (feature 021)`), sem co-autoria.

## Próximos passos
- **Re-extração (`/reversa`) para reconciliar `_reversa_sdd/` com a 021:** RN-07 estendida (a reinjeção agora inclui o índice de decisões no Claude), **RN nova do "resume ancorado"** a formalizar em `domain.md#2.3`, regression-check dos watch `W001–W005` da 021. Segue pendente também a reconciliação da **020** (RN-N15/N19, RN-08, `remove_tree`, RN-N16/CORE_VERSION).
- **Extensão multi-harness da 021 (adiada):** Gemini (trivial, mesmo `HookContextSink` — trocar o gate `claude` por família hook) e Antigravity (família arquivo, `FileProjectionSink` sem teto — exige desenhar a projeção).
- **⚠️ Renumeração:** a "descontinuação de `sync`/`upgrade`/oferta-014" (que a sessão anterior apelidou de "candidata 021") agora é feature **FUTURA (022+)**, pois o número 021 virou o hook de busca ancorada. T008/T009/T013/T015/T016 seguem `[ ]` na 020, desescopados; `current_version` órfão sai junto.
- **Achado pré-existente:** `cmd resume` em repo sem nenhum commit estoura traceback cru de `git rev-parse HEAD` (viola RN-N4; anotado no regression-watch da 020).

## Pendências / bloqueios
- Sem bloqueios: suíte **256 verde** local; smoke real dos 4 cenários OK; trabalho da 021 commitado (`cc19d58`) e prestes a ser pushado no encerramento.
- Dívida pré-existente tolerada: `ruff` não está instalado na venv local (CI roda só pytest); avisos cosméticos herdados.

## Ponteiros
- Feature 021: `_reversa_forward/021-hook-busca-ancorada/` (requirements, roadmap, investigation, data-delta, onboarding, actions, progress.jsonl, legacy-impact, regression-watch).
- Código: `build_decisions_appendix` em `.harness/harness-core/src/core/session/resume_context.py`; fiação no ramo `cmd resume` de `src/main.py`; campo em `src/core/domain/config.py` (`SessionSection`).
- Testes: `tests/test_resume_context.py` (novo); adições em `test_config.py` (parse do flag) e `test_cli.py` (4 testes de fiação via helper `_seed_resume_repo`).
- Commit desta sessão: `cc19d58` (feature 021). Âncora de trabalho: `cc19d58`.
