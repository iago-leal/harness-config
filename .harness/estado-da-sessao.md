---
commit: cf739806a360469b3f0d9080883e037dc36a1a0e
feature: 005-decisoes-em-harness
start_time: "2026-06-23T23:55:46.960785+00:00"
status: active
---

## O que foi feito

- **Re-extração reversa completa** (`/reversa`, Scout→Reviewer) refletindo as features 003/004/005 e o purge do `claude-config/`. Documentados os módulos novos `install/` (f003) e `session/` (f004); ADRs **0009–0012**; C4, ERD e specs migrados para `.harness/decisoes/`, `.harness/microdecisoes.md` e `.harness/estado-da-sessao.md`. Confiança do Reviewer ~85% (~76% 🟢). Commit `2646941` (empurrado).
- **Verificação de regressão** (step-04) dos 5 `regression-watch.md`: 14 watch items — **11 🟢, 2 🟡, 1 🔴**. Bloco de histórico `2026-06-23 21:58` gravado em cada arquivo (só a seção de histórico).
- **Três bugs de driver, detectados pelo regression-check e corrigidos** (commit `cf73980`, empurrado): **T1** — `adapters/mcp/server.py` chamava `load_config` sem importar, deixando o tool MCP de decisões inoperante (`NameError`); **T2** — `session_command` apontava para `ESTADO-DA-SESSAO.md` na raiz, divergente da CLI, corrigido para `.harness/estado-da-sessao.md`; **T3** — `json` não importado em `main.py`, quebrando `resolve_format_target` no hook `PostToolUse` (autoformat nunca rodava). 55 testes verdes + smoke tests dos três caminhos.

## Próximos passos

- A próxima `/reversa` deve marcar **005/W003, 004/W002 e 003/W003** como verdes — os bugs que os motivaram já estão corrigidos em `cf73980`.
- Decidir o destino dos artefatos obsoletos: `_reversa_sdd/flowcharts/*` e `_reversa_sdd/user-stories/fluxo-de-sincronia-e-sessao.md` ainda descrevem o legado purgado (questão Q5 do Reviewer em `_reversa_sdd/questions.md`). Opções: regenerar, marcar como históricos ou remover.
- Feature nova pendente: **"harness-core como config canônica"** (substituto do `~/.claude`), absorvendo o RF-04 diferido da 005. Q2 (mecanismo de substituição) em aberto.

## Pendências / bloqueios

- **001/W001–W003** acumulam 3 vereditos verdes consecutivos (limiar `archive-after=3`): candidatos a arquivamento. O Reversa não move a tabela principal; ação manual do mantenedor.
- Inconsistência menor não corrigida: no MCP, `process_decisions` deriva `header_file` de `os.path.join(dir, "_cabecalho.md")` e ignora o override `config.decisions.header_file`. Fora do escopo dos 3 bugs.
- Premissa aberta da 004: gatilho de boot do Antigravity (`agy`) — validar.

## Ponteiros

- Commits desta sessão: `2646941` (re-extração + regression-check), `cf73980` (fix T1/T2/T3). Ambos em `main`, empurrados.
- `_reversa_forward/*/regression-watch.md` — histórico de re-extração `2026-06-23 21:58`.
- `_reversa_sdd/confidence-report.md`, `gaps.md`, `questions.md` (Reviewer).
- `_reversa_sdd/install/`, `_reversa_sdd/session/`, `_reversa_sdd/adrs/0009-0012`.
