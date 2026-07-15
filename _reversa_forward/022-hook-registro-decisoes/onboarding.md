# Onboarding — 022-hook-registro-decisoes

> Passo a passo executável para um humano testar o gate de registro pela primeira vez. Pré-requisito: suíte verde (`cd .harness/harness-core && .venv/bin/python -m pytest`).

## Cenário A — bloqueio no encerramento deliberado

1. Na raiz do repo, garanta sessão ativa: `./harness cmd resume`
2. Faça uma mudança substantiva e commite-a (qualquer arquivo serve — código **ou** documento):
   `echo "teste gate" >> tmp-gate-teste.md && git add tmp-gate-teste.md && git commit -m "teste: mudança substantiva sem ficha"`
3. Atualize a narrativa da sessão (edite as 4 seções de `.harness/estado-da-sessao.md`) para passar o gate de narrativa.
4. Rode `./harness cmd encerrar-sessao` **sem TTY** (ex.: `echo | ./harness cmd encerrar-sessao`).
5. **Esperado:** marker `[HARNESS:DECISAO_PENDENTE ...]` no stdout, sessão permanece ativa, exit 0.

## Cenário B — ficha registrada libera

1. Ainda na pendência do cenário A, crie uma ficha válida `.harness/decisoes/MD-9999.md` (front-matter `id/gancho/estado/relacoes` + H1 + 4 seções `D/PORQUÊ/DESCARTADO/ESTADO`) e commite-a.
2. Re-rode o encerramento.
3. **Esperado:** encerramento conclui (commit de registro por cima), sem marker de decisão.

## Cenário C — escape auditável

1. Repita o cenário A (nova mudança, sem ficha).
2. Rode `./harness cmd encerrar-sessao --sem-decisao`.
3. **Esperado:** encerramento conclui; `.harness/estado-da-sessao.md` (no commit de registro) contém a linha `Declarado: sem decisão não óbvia nesta sessão (gate de registro).` na seção "O que foi feito".

## Cenário D — anti-loop

1. Repita o cenário A até receber o marker (1º bloqueio).
2. Re-rode o encerramento **sem mudar nada** (mesma pendência).
3. **Esperado:** encerramento conclui com aviso de pendência não sanada em `stderr` (2ª tentativa nunca re-bloqueia).

## Cenário E — lembrete no `Stop` do Claude

1. Com sessão ativa e mudança suja no working tree (não commitada), sem ficha nova:
   `echo "" | ./harness decisions --gate`
2. **Esperado:** stdout contém **apenas** JSON `{"decision": "block", "reason": "[HARNESS:DECISAO_PENDENTE ..."}`; informativos em stderr.
3. Rode de novo, sem mudar nada.
4. **Esperado:** stdout vazio (ou sem bloqueio) — mesmo fingerprint não lembra duas vezes.
5. Confira o comportamento sem a flag: `./harness decisions` → saída humana atual, byte-idêntica ao pré-022 (contrato do git post-merge, MD-0006).

## Cenário F — advisory do Antigravity

1. Simule o evento: `echo '{"artifactDirectoryPath": "/tmp"}' | ./harness agy-hook stop`
2. **Esperado:** stdout exatamente `{}`; se houver pendência, aviso `[harness agy-hook] ...` em stderr. Nunca bloqueia.

## Cenário G — opt-out por configuração

1. No `harness.toml`, adicione `require_registration = false` sob `[decisions]`.
2. Repita o cenário A.
3. **Esperado:** comportamento pré-022 (nenhum marker de decisão).
4. Remova a linha ao terminar.

## Limpeza

`git rm tmp-gate-teste.md .harness/decisoes/MD-9999.md && git commit -m "teste: limpeza do onboarding 022"` e re-rode `./harness decisions` para reindexar.
