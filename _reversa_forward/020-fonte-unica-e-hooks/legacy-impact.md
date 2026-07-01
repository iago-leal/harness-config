# Legacy-impact: fonte única + hooks não-destrutivos

> Feature: `020-fonte-unica-e-hooks` · Data: `2026-07-01`
> **Rodada parcial** — blocos executados: (1) materializadores não-destrutivos (T004/T005/T010/T011); (2) shim + init fonte única (T001/T002/T003/T006/T012); (3) migração (T007/T014/T017). **Desescopados** (feature própria): descontinuação de `sync`/`upgrade`/oferta‑014 (T008/T009/T013/T015/T016). Falta: verificação final (T018/T019/T020).

## Arquivos afetados

| Arquivo afetado                                     | Componente (`_reversa_sdd/`)                           | Tipo              | Severidade | Justificativa                                                                                                                                            |
| --------------------------------------------------- | ------------------------------------------------------ | ----------------- | ---------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `src/core/bootstrap/init_service.py`                | `initialize_project` — `domain.md#2.9` (RN-N19)        | regra-alterada    | HIGH       | `init` fonte única: sem cópia do core nem venv; grava o shim, hooks in-process, `harness.toml` sem `version`                                             |
| `src/core/bootstrap/shim.py` (novo)                 | Wrapper de execução — `domain.md#2.9` (RN-N19)         | componente-novo   | MEDIUM     | `render_shim()`: executa o core do upstream com o cwd do projeto; falha barulhento sem upstream                                                          |
| `src/core/migrate/service.py` (novo)                | Migração da base — RN-08 (nova)                        | componente-novo   | HIGH       | `MigrateService`: converte instalações copiadas → fonte única; remove `.harness/harness-core/` (por último), com guarda de nunca tocar o upstream        |
| `src/core/ports/fs.py` + `src/adapters/fs/local.py` | `FileSystemPort` — porta de infraestrutura             | contrato-alterado | MEDIUM     | Novo método `remove_tree` (rmtree) para a migração apagar a cópia do core                                                                                |
| `src/main.py`                                       | CLI — driver                                           | contrato-alterado | MEDIUM     | Novo subcomando `migrate` (`--dry-run`, raiz default `~/dev`); correção do `except NotAGitRepositoryError` (import faltante, F821 latente pré-existente) |
| `src/core/install/claude_settings.py`               | `materialize_claude_settings` — 016/RN-05 (sob RN-N30) | regra-alterada    | MEDIUM     | Merge do `settings.json` por-item, preservando hooks do usuário                                                                                          |
| `src/core/bootstrap/service.py`                     | `install_hooks` — `domain.md#2.7` (RN-N15)             | regra-alterada    | MEDIUM     | Hooks git não-destrutivos (assinatura + `.local`) e via shim                                                                                             |
| `tests/*`                                           | (suíte)                                                | —                 | LOW        | +smoke shim, contrato init, tolerância a version, merge por-item, hooks não-destrutivos, migração (238 passed)                                           |

## Diff conceitual por componente

- **`MigrateService` (novo).** Descobre instalações sob uma raiz (`list_dir` + `harness.toml`), e para cada uma: instala o shim, reescreve os hooks (via `install_hooks`), re-materializa o `settings.json`, remove `version` do toml e **por último** apaga a(s) cópia(s) do core (`.harness/harness-core/` e o legado `harness-core/` do `livro-mfc`). Idempotente; `--dry-run` só relata. **Guardas de segurança:** nunca migra o diretório do upstream (`upstream_self`) nem uma autoreferência; `remove_tree` só aceita alvos cujo basename é `harness-core`; pula instalações cujo core do upstream esteja ausente. Exceção consciente ao footprint zero (RN-N17): atua sobre outros projetos por design.
- **`FileSystemPort.remove_tree` (novo).** Método de porta implementado em `LocalFileSystemAdapter` (`shutil.rmtree`) e nos três fakes de teste. A validação do alvo cabe ao chamador (`MigrateService._safe_remove_core`).
- **`initialize_project` / `shim.py` / `materialize_claude_settings` / `install_hooks`:** ver blocos anteriores; comportamento inalterado nesta rodada.

## Preservadas (regras 🟢 do `domain.md` intactas)

- **RN-N16** (config tipada), **RN-N17** (footprint zero no `init`/materialize — o `migrate` é a exceção declarada), **RN-N4** (barulhento).
- **RN-N20 / RN-N21** (upgrade físico / checagem passiva) — **ainda intactas**; desescopadas para feature própria.
- **RN-N27 / RN-N28 / RN-N29 / RN-N30** (materializadores) — fiação in-process preservada.

## Modificadas (regras 🟢 alteradas) / Novas

- **RN-N19** (init replica core + venv) → **fonte única** (shim, sem cópia/venv, sem `version`).
- **RN-N15** (bootstrap reescreve hooks) → não-destrutivo + via shim.
- **Materialização do `settings.json`** (016/RN-05) → merge **por-item**.
- **RN-08 (nova)** — migração da base instalada via `harness migrate`, com guardas de segurança.
- **`FileSystemPort` (contrato de porta)** — novo `remove_tree`.
