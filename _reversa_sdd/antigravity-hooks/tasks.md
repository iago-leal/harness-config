# Antigravity Hooks (Driver de Ganchos do Antigravity) — Tarefas de Implementação

> Gerado pelo Archaeologist em 2026-06-24 15:19 (Re-extração após a feature 009-hooks-antigravity). Âncora (HEAD): `e30b9a6`.
> Sequência executável para reimplementar a unit a partir do legado, com rastreabilidade ao código original.

## Pré-requisitos

- [ ] `FileSystemPort` disponível (`core/ports/fs.py`), com `read_file`, `write_file_atomic`, `exists`, `makedirs`.
- [ ] `FormattingService` e `DecisionService` disponíveis (reusados, agnósticos ao harness).
- [ ] `AntigravityProfile` (`core/install/harness_profiles.py`) emitindo o named-hook `harness`.

## Tarefas

- [ ] T-01, Definir `AntigravityHookBridge.__init__` com injeção
  - Origem no legado: `adapters/antigravity/hook_bridge.py`
  - Critério de pronto: recebe `fs`, `formatting_service`, `decision_service`, `decisions_dir`, `decisions_index_file`, `decisions_header_file`; nenhuma instanciação concreta no adaptador.
  - Confiança: 🟢

- [ ] T-02, Implementar o despacho `handle(event, stdin_text)` não-bloqueante
  - Origem no legado: `adapters/antigravity/hook_bridge.py`
  - Critério de pronto: roteia `pre-tool-use`/`post-tool-use`/`stop` via `_safe`; evento desconhecido loga e retorna `{}`; nunca levanta.
  - Confiança: 🟢

- [ ] T-03, Handler `PreToolUse` (captura `stepIdx → TargetFile`)
  - Origem no legado: `adapters/antigravity/hook_bridge.py` (`_handle_pre_tool_use`)
  - Critério de pronto: grava `{ "<stepIdx>": "<TargetFile>" }` no scratch quando ambos presentes; retorna `{"decision": "allow"}`.
  - Confiança: 🟢

- [ ] T-04, Handler `PostToolUse` (formatação por `stepIdx`)
  - Origem no legado: `adapters/antigravity/hook_bridge.py` (`_handle_post_tool_use`)
  - Critério de pronto: com `stepIdx` presente, `error` vazio e scratch existente, resolve o caminho e chama `format_file`; retorna `{}`.
  - Confiança: 🟢

- [ ] T-05, Handler `Stop` (validação + indexação de decisões)
  - Origem no legado: `adapters/antigravity/hook_bridge.py` (`_handle_stop`)
  - Critério de pronto: `load_decisions` + `validate_integrity` (erros logados, não bloqueiam) + `compile_index`; retorna `{}` (nunca `"continue"`).
  - Confiança: 🟢

- [ ] T-06, Scratch do mapa (`_scratch_path`/`_read_map`/`_write_map`)
  - Origem no legado: `adapters/antigravity/hook_bridge.py`
  - Critério de pronto: caminho `<artifactDirectoryPath>/.harness-agy/pending-format.json`; leitura tolerante (ausência/JSON inválido → `{}`); escrita atômica com `makedirs`.
  - Confiança: 🟢

- [ ] T-07, Blindagem não-bloqueante (`_safe`/`_log`)
  - Origem no legado: `adapters/antigravity/hook_bridge.py`
  - Critério de pronto: toda exceção do handler é capturada, logada em stderr e o `fallback` do evento é emitido; stdout reservado ao contrato.
  - Confiança: 🟢

- [ ] T-08, `AntigravityProfile.hooks_block` / `apply_instructions`
  - Origem no legado: `core/install/harness_profiles.py`
  - Critério de pronto: `hooks_block()` emite o named-hook `harness` (Pre/Post com `WRITE_MATCHER`, Stop sem matcher, comandos `<ABS>/harness agy-hook ...`, timeouts 10/30/10); `apply_instructions()` aponta o `.agents/hooks.json` do projeto.
  - Confiança: 🟢

- [ ] T-09, `materialize_hooks_json` com merge por named-hook
  - Origem no legado: `core/install/antigravity_hooks.py`
  - Critério de pronto: resolve `<ABS>` para `command_path`, extrai o named-hook `harness`, lê o `hooks.json` existente, substitui só `harness`, grava atomicamente sob `<project>/.agents/`.
  - Confiança: 🟢

- [ ] T-10, Subcomando `agy-hook` na CLI (borda)
  - Origem no legado: `src/main.py`
  - Critério de pronto: aceita `pre-tool-use`/`post-tool-use`/`stop`; `fallback` pré-computado a partir de `args.event` antes de qualquer I/O; todo o ramo sob try/except; exit 0; `agy-hook` na exceção do config global e do check de sync.
  - Confiança: 🟢

- [ ] T-11, Integração com `init`/`upgrade`
  - Origem no legado: `src/core/bootstrap/init_service.py`
  - Critério de pronto: `initialize_project`/`upgrade_project` chamam `materialize_hooks_json` quando `active_harness == "antigravity"`, com `command_path = os.path.abspath(target_path)`.
  - Confiança: 🟢

## Tarefas de Teste

- [ ] TT-01, `PreToolUse`: payload com `stepIdx`/`TargetFile` grava o scratch e emite `{"decision": "allow"}`.
- [ ] TT-02, `PostToolUse`: `stepIdx` mapeado e `error` vazio dispara `format_file` e emite `{}`.
- [ ] TT-03, `Stop`: valida e recompila o índice e emite `{}` (sem `"continue"`).
- [ ] TT-04, Resiliência: config corrompida/stdin ilegível/exceção no handler ainda emitem o stdout exigido e exit 0.
- [ ] TT-05, Materialização: `init --harness antigravity` escreve `.agents/hooks.json` válido, preserva chaves de terceiros e não escreve fora do repo (footprint).
- [ ] TT-06, Não-regressão: caminhos Claude/Gemini permanecem verdes.

## Ordem Sugerida

1. T-01/T-06 (esqueleto + scratch) e T-08 (perfil) primeiro.
2. T-03/T-04/T-05 (handlers) sobre o esqueleto; T-07 (blindagem) envolve tudo; T-02 (despacho) fecha o adaptador.
3. T-09 (materialização) e T-10/T-11 (CLI + init/upgrade) integram a borda.

## Lacunas Pendentes (🔴)

- Nenhuma 🔴. Ressalva 🟡: as premissas de runtime do Antigravity (estabilidade do `stepIdx` entre eventos; acesso ao `artifactDirectoryPath`) são cobertas por testes de fixtures, não por integração real. Suíte de 110 testes verde no HEAD `e30b9a6`.
