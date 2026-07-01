---
name: encerrar-sessao
description: >-
  Encerra a sessão do Harness — atualiza a narrativa da sessão, regenera os
  artefatos derivados, oferece commitar o trabalho pendente e grava o commit de
  registro do fechamento por cima do último commit de trabalho. Ative quando o
  usuário pedir para "encerrar a sessão", "fechar a sessão", "finalizar a
  sessão", "encerrar sessão do Harness" ou digitar "/encerrar-sessao". NÃO ative
  para iniciar ou retomar a sessão (isso é função do resume), nem para apenas
  commitar trabalho sem encerrar.
license: MIT
compatibility: Antigravity, Claude Code, Codex, Cursor, Gemini CLI e demais agentes compatíveis com Agent Skills.
metadata:
  author: iagoleal
  version: "1.1.0"
  framework: harness
  role: session
---

# Encerrar sessão do Harness

Conduza o encerramento autônomo da sessão do Harness. A lógica vive no Harness
Core (testada); os scripts desta skill são finos e apenas a invocam — não
reimplementam regra.

O `.harness/estado-da-sessao.md` tem duas metades: o front-matter (âncora, status
e tempo, que o fechamento mantém sozinho) e a **narrativa** — as quatro seções
`##` que só você, agente, sabe escrever. O core nunca inventa a narrativa; por
isso o primeiro passo do encerramento é **você** consolidá-la. Se esquecer, o
fechamento recusa de forma barulhenta (marker `NARRATIVA_PENDENTE`) e não fecha.

## Passos

1. **Atualize a narrativa da sessão.** Edite `.harness/estado-da-sessao.md` e
   reescreva as quatro seções refletindo o trabalho REAL desta sessão — não
   repita a narrativa anterior; descreva o que mudou:

   - `## O que foi feito`
   - `## Próximos passos`
   - `## Pendências / bloqueios`
   - `## Ponteiros`

   Preserve o front-matter YAML no topo: o fechamento o reescreve; você cuida só
   do corpo.

2. **Encerre a sessão.** Execute o script de entrada desta skill, que fica ao
   lado deste `SKILL.md`:

   ```bash
   python3 scripts/encerrar_sessao.py
   ```

   Ele resolve a raiz do projeto (via git), localiza o Harness Core em
   `.harness/harness-core`, e conduz, em ordem: regeneração dos artefatos
   derivados → pré-check de trabalho pendente → gate de narrativa → fechamento
   (commit de registro por cima do último commit de trabalho, com a âncora
   seguindo apontando para o trabalho) → ofertas de fim de sessão. Se a
   regeneração falhar (exit ≠ 0), o script **para** antes de fechar e mostra o
   erro.

3. **Se a saída trouxer um marker `[HARNESS:COMMIT_PENDENTE …]`**, há trabalho
   não commitado fora de `.harness/`: commite apenas o que for trabalho real,
   **por caminho** (`git add -- <arquivo>` e `git commit` com mensagem
   descritiva; nunca `git add -A`; separe fonte de artefato regenerável, que pode
   ir ao `.gitignore`) e rode o script novamente.

4. **Se a saída trouxer um marker `[HARNESS:NARRATIVA_PENDENTE …]`**, a narrativa
   continua vazia ou idêntica à do início da sessão — o Passo 1 não foi feito, ou
   não refletiu nada de novo. Volte ao Passo 1, reescreva de fato as quatro
   seções e rode o script novamente. O fechamento só prossegue quando a narrativa
   muda.

5. **Ofertas finais.** Ao encerrar com sucesso, o script pode emitir markers
   oferecendo publicar o trabalho (`[HARNESS:PUSH_DISPONIVEL …]` → `git push`) e
   atualizar o Harness Core (`[HARNESS:UPGRADE_DISPONIVEL …]` → `./harness upgrade`).
   Conduza essas ofertas se aparecerem. Mostre a saída ao usuário.

## Em caso de erro

Se o Harness Core não for encontrado ou não puder ser importado, o script falha
de forma **barulhenta** (exit ≠ 0 com mensagem orientadora), nunca em silêncio.
Confirme que você está dentro de um projeto com o Harness instalado (existe um
wrapper `./harness` e o diretório `.harness/harness-core`).
