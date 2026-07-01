# Legacy-impact: fonte única + hooks não-destrutivos

> Feature: `020-fonte-unica-e-hooks` · Data: `2026-07-01`
> **Rodada parcial** — blocos executados: (1) materializadores não-destrutivos (T004/T005/T010/T011) e (2) shim + init fonte única (T001/T002/T003/T006/T012). Faltam: descontinuação de `upgrade`/`sync`/`version` (T008/T009/T013/T015/T016), `migrate` (T007/T014/T017) e verificação (T018/T019/T020).

## Arquivos afetados

| Arquivo afetado                                                                                                                        | Componente (`_reversa_sdd/`)                                                 | Tipo            | Severidade | Justificativa                                                                                                                                           |
| -------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------- | --------------- | ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `src/core/bootstrap/init_service.py`                                                                                                   | `initialize_project` — `domain.md#2.9` (RN-N19)                              | regra-alterada  | HIGH       | O `init` deixa de copiar o core e de criar venv; grava o shim, não grava `version`, instala hooks in-process e ignora só o sync-cache (não mais o core) |
| `src/core/bootstrap/shim.py` (novo)                                                                                                    | Wrapper de execução — `domain.md#2.9` (RN-N19)                               | componente-novo | MEDIUM     | `render_shim()`: fonte única do wrapper que executa o core do upstream com o cwd do projeto e falha barulhento sem upstream                             |
| `src/core/install/claude_settings.py`                                                                                                  | `materialize_claude_settings` — `domain.md#2.13` (RN-N30), feature 016/RN-05 | regra-alterada  | MEDIUM     | Merge do `.claude/settings.json` passa a ser **por-item** por assinatura no `command`, preservando hooks do usuário no mesmo evento                     |
| `src/core/bootstrap/service.py`                                                                                                        | `install_hooks` — `domain.md#2.7` (RN-N15)                                   | regra-alterada  | MEDIUM     | Instalação dos hooks git não-destrutiva (cria/atualiza/encadeia por assinatura) e via shim                                                              |
| `src/core/domain/config.py`                                                                                                            | `load_config`/`HarnessSection` — `domain.md#2.8` (RN-N16)                    | preservada      | LOW        | Já tolerava `harness.toml` com e sem `version`; nenhuma alteração de produção — apenas fixado por teste                                                 |
| `tests/test_shim.py`, `tests/test_init.py`, `tests/test_config.py`, `tests/test_install_claude_settings.py`, `tests/test_bootstrap.py` | (suíte)                                                                      | —               | LOW        | +smoke do shim, contrato de init fonte única, tolerância a version, merge por-item, hooks não-destrutivos                                               |

## Diff conceitual por componente

- **`initialize_project` (cópia física → fonte única).** Antes replicava `harness-core` no alvo (`_copy_tree`), criava `.venv` + `pip install`, copiava o wrapper e rodava bootstrap por subprocesso da venv de destino, além de gravar `version` no `harness.toml` e ignorar a cópia vendored no `.gitignore`. Agora grava o **shim** (`render_shim()`), instala os hooks **in-process** (`BootstrapService(fs).install_hooks`), mantém a árvore `.harness/` e as materializações de IDE, grava o `harness.toml` **sem `version`** e ignora apenas `sync-cache.json`. O core (código + venv) passa a viver exclusivamente no upstream.
- **`shim.py` (novo).** Contrato de execução do wrapper: `cd` para a raiz do projeto, lê `upstream_path`, executa `python`+`main.py` do upstream repassando os args; upstream ausente → stderr + exit 1. Reutilizável por `init` e (adiante) `migrate`.
- **`materialize_claude_settings` (por-evento → por-item)** e **`install_hooks` (sobrescrita → não-destrutivo + shim):** ver rodada anterior; comportamento inalterado nesta.

## Preservadas (regras 🟢 do `domain.md` intactas)

- **RN-N16** (via única tipada de configuração) — `load_config` inalterado; só ganhou testes de tolerância a `version`.
- **RN-N17** (footprint global zero) — toda escrita do `init` segue sob `target_path`.
- **RN-N20 / RN-N21** (upgrade físico / checagem passiva de versão) — **ainda intactas** neste corte; serão modificadas/removidas no bloco de descontinuação.
- **RN-N27 / RN-N28 / RN-N29 / RN-N30** (materializadores Antigravity/skills/local_apply) — a fiação in-process do `init` para materializações foi preservada.
- **RN-N4** (comportamento barulhento) — shim e materializadores falham barulhento.

## Modificadas (regras 🟢 alteradas)

- **RN-N19** (init replica core + venv, instala hooks por subprocesso) → **fonte única**: instala o shim, sem cópia nem venv, com bootstrap in-process e `harness.toml` sem `version`.
- **RN-N15** (bootstrap reescreve hooks incondicionalmente) → não-destrutivo por assinatura + via shim.
- **Materialização do `settings.json` do Claude** (016/RN-05, sob RN-N30) → merge **por-item**.
