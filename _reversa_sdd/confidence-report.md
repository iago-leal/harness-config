# Relatório de Confiança — harness

> Regenerado pelo Revisor em 2026-06-24 (Re-extração após a feature 008-reprodutibilidade-e-config)
> Nível de Documentação: **Completo** · Escala: 🟢 CONFIRMADO · 🟡 INFERIDO · 🔴 LACUNA
> **Reconciliação de 2026-07-05** (Reviewer, pós-features 010-021): Scout, Archaeologist, Detective, Architect e Writer reconciliaram nesta sessão os artefatos que estavam congelados desde a feature 009 (`inventory.md`, `dependencies.md`, `surface.json`, `code-analysis.md`, `data-dictionary.md`, `modules.json`, `c4-components.md`, `erd-complete.md`, `traceability/spec-impact-matrix.md`) e incorporaram as features 019-021 em `domain.md`/`state-machines.md`/`permissions.md`/ADRs/`architecture.md`/specs SDD. Ver seção "Reconciliação 2026-07-05" abaixo para o detalhe do que mudou desde o relatório de 2026-06-24.
> **Reconciliação de 2026-08-11** (Reviewer, pós-features 024-027; a 024 commitada em `5c4433d`, **025/026/027 apenas na working tree nesta data**): reconciliação dirigida do consentimento para escrita no git ao encerrar (024), da aposentadoria do soft-block do Stop (025), do medidor de progresso read-only (026) e do exportador kanban (027). Ver seção "Reconciliação 2026-08-11" abaixo.
> **Reconciliação de 2026-08-11-b** (Reviewer, pós-feature 028; **todo o delta apenas na working tree nesta data**): reconciliação dirigida da visão compacta de decisões (028: `compile_compact_view`, precedência compacta→índice no resume, guidance write-once no init, config `compact_file`/`compact_index_size`; core 2.6.0, suíte 389) + MD-0021 (decisão operacional sem código) e README.md novo na raiz. Ver seção "Reconciliação 2026-08-11-b" abaixo.
> **Reconciliação de 2026-07-15** (Reviewer, pós-MD-0014 e features 022-023): reconciliação incremental do gate de registro de microdecisões (022: `gate.py`, 3º portão, `decisions --gate`, advisory Antigravity) e da dupla identidade do lembrete (023), mais a aposentadoria do format-on-edit no perfil Claude (MD-0014). Ver seção "Reconciliação 2026-07-15" abaixo.

Sintetiza a avaliação de confiança da **re-extração** do ecossistema `harness` após a implementação do motor de bootstrap evolucionário (feature 007) e da reprodutibilidade e configurações dinâmicas de formatação (feature 008). Substitui integralmente o relatório anterior de 2026-06-24; a reconciliação de 2026-07-05 estende (não substitui) este relatório para as features 010-021.

---

## Resumo Geral (histórico, 2026-06-24 — feature 008)

| Nível         | Quantidade | Percentual |
| :------------ | :--------: | :--------: |
| 🟢 CONFIRMADO |    275     |   80.2%    |
| 🟡 INFERIDO   |     50     |   14.6%    |
| 🔴 LACUNA     |     18     |    5.2%    |
| **Total**     |  **343**   |  **100%**  |

**Confiança geral do projeto em 2026-06-24:** **87.5%** 🟢
_(Cálculo: (275 + 50 × 0.5) / 343 = 87.46%)_

> A confiança subiu de forma robusta para **87.5%**, impulsionada pelo fechamento das últimas duas dívidas técnicas abertas do projeto (T4 e T6). O serviço de formatação agora consome ativamente o manifesto local e o build do core tornou-se determinístico e travado via `uv`, validado em integração contínua (CI).

## Resumo Geral (reconciliação 2026-07-05 — features 010-021)

> Esta rodada não recontou item-a-item toda a base anterior (343 afirmações) — seria refazer a extração inteira sem necessidade, já que o núcleo 001-009 permanece válido e não foi tocado pelas features 010-021. Em vez disso, avalia-se a confiança do **delta reconciliado nesta sessão**: as seções/arquivos novos ou reescritos por Scout/Archaeologist/Detective/Architect/Writer hoje.

