# Data-delta: Hook de busca ancorada no estado da sessão e no índice de decisões

> Identificador: `021-hook-busca-ancorada`
> Data: `2026-07-05`
> Base: modelo de configuração extraído em `_reversa_sdd/domain.md#2.8` (RN-N16) e `.harness/harness-core/src/core/domain/config.py`

## 1. Natureza do "dado" no harness

O harness **não tem banco relacional** (`_reversa_sdd/architecture.md#3`). O "modelo de dados" é o conjunto de estruturas tipadas de configuração/estado. O delta desta feature é um único campo de configuração; não há tabela, migração de schema nem índice de banco.

## 2. Campo novo

| Estrutura | Campo | Tipo | Default | Semântica |
|-----------|-------|------|---------|-----------|
| `SessionSection` (`[session]` no `harness.toml`) | `inject_decisions_index` | `bool` | `True` | Quando `True`, o `cmd resume` anexa o índice de decisões (`decisions.index_file`) ao contexto reinjetado no `SessionStart`. `False` suprime o anexo, preservando a reinjeção do estado |

Definição pretendida (delta sobre `config.py`):

```python
class SessionSection(BaseModel):
    state_file: str = ".harness/estado-da-sessao.md"
    inject_decisions_index: bool = True   # ← novo (feature 021)
```

## 3. Campos reusados (sem alteração)

| Estrutura | Campo | Papel nesta feature |
|-----------|-------|---------------------|
| `DecisionsSection` | `index_file` (default `.harness/microdecisoes.md`) | Origem do índice a anexar; já configurável (RN-N11) |
| `SessionSection` | `state_file` (default `.harness/estado-da-sessao.md`) | Fonte da narrativa reinjetada, inalterada |

## 4. Campos removidos

Nenhum.

## 5. Migração

**n/a — aditiva e retrocompatível.** `load_config` faz `HarnessConfig(**data)` (`config.py:63-68`); um `harness.toml` sem `[session].inject_decisions_index` (ou sem a seção `[session]` inteira) herda o default `True` via `Field(default_factory=SessionSection)`. Nenhuma reescrita de arquivo, nenhum passo de migração. Para desligar, o mantenedor adiciona:

```toml
[session]
inject_decisions_index = false
```

## 6. Compatibilidade

- Tomls antigos: válidos, com o recurso **ligado** por padrão (RN-05).
- `pydantic` ignora chaves extras somente se configurado; o `HarnessConfig` atual aceita as seções conhecidas. Um campo novo com default não quebra o parse de arquivos que não o declaram (é o comportamento já exercido por `RegenSection.command`, adicionado na feature 016).
