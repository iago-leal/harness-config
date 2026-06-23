# Data Delta: Instalação do Harness por Prompt Estruturado

> Identificador: `003-instalacao-por-prompt`
> Data: `2026-06-23`
> Modelo de referência: `_reversa_sdd/erd-complete.md`, `_reversa_sdd/domain.md`

## 1. Resumo

A feature **não cria nem altera nenhuma entidade persistente**. Ela apenas passa a **consumir** uma configuração já modelada e hoje ociosa: `HarnessConfig.harness.active_harness`. Não há banco de dados, schema, migração ou índice envolvidos — o estado relevante são arquivos de configuração já existentes.

## 2. Entidades de configuração tocadas

| Entidade / modelo | Arquivo | Mudança | Observação |
|-------------------|---------|---------|------------|
| `HarnessConfig` (pydantic) | `harness-core/src/core/domain/config.py` | passa a ser **usado** | Hoje o modelo existe mas o `main.py` re-parseia o `harness.toml` à mão. A feature lê `active_harness` via o modelo, fechando a dívida de config decorativo. |
| `harness.toml` `[harness].active_harness` | `harness-core/harness.toml` | leitura, sem alteração de schema | Valores válidos: `claude` \| `gemini` \| `antigravity` (já restritos por `Literal` no modelo). |

## 3. Campos novos

- Nenhum.

## 4. Campos removidos

- Nenhum.

## 5. Migrações necessárias

- Nenhuma. A feature é aditiva e somente leitura sobre a configuração existente.

## 6. Nota de integridade

- O modelo `HarnessConfig` já valida `active_harness` por `Literal["claude", "gemini", "antigravity"]`; um valor fora desse conjunto falha na carga — comportamento de erro barulhento desejado, alinhado ao RNF de robustez do `requirements.md`.
