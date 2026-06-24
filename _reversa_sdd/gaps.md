# Lacunas Pendentes (Gaps) — harness

> Regenerado pelo Revisor em 2026-06-24 (Re-extração pós-feature 008-reprodutibilidade-e-config)
> Nível de Documentação: **Completo** · Escala: 🟢 CONFIRMADO · 🟡 INFERIDO · 🔴 LACUNA

Lacunas que permaneceram sem resolução possível apenas pela leitura do código, mais inconsistências entre artefatos detectadas na revisão crítica. As lacunas decisórias e dívidas técnicas remanescentes (T4 e T6) foram completamente sanadas na feature 008.

> ⚠️ **Distinção importante:** os bugs latentes **T1, T2, T3** nunca foram lacunas de especificação — eram comportamentos _confirmados_ (🟢) e documentados de forma consistente em todos os artefatos. Foram **RESOLVIDOS** desde a re-extração: T1/T3 no commit `cf73980` (imports de `load_config` e `json`); T2 por configuração na feature 006 (`e894c59`, `SessionSection` + seção `[session]`). Permanecem aqui apenas como memória histórica.

---

## 🔴 Crítico — bloqueia ou degrada o uso real

Nenhuma lacuna _crítica de especificação_ impede a reimplementação: a cobertura do código de produto é completa. Não há mais item crítico operacional aberto — os três bugs latentes foram corrigidos:

| ID   | Item                       | Natureza                                                                                                                                                                 | Onde                                                        |
| :--- | :------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :---------------------------------------------------------- |
| G-01 | ✅ **T1/T2/T3 RESOLVIDOS** | Eram bugs reais documentados (MCP de decisões/sessão e autoformat degradados). Corrigidos: T1/T3 em `cf73980`; T2 por config na feature 006. MCP e hook voltam a operar. | `code-analysis.md`, `domain.md §3`, `spec-impact-matrix.md` |

> G-01 nunca foi lacuna de _spec_ — era "documentar, não corrigir". Encerrado: os bugs foram corrigidos no código (`cf73980` + feature 006). Mantido para visibilidade histórica.

---

## 🟡 Moderado — inconsistências entre artefatos (precisam de ação)

| ID   | Item                                                            | Detalhe                                                                                                                                                                                                                                                                                                                       | Resolução sugerida                                                                                                              |
| :--- | :-------------------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------ |
| G-02 | **`user-stories/fluxo-de-sincronia-e-sessao.md` desatualizado** | Datado 2026-06-23, título "harness-config". Cita `sync-check.sh` (l.23), `format-on-edit.sh` + manifesto `pyproject.toml` (l.44) e grava no `ESTADO-DA-SESSAO.md` / `microdecisoes.md` na raiz (l.60). Todos referem o **legado purgado** — contradizem o estado atual (Python, `.harness/`, raiz por `.git`/`harness.toml`). | ✅ **RESOLVIDO (2026-06-24, Q5)** — arquivo removido. Histórico preservado no git (`af4a034`).                                  |
| G-03 | **`flowcharts/*.md` desatualizados (4 arquivos)**               | `bin.md`, `commands.md`, `decisoes.md`, `hooks.md` datam de 2026-06-23 e diagramam `sync-check.sh`, `gerar-index-decisoes.sh`, `format-on-edit.sh`, `.claude/ESTADO-DA-SESSAO.md` — legado purgado. (Correção: `harness-core.md`, gerado às 13:30, **já descreve o core Python atual** e não integrava o conjunto obsoleto.)  | ✅ **RESOLVIDO (2026-06-24, Q5)** — os 4 obsoletos removidos; `harness-core.md` mantido. Histórico no git (`af4a034`).          |
| G-04 | **`inventory.md`: `core/ports/` descrito como "Protocols"**     | Linha 44 diz "interfaces (Protocols)"; o código usa `from abc import ABC, abstractmethod` (`fs.py:1`), e `code-analysis.md` / `modules.json` dizem `ABC`. Contradição terminológica.                                                                                                                                          | Trocar "Protocols" por `ABC` no inventory.                                                                                      |
| G-05 | **ADRs 0002 e 0003 sem nota de superação**                      | Descrevem `hooks/format-on-edit.sh` (0002) e `bin/sync-check.sh` (0003) como mecanismo vigente. Os pares 0001→0012 e 0004→0010 ganharam aviso de delta datado 2026-06-24; 0002/0003 não. O mecanismo shell foi substituído por Python (`core/formatting`, `core/sync`).                                                       | Anexar nota de delta apontando os serviços Python que os substituíram.                                                          |
| G-06 | **Atribuição de bug na `spec-impact-matrix` — RESOLVIDO** | Resolvido na feature 008: a CLI `main.py` e o MCP `server.py` listam os seus bugs e as resoluções de T3/T4 de forma explícita e coerente. | ✅ **RESOLVIDO (2026-06-24, feature 008)** |


---

## 🔵 Cosmético / dívida consciente — sem ação obrigatória

| ID   | Item                                                    | Detalhe                                                                                                                                                                                                                                                                                     |
| :--- | :------------------------------------------------------ | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| G-07 | **Sem lock file / sem CI/CD (T6) — RESOLVIDO**           | Resolvido na feature 008 com a adoção de `uv` (compilando `requirements.txt` a partir de `requirements.in`) e ativação do pipeline do GitHub Actions `.github/workflows/ci.yml`. |
| G-08 | **`[formatting]` inerte (T4) — RESOLVIDO**              | Resolvido na feature 008: `FormattingService` agora consome as opções de `exclude_paths` (com matching de glob) e `opt_out_file` dinamicamente a partir do `HarnessConfig`. |
| G-09 | ✅ **Duas vias de config (T5) — RESOLVIDO**             | Feature 006 removeu `load_harness_config` (dict legado) e `import toml` de `main.py`. Via ÚNICA tipada `load_config`; o subcomando `cmd` lê `config.harness.active_harness`. Encerrado.                                                                                                     |
| G-10 | **Header de decisões: CLI configurável × MCP derivado** | A CLI usa `config.decisions.header_file`; o MCP deriva `os.path.join(dir, "_cabecalho.md")`, ignorando override. Coincide no default; diverge sob override. (Com T1 resolvido, o MCP volta a executar, então o override divergente passa a ter efeito observável — dívida menor de coesão.) |
| G-11 | **Migração (`_reversa_sdd/migration/`)**                | Artefatos do Time de Migração presentes mas não no escopo desta revisão; podem referenciar a topologia anterior. Não auditados aqui.                                                                                                                                                        |

---

## Resumo

- **Lacunas de conhecimento que exijam o stakeholder:** Nenhuma. Todas as perguntas técnicas e decisórias (Q1 a Q5) foram respondidas e implementadas com sucesso na feature 008.
- **Inconsistências entre artefatos:** concentradas em material **não regenerado** nesta re-extração (`user-stories/`, `flowcharts/`, ADRs 0002/0003) e numa imprecisão terminológica (`inventory.md` "Protocols"). Nenhuma compromete a fidelidade dos artefatos centrais (code-analysis, domain, matrizes, C4, specs por unit), que estão coerentes entre si e com o código.
- **Cobertura de produto:** completa. Todo `service.py` de `core/*`, os 3 adaptadores físicos, os 2 drivers e o wrapper têm unit correspondente.
