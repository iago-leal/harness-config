# Actions: harness-core dentro de `.harness/` (footprint de um diretório na raiz)

> Identificador: `011-harness-core-em-dot-harness`
> Data: `2026-06-25`
> Roadmap: `_reversa_forward/011-harness-core-em-dot-harness/roadmap.md`

## Resumo

| Métrica                     | Valor                                                     |
| --------------------------- | --------------------------------------------------------- |
| Total de ações              | 18                                                        |
| Concluídas                  | 18                                                        |
| Pendentes                   | 0                                                         |
| Paralelizáveis (`[//]`)     | 8                                                         |
| Maior cadeia de dependência | 8 (T001 → T005 → T006 → T007 → T015 → T016 → T017 → T018) |

## Fase 1, Preparação

| ID   | Descrição                                                                                                                                                                                    | Dependências | Paralelismo | Arquivo alvo                             | Confidência | Status |
| ---- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ | ----------- | ---------------------------------------- | ----------- | ------ |
| T001 | Criar o módulo de layout com a fonte única do caminho do core: `CORE_REL_PATH = ".harness/harness-core"` e derivados úteis (caminho relativo de `src/main.py` e do `python3` da venv) (D-01) | -            | -           | `harness-core/src/core/domain/layout.py` | 🟢          | `[X]`  |

## Fase 2, Testes

| ID   | Descrição                                                                                                                                                                                                                                                                       | Dependências | Paralelismo | Arquivo alvo                                               | Confidência | Status |
| ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ | ----------- | ---------------------------------------------------------- | ----------- | ------ |
| T002 | Atualizar os testes de `init`/`upgrade`: layout de origem do mock e caminhos esperados de `harness-core/...` para `.harness/harness-core/...`. Inclui a correção do `test_wrapper.py` (`../../../harness`, pois `tests/` ficou 3 níveis abaixo da raiz após o move) (D-03/D-07) | -            | `[//]`      | `harness-core/tests/test_init.py`, `tests/test_wrapper.py` | 🟢          | `[X]`  |
| T003 | Estender o teste de footprint para cobrir a escrita do `.gitignore` sob `target_path` e o novo caminho do core, garantindo que nenhuma escrita escape do repositório (RN-N17/D-07)                                                                                              | -            | `[//]`      | `harness-core/tests/test_footprint.py`                     | 🟢          | `[X]`  |
| T004 | Novo teste do `_ensure_gitignore_entry`: grava a linha `.harness/harness-core/` quando ausente, é idempotente na reexecução e escreve só sob `target_path` (D-04)                                                                                                               | -            | `[//]`      | `harness-core/tests/test_gitignore_entry.py`               | 🟡          | `[X]`  |

## Fase 3, Núcleo

| ID   | Descrição                                                                                                                                                                                                                                                                      | Dependências | Paralelismo | Arquivo alvo                                      | Confidência | Status |
| ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------ | ----------- | ------------------------------------------------- | ----------- | ------ |
| T005 | Em `init_service.py`, usar `CORE_REL_PATH` para origem e destino da cópia (`src_core`/`dst_core`) em `initialize_project` e `upgrade_project`, passando a copiar para `<alvo>/.harness/harness-core/` (D-03)                                                                   | T001         | -           | `harness-core/src/core/bootstrap/init_service.py` | 🟢          | `[X]`  |
| T006 | Em `init_service.py`, ajustar a resolução do `upstream_path` para subir um nível a mais (arquivo passa a residir em `.harness/harness-core/src/core/bootstrap/`) e corrigir o caminho de `_get_upstream_version` para `.harness/harness-core/src/core/domain/config.py` (D-03) | T005         | -           | `harness-core/src/core/bootstrap/init_service.py` | 🟢          | `[X]`  |
| T007 | Em `init_service.py`, implementar `_ensure_gitignore_entry(target_path, ".harness/harness-core/")` (leitura, presença, append idempotente, escrita atômica sob `target_path`) e chamá-lo em `initialize_project` e `upgrade_project` (D-04)                                    | T006         | -           | `harness-core/src/core/bootstrap/init_service.py` | 🟡          | `[X]`  |
| T008 | Atualizar `sync/service.py` para ler a versão do upstream em `.harness/harness-core/src/core/domain/config.py` via `CORE_REL_PATH` (checagem passiva, RN-N21) (D-03)                                                                                                           | T001         | `[//]`      | `harness-core/src/core/sync/service.py`           | 🟢          | `[X]`  |
| T009 | Atualizar `bootstrap/service.py` para que o script dos ganchos Git (pre-commit/post-merge) embuta `.harness/harness-core/src/main.py` e `.harness/harness-core/.venv/bin/python3` via `CORE_REL_PATH` (D-01/D-03)                                                              | T001         | `[//]`      | `harness-core/src/core/bootstrap/service.py`      | 🟢          | `[X]`  |