| Nível             | Quantidade (estimativa do delta) | Percentual do delta |
| :---------------- | :------------------------------: | :-----------------: |
| 🟢 CONFIRMADO     |               ~92                |         90%         |
| 🟡 INFERIDO       |                ~9                |         9%          |
| 🔴 LACUNA         |                ~1                |         1%          |
| **Total (delta)** |             **~102**             |      **100%**       |

**Confiança do delta reconciliado (010-021):** **~94%** 🟢 — mais alta que a média histórica do projeto porque quase todo o conteúdo novo foi lido diretamente do código-fonte atual (leitura direta de `main.py`, `close_flow.py`, `resume_context.py`, `migrate/service.py`, `offers.py`, `claude_settings.py`, `layout.py`) e cruzado contra `requirements.md`/`actions.md` dos próprios forwards 019-021, não inferido por analogia. O único 🔴 residual é a instabilidade de `stepIdx` do Antigravity (herdada, não nova) — ver Lacunas.

**Confiança combinada estimada do projeto como um todo:** entre **87% e 90%** (não recalculada com precisão de casas decimais nesta rodada — a base histórica de 343 itens não foi reauditada; o delta de ~102 itens novos eleva a média geral, mas o cálculo exato exigiria reclassificar cada item das 343 afirmações originais, fora do escopo desta reconciliação cirúrgica).

---

## Por Spec / Artefato

### Specs por unit (geração)

| Unidade de Especificação (Unit)                                      | 🟢  | 🟡  | 🔴  | Confiança |
| :------------------------------------------------------------------- | :-: | :-: | :-: | :-------: |
| `install/`                                                           | 26  |  4  |  0  |    93%    |
| `session/`                                                           | 27  |  6  |  0  |    91%    |
| `microdecisoes/`                                                     | 35  |  9  |  3  |    81%    |
| `format-on-edit/` 🛠️ (f008)                                          | 45  | 10  |  0  |    91%    |
| `sync-check/`                                                        | 30  |  7  |  4  |    81%    |
| `comandos-customizados/` 🆕 (f018/f019/f021)                         | 51  |  6  |  4  |    89%    |
| `bootstrap/` 🚀 (f007, f020)                                         | 26  |  7  |  3  |    85%    |
| `documentacao-uso-html/`                                             | 20  |  3  |  2  |    84%    |
| `run-harness-core-local/`                                            | 22  |  2  |  2  |    88%    |
| `antigravity-hooks/` (f009, não revisada em detalhe até esta rodada) | ~24 | ~3  |  1  |   ~89%    |
| `migrate/` 🆕 (NOVA, f020)                                           | 25  |  3  |  1  |    92%    |
| `progress/` 🆕🆕 (NOVA, f026/f027)                                   | 30  |  4  |  0  |    94%    |

> 🛠️ = unit significativamente refinada na feature 008 para consumir configurações e padrões glob.
> 🚀 = unit significativamente expandida na feature 007 para cobrir bootstrapping e evolução não destrutiva; estendida na f020 (`bootstrap/shim.py`, `claude_settings.py`).
> 🆕 = conteúdo novo desta reconciliação de 2026-07-05. `comandos-customizados/` ganhou +11 afirmações 🟢 (RN-N34/N35/N41, RF-06/07/08, rastreabilidade de `close_flow.py`/`resume_context.py`); `migrate/` é uma unit inteiramente nova (nunca revisada antes por não existir).
> `antigravity-hooks/` não foi objeto de revisão linha-a-linha nesta rodada (fora do escopo da reconciliação 019-021); a contagem é herdada da extração de 2026-06-24 sem verificação adicional.
> 🆕🆕 = conteúdo novo da reconciliação de 2026-08-11. `progress/` é unit inteiramente nova (medidor + exportador kanban); na mesma rodada, `session/` ganhou RN-N48/N49 + RF-08 (consentimento, f024) e `microdecisoes/` teve RN-N44 revisada e RF-06 reescrito (advisory, f025) — os quatro 🟡 da `progress/` são as pendências operacionais listadas no `design.md` (conferência visual do board, paridade por convenção, medidor sem gatilho de hook, condução manual das demandas).

### Artefatos de interpretação e arquitetura

