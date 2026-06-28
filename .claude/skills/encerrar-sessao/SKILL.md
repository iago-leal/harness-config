---
name: encerrar-sessao
description: >-
  Encerra a sessão do Harness — regenera os artefatos derivados, oferece commitar
  o trabalho pendente e grava o commit de registro do fechamento por cima do
  último commit de trabalho. Ative quando o usuário pedir para "encerrar a
  sessão", "fechar a sessão", "finalizar a sessão", "encerrar sessão do Harness"
  ou digitar "/encerrar-sessao". NÃO ative para iniciar ou retomar a sessão (isso
  é função do resume), nem para apenas commitar trabalho sem encerrar.
license: MIT
compatibility: Antigravity, Claude Code, Codex, Cursor, Gemini CLI e demais agentes compatíveis com Agent Skills.
metadata:
  author: iagoleal
  version: "1.0.0"
  framework: harness
  role: session
---

# Encerrar sessão do Harness

Conduza o encerramento autônomo da sessão do Harness. A lógica vive no Harness
Core (testada); os scripts desta skill são finos e apenas a invocam — não
reimplementam regra.

## Passos

1. **Encerrar a sessão.** Execute o script de entrada desta skill, que fica ao
   lado deste `SKILL.md`:

   ```bash
   python3 scripts/encerrar_sessao.py
   ```

   Ele resolve a raiz do projeto (via git), localiza o Harness Core em
   `.harness/harness-core`, e conduz, em ordem: regeneração dos artefatos
   derivados → pré-check de trabalho pendente → fechamento (commit de registro
   por cima do último commit de trabalho, com a âncora seguindo apontando para o
   trabalho) → ofertas de fim de sessão. Se a regeneração falhar (exit ≠ 0), o
   script **para** antes de fechar e mostra o erro.

2. **Se a saída trouxer um marker `[HARNESS:COMMIT_PENDENTE …]`**, há trabalho
   não commitado fora de `.harness/`: commite apenas o que for trabalho real,
   **por caminho** (`git add -- <arquivo>` e `git commit` com mensagem
   descritiva; nunca `git add -A`; separe fonte de artefato regenerável, que pode
   ir ao `.gitignore`) e rode o script novamente.

3. **Ofertas finais.** Ao encerrar com sucesso, o script pode emitir markers
   oferecendo publicar o trabalho (`[HARNESS:PUSH_DISPONIVEL …]` → `git push`) e
   atualizar o Harness Core (`[HARNESS:UPGRADE_DISPONIVEL …]` → `./harness
upgrade`). Conduza essas ofertas se aparecerem. Mostre a saída ao usuário.

## Em caso de erro

Se o Harness Core não for encontrado ou não puder ser importado, o script falha
de forma **barulhenta** (exit ≠ 0 com mensagem orientadora), nunca em silêncio.
Confirme que você está dentro de um projeto com o Harness instalado (existe um
wrapper `./harness` e o diretório `.harness/harness-core`).
