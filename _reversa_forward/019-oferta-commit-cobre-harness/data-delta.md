# Data-delta: oferta de commit pendente cobre o vão de `.harness/`

> Identificador: `019-oferta-commit-cobre-harness`
> Data: `2026-06-30`

## 1. Modelo de dados persistido

**n/a.** O Harness Core não tem banco de dados nem schema persistido relevante a esta feature. Não há tabelas, colunas, índices nem migrações.

## 2. Estruturas afetadas (em memória / arquivos de config)

### 2.1 Conjunto de caminhos pendentes (em memória)

`pending_work_paths(git, repo_path, session_file) -> list[str]`

| Antes (016)                                                   | Depois (019)                                 |
| ------------------------------------------------------------- | -------------------------------------------- |
| `dirty \ { p : p == ".harness" ou p começa com ".harness/" }` | `dirty \ { session_file }`                   |
| Exclui o diretório do harness inteiro                         | Exclui apenas `.harness/estado-da-sessao.md` |

Efeito no conteúdo do conjunto, dado `dirty = [src/foo.py, .harness/estado-da-sessao.md, .harness/decisoes/MD-0007.md, .harness/microdecisoes.md, .harness/sync-cache.json]`:

- **Antes:** `[src/foo.py]`
- **Depois (porcelain):** `[src/foo.py, .harness/decisoes/MD-0007.md, .harness/microdecisoes.md]` — `sync-cache.json` ausente porque o `.gitignore` o omite de `git status --porcelain` (após a salvaguarda D-02); `estado-da-sessao.md` ausente por exclusão explícita.

### 2.2 `.gitignore` do projeto-alvo

Entrada nova garantida (idempotente) por `_ensure_gitignore_entry`, além da já existente `.harness/harness-core/`:

```
.harness/sync-cache.json
```

- Aplicada em `initialize_project` (in-process) e em `upgrade_project` (subprocesso com código novo, RN-N30).
- Não remove nem reordena entradas pré-existentes; só acrescenta se ausente.

## 3. Migração

Nenhuma migração de dados. A propagação ocorre por `./harness upgrade`, que re-materializa o `.gitignore` antes de o novo filtro passar a valer no consumidor.
