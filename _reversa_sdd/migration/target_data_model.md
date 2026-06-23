---
schemaVersion: 1
generatedAt: 2026-06-23T14:20:00Z
reversa:
  version: "1.2.43"
kind: target_data_model
producedBy: designer
hash: "sha256:4299550cdece3a5f22a08241c0053743ccdaa00178b40d4e916305cef7ce980e"
---

# Target Data Model

> Modelo de dados do sistema novo. Definições de schema física baseada em arquivos, relacionamentos e restrições.

## Visão geral
O modelo de persistência de dados é **Baseado em Sistema de Arquivos (File-based Storage)**. Não são utilizados servidores de banco de dados tradicionais. O estado, caches e decisões residem em arquivos Markdown estruturados, caches JSON locais e arquivos de configuração TOML. O acesso e persistência física dessas estruturas são centralizados nos adaptadores da interface `FileSystemPort`.

## Entidades de dados

| Entidade | Tabela / coleção / arquivo | Aggregate dono | PK / ID de busca | Bounded context |
|---|---|---|---|---|
| `DecisionFile` | `decisoes/MD-*.md` | `AGG-Decision` | `MD-XXXX` (extraído do cabeçalho) | `DecisionRegistry` |
| `IndexFile` | `microdecisoes.md` | `AGG-Decision` | N/A (projeção do grafo) | `DecisionRegistry` |
| `SessionFile` | `ESTADO-DA-SESSAO.md` | `AGG-Session` | N/A (estado ativo único) | `InteractiveSession` |
| `SyncCacheFile` | `.reversa/cache/sync-check.json` | `SyncCache` | N/A (dados de cache locais) | `Automations` |
| `ConfigFile` | `harness.toml` | `FormatterConfig` | N/A (configurações do repositório) | `Automations` |

## Schema (JSON, TOML e Metadados Markdown)

### 1. Metadados do `DecisionFile` (Markdown YAML Front-matter)
```yaml
id: "MD-XXXX"
gancho: "pre-commit" | "post-merge" | "SessionStart" | "PostToolUse"
relacoes:
  - "refina MD-YYYY"
  - "estende MD-ZZZZ"
estado: "ativo" | "descartado"
```

### 2. Schema do `SyncCacheFile` (JSON)
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "SyncCache",
  "type": "object",
  "properties": {
    "last_checked_time": {
      "type": "string",
      "format": "date-time"
    },
    "commit_hash": {
      "type": "string",
      "pattern": "^[a-f0-9]{40}$"
    }
  },
  "required": ["last_checked_time", "commit_hash"]
}
```

### 3. Schema do `ConfigFile` (`harness.toml`)
```toml
[harness]
active_harness = "claude"     # claude | gemini | antigravity

[formatting]
exclude_paths = ["~/Notas", "~/.claude"]
opt_out_file = ".no-autoformat"

[sync]
cache_ttl_hours = 24
remote_check_enabled = true
```

## Relacionamentos

| Origem | Destino | Cardinalidade | Integridade | Notas |
|---|---|---|---|---|
| `DecisionFile.relacoes` | `DecisionFile.id` | N:1 | Validação semântica de parser | Cada ID referenciado nas relações de uma microdecisão deve existir como arquivo físico correspondente. |

## Restrições

- **Unicidade**: O ID contido em `DecisionFile` deve ser exclusivo. Não podem existir dois arquivos Markdown com o mesmo cabeçalho `id: MD-XXXX`.
- **Integridade referencial**: O parser valida se todas as dependências declaradas em `relacoes` correspondem a arquivos existentes. Relações órfãs geram erro de validação.
- **Gravação Atômica (Thread-Safety)**: Atualizações de arquivos de cache e estado devem ser escritas primeiramente em um arquivo temporário `.tmp` no mesmo diretório e, em seguida, renomeadas usando substituição atômica (`os.replace` do Python) para evitar arquivos corrompidos em caso de falha física no meio da gravação.

## Considerações específicas do paradigma alvo
- **Imutabilidade de Histórico**: As fichas de microdecisões sob `decisoes/` são persistidas de forma imutável (cada alteração resulta em uma nova versão ou novo MD). O arquivo `microdecisoes.md` é uma projeção gerada por demanda.

## Origem no legado

| Coleção / Arquivo novo | Origem no legado | Transformação |
|---|---|---|
| `decisoes/MD-*.md` | `harness-config/decisoes/MD-*.md` | Adicionado front-matter YAML formatado para simplificar parsing. |
| `.reversa/cache/sync-check.json` | Variáveis locais do Bash no boot | Transformado de cache volátil implícito em arquivo JSON isolado em cache local. |
| `harness.toml` | `settings.json` (parcial) | Migrado de formato acoplado ao Claude para TOML geral portável. |

## Notas
O formato TOML do `harness.toml` permite adicionar novas chaves e parametrizações sem afetar a lógica de leitura do Core, o que atende perfeitamente ao requisito de manutenibilidade e baixo acoplamento.
