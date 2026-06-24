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

## Tarefas de Teste

- [ ] TT-01, `resume` sem estado cria sessão; com estado reativa preservando narrativa.
- [ ] TT-02, Divergência de âncora antecede alerta `⚠️`.
- [ ] TT-03, `encerrar-sessao` sem sessão ativa → erro; com sessão ativa grava âncora.
- [ ] TT-04, Estado malformado → `MalformedSessionStateError`.

## Ordem Sugerida

1. T-01 (load/save) primeiro — base dos demais.
2. T-02/T-03 (resume/encerrar) antes de T-04/T-05.
3. T-06 fecha a integração CLI + sink.

## Lacunas Pendentes (🔴)

- Nenhuma 🔴. Ressalva 🟡: **T2** — caminho divergente CLI×MCP do estado de sessão. Bug latente documentado, não corrigido aqui.
