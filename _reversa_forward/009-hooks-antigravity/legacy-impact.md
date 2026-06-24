# Legacy-impact: feature 009-hooks-antigravity

> Identificador: `009-hooks-antigravity`
> Data: `2026-06-24`
> Para a próxima re-extração reversa reconciliar o `_reversa_sdd/`.

Esta feature **estende** o legado; não removeu nem alterou contrato de domínio existente. Resumo do impacto por componente do `_reversa_sdd/`.

## Componentes do legado afetados

| Componente / arquivo                                        | Tipo de impacto   | Detalhe                                                                                                                                                                         |
| ----------------------------------------------------------- | ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `harness_profiles.py` — `AntigravityProfile`                | regra alterada    | Deixou de ser placeholder; `hooks_block()` emite `hooks.json` real e `apply_instructions()` aponta `.agents/hooks.json`. Novos atributos `ABS_PLACEHOLDER`, `WRITE_MATCHER`.    |
| `harness_profiles.py` — `ClaudeProfile`, `GeminiProfile`    | regra alterada    | `apply_instructions()` passou a carregar a nota de escopo por harness (antes estava chumbada no `template.md`).                                                                 |
| `src/adapters/antigravity/` (novo)                          | componente novo   | Terceiro driver de entrada (`hook_bridge.py` + `AntigravityHookBridge`), irmão da CLI e do servidor MCP.                                                                        |
| `main.py`                                                   | contrato alterado | Novo subcomando `agy-hook <evento>`; `agy-hook` adicionado à exceção do check passivo de sync e do carregamento global de config (carrega config dentro do próprio try/except). |
| `init_service.py` — `initialize_project`, `upgrade_project` | regra alterada    | Passam a materializar `.agents/hooks.json` quando `active_harness == "antigravity"` (RN-N19/RN-N20 estendidas).                                                                 |
| `install/antigravity_hooks.py` (novo)                       | componente novo   | `materialize_hooks_json` — rotina única de escrita com merge por named-hook, compartilhada por init e upgrade.                                                                  |
| `template.md`                                               | contrato alterado | Escopo dos ganchos agora flui por `{{APPLY_HOOKS}}` (RN-N9 preservada: seguem 4 placeholders). Removida a nota obsoleta do `SessionStart`/MD-0001 (feature 004 já a fechou).    |

## Regras de domínio (`domain.md`) tocadas

- **RN-N5 (o core não conhece o harness):** respeitada e reforçada — toda a lógica do Antigravity vive no adaptador/perfil/materializador; nenhum serviço de domínio foi ramificado por harness.
- **RN-N6 (reinjeção multi-harness por família):** inalterada — a reinjeção de estado segue só pelo `FileProjectionSink`.
- **RN-03 (não-bloqueio de formatadores):** preservada — o adaptador reusa `FormattingService.format_file` (sempre 0) e captura toda exceção.
- **RN-N9 (4 placeholders):** preservada.
- **RN-N17 (footprint global zero):** preservada — `materialize_hooks_json` escreve só dentro do projeto via `FileSystemPort`.
- **RN-N19/RN-N20 (init/upgrade):** estendidas com o passo de materialização do `hooks.json`.

## Regras de domínio NOVAS sugeridas para a próxima extração

- **(nova) Ganchos do Antigravity via `hooks.json` declarativo:** o harness emite `.agents/hooks.json` (named-hook `harness`, eventos `PreToolUse`/`PostToolUse`/`Stop`) traduzido por um driver de borda (`AntigravityHookBridge`) que delega aos serviços de domínio; stdin/stdout JSON camelCase. Origem: `src/adapters/antigravity/hook_bridge.py`, `src/core/install/antigravity_hooks.py`.

## Dívida / nota de manutenção

- O caminho do `command` no `hooks.json` é absoluto (gravado no init/upgrade). Se o repositório for movido sem rodar `upgrade`, os ganchos apontam para o caminho antigo. Mitigado por `upgrade`; documentado no onboarding.
- Premissas de runtime do Antigravity (estabilidade do `stepIdx` entre `PreToolUse`/`PostToolUse`; acesso ao `artifactDirectoryPath`) não foram verificáveis localmente (sem runtime do Antigravity). Cobertas por testes de contrato (fixtures), não por integração real.