## Fase 4, Integração

| ID   | Descrição                                                                                                                                                                                                        | Dependências                       | Paralelismo | Arquivo alvo    | Confidência | Status |
| ---- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------- | ----------- | --------------- | ----------- | ------ |
| T010 | Atualizar o wrapper `harness` (raiz) para resolver `VENV_PYTHON=.harness/harness-core/.venv/bin/python3` e `MAIN_PY=.harness/harness-core/src/main.py` (D-02)                                                    | -                                  | -           | `harness`       | 🟢          | `[X]`  |
| T011 | Endurecer as mensagens de erro do wrapper: quando a venv ou o core estiverem ausentes, imprimir instrução de restauração via `upgrade`/`init` a partir do `upstream_path` e encerrar com código ≠ 0 (RN-07/D-02) | T010                               | -           | `harness`       | 🟡          | `[X]`  |
| T015 | Rodar a suíte `pytest` completa e confirmar verde: init/upgrade no novo caminho, footprint estendido e idempotência do `.gitignore`, sem regressão nos caminhos Claude/Gemini/Antigravity (RF-08)                | T002, T003, T004, T007, T008, T009 | -           | `harness-core/` | 🟢          | `[X]`  |

## Fase 5, Polimento

| ID   | Descrição                                                                                                                                                                                                | Dependências | Paralelismo | Arquivo alvo                                        | Confidência | Status |
| ---- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ | ----------- | --------------------------------------------------- | ----------- | ------ |
| T012 | Atualizar o template de instalação por prompt: trocar `harness-core/.venv` e `harness-core/requirements.txt` por `.harness/harness-core/...` nas etapas e na checklist                                   | -            | `[//]`      | `harness-core/src/core/install/template.md`         | 🟢          | `[X]`  |
| T013 | Atualizar o snippet `cd harness-core` para `cd .harness/harness-core` no template de documentação HTML                                                                                                   | -            | `[//]`      | `harness-core/src/core/documentation/template.html` | 🟢          | `[X]`  |
| T014 | Conferir `CLAUDE.md`, `GEMINI.md` e `AGENTS.md` quanto a caminhos de setup do core (verificado: nenhuma referência de caminho, sem mudança)                                                              | -            | `[//]`      | `CLAUDE.md, GEMINI.md, AGENTS.md`                   | 🟡          | `[X]`  |
| T016 | No repo-fonte, `git mv harness-core .harness/harness-core` e **recriar** a `.venv` no novo caminho (`python3 -m venv .venv` + `pip install -r requirements.txt`), nunca mover a venv antiga (D-06)       | T015, T011   | -           | (árvore do repo)                                    | 🟢          | `[X]`  |
| T017 | Re-rodar `./harness bootstrap` para regenerar os ganchos Git com o novo caminho do core (D-06)                                                                                                           | T016, T009   | -           | `.git/hooks/`                                       | 🟢          | `[X]`  |
| T018 | Smoke conforme `onboarding.md` (seções A–C): `./harness decisions`/`format` da raiz, `init` num alvo descartável com `.gitignore` correto e idempotente, e a falha barulhenta com o core ausente (RN-07) | T016, T017   | -           | (verificação)                                       | 🟡          | `[X]`  |

## Notas de execução

- **2026-06-25 — execução completa.** Todas as 18 ações concluídas; suíte `pytest` verde (139 passed) antes e depois do move físico. O core foi realocado para `.harness/harness-core/` (69 arquivos versionados no fonte), a `.venv` recriada fresca, o wrapper aponta para o novo caminho com falha barulhenta, e os ganchos Git foram regenerados (`.git/hooks/*` embutem `.harness/harness-core/...`).
- **Achado durante o deploy:** o `test_wrapper.py` calculava o caminho do wrapper como `../../harness` a partir de `tests/`; após o move, `tests/` ficou 3 níveis abaixo da raiz, exigindo `../../../harness`. Corrigido e registrado como `corrected` no `progress.jsonl` sob T002. Esse arquivo escapou ao grep inicial por não conter o literal `harness-core`.
- **Smoke do `init`:** num alvo descartável, o core nasceu em `<alvo>/.harness/harness-core/`, sem `<alvo>/harness-core/`, com `.gitignore` contendo a linha uma única vez e o git efetivamente ignorando o core. A ausência do core produziu mensagem de restauração + exit 1.
- A `.venv` é gitignorada, então `git mv` não a carrega de forma útil — foi reconstruída em T016 (venvs não são realocáveis).

## Histórico de alterações

| Data       | Alteração                                           | Autor   |
| ---------- | --------------------------------------------------- | ------- |
| 2026-06-25 | Versão inicial gerada por `/reversa-to-do`          | reversa |
| 2026-06-25 | Execução completa por `/reversa-coding` (T001–T018) | reversa |