| Artefato                                     | Veredito | Observação                                                                                                                              |
| :------------------------------------------- | :------- | :-------------------------------------------------------------------------------------------------------------------------------------- |
| `code-analysis.md`                           | 🟢 forte | Estendido para 12 unidades; detalha as modificações no `FormattingService` e o locking determinístico.                                  |
| `domain.md`                                  | 🟢 forte | Incorpora as regras novas RN-N18 a RN-N25 sobre upstream, atualizações passivas locais, exclusão dinâmica glob de formatação e locking. |
| `state-machines.md`                          | 🟢 forte | Preservado; o ciclo de vida das sessões e decisões arquiteturais não sofreu alterações nas regras de transições do núcleo.              |
| `permissions.md`                             | 🟡 médio | Atualizado com os privilégios dos novos comandos `init` e `upgrade` mapeados a ações de setup manuais (do humano).                      |
| `data-dictionary.md`                         | 🟢 forte | Modelo `HarnessConfig` tipado agora contempla os campos `upstream_path` e `version` na seção `[harness]`.                               |
| `architecture.md`, `c4-*`, `erd-complete.md` | 🟢 forte | C4, ERD e dependências atualizados para refletir o consumo de configurações ativas e a compatibilidade dinâmica com glob patterns.      |
| `traceability/spec-impact-matrix.md`         | 🟢 forte | Mapeia o impacto e dependências no core para os novos fluxos e a resolução de T4/T6.                                                    |
| `traceability/code-spec-matrix.md`           | 🟢 forte | Atualizado com os novos arquivos (`requirements.in` e `.github/workflows/ci.yml`).                                                      |
| `inventory.md`, `dependencies.md`            | 🟢 forte | Atualizados; estatísticas gerais refletem a introdução do lock file com `uv` e da matriz de integração contínua (CI).                   |

## Resumo Geral (reconciliação 2026-07-15 — MD-0014 + features 022-023)

> Mesmo protocolo da rodada anterior: avalia-se a confiança do **delta** reconciliado, não a base histórica.

| Nível             | Quantidade (estimativa do delta) | Percentual do delta |
| :---------------- | :------------------------------: | :-----------------: |
| 🟢 CONFIRMADO     |               ~46                |         96%         |
| 🟡 INFERIDO       |                ~2                |         4%          |
| 🔴 LACUNA         |                0                 |         0%          |
| **Total (delta)** |              **~48**             |      **100%**       |

**Confiança do delta reconciliado (MD-0014 + 022-023):** **~98%** 🟢 — a mais alta de qualquer rodada, por três razões: (1) todo o conteúdo foi lido diretamente do código as-built (`gate.py` integral, diffs de `main.py`/`close_flow.py`/`serializer.py`/`models.py`/`config.py`/`hook_bridge.py`/`claude_settings.py`/`harness_profiles.py`); (2) as features 022/023 nasceram por TDD com specs forward completas (requirements com esclarecimentos, roadmap, actions 9/9), cruzadas nesta reconciliação; (3) a suíte de 300 testes e os smokes reais (A–F da 022, A–E 9/9 da 023) foram relatados nos fechamentos das sessões e as fichas MD-0015/MD-0016 documentam decisão e descartes. Os ~2 🟡 são: a contagem de 300 testes (relato de sessão, não recontada por execução nesta rodada) e o efeito colateral da remoção da assinatura `"harness format"` (itens legados preservados como de terceiros — comportamento deduzido do merge por-item + teste `test_migrate.py`, não smoke-testado em projeto-alvo real nesta rodada).

## Resumo Geral (reconciliação 2026-08-11 — features 024-027)

> Mesmo protocolo das rodadas anteriores: avalia-se a confiança do **delta** reconciliado, não a base histórica.

| Nível             | Quantidade (estimativa do delta) | Percentual do delta |
| :---------------- | :------------------------------: | :-----------------: |
| 🟢 CONFIRMADO     |               ~68                |         93%         |
| 🟡 INFERIDO       |                ~5                |         7%          |
| 🔴 LACUNA         |                0                 |         0%          |
| **Total (delta)** |              **~73**             |      **100%**       |

