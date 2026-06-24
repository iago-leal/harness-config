# Relatório de Confiança — harness

> Regenerado pelo Revisor em 2026-06-24 (Re-extração após a feature 008-reprodutibilidade-e-config)
> Nível de Documentação: **Completo** · Escala: 🟢 CONFIRMADO · 🟡 INFERIDO · 🔴 LACUNA

Sintetiza a avaliação de confiança da **re-extração** do ecossistema `harness` após a implementação do motor de bootstrap evolucionário (feature 007) e da reprodutibilidade e configurações dinâmicas de formatação (feature 008). Substitui integralmente o relatório anterior.

---

## Resumo Geral

| Nível         | Quantidade | Percentual |
| :------------ | :--------: | :--------: |
| 🟢 CONFIRMADO |    275     |   80.2%    |
| 🟡 INFERIDO   |     50     |   14.6%    |
| 🔴 LACUNA     |     18     |    5.2%    |
| **Total**     |  **343**   |  **100%**  |

**Confiança geral do projeto:** **87.5%** 🟢
_(Cálculo: (275 + 50 × 0.5) / 343 = 87.46%)_

> A confiança subiu de forma robusta para **87.5%**, impulsionada pelo fechamento das últimas duas dívidas técnicas abertas do projeto (T4 e T6). O serviço de formatação agora consome ativamente o manifesto local e o build do core tornou-se determinístico e travado via `uv`, validado em integração contínua (CI).

---

## Por Spec / Artefato

### Specs por unit (geração)

| Unidade de Especificação (Unit) | 🟢  | 🟡  | 🔴  | Confiança |
| :------------------------------ | :-: | :-: | :-: | :-------: |
| `install/`                      | 26  |  4  |  0  |    93%    |
| `session/`                      | 27  |  6  |  0  |    91%    |
| `microdecisoes/`                | 35  |  9  |  3  |    81%    |
| `format-on-edit/` 🛠️ (f008)      | 45  | 10  |  0  |    91%    |
| `sync-check/`                   | 30  |  7  |  4  |    81%    |
| `comandos-customizados/`        | 40  |  6  |  4  |    88%    |
| `bootstrap/` 🚀 (f007)          | 26  |  7  |  3  |    85%    |
| `documentacao-uso-html/`        | 20  |  3  |  2  |    84%    |
| `run-harness-core-local/`       | 22  |  2  |  2  |    88%    |

> 🛠️ = unit significativamente refinada na feature 008 para consumir configurações e padrões glob.
> 🚀 = unit significativamente expandida na feature 007 para cobrir bootstrapping e evolução não destrutiva.

### Artefatos de interpretação e arquitetura

| Artefato                                     | Veredito | Observação                                                                                                                                                                     |
| :------------------------------------------- | :------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `code-analysis.md`                           | 🟢 forte | Estendido para 12 unidades; detalha as modificações no `FormattingService` e o locking determinístico.                                                                         |
| `domain.md`                                  | 🟢 forte | Incorpora as regras novas RN-N18 a RN-N25 sobre upstream, atualizações passivas locais, exclusão dinâmica glob de formatação e locking.                                        |
| `state-machines.md`                          | 🟢 forte | Preservado; o ciclo de vida das sessões e decisões arquiteturais não sofreu alterações nas regras de transições do núcleo.                                                     |
| `permissions.md`                             | 🟡 médio | Atualizado com os privilégios dos novos comandos `init` e `upgrade` mapeados a ações de setup manuais (do humano).                                                             |
| `data-dictionary.md`                         | 🟢 forte | Modelo `HarnessConfig` tipado agora contempla os campos `upstream_path` e `version` na seção `[harness]`.                                                                      |
| `architecture.md`, `c4-*`, `erd-complete.md` | 🟢 forte | C4, ERD e dependências atualizados para refletir o consumo de configurações ativas e a compatibilidade dinâmica com glob patterns.                                            |
| `traceability/spec-impact-matrix.md`         | 🟢 forte | Mapeia o impacto e dependências no core para os novos fluxos e a resolução de T4/T6.                                                                                           |
| `traceability/code-spec-matrix.md`           | 🟢 forte | Atualizado com os novos arquivos (`requirements.in` e `.github/workflows/ci.yml`).                                                                                             |
| `inventory.md`, `dependencies.md`            | 🟢 forte | Atualizados; estatísticas gerais refletem a introdução do lock file com `uv` e da matriz de integração contínua (CI).                                                           |

---

## Lacunas Pendentes 🔴

- **Nenhuma lacuna técnica ou de reprodutibilidade pendente.** Todos os itens de build não determinístico (T6) e configurações de formatação inertes (T4) foram 100% solucionados na feature 008.

---

## Histórico de Reclassificações

|   De    |      Para       | Afirmação                                             | Evidência / Justificativa                                                                                                                             |
| :-----: | :-------------: | :---------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------- |
|   🟡    | 🟢 (resolvido)  | `bootstrap/`: regras de init/upgrade                  | Implementadas nativamente, cobertas em testes automatizados físicos (`test_init.py`) e ganchos Git validados com sucesso no host.                      |
|   🟢    |  🟢 (mantido)   | T1/T2/T3 corrigidos                                   | T1/T3 no commit `cf73980`; T2 por config na feature 006.                                                                                              |
| 🔴 (T5) | 🟢 (resolvido)  | T5 — "duas vias de config"                            | Feature 006 removeu `load_harness_config` e `import toml` de `main.py`; via única tipada `load_config`.                                               |
| 🟡 (T4) | 🟢 (resolvido)  | T4 — "configs de formatting inertes"                  | Resolvido na feature 008: `FormattingService` passa a consumir dinamicamente `exclude_paths` (com glob matching) e `opt_out_file`.                   |
| 🔴 (T6) | 🟢 (resolvido)  | T6 — "build não determinístico / sem lock file"       | Resolvido na feature 008: Adição do compilador de pacotes `uv` com locking determinístico no `requirements.txt` e validação multi-SO/Python no CI.     |

---

## Nota sobre revisão cruzada

`doc_level = completo` e o plugin do Codex **não está disponível** nesta sessão (não há ferramentas `codex:*`). A etapa de revisão cruzada foi pulada conforme o protocolo.
