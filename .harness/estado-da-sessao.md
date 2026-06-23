---
commit: c5482239f5127fb4fb1737c160bd5b2a2b5b5c6b
feature: 005-decisoes-em-harness
start_time: '2026-06-23T23:51:13.646363+00:00'
status: active
---

## O que foi feito
- Feature 005 (decisões em `.harness/`) CODADA, testada (55 verde) e empurrada — commit `c548223`. `decisoes/`→`.harness/decisoes/` e `microdecisoes.md`→`.harness/microdecisoes.md` via `git mv` (histórico preservado); CLI (`main.py`) e MCP (`server.py`) leem os 3 caminhos de `load_config().decisions` (fonte única, D-01=B).
- Bugs latentes mortos no caminho: `load_config` sem imports (`toml`/`FileSystemPort`) e import lazy que causava `UnboundLocalError`; de brinde conserta o `install-prompt`.
- Removida a sincronização cross-harness Claude↔Gemini (scripts de ponte/bastão em `~/.agent-memory`; fiação no `~/.claude` e `~/.gemini`) — MD-0004; conteúdo de memória preservado. Decisão do mantenedor, destrutiva e autorizada.
- Commits desta sessão: `c0f7402` (CLAUDE.md global), `b2df06a` (spec 005), `ea96656` (MD-0004), `c548223` (implementação 005). Harness, `~/.claude` e `~/.agent-memory` em sincronia com o remoto.

## Próximos passos
- (Opcional) `/reversa` re-extração para fechar o loop reversa e atualizar o `regression-watch` (W001–W004) da 005.
- Feature nova pendente: "harness-core como config canônica" (substituto do `~/.claude`). A Q2 (mecanismo de substituição) ficou para decidir depois; nela entram os scripts globais de decisão a reconhecerem `.harness/` (RF-04, diferido da 005).

## Pendências / bloqueios
- Bug latente pré-existente: `json` não importado em `harness-core/src/main.py` (`resolve_format_target`). Fora do escopo; corrigir à parte.
- Nuance de cwd: a seção `[decisions]` do `harness.toml` só é lida com cwd=`harness-core`; o wrapper roda da raiz e usa os defaults do `config.py` (corretos na invocação real).
- Premissa aberta da 004: gatilho de boot do Antigravity (`agy`) — validar.

## Ponteiros
- _reversa_forward/005-decisoes-em-harness/ (requirements, roadmap, actions, legacy-impact, regression-watch)
- .harness/decisoes/MD-0004.md
- .harness/microdecisoes.md
