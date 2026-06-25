# Regression-watch: feature 009-hooks-antigravity

> Identificador: `009-hooks-antigravity`
> Data: `2026-06-24`
> Itens a vigiar em re-extrações e features futuras. Estado no fechamento: 🟢 verde.

| ID   | Item de vigilância                                                         | Como verificar                                                                                                                                               | Estado                  |
| ---- | -------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------- |
| W001 | Caminhos Claude/Gemini do `install-prompt` não regrediram                  | `test_install.py` (5 testes) verde; escopo do Claude (`.claude/settings.json`, `~/.claude`) vem de `apply_instructions()`                                    | 🟢                      |
| W002 | Pureza hexagonal: nenhum serviço de domínio ramificado por harness (RN-N5) | `grep -rn active_harness .harness/harness-core/src/core/{formatting,decisions}/` deve ser vazio; lógica do Antigravity só no adaptador/perfil/materializador | 🟢                      |
| W003 | Não-bloqueio do `agy-hook`                                                 | `test_cli.py::test_agy_hook_nonblocking_*` verde; `load_config` e construção do bridge dentro do try/except do ramo                                          | 🟢                      |
| W004 | Footprint zero do `materialize_hooks_json`                                 | `test_antigravity_hooks_materializer.py` (RecordingFileSystem) verde; nada escrito fora do `project_path`                                                    | 🟢                      |
| W005 | Merge por named-hook preserva chaves de terceiros (init e upgrade)         | Teste de merge com chave `outroPlugin` verde; init e upgrade usam a mesma rotina                                                                             | 🟢                      |
| W006 | `hooks.json` do Antigravity permanece JSON válido com `<ABS>` substituído  | `test_antigravity_profile.py` (parse) + materializer (sem `<ABS>` remanescente) verde                                                                        | 🟢                      |
| W007 | Round-trip de formatação por evento (`PreToolUse`→`PostToolUse`)           | Smoke CLI: `pre-tool-use` grava o mapa, `post-tool-use` formata o arquivo do `stepIdx`                                                                       | 🟢                      |
| W008 | Suíte completa verde                                                       | `.harness/harness-core/.venv/bin/python -m pytest -q` → 110 passed                                                                                           | 🟢                      |
| W009 | Premissa de runtime do Antigravity (não verificável local)                 | Validar contra o Antigravity real quando disponível: estabilidade do `stepIdx` entre Pre/PostToolUse e acesso ao `artifactDirectoryPath`                     | 🟡 (não testável agora) |

## Histórico de re-extrações

### Re-extração 2026-06-25 14:32

| ID   | Veredito   | Observação                                                                                                                                       |
| ---- | ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| W001 | 🟢 verde   | Caminhos Claude/Gemini do `install-prompt` preservados em `harness_profiles.py` (`apply_instructions`); inalterados por 011/012.                 |
| W002 | 🟢 verde   | Pureza hexagonal: `grep active_harness` em `core/{formatting,decisions}/` = vazio.                                                               |
| W003 | 🟢 verde   | Não-bloqueio do `agy-hook` coberto pela suíte (verde).                                                                                           |
| W004 | 🟢 verde   | Footprint do `materialize_hooks_json` coberto por `RecordingFileSystem` na suíte (verde).                                                        |
| W005 | 🟢 verde   | Merge por named-hook (init e upgrade) coberto pela suíte.                                                                                        |
| W006 | 🟢 verde   | `hooks.json` válido com `<ABS>` resolvido — coberto pela suíte.                                                                                  |
| W007 | 🟢 verde   | Round-trip `PreToolUse`→`PostToolUse` coberto pela suíte.                                                                                        |
| W008 | 🟢 verde   | Suíte completa verde: **149 passed em 3,07s** (era 130 após a 010; +19 de 011/012, sem regressão; bem abaixo do teto de 2 min).                  |
| W009 | 🟡 amarelo | Premissa de runtime do Antigravity (estabilidade do `stepIdx` Pre/PostToolUse, acesso ao `artifactDirectoryPath`) segue não testável localmente. |

### Re-extração 2026-06-24 19:30 (pós-feature 010)

| ID   | Veredito   | Observação                                                                                                                                                                                                         |
| ---- | ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| W001 | 🟢 verde   | Caminhos Claude/Gemini do `install-prompt` inalterados pela 010.                                                                                                                                                   |
| W002 | 🟢 verde   | Pureza hexagonal preservada: `grep active_harness` em `core/{formatting,decisions}` vazio; a 010 **não** ramificou domínio por harness — o materializador é incondicional e o perfil encapsula o artefato (RN-N5). |
| W003 | 🟢 verde   | Não-bloqueio do `agy-hook` inalterado.                                                                                                                                                                             |
| W004 | 🟢 verde   | Footprint do `materialize_hooks_json` inalterado.                                                                                                                                                                  |
| W005 | 🟢 verde   | Merge por named-hook (init e upgrade) inalterado.                                                                                                                                                                  |
| W006 | 🟢 verde   | `hooks.json` válido com `<ABS>` resolvido — inalterado.                                                                                                                                                            |
| W007 | 🟢 verde   | Round-trip de formatação por evento inalterado.                                                                                                                                                                    |
| W008 | 🟢 verde   | Suíte completa verde: **130 passed** (era 110; +20 da 010, sem regressão).                                                                                                                                         |
| W009 | 🟡 amarelo | Premissa de runtime do Antigravity segue não testável localmente; a 010 herda a mesma ressalva no comportamento do workflow.                                                                                       |

## Resumo

- Itens: 9 · Verde: 8 · Amarelo: 1 (W009, dependente de runtime do Antigravity indisponível localmente) · Vermelho: 0.
- Nenhuma regressão detectada no fechamento da feature.
