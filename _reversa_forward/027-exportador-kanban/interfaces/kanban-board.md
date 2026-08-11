# Contrato: board do vscode-kanban (`.vscode/vscode-kanban.json`)

> Identificador: `027-exportador-kanban`
> Tipo: arquivo (JSON, UTF-8), lido/escrito por `harness progress` quando `[progress.kanban].enabled = true`
> Consumidor visual: fork do mantenedor em `~/dev/vscode-kanban` (schema lido na fonte em 2026-08-11)

## Estrutura

Objeto com quatro chaves, cada uma um array de cards, nesta ordem de serialização: `todo`, `in-progress`, `testing`, `done`. Card:

```json
{
  "id": "hns:026:T003",
  "title": "T003 — Testes de stages",
  "type": "note",
  "prio": 0,
  "creation_time": "2026-08-11T11:20:00Z",
  "description": { "content": "<uma linha>", "mime": "text/markdown" },
  "details": { "content": "<markdown opcional>", "mime": "text/markdown" },
  "category": "harness"
}
```

## Posse e namespace

| Card | Critério | Quem escreve |
|------|----------|--------------|
| Gerenciado | `category == "harness"` | Só o exportador: recriado do zero a cada exportação a partir da `Medicao` |
| Manual | qualquer outro (`category` ausente ou diferente) | Só o mantenedor: preservado byte a byte, na coluna onde estiver, ordem relativa mantida |

Ids gerenciados, estáveis e derivados dos ids reais:

- `hns:<feature_id>` — card-resumo de feature (título com `NNN-short-name` e contagem `feitas/total`)
- `hns:<feature_id>:<T00N>` — card de ação da feature ativa
- `hns:alerta:<origem>` — card de alerta

## Mapeamento (namespace gerenciado)

| Elemento da `Medicao` | Coluna | `type` | `prio` |
|------------------------|--------|--------|--------|
| Ação `[ ]` da ativa | `todo` | `note` | 0 |
| Ação `[X]` da ativa | `done` | `note` | 0 |
| Resumo da feature ativa | `in-progress` | `note` | 1 |
| Resumo de feature pausada | `todo` | `note` | 1 |
| Alerta alta | `todo` | `bug` | 9 |
| Alerta média | `todo` | `bug` | 5 |

A coluna `testing` nunca recebe card gerenciado. `creation_time` é determinístico (primeiro `ts` da ação no `progress.jsonl`; fallback e resumos usam `started-at` do `active-requirements.json`); nenhum caminho usa a hora corrente.

As-built (2026-08-11): features CONCLUÍDAS não geram card — a `Medicao` carrega delas apenas a contagem, e cards de concluídas cresceriam sem limite num board que projeta trabalho em curso. O campo `details` não é emitido (opcional no fork); a descrição de uma linha vai em `description`.

## Leitura (medição)

O exportador lê o board existente APENAS para os cards manuais: (a) preservá-los no merge; (b) listar os que estão em coluna não-`done` como `Medicao.demandas` (fila de entrada de demandas para o agente conduzir pelo processo forward). Cards gerenciados do arquivo são descartados e recomputados; jamais servem de fonte de progresso.

## Escrita e falhas

- Atômica, apenas quando o conteúdo muda; JSON com `ensure_ascii=False`, indentação de 2, chave de coluna na ordem fixa acima; `.vscode/` criado se ausente.
- Board ausente: primeira exportação normal (sem demandas, sem manuais).
- Board presente mas JSON inválido: falha REAL — `Erro de leitura:` em stderr, exit 2, NENHUM artefato regravado (nem markdown nem board).
- `enabled = false` (default): o arquivo nunca é lido nem escrito.
- O exportador jamais toca outro arquivo sob `.vscode/` (em particular, nunca cria `vscode-kanban.js`).

## Garantias

1. Determinismo: mesmo estado medido + mesmos cards manuais → bytes idênticos.
2. Card manual sobrevive a N exportações, em qualquer coluna, byte a byte.
3. Editar card gerenciado não altera fonte alguma e a edição é sobrescrita na exportação seguinte.
4. Mover card manual para `done` o retira das demandas sem removê-lo do board.
