# Actions: Ganchos de ciclo de vida para o Antigravity

> Identificador: `009-hooks-antigravity`
> Data: `2026-06-24`
> Roadmap: `_reversa_forward/009-hooks-antigravity/roadmap.md`

## Resumo

| Métrica                     | Valor                              |
| --------------------------- | ---------------------------------- |
| Total de ações              | 11                                 |
| Paralelizáveis (`[//]`)     | 10                                 |
| Maior cadeia de dependência | 4 (ex.: T003 → T006 → T008 → T011) |

## Fase 1, Preparação

| ID   | Descrição                                                                                                                       | Dependências | Paralelismo | Arquivo alvo                                        | Confidência | Status |
| ---- | ------------------------------------------------------------------------------------------------------------------------------- | ------------ | ----------- | --------------------------------------------------- | ----------- | ------ |
| T001 | Criar o pacote do adaptador de entrada do Antigravity com `__init__.py` vazio, abrindo o anel de adaptadores para o novo driver | -            | `[//]`      | `harness-core/src/adapters/antigravity/__init__.py` | 🟢          | `[X]`  |

## Fase 2, Testes

| ID   | Descrição                                                                                                                                                                                                                                                                                             | Dependências | Paralelismo | Arquivo alvo                                                | Confidência | Status |
| ---- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ | ----------- | ----------------------------------------------------------- | ----------- | ------ |
| T002 | Escrever testes do `AntigravityProfile`: `hooks_block()` parseia como JSON e contém o named-hook `harness` com `PostToolUse` (matcher das tools de escrita) e `Stop`; `apply_instructions()` não contém o aviso de placeholder e aponta `.agents/hooks.json`                                          | -            | `[//]`      | `harness-core/tests/test_antigravity_profile.py`            | 🟢          | `[X]`  |
| T003 | Escrever testes do adaptador de borda por payloads-fixture: `pre-tool-use` grava o mapa `stepIdx→TargetFile`; `post-tool-use` lê o mapa, chama o serviço de formatação e emite stdout `{}`; `stop` chama o serviço de decisões e emite JSON sem `decision:"continue"`; exceção interna nunca bloqueia | -            | `[//]`      | `harness-core/tests/test_antigravity_hook_bridge.py`        | 🟡          | `[X]`  |
| T004 | Escrever testes da materialização de `.agents/hooks.json`: merge por named-hook preservando chaves de terceiros, `command` com caminho absoluto, e nenhuma escrita fora do repositório (footprint)                                                                                                    | -            | `[//]`      | `harness-core/tests/test_antigravity_hooks_materializer.py` | 🟡          | `[X]`  |

## Fase 3, Núcleo

| ID   | Descrição                                                                                                                                                                                                                                                                                                                                                                              | Dependências | Paralelismo | Arquivo alvo                                           | Confidência | Status |
| ---- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ | ----------- | ------------------------------------------------------ | ----------- | ------ |
| T005 | Preencher `AntigravityProfile.hooks_block()` com o `hooks.json` real (named-hook `harness`: `PostToolUse` e `Stop`, mais `PreToolUse` de captura) e mover para `apply_instructions()` o texto de escopo por harness dos três perfis (Claude→`.claude/settings.json`, Gemini→ponte, Antigravity→`.agents/hooks.json`), sem o aviso de placeholder e sem novo placeholder (A003 / RN-N9) | T002         | `[//]`      | `harness-core/src/core/install/harness_profiles.py`    | 🟢          | `[X]`  |
| T006 | Implementar o adaptador de borda `hook_bridge`: parse do stdin do Antigravity por evento, recuperação do caminho via mapa `stepIdx→TargetFile` sob `artifactDirectoryPath`, delegação a `FormattingService`/`DecisionService` e emissão do stdout JSON exigido por evento, com captura de exceção sempre não-bloqueante                                                                | T001, T003   | `[//]`      | `harness-core/src/adapters/antigravity/hook_bridge.py` | 🟡          | `[X]`  |
| T007 | Implementar a rotina única `materialize_hooks_json(fs, project_path, command_path)` que lê o `.agents/hooks.json` existente, faz merge do named-hook `harness` (preservando chaves de terceiros) a partir do `AntigravityProfile` e grava de forma atômica — compartilhada por init e upgrade (A001)                                                                                   | T004         | `[//]`      | `harness-core/src/core/install/antigravity_hooks.py`   | 🟡          | `[X]`  |

