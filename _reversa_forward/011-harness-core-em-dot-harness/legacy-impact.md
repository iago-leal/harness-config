# Legacy Impact: harness-core dentro de `.harness/`

> Feature `011-harness-core-em-dot-harness` · 2026-06-25
> Execução **completa** por `/reversa-coding` (T001–T018): código, testes, move físico do core para `.harness/harness-core/`, wrapper e smoke. Suíte verde (139 passed) antes e depois do move.

## Estado final

O core foi fisicamente realocado para `.harness/harness-core/` (no fonte e no que o `init` gera), o wrapper resolve o novo caminho, a `.venv` foi recriada fresca e os ganchos Git foram regenerados apontando `.harness/harness-core/...`. A raiz do repositório-fonte passou a exibir um único diretório do harness (`.harness/`), com o core ainda **versionado** ali (69 arquivos rastreados). Em projetos-alvo, `init`/`upgrade` instalam o core em `.harness/harness-core/` e o gitignoram. Smoke ponta-a-ponta verde.

## Arquivos afetados

| Arquivo afetado                                     | Componente (`_reversa_sdd/`)                             | Tipo                      | Severidade | Justificativa                                                                                                                       |
| --------------------------------------------------- | -------------------------------------------------------- | ------------------------- | ---------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| `harness-core/src/core/domain/layout.py`            | Núcleo de domínio (`architecture.md#1`)                  | componente-novo           | LOW        | Fonte única do caminho do core; só constantes, sem lógica                                                                           |
| `harness-core/src/core/bootstrap/init_service.py`   | `InitializationService` (`domain.md#2.9`, RN-N19/RN-N20) | regra-alterada            | MEDIUM     | Destino da cópia → `.harness/harness-core/`; subida de upstream +1 nível; novo `_ensure_gitignore_entry` chamado por init e upgrade |
| `harness-core/src/core/bootstrap/service.py`        | `BootstrapService` (ganchos Git)                         | regra-alterada            | MEDIUM     | Os scripts pre-commit/post-merge passam a embutir `.harness/harness-core/...` via `CORE_REL_PATH`                                   |
| `harness-core/src/core/sync/service.py`             | `SyncService` (`domain.md#2.9`, RN-N21)                  | regra-alterada            | LOW        | Caminho do `config.py` do upstream na checagem passiva de versão                                                                    |
| `harness-core/src/core/install/template.md`         | Documentação de instalação                               | delta-de-contrato-externo | LOW        | Texto de setup aponta o novo caminho (contrato com o humano/agente instalador)                                                      |
| `harness-core/src/core/documentation/template.html` | Documentação HTML                                        | regra-alterada            | LOW        | Snippet `cd .harness/harness-core`                                                                                                  |
| `harness-core/tests/test_init.py`                   | Cobertura de init/upgrade                                | cobertura                 | LOW        | Caminhos esperados atualizados; e `tests/test_wrapper.py` ajustado para `../../../harness` após o move                              |
| `harness-core/tests/test_footprint.py`              | Contrato de footprint (RN-N17)                           | cobertura                 | LOW        | Novo caso cobre a escrita do `.gitignore` sob `target_path`                                                                         |
| `harness-core/tests/test_gitignore_entry.py`        | Cobertura de `_ensure_gitignore_entry`                   | cobertura                 | LOW        | Cria/idempotência/preservação de conteúdo                                                                                           |

## Diff conceitual por componente

- **Módulo de layout (novo).** Introduz `CORE_REL_PATH = ".harness/harness-core"` e derivados (`CORE_MAIN_REL_PATH`, `CORE_VENV_PYTHON_REL_PATH`, `CORE_GITIGNORE_ENTRY`). Centraliza o literal antes espalhado em ~7 pontos — ponto único de mudança, baixo acoplamento.
- **`InitializationService`.** `src_core`/`dst_core` passam a usar `CORE_REL_PATH` (init e upgrade), copiando para `<alvo>/.harness/harness-core/`. A resolução default do `upstream_path` sobe um nível a mais (o arquivo residirá em `.harness/harness-core/src/core/bootstrap/` após o move). `_get_upstream_version` lê o `config.py` sob o novo caminho. Novo método `_ensure_gitignore_entry` registra `.harness/harness-core/` no `.gitignore` do alvo, de forma idempotente e sob `target_path`, chamado ao fim de `initialize_project` e `upgrade_project`.
- **`BootstrapService`.** Os geradores `_pre_commit_script`/`_post_merge_script` embutem `CORE_MAIN_REL_PATH` e `CORE_VENV_PYTHON_REL_PATH` no lugar dos literais `harness-core/...`. Os ganchos passam a apontar para o core no novo layout (efetivo após re-bootstrap no deploy).
- **`SyncService`.** `check_version_update` lê a versão do upstream em `.harness/harness-core/src/core/domain/config.py`. Comportamento idêntico; muda só o caminho.

## Preservadas (regras 🟢 intactas)

- **RN-N17 — Footprint Global Zero.** Preservada e **reforçada**: o novo `_ensure_gitignore_entry` escreve apenas sob `target_path`, e o caso correspondente foi adicionado ao `test_footprint.py`.
- **RN-N5 — Core agnóstico ao harness.** Preservada: nenhum serviço de domínio foi ramificado por harness; a constante de layout é neutra.
- **RN-N16 — Configuração por via única tipada.** Inalterada.
- **RN-N18 — Upstream e versão no `harness.toml`.** Inalterada: o `harness.toml` operativo não mudou de lugar nem de esquema (D-05).
- **RN-N27 / RN-N28 — Materializadores de `hooks.json` e slash commands.** Inalterados em comportamento; seguem escrevendo sob `project_path`.

## Modificadas (regras 🟢 alteradas)

- **RN-N19 — Inicialização de Repositório Alvo.** O destino da replicação do core passa de `<alvo>/harness-core/` para `<alvo>/.harness/harness-core/`, e o `init` agora também registra a entrada no `.gitignore` do alvo.
- **RN-N20 — Evolução Não-Destrutiva (Upgrade).** Mesmo redirecionamento de destino; a preservação de `.reversa/` e `.harness/decisoes/` permanece; acrescenta a garantia idempotente do `.gitignore` (útil na migração de instalações antigas).
- **RN-N21 — Checagem Passiva de Atualização.** O caminho do `config.py` do upstream passa a `.harness/harness-core/...`.
- **Wrapper Executável (`harness`).** Passou a resolver `.harness/harness-core/.venv/bin/python3` e `.harness/harness-core/src/main.py`, com mensagem de falha instruindo restauração via `upgrade`/`init` (RN-07). Permanece um arquivo na raiz.
- **Ganchos Git (BootstrapService).** O conteúdo gerado e os ganchos instalados (`.git/hooks/pre-commit`, `post-merge`) apontam `.harness/harness-core/...` após o re-bootstrap (T017).
