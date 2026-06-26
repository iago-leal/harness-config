# Investigation: Versionar o estado da sessão ao encerrar

> Identificador: `013-commit-encerrar-sessao`
> Data: `2026-06-26`
> Acompanha: `roadmap.md`

## 1. Pesquisa de fundo

O estado da sessão é o artefato canônico `.harness/estado-da-sessao.md`
(`_reversa_sdd/session/requirements.md`, RN-N1): front-matter YAML (header-máquina) +
corpo Markdown (narrativa). O ramo `encerrar-sessao` de `CommandService.execute_command`
(`src/core/commands/service.py:37-46`) hoje executa, nesta ordem:

1. `load_session` — exige sessão ativa (senão devolve erro).
2. `current_commit = self.git.get_head_commit(repo_path)` — captura o HEAD.
3. `session.close_session(current_commit)` — grava a âncora no modelo e desativa.
4. `self.save_session(...)` — escrita atômica do artefato.
5. retorna a mensagem com a âncora.

Não há `git add`/`git commit`. O `GitPort` (`src/core/ports/git.py`) expõe apenas
`get_head_commit`, `get_remote_commit`, `init_repo` — todos de leitura/init, nenhum de
escrita de commit. O `SubprocessGitAdapter` (`src/adapters/git/subprocess.py`) segue o
mesmo padrão: cada método roda um `subprocess.run([... ], check=True)` e traduz
`CalledProcessError` em `RuntimeError` com `stderr`.

Os slash commands materializados (`session_command_artifact` em
`src/core/install/harness_profiles.py`) apenas delegam ao wrapper: o `ClaudeProfile`
grava `.claude/commands/encerrar-sessao.md` com `!\`./harness cmd encerrar-sessao\``; o
`AntigravityProfile`grava`.agents/workflows/encerrar-sessao.md`. Ambos anunciam na
`description` "gravando o commit-âncora", o que já é impreciso hoje (nenhum commit é
criado) e ficaria enganoso após a feature.

A materialização desses artefatos é feita por `materialize_session_commands`, chamada
**sempre** por `init` e `upgrade` (`_reversa_sdd/domain.md#2.12`). A feature 012 já
ensinou que mudar um materializador exige bump de versão e rematerialização do código
fresco, sob pena de o `upgrade` regravar o artefato stale.

## 2. Alternativas avaliadas

| Alternativa                                   | Avaliação                                                                                                                 | Veredito                     |
| --------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- | ---------------------------- |
| `commit_paths` na porta `GitPort` + adapter   | Mantém o domínio agnóstico ao `git`; contrato explícito e testável com fake.                                              | **Escolhida** (D-01).        |
| `subprocess` direto no `CommandService`       | Acoplaria a regra de negócio à infra; viola RN-N5 e o princípio de baixo acoplamento.                                     | Descartada.                  |
| Método genérico de shell na porta             | Porta vira canivete suíço; perde coesão e abre brecha para `git add -A` acidental.                                        | Descartada.                  |
| Commit em `main.py`/`server.py` (na borda)    | Duplicaria a lógica entre CLI e MCP e divergiria com o tempo; o requirements pede no próprio comando.                     | Descartada (D-02).           |
| `git add -A` / `git commit -a`                | Arrastaria mudanças alheias do working tree (`AGENTS.md`, `CLAUDE.md`, regras da Mira) — o erro explicitamente destacado. | Descartada (D-04).           |
| Capturar âncora após o commit                 | A âncora passaria a apontar para o próprio commit de encerramento, não para o trabalho.                                   | Descartada (D-03).           |
| Reverter o `state_file` quando o commit falha | Perderia a narrativa de fechamento já escrita; usuário escolheu preservar o estado salvo.                                 | Descartada (clarify; RN-05). |
| Mudar a string do materializador sem bump     | O `upgrade` regravaria o texto stale; lição direta da feature 012.                                                        | Descartada (D-08).           |

## 3. Padrões aplicáveis

- **Ports & Adapters (hexagonal):** o novo método nasce na porta `GitPort` e é
  implementado no adapter de subprocess, espelhando `get_head_commit`/`init_repo`.
- **Erro nomeado / falha barulhenta:** segue o padrão de `MalformedSessionStateError`
  (`src/core/session/errors.py`) — uma classe `Exception` dedicada, dado que o módulo
  de comandos ainda não tem `errors.py`.
- **Pathspec seguro:** `git add -- <paths>` com `--` separa opções de caminhos e blinda
  contra nomes que comecem com `-`; commit restrito ao conjunto explícito.
- **Test double que modela transição:** um Git fake que avança o HEAD ao commitar deixa
  o teste asserir, com naturalidade, que a âncora é o HEAD pré-commit e que o retorno é
  o hash pós-commit.

## 4. Fontes externas

- Nenhuma dependência ou serviço externo novo. A feature usa apenas o `git` já
  pressuposto pelo `SubprocessGitAdapter` e a stdlib (`subprocess`). Filtro de
  longevidade não se aplica — nada novo é introduzido.

## 5. Pontos de atenção para o `/reversa-coding`

- Capturar a âncora **antes** de `close_session`/`save_session` (já é a ordem atual; não inverter).
- Passar **somente** `[session_filepath]` a `commit_paths`; jamais `-A`.
- Atualizar `tests/test_commands.py::test_execute_encerrar_sessao`, que hoje espera a mensagem antiga só com a âncora.
- Após o bump, **rematerializar** os artefatos locais a partir do código novo (não confiar na cópia em memória).
- Conferir que a suíte cobre: isolamento do commit, âncora pré-commit, dois hashes, e `SessionCommitError` na falha.
