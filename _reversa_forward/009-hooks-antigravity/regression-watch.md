# Regression-watch: feature 009-hooks-antigravity

> Identificador: `009-hooks-antigravity`
> Data: `2026-06-24`
> Itens a vigiar em re-extrações e features futuras. Estado no fechamento: 🟢 verde.

| ID   | Item de vigilância                                                         | Como verificar                                                                                                                                      | Estado                  |
| ---- | -------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------- |
| W001 | Caminhos Claude/Gemini do `install-prompt` não regrediram                  | `test_install.py` (5 testes) verde; escopo do Claude (`.claude/settings.json`, `~/.claude`) vem de `apply_instructions()`                           | 🟢                      |
| W002 | Pureza hexagonal: nenhum serviço de domínio ramificado por harness (RN-N5) | `grep -rn active_harness harness-core/src/core/{formatting,decisions}/` deve ser vazio; lógica do Antigravity só no adaptador/perfil/materializador | 🟢                      |
| W003 | Não-bloqueio do `agy-hook`                                                 | `test_cli.py::test_agy_hook_nonblocking_*` verde; `load_config` e construção do bridge dentro do try/except do ramo                                 | 🟢                      |
| W004 | Footprint zero do `materialize_hooks_json`                                 | `test_antigravity_hooks_materializer.py` (RecordingFileSystem) verde; nada escrito fora do `project_path`                                           | 🟢                      |
| W005 | Merge por named-hook preserva chaves de terceiros (init e upgrade)         | Teste de merge com chave `outroPlugin` verde; init e upgrade usam a mesma rotina                                                                    | 🟢                      |
| W006 | `hooks.json` do Antigravity permanece JSON válido com `<ABS>` substituído  | `test_antigravity_profile.py` (parse) + materializer (sem `<ABS>` remanescente) verde                                                               | 🟢                      |
| W007 | Round-trip de formatação por evento (`PreToolUse`→`PostToolUse`)           | Smoke CLI: `pre-tool-use` grava o mapa, `post-tool-use` formata o arquivo do `stepIdx`                                                              | 🟢                      |
| W008 | Suíte completa verde                                                       | `harness-core/.venv/bin/python -m pytest -q` → 110 passed                                                                                           | 🟢                      |
| W009 | Premissa de runtime do Antigravity (não verificável local)                 | Validar contra o Antigravity real quando disponível: estabilidade do `stepIdx` entre Pre/PostToolUse e acesso ao `artifactDirectoryPath`            | 🟡 (não testável agora) |

## Resumo

- Itens: 9 · Verde: 8 · Amarelo: 1 (W009, dependente de runtime do Antigravity indisponível localmente) · Vermelho: 0.
- Nenhuma regressão detectada no fechamento da feature.
