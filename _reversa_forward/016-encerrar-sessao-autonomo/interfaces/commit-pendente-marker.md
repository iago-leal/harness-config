# Contrato: marker `[HARNESS:COMMIT_PENDENTE …]`

> Identificador: `016-encerrar-sessao-autonomo`
> Tipo: protocolo de borda (core → agente), pré-fechamento
> Irmão de: `_reversa_forward/014-oferta-upgrade-ao-encerrar/interfaces/session-end-offers.md` (markers pós-fechamento)

## 1. Quando é emitido

Durante `./harness cmd encerrar-sessao`, **antes** de fechar, a borda (`main.py`) consulta `GitPort.list_dirty_paths(repo_path)`, filtra os caminhos sob `.harness/` (que o próprio fechamento versiona) e:

- **Árvore limpa fora de `.harness/`** → segue o fechamento normal (sem marker).
- **Há trabalho solto** → emite o marker e faz **early return sem fechar** (exit 0). O fechamento só ocorre numa execução posterior, com a árvore limpa.

## 2. Dualidade TTY × não-TTY (espelha a feature 014)

- **Sem TTY (slash command / agente):** emite a linha de marker estruturada (abaixo) e retorna. O agente medeia: lista os arquivos, commita o que é trabalho real e re-roda o comando.
- **Com TTY (terminal interativo):** pergunta `[s/N]` se deseja commitar o pendente antes de encerrar; em "s", conduz o commit; segue ou aborta conforme a resposta.

## 3. Formato do marker (não-TTY)

```
[HARNESS:COMMIT_PENDENTE arquivos="<lista separada por vírgula>" total=<n> acao="git add + commit por caminho; depois re-rodar encerrar-sessao"]
```

- `arquivos`: caminhos sujos **fora** de `.harness/`, relativos à raiz. Lista possivelmente truncada com indicação de truncamento se muito longa (alinhar ao teto de contexto, RN-N8).
- `total`: número total de caminhos sujos fora de `.harness/` (mesmo se a lista for truncada).
- `acao`: instrução curta e estável para o agente.

## 4. Regras de processamento (lado do agente)

1. Para cada arquivo listado, julgar se é trabalho real (versionar) ou lixo/derivado (ignorar ou `.gitignore`).
2. Commitar **por caminho** (`git add -- <path>`), nunca `git add -A`, com mensagem descritiva; split sensato entre fonte e regenerável.
3. Re-rodar `./harness cmd encerrar-sessao`. Com a árvore limpa fora de `.harness/`, o fechamento procede.

## 5. Invariantes preservados

- O marker é **anterior** ao fechamento; não altera `commit_paths` (RN-N31/N32): o commit de fechamento continua versionando só `.harness/estado-da-sessao.md`.
- O core não faz `git add` do trabalho do usuário — quem decide e commita é o agente/usuário (RN-N5; o core só **lista** via `list_dirty_paths`).
- Idempotência: re-rodar com árvore suja re-emite o marker; com árvore limpa, fecha.

## 6. Erros e bordas

- `list_dirty_paths` falha de execução real → erro barulhento (a consulta é da borda; tratar como falha do comando, sem fechar). Estado normal "sem sujeira" → lista vazia, nunca exceção.
- Só `.harness/estado-da-sessao.md` sujo → tratado como limpo (não dispara marker): é o que o fechamento versiona.
