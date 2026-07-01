# Data-delta: fonte única + hooks não-destrutivos

> Feature: `020-fonte-unica-e-hooks` · Data: `2026-07-01`
> Base: modelo extraído em `_reversa_sdd/` (não há banco relacional; o "dado" do harness é config em arquivo e estado em `.harness/`).

## 1. Escopo

O harness não tem esquema de banco. Os "dados" afetados são: (a) o `harness.toml` por-projeto e (b) o layout físico da instalação. O estado de negócio em `.harness/` (decisões, índice, estado-da-sessão) é **inalterado**.

## 2. `harness.toml` — diff conceitual

| Campo                                                | Antes                                      | Depois                               | Migração                                                                        |
| ---------------------------------------------------- | ------------------------------------------ | ------------------------------------ | ------------------------------------------------------------------------------- |
| `[harness].upstream_path`                            | caminho absoluto do upstream               | **inalterado** — vira a única âncora | nenhuma                                                                         |
| `[harness].version`                                  | versão do core instalada (ex.: `"1.2.56"`) | **removido**                         | `migrate` apaga a linha; ausência é tolerada por `load_config` (campo opcional) |
| `[harness].active_harness`                           | `claude`/`gemini`/`antigravity`            | inalterado                           | nenhuma                                                                         |
| `[session]`, `[decisions]`, `[formatting]`           | paths relativos ao projeto                 | inalterados                          | nenhuma                                                                         |
| `[sync]` (`cache_ttl_hours`, `remote_check_enabled`) | usado pelo `SyncService`                   | **órfão** (SyncService removido)     | `migrate` pode remover a seção; inofensiva se ficar                             |

Nota: `load_config` usa `HarnessConfig(**data)` (pydantic). Remover `version` exige que o campo seja **opcional** no modelo (ou que o parse ignore extras). Verificar `SyncSection`/campo `version` em `core/domain/config.py` ao remover — evitar que um toml antigo com `version` quebre o parse e vice-versa.

## 3. Layout físico da instalação — diff

| Artefato no alvo                                                | Antes                                       | Depois                                                                         |
| --------------------------------------------------------------- | ------------------------------------------- | ------------------------------------------------------------------------------ |
| `.harness/harness-core/` (código + `.venv`, ~108 MB)            | presente, gitignored                        | **ausente** (executa do upstream)                                              |
| `harness` (wrapper)                                             | cópia executora (aponta p/ core local)      | **shim** (aponta p/ core do upstream)                                          |
| `.harness/decisoes/`, `microdecisoes.md`, `estado-da-sessao.md` | presentes                                   | inalterados                                                                    |
| `.git/hooks/pre-commit`,`post-merge`                            | apontam p/ python local                     | apontam p/ **shim**; hooks alheios preservados                                 |
| `.claude/settings.json`                                         | eventos do harness substituídos por inteiro | itens do harness mesclados por-item; itens alheios preservados                 |
| `.gitignore` (`/.harness/harness-core/`)                        | entrada do core vendored                    | pode ser removida pelo `migrate` (não há mais core local); inofensiva se ficar |

## 4. Migração de dados

- **Idempotente:** rodar `migrate` duas vezes converge (shim já instalado, core já ausente, `version` já removido).
- **Não-destrutiva:** só `.harness/harness-core/` é apagado; todo o resto de `.harness/` e hooks/settings alheios são preservados.
- **`--dry-run`:** relata o que faria (espaço a liberar, hooks a preservar) sem escrever.
- **Ordem segura:** apagar o core é o **último** passo, após shim + hooks já apontarem para o upstream.
- **Caso `livro-mfc`:** remover também o `harness-core/` legado na raiz (layout duplo pré-011).

## 5. Rollback

Reverter uma instalação = reidratar pelo `init` clássico do upstream (recopia core + venv) — o inverso exato do `migrate`. O estado em `.harness/` nunca é tocado, então nenhum dado de negócio se perde no ciclo migrar↔reidratar.
