# Actions: Registro obrigatório de microdecisões via gancho de sessão

> Identificador: `022-hook-registro-decisoes`
> Data: `2026-07-15`
> Roadmap: `_reversa_forward/022-hook-registro-decisoes/roadmap.md`

## Resumo

| Métrica | Valor |
|---------|-------|
| Total de ações | 23 |
| Paralelizáveis (`[//]`) | 13 |
| Maior cadeia de dependência | 8 (T001 → T003 → T007 → T013 → T015 → T017 → T020 → T023) |

## Fase 1, Preparação

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T001 | Commitar o trabalho em curso da MD-0014 pendente no working tree (`claude_settings.py`, `harness_profiles.py`, testes, ADR 0002, snippet, `.claude/settings.json`, ficha MD-0014) em commit próprio — a 022 edita os mesmos arquivos (risco alto do `roadmap.md#9`) | - | - | working tree (vários) | 🟢 | `[X]` |
| T002 | Adicionar `require_registration: bool = True` a `DecisionsSection` (D-07; retrocompatível: tomls sem o campo herdam `True`, padrão da 021) | T001 | `[//]` | `.harness/harness-core/src/core/domain/config.py` | 🟢 | `[X]` |
| T003 | Adicionar campos opcionais `gate_lembrete_fingerprint`/`gate_encerramento_fingerprint` (`Optional[str] = None`) ao `SessionState` (D-03) | T001 | `[//]` | `.harness/harness-core/src/core/domain/models.py` | 🟢 | `[X]` |
| T004 | Adicionar `list_changed_paths_since(repo_path, ref)` à porta `GitPort`, implementar no `SubprocessGitAdapter` (`git diff --name-only <ref> HEAD`) e estender o `FakeGit` dos testes (D-02) | T001 | `[//]` | `.harness/harness-core/src/core/ports/git.py` + `src/adapters/git/subprocess.py` | 🟢 | `[X]` |

## Fase 2, Testes

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T005 | Teste (red) do parse do flag: `[decisions] require_registration=false` → `False`; campo ausente → `True`; seção ausente → `True` | T002 | `[//]` | `.harness/harness-core/tests/test_config.py` | 🟢 | `[X]` |
| T006 | Teste (red) do round-trip do serializer com os campos novos: `parse(render(x)) == x` com fingerprints presentes; YAML pré-022 (sem os campos) → `None` (RN-N2/RN-N4) | T003 | `[//]` | `.harness/harness-core/tests/` (arquivo de testes do serializer de sessão — localizar o existente) | 🟡 | `[X]` |
| T007 | Teste (red) de `evaluate_registration_gate` (novo `test_decision_gate.py`): (a) mudança sem ficha → pendente; (b) ficha `MD-*.md` no conjunto → não pendente; (c) só artefatos de estado do harness → não pendente; (d) mudança exclusivamente documental → pendente; (e) âncora ausente/ilegível → não pendente com aviso (fail-open); (f) fingerprint determinístico e sensível a mudança nova | T003, T004 | `[//]` | `.harness/harness-core/tests/test_decision_gate.py` (novo) | 🟢 | `[X]` |
| T008 | Teste (red) de `list_changed_paths_since` com **git real** (smoke, lição da 019): arquivo commitado após a âncora aparece; ref inválida → `RuntimeError`; repo sem commit tratado | T004 | `[//]` | `.harness/harness-core/tests/test_git_dirty.py` | 🟢 | `[X]` |
| T009 | Teste (red) do 3º portão no close flow: marker `DECISAO_PENDENTE` emitido (formato da `interfaces/decisao-pendente-marker.md`); `sem_decisao=True` anexa a linha padrão a "O que foi feito" e fecha; anti-loop (mesmo fingerprint → conclui com aviso); `require_registration=false` → sem gate; fingerprints zerados no fechamento | T007 | `[//]` | `.harness/harness-core/tests/test_close_flow.py` | 🟢 | `[X]` |
| T010 | Teste (red) de `decisions --gate` na CLI: 1ª pendência → stdout é **só** o JSON `{"decision":"block","reason":...}` e grava `gate_lembrete_fingerprint`; mesma pendência → stdout vazio; sem pendência → vazio; erro interno → vazio + stderr + exit 0; **sem** `--gate` → saída humana atual intocada (D-09, contrato da `interfaces/stop-gate-lembrete.md`) | T007 | `[//]` | `.harness/harness-core/tests/test_cli.py` | 🟡 | `[X]` |
| T011 | Teste (red) do perfil e do merge: `ClaudeProfile.hooks_block()` emite `Stop → harness decisions --gate` (e segue sem `PostToolUse`, pós-MD-0014); merge por-item substitui item `harness decisions` legado preservando itens alheios (D-08) | T001 | `[//]` | `.harness/harness-core/tests/test_harness_profiles.py` + `tests/test_install_claude_settings.py` | 🟢 | `[X]` |
| T012 | Teste (red) do advisory do Antigravity: `stop` com pendência → stdout exatamente `{}` + aviso em stderr; sem pendência → `{}` silencioso; falha na avaliação → `{}` + stderr (nunca bloqueia, RN-N26) | T007 | `[//]` | `.harness/harness-core/tests/` (arquivo de testes do hook bridge — localizar o existente `test_antigravity_*`) | 🟢 | `[X]` |

