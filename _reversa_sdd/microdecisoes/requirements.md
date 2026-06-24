# Microdecisões (Decisions) — Requisitos (Requirements)

> Regenerado pelo Writer em 2026-06-24 (Re-extração após a feature 005)
> Nível de Documentação: **Completo** · Escala: 🟢 CONFIRMADO · 🟡 INFERIDO · 🔴 LACUNA
> Rastreabilidade ao Legado: [`harness-core/src/core/decisions/service.py`](file:///Users/iagoleal/dev/harness/harness-core/src/core/decisions/service.py); fichas em [`.harness/decisoes/`](file:///Users/iagoleal/dev/harness/.harness/decisoes/); índice [`.harness/microdecisoes.md`](file:///Users/iagoleal/dev/harness/.harness/microdecisoes.md). Drivers: `src/main.py` (subcomando `decisions`, hook `Stop`) e `adapters/mcp/server.py` (`process_decisions`).

> ⚠️ **Reescrita vs versão anterior:** a implementação **deixou de ser** o script shell `bin/gerar-index-decisoes.sh` em `harness-config/` (purgado, commit `5624f78`) e passou a ser o `DecisionService` Python em `harness-core`. As fichas migraram de `decisoes/` (raiz) para `.harness/decisoes/` e o índice de `microdecisoes.md` (raiz) para `.harness/microdecisoes.md` (feature 005). Os caminhos não são mais chumbados: vêm de `[decisions]` no `harness.toml`.

## Visão Geral

Gerencia o grafo de microdecisões arquiteturais — fichas `MD-NNNN.md` com front-matter YAML e relações tipadas — e DERIVA delas o índice `.harness/microdecisoes.md` com backlinks (verbos inversos). Valida a integridade do grafo antes de compilar. Os caminhos são lidos de configuração, não chumbados (feature 005).

## Responsabilidades

- Carregar as fichas `MD-*.md` de um diretório, parseando front-matter (`id`, `gancho`, `estado`, `relacoes`). 🟢
- Validar a integridade do grafo (fichas individuais + auto-relação + aresta órfã). 🟢
- Compilar o índice consolidado com backlinks derivados por verbos inversos, de forma determinística. 🟢
- Receber todos os caminhos por parâmetro — não chumbar `decisoes/` nem `microdecisoes.md`. 🟢

## Regras de Negócio

- **RN-N11 — Caminhos desacoplados via config:** `dir`, `index_file`, `header_file` vêm de `[decisions]` no `harness.toml`; o `DecisionService` recebe tudo por parâmetro. Default: `.harness/decisoes`, `.harness/microdecisoes.md`, `.harness/decisoes/_cabecalho.md`. (watch item **W001**) 🟢 — 🟡 Ressalva (T1): via MCP a chamada `load_config` quebra por import ausente; o caminho configurável só é exercido pela CLI.
- **RN-N12 — Índice derivado, não editado à mão:** `.harness/microdecisoes.md` é DERIVADO pelo `./harness decisions`; o cabeçalho declara "Não edite à mão". Backlinks ordenados por ID de origem (determinismo). 🟢
- **RN-N13 — Integridade do grafo:** `validate_integrity` agrega erros — validação de cada ficha, **auto-relação** (`target == self.id`) e **aresta órfã** (alvo fora do grafo). Lista vazia = grafo válido. 🟢
- **RN-N14 — Front-matter obrigatório:** cada `MD-*.md` exige front-matter YAML; diretório ausente → lista vazia; front-matter ausente/YAML inválido → `ValueError`. Cada relação é `"<verbo> MD-XXXX"` (dois tokens), verbo num conjunto fechado de seis, alvo `^MD-\d{4}$`. 🟢
- **Integridade de conteúdo da ficha:** H1 `# MD-XXXX` + as 4 seções obrigatórias `D / PORQUÊ / DESCARTADO / ESTADO` (regex case-insensitive). 🟢

## Requisitos Funcionais

| ID | Requisito | Prioridade | Critério de Aceite |
|----|-----------|-----------|-------------------|
| RF-01 | Carregar fichas e parsear relações. | Must | `load_decisions(dir)` retorna lista ordenada de `Decision`; relação malformada → `ValueError`. |
| RF-02 | Validar integridade do grafo. | Must | `validate_integrity` detecta auto-relação, aresta órfã e ficha sem seção obrigatória; grafo válido → lista vazia. |
| RF-03 | Compilar o índice com backlinks. | Must | `compile_index` grava `.harness/microdecisoes.md` com sub-linhas `↳ <saídas> · <entradas>`, deterministicamente. |
| RF-04 | Caminhos por configuração. | Must | `./harness decisions` lê `dir`/`index_file`/`header_file` de `load_config().decisions`; nenhum literal de caminho no serviço. |

## Requisitos Não Funcionais

| Tipo | Requisito inferido | Evidência no código | Confiança |
|------|--------------------|---------------------|-----------|
| Determinismo | Backlinks ordenados por ID de origem; índice reprodutível. | `core/decisions/service.py` (`compile_index`) | 🟢 |
| Robustez | Front-matter inválido falha barulhento (`ValueError`). | `core/decisions/service.py` (`load_decisions`) | 🟢 |
| Atomicidade | Gravação do índice via `write_file_atomic`. | `core/decisions/service.py` + `adapters/fs/local.py` | 🟢 |
| Manutenibilidade | Caminhos desacoplados (config), sem literais. | `core/decisions/service.py`, `core/domain/config.py` | 🟢 |

## Critérios de Aceitação

```gherkin
Dado que MD-0002 declara "refina MD-0001"
Quando executo `./harness decisions`
Então o índice .harness/microdecisoes.md mostra em MD-0001 o backlink "↳ refinado-por MD-0002".

Dado uma ficha cuja relação aponta para um MD inexistente
Quando validate_integrity roda
Então o erro de aresta órfã é incluído na lista de erros (índice não é compilado limpo).

Dado um harness.toml com [decisions].dir customizado
Quando `./harness decisions` roda
Então o serviço lê as fichas do diretório configurado, sem caminho chumbado.

Dado uma ficha MD-*.md sem front-matter YAML
Quando load_decisions roda
Então um ValueError barulhento é levantado.
```

## Prioridade (MoSCoW)

| Requisito | MoSCoW | Justificativa |
|-----------|--------|---------------|
| Compilação do índice com backlinks (RN-N12) | Must | Entrega central; o índice é o artefato consumido. |
| Integridade do grafo (RN-N13) | Must | Sem ela, o índice consolida um grafo inconsistente. |
| Caminhos por config (RN-N11) | Must | Efeito da feature 005; watch item W001. |
| Front-matter obrigatório (RN-N14) | Must | Pré-condição do parse; falha barulhenta. |

## Rastreabilidade de Código

| Arquivo | Função / Classe | Cobertura |
|---------|-----------------|-----------|
| `core/decisions/service.py` | `DecisionService.load_decisions`, `validate_integrity`, `compile_index` | 🟢 |
| `core/domain/models.py` | `Decision`, `Relationship` | 🟢 |
| `core/domain/config.py` | `DecisionsSection`, `load_config` | 🟢 |
| `src/main.py` | Subcomando `decisions` (deriva caminhos de `load_config`) | 🟢 |
| `adapters/mcp/server.py` | Tool `process_decisions` (🟡 T1: `load_config` sem import) | 🟡 |
| `tests/` | Cobertura de teste do serviço de decisões | 🟢 |