**Confiança do delta reconciliado (024-027):** **~97%** 🟢 — todo o conteúdo foi lido do código as-built (`close_flow.py`, `commands/service.py`, `main.py`, o pacote `core/progress/` integral) e cruzado com as specs forward das quatro features (requirements com esclarecimentos, roadmaps, actions) e as fichas MD-0017..MD-0020; as quatro nasceram por TDD e a suíte 372 verde foi relatada nos fechamentos. Os ~5 🟡: (1) a conferência visual do board no fork do vscode-kanban permanece pendente do mantenedor (ids não numéricos, campos opcionais, efeito de mover card gerenciado na UI — Observações do regression-watch da 027); (2) a paridade `stages.py` ↔ prosa do skill é convenção vigiada por teste, não derivação (ADR 0026); (3) a contagem de 372 testes é relato de sessão, não recontada por execução nesta rodada; (4) o comportamento do marker `ENCERRAMENTO_NAO_VERSIONADO` na skill 1.4.0 foi conferido no asset, não em sessão real de encerramento pós-024; (5) T028 da 024 (propagação manual à base migrada) segue pendente por decisão, com a feature pausada em 27/28.

## Resumo Geral (reconciliação 2026-08-11-b — feature 028)

> Mesmo protocolo: avalia-se a confiança do **delta** reconciliado, não a base histórica.

| Nível             | Quantidade (estimativa do delta) | Percentual do delta |
| :---------------- | :------------------------------: | :-----------------: |
| 🟢 CONFIRMADO     |               ~24                |         96%         |
| 🟡 INFERIDO       |                ~1                |         4%          |
| 🔴 LACUNA         |                0                 |         0%          |
| **Total (delta)** |              **~25**             |      **100%**       |

**Confiança do delta reconciliado (028):** **~98%** 🟢 — delta pequeno e integralmente lido do código as-built (`decisions/service.py` 195 linhas, `resume_context.py` 47, `init_service.py` 368, `config.py` 111, `hook_bridge.py` 197, `main.py`), cruzado com a spec forward da 028 (requirements com esclarecimentos, roadmap, actions, legacy-impact, regression-watch W001-W008) e a ficha MD-0022; TDD com suíte 389 verde relatada no fechamento. O único 🟡: a contagem de 389 testes é relato de sessão desta mesma data, não recontada por execução independente nesta rodada de re-extração. Nota: MD-0021 (abandono do vault Obsidian no encerramento) é decisão **operacional sem código** — registrada como nota de rodada em `domain.md#2.26`, sem RN própria, deliberadamente.

### Reconciliação 2026-08-11-b — delta feature 028

| Artefato                                                                     | Veredito | Observação                                                                                                                                                                                                                    |
| :--------------------------------------------------------------------------- | :------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `inventory.md`, `surface.json`                                               | 🟢 forte | Fichas 20→22, suíte 372→389, core 2.6.0; novo artefato derivado `.harness/decisoes-recentes.md`; README.md novo na raiz; delta sem commit sinalizado.                                                                          |
| `code-analysis.md`, `data-dictionary.md`, `modules.json`                     | 🟢 forte | `compile_compact_view`/`_extract_title`/`_write_if_changed` (§4), precedência compacta→índice no resume (§8), guidance idempotente no init (§1), config e bordas (§9/§11/§12); dicionário com os 2 campos novos e o formato da compacta. |
| `domain.md`, `permissions.md`, ADR 0028                                      | 🟢 forte | RN-N41 revisada in-place (§2.18) + §2.26 nova (RN-N56..N58) + 2 entradas de glossário; matriz de permissões com `init`/`decisions`/`cmd resume` atualizadas e a salvaguarda da posse do artefato derivado; ADR 0028 com alternativas descartadas da MD-0022. |
| `architecture.md`, `c4-components.md`, `erd-complete.md`                     | 🟢 forte | Nenhum componente novo (métodos em componentes existentes — refletido como revisão, não linha nova); ERD com `DECISIONS_SECTION.compact_file`/`compact_index_size` e população 20→22; sem mudança de schema em `SESSION_STATE`. |
| specs SDD (`microdecisoes/`, `comandos-customizados/`, `bootstrap/`) + `code-spec-matrix.md` | 🟢 forte | RN-N56/N57 e RF-08 na unit de decisões; RN-N41/RF-08 revisados + 2 cenários na unit de comandos (onde o contrato do resume vive); nota RN-N58 na unit de bootstrap; matriz sem arquivo novo, 4 linhas atualizadas.              |
| `spec-impact-matrix.md`                                                      | 🟢 forte | Subseção 028; linhas `DecisionService`/`resume_context`/`InitService`/`config`/ponte atualizadas com RN-N56..N58 e features/ADRs 028.                                                                                          |