## Fase 4, Integração

| ID   | Descrição                                                                                                                                                                                                                                               | Dependências | Paralelismo | Arquivo alvo                                      | Confidência | Status |
| ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ | ----------- | ------------------------------------------------- | ----------- | ------ |
| T008 | Registrar o subcomando fino `agy-hook <evento>` na CLI (`pre-tool-use`/`post-tool-use`/`stop`) que instancia o adaptador de borda e despacha por evento, reusando os adaptadores de fs/process já construídos                                           | T006         | `[//]`      | `harness-core/src/main.py`                        | 🟡          | `[X]`  |
| T009 | Chamar `materialize_hooks_json` em `initialize_project` (quando `active_harness == "antigravity"`) e em `upgrade_project`, ambos passando o caminho absoluto do `./harness` do projeto-alvo (D-05/D-06, rotina compartilhada A001)                      | T007         | `[//]`      | `harness-core/src/core/bootstrap/init_service.py` | 🟡          | `[X]`  |
| T010 | Tornar o `template.md` harness-aware: remover das linhas estáticas o escopo chumbado `.claude/settings.json` (Passo 3 e checklist do Passo 5) e a nota de pendência do SessionStart, deixando o escopo fluir por `{{APPLY_HOOKS}}` sem novo placeholder | T005         | `[//]`      | `harness-core/src/core/install/template.md`       | 🟢          | `[X]`  |

## Fase 5, Polimento

| ID   | Descrição                                                                                                                                                           | Dependências                       | Paralelismo | Arquivo alvo    | Confidência | Status |
| ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------- | ----------- | --------------- | ----------- | ------ |
| T011 | Rodar a suíte pytest completa e confirmar verde, incluindo os caminhos Claude/Gemini (sem regressão), e os novos testes do perfil, do adaptador e da materialização | T005, T006, T007, T008, T009, T010 | -           | `harness-core/` | 🟢          | `[X]`  |

## Notas de execução

- Execução via Workflow ultracode (`code-feature-009-hooks-antigravity`): 3 construtores em paralelo (fatias disjuntas), verificação adversarial e 1 iteração de correção. Suíte final: **110 testes verdes**.
- A verificação adversarial pegou um CRITICAL (import faltante de `materialize_hooks_json` em `init_service.py` → `NameError`) e um HIGH (ramo `agy-hook` carregava config fora do `try/except` não-bloqueante); ambos corrigidos.
- T010 ficou parcial no Workflow (o agente de correção restaurou a nota obsoleta do `SessionStart`/MD-0001 para manter um teste antigo verde). Completado manualmente fora do Workflow: nota obsoleta removida do `template.md` e teste `test_prompt_signals_sessionstart_gap` reescrito como `test_prompt_has_no_obsolete_sessionstart_pending`.
- Smoke test end-to-end real (CLI): `pre-tool-use`→`{"decision":"allow"}`, `post-tool-use` formatou o arquivo, `stop`→`{}`; prompt do Antigravity sem placeholder, apontando `.agents/hooks.json`, com `hooks.json` válido.
- D-03: implementada a estratégia primária (captura `PreToolUse` + formatação `PostToolUse` via scratch em `artifactDirectoryPath`). Fallback Stop+git-diff não foi necessário.

## Histórico de alterações

| Data       | Alteração                                                                   | Autor   |
| ---------- | --------------------------------------------------------------------------- | ------- |
| 2026-06-24 | Versão inicial gerada por `/reversa-to-do` (restrições A001/A003 embutidas) | reversa |
