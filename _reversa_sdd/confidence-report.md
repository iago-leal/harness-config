# Relatório de Confiança — harness

> Regenerado pelo Revisor em 2026-06-24 (Re-extração após as features 003, 004 e 005)
> Nível de Documentação: **Completo** · Escala: 🟢 CONFIRMADO · 🟡 INFERIDO · 🔴 LACUNA

Sintetiza a avaliação de confiança da **re-extração** do ecossistema `harness` — núcleo Python `harness-core` (arquitetura hexagonal), wrapper de raiz, servidor MCP e documentação HTML — após o purge do legado `claude-config/` (commit `5624f78`) e a migração de estado e decisões para `.harness/`. Substitui integralmente o relatório anterior (feature 002), que ficou obsoleto: citava artefatos do legado já purgado (`harness-config/bin/*.sh`).

---

## Resumo Geral

| Nível         | Quantidade | Percentual |
| :------------ | :--------: | :--------: |
| 🟢 CONFIRMADO |    251     |   76.3%    |
| 🟡 INFERIDO   |     56     |   17.0%    |
| 🔴 LACUNA     |     22     |    6.7%    |
| **Total**     |  **329**   |  **100%**  |

**Confiança geral do projeto:** **84.8%** 🟢
_(Cálculo: (251 + 56 × 0.5) / 329 = 84.8%)_

> A confiança é **alta**, sustentada por código-fonte real e por verificação dirigida dos três bugs latentes diretamente no `harness-core/`. A queda frente ao relatório anterior (97%) é honesta, não regressão: a re-extração expôs lacunas legítimas (reprodutibilidade, dívidas T4–T6) que a extração da feature 002 havia mascarado com 🟢 de excesso de confiança. As contagens 🟢/🟡/🔴 são estimativas agregadas das marcações presentes nos artefatos.

---

## Por Spec / Artefato

### Specs por unit (geração)

| Unidade de Especificação (Unit) | 🟢  | 🟡  | 🔴  | Confiança |
| :------------------------------ | :-: | :-: | :-: | :-------: |
| `install/` ✨ (f003)            | 26  |  4  |  0  |    93%    |
| `session/` ✨ (f004)            | 27  |  6  |  0  |    91%    |
| `microdecisoes/` (f005)         | 35  |  9  |  3  |    81%    |
| `format-on-edit/`               | 38  | 13  |  4  |    79%    |
| `sync-check/`                   | 30  |  7  |  4  |    81%    |
| `comandos-customizados/`        | 40  |  6  |  4  |    88%    |
| `bootstrap/`                    | 14  |  5  |  3  |    75%    |
| `documentacao-uso-html/`        | 20  |  3  |  2  |    84%    |
| `run-harness-core-local/`       | 22  |  2  |  2  |    88%    |

> ✨ = unit nova nesta re-extração. As lacunas 🔴 das units são, em sua maioria, marcações "nenhuma lacuna" nas seções de `tasks.md` ou ressalvas de cobertura — não bloqueiam reimplementação.

### Artefatos de interpretação e arquitetura

| Artefato                                     | Veredito | Observação                                                                                                     |
| :------------------------------------------- | :------- | :------------------------------------------------------------------------------------------------------------- |
| `code-analysis.md`                           | 🟢 forte | Verificação dirigida (V1/V2/V3 + achado adicional) bate com o código real. T1/T2/T3 confirmados linha a linha. |
| `domain.md`                                  | 🟢 forte | RN-01..RN-10 + RN-N1..RN-N15 ancoradas em código; bugs T1–T6 na tabela de dívidas.                             |
| `state-machines.md`                          | 🟢 forte | Corrigiu os estados fictícios (`em-revisao`/`rejeitado` removidos); só `ativo`/`descartado`.                   |
| `permissions.md`                             | 🟡 médio | Matriz é convenção inferida (sem RBAC no código) — corretamente marcada 🟡; gatilhos de hook 🟢.               |
| `data-dictionary.md`                         | 🟢 forte | Modelos Pydantic v2 fiéis; T4 ([formatting] inerte) documentado.                                               |
| `architecture.md`, `c4-*`, `erd-complete.md` | 🟢 forte | Regenerados 2026-06-24; refletem `.harness/`, claude-config purgado, T1/T2/T3.                                 |
| `traceability/spec-impact-matrix.md`         | 🟢 forte | Componentes ✨ marcados; bugs mapeados por componente.                                                         |
| `traceability/code-spec-matrix.md`           | 🟢 forte | Legado purgado sinalizado; units `install/`+`session/` novas.                                                  |
| `inventory.md`, `dependencies.md`            | 🟢 forte | Superfície atual correta; lacuna de lock file 🔴 honesta.                                                      |

---

## Verificação independente dos bugs latentes (no código real)

Reexecutei a verificação dos três bugs latentes diretamente no fonte — **todos confirmados**, e os artefatos os documentam de forma consistente (nenhum afirma que o caminho quebrado funciona):

