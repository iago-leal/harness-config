# Actions: fonte única de execução + materialização de hooks não-destrutiva

> Identificador: `020-fonte-unica-e-hooks`
> Data: `2026-07-01`
> Roadmap: `_reversa_forward/020-fonte-unica-e-hooks/roadmap.md`

## Resumo

| Métrica                     | Valor                                              |
| --------------------------- | -------------------------------------------------- |
| Total de ações              | 20                                                 |
| Paralelizáveis (`[//]`)     | 12                                                 |
| Maior cadeia de dependência | 7 (T002 → T006 → T012 → T013 → T016 → T019 → T020) |

> Prática: TDD red→green por bloco (testes na Fase 2 antes do núcleo na Fase 3). Portas `fs`/`git`/`process` com `FakeFs` nos testes; smoke com git real na verificação final (memória `smoke-git-real-vs-mock-porcelain`).

## Fase 1, Preparação

| ID   | Descrição                                                                                                                                                                                                                                                                       | Dependências | Paralelismo | Arquivo alvo                                              | Confidência | Status |
| ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ | ----------- | --------------------------------------------------------- | ----------- | ------ |
| T001 | Definir o conteúdo canônico do **shim** como fonte única (constante/função `render_shim()`), conforme `interfaces/shim-execution.md`: resolve `upstream_path`, `cd` na raiz, `exec` do python+main do upstream, erro barulhento se ausente. Reutilizável por `init` e `migrate` | -            | `[//]`      | `.harness/harness-core/src/core/bootstrap/shim.py` (novo) | 🟢          | `[ ]`  |
| T002 | Tornar o parse de `load_config` tolerante a `harness.toml` **com e sem** `version` (campo opcional / extras ignorados), para não quebrar tomls antigos nem novos — ponto do `data-delta.md#2`                                                                                   | -            | `[//]`      | `.harness/harness-core/src/core/domain/config.py`         | 🟢          | `[ ]`  |

## Fase 2, Testes (red)

| ID   | Descrição                                                                                                                                                                                                                                                                                    | Dependências | Paralelismo | Arquivo alvo                                                 | Confidência | Status |
| ---- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ | ----------- | ------------------------------------------------------------ | ----------- | ------ |
| T003 | Testes (red) do shim (smoke por subprocesso, bash real): upstream válido → executa e repassa exit; `upstream_path` inválido/ausente → stderr nomeado + exit ≠ 0; invocação de subpasta ainda resolve a raiz (`cd`)                                                                           | T001         | `[//]`      | `.harness/harness-core/tests/test_shim.py` (novo)            | 🟢          | `[ ]`  |
| T004 | Testes (red) do merge **por-item** do `settings.json` (`interfaces/claude-settings-merge.md`): item próprio no mesmo evento preservado; sem duplicar em reexecução; `PreToolUse` e chaves de topo intactos; sem arquivo prévio → cria só os 3 itens                                          | -            | `[//]`      | `.harness/harness-core/tests/test_install_claude_settings.py`        | 🟢          | `[X]`  |
| T005 | Testes (red) de `install_hooks` não-destrutivo (`interfaces/git-hooks-merge.md`): `pre-commit` alheio → preservado em `.local` + encadeado; hook do harness antigo → atualizado; ausente → criado; `commit-msg` de terceiro intacto; hooks chamam o shim                                     | -            | `[//]`      | `.harness/harness-core/tests/test_bootstrap.py` | 🟢          | `[X]`  |
| T006 | Testes (red) do `init` fonte única: após `init`, alvo **sem** `.harness/harness-core/` e **sem** `.venv`; shim executável presente; `harness.toml` com `upstream_path` e **sem** `version`                                                                                                   | T001, T002   | `[//]`      | `.harness/harness-core/tests/test_init.py`                   | 🟢          | `[ ]`  |
| T007 | Testes (red) do `migrate`: instalação simulada convertida (shim instalado, hooks reescritos p/ shim, settings mesclado, `version` removido, `.harness/harness-core/` removido **por último**); `--dry-run` não escreve; idempotente; caso `livro-mfc` duplo; `.harness/decisoes/` preservado | T001         | `[//]`      | `.harness/harness-core/tests/test_migrate.py` (novo)         | 🟢          | `[ ]`  |
| T008 | Teste (red) de que `upgrade` virou **no-op barulhento**: aviso claro + exit 0, sem recopiar core nem materializar                                                                                                                                                                            | -            | `[//]`      | `.harness/harness-core/tests/test_upgrade_noop.py` (novo)    | 🟢          | `[ ]`  |
| T009 | Teste (red) do boot da CLI **sem** checagem passiva de versão: `SyncService` não importado/chamado; boot não emite alerta de nova versão                                                                                                                                                     | -            | `[//]`      | `.harness/harness-core/tests/test_main_boot.py` (novo)       | 🟡          | `[ ]`  |

## Fase 3, Núcleo

