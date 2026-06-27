---
description: Encerra a sessão do Harness, criando um commit de registro do fechamento por cima do último commit de trabalho.
allowed-tools: Bash(cd:*), Bash(git rev-parse:*), Bash(./harness cmd encerrar-sessao:*)
---

Encerrando a sessão do Harness: o fechamento é gravado como um commit de registro por cima do último commit de trabalho (a âncora segue apontando para o trabalho). Ao final, o comando pode oferecer publicar o trabalho (git push) e atualizar o Harness Core (upgrade). O `cd` para a raiz do projeto (resolvida via git) faz o comando funcionar mesmo quando a sessão está num subdiretório.

!`cd "$(git rev-parse --show-toplevel)" && ./harness cmd encerrar-sessao`