### Reconciliação 2026-08-11 — delta features 024-027

| Artefato                                                                     | Veredito | Observação                                                                                                                                                                                                                   |
| :--------------------------------------------------------------------------- | :------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `inventory.md`, `dependencies.md`, `surface.json`                            | 🟢 forte | Contagens atualizadas (13 subcomandos com `progress`, 20 fichas, suíte 372, core 2.5.0); nenhuma dependência nova nas quatro features.                                                                                        |
| `code-analysis.md`, `data-dictionary.md`, `modules.json`                     | 🟢 forte | Nova unidade `core/progress/` (13ª); consentimento no `close_flow`/`CommandService`; `Medicao` e o contrato do board no dicionário (§10/§11).                                                                                 |
| `domain.md`, `state-machines.md`, `permissions.md`, ADRs 0024-0027           | 🟢 forte | §2.22-2.25 novas (RN-N48..N55); RN-N31/RN-N44 revisadas in-place; máquina do encerramento com os dois desfechos válidos (com/sem commit); matriz de permissões com a linha `progress` e quatro salvaguardas novas.            |
| `architecture.md`, `c4-containers/components.md`, `erd-complete.md`          | 🟢 forte | 13 unidades; `core/progress` nos dois diagramas C4 com os artefatos derivados; ERD com `PROGRESS_SECTION`/`PROGRESS_KANBAN_SECTION` e a família efêmera `MEDICAO`; **sem mudança de schema** em `SESSION_STATE`/`GATE_VERDICT` (a 024 muda fluxo, não dado). |
| specs SDD (`session/`, `microdecisoes/`, nova `progress/`) + `code-spec-matrix.md` | 🟢 forte | `session/` com RN-N48/N49 e RF-08; `microdecisoes/` com RN-N44 revisada e RF-06 reescrito (advisory); `progress/` é unit inteiramente nova (requirements/design/tasks); matriz com 12 units e os dois artefatos derivados.     |
| `spec-impact-matrix.md`                                                      | 🟢 forte | Linhas ✨✨✨✨ para o medidor (HIGH) e o exportador (MEDIUM); item 10 de impacto crítico (tripwire de pureza + posse por namespace); subseções 024-027.                                                                        |

### Reconciliação 2026-07-05 — artefatos estruturais (Scout/Archaeologist/Architect)

| Artefato                                                                    | Veredito | Observação                                                                                                                                                                                                                                                     |
| :-------------------------------------------------------------------------- | :------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `inventory.md`, `dependencies.md`, `surface.json`                           | 🟢 forte | Estavam congelados desde 2026-06-24 (feature 009) e nunca refletiam a relocação de caminhos da feature 011 — corrigido; contagens de arquivos/testes atualizadas (90 Python, 33 test\_\*.py, 12 fichas de decisão).                                            |
| `code-analysis.md`, `data-dictionary.md`, `modules.json`                    | 🟢 forte | Congelados desde 009; ganharam a 13ª/12ª unidade `core/migrate` e a expansão de `core/session` (`close_flow.py`, `resume_context.py`). Caminhos corrigidos para `.harness/harness-core/`.                                                                      |
| `c4-components.md`, `erd-complete.md`, `traceability/spec-impact-matrix.md` | 🟢 forte | Congelados desde 009 — os mais defasados do conjunto (nem a relocação de 011 estava refletida). Reconciliados integralmente nesta rodada; novo achado T7 documentado no `erd-complete.md` e `architecture.md`.                                                 |
| `architecture.md`, `c4-context.md`, `c4-containers.md`                      | 🟢 forte | `architecture.md` já cobria até a feature 018 no corpo (mas não no cabeçalho/ADRs, corrigido); `c4-containers.md` estava mais defasado que `c4-components.md` (não incluía nem o driver do Antigravity, f009) — redesenhado com o split shim/upstream da f020. |
| `domain.md`, `state-machines.md`, `permissions.md`, ADRs 0019-0021          | 🟢 forte | `domain.md` já estava atualizado até a f018 (§2.15) pela reconciliação de 2026-06-28; esta rodada acrescentou §2.16-2.18 (019-021) e revisou RN-N19/20/21 para refletir o desescopo da 020 (ver abaixo).                                                       |

