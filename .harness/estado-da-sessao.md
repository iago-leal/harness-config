---
commit: 69a8e6c
feature: correções pós-009 — hooks (MD-0006, MD-0007)
start_time: "2026-06-24T16:57:44+00:00"
status: active
---

## O que foi feito

- **Feature 009 — `hooks-antigravity`** mesclada em `main` (`8b3cd4c`, merge de `feat/009-hooks-antigravity`). Ganchos de ciclo de vida para o Antigravity, com re-extração reversa cirúrgica e regression-check pós-009.
- **Correção do hook post-merge (MD-0006)** — `BootstrapService._post_merge_script()` repassava `"$@"` ao subcomando `decisions`. O git invoca `post-merge` com o flag de squash (`0`/`1`) como posicional, e `decisions` (parser sem `add_argument`) o recusava com `unrecognized arguments: 0`. Disparou no merge da 009. Defeito no **gerador**, não na instância — regressão viva desde `af4a034`, preservada por `5624f78`; propaga a todo projeto criado por `harness init`. Conduzido como **TDD direto + registro leve**, fora do pipeline forward (Princípio nº 4), por decisão do mantenedor.
  - Teste de regressão em `test_bootstrap.py`: invertido o assert que codificava o bug (`'decisions "$@"' in post_content`) e adicionado `test_post_merge_hook_does_not_forward_git_args_to_decisions`. Vermelho antes, verde depois.
  - Correção de uma linha em `service.py:53` (remoção do `"$@"`).
  - Hook da raiz regenerado via `./harness bootstrap`. Provado de ponta a ponta: `./.git/hooks/post-merge 0` retorna `exit 0`. Commitado em `69a8e6c`.
- **Endurecimento do bootstrap (MD-0007)** — `install_hooks` instalava em `os.getcwd()/.git/hooks` sem verificar o `.git`, criando um `.git` degenerado quando rodado fora da raiz (acidente da sessão anterior). Agora `BootstrapService.install_hooks` recusa fora de repo git (`NotAGitRepositoryError`), e a CLI **oferece** `git init` antes de instalar; sem TTY, aborta com `exit 1` sem instalar. `GitPort` ganhou `init_repo`. Também TDD direto + registro leve.
  - Domínio: guarda em `service.py` (`fs.exists(.git)`) + exceção nomeada.
  - Apresentação: `offer_git_init()` em `main.py` (espelha `sys.stdin.isatty()` de `resolve_format_target`) e novo fluxo no handler do `bootstrap`.
  - Infra: `SubprocessGitAdapter.init_repo` (`git init`).
  - Provado: sem git → recusa/`exit 1` sem criar `.git`; com git → instala os dois hooks.
- **Suíte verde: 117 passed** (`.venv/bin/python -m pytest` a partir de `harness-core/`).

## Próximos passos

- Commit do MD-0007 e arquivos relacionados pendente de aval (após o `69a8e6c` da correção anterior).

## Pendências / bloqueios

- Inconsistência menor não corrigida (herdada): no MCP, `process_decisions` deriva `header_file` de `os.path.join(dir, "_cabecalho.md")` e ignora o override `config.decisions.header_file`.
- `001/W001–W003` acumulam 3 vereditos verdes consecutivos (limiar `archive-after=3`): candidatos a arquivamento. Ação manual do mantenedor.

## Ponteiros

- Microdecisões: `.harness/decisoes/MD-0006.md` (post-merge `"$@"`) e `MD-0007.md` (bootstrap recusa/oferta `git init`).
- Gerador dos hooks: `harness-core/src/core/bootstrap/service.py` (`install_hooks`, `_post_merge_script`, `NotAGitRepositoryError`).
- Oferta na CLI: `harness-core/src/main.py::offer_git_init` + handler `bootstrap`. Porta: `ports/git.py::init_repo`; adapter: `adapters/git/subprocess.py`.
- Testes: `harness-core/tests/test_bootstrap.py`, `test_cli.py`, `test_adapters.py`.
