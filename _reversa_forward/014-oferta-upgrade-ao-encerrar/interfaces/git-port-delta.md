# Interface: delta do contrato `GitPort`

> Identificador: `014-oferta-upgrade-ao-encerrar`
> Tipo: contrato interno (porta) — `.harness/harness-core/src/core/ports/git.py`
> Implementação concreta: `.harness/harness-core/src/adapters/git/subprocess.py`

O domínio só fala com git pela porta (RN-N5). Abaixo, os métodos **novos**. Todos seguem o
molde do adapter atual: `subprocess.run(..., check=True)` e `CalledProcessError → RuntimeError`
com o `stderr`. Os métodos de **consulta** usados na detecção devem ser chamados pela borda
sob `try/except` (a detecção nunca trava — D-09).

## Métodos novos

| Método                                             | Comando git subjacente                                                                                    | Retorno                                | Erros                                                                    |
| -------------------------------------------------- | --------------------------------------------------------------------------------------------------------- | -------------------------------------- | ------------------------------------------------------------------------ |
| `fetch(repo_path, remote="origin", branch=None)`   | `git fetch <remote> [<branch>]`                                                                           | `None`                                 | `RuntimeError` (rede/auth) — capturado na borda                          |
| `get_current_branch(repo_path)`                    | `git rev-parse --abbrev-ref HEAD`                                                                         | `str` (ex.: `main`)                    | `RuntimeError`                                                           |
| `get_default_branch(repo_path, remote="origin")`   | `git symbolic-ref refs/remotes/<remote>/HEAD` → basename; fallback `{main, master}` por existência de ref | `str`                                  | nunca levanta: cai no fallback                                           |
| `count_commits_ahead(repo_path, rev="@{u}..HEAD")` | `git rev-list --count <rev>`                                                                              | `int` (0 se sem tracking ou em dia)    | sem upstream tracking → `0` (não levanta)                                |
| `get_file_at_ref(repo_path, ref, rel_path)`        | `git show <ref>:<rel_path>`                                                                               | `Optional[str]` (None se ausente)      | conteúdo ausente → `None`                                                |
| `is_working_tree_clean(repo_path)`                 | `git status --porcelain` (vazio = limpo)                                                                  | `bool`                                 | `RuntimeError`                                                           |
| `merge_ff_only(repo_path, ref)`                    | `git merge --ff-only <ref>`                                                                               | `bool` (True se fast-forward aplicado) | não-FF / sujo → `False` ou `RuntimeError` tratado como "não sincronizou" |
| `push(repo_path, remote=None, branch=None)`        | `git push` (respeita tracking; **nunca** `--force`)                                                       | `None`                                 | `RuntimeError` (rede/auth/rejeição)                                      |

## Notas de contrato

- **Sem `--force` em `push`** (RN-06): rejeição do remoto (ex.: non-fast-forward) é `RuntimeError`,
  reportada como aviso; jamais reescreve histórico.
- `count_commits_ahead` deve devolver `0` (não levantar) quando não há upstream tracking (`@{u}`
  indefinido), para que a borda simplesmente **não ofereça** push (RN-11) sem tratar exceção.
- `get_file_at_ref` é a base da detecção remota de versão (D-04): após `fetch`, lê
  `<remote>/<branch>:<CORE_CONFIG_*_RELPATH>` sem tocar o working tree do upstream.
- `merge_ff_only` é a sincronização não-destrutiva do upstream antes do upgrade (D-05): se não
  for fast-forward (working tree sujo ou divergência), **não** aplica e sinaliza falha, levando
  a borda a abortar o upgrade barulhento sem sobrescrever trabalho.

## Impacto em testes

Adicionar estes métodos como `@abstractmethod` **quebra** todo dublê de `GitPort` nos testes
(`test_commands.py`, `test_adapters.py`, helpers). Cada fake precisa implementar os novos
métodos (ou herdar de um `FakeGitBase` comum). Tratar na mesma mudança (roadmap §8, passo 1).
