---
schemaVersion: 1
generatedAt: 2026-06-23T14:20:00Z
reversa:
  version: "1.2.43"
kind: target_domain_model
producedBy: designer
hash: "sha256:f7c6b66366bc1c8aeb2df09f66136a2d47505caff2d2b0a51f3438b73f367d12"
---

# Target Domain Model

> Modelo de domínio do sistema novo. Rastreabilidade explícita para o legado.

## Aggregates

### AGG-Decision
- **Aggregate root**: `Decision`
- **Invariantes**:
  - Toda decisão precisa de um ID estruturado e exclusivo no padrão `MD-XXXX`.
  - Deve conter um `gancho` de lifecycle válido declarado em seus metadados.
  - O arquivo Markdown correspondente deve conter cabeçalho H1 e seções delimitadas (`D`, `PORQUÊ`, `DESCARTADO`, `ESTADO`).
  - Relações declaradas de backlinks no grafo devem ter exatamente dois tokens (ex: `refina MD-0002`).
- **Comandos aceitos**:
  - `parse_from_markdown(content: str)`
  - `validate_integrity()`
  - `add_relationship(rel_type: str, target: str)`
- **Origem no legado**: `_reversa_sdd/microdecisoes/` (fichas sob `decisoes/`)

### AGG-Session
- **Aggregate root**: `SessionState`
- **Invariantes**:
  - Deve possuir a âncora do commit HEAD atual válida.
  - Apenas uma feature pode estar marcada como ativa por repositório.
- **Comandos aceitos**:
  - `start_session(feature_name: str, commit_hash: str)`
  - `close_session(commit_hash: str)`
  - `update_active_feature(feature_name: str)`
- **Origem no legado**: `_reversa_sdd/comandos-customizados/` (`ESTADO-DA-SESSAO.md`)

## Entidades

| Entidade | Aggregate dono | Atributos principais | Origem no legado |
|---|---|---|---|
| `Decision` | `AGG-Decision` | `id: str`, `gancho: str`, `status: str`, `relationships: List[Relationship]`, `filepath: str` | `decisoes/MD-*.md` |
| `SessionState` | `AGG-Session` | `commit_hash: str`, `active_feature: str`, `start_time: datetime`, `elapsed_seconds: int` | `ESTADO-DA-SESSAO.md` |

## Value objects

| Value object | Atributos | Validações | Origem |
|---|---|---|---|
| `Relationship` | `rel_type: str`, `target_id: str` | O tipo de relação deve ser válido (`refina`, `estende`, `bloqueia`); o ID alvo deve ter formato `MD-XXXX`. | Parser de relações em `gerar-index-decisoes.sh` |
| `SyncCache` | `last_checked_time: datetime`, `commit_hash: str` | Valida TTL de 24 horas antes de permitir novas requisições de rede. | `sync-check.sh` cache local |
| `FormatterConfig` | `file_extensions: List[str]`, `opt_out_file: str` | Extensões válidas para o resolvedor; nome fixo `.no-autoformat`. | `format-on-edit.sh` resolvedor |

## Eventos de domínio
*(Não aplicável. O paradigma escolhido é Orientação a Objetos com Injeção de Dependências puro acionado via CLI/MCP síncrono, sem mensageria ou pub/sub de eventos no domínio).*

## Regras de domínio

| Regra (ID) | Local no domínio novo | Origem (target_business_rules.md) |
|---|---|---|
| BR-MIGRAR-002 | `DecisionService` e `Decision.validate_integrity()` | BR-MIGRAR-002 |
| BR-MIGRAR-003 | `SyncService` e `SyncCache` | BR-MIGRAR-003 |
| BR-MIGRAR-007 | `FormattingService` e resolvedor de caminhos | BR-MIGRAR-007 |
| BR-MIGRAR-009 | `FormattingService` e `FormatterConfig` | BR-MIGRAR-009 |
| BR-MIGRAR-010 | `Decision.validate_integrity()` | BR-MIGRAR-010 |
| BR-MIGRAR-011 | `Decision.add_relationship()` | BR-MIGRAR-011 |
| BR-MIGRAR-015 | `SessionState.close_session()` | BR-MIGRAR-015 |

## Rastreabilidade para o legado

| Elemento novo | Origem no legado | Tipo de mapeamento |
|---|---|---|
| `AGG-Decision` | `decisoes/` + `gerar-index-decisoes.sh` | fundido |
| `AGG-Session` | `commands/encerrar-sessao.md` + `ESTADO-DA-SESSAO.md` | fundido |
| `SyncCache` | `bin/sync-check.sh` | dividido |
| `FormatterConfig` | `hooks/format-on-edit.sh` | dividido |

## Notas
As invariantes de integridade do `AGG-Decision` garantem que qualquer modificação em microdecisões no repositório local seja devidamente compilada no pre-commit, impedindo a submissão de relacionamentos de grafo corrompidos ou links sem correspondentes reais no disco.
