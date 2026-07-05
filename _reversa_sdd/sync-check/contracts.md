# Sync-Check (Sync) — Contratos e Payloads (Contracts)

> Regenerado pelo Writer em 2026-06-24 (Re-extração)
> Interface de dados da unit no estado ATUAL (core Python, exposto via MCP). Escala: 🟢 / 🟡 / 🔴

> ⚠️ **Reescrita vs versão anterior:** no estado atual a sincronia é exposta como **tool MCP** (`check_repository_sync`), não como hook `SessionStart` que emite `additionalContext`. O serviço retorna um booleano; não produz mais o payload JSON de alerta de sincronização do legado.

---

## 🔌 1. Tool MCP `check_repository_sync` 🟢

| Aspecto    | Valor                                                                               |
| ---------- | ----------------------------------------------------------------------------------- |
| Transporte | Model Context Protocol (JSON-RPC sobre stdin/stdout), servidor FastMCP "Harness".   |
| Entrada    | `repo_path` (caminho do repositório a verificar).                                   |
| Cache      | `.harness/sync-cache.json` (fonte única `layout.py:SYNC_CACHE_REL_PATH`, MD-0013).  |
| TTL        | 24 horas (chumbado na tool).                                                        |
| Saída      | `bool` — `True` = em sincronia (ou degradação por TTL/falha); `False` = divergente. |

---

## 💾 2. Estrutura do cache (`SyncCache`) 🟢

JSON persistido em `cache_filepath`:

```json
{
  "last_checked_time": "2026-06-24T00:02:09+00:00",
  "commit_hash": "c548223........................................"
}
```

| Campo               | Tipo           | Validação                   |
| ------------------- | -------------- | --------------------------- |
| `last_checked_time` | datetime (ISO) | naive → coerção UTC         |
| `commit_hash`       | str            | regex SHA1 `^[a-f0-9]{40}$` |

---

## 🔁 3. Contrato com o `GitPort` 🟢

| Método                         | Comando subjacente          |
| ------------------------------ | --------------------------- |
| `get_head_commit(repo_path)`   | `git rev-parse HEAD`        |
| `get_remote_commit(repo_path)` | `git ls-remote origin main` |

`CalledProcessError` no adaptador → `RuntimeError` com stderr; o `SyncService` captura e degrada para `True` (RN-02).
