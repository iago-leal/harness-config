# Actions: Exportador kanban derivado da Medicao

> Identificador: `027-exportador-kanban`
> Data: `2026-08-11`
> Roadmap: `_reversa_forward/027-exportador-kanban/roadmap.md`

## Resumo

| Métrica | Valor |
|---------|-------|
| Total de ações | 14 |
| Paralelizáveis (`[//]`) | 5 |
| Maior cadeia de dependência | 8 |

## Fase 1, Preparação

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T001 | Config: `ProgressKanbanSection(enabled=False, file=".vscode/vscode-kanban.json")` aninhada em `ProgressSection.kanban` (D-03; herança sem migração) | - | `[//]` | `.harness/harness-core/src/core/domain/config.py` | 🟢 | `[X]` |
| T002 | Scaffold: modelo `Demanda` + campo `Medicao.demandas` em `service.py`; stub `kanban.py` com assinaturas `extrair_manuais(board_json)` e `render_board(medicao, board_atual)` levantando NotImplementedError | - | `[//]` | `.harness/harness-core/src/core/progress/kanban.py` | 🟢 | `[X]` |

## Fase 2, Testes

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T003 | Testes (red) de `kanban.py`: determinismo byte a byte, namespace `category=="harness"`, ids `hns:*`, mapeamento de colunas (D-05), `creation_time` derivado sem `now()` (D-06), merge preservando manuais byte a byte em qualquer coluna, `testing` sem card gerenciado | T002 | `[//]` | `.harness/harness-core/tests/test_progress_kanban.py` | 🟢 | `[X]` |
| T004 | Testes (red) do serviço/render: `demandas` extraídas de manuais não-`done` quando `enabled`; board não lido quando `enabled=False`; board ilegível → falha real; `## Demandas do board` no markdown (`- nenhuma` vazio); `demandas` no JSON | T002 | `[//]` | `.harness/harness-core/tests/test_progress_service.py` | 🟢 | `[X]` |
| T005 | Testes (red) da CLI em subprocesso: com `[progress.kanban].enabled=true` grava board e markdown; idempotência dupla; card manual sobrevive; board corrompido → exit 2 sem regravar nada; default desligado não cria board | T002 | `[//]` | `.harness/harness-core/tests/test_cli.py` | 🟢 | `[X]` |

## Fase 3, Núcleo

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T006 | Implementar `kanban.py`: parser de manuais (posse por categoria) e `render_board` (mapeamento D-05, ids D-02, `creation_time` D-06, serialização estável) | T003 | - | `.harness/harness-core/src/core/progress/kanban.py` | 🟢 | `[X]` |
| T007 | Serviço: quinta fonte condicionada à config (ler board só para manuais; `demandas` de colunas não-`done`; ilegível → `falhas`) (D-04) | T004, T006 | - | `.harness/harness-core/src/core/progress/service.py` | 🟢 | `[X]` |
| T008 | Render: seção `## Demandas do board` no markdown e exposição no JSON (D-08) | T004 | - | `.harness/harness-core/src/core/progress/render.py` | 🟢 | `[X]` |

## Fase 4, Integração

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T009 | Borda: no modo padrão do `progress`, com kanban habilitado, gravar o board (atômico, write-only-when-changed, `makedirs`, linha própria no stdout); falha real cobre board ilegível antes de qualquer escrita (D-07, D-09) | T005, T006, T007, T008 | - | `.harness/harness-core/src/main.py` | 🟢 | `[X]` |
| T010 | Suíte completa verde + ruff nos arquivos tocados | T009 | - | `.harness/harness-core/` | 🟢 | `[X]` |
| T011 | Smoke real neste repo: opt-in no `harness.toml`, exportar, conferir no fork (RF-06), card manual → demanda, re-exportação preservando, corromper e conferir exit 2 | T010 | - | `.vscode/vscode-kanban.json` | 🟡 | `[X]` |

## Fase 5, Polimento

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T012 | Bump `version` 2.4.0 → 2.5.0 (D-10) | T010 | - | `.harness/harness-core/src/core/domain/config.py` | 🟢 | `[X]` |
| T013 | Ficha MD-0020 + recompilação do índice de decisões | T011, T012 | - | `.harness/decisoes/MD-0020.md` | 🟢 | `[X]` |
| T014 | Reconciliação as-built de `interfaces/kanban-board.md` e `onboarding.md` se o smoke divergir; regenerar `progresso.md` e board finais | T013 | - | `_reversa_forward/027-exportador-kanban/` | 🟢 | `[X]` |

## Notas de execução

- **T002 (as-built):** o scaffold revelou que a `Medicao` só carregava agregados por fase; ids ordinais de card seriam instáveis a reordenação da tabela. Solução: `AcaoProgresso` com o ID real (`T00N`) extraído por `stages.listar_acoes` (mesmo critério de linha da contagem), e `criada_em`/`iniciada_em` medidos no serviço — o `render_board` ficou sem parâmetros de criação. Registrado no `data-delta.md`.
- **T011 (achado):** smoke em arquivo integral (exportação, idempotência byte a byte, card manual → demanda no markdown e no `--json`, board corrompido → exit 2 sem regravar nada). A conferência VISUAL no fork (ids `hns:*`, campos opcionais ausentes, mover card gerenciado) ficou pendente do mantenedor abrir o board no VS Code — registrada como observação no `regression-watch.md`.
- **T014 (reconciliação):** features concluídas NÃO geram card (a `Medicao` só carrega a contagem); linha removida do contrato `interfaces/kanban-board.md` com nota as-built. `onboarding.md` conferido sem divergência.
