# Comandos Customizados (Commands) — Tarefas de Implementação

> Regenerado pelo Writer em 2026-06-24 (Re-extração após a feature 004)
> Sequência executável para reimplementar a unit a partir do legado, com rastreabilidade ao código original.

> ⚠️ Reescrita: a unit agora é o `CommandService` Python (`harness-core`), não os arquivos Markdown legados `commands/*.md` (purgados). Estado em `.harness/estado-da-sessao.md`; sem `~/.agent-memory/BASTAO.md`.

## Pré-requisitos

- [ ] `GitPort` / `FileSystemPort` disponíveis.
- [ ] `core/session/{serializer,sinks,errors}` implementados (unit `session`).
- [ ] `SessionState` / `SessionNarrative` em `core/domain/models.py`.

## Tarefas

- [ ] T-01, Implementar `load_session` / `save_session`
  - Origem no legado: `core/commands/service.py`
  - Critério de pronto: ausente → `None`; malformado → `MalformedSessionStateError`; `save` via `serializer.render` + gravação atômica.
  - Confiança: 🟢

- [ ] T-02, Implementar `resume`
  - Origem no legado: `core/commands/service.py`
  - Critério de pronto: cria sessão nova com HEAD/feature; reativa preservando a narrativa; alerta `⚠️` se HEAD ≠ âncora; retorna a narrativa reinjetada.
  - Confiança: 🟢

- [ ] T-03, Implementar `encerrar-sessao`
  - Origem no legado: `core/commands/service.py`
  - Critério de pronto: exige sessão ativa; `close_session(commit)` com HEAD; salva atomicamente.
  - Confiança: 🟢

- [ ] T-04, Implementar `handoff` e `clarificar`
  - Origem no legado: `core/commands/service.py`
  - Critério de pronto: `handoff` monta bloco com feature+HEAD; `clarificar` retorna texto fixo (limite 2 rodadas).
  - Confiança: 🟢

- [ ] T-05, Despacho e comando desconhecido
  - Origem no legado: `core/commands/service.py`
  - Critério de pronto: normaliza comando; desconhecido → `"Comando desconhecido: <command>"`.
  - Confiança: 🟢

- [ ] T-06, Integrar no driver CLI (`cmd`) com sink
  - Origem no legado: `src/main.py`
  - Critério de pronto: usa `.harness/estado-da-sessao.md`; resolve o sink por `active_harness` (RN-N5); hook `SessionStart`→`cmd resume`.
  - Confiança: 🟢

- [x] T-07, Implementar `SessionCloseFlow` com pré-check restrito ao estado (✨f018/f019)
  - Origem no legado: `core/session/close_flow.py` (`pending_work_paths`, `narrative_is_stale`, `conduct_commit_pendente`, `conduct_narrativa_pendente`, `SessionCloseFlow.run`)
  - Critério de pronto: `pending_work_paths` exclui só `session_file`; gate de narrativa recusa fechar se vazia/idêntica à âncora; ambos abortam com marker (sem TTY) ou prompt (TTY) sem chamar `execute_command`; `main.py` delega a `SessionCloseFlow(...).run(...)` em vez de chamar `execute_command("encerrar-sessao")` direto.
  - Confiança: 🟢 (já implementado no legado; tarefa registrada para reconstrução fiel)

- [x] T-08, Implementar `build_decisions_appendix` e a fiação do `resume` (✨f021)
  - Origem no legado: `core/session/resume_context.py`, ramo `cmd resume` de `src/main.py`, `SessionSection.inject_decisions_index`
  - Critério de pronto: função pura recebe `enabled` já calculado; `main.py` computa `enabled = active_harness == "claude" and session.inject_decisions_index` e concatena o apêndice ao `result_msg` do resume, depois do estado; índice ausente/vazio/gate off → sem apêndice, sem erro.
  - Confiança: 🟢 (já implementado no legado; tarefa registrada para reconstrução fiel)

## Tarefas de Teste

- [ ] TT-01, `resume` sem estado cria sessão; com estado reativa preservando narrativa.
- [ ] TT-02, Divergência de âncora antecede alerta `⚠️`.
- [ ] TT-03, `encerrar-sessao` sem sessão ativa → erro; com sessão ativa grava âncora.
- [ ] TT-04, Estado malformado → `MalformedSessionStateError`.
- [ ] TT-05, Trabalho sujo em `.harness/decisoes/` (não o `session_file`) → `encerrar-sessao` aborta com marker/prompt de pendência, sessão permanece ATIVA.
- [ ] TT-06, Narrativa vazia ou idêntica à da âncora de partida → `encerrar-sessao` aborta com marker/prompt de narrativa, sessão permanece ATIVA.
- [ ] TT-07, `resume` com Claude + flag ligado + índice não-vazio → texto reinjetado contém o apêndice após o estado.
- [ ] TT-08, `resume` com Gemini (ou índice ausente) → texto reinjetado não contém apêndice, sem erro.

## Ordem Sugerida

1. T-01 (load/save) primeiro — base dos demais.
2. T-02/T-03 (resume/encerrar) antes de T-04/T-05.
3. T-06 fecha a integração CLI + sink.
4. T-07 envolve T-03 com os portões de pré-check (depende de `GitPort.list_dirty_paths`/`get_file_at_ref`).
5. T-08 estende T-02, depois de T-06 (a fiação vive no mesmo ramo `cmd resume` de `main.py`).

## Lacunas Pendentes (🔴)

- Nenhuma 🔴. 🟢 **T2 resolvido (feature 006):** o caminho divergente CLI×MCP do estado de sessão foi fechado — ambos os drivers leem `session_file` de `config.session.state_file`. Não há mais ressalva pendente nesta unit.
