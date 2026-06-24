# Microdecisões (Decisions) — Tarefas de Implementação

> Regenerado pelo Writer em 2026-06-24 (Re-extração após a feature 005)
> Sequência executável para reimplementar a unit a partir do legado, com rastreabilidade ao código original.

> ⚠️ Reescrita: a unit agora é o `DecisionService` Python (`harness-core`), não o script shell legado `bin/gerar-index-decisoes.sh` (purgado). Fichas em `.harness/decisoes/`, índice em `.harness/microdecisoes.md`, caminhos lidos de `[decisions]` no `harness.toml`.

## Pré-requisitos

- [ ] `Decision` e `Relationship` definidos em `core/domain/models.py`.
- [ ] `DecisionsSection` em `core/domain/config.py` e `load_config` funcional.
- [ ] `FileSystemPort` disponível (leitura das fichas + gravação atômica).
- [ ] `PyYAML` disponível.

## Tarefas

- [ ] T-01, Implementar `load_decisions(directory)`
  - Origem no legado: `core/decisions/service.py`
  - Critério de pronto: lista ordenada de `MD-*.md`; parse de front-matter (`id`, `gancho`, `estado`, `relacoes`); diretório ausente → `[]`; front-matter/YAML inválido → `ValueError`.
  - Confiança: 🟢

- [ ] T-02, Implementar `validate_integrity(decisions)`
  - Origem no legado: `core/decisions/service.py`, `core/domain/models.py` (`Decision.validate_integrity`)
  - Critério de pronto: agrega validação por ficha (H1 + 4 seções `D/PORQUÊ/DESCARTADO/ESTADO`), auto-relação e aresta órfã; grafo válido → `[]`.
  - Confiança: 🟢

- [ ] T-03, Implementar `compile_index(decisions, output, header)`
  - Origem no legado: `core/decisions/service.py`
  - Critério de pronto: deriva backlinks por verbos inversos, ordena por ID de origem, monta `↳ <saídas> · <entradas>`, concatena cabeçalho e grava atomicamente.
  - Confiança: 🟢

- [ ] T-04, Validar `Relationship` (verbos e alvo)
  - Origem no legado: `core/domain/models.py`
  - Critério de pronto: `rel_type` ∈ conjunto de seis verbos (lower); `target_id` regex `^MD-\d{4}$`.
  - Confiança: 🟢

- [ ] T-05, Derivar caminhos de `[decisions]` no driver
  - Origem no legado: `src/main.py` (subcomando `decisions`)
  - Critério de pronto: `decisoes_dir`/`output_file`/`header_file` vêm de `load_config().decisions`; nenhum literal de caminho no serviço (W001).
  - Confiança: 🟢

## Tarefas de Teste

- [ ] TT-01, Inversão de relações: duas fichas com `refina`/`depende-de` produzem os backlinks reversos esperados no índice.
- [ ] TT-02, Caso de erro: relação malformada → `ValueError`; aresta órfã → erro em `validate_integrity`.
- [ ] TT-03, Config: alterar `[decisions].dir` muda o diretório lido (sem literal chumbado).
  - Cobertura existente: `tests/` (serviço de decisões).

## Ordem Sugerida

1. T-04 (validação de relação) e T-01 (carga) primeiro.
2. T-02 (integridade) antes de T-03 (compilação), que consome o grafo validado.
3. T-05 (config) fecha a integração com o driver.

## Lacunas Pendentes (🔴)

- Nenhuma 🔴. **T1** — via MCP, `load_config` quebrava por import ausente e a tool de decisões MCP não processava — **resolvido** no commit `cf73980` (import presente em `server.py:12`).
