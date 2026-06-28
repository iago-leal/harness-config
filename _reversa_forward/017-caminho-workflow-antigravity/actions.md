# Actions: Corrige o caminho de materialização do workflow Antigravity

> Identificador: `017-caminho-workflow-antigravity`
> Data: `2026-06-27`
> Roadmap: `_reversa_forward/017-caminho-workflow-antigravity/roadmap.md`

## Resumo

| Métrica                     | Valor                                       |
| --------------------------- | ------------------------------------------- |
| Total de ações              | 9                                           |
| Paralelizáveis (`[//]`)     | 3                                           |
| Maior cadeia de dependência | 6 (T002 → T005 → T006 → T007 → T008 → T009) |

## Fase 1, Preparação

| ID   | Descrição                                                                                                                                      | Dependências | Paralelismo | Arquivo alvo                                                         | Confidência | Status |
| ---- | ---------------------------------------------------------------------------------------------------------------------------------------------- | ------------ | ----------- | -------------------------------------------------------------------- | ----------- | ------ |
| T001 | Bump de versão 1.2.53 → 1.2.54 nos dois pontos de código sincronizados (`HarnessSection.version` e `BootstrapService.current_version`) (D-04). | -            | `[//]`      | `src/core/domain/config.py` (+ `src/core/bootstrap/init_service.py`) | 🟢          | `[X]`  |

## Fase 2, Testes

| ID   | Descrição                                                                                                                                                                                                                                                                                                                        | Dependências | Paralelismo | Arquivo alvo                                  | Confidência | Status |
| ---- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ | ----------- | --------------------------------------------- | ----------- | ------ |
| T002 | Teste do `AntigravityProfile`: `session_command_artifact` devolve `.agent/workflows/encerrar-sessao.md` (singular) e frontmatter **sem** `name:` (só `description`); `stale_session_command_paths()` → `[".agents/workflows/encerrar-sessao.md"]` (D-01/D-02/D-03). Adaptar asserções existentes que afirmavam o caminho plural. | -            | `[//]`      | `tests/test_antigravity_profile.py`           | 🟢          | `[X]`  |
| T003 | Teste de `materialize_session_commands`: grava o artefato no caminho do perfil; remove cada caminho de `stale_session_command_paths()` que exista; preserva outro `.md` de terceiro no mesmo diretório; **não** remove o diretório; perfil base sem override (default `[]`) não remove nada (via perfil fake) (D-03).            | -            | `[//]`      | `tests/test_session_commands_materializer.py` | 🟢          | `[X]`  |
| T004 | Teste: a versão materializada/asserida é `1.2.54` (D-04). Adaptar a asserção da 016 que fixava `1.2.53`.                                                                                                                                                                                                                         | T001         | -           | `tests/test_init.py`                          | 🟢          | `[X]`  |

## Fase 3, Núcleo

| ID   | Descrição                                                                                                                                                                                                                                                                                                                                                                                       | Dependências | Paralelismo | Arquivo alvo                           | Confidência | Status |
| ---- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ | ----------- | -------------------------------------- | ----------- | ------ |
| T005 | Editar `harness_profiles.py`: (a) `AntigravityProfile.session_command_artifact` devolve `.agent/workflows/encerrar-sessao.md` (singular) e remove a linha `name:` do `content`; (b) adicionar `stale_session_command_paths() -> list[str]` na base `HarnessProfile` com default `[]` e override no `AntigravityProfile` devolvendo `[".agents/workflows/encerrar-sessao.md"]` (D-01/D-02/D-03). | T002         | -           | `src/core/install/harness_profiles.py` | 🟢          | `[X]`  |
| T006 | Editar `materialize_session_commands`: após gravar `(rel_path, content)`, iterar `profile.stale_session_command_paths()` e, para cada caminho legado existente (`fs.exists`), removê-lo (`fs.remove`), sem nunca remover diretórios (não-destrutivo, RN-03) (D-03).                                                                                                                             | T003, T005   | -           | `src/core/install/session_commands.py` | 🟢          | `[X]`  |

## Fase 4, Integração

| ID   | Descrição                                                                                                                                                                                                                                                                                            | Dependências | Paralelismo | Arquivo alvo                | Confidência | Status |
| ---- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ | ----------- | --------------------------- | ----------- | ------ |
| T007 | Teste de integração de `apply_local_materializers`: num projeto com `.agents/workflows/encerrar-sessao.md` pré-existente (e um `.md` de terceiro), após materializar passa a existir `.agent/workflows/encerrar-sessao.md`, o órfão plural some e o terceiro permanece (migração via upgrade, D-05). | T006         | -           | `tests/test_local_apply.py` | 🟡          | `[X]`  |

## Fase 5, Polimento

| ID   | Descrição                                                                                                                                                                                                                           | Dependências                 | Paralelismo | Arquivo alvo                     | Confidência | Status |
| ---- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------- | ----------- | -------------------------------- | ----------- | ------ |
| T008 | Suíte do core verde: testes novos (T002–T003, T007) e adaptados (T002 caminho, T004 versão); revisar que gravação e remoção falham de forma barulhenta (a porta FS propaga exceção).                                                | T001, T004, T005, T006, T007 | -           | (verificação; sem arquivo único) | 🟢          | `[X]`  |
| T009 | Smoke end-to-end dos cenários A e B do `onboarding.md`: `init` em sandbox antigravity grava no singular sem `name`; `upgrade` num projeto com órfão plural migra para o singular, remove o órfão e preserva o workflow de terceiro. | T008                         | -           | (verificação; sem arquivo único) | 🟡          | `[X]`  |

## Notas de execução

<!-- Reservado para /reversa-coding registrar avisos ou observações durante a execução. -->

## Histórico de alterações

| Data       | Alteração                                  | Autor   |
| ---------- | ------------------------------------------ | ------- |
| 2026-06-27 | Versão inicial gerada por `/reversa-to-do` | reversa |