| ID   | Descrição                                                                                                                                                                                                                                                                                           | Dependências           | Paralelismo | Arquivo alvo                                                                        | Confidência | Status |
| ---- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------- | ----------- | ----------------------------------------------------------------------------------- | ----------- | ------ |
| T010 | Reescrever `materialize_claude_settings`: trocar `hooks[event] = value` por **merge por-item** com assinatura no `command` (`harness cmd resume`/`harness format`/`harness decisions`) — substitui/insere e preserva itens alheios (green T004)                                                     | T004                   | `[//]`      | `.harness/harness-core/src/core/install/claude_settings.py`                         | 🟢          | `[X]`  |
| T011 | Reescrever `install_hooks`: criar/atualizar/encadear por assinatura `— Harness Core`; hooks passam a invocar o shim (`./harness format`/`./harness decisions`) (green T005)                                                                                                                         | T005, T001             | `[//]`      | `.harness/harness-core/src/core/bootstrap/service.py`                               | 🟢          | `[X]`  |
| T012 | Reescrever `initialize_project` p/ fonte única: remover cópia do core (passo 3) e criação de venv (passo 7); gravar o shim (T001); não gravar `version`; manter `.harness/`, bootstrap e `apply_local_materializers`; revisar as entradas de `.gitignore` (core local não existe mais) (green T006) | T006, T001, T002       | -           | `.harness/harness-core/src/core/bootstrap/init_service.py`                          | 🟢          | `[ ]`  |
| T013 | Remover `upgrade_project`, `_get_upstream_version`, `UpstreamVersionUndeterminedError` de `init_service`; limpar de `layout.py` os `CORE_CONFIG_CANDIDATE_RELPATHS`/`CORE_CONFIG_REL_PATH`/`_LEGACY_CORE_REL_PATH` (detecção de versão do upstream)                                                 | T012                   | -           | `.harness/harness-core/src/core/bootstrap/init_service.py` + `.../domain/layout.py` | 🟢          | `[ ]`  |
| T014 | `MigrateService` (novo): converte instalações (shim, hooks git, settings merge, remove `version` do toml, remove `.harness/harness-core/` **por último**; caso `livro-mfc` duplo); idempotente, `--dry-run`, não-destrutivo quanto a estado/hooks alheios; relata espaço liberado (green T007)      | T007, T001, T010, T011 | -           | `.harness/harness-core/src/core/migrate/service.py` (novo)                          | 🟢          | `[ ]`  |

## Fase 4, Integração

| ID   | Descrição                                                                                                                                                                | Dependências | Paralelismo | Arquivo alvo                                                 | Confidência | Status |
| ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------ | ----------- | ------------------------------------------------------------ | ----------- | ------ |
| T015 | Remover `core/sync/service.py` e o **alerta passivo de versão** no boot do `main.py` (import + chamada `SyncService.check_version_update`) (green T009)                  | T009         | -           | `.harness/harness-core/src/main.py` + `.../core/sync/` (del) | 🟢          | `[ ]`  |
| T016 | `upgrade` no parser do `main.py` vira **no-op barulhento** (aviso "fonte única — nada a atualizar" + exit 0), sem chamar `upgrade_project` (removido) (green T008)       | T008, T013   | -           | `.harness/harness-core/src/main.py`                          | 🟢          | `[ ]`  |
| T017 | Adicionar o subcomando `migrate` ao parser do `main.py` (com `--dry-run` e alvo opcional, default `~/dev`), fiando o `MigrateService` com as portas `fs`/`git`/`process` | T014         | -           | `.harness/harness-core/src/main.py`                          | 🟢          | `[ ]`  |

## Fase 5, Polimento

| ID   | Descrição                                                                                                                                                                                                                                                          | Dependências                                               | Paralelismo | Arquivo alvo                                                                    | Confidência | Status |
| ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------- | ----------- | ------------------------------------------------------------------------------- | ----------- | ------ |
| T018 | Reconciliar a versão entre `config.py` (`1.3.0`) e `init_service.py` (`current_version` defasado em `1.2.56`); decidir e aplicar o bump da feature em lockstep + asserção de teste                                                                                 | T012, T013                                                 | `[//]`      | `.../domain/config.py` + `.../bootstrap/init_service.py` + `tests/test_init.py` | 🟡          | `[ ]`  |
| T019 | Ajustar mensagens/help/doc: texto do no-op do `upgrade`, help do `migrate`, remover menção a `./harness upgrade` do fluxo removido; conferir `doc-gen` (introspecção do parser) refletindo os comandos novos                                                       | T015, T016, T017                                           | -           | `.harness/harness-core/src/main.py`                                             | 🟢          | `[ ]`  |
| T020 | Verificação final: suíte do core verde + **smoke com git real** dos cenários A–F do `onboarding.md` (init sem venv/core; shim via upstream; erro barulhento; merge settings preserva alheio; hook git alheio preservado; `migrate` libera disco e preserva estado) | T010, T011, T012, T013, T014, T015, T016, T017, T018, T019 | -           | `.harness/harness-core/tests/` + manual                                         | 🟢          | `[ ]`  |

## Notas de execução

<!-- Reservado para /reversa-coding. -->

## Histórico de alterações

| Data       | Alteração                                  | Autor   |
| ---------- | ------------------------------------------ | ------- |
| 2026-07-01 | Versão inicial gerada por `/reversa-to-do` | reversa |
