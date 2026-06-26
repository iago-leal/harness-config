# Data Delta: Ofertas de fim de sessão — push e upgrade

> Identificador: `014-oferta-upgrade-ao-encerrar`
> Data: `2026-06-26`
> Base: modelo extraído em `_reversa_sdd/` (sessão, sync, config)

## 1. Resumo

A feature **não introduz nem altera estado persistido de domínio**. As ofertas são calculadas
no momento do encerramento e descartadas; nada é gravado para representá-las. Não há novo
arquivo de cache (RN-07 dispensa TTL para a verificação de upgrade ao encerrar).

## 2. Modelos efêmeros (em memória, não persistidos)

Modelos de valor produzidos pelo `EndSessionOffersService` e consumidos pela borda:

| Modelo             | Campos                                                                | Origem dos dados                                                                        |
| ------------------ | --------------------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| `PushOffer`        | `branch: str`, `ahead: int`, `is_default_branch: bool`, `remote: str` | `GitPort.get_current_branch`, `count_commits_ahead('@{u}..HEAD')`, `get_default_branch` |
| `UpgradeOffer`     | `current_version: str`, `target_version: str`, `upstream_path: str`   | `config.harness.version` + `SyncService` (fetch + ler ref remota)                       |
| `EndSessionOffers` | `push: Optional[PushOffer]`, `upgrade: Optional[UpgradeOffer]`        | agregado; campos `None` quando a oferta não se aplica                                   |

> São objetos de transporte entre domínio e borda; não têm serialização persistida nem schema
> de arquivo. Implementáveis como `dataclass`/`pydantic` simples, coerentes com `core/domain`.

## 3. Estado persistido existente — sem mudança

| Artefato                                        | Mudança                                                       |
| ----------------------------------------------- | ------------------------------------------------------------- |
| `.harness/estado-da-sessao.md` (`SessionState`) | nenhuma; o fechamento (013) grava como hoje.                  |
| `.harness/sync-cache.json` (`SyncCache`)        | nenhuma; não é usado pela verificação de upgrade ao encerrar. |

## 4. Configuração tocada (não é modelo de domínio)

| Campo                         | Arquivo                                                           | Mudança                                                                                              |
| ----------------------------- | ----------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| `harness.version`             | `harness.toml` (do projeto-alvo)                                  | regravado pelo `upgrade_project` quando o upgrade é aceito e executado (comportamento já existente). |
| `version` / `current_version` | `src/core/domain/config.py`, `src/core/bootstrap/init_service.py` | bump da própria release do core (D-11), gate de rematerialização.                                    |

## 5. Migração de dados

n/a — nenhuma migração necessária. Nenhum dado histórico é reinterpretado nem convertido.