### Reconciliação 2026-07-15 — delta MD-0014 + features 022-023

| Artefato                                                                     | Veredito | Observação                                                                                                                                                                                                                                       |
| :--------------------------------------------------------------------------- | :------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `inventory.md`, `surface.json`                                               | 🟢 forte | Contagens atualizadas (92 Python, 34 test\_\*.py, 16 fichas, suíte 300, core 2.1.1); hooks do Claude corrigidos (sem `PostToolUse`, Stop com `--gate`).                                                                                            |
| `code-analysis.md`, `data-dictionary.md`, `modules.json`                     | 🟢 forte | Nova subseção `gate.py` (§4), 3º portão (§8), `--gate`/`--sem-decisao` na borda (§11), advisory (§12); `GateVerdict` (§9 do dicionário) e campos anti-loop do `SessionState` (§1).                                                                 |
| `domain.md`, `state-machines.md`, `permissions.md`, ADRs 0022-0023           | 🟢 forte | §2.19-2.21 novas (RN-N42..N47); máquina de estado da sessão com 3 portões e fingerprints zerados no fechamento; ADR 0002 já estava emendado ("parcialmente revertido") pela sessão da MD-0014.                                                     |
| `architecture.md`, `c4-context/containers/components.md`, `erd-complete.md`  | 🟢 forte | Diagrama com `decisions/gate.py`; ganchos do Claude atualizados; ERD com os dois campos novos, `require_registration` e `GATE_VERDICT`.                                                                                                            |
| specs SDD (`microdecisoes/`, `session/`, `format-on-edit/`, `comandos-customizados/`) + `code-spec-matrix.md` | 🟢 forte | Gate especificado na unit de decisões (RF-05..07 + gherkin do soft-block único e do rearme do portão); ressalva T1 stale removida da RN-N11; `format-on-edit/` com o gatilho revisto (MD-0014) sem tocar as RNs do serviço, que permanecem válidas. |
| `spec-impact-matrix.md`                                                      | 🟢 forte | Nova linha `decisions/gate` (HIGH) + item 9 de impacto crítico; corrigidas duas menções stale de "T7 aberto" que contradiziam o próprio rodapé do arquivo.                                                                                          |

---

## Lacunas Pendentes 🔴

- **Nenhuma lacuna técnica ou de reprodutibilidade pendente das features 001-008.** Todos os itens de build não determinístico (T6) e configurações de formatação inertes (T4) foram 100% solucionados na feature 008.
- **T7 (2026-07-05, RESOLVIDO no mesmo dia — MD-0013):** o servidor MCP gravava o cache de sincronia em `.harness/sync_cache.json` (underscore, chumbado em `server.py:42`); a CLI usava `.harness/sync-cache.json` (hífen), o mesmo nome que o `.gitignore` do `init` cobre — o cache do MCP escapava do `.gitignore` e, desde a feature 019, seria oferecido para commit por engano. Saneado via fonte única `layout.py:SYNC_CACHE_REL_PATH` (consumida por CLI, `close_flow.py` e MCP), com TDD em `test_mcp.py` e bump do core para 2.0.1. Artefatos atualizados: `architecture.md` §5, `erd-complete.md` §3, `c4-containers.md`, `data-dictionary.md`, `sync-check/`, `gaps.md#G-12`.
- **Desescopo da 020 — decisão documentada, não lacuna:** o plano original da feature 020 previa remover `upgrade_project`/`SyncService`/o campo `version` (tornando `upgrade` um no-op). A varredura de implementação revelou que ambos sustentam a `UpgradeOffer` do encerramento de sessão (feature 014); o mantenedor **decidiu explicitamente adiar** essa remoção (registrado em `actions.md` da 020, `domain.md` nota de reconciliação, ADR 0020). Não é uma lacuna de conhecimento — é uma decisão de escopo já tomada e documentada; citada aqui só para deixar claro que **não** é um erro de reconciliação `upgrade`/`SyncService` ainda aparecerem como "ativos" nos artefatos.

---

## Histórico de Reclassificações

