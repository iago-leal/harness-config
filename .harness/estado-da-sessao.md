---
commit: 6e85a78e633b11a707502ab47893d497ffe97943
feature: reversa-forward (roteamento) + brief da feature 015
start_time: "2026-07-05T18:23:18.802245+00:00"
status: active
---

## O que foi feito

- **Gap da skill `encerrar-sessao` sob fonte única — CORRIGIDO (fix TDD-direto, MD-0012):** o `_bootstrap.py` (asset da 018) passou a resolver o core na mesma ordem do shim — local em `.harness/harness-core` e, na ausência, o core do `upstream_path` do `harness.toml`. Novos helpers puros `_core_at`/`_read_upstream_path`; `bootstrap_core` intocado (o re-exec/`sys.path` já usam o `core` devolvido). Skill 1.1.0 → 1.2.0, cópias `.claude`/`.agents` rematerializadas do asset (paridade byte-a-byte). TDD: +4 testes em `test_skill_scripts.py`; suíte 246 verde; ruff limpo. **Smoke real** em shim descartável: resolveu a raiz do shim, re-executou na venv do upstream e importou `CORE_VERSION` 2.0.0 — o caminho que antes estourava `CoreNotFoundError`.
- **Migração real executada (pendente crítico da sessão anterior quitado):** `./harness migrate ~/dev` rodou sobre 17 projetos. Constatação: a parte **destrutiva já havia ocorrido** entre 01/07 e hoje (nenhum filho tinha mais core/venv; só o upstream retém a única `.venv` de 108 MB) — a passada desta sessão foi a normalização idempotente (shim reescrito, hooks re-encadeados, settings re-mesclados, `version` removido dos tomls). Smoke: shim do `experimento` executa o core do upstream normalmente.
- **Verificado e confirmado o gap da skill `encerrar-sessao` sob fonte única:** o `_bootstrap.py` (asset da 018, idêntico no filho e no upstream) resolve o core só em `.harness/harness-core` local e não conhece `upstream_path` → em projeto migrado a skill falha (`CoreNotFoundError`) e o desvio é `./harness cmd encerrar-sessao`. Registrado como **feature candidata** (ensinar `resolve_core` a cair no upstream); o usuário optou por fechar a 020 antes (CONTINUAR no roteador).
- **Feature 020 CONCLUÍDA — bloco polimento (T018/T019/T020)** via `/reversa-coding` (commits `358af6f` código + `bebac79` trilha):
- **Rastros da 020 fechados:** actions.md 15/20 `[X]` (5 restantes = desescopo da 021), progress.jsonl +3, legacy-impact.md (rodada final), regression-watch.md (**W008** lockstep de versão + 2 observações).

## Próximos passos

- **Propagar o fix da skill aos projetos já migrados:** a `_bootstrap.py` corrigida só chega aos filhos via `harness migrate`/`init` — os migrados antes de hoje ainda carregam o asset antigo. Reconciliar quando conveniente (o desvio `./harness cmd encerrar-sessao` segue funcionando enquanto isso).
- **Feature 021 — descontinuação de `sync`/`upgrade`/oferta-014:** T008/T009/T013/T015/T016 esperam lá; `current_version` órfão sai junto.
- **Re-extração** (`/reversa`) para reconciliar `_reversa_sdd/` com a 020 (RN-N15/N19 modificadas, RN-08 nova, `remove_tree` no port, RN-N16 com CORE_VERSION).
- **Achado pré-existente a corrigir em ciclo futuro:** `cmd resume` em repo sem nenhum commit estoura traceback cru de `git rev-parse HEAD` (viola RN-N4; anotado no regression-watch da 020).

## Pendências / bloqueios

- Sem bloqueios: suíte 246 verde, migração da base concluída, disco recuperado (~1,5 GB), tudo commitado.
- Dívida pré-existente tolerada: 5 avisos cosméticos de ruff (F401/F841); o CI roda só pytest.

## Ponteiros

- Trilha da 020 (completa): `_reversa_forward/020-fonte-unica-e-hooks/` — actions.md com a nota "2026-07-03 — bloco polimento"; regression-watch W001–W008.
- Versão canônica: `src/core/domain/config.py` (`CORE_VERSION`), testes de lockstep em `tests/test_init.py` (3 últimos).
- Fix da skill: `resolve_core` em `src/core/install/assets/skills/encerrar-sessao/scripts/_bootstrap.py` (helpers `_core_at`/`_read_upstream_path`), testes em `tests/test_skill_scripts.py`, decisão em MD-0012. Contrato espelhado do shim: `src/core/bootstrap/shim.py`.
- Smoke T020: `scratchpad/smoke-t020.sh` (descartável, fora do repo).
- Commits desta sessão: `358af6f` (feat, CORE_VERSION/2.0.0) + `bebac79` (docs, trilha do polimento).
- Âncora desta sessão: `bebac79` (último commit de trabalho).
