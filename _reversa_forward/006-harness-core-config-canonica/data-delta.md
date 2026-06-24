# Data Delta: harness-core como módulo per-projeto autocontido

> Identificador: `006-harness-core-config-canonica`
> Data: `2026-06-24`
> Base: modelo extraído em `_reversa_sdd/` (config tipada, estado de sessão, decisões)

## 1. Escopo do delta

Não há mudança de esquema de dados de domínio. O delta é de **configuração** (a forma do `HarnessConfig` e do `harness.toml`) e de **remoção de uma estrutura legada** (o dict de `load_harness_config`). O artefato de dados real — `.harness/estado-da-sessao.md` e suas entidades `SessionState`/`SessionNarrative` — fica inalterado.

## 2. Config: campos novos

### Nova seção `[session]` no `harness.toml`

```toml
[session]
state_file = ".harness/estado-da-sessao.md"
```

### Novo modelo `SessionSection` em `config.py`

| Campo | Tipo | Default | Papel |
|-------|------|---------|-------|
| `state_file` | `str` | `.harness/estado-da-sessao.md` | Caminho do estado de sessão canônico, lido por CLI (`cmd`) e MCP (`session_command`) |

`HarnessConfig` ganha o campo `session: SessionSection = Field(default_factory=SessionSection)`, na mesma forma de `decisions`.

## 3. Config: estrutura removida

- `load_harness_config(fs) -> dict` e seu `default_config` (`main.py:22-42`) são removidos. O dict expunha `harness.active_harness`, `formatting.*` e `sync.*` sem a seção `[decisions]` nem `[session]`; era a segunda via de config (dívida T5). Toda leitura passa a `load_config(fs) -> HarnessConfig`.

## 4. Campos alterados

- Nenhum campo de dados de domínio muda. Os campos existentes de `HarnessConfig` (`harness`, `formatting`, `sync`, `decisions`) permanecem idênticos.

## 5. Migração necessária

**Nenhuma migração de dados.** Justificativa:

- O default de `session.state_file` é idêntico ao literal hoje chumbado (`.harness/estado-da-sessao.md`), então o arquivo de estado existente continua sendo lido sem qualquer movimento.
- `harness.toml` sem `[session]` resolve para o default (o loader já trata seção ausente). Adicionar `[session]` explicitamente é recomendado, mas não obrigatório para o comportamento atual.
- A remoção de `load_harness_config` é refactor de código, não de dados: não há estado persistido associado a ele.

## 6. Invariantes preservados

- Round-trip do estado de sessão (`parse(render(x)) == x`) inalterado.
- Formato `MD-NNNN`, índice derivado e backlinks das decisões inalterados.
- A nova ficha `MD-NNNN` (reversão do `MD-0004`) segue o mesmo esquema das demais decisões; não é um campo novo, é um registro novo no grafo existente.
