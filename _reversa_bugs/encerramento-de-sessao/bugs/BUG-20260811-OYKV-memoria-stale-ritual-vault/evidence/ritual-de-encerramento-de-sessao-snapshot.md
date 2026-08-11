# Snapshot em 2026-08-11 de ~/.claude/projects/-Users-iagoleal-dev-comentarios-concursos/memory/ritual-de-encerramento-de-sessao.md

---
name: ritual-de-encerramento-de-sessao
description: "Ao pedir para encerrar, o usuário espera a sequência completa commit → push → nota do vault executada de uma vez, sem perguntar a cada passo."
metadata:
  node_type: memory
  type: feedback
  originSessionId: 99b3ca7e-b0cd-4c62-8696-b371eac0fd46
  modified: 2026-08-02T16:43:52.086Z
---

Quando o usuário pede para encerrar a sessão deste projeto, ele espera a cadeia inteira executada de
uma vez: commit do trabalho, `git push origin main` (o repo tem remoto) e atualização da nota
`Projetos/comentarios-concursos.md` no vault Obsidian — seguida de commit e push no repo do vault
(`~/Notas`). O remoto do vault chama-se **`origin`** e aponta para `iago-leal/notas-obsidian`:
`git push notas-obsidian` falha, porque `notas-obsidian` é o nome do repositório, não do remoto. Em
2026-08-01 os scripts `gerar_pendencias.py` e `gerar_indice.py` **não existiam mais** no vault; não
os procure.

**Why:** o Princípio nº 1 dele é "executar, não delegar", e a instrução de encerramento costuma vir
composta ("commit, push, atualize a nota e encerre"). Parar para confirmar cada etapa que a própria
frase já autorizou é fricção, não cuidado.

**How to apply:** execute na ordem acima; o trabalho vai direto em `main`, que é o que o histórico do
repo faz. Em 2026-07-31 o Harness foi desinstalado deste projeto a pedido do usuário ("o reversa é o
suficiente"), de modo que **não há mais** skill `encerrar-sessao`, `.harness/estado-da-sessao.md`,
gate `NARRATIVA_PENDENTE` nem commit `chore(sessao): encerrar sessão …` — o ritual termina no push.
O registro de decisões agora é `_reversa_sdd/adrs/`. Ver [[gemeo-ipm-e-referencia-autoritativa]].
