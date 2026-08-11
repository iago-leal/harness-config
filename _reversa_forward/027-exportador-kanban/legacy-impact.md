# Legacy Impact: exportador kanban derivado da Medicao

> Identificador: `027-exportador-kanban`
> Data: `2026-08-11`
> Âncora da extração: `_reversa_sdd/architecture.md`, `_reversa_sdd/domain.md`

## Arquivos afetados

| Arquivo afetado | Componente (`_reversa_sdd/architecture.md`) | Tipo | Severidade | Justificativa |
|-----------------|---------------------------------------------|------|------------|---------------|
| `.harness/harness-core/src/core/progress/kanban.py` | Componente novo — exportador kanban (módulo único de schema do fork) | componente-novo | MEDIUM | `extrair_manuais` (posse por `category == "harness"`) e `render_board` (projeção determinística da `Medicao` + merge preservando manuais); único arquivo do core que conhece o formato do board |
| `.harness/harness-core/src/core/progress/service.py` | Serviço de medição (026) | regra-nova | MEDIUM | Modelos `AcaoProgresso` e `Demanda`; `FeatureProgresso.{iniciada_em,acoes}`; `Medicao.{board_habilitado,demandas}`; quinta fonte `_medir_demandas` (board lido SÓ pelos manuais, opt-in) e `_criacao_por_acao` (1º ts do `progress.jsonl`) |
| `.harness/harness-core/src/core/progress/stages.py` | Paridade com o skill `reversa-requirements` (026) | regra-nova | LOW | `listar_acoes`: extrai fase, ID real (`T00N`), descrição e status por linha de ação, com o MESMO critério de linha de `contar_checkboxes` |
| `.harness/harness-core/src/core/progress/render.py` | Renderizadores (026) | regra-nova | LOW | Seção `## Demandas do board` no markdown, presente apenas com o kanban habilitado (`- nenhuma` quando vazio); JSON herda `demandas` pelo `model_dump` |
| `.harness/harness-core/src/main.py` (ramo `progress`, modo padrão) | Borda CLI (`main.py`) | regra-nova | MEDIUM | Segundo artefato derivado: board gravado atômico e write-only-when-changed, com linha própria no stdout; só no modo padrão e por opt-in; board ilegível já saiu com 2 antes de qualquer escrita |
| `.harness/harness-core/src/core/domain/config.py` | Domínio — configuração canônica | regra-nova | LOW | `ProgressKanbanSection(enabled=False, file=".vscode/vscode-kanban.json")` aninhada em `ProgressSection.kanban`; herança sem migração; `version` 2.4.0 → 2.5.0 |
| `.harness/harness-core/tests/test_progress_kanban.py`, `tests/test_progress_service.py` (append), `tests/test_cli.py` (append) | Suíte de testes | componente-novo | LOW | 20 testes novos (9 kanban, 7 serviço/render, 4 CLI em subprocesso real); suíte total 372 |
| `harness.toml` (raiz deste repo) | Configuração do projeto (não core) | delta-de-dados | LOW | Arquivo criado no smoke com apenas `[progress.kanban] enabled = true`; todo o resto herda defaults |
| `.vscode/vscode-kanban.json` | Artefato derivado novo (nível projeto, não core) | delta-de-dados | LOW | Board versionado: namespace `harness` recomputado a cada `harness progress`; ilha manual preservada como canal de demandas |
| `.harness/decisoes/MD-0020.md` | Governança — microdecisões | componente-novo | LOW | Ficha da decisão; relação `refina MD-0019` |

## Diff conceitual por componente

**Exportador (`core/progress/kanban.py`).** Componente novo e aditivo: projeta a mesma `Medicao` da 026 no schema do fork do vscode-kanban (colunas `todo`/`in-progress`/`testing`/`done`). Posse por namespace: card `category == "harness"` é do exportador e recomputado do zero (ids `hns:<feature>`, `hns:<feature>:<T00N>`, `hns:alerta:<origem>`); qualquer outro é manual e preservado intacto na coluna onde estiver. `testing` nunca recebe card gerenciado. Determinismo integral: `creation_time` vem de `criada_em`/`iniciada_em` da própria `Medicao`; nenhum caminho consulta a hora corrente.

**Serviço de medição.** Ganhou granularidade (as ações individuais com ID real, exigência dos cards) e uma quinta fonte condicionada à config: o board, lido SOMENTE pelos cards manuais — os em coluna não-`done` viram `Medicao.demandas` (fila de entrada de demandas do mantenedor). Cards gerenciados do arquivo jamais são fonte: o fluxo é unidirecional (`actions.md` → board), e edição manual em card gerenciado é descartada na exportação seguinte. Board presente mas ilegível é falha real (herda o contrato de exit 2 sem regravar nada da 026).

**Borda CLI.** O modo padrão passa a manter dois artefatos derivados quando o opt-in existe; `--json` e `--em-hook` não tocam o board. Segurança: o exportador escreve apenas o `.json` configurado e nunca cria ou toca `.vscode/vscode-kanban.js` (o fork executa esse arquivo, `workspaces.ts:769`).

## Preservadas (regras 🟢 do `_reversa_sdd/domain.md` intactas)

- Contrato do medidor 026 por inteiro (W001–W007 do regression-watch da 026): markdown sem valor volátil, write-only-when-changed, `--em-hook` falhando só por defasagem, exit 2 sem regravar, serviço em leitura pura (a quinta fonte também só lê), paridade `stages.py` ↔ skill (o `listar_acoes` reusa o MESMO regex de linha), alerta persistente sem ack.
- RN-N44 (pós-025) — nenhuma política nova de bloqueio: o board não participa de hook algum.
- RN-N36..N40 — fonte única: o exportador chega à base migrada pelo shim; bump 2.5.0 no fluxo padrão.
- RN-N12 — índice de decisões derivado: inalterado.

## Modificadas

- Nenhuma regra 🟢 do `_reversa_sdd/domain.md` foi alterada ou removida: a feature é aditiva. Persiste a defasagem de COBERTURA estrutural (o `_reversa_sdd/` ainda não descreve `core/progress/`, agora com o exportador; ver pendência no `regression-watch.md`).
