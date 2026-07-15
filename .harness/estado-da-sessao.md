---
commit: 8348e48be3eb67aec7fc8c9bd5eea8d1bb1b9774
feature: saneamento do T7 (cache de sync com fonte única em layout.py)
start_time: '2026-07-15T20:51:49.683762+00:00'
status: inactive
---

## O que foi feito
- **Feature 023 (`granularidade-lembrete-gate`) da queixa ao código, ciclo forward completo com TDD** (`/reversa-requirements` → `/reversa-clarify` → `/reversa-plan` → `/reversa-to-do` → `/reversa-coding`, 9/9 ações). Queixa: "cada mudança de arquivo está rodando o hook". Diagnóstico: não há hook por-edição (zero `PostToolUse` na base, MD-0014); o rearme vinha do fingerprint do lembrete (`decisions --gate`) incluir os sujos — cada arquivo tocado rearmava o soft-block. O gate demonstrou o sintoma ao vivo durante a própria sessão.
- **Correção — dupla identidade anti-loop**: o lembrete do Stop passa a usar `sha1(âncora)` (grossa, estável → **no máximo 1 soft-block por sessão**); o 3º portão do `encerrar-sessao` mantém `sha1(âncora+HEAD+sujos)` (fina — trabalho novo sem ficha continua rearmando a garantia dura, agora pinado por teste-guarda). Nova `compute_lembrete_fingerprint` + campo `fingerprint_lembrete` no `GateVerdict`; ramo `--gate` do `main.py` compara/persiste a grossa no mesmo campo. Sem schema novo, sem flag nova, transição autoresolvente (valor antigo nunca coincide → 1 lembrete pós-upgrade e converge).
- **Esclarecimentos (2 + 2 por extensão da delegação)**: sintoma confirmado (1a); política escolhida por recomendação com critérios do mantenedor (longevidade/coesão/mínima dívida) — única por sessão, âncora como identidade; política fixa no core (sem flag, YAGNI); transição sem código de migração. Alternativas descartadas: por-commit, carência de N turnos (relógio), remover o lembrete.
- **TDD red→green**: 7 testes novos escritos antes da implementação (teste-queixa e persistência nasceram vermelhos); suíte 293 → **300 passed**. Smoke real A–E **9/9** em repos git descartáveis (formato antigo, silêncio pós-arquivo-novo, ficha, rearme do portão, opt-out). Core 2.1.0 → **2.1.1** (patch; materializadores intocados — hook command idêntico).
- **Registro:** ficha **MD-0016** (estende MD-0015) + índice regenerado (grafo zero erros). Higiene: removido índice `microdecisoes.md` vazio gravado por engano dentro da pasta da feature (cwd errado em invocação avulsa). Commit da feature: `8348e48` (19 arquivos, +670/−13).
- **Vault:** reconfirmado — não há nota-projeto do `harness` no Obsidian ("Memória longitudinal do harness" tem `Repo: ~/.agent-memory`); nada a atualizar.

## Próximos passos
- **Re-extração `/reversa`** para reconciliar `_reversa_sdd/` com o gate — agora cobrindo 022 **e** 023 (dupla identidade; se a re-extração incorporar só a semântica da 022, W001–W003 da 023 acusam). Regression-watch da 022 (W001–W010) e da 023 (W001–W006) pendentes de primeira verificação.
- **Propagar à base instalada:** `upgrade`/`migrate` nos projetos-alvo e core-raiz de `~/dev` via `.harness/upgrade-raiz.sh` (leva junto o gate da 022 já calibrado pela 023).
- **Retomar a feature "estrutura de pastas advisory"** (pausada na clarificação): falta travar o gatilho fino e os sinais para virar `reversa-requirements`.
- **`harness migrate` real** nos ~17 projetos com layout copiado (manual, `!`); **descontinuação de `sync`/`upgrade`/oferta-014** segue feature futura; **mini-site** ainda cita literal antigo do cache (regenerar via `/reversa-docs`); **G-11** inalterado.

## Pendências / bloqueios
- Sem bloqueios. Push para `origin/main` autorizado pelo mantenedor nesta sessão (executar após o fechamento, cobrindo o commit de trabalho `8348e48` e o commit de registro).
- Atenção na retomada: o lembrete do Stop agora dispara **no máximo 1 vez por sessão**; a garantia de registro continua no 3º portão do encerramento (escape: `encerrar-sessao --sem-decisao`).

## Ponteiros
- Feature: `_reversa_forward/023-granularidade-lembrete-gate/` (requirements com esclarecimentos, roadmap D-01..D-07, investigation §2 — dupla identidade, data-delta, onboarding A–E, legacy-impact, regression-watch W001–W006, interfaces/stop-gate-lembrete.md).
- Código-chave: `core/decisions/gate.py` (`compute_lembrete_fingerprint`, `GateVerdict.fingerprint_lembrete`), `main.py` (ramo `--gate` na identidade grossa), `tests/test_close_flow.py::test_gate_portao_rearma_com_trabalho_novo_apos_bloqueio` (guarda do portão).
- Decisões: `.harness/decisoes/MD-0016.md` (dupla identidade; estende MD-0015). Commit: `8348e48` (feature 023).
