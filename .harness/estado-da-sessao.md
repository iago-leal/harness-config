---
commit: d23a097249ed88d00c7741a2215f5173096d178a
feature: saneamento do T7 (cache de sync com fonte única em layout.py)
start_time: '2026-07-15T22:28:48.632585+00:00'
status: inactive
---

## O que foi feito
- **Re-extração `/reversa` de reconciliação pós-MD-0014 e features 022/023, completa (7/7 itens do plano)**: Scout → Archaeologist → Detective → Architect → Writer → Reviewer → Regression-check, execução autônoma sequencial. Escopo: incorporar a `_reversa_sdd/` o gate de registro de microdecisões (022), a dupla identidade do lembrete (023) e a aposentadoria do format-on-edit no Claude (MD-0014).
- **Scout/Archaeologist**: `inventory.md`/`surface.json` (92 Python, 34 `test_*.py`, 16 fichas, suíte 300, core 2.1.1; hooks do Claude sem `PostToolUse`, Stop com `--gate`); `code-analysis.md` com nova subseção `gate.py` (§4), 3º portão (§8), bordas `--gate`/`--sem-decisao` (§11) e advisory (§12); `data-dictionary.md` (§1 campos anti-loop, §6 `require_registration`, §9 `GateVerdict`); `modules.json`.
- **Detective**: `domain.md` §2.19–2.21 (**RN-N42..N47**) + 5 conceitos novos no glossário; `state-machines.md` (encerramento com **três portões**, fingerprints zerados no fechamento); `permissions.md`; **ADRs 0022 e 0023** novos (0002 já emendado pela sessão da MD-0014).
- **Architect/Writer**: `architecture.md`, C4 (contexto/containers/componentes com nó `decisions/gate`), `erd-complete.md` (primeira mudança de schema do `SESSION_STATE`; `GATE_VERDICT`), `spec-impact-matrix.md` (linha `decisions/gate` HIGH + item 9 de impacto crítico); units `microdecisoes/` (RF-05..07 + gherkin do soft-block único e do rearme), `session/`, `format-on-edit/` (gatilho revisto), `comandos-customizados/` (3º portão); `code-spec-matrix.md`.
- **Reviewer**: confiança do delta **~98%** (46🟢/2🟡/0🔴, a mais alta de qualquer rodada — tudo lido do código as-built + fichas MD). Saneadas 3 podridões stale: ressalva T1 obsoleta na RN-N11 (**G-14 fechado**), duas menções "T7 aberto" na spec-impact-matrix; registrado **G-15** (hooks `format` legados não podados — decisão da MD-0014, não bug). Nenhuma pergunta nova.
- **Regression-check — 23 features, ZERO vermelhos**: primeira verificação de **022 (W001–W010) e 023 (W001–W006), 16/16 verdes** (incl. soft-block único por sessão em `main.py:362`, teste-guarda do rearme em `test_close_flow.py:481`, skill 1.3.0 com `--sem-decisao`); 7 features com origens tocadas pelo delta re-verificadas item a item (004/009/014/018/019/020/021 — 42 verdes + 1 amarelo herdado 009/W009); 14 restantes reconfirmadas por escopo de diff. O cenário temido pela 023 (re-extração só com a semântica da 022) não se materializou.
- **Gate ao vivo, 3ª demonstração**: o soft-block disparou uma única vez ao fim do turno da re-extração (identidade grossa funcionando); avaliado: sessão sem decisão não óbvia nova (tudo deriva de MD-0014/0015/0016) → fechamento com `--sem-decisao`.
- Declarado: sem decisão não óbvia nesta sessão (gate de registro).

## Próximos passos
- **Propagar à base instalada**: `upgrade`/`migrate` nos projetos-alvo e core-raiz de `~/dev` via `.harness/upgrade-raiz.sh` (leva o gate da 022 calibrado pela 023).
- **Retomar a feature "estrutura de pastas advisory"** (pausada na clarificação): falta travar o gatilho fino e os sinais para virar `reversa-requirements`.
- **`harness migrate` real** nos ~17 projetos com layout copiado (manual, `!`); **descontinuação de `sync`/`upgrade`/oferta-014** segue feature futura; **mini-site** ainda cita literal antigo do cache (regenerar via `/reversa-docs`); **G-11** inalterado.
- 💡 Reversa 1.2.43 → 1.2.52 disponível no npm (`npx reversa update`), se quiser atualizar o framework em si.

## Pendências / bloqueios
- Sem bloqueios. Push para `origin/main` autorizado e executado nesta sessão (commit da re-extração + commit de registro).
- Vault: segue sem nota-projeto do `harness` no Obsidian (reconfirmado na sessão anterior; nada a atualizar).

## Ponteiros
- Artefatos reconciliados: `_reversa_sdd/` (domain §2.19–2.21, ADRs 0022/0023, spec-impact com linha `decisions/gate`, confidence-report com o resumo do delta), `.reversa/{state.json,plan.md}` (bloco "Re-extração 2026-07-15" e `last_reextraction` com o regression_check 23 features/0 vermelhos).
- Históricos de regressão gravados em: `_reversa_forward/{022,023}/regression-watch.md` (primeira verificação) e `{004,009,014,018,019,020,021}/regression-watch.md` (re-verificação dirigida, blocos de 2026-07-15 19:22).
- Decisões: nenhuma ficha nova (declarado `--sem-decisao`); base MD-0001..MD-0016 inalterada.
