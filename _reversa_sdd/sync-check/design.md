# Sync-Check (Sync) — Design Técnico

> Regenerado pelo Writer em 2026-06-24 (Re-extração)
> Foca no COMO a unit é construída, a partir do código legado lido. Escala: 🟢 / 🟡 / 🔴

## Interface

| Símbolo                  | Assinatura                                                 | Retorno | Observação                                                                 |
| ------------------------ | ---------------------------------------------------------- | ------- | -------------------------------------------------------------------------- |
| `SyncService.check_sync` | `(repo_path: str)`                                         | `bool`  | `True` = em sincronia (ou degradação por falha/TTL); `False` = divergente. |
| `SyncCache`              | `(last_checked_time: datetime, commit_hash: constr(SHA1))` | —       | Modelo Pydantic do cache JSON.                                             |

## Fluxo Principal

1. **Cache (RN-01):** se `cache_filepath` existe, lê JSON, parseia `last_checked_time` (ISO, naive→UTC). Dentro do TTL (`cache_ttl_hours`, default 24): retorna `True` — se o `commit_hash` do cache bate com o HEAD, por consistência, mas **mesmo divergindo retorna `True`** dentro do TTL. Falha no parse → cai para checagem de rede. 🟢
2. **Rede:** `git rev-parse HEAD` (local) e `git ls-remote origin main` (remoto), via `GitPort`. 🟢
3. **Atualiza cache** atomicamente via `SyncCache(...).model_dump_json()` + `write_file_atomic`. 🟢
4. Retorna `local_commit == remote_commit`. 🟢

## Fluxos Alternativos

- **Cache válido (dentro do TTL):** retorna `True` sem rede. 🟢
- **Parse de cache falho:** ignora cache, vai à rede. 🟢
- **Erro de rede/git (RN-02):** captura, imprime aviso e retorna `True`. 🟢

## Dependências

- `GitPort` / `SubprocessGitAdapter` — HEAD local e commit remoto.
- `FileSystemPort` — leitura/gravação atômica do cache.
- `core/domain/cache.SyncCache` — estrutura validada do cache.

## Decisões de Design Identificadas

| Decisão                                                         | Evidência no código                            | Confiança |
| --------------------------------------------------------------- | ---------------------------------------------- | --------- |
| Degradar para `True` em falha (não-bloqueio)                    | `service.py` (`try/except` → `True`)           | 🟢        |
| Dentro do TTL retorna `True` mesmo divergindo (evita rede)      | `service.py`                                   | 🟢        |
| Cache validado por Pydantic (regex SHA1) e gravado atomicamente | `cache.py` + `write_file_atomic`               | 🟢        |
| Exposição exclusiva via MCP (sem subcomando CLI)                | ausência em `main.py`, presença em `server.py` | 🟢        |

## Estado Interno

O estado persistente é o arquivo de cache JSON (`.harness/sync-cache.json`, fonte única `layout.py:SYNC_CACHE_REL_PATH`), com `last_checked_time` e `commit_hash`. Sem estado em memória entre chamadas.

## Observabilidade

- Avisos impressos em falha de rede/git (degradação para `True`).
- Sem logging estruturado dedicado.

## Riscos e Lacunas

- 🟡 O TTL segue **chumbado na tool MCP** (24), embora `[sync]` exista no domínio — config declarada parcialmente sem efeito na borda. O caminho do cache deixou de ser chumbado: vem de `layout.py:SYNC_CACHE_REL_PATH` (T7 saneado, MD-0013).
- 🟡 Sem verificação de trabalho local (ahead/dirty) — comportamento presente no legado, ausente no core atual.
