# Evidência: estado de sessão espúrio semeado dentro do harness-core

Observado em 2026-08-11, ~17:54 (hora local), durante a sessão de correção do
BUG-20260811-XZ3B. Após um compact do Claude Code (que dispara o SessionStart
desde a MD-0024), apareceu no `git status` a entrada não rastreada
`.harness/harness-core/.harness/`.

Conteúdo integral do arquivo espúrio
`/Users/iagoleal/dev/harness/.harness/harness-core/.harness/estado-da-sessao.md`
(227 bytes, mtime 11 ago 17:54), removido após a coleta:

```
---
commit: 45251f55a9a876c42440577f43cfbfb623a4b96d
feature: default_feature
start_time: '2026-08-11T20:54:49.501149+00:00'
status: active
---

## O que foi feito

## Próximos passos

## Pendências / bloqueios

## Ponteiros
```

O `commit` registrado é o HEAD do repositório no momento (45251f5), e o
`start_time` (20:54 UTC = 17:54 local) coincide com o compact da sessão. O cwd
do shell da sessão estava em `.harness/harness-core/` (execuções de pytest);
o hook herdou esse cwd e o `cmd resume` semeou o estado ali.
