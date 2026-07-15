---
commit: 95612b11872f11a9cec58e32303afaee62801536
feature: saneamento do T7 (cache de sync com fonte única em layout.py)
start_time: '2026-07-15T12:47:58.971369+00:00'
status: inactive
---

## O que foi feito
- **Feature 022 (`hook-registro-decisoes`) executada do argumento livre ao código, ciclo forward completo** (`/reversa-requirements` → `/reversa-clarify` → `/reversa-plan` → `/reversa-to-do` → `/reversa-coding`, 23/23 ações). O gate de registro obrigatório de microdecisões está vivo: 3º portão do `encerrar-sessao` (marker `DECISAO_PENDENTE`, protocolo abortar-e-reexecutar), escape auditável `--sem-decisao` (rastro na narrativa), anti-loop por fingerprint no front-matter do estado, soft-block único por pendência no `Stop` do Claude (`harness decisions --gate`), advisory em stderr no Antigravity (RN-N26 preservada). Sinal físico sem filtro de tipo de arquivo (repos documentais contam) via novo `GitPort.list_changed_paths_since` + dirty. Flag `decisions.require_registration` (default ligado).
- **Esclarecimentos do mantenedor (5)**: sinal sem filtro de tipo; enforcement híbrido (2c); default ligado em todo lugar (3a); Claude+Antigravity nesta iteração (4b); rastro do escape no estado da sessão (5a). RF-08 reconciliado no requirements: o `Stop` não tem canal não-bloqueante que alcance o modelo → soft-block único (roadmap D-04).
- **Qualidade:** suíte 257 → **293 passed** (36 testes novos, incl. smoke com git real); smoke manual A–F do `onboarding.md` verde; core 2.0.1 → **2.1.0**; skill `encerrar-sessao` 1.3.0; `.claude/settings.json`/snippet/skills deste repo regenerados do perfil novo; `harness-docs.html` regerado.
- **Higiene prévia:** o pacote pendente da MD-0014 (aposentar `PostToolUse` format-on-edit) foi commitado como pré-condição (`9c9d52f`) — a 022 editava os mesmos arquivos.
- **Registro:** ficha **MD-0015** (fingerprint no estado; soft-block único; alternativas descartadas) + índice regenerado. Commit da feature: `95612b1` (44 arquivos, +1922/−82).
- **Vault:** não há nota-projeto do `harness` no Obsidian (a "Memória longitudinal do harness" tem `Repo: ~/.agent-memory`) — nada a atualizar lá, confirmado de novo.

## Próximos passos
- **Re-extração `/reversa`** para reconciliar `_reversa_sdd/` com o gate (state-machines.md precisa da nota do 3º portão; domain.md ganha as RNs da 022; regression-watch da 022 tem 10 itens W001–W010).
- **Propagar o gate à base instalada:** `upgrade`/`migrate` nos projetos-alvo (o default ligado só chega com a materialização nova) e core-raiz de `~/dev` via `.harness/upgrade-raiz.sh`.
- **Retomar a feature "estrutura de pastas advisory"** (pausada na clarificação): falta travar o gatilho fino e os sinais para virar `reversa-requirements`.
- **`harness migrate` real** nos ~17 projetos com layout copiado (manual, `!`); **descontinuação de `sync`/`upgrade`/oferta-014** segue feature futura; **mini-site** ainda cita literal antigo do cache (regenerar via `/reversa-docs`); **G-11** inalterado.

## Pendências / bloqueios
- Sem bloqueios. Push para `origin/main` autorizado pelo mantenedor nesta sessão (executar após o fechamento, cobrindo também o commit de registro).
- Atenção na retomada: o `Stop` deste repo agora roda `decisions --gate` — pendência de registro gera um soft-block único por estado; o escape é `encerrar-sessao --sem-decisao`.

## Ponteiros
- Feature: `_reversa_forward/022-hook-registro-decisoes/` (requirements com esclarecimentos, roadmap D-01..D-09, investigation §1 — semântica do Stop, legacy-impact, regression-watch W001–W010, onboarding A–G).
- Código-chave: `core/decisions/gate.py` (novo), `core/session/close_flow.py` (3º portão), `main.py` (ramo `decisions --gate`), `adapters/antigravity/hook_bridge.py` (advisory), assets da skill `encerrar-sessao` v1.3.0.
- Decisões: `.harness/decisoes/MD-0015.md` (gate) e `MD-0014.md` (format-on-edit aposentado). Commits: `9c9d52f` (MD-0014), `95612b1` (feature 022).
