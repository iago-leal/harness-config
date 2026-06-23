# Actions: Estado de sessão unificado em `.harness/` com reinjeção de contexto

> Identificador: `004-estado-sessao-unificado`
> Data: `2026-06-23`
> Roadmap: `_reversa_forward/004-estado-sessao-unificado/roadmap.md`

## Resumo

| Métrica | Valor |
|---------|-------|
| Total de ações | 17 |
| Paralelizáveis (`[//]`) | 9 |
| Maior cadeia de dependência | 8 (T002→T004→T007→T009→T011→T012→T013→T017) |

## Fase 1, Preparação

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T001 | Esqueleto do pacote `core/session/`: `__init__.py`, `serializer.py` (assinaturas `parse`/`render`), `sinks.py` (interface `SessionSink` + stubs `HookContextSink`/`FileProjectionSink`), `errors.py` (`MalformedSessionStateError`) | - | `[//]` | `harness-core/src/core/session/` | 🟢 | `[X]` |
| T002 | Domínio: criar value-object `SessionNarrative` (pydantic; feito/próximos/pendências/ponteiros) e adicionar `narrative: Optional[SessionNarrative]` em `SessionState` | - | `[//]` | `harness-core/src/core/domain/models.py` | 🟢 | `[X]` |

## Fase 2, Testes

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T003 | Testes do `SessionNarrative` (construção, campos opcionais, narrativa parcial) | T002 | `[//]` | `harness-core/tests/test_domain.py` | 🟢 | `[X]` |
| T004 | Testes do serializer: round-trip `parse(render(x)) == x` (com e sem narrativa) e parse barulhento (ausente → sessão nova; presente-malformado → `MalformedSessionStateError`) | T001, T002 | `[//]` | `harness-core/tests/test_session.py` | 🟢 | `[X]` |
| T005 | Testes dos sinks: `HookContextSink` emite JSON `hookSpecificOutput.additionalContext` válido e isolado; `FileProjectionSink` escreve o arquivo de projeção | T001 | `[//]` | `harness-core/tests/test_session_sinks.py` | 🟢 | `[X]` |
| T006 | Testes do `CommandService`: `resume` entrega via sink (sem status solto no stdout) e `encerrar-sessao` sela o header via `GitPort` preservando a regra de repo limpo | T002 | `[//]` | `harness-core/tests/test_commands.py` | 🟢 | `[X]` |

## Fase 3, Núcleo

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T007 | Implementar `serializer.parse/render`: front-matter YAML (`pyyaml`) + corpo em seções `##`; round-trip; erro nomeado `MalformedSessionStateError` para front-matter inválido | T001, T002, T004 | - | `harness-core/src/core/session/serializer.py` | 🟢 | `[X]` |
| T008 | Implementar os sinks: `HookContextSink` (JSON `hookSpecificOutput.additionalContext` no stdout, logs a stderr, trunca >10.000 chars com aviso) e `FileProjectionSink` (escreve `.agents/rules/estado-sessao.md`) | T001, T005, T007 | - | `harness-core/src/core/session/sinks.py` | 🟢 | `[X]` |
| T009 | Refatorar `CommandService.load_session/save_session` para usar o serializer (round-trip), recebendo o caminho do arquivo | T007 | - | `harness-core/src/core/commands/service.py` | 🟢 | `[X]` |
| T010 | Branch `encerrar-sessao` no `CommandService`: sela o header-máquina via `GitPort`, valida repo limpo, preserva a narrativa já escrita pelo agente | T009 | - | `harness-core/src/core/commands/service.py` | 🟢 | `[X]` |
| T011 | Branch `resume` no `CommandService`: ao final, entrega o estado via sink injetado (família por harness), em vez de imprimir status | T009, T008 | - | `harness-core/src/core/commands/service.py` | 🟢 | `[X]` |

## Fase 4, Integração

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T012 | `main.py`: resolver `active_harness`, selecionar o sink, apontar `session_file` para `.harness/estado-da-sessao.md`, fiar `cmd resume` e `cmd encerrar-sessao` à nova orquestração | T011, T008, T006 | - | `harness-core/src/main.py` | 🟢 | `[X]` |
| T013 | Migração one-shot: criar `.harness/estado-da-sessao.md` a partir da narrativa de `.claude/ESTADO-DA-SESSAO.md`; `git rm` do antigo; remover o `ESTADO-DA-SESSAO.md` da raiz | T012 | - | `.harness/estado-da-sessao.md` | 🟢 | `[X]` |
| T014 | Gatilho do Gemini: criar/editar `.gemini/settings.json` com hook `SessionStart` → `./harness cmd resume` | T012 | `[//]` | `.gemini/settings.json` | 🟡 | `[X]` |
| T015 | Antigravity: garantir a projeção `.agents/rules/estado-sessao.md` (via `FileProjectionSink`) e validar/instalar o hook de pré-invocação do `agy` (teste de fumaça; fallback passivo) | T012 | `[//]` | `.agents/rules/estado-sessao.md` | 🟡 | `[X]` |

## Fase 5, Polimento

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T016 | Ajustar help/mensagens do `resume`/`encerrar-sessao` no parser (argparse): distinguir "concluído" de "pendência conhecida", sem poluir o stdout do hook | T012 | - | `harness-core/src/main.py` | 🟢 | `[X]` |
| T017 | Teste de fumaça do boot real conforme `onboarding.md` nos harnesses disponíveis; registrar o resultado (entra no `regression-watch.md` do coding) | T013, T014, T015 | `[//]` | `_reversa_forward/004-estado-sessao-unificado/onboarding.md` | 🟡 | `[X]` |

## Notas de execução

- Suíte: **52 testes verdes** (41 baseline + 11 novos). Núcleo coberto por TDD (round-trip `parse∘render`, parse barulhento, sinks).
- O formatador PostToolUse (`ruff`) removeu imports ainda-não-usados entre edits; readicionados após o uso (gotcha registrado para a próxima sessão).
- **Smoke test do dogfooding:** `./harness cmd resume` valida — emite só JSON `hookSpecificOutput.additionalContext` (exit 0, 1162 chars, stderr limpo) e preserva a narrativa no round-trip.
- **T017 parcial:** boot validado no Claude (harness ativo). Gemini 0.47.0 (≥ 0.25 ✓) e `agy` presentes, mas o boot vivo de cada um exige sessão interativa — verificação manual pelo `onboarding.md`.
- Bug latente pré-existente fora do escopo: `json` não importado em `main.py` (`resolve_format_target`). Sinalizado no `legacy-impact.md`.

## Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-06-23 | Versão inicial gerada por `/reversa-to-do` | reversa |
