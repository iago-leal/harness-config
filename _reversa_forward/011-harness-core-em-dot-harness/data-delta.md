# Data Delta: harness-core dentro de `.harness/`

> Feature `011-harness-core-em-dot-harness` · 2026-06-25
> Base: `_reversa_sdd/erd-complete.md` (sem banco relacional; persistência em arquivos)

## 1. Natureza dos dados afetados

Não há banco de dados, DDL, ORM nem migrations (`_reversa_sdd/architecture.md#3`). A "persistência" é a árvore de arquivos versionados e a configuração em TOML/JSON. O delta é, portanto, sobre **estrutura de arquivos** e **regras de ignore do git**, não sobre esquema relacional.

## 2. Diff conceitual da árvore de arquivos

### Antes (layout atual)

```
<projeto>/
├── .harness/                  # estado e decisões versionados
│   ├── decisoes/
│   ├── microdecisoes.md
│   └── estado-da-sessao.md
├── harness-core/              # código + venv  ← segundo diretório
│   ├── src/ tests/ harness.toml requirements.txt
│   └── .venv/                 (gitignorado)
├── harness                    # wrapper (arquivo)
└── harness.toml               # config operativa (só no alvo; no fonte roda em defaults)
```

### Depois (layout alvo)

```
<projeto>/
├── .harness/
│   ├── harness-core/          # código + venv  ← agora aninhado
│   │   ├── src/ tests/ harness.toml requirements.txt
│   │   └── .venv/             (gitignorado pela regra .venv/ existente)
│   ├── decisoes/
│   ├── microdecisoes.md
│   └── estado-da-sessao.md
├── harness                    # wrapper permanece na raiz
└── harness.toml               # inalterado: raiz, cwd-relative
```

## 3. Campos / artefatos: novos, movidos e inalterados

| Artefato                                                        | Mudança                                               | Observação                                                                             |
| --------------------------------------------------------------- | ----------------------------------------------------- | -------------------------------------------------------------------------------------- |
| Diretório do core                                               | **movido** `harness-core/` → `.harness/harness-core/` | Em fonte e alvo (D-01/D-03)                                                            |
| `harness.toml` operativo                                        | **inalterado**                                        | Raiz, lido cwd-relative por `load_config` (D-05)                                       |
| `harness-core/harness.toml` (template)                          | **movido** junto com o core                           | Não é o config operativo                                                               |
| `.gitignore` do **alvo**                                        | **novo campo**: linha `.harness/harness-core/`        | Escrita idempotente por `_ensure_gitignore_entry` (D-04)                               |
| `.gitignore` do **fonte**                                       | **inalterado**                                        | Core segue versionado; `.venv/`, `__pycache__/`, `.pytest_cache/` já cobrem os pesados |
| `.harness/decisoes/`, `microdecisoes.md`, `estado-da-sessao.md` | **inalterados**                                       | Não tocados pela realocação (RN-06/RN-N20)                                             |
| `.venv` do core                                                 | **recriado** no novo caminho                          | Não realocável; gitignorado                                                            |

## 4. Migração de instalações existentes

Para um **alvo já instalado** no layout antigo, ao rodar `upgrade` na nova versão:

1. O core é (re)copiado para `<alvo>/.harness/harness-core/` e o wrapper passa a apontar para lá.
2. A linha `.harness/harness-core/` é acrescentada ao `.gitignore` do alvo (idempotente).
3. O diretório antigo `<alvo>/harness-core/` **permanece órfão** na raiz — a diretriz não-destrutiva proíbe apagá-lo automaticamente.

→ Remoção do diretório órfão é **passo manual documentado** (ver `onboarding.md`), e a mensagem de `upgrade` deve avisar sobre ele. Sem índices, sem dados de usuário em risco: o core é vendored e regenerável.

## 5. Compatibilidade com o modelo extraído

- RN-N17 (footprint global zero) preservada: toda escrita sob `target_path`/repositório.
- RN-N18 (`upstream_path`/`version` no `harness.toml`) preservada: o `harness.toml` operativo não muda de lugar nem de esquema.
- RN-N19/RN-N20 (init/upgrade) alteradas apenas no **destino físico** da cópia, não no contrato.