|       De       |      Para       | Afirmação                                               | Evidência / Justificativa                                                                                                                                                                                    |
| :------------: | :-------------: | :------------------------------------------------------ | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
|       🟡       | 🟢 (resolvido)  | `bootstrap/`: regras de init/upgrade                    | Implementadas nativamente, cobertas em testes automatizados físicos (`test_init.py`) e ganchos Git validados com sucesso no host.                                                                            |
|       🟢       |  🟢 (mantido)   | T1/T2/T3 corrigidos                                     | T1/T3 no commit `cf73980`; T2 por config na feature 006.                                                                                                                                                     |
|    🔴 (T5)     | 🟢 (resolvido)  | T5 — "duas vias de config"                              | Feature 006 removeu `load_harness_config` e `import toml` de `main.py`; via única tipada `load_config`.                                                                                                      |
|    🟡 (T4)     | 🟢 (resolvido)  | T4 — "configs de formatting inertes"                    | Resolvido na feature 008: `FormattingService` passa a consumir dinamicamente `exclude_paths` (com glob matching) e `opt_out_file`.                                                                           |
|    🔴 (T6)     | 🟢 (resolvido)  | T6 — "build não determinístico / sem lock file"         | Resolvido na feature 008: Adição do compilador de pacotes `uv` com locking determinístico no `requirements.txt` e validação multi-SO/Python no CI.                                                           |
|       🟡       |       🟢        | `inventory.md`: `core/ports/` descrito como "Protocols" | **G-04 fechado nesta rodada** — corrigido para `ABC`/`abstractmethod`, coerente com `code-analysis.md`/`modules.json` e com o código (`from abc import ABC, abstractmethod`).                                |
|       —        |    🔴 (novo)    | T7 — cache de sync com nomes divergentes CLI×MCP        | Achado nesta reconciliação (não existia como afirmação nos relatórios anteriores porque `c4-containers.md`/`erd-complete.md` nunca haviam sido atualizados para cruzar os dois literais). Ver Lacunas acima. |
| 🟡 (histórica) | 🟢 (confirmado) | RN-N19 (`init` copia o core e cria venv)                | Reclassificada como **histórica/substituída** por RN-N36 (fonte única, f020) — o comportamento descrito pela RN-N19 original só se aplica hoje a instalações ainda não convertidas por `migrate`.            |
|   🟡 (stale)   | 🟢 (corrigido)  | RN-N11: "via MCP `load_config` quebra (T1)"             | **2026-07-15:** a ressalva em `microdecisoes/requirements.md` estava stale — T1 foi resolvido em `cf73980` e todos os demais artefatos já o diziam; removida.                                                |
|   🟢 (stale)   | 🟢 (corrigido)  | ADR 0002 / hooks do Claude com `PostToolUse`            | **2026-07-15:** MD-0014 aposentou o gatilho; `c4-context.md`, `permissions.md`, `architecture.md` §4/§6, `format-on-edit/` e `code-spec-matrix.md` atualizados (o ADR 0002 em si já fora emendado em 07/07). |
|       —        |    🟢 (novo)    | Gate de registro (022) e dupla identidade (023)         | **2026-07-15:** ~48 afirmações novas, 96% confirmadas por leitura direta do código as-built + specs forward + fichas MD-0015/MD-0016.                                                                        |
| 🟢 (redação 022) | 🟢 (revisada)  | RN-N44 — enforcement híbrido em três bordas             | **2026-08-11:** a 025 colapsou as três políticas em duas (portão duro único no encerramento; advisory nos fins de turno); a redação foi revisada in-place em `domain.md` §2.20, não substituída — a mecânica do gate sobrevive integral. |
| 🟢 (redação 013) | 🟢 (revisada)  | RN-N31 — commit incondicional do encerramento           | **2026-08-11:** a 024 condiciona o commit ao consentimento (`versionar_estado`); RN-N48/N49 assumem a política; o MCP preserva o comportamento antigo (D-04).                                                |
|       —        |    🟢 (novo)    | Medidor read-only (026) e exportador kanban (027)       | **2026-08-11:** ~73 afirmações novas no delta 024-027, 93% confirmadas por leitura direta do pacote `core/progress/` + specs forward + fichas MD-0017..MD-0020.                                              |

`doc_level = completo` e o plugin do Codex **não está disponível** nesta sessão (não há ferramentas `codex:*`). A etapa de revisão cruzada foi pulada conforme o protocolo.