| Bug    | Evidência no código                                                                                                                                               | Documentado consistentemente em                                                                                        |
| :----- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------- |
| **T1** | `server.py:60` usa `load_config(fs)`; imports vão só até a linha 11 — não há `from src.core.domain.config import load_config`.                                    | code-analysis (V1), domain (T1), spec-impact, code-spec, `microdecisoes/`, inventory                                   |
| **T2** | `server.py:92` = `"ESTADO-DA-SESSAO.md"` × `main.py:192` = `".harness/estado-da-sessao.md"`. `harness.toml` não tem seção `[session]` (sem config para resolver). | code-analysis (V2), domain (RN-N1), state-machines, c4-containers, erd, `session/`, `comandos-customizados/`, ADR 0012 |
| **T3** | `main.py:63` usa `json.loads`; imports (1–18) trazem `os, sys, argparse, toml` — **não** `json`.                                                                  | code-analysis (achado adicional), domain (T3), c4-components, `format-on-edit/`                                        |

> Coerência da escala de bugs: T1/T2/T3 são 🟢 (confirmados, são bugs reais); a **mitigação** "só a CLI funciona" é o que aparece como 🟡 (ressalva) nas regras de domínio. Não há contradição — a regra é confirmada, o caminho MCP é a ressalva.

---

## Lacunas Pendentes 🔴

Itens que permaneceram sem confirmação possível só pelo código (ver `questions.md`):

### Reprodutibilidade temporal

- **Sem lock file e sem CI/CD** — pins apenas `>=` em `requirements.txt`; build não determinístico. Confirmado por `dependencies.md` e `surface.json` (`ci_cd: []`). Decisão do mantenedor, não do código → `questions.md#1`.

### Dívidas conscientes (não bugs, mas pendências de design)

- **T4** — `[formatting]` do `harness.toml` declarado mas não consumido (blindagens chumbadas). Manter chumbado ou ligar à config? → `questions.md#2`.
- **T5** — `load_harness_config` (dict legado) coexiste com `load_config` (tipada) em `main.py`. Consolidar? → `questions.md#3`.
- **T2 (decisão de design)** — ADR 0012 deixou explícito que a seção `[session]` análoga à `[decisions]` **não** foi adotada na f005; o caminho do estado de sessão segue chumbado e divergente CLI×MCP. Corrigir o import/caminho do MCP é a próxima ação? → `questions.md#4`.

### Artefatos não regenerados nesta re-extração (inconsistência cruzada)

- ✅ **RESOLVIDO (2026-06-24, Q5):** `user-stories/fluxo-de-sincronia-e-sessao.md` e **4** dos 5 `flowcharts/*.md` (`bin.md`, `commands.md`, `decisoes.md`, `hooks.md`) datavam de **2026-06-23** e descreviam o **legado purgado** (`sync-check.sh`, `format-on-edit.sh`, `gerar-index-decisoes.sh`, `.claude/ESTADO-DA-SESSAO.md`, manifesto `pyproject.toml`). Foram **removidos** (decisão Q5); o snapshot histórico segue no git (`af4a034`). O quinto flowchart, `harness-core.md` (13:30), já descrevia o core Python atual e foi **mantido**.

---

## Recomendações

- [ ] **Drivers MCP/CLI (T1, T2, T3):** três bugs latentes de severidade alta concentrados em `server.py` e `main.py`. A CLI é o caminho confiável; MCP de decisões e sessão estão degradados, e o autoformat por hook não ocorre. Priorizar correção (fora do escopo desta extração — apenas documentado).
- [ ] **Regenerar `user-stories/` e `flowcharts/`:** alinhar ao estado atual (Python + `.harness/`) ou marcá-los explicitamente como históricos. Hoje contradizem os demais artefatos.
- [ ] **Reprodutibilidade (T6):** adotar lock file e CI mínimo (lint + testes) — Princípio nº 5.3 do mantenedor.
- [ ] **Coesão de configuração (T4, T5):** decidir se `[formatting]` passa a alimentar o serviço e se as duas vias de config (`load_config` × `load_harness_config`) se unificam.
- [ ] **`inventory.md` (cosmético):** corrigir a descrição de `core/ports/` de "interfaces (Protocols)" para `ABC` — o código usa `from abc import ABC, abstractmethod` (consistente com code-analysis e modules.json).

---

## Histórico de Reclassificações

| De  |     Para     | Afirmação                                             | Evidência / Justificativa                                                                                          |
| :-: | :----------: | :---------------------------------------------------- | :----------------------------------------------------------------------------------------------------------------- |
| 🟢  | 🟢 (mantida) | T1/T2/T3 são bugs reais                               | Verificação independente no fonte (`server.py:60/92`, `main.py:63`) confirma o já documentado.                     |
| 🟢  |      🟡      | `inventory.md`: `core/ports/` como "Protocols"        | Contradição com o código (`ABC`/`@abstractmethod`) e com code-analysis/modules.json. Inconsistência terminológica. |
| 🟢  |      🔴      | "100% de cobertura, sem lacunas" (relatório anterior) | Obsoleto: citava o legado purgado e ignorava lock file / CI ausentes e as dívidas T4–T6.                           |
| n/a |      🔴      | `user-stories/` + `flowcharts/` desatualizados        | Não regenerados; descrevem o legado purgado — inconsistência cruzada nova.                                         |

---

## Nota sobre revisão cruzada

`doc_level = completo` e o plugin do Codex **não está disponível** nesta sessão (não há ferramentas `codex:*`). Conforme o SKILL.md, a etapa de revisão cruzada é ignorada sem menção de motivo ao usuário; registrada aqui apenas para rastreabilidade. Revisão conduzida apenas pelo Revisor.