## Fase 3, Núcleo

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T013 | Implementar `core/decisions/gate.py`: `GateVerdict` (pydantic) + `evaluate_registration_gate(git, repo_path, session, config) -> GateVerdict` + fingerprint `sha1(âncora + HEAD + sorted(dirty))` — puro, sem I/O de saída, agnóstico ao harness (RN-N5). Torna T007 verde | T007 | - | `.harness/harness-core/src/core/decisions/gate.py` (novo) | 🟢 | `[X]` |
| T014 | Implementar o round-trip dos campos novos no serializer (render/parse do front-matter; ausente → `None`). Torna T006 verde | T006 | - | `.harness/harness-core/src/core/session/serializer.py` | 🟢 | `[X]` |
| T015 | Implementar o 3º portão no `SessionCloseFlow.run` (após o gate de narrativa): `render_decisao_pendente_marker`/`conduct_decisao_pendente` (dualidade TTY × marker), parâmetro `sem_decisao` (anexa linha padrão à narrativa antes de fechar), anti-loop via `gate_encerramento_fingerprint`, limpeza dos fingerprints no fechamento, gate por `require_registration`. Torna T009 verde | T009, T013, T014 | - | `.harness/harness-core/src/core/session/close_flow.py` | 🟢 | `[X]` |

## Fase 4, Integração

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T016 | Fiar `--gate` no subcomando `decisions` de `main.py` (D-04/D-09): avaliação via `evaluate_registration_gate`, soft-block JSON único no stdout, informativos para stderr, persistência de `gate_lembrete_fingerprint`, exit 0 sempre; sem a flag, byte-idêntico ao atual (MD-0006). Torna T010 verde | T010, T013, T014 | - | `.harness/harness-core/src/main.py` | 🟡 | `[X]` |
| T017 | Fiar `--sem-decisao` no ramo `cmd encerrar-sessao` de `main.py` (argparse → `SessionCloseFlow.run(sem_decisao=...)`) | T015 | - | `.harness/harness-core/src/main.py` | 🟢 | `[X]` |
| T018 | Atualizar `ClaudeProfile.hooks_block()` para `Stop → ${CLAUDE_PROJECT_DIR}/harness decisions --gate` e conferir/ajustar a assinatura do merge por-item para casar `harness decisions` com e sem flag (D-08). Torna T011 verde | T011, T016 | - | `.harness/harness-core/src/core/install/harness_profiles.py` + `src/core/install/claude_settings.py` | 🟢 | `[X]` |
| T019 | Advisory no Antigravity (D-06): `_handle_stop` do `AntigravityHookBridge` avalia o gate e loga pendência via `_log`; injeção de `git`/config no ramo `agy-hook` de `main.py`; stdout `{}` intocado. Torna T012 verde | T012, T013 | - | `.harness/harness-core/src/adapters/antigravity/hook_bridge.py` | 🟢 | `[X]` |
| T020 | Atualizar os assets da skill `encerrar-sessao`: `SKILL.md` documenta o marker `DECISAO_PENDENTE` e o protocolo (registrar ficha OU `--sem-decisao`); `scripts/encerrar_sessao.py` repassa `--sem-decisao` ao `SessionCloseFlow` | T015, T017 | - | `.harness/harness-core/src/core/install/assets/skills/encerrar-sessao/` | 🟢 | `[X]` |

## Fase 5, Polimento

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T021 | Regenerar `.claude/settings.json` e `.reversa/settings.json.snippet` deste repo a partir do perfil novo (lição da memória "upgrade regrava materializadores stale") | T018 | `[//]` | `.claude/settings.json` + `.reversa/settings.json.snippet` | 🟢 | `[X]` |
| T022 | Atualizar o `help` da CLI (`decisions --gate`, `encerrar-sessao --sem-decisao`) e conferir que o `doc-gen` (introspecção do argparse) reflete os textos novos | T016, T017 | `[//]` | `.harness/harness-core/src/main.py` | 🟢 | `[X]` |
| T023 | Verificação final: bump do core (2.0.1 → 2.1.0, contrato novo retrocompatível), suíte completa verde e **smoke real** dos cenários A–G do `onboarding.md` (bloqueio, ficha libera, escape registra, anti-loop, `--gate` JSON, advisory `{}`, opt-out) | T015, T016, T017, T018, T019, T020, T021, T022 | - | `.harness/harness-core/` + manual | 🟢 | `[X]` |

## Notas de execução

<!-- Reservado para /reversa-coding. -->

## Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-07-15 | Versão inicial gerada por `/reversa-to-do` | reversa |
