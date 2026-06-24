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

> A confiança é **alta**, sustentada por código-fonte real e por verificação dirigida diretamente no `harness-core/`. Os três bugs latentes T1/T2/T3, abertos na re-extração de 24/06, foram desde então **RESOLVIDOS** (T1/T3 no commit `cf73980`; T2 por configuração na feature 006, commit `e894c59`) 🟢; a feature 006 fechou ainda T5 e a divergência CLI×MCP de caminho de sessão. A queda frente ao relatório original da feature 002 (97%) permanece honesta, não regressão: a re-extração expôs lacunas legítimas (reprodutibilidade, dívida T4) que aquela extração havia mascarado com 🟢 de excesso de confiança. As contagens 🟢/🟡/🔴 são estimativas agregadas das marcações presentes nos artefatos.

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

| Artefato                                     | Veredito | Observação                                                                                                                                                                     |
| :------------------------------------------- | :------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `code-analysis.md`                           | 🟢 forte | Verificação dirigida (V1/V2/V3 + achado adicional) bate com o histórico. T1/T2/T3 foram **RESOLVIDOS** (`cf73980` + feature 006); a divergência CLI×MCP de V2 caiu por config. |
| `domain.md`                                  | 🟢 forte | RN-01..RN-10 + RN-N1..RN-N15 ancoradas em código; T1/T2/T3/T5 já corrigidos; T4 segue como dívida na tabela.                                                                   |
| `state-machines.md`                          | 🟢 forte | Corrigiu os estados fictícios (`em-revisao`/`rejeitado` removidos); só `ativo`/`descartado`.                                                                                   |
| `permissions.md`                             | 🟡 médio | Matriz é convenção inferida (sem RBAC no código) — corretamente marcada 🟡; gatilhos de hook 🟢.                                                                               |
| `data-dictionary.md`                         | 🟢 forte | Modelos Pydantic v2 fiéis; T4 ([formatting] inerte) documentado.                                                                                                               |
| `architecture.md`, `c4-*`, `erd-complete.md` | 🟢 forte | Regenerados 2026-06-24; refletem `.harness/`, claude-config purgado; T1/T2/T3 desde então corrigidos (`cf73980` + feature 006).                                                |
| `traceability/spec-impact-matrix.md`         | 🟢 forte | Componentes ✨ marcados; bugs mapeados por componente.                                                                                                                         |
| `traceability/code-spec-matrix.md`           | 🟢 forte | Legado purgado sinalizado; units `install/`+`session/` novas.                                                                                                                  |
| `inventory.md`, `dependencies.md`            | 🟢 forte | Superfície atual correta; lacuna de lock file 🔴 honesta.                                                                                                                      |

---

## Verificação independente dos bugs latentes (resolvidos após a re-extração) 🟢

Na re-extração de 24/06 verifiquei os três bugs latentes diretamente no fonte e os confirmei. **Todos foram corrigidos desde então** (T1/T3 no commit `cf73980`; T2 por configuração na feature 006, `e894c59`), e os artefatos foram atualizados de forma consistente:

| Bug    | Achado original (re-extração 24/06)                                                                                                               | Resolução 🟢                                                                                                                                                                                                                        |
| :----- | :------------------------------------------------------------------------------------------------------------------------------------------------ | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **T1** | `process_decisions`/`session_command` em `server.py` chamavam `load_config` sem o import (`NameError`).                                           | Resolvido em `cf73980`: `server.py:12` importa `from src.core.domain.config import load_config`. A tool MCP `process_decisions` não levanta mais `NameError`.                                                                       |
| **T2** | `server.py` apontava `"ESTADO-DA-SESSAO.md"` na raiz × CLI em `.harness/estado-da-sessao.md` (divergência); `harness.toml` sem seção `[session]`. | Resolvido por configuração na feature 006 (`e894c59`): nova `SessionSection` + seção `[session]`; CLI (`main.py:169`) e MCP (`server.py:94`) leem `config.session.state_file`. Sem literal chumbado; divergência CLI×MCP eliminada. |
| **T3** | `main.py` usava `json.loads` sem importar `json` — autoformat por hook quebrava.                                                                  | Resolvido em `cf73980`: `main.py:5` importa `json`. `resolve_format_target` → `json.loads` opera; o autoformat via hook `PostToolUse` funciona.                                                                                     |

> Histórico de confiança: na re-extração, T1/T2/T3 eram 🟢 (bugs reais confirmados) e a mitigação "só a CLI funciona" aparecia como 🟡 (ressalva) nas regras de domínio. Com a correção (`cf73980` + feature 006), o caminho MCP deixa de ser ressalva: decisões e sessão via MCP operam pela via tipada e por `config.session.state_file`.

---

## Lacunas Pendentes 🔴

Itens que permaneceram sem confirmação possível só pelo código (ver `questions.md`):

### Reprodutibilidade temporal

