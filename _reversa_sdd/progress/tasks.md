# Progress (Medidor de Entregáveis + Exportador Kanban) — Tarefas de Implementação

> Gerado pelo Writer em 2026-08-11 (Reconciliação das features 026-027)
> Sequência executável para reimplementar a unit a partir do legado, com rastreabilidade ao código original.

## Pré-requisitos

- [ ] `FileSystemPort` e `GitPort` disponíveis (adapters reais e fakes de teste).
- [ ] `pydantic` disponível (modelos transitórios).
- [ ] `core/decisions/gate.evaluate_registration_gate` implementado (unit `microdecisoes`).
- [ ] `ProgressSection`/`ProgressKanbanSection` em `core/domain/config.py`.

## Tarefas

- [ ] T-01, Implementar `stages.py` (estágio físico + checkboxes)
  - Origem no legado: `core/progress/stages.py`
  - Critério de pronto: `detectar_estagio` reproduz a tabela do skill `reversa-requirements`; `contar_checkboxes`/`listar_acoes`/`contar_por_fase` compartilham o mesmo critério de linha (`_CHECKBOX_ROW`).
  - Confiança: 🟢

- [ ] T-02, Implementar os modelos transitórios
  - Origem no legado: `core/progress/service.py` (classes Pydantic)
  - Critério de pronto: `Medicao`, `FeatureProgresso`, `FasesProgresso`, `AcaoProgresso`, `Demanda`, `Alerta`, `HarnessMedicao`; jamais serializados em disco.
  - Confiança: 🟢

- [ ] T-03, Implementar `ProgressService.measure` (cinco fontes, leitura pura)
  - Origem no legado: `core/progress/service.py`
  - Critério de pronto: `_medir_forward` (estágio físico, divergência → alerta alta, `_MARCA_RECONCILIACAO` → alerta média), `_medir_harness` (sessão, fichas, gate em leitura pura sem persistir fingerprint), `_medir_demandas` (opt-in, só manuais fora de `done`); alertas ordenados; **nenhuma escrita** (tripwire `fs.writes == []`).
  - Confiança: 🟢

- [ ] T-04, Implementar `render.py` (markdown + JSON)
  - Origem no legado: `core/progress/render.py`
  - Critério de pronto: `render_markdown` sem timestamp/caminho absoluto; `render_json` com `aferido_em`.
  - Confiança: 🟢

- [ ] T-05, Integrar o subcomando `progress` na CLI
  - Origem no legado: `src/main.py` (13º subcomando; ramos padrão/`--json`/`--em-hook` mutuamente exclusivos)
  - Critério de pronto: modo padrão regrava `config.progress.file` atomicamente e só quando mudou; fonte ilegível → `Erro de leitura:` stderr exit 2 sem regravar; `--em-hook` exit 1 só por artefato defasado (alerta grave = aviso stderr, exit 0 — sem exit 3, D-03).
  - Confiança: 🟢

- [ ] T-06, Implementar `kanban.py` (exportador, 027)
  - Origem no legado: `core/progress/kanban.py`
  - Critério de pronto: `extrair_manuais` (JSON inválido levanta; borda → exit 2 sem escrita); `render_board` recomputa só `category == "harness"` com ids `hns:*`, preserva manuais byte a byte, mapeamento fixo de colunas, `testing` nunca gerenciada, concluídas sem card; `creation_time` do primeiro `ts` do `progress.jsonl` (fallback `started-at`, nunca `now()`).
  - Confiança: 🟢

- [ ] T-07, Fiar o board na borda (opt-in)
  - Origem no legado: `src/main.py` (modo padrão) + `core/domain/config.py` (`ProgressKanbanSection`)
  - Critério de pronto: board lido/escrito só com `enabled = true` e só no modo padrão; write-only-when-changed; **jamais** cria ou toca `.vscode/vscode-kanban.js`.
  - Confiança: 🟢

## Tarefas de Teste

- [ ] TT-01, Tripwire de pureza: `measure()` com `RecordingFileSystem` termina com `fs.writes == []`.
- [ ] TT-02, Write-only-when-changed: segunda execução sem mudança de estado não regrava o artefato.
- [ ] TT-03, Contrato de exit codes: fonte ilegível → 2 sem regravar; `--em-hook` defasado → 1; alerta grave → 0 com aviso stderr.
- [ ] TT-04, Alerta por sinal físico: marca "pendência de reconciliação" gera alerta média; some quando a marca some.
- [ ] TT-05, Idempotência do board: duas exportações do mesmo estado → bytes idênticos.
- [ ] TT-06, Posse por namespace: manuais preservados byte a byte; manuais fora de `done` viram `demandas`; board corrompido → exit 2 sem escrita.
  - Cobertura existente: TDD das features 026/027 (20 testes novos na 027; suíte 372 verde).

## Ordem Sugerida

1. T-01 (stages) e T-02 (modelos) primeiro — base da medição.
2. T-03 (measure) com TT-01 desde o início (a pureza é a invariante central).
3. T-04/T-05 (render + CLI) fecham a feature 026.
4. T-06/T-07 (kanban + opt-in) fecham a 027, com TT-05/TT-06.

## Lacunas Pendentes (🔴)

- Nenhuma 🔴. Pendências 🟡 registradas no `design.md` (paridade por convenção, conferência visual do board no fork, medidor sem gatilho de hook, condução manual das demandas).
