---
commit: 56f94cf1ad9e7e8be29beafa064688bcc8edb446
feature: reversa-forward (roteamento) + brief da feature 015
start_time: '2026-07-05T18:23:18.802245+00:00'
status: inactive
---

## O que foi feito
- **Gap da skill `encerrar-sessao` sob fonte única — CORRIGIDO (fix TDD-direto, MD-0012):** o `_bootstrap.py` (asset da 018) passou a resolver o core na mesma ordem do shim — local em `.harness/harness-core` e, na ausência, o core do `upstream_path` do `harness.toml`. Novos helpers puros `_core_at`/`_read_upstream_path`; `bootstrap_core` intocado. Skill 1.1.0 → 1.2.0, cópias `.claude`/`.agents` rematerializadas (paridade byte-a-byte). TDD: +4 testes; suíte 246 verde. **Smoke real** em shim descartável e depois no `experimento` real: resolve a raiz do shim, re-executa na venv do upstream e importa `CORE_VERSION` 2.0.0 — o caminho que antes estourava `CoreNotFoundError`. Commit `83d54ab`.
- **Propagação do fix aos 17 projetos migrados:** rematerializei a árvore da skill via `materialize_session_skills` (o mesmo código do `init`), não-destrutivo. Resultado: **13 corrigidos** (tinham o `_bootstrap.py` antigo) + **4 adicionados** (`contrato-fotos-higor`, `experimento`, `laudos-periciais`, `portar-md` — inicializados antes da 018, não tinham a skill). Achado: `migrate` **não** rematerializa skills (só shim/hooks/settings), por isso a propagação foi por materialize direto.
- **Diagnóstico do CI vermelho: era BILLING, não código.** As runs cancelavam em ~4s com "recent account payments have failed / spending limit" — repo privado ⇒ minutos de Actions medidos. Pista: run que "falha" em < ~10s é billing.
- **Repositório tornado PÚBLICO após varredura de segurança limpa.** Varredura sobre todo o histórico (93 commits): gitleaks sem segredos reais (2 achados = hashes SHA-256, falsos positivos); zero PII/PHI (CPF/PHI/INSS são conceito/template/φ do Three.js); nenhum `.env`/chave jamais adicionado; nenhum nome clínico/jurídico/empresarial no histórico. Prep: `LICENSE` MIT, `.gitleaks.toml` (allowlist dos FP), `.reversa/config.user.toml` destrackeado. Commit `56f94cf` + flip de visibilidade. **Bônus:** repo público ⇒ Actions grátis ⇒ CI voltou a rodar e ficou **verde em 3.12/3.13**, validando o fix nas versões do runner.

## Próximos passos
- **Artefato da skill não-commitado nos 17 projetos:** a rematerialização deixou `.claude`/`.agents/skills/encerrar-sessao/` alterados na árvore de trabalho de cada projeto. O fluxo de encerramento de cada um oferece o commit por caminho quando você voltar a trabalhar neles — nenhuma ação em massa foi feita (vários são PII/local-only).
- **Feature 021 — descontinuação de `sync`/`upgrade`/oferta-014:** T008/T009/T013/T015/T016 esperam lá; `current_version` órfão sai junto.
- **Re-extração** (`/reversa`) para reconciliar `_reversa_sdd/` com a 020 (RN-N15/N19 modificadas, RN-08 nova, `remove_tree` no port, RN-N16 com CORE_VERSION).
- **Achado pré-existente a corrigir em ciclo futuro:** `cmd resume` em repo sem nenhum commit estoura traceback cru de `git rev-parse HEAD` (viola RN-N4; anotado no regression-watch da 020).

## Pendências / bloqueios
- Sem bloqueios: suíte 246 verde local, **CI verde em 3.12/3.13** (billing resolvido com o repo público), tudo commitado e pushado.
- Dívida pré-existente tolerada: 5 avisos cosméticos de ruff (F401/F841); o CI roda só pytest.

## Ponteiros
- Fix da skill: `resolve_core` em `src/core/install/assets/skills/encerrar-sessao/scripts/_bootstrap.py` (helpers `_core_at`/`_read_upstream_path`), testes em `tests/test_skill_scripts.py`, decisão em MD-0012. Contrato espelhado do shim: `src/core/bootstrap/shim.py`.
- Propagação: `scratchpad/propagar_skill.py` (descartável) usa `materialize_session_skills`; `migrate` NÃO rematerializa skills (ver `src/core/migrate/service.py`).
- Repo público: `github.com/iago-leal/harness-config` (HTTPS, remote `harness-config`); `.gitleaks.toml` guarda o allowlist do `files-manifest.json`.
- Commits desta sessão: `83d54ab` (fix da skill + MD-0012) e `56f94cf` (prep de repo público) + flip de visibilidade.
- Âncora desta sessão: `56f94cf` (último commit de trabalho).
