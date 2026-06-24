# Lacunas Pendentes (Gaps) — harness

> Regenerado pelo Revisor em 2026-06-24 (Re-extração após as features 003, 004 e 005)
> Nível de Documentação: **Completo** · Escala: 🟢 CONFIRMADO · 🟡 INFERIDO · 🔴 LACUNA

Lacunas que permaneceram sem resolução possível apenas pela leitura do código, mais inconsistências entre artefatos detectadas na revisão crítica. Substitui o `gaps.md` anterior (feature 002), que declarava "nenhuma lacuna" — afirmação obsoleta, baseada num inventário que ainda incluía o legado purgado.

> ⚠️ **Distinção importante:** os bugs latentes **T1, T2, T3** **não são lacunas de especificação** — são comportamentos *confirmados* (🟢) e documentados de forma consistente em todos os artefatos. Estão listados aqui apenas como contexto para a seção de dívidas; **não foram corrigidos** (regra da extração).

---

## 🔴 Crítico — bloqueia ou degrada o uso real

Nenhuma lacuna *crítica de especificação* impede a reimplementação: a cobertura do código de produto é completa e os três bugs latentes estão plenamente caracterizados. O que existe de crítico é **operacional**, não de conhecimento:

| ID | Item | Natureza | Onde |
| :--- | :--- | :--- | :--- |
| G-01 | **T1/T2/T3 não corrigidos** | Bugs reais documentados; CLI confiável, MCP de decisões/sessão e autoformat por hook degradados. | `code-analysis.md`, `domain.md §3`, `spec-impact-matrix.md` |

> G-01 não é lacuna de *spec* — é uma decisão de "documentar, não corrigir". Listado para visibilidade.

---

## 🟡 Moderado — inconsistências entre artefatos (precisam de ação)

| ID | Item | Detalhe | Resolução sugerida |
| :--- | :--- | :--- | :--- |
| G-02 | **`user-stories/fluxo-de-sincronia-e-sessao.md` desatualizado** | Datado 2026-06-23, título "harness-config". Cita `sync-check.sh` (l.23), `format-on-edit.sh` + manifesto `pyproject.toml` (l.44) e grava no `ESTADO-DA-SESSAO.md` / `microdecisoes.md` na raiz (l.60). Todos referem o **legado purgado** — contradizem o estado atual (Python, `.harness/`, raiz por `.git`/`harness.toml`). | Regenerar alinhado ao core Python, ou marcar como histórico explícito. |
| G-03 | **`flowcharts/*.md` desatualizados (5 arquivos)** | `bin.md`, `commands.md`, `decisoes.md`, `harness-core.md`, `hooks.md` datam de 2026-06-23 e diagramam `sync-check.sh`, `gerar-index-decisoes.sh`, `format-on-edit.sh`, `.claude/ESTADO-DA-SESSAO.md`. Não refletem o `harness-core` atual. | Idem G-02. Não estavam no conjunto regenerado hoje. |
| G-04 | **`inventory.md`: `core/ports/` descrito como "Protocols"** | Linha 44 diz "interfaces (Protocols)"; o código usa `from abc import ABC, abstractmethod` (`fs.py:1`), e `code-analysis.md` / `modules.json` dizem `ABC`. Contradição terminológica. | Trocar "Protocols" por `ABC` no inventory. |
| G-05 | **ADRs 0002 e 0003 sem nota de superação** | Descrevem `hooks/format-on-edit.sh` (0002) e `bin/sync-check.sh` (0003) como mecanismo vigente. Os pares 0001→0012 e 0004→0010 ganharam aviso de delta datado 2026-06-24; 0002/0003 não. O mecanismo shell foi substituído por Python (`core/formatting`, `core/sync`). | Anexar nota de delta apontando os serviços Python que os substituíram. |
| G-06 | **Atribuição de bug na `spec-impact-matrix`** | A linha de `FormattingService` lista "T3, T4". T3 é, na origem, bug de `main.py` (json não importado); T4 é o de `formatting`. A atribuição de T3 ao FormattingService é defensável (o efeito recai sobre o autoformat), mas a *localização* do bug é `main.py`. | Esclarecer que T3 afeta o fluxo de formatting mas reside em `main.py`, ou mover T3 para a linha do CLI driver (onde já consta). |

---

## 🔵 Cosmético / dívida consciente — sem ação obrigatória

| ID | Item | Detalhe |
| :--- | :--- | :--- |
| G-07 | **Sem lock file / sem CI/CD** | `requirements.txt` com pins `>=`; `surface.json.ci_cd = []`. Build não determinístico (T6). Coerente com contexto *single maintainer*, mas dívida de reprodutibilidade (Princípio nº 5.3). |
| G-08 | **`[formatting]` inerte (T4)** | Config declarada no domínio, ignorada pelo serviço; blindagens/opt-out chumbados. Dívida de coesão. |
| G-09 | **Duas vias de config (T5)** | `load_harness_config` (dict legado) coexiste com `load_config` (tipada) em `main.py`. |
| G-10 | **Header de decisões: CLI configurável × MCP derivado** | A CLI usa `config.decisions.header_file`; o MCP deriva `os.path.join(dir, "_cabecalho.md")`, ignorando override. Coincide no default; diverge sob override. (Anulado na prática por T1, que quebra o MCP.) |
| G-11 | **Migração (`_reversa_sdd/migration/`)** | Artefatos do Time de Migração presentes mas não no escopo desta revisão; podem referenciar a topologia anterior. Não auditados aqui. |

---

## Resumo

- **Lacunas de conhecimento que exijam o stakeholder:** poucas e de natureza decisória (reprodutibilidade, rumo das dívidas T4/T5, correção dos bugs) — ver `questions.md`.
- **Inconsistências entre artefatos:** concentradas em material **não regenerado** nesta re-extração (`user-stories/`, `flowcharts/`, ADRs 0002/0003) e numa imprecisão terminológica (`inventory.md` "Protocols"). Nenhuma compromete a fidelidade dos artefatos centrais (code-analysis, domain, matrizes, C4, specs por unit), que estão coerentes entre si e com o código.
- **Cobertura de produto:** completa. Todo `service.py` de `core/*`, os 3 adaptadores físicos, os 2 drivers e o wrapper têm unit correspondente.
