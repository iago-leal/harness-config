---
name: ritual-de-encerramento-de-sessao
description: "Encerrar sessão neste projeto: commit, push e /encerrar-sessao do harness, de uma vez, sem perguntar a cada passo; o vault Obsidian está FORA do ritual (MD-0021)."
metadata:
  node_type: memory
  type: feedback
  originSessionId: 99b3ca7e-b0cd-4c62-8696-b371eac0fd46
  modified: 2026-08-11T00:00:00.000Z
---

Quando o usuário pede para encerrar a sessão deste projeto, ele espera a cadeia inteira executada de
uma vez: commit do trabalho, `git push origin main` (o trabalho vai direto em `main`) e o fluxo de
encerramento do harness, que está **reinstalado** neste projeto (layout fonte única, commit
`3ff3f3f9`; skill `/encerrar-sessao` materializada em `.claude/skills/`, estado em
`.harness/estado-da-sessao.md`, gates de narrativa e de registro de decisões ativos).

**A atualização da nota do vault Obsidian NÃO faz mais parte do ritual**: abandonada pela decisão
MD-0021 do harness (2026-08-11). Não atualize `Projetos/comentarios-concursos.md` nem faça commit no
`~/Notas` ao encerrar, salvo pedido explícito. Se um dia precisar tocar o vault: o remoto chama-se
**`origin`** (aponta para `iago-leal/notas-obsidian`; `git push notas-obsidian` falha, porque esse é
o nome do repositório, não do remoto).

**Why:** o Princípio nº 1 dele é "executar, não delegar", e a instrução de encerramento costuma vir
composta ("commit, push e encerre"). Parar para confirmar cada etapa que a própria frase já autorizou
é fricção, não cuidado. A versão anterior desta memória (2026-08-02) dizia que o harness fora
desinstalado e prescrevia a nota do vault; ambas as afirmações ficaram stale e causaram um
encerramento errado em 2026-08-11 (BUG-20260811-OYKV no repo do harness).

**How to apply:** commit do trabalho → push → `/encerrar-sessao` (ou
`./harness cmd encerrar-sessao`), atendendo aos gates que o fluxo emitir. Sem vault. O registro de
decisões do projeto vive em `.harness/decisoes/` (microdecisões) e `_reversa_sdd/adrs/`. Ver
[[gemeo-ipm-e-referencia-autoritativa]].
