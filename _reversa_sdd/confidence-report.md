# Relatório de Confiança — harness

> Regenerado pelo Revisor em 2026-06-24 (Re-extração após a feature 008-reprodutibilidade-e-config)
> Nível de Documentação: **Completo** · Escala: 🟢 CONFIRMADO · 🟡 INFERIDO · 🔴 LACUNA
> **Reconciliação de 2026-07-05** (Reviewer, pós-features 010-021): Scout, Archaeologist, Detective, Architect e Writer reconciliaram nesta sessão os artefatos que estavam congelados desde a feature 009 (`inventory.md`, `dependencies.md`, `surface.json`, `code-analysis.md`, `data-dictionary.md`, `modules.json`, `c4-components.md`, `erd-complete.md`, `traceability/spec-impact-matrix.md`) e incorporaram as features 019-021 em `domain.md`/`state-machines.md`/`permissions.md`/ADRs/`architecture.md`/specs SDD. Ver seção "Reconciliação 2026-07-05" abaixo para o detalhe do que mudou desde o relatório de 2026-06-24.

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

> 🛠️ = unit significativamente refinada na feature 008 para consumir configurações e padrões glob.
> 🚀 = unit significativamente expandida na feature 007 para cobrir bootstrapping e evolução não destrutiva; estendida na f020 (`bootstrap/shim.py`, `claude_settings.py`).
> 🆕 = conteúdo novo desta reconciliação de 2026-07-05. `comandos-customizados/` ganhou +11 afirmações 🟢 (RN-N34/N35/N41, RF-06/07/08, rastreabilidade de `close_flow.py`/`resume_context.py`); `migrate/` é uma unit inteiramente nova (nunca revisada antes por não existir).
> `antigravity-hooks/` não foi objeto de revisão linha-a-linha nesta rodada (fora do escopo da reconciliação 019-021); a contagem é herdada da extração de 2026-06-24 sem verificação adicional.

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

### Reconciliação 2026-07-05 — artefatos estruturais (Scout/Archaeologist/Architect)

| Artefato                                                                    | Veredito | Observação                                                                                                                                                                                                                                                     |
| :-------------------------------------------------------------------------- | :------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `inventory.md`, `dependencies.md`, `surface.json`                           | 🟢 forte | Estavam congelados desde 2026-06-24 (feature 009) e nunca refletiam a relocação de caminhos da feature 011 — corrigido; contagens de arquivos/testes atualizadas (90 Python, 33 test\_\*.py, 12 fichas de decisão).                                            |
| `code-analysis.md`, `data-dictionary.md`, `modules.json`                    | 🟢 forte | Congelados desde 009; ganharam a 13ª/12ª unidade `core/migrate` e a expansão de `core/session` (`close_flow.py`, `resume_context.py`). Caminhos corrigidos para `.harness/harness-core/`.                                                                      |
| `c4-components.md`, `erd-complete.md`, `traceability/spec-impact-matrix.md` | 🟢 forte | Congelados desde 009 — os mais defasados do conjunto (nem a relocação de 011 estava refletida). Reconciliados integralmente nesta rodada; novo achado T7 documentado no `erd-complete.md` e `architecture.md`.                                                 |
| `architecture.md`, `c4-context.md`, `c4-containers.md`                      | 🟢 forte | `architecture.md` já cobria até a feature 018 no corpo (mas não no cabeçalho/ADRs, corrigido); `c4-containers.md` estava mais defasado que `c4-components.md` (não incluía nem o driver do Antigravity, f009) — redesenhado com o split shim/upstream da f020. |
| `domain.md`, `state-machines.md`, `permissions.md`, ADRs 0019-0021          | 🟢 forte | `domain.md` já estava atualizado até a f018 (§2.15) pela reconciliação de 2026-06-28; esta rodada acrescentou §2.16-2.18 (019-021) e revisou RN-N19/20/21 para refletir o desescopo da 020 (ver abaixo).                                                       |

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

`doc_level = completo` e o plugin do Codex **não está disponível** nesta sessão (não há ferramentas `codex:*`). A etapa de revisão cruzada foi pulada conforme o protocolo.
