# Investigation: Ofertas de fim de sessão — push e upgrade

> Identificador: `014-oferta-upgrade-ao-encerrar`
> Data: `2026-06-26`

## 1. Pesquisa de fundo (o que já existe)

- **Alerta passivo de versão.** `main.py` (antes do despacho dos subcomandos) chama
  `SyncService.check_version_update(version_local, upstream_path)`, que lê a `version` do
  arquivo de config do upstream **no filesystem** (varrendo `CORE_CONFIG_CANDIDATE_RELPATHS`)
  e, se diferente, imprime em `stderr` "Execute './harness upgrade'". Roda em todo comando
  exceto `init/upgrade/agy-hook/materialize`. É passivo e local. (`_reversa_sdd/domain.md#2.9` RN-N21)
- **Encerramento (013).** `CommandService.execute_command('encerrar-sessao')` captura a âncora
  (HEAD), grava o estado e cria um commit isolado via `GitPort.commit_paths`, reportando os dois
  hashes; falha barulhenta com `SessionCommitError`. (`_reversa_sdd/domain.md#2.14`)
- **Upgrade (007/012).** `InitializationService.upgrade_project(target_path, force)` lê
  `upstream_path` do `harness.toml`, compara versão, copia o core do upstream **no filesystem**
  (`_copy_tree`, excluindo `.harness`), atualiza o wrapper, regrava a `version` e rematerializa
  os artefatos de IDE via subprocesso do python de destino. (`_reversa_sdd/domain.md#2.9/2.13`)
- **Sincronia resiliente.** `SyncService.check_sync` faz `git ls-remote origin main`, com cache
  TTL e degradação para `True` em qualquer falha. Exposto só via MCP. Mostra o padrão de
  resiliência a adotar. (`_reversa_sdd/sync-check/requirements.md`)
- **Molde de oferta interativa.** `main.py#offer_git_init` pergunta `[s/N]` guardado por
  `sys.stdin.isatty()`; em contexto não-interativo retorna `False` sem perguntar. É o molde
  direto da dupla camada.
- **Porta de Git.** `GitPort` hoje expõe `get_head_commit`, `get_remote_commit` (ls-remote),
  `init_repo`, `commit_paths`. O `SubprocessGitAdapter` traduz `CalledProcessError` em
  `RuntimeError`. Faltam fetch, push, ahead-count, branch corrente/default, ler ref, ff-only.

## 2. Alternativas avaliadas

| Questão                       | Opção escolhida                                                  | Opções descartadas e porquê                                                                                 |
| ----------------------------- | ---------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| Onde colocar as ofertas       | Borda (`main.py`), após o fechamento (D-01)                      | No `CommandService`: acoplaria TTY/`input`/upgrade ao domínio e poria em risco a integridade do fechamento. |
| Como detectar a versão remota | `fetch` + `git show <remote>/<branch>:<config>` read-only (D-04) | `pull` no upstream só para detectar: efeito colateral e risco de conflito antes mesmo de o usuário aceitar. |
| Onde sincronizar o upstream   | No fluxo da oferta, antes de chamar `upgrade_project` (D-05)     | Dentro do `upgrade_project`: muda `./harness upgrade` standalone e força reescrever testes de 007/012.      |
| Aplicar o core                | Reusar `upgrade_project` (RN-08)                                 | Reimplementar cópia/rematerialização: duplicação de lógica crítica e dívida.                                |
| Cache da verificação          | Sem cache; fetch a cada encerramento (RN-07)                     | Reusar TTL de 24h: o encerramento é pontual e o frescor importa mais que poupar uma chamada.                |
| Push sem tracking             | Não oferecer (RN-11)                                             | `git push -u`: exigiria escolher remoto e poderia publicar para destino não pretendido.                     |

## 3. Padrões aplicáveis

- **Ports & Adapters (hexagonal).** Já é o padrão do core; os novos verbos de git entram na
  porta, a implementação concreta no adapter, o domínio permanece agnóstico (RN-N5).
- **Resiliência por degradação não-bloqueante.** Espelha `SyncService.check_sync` e a blindagem
  dos formatadores (RN-03/RN-02 do domínio): a borda envolve a etapa de ofertas em `try/except`.
- **Guarda de interatividade por TTY.** Espelha `offer_git_init`/`resolve_format_target`.
- **Marcadores estruturados para o agente.** Linha estável e parseável no `stdout` que o agente
  reconhece — análogo, em espírito, ao `additionalContext`/JSON que outras bordas emitem, mas
  aqui em texto simples por rodar no `!`-bash do slash command. Detalhe em
  `interfaces/session-end-offers.md`.

## 4. Pontos a confirmar na implementação

- Comportamento exato do workflow do Antigravity ao exibir os marcadores (não verificável
  localmente; alinha ao amarelo herdado de 009/010 sobre o Antigravity real).
- Forma final de detectar "sucesso" do encerramento sem tocar o `CommandService` (D-10): hoje
  por inspeção da mensagem; avaliar resultado tipado num refactor futuro.

## 5. Fontes externas

- Sem dependência de bibliotecas novas. Tudo via `git` por `subprocess` (já presente no adapter)
  e `argparse`/`sys` da stdlib. Nenhuma adição ao `requirements.txt` prevista.