- **Sem lock file e sem CI/CD** — pins apenas `>=` em `requirements.txt`; build não determinístico. Confirmado por `dependencies.md` e `surface.json` (`ci_cd: []`). Decisão do mantenedor, não do código → `questions.md#1`.

### Dívidas conscientes (não bugs, mas pendências de design)

- **T4** — `[formatting]` do `harness.toml` declarado mas não consumido (blindagens chumbadas). Manter chumbado ou ligar à config? → `questions.md#2`. _Única dívida desta lista ainda aberta._
- ✅ **T5 — RESOLVIDO (feature 006):** `load_harness_config` (dict legado) e `import toml` foram **removidos** de `main.py`. Via ÚNICA de configuração: tudo por `load_config(fs)` tipada; o subcomando `cmd` lê `config.harness.active_harness`. Não há mais "duas vias de config". 🟢
- ✅ **T2 — RESOLVIDO (feature 006):** a seção `[session]` (com `state_file`) foi adotada, revertendo a pendência do ADR 0012. O caminho do estado de sessão deixa de ser chumbado e divergente: CLI e MCP leem `config.session.state_file`. 🟢

### Artefatos não regenerados nesta re-extração (inconsistência cruzada)

- ✅ **RESOLVIDO (2026-06-24, Q5):** `user-stories/fluxo-de-sincronia-e-sessao.md` e **4** dos 5 `flowcharts/*.md` (`bin.md`, `commands.md`, `decisoes.md`, `hooks.md`) datavam de **2026-06-23** e descreviam o **legado purgado** (`sync-check.sh`, `format-on-edit.sh`, `gerar-index-decisoes.sh`, `.claude/ESTADO-DA-SESSAO.md`, manifesto `pyproject.toml`). Foram **removidos** (decisão Q5); o snapshot histórico segue no git (`af4a034`). O quinto flowchart, `harness-core.md` (13:30), já descrevia o core Python atual e foi **mantido**.

---

## Recomendações

- [x] **Drivers MCP/CLI (T1, T2, T3):** ~~três bugs latentes de severidade alta em `server.py` e `main.py`~~ — **RESOLVIDOS** (T1/T3 em `cf73980`; T2 por config na feature 006). MCP de decisões e sessão e o autoformat por hook voltaram a operar.
- [ ] **Regenerar `user-stories/` e `flowcharts/`:** alinhar ao estado atual (Python + `.harness/`) ou marcá-los explicitamente como históricos. Hoje contradizem os demais artefatos.
- [ ] **Reprodutibilidade (T6):** adotar lock file e CI mínimo (lint + testes) — Princípio nº 5.3 do mantenedor.
- [ ] **Coesão de configuração (T4):** decidir se `[formatting]` passa a alimentar o serviço. (T5 já resolvido na feature 006: via única `load_config`; `load_harness_config` removida.)
- [ ] **`inventory.md` (cosmético):** corrigir a descrição de `core/ports/` de "interfaces (Protocols)" para `ABC` — o código usa `from abc import ABC, abstractmethod` (consistente com code-analysis e modules.json).

---

## Histórico de Reclassificações

|   De    |      Para       | Afirmação                                             | Evidência / Justificativa                                                                                                                             |
| :-----: | :-------------: | :---------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------- |
|   🟢    |  🟢 (mantida)   | T1/T2/T3 eram bugs reais na re-extração               | Verificação independente no fonte confirmou os três achados.                                                                                          |
|   🟢    | 🟢 (resolvidos) | T1/T2/T3 corrigidos                                   | T1/T3 em `cf73980` (imports `load_config` e `json`); T2 por config na feature 006 (`SessionSection` + `[session]`). MCP e autoformat voltam a operar. |
| 🔴 (T5) | 🟢 (resolvido)  | T5 — "duas vias de config"                            | Feature 006 removeu `load_harness_config` e `import toml` de `main.py`; via única tipada `load_config`.                                               |
|   🟢    |       🟡        | `inventory.md`: `core/ports/` como "Protocols"        | Contradição com o código (`ABC`/`@abstractmethod`) e com code-analysis/modules.json. Inconsistência terminológica.                                    |
|   🟢    |       🔴        | "100% de cobertura, sem lacunas" (relatório anterior) | Obsoleto: citava o legado purgado e ignorava lock file / CI ausentes e as dívidas T4–T6.                                                              |
|   n/a   |       🔴        | `user-stories/` + `flowcharts/` desatualizados        | Não regenerados; descrevem o legado purgado — inconsistência cruzada nova.                                                                            |

---

## Nota sobre revisão cruzada

`doc_level = completo` e o plugin do Codex **não está disponível** nesta sessão (não há ferramentas `codex:*`). Conforme o SKILL.md, a etapa de revisão cruzada é ignorada sem menção de motivo ao usuário; registrada aqui apenas para rastreabilidade. Revisão conduzida apenas pelo Revisor.
