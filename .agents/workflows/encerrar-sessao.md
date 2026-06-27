---
name: encerrar-sessao
description: Encerra a sessão do Harness, criando um commit de registro do fechamento por cima do último commit de trabalho.
---

Encerra a sessão do Harness: o fechamento vira um commit de registro por cima do último commit de trabalho (a âncora segue no trabalho). Ao final, o comando pode oferecer publicar o trabalho (git push) e atualizar o Harness Core (upgrade). O `cd` para a raiz garante que rode bem de qualquer diretório. Execute o comando de shell abaixo e mostre a saída ao usuário:

`cd /Users/iagoleal/dev/harness && /Users/iagoleal/dev/harness/harness cmd encerrar-sessao`
