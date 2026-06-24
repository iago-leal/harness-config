# Sync-Check (Sync) — Requisitos (Requirements)

> Regenerado pelo Writer em 2026-06-24 (Re-extração)
> Nível de Documentação: **Completo** · Escala: 🟢 CONFIRMADO · 🟡 INFERIDO · 🔴 LACUNA
> Rastreabilidade ao Legado: [`harness-core/src/core/sync/service.py`](file:///Users/iagoleal/dev/harness/harness-core/src/core/sync/service.py); cache `core/domain/cache.py`. Exposto **apenas via MCP** (`adapters/mcp/server.py`, tool `check_repository_sync`).

> ⚠️ **Reescrita vs versão anterior:** a implementação **deixou de ser** o script `harness-config/bin/sync-check.sh` (purgado, commit `5624f78`) e passou a ser o `SyncService` Python em `harness-core`. **Não há subcomando `sync` na CLI** — a capacidade só é acessível pelo servidor MCP. O cache saiu de `~/.claude/.sync-check/` para `.harness/sync_cache.json` (chumbado no MCP). Não há mais verificação de trabalho local (ahead/dirty), apenas a comparação HEAD local × remoto.

## Visão Geral

Decide se o repositório local está em sincronia com o remoto, de modo **resiliente a falhas**: qualquer erro de rede/git resulta em `True` (não trava o boot). Usa cache local com TTL para evitar `ls-remote` redundante.

## Responsabilidades

- Comparar o HEAD local com o commit remoto de `origin main`. 🟢
- Guardar o resultado em cache JSON por `cache_ttl_hours` (default 24). 🟢
- Degradar para `True` em qualquer falha de rede/git (não bloqueia). 🟢

## Regras de Negócio

- **RN-01 — Janela TTL de sincronia:** dentro do TTL, retorna `True` sem chamar a rede; mesmo divergindo o `commit_hash` cacheado do HEAD, retorna `True` dentro do TTL (política de evitar excesso de rede). 🟢
- **RN-02 — Resiliência offline:** qualquer erro de rede/git → `True` (imprime aviso e prossegue), nunca travando a inicialização. 🟢

## Requisitos Funcionais

| ID | Requisito | Prioridade | Critério de Aceite |
|----|-----------|-----------|-------------------|
| RF-01 | Verificar sincronia local × remoto. | Must | `check_sync(repo_path)` retorna `True` se `local_commit == remote_commit`, senão `False`. |
| RF-02 | Cache com TTL. | Must | Dentro do TTL, retorna sem chamar a rede; fora, consulta `git ls-remote origin main` e atualiza o cache. |
| RF-03 | Resiliência a falhas. | Must | Erro de parse de cache → checagem de rede; erro de rede/git → `True`. |

## Requisitos Não Funcionais

| Tipo | Requisito inferido | Evidência no código | Confiança |
|------|--------------------|---------------------|-----------|
| Performance | Evita `ls-remote` redundante dentro do TTL (default 24h). | `core/sync/service.py` | 🟢 |
| Resiliência | Tolerante a offline: assume `True` em falha. | `core/sync/service.py` | 🟢 |
| Atomicidade | Cache atualizado via `write_file_atomic`. | `core/sync/service.py` + `adapters/fs/local.py` | 🟢 |

## Critérios de Aceitação

```gherkin
Dado que o cache local foi atualizado há menos de 24h
Quando check_sync é chamado
Então retorna True sem executar git ls-remote.

Dado que o host está offline e o cache expirou
Quando check_sync tenta consultar o remoto
Então degrada para True (imprime aviso) sem levantar exceção.

Dado HEAD local diferente do commit remoto e cache expirado
Quando check_sync consulta a rede
Então retorna False.
```

## Prioridade (MoSCoW)

| Requisito | MoSCoW | Justificativa |
|-----------|--------|---------------|
| Comparação local × remoto (RF-01) | Must | Razão de existir da unit. |
| Cache TTL (RN-01) | Must | Evita gargalo de rede no boot do agente. |
| Resiliência offline (RN-02) | Must | Salvaguarda: nunca trava a inicialização. |

## Rastreabilidade de Código

| Arquivo | Função / Classe | Cobertura |
|---------|-----------------|-----------|
| `core/sync/service.py` | `SyncService.check_sync` | 🟢 |
| `core/domain/cache.py` | `SyncCache` | 🟢 |
| `adapters/git/subprocess.py` | `get_head_commit`, `get_remote_commit` | 🟢 |
| `adapters/mcp/server.py` | Tool `check_repository_sync` (cache `.harness/sync_cache.json`, TTL 24, chumbados) | 🟢 |

> 🟡 **Nota:** não há subcomando `sync` na CLI; a capacidade é exposta **apenas** via MCP.
