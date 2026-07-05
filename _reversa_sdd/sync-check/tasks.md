# Sync-Check (Sync) — Tarefas de Implementação

> Regenerado pelo Writer em 2026-06-24 (Re-extração)
> Sequência executável para reimplementar a unit a partir do legado, com rastreabilidade ao código original.

> ⚠️ Reescrita: a unit agora é o `SyncService` Python (`harness-core`), exposto **apenas via MCP** (`check_repository_sync`), não o script shell legado `bin/sync-check.sh` (purgado). Sem checagem de trabalho local (ahead/dirty).

## Pré-requisitos

- [ ] `GitPort` / `SubprocessGitAdapter` disponíveis.
- [ ] `FileSystemPort` disponível.
- [ ] `SyncCache` definido em `core/domain/cache.py`.

## Tarefas

- [ ] T-01, Implementar leitura/validação do cache com TTL (RN-01)
  - Origem no legado: `core/sync/service.py`
  - Critério de pronto: dentro do TTL retorna `True` sem rede; parse de `last_checked_time` (ISO, naive→UTC); parse falho → vai à rede.
  - Confiança: 🟢

- [ ] T-02, Consultar HEAD local e commit remoto
  - Origem no legado: `core/sync/service.py`, `adapters/git/subprocess.py`
  - Critério de pronto: `get_head_commit` e `get_remote_commit(origin main)`; compara igualdade.
  - Confiança: 🟢

- [ ] T-03, Atualizar cache atomicamente
  - Origem no legado: `core/sync/service.py`
  - Critério de pronto: grava `SyncCache.model_dump_json()` via `write_file_atomic`.
  - Confiança: 🟢

- [ ] T-04, Resiliência a falhas (RN-02)
  - Origem no legado: `core/sync/service.py`
  - Critério de pronto: qualquer erro de rede/git → retorna `True` (imprime aviso), sem exceção propagada.
  - Confiança: 🟢

- [ ] T-05, Expor a tool MCP `check_repository_sync`
  - Origem no legado: `adapters/mcp/server.py`
  - Critério de pronto: instancia o serviço, usa o cache canônico `layout.py:SYNC_CACHE_REL_PATH` (`.harness/sync-cache.json`) e TTL 24.
  - Confiança: 🟢

## Tarefas de Teste

- [ ] TT-01, Cache TTL: cache recente → retorna `True` sem rede; cache expirado → dispara `ls-remote`.
- [ ] TT-02, Offline: falha de rede → retorna `True` sem exceção.
- [ ] TT-03, Divergência: HEAD ≠ remoto com cache expirado → retorna `False`.

## Ordem Sugerida

1. T-01 (cache) e T-02 (rede) antes de T-03 (gravação) e T-04 (resiliência).
2. T-05 fecha a exposição MCP.

## Lacunas Pendentes (🔴)

- Nenhuma 🔴. Ressalva 🟡: caminho de cache e TTL chumbados na tool MCP (config `[sync]` parcialmente inerte na borda).
