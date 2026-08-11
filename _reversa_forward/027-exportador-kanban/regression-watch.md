# Regression Watch: exportador kanban derivado da Medicao

> Identificador: `027-exportador-kanban`
> Data: `2026-08-11`
> Fonte: `legacy-impact.md` desta feature; ficha `.harness/decisoes/MD-0020.md`

## Watch items

| ID | Origem (arquivo, seção) | Regra esperada após mudança | Tipo de verificação | Sinal de violação |
|----|--------------------------|------------------------------|---------------------|-------------------|
| W001 | `core/progress/kanban.py` (027/RN-01) | Card manual (qualquer `category != "harness"`, inclusive ausente) sobrevive intacto a N exportações, na coluna onde estiver, ordem relativa mantida; só o mantenedor o remove | presença | Card manual sumindo, mudando de coluna ou de conteúdo após `harness progress` |
| W002 | `core/progress/kanban.py` (027/RN-03, D-06) | Board 100% determinístico: ids `hns:*` derivados dos ids reais; `creation_time` do 1º ts da ação no `progress.jsonl` com fallback no `started-at`; NENHUM caminho consulta a hora corrente; mesmo estado + mesmos manuais → bytes idênticos | ausência | `now()`/`datetime.now`/`time.time` em `kanban.py` ou nos campos do board; diff do board em commit que não mudou o estado medido |
| W003 | `core/progress/service.py`, `_medir_demandas` (027/RN-05) | O board é lido SÓ pelos cards manuais e SÓ com `[progress.kanban] enabled = true`; manuais fora de `done` viram `demandas`; cards gerenciados do arquivo jamais são fonte de progresso (fluxo unidirecional: `actions.md` → board) | ausência | Estado de card gerenciado influenciando qualquer medida; board lido com o opt-in desligado; arrastar card gerenciado alterando `actions.md` |
| W004 | `src/main.py`, ramo `progress` (027/RN-07) | Board presente mas ilegível é falha REAL: `Erro de leitura:` em stderr, exit 2, NENHUM artefato regravado (nem markdown nem board); board ausente com opt-in é primeira exportação normal | presença | Board corrompido sendo sobrescrito; exit 0 com board ilegível; markdown regravado num run com falha de board |
| W005 | `src/main.py`, ramo `progress` (027/D-07) | O board é escrito apenas no modo padrão, atômico, write-only-when-changed, com linha própria no stdout; `--json` e `--em-hook` nunca tocam o board; sem opt-in, nada sob `.vscode/` é criado | ausência | Board gravado por `--json`/`--em-hook`; `.vscode/` surgindo em projeto sem opt-in; regravação incondicional |
| W006 | `core/progress/kanban.py` (027/D-11, segurança) | O exportador escreve unicamente o arquivo configurado em `[progress.kanban].file` e jamais cria ou toca `.vscode/vscode-kanban.js` (o fork EXECUTA esse arquivo: `workspaces.ts:769`) | ausência | Qualquer escrita fora do `.json` configurado; um `vscode-kanban.js` surgindo em repositório com o exportador ativo |
| W007 | `core/progress/kanban.py` × `core/progress/stages.py` (027/D-05) | Mapeamento estável: ação `[ ]` → `todo`, `[X]` → `done`, resumo da ativa → `in-progress`, pausadas → `todo`, alertas → `todo` como `bug` (prio 9 alta / 5 média); `testing` nunca recebe card gerenciado; `listar_acoes` usa o MESMO critério de linha de `contar_checkboxes` | redação | Card gerenciado em `testing`; contagem e listagem de ações divergindo para o mesmo `actions.md`; segunda implementação do schema do board fora de `kanban.py` |

## Reconciliação do `_reversa_sdd/` — ✅ resolvida em 2026-08-11

- `architecture.md` / `domain.md` §2.25: descrevem o componente `core/progress/` completo (com `kanban.py` e a quinta fonte) e os artefatos derivados `.harness/progresso.md` e `.vscode/vscode-kanban.json` (este também no `erd-complete.md`, como único delta-de-contrato-externo do ciclo, e no `code-spec-matrix.md` §5).
- Executada na re-extração dirigida de 2026-08-11, na mesma rodada das features 024/025/026.

## Observações (sem peso de regressão)

- 🟡 Conferência visual no fork pendente do mantenedor: renderização de ids não numéricos (`hns:026:T003`), tolerância a campos opcionais ausentes (`references`, `assignedTo`, `details`) e efeito de mover card gerenciado na UI (a exportação seguinte o devolve ao lugar derivado). O smoke em arquivo passou integralmente; falta o olho no VS Code.
- Features CONCLUÍDAS não geram card (as-built): a `Medicao` só carrega a contagem, e cards de concluídas cresceriam sem limite. Reconciliado no contrato `interfaces/kanban-board.md`.
- O board como canal de demandas é convenção operacional: o agente harness deve tratar `Medicao.demandas` como fila de entrada e conduzir cada demanda pelo processo forward; nada disso é automatizado nesta feature.

## Histórico de re-extrações

### Re-extração 2026-08-11 11:26

> Primeira verificação da 027, na re-extração dirigida de reconciliação das features 024-027. Vereditos por leitura direta de `core/progress/kanban.py`, `service.py` (`_medir_demandas`, `_criacao_por_acao`) e do ramo `progress` de `main.py`, cruzada com os artefatos recém-gerados (unit `progress/`, `domain.md` §2.25, `erd-complete.md` — contrato do board como único delta-de-contrato-externo —, `spec-impact-matrix.md`). Suíte 372 verde (20 testes novos da 027). A seção de reconciliação abaixo foi **resolvida nesta rodada**. Pendência operacional que segue aberta: a conferência visual do board no fork (Observações; `gaps.md#G-16`).

| ID | Veredito | Observação |
|----|----------|------------|
| W001 | 🟢 verde | Manuais (`category != "harness"`, inclusive ausente) preservados byte a byte, na coluna e ordem onde estiverem; teste de sobrevivência a N exportações na suíte. RN-N53. |
| W002 | 🟢 verde | Nenhum `now()`/`datetime.now`/`time.time` em `kanban.py` (grep vazio); `creation_time` do 1º `ts` do `progress.jsonl` com fallback `started-at`; idempotência pinada por teste. RN-N54. |
| W003 | 🟢 verde | Board lido só pelos manuais e só com `enabled = true`; manuais fora de `done` viram `Medicao.demandas`; fluxo unidirecional (`actions.md` → board). RN-N55. |
| W004 | 🟢 verde | Board ilegível → `extrair_manuais` levanta → borda converte em `Erro de leitura:` stderr, exit 2, nenhum artefato regravado. |
| W005 | 🟢 verde | Board escrito apenas no modo padrão, atômico, write-only-when-changed; `--json`/`--em-hook` não tocam o board; sem opt-in, nada sob `.vscode/` é criado. |
| W006 | 🟢 verde | Escrita restrita ao arquivo configurado em `[progress.kanban].file`; `vscode-kanban.js` jamais criado ou tocado (invariante de segurança pinada; `workspaces.ts:769`). |
| W007 | 🟢 verde | Mapeamento fixo de colunas confirmado (`[ ]`→todo, `[X]`→done, ativa→in-progress, pausadas→todo, alertas→todo bug 9/5); `testing` nunca gerenciada; `listar_acoes` compartilha o critério de linha de `contar_checkboxes` via `_CHECKBOX_ROW`. |

## Arquivadas

_(vazio)_
