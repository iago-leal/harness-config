# Data-delta: Artefatos de decisão dentro de `.harness/`

> Feature `005-decisoes-em-harness` · 2026-06-23
> Base: modelo extraído em `_reversa_sdd/code-analysis.md#2.4` e `_reversa_sdd/state-machines.md#2`

## 1. Natureza da mudança

**Relocação física, não evolução de esquema.** O "modelo de dados" das microdecisões são os próprios arquivos Markdown com front-matter YAML. Nenhum campo nasce, muda ou morre.

## 2. Diff conceitual

| Antes (raiz) | Depois (`.harness/`) |
|--------------|----------------------|
| `decisoes/MD-NNNN.md` | `.harness/decisoes/MD-NNNN.md` |
| `decisoes/_cabecalho.md` | `.harness/decisoes/_cabecalho.md` |
| `microdecisoes.md` (índice derivado) | `.harness/microdecisoes.md` |

- **Campos novos:** nenhum.
- **Campos removidos:** nenhum.
- **Front-matter (`id`, `gancho`, `relacoes`, `estado`):** inalterado.
- **Índice derivado (backlinks, títulos H1, sub-linha `↳`):** regenerado idêntico pelo `compile_index` — mesma entrada, mesma saída, só o caminho de gravação muda.

## 3. Migração necessária

1. `git mv decisoes .harness/decisoes` (move as 4 fichas atuais MD-0001..0004 + `_cabecalho.md`, preservando histórico).
2. `git mv microdecisoes.md .harness/microdecisoes.md`.
3. `./harness decisions` regenera `.harness/microdecisoes.md` a partir de `.harness/decisoes/` — deve produzir conteúdo semanticamente idêntico ao índice anterior.

Sem migração de banco, sem script de transformação de dados, sem reescrita de conteúdo das fichas.

## 4. Verificação de não-regressão dos dados

- `git log --follow .harness/decisoes/MD-0001.md` mostra o histórico anterior ao move.
- `diff` semântico do índice: os mesmos IDs, títulos e backlinks de antes (MD-0001..0004), só com o arquivo gravado em `.harness/microdecisoes.md`.
- Validação de integridade (`validate_integrity`): zero erros (grafo inalterado).
