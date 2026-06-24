# Data-delta: Ganchos de ciclo de vida para o Antigravity

> Identificador: `009-hooks-antigravity`
> Data: `2026-06-24`
> Base extraída: `_reversa_sdd/erd-complete.md` (sem banco relacional — persistência em arquivos versionados)

## Contexto

O `harness-core` **não tem banco de dados** (`_reversa_sdd/architecture.md#3-modelo-de-dados`): a persistência é toda em arquivos (Markdown, JSON, TOML). O "modelo de dados" desta feature é, portanto, um delta de **artefatos de configuração**.

## Novos artefatos

### 1. `.agents/hooks.json` (novo, versionável no projeto-alvo)

Estrutura (named-hook único `harness`; schema completo em `interfaces/antigravity-hook-io.md`):

| Chave                 | Tipo   | Descrição                                                                                                                                     |
| --------------------- | ------ | --------------------------------------------------------------------------------------------------------------------------------------------- |
| `harness`             | objeto | Named-hook do harness. Convive com chaves de terceiros (merge preserva as demais)                                                             |
| `harness.PreToolUse`  | array  | Captura de `TargetFile` nas tools de escrita (matcher `write_to_file\|replace_file_content\|multi_replace_file_content`) — condicional a D-03 |
| `harness.PostToolUse` | array  | Formatação (mesmo matcher de escrita)                                                                                                         |
| `harness.Stop`        | array  | Indexação de microdecisões                                                                                                                    |

Cada handler: `{ "type": "command", "command": "<abs>/harness agy-hook <evento>", "timeout": <int> }`.

### 2. Mapa efêmero `stepIdx → TargetFile` (scratch, não versionado)

- **Local:** sob o `artifactDirectoryPath` informado no payload (ex.: `<artifactDir>/.harness-agy/pending-format.json`).
- **Ciclo de vida:** escrito no `PreToolUse`, lido e consumido no `PostToolUse` do mesmo `stepIdx`. Efêmero por conversa.
- **Só existe se** D-03 confirmar a estratégia de captura (no fallback Stop+git-diff, este artefato não nasce).

## Artefatos alterados

### `harness.toml` — **sem mudança**

O campo `[harness].active_harness: Literal["claude","gemini","antigravity"]` já aceita `"antigravity"` (`core/domain/config.py`). Nenhum campo novo é necessário. Se no futuro o caminho do `hooks.json` precisar ser configurável, seria uma `FormattingSection`-like nova seção — **fora de escopo** agora.

## Migrações necessárias

- **n/a.** Não há dados pré-existentes a migrar. Projetos já inicializados como `antigravity` que rodarem `./harness upgrade` passam a receber/atualizar o `.agents/hooks.json` (idempotente, merge por named-hook).

## Campos removidos

- Nenhum.
