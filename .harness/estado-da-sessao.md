---
commit: 8b3cd4c
feature: correção pós-009 — hook post-merge (MD-0006)
start_time: "2026-06-24T16:57:44+00:00"
status: active
---

## O que foi feito

- **Feature 009 — `hooks-antigravity`** mesclada em `main` (`8b3cd4c`, merge de `feat/009-hooks-antigravity`). Ganchos de ciclo de vida para o Antigravity, com re-extração reversa cirúrgica e regression-check pós-009.
- **Correção do hook post-merge (MD-0006)** — `BootstrapService._post_merge_script()` repassava `"$@"` ao subcomando `decisions`. O git invoca `post-merge` com o flag de squash (`0`/`1`) como posicional, e `decisions` (parser sem `add_argument`) o recusava com `unrecognized arguments: 0`. Disparou no merge da 009. Defeito no **gerador**, não na instância — regressão viva desde `af4a034`, preservada por `5624f78`; propaga a todo projeto criado por `harness init`. Conduzido como **TDD direto + registro leve**, fora do pipeline forward (Princípio nº 4), por decisão do mantenedor.
  - Teste de regressão em `test_bootstrap.py`: invertido o assert que codificava o bug (`'decisions "$@"' in post_content`) e adicionado `test_post_merge_hook_does_not_forward_git_args_to_decisions`. Vermelho antes, verde depois.
  - Correção de uma linha em `service.py:53` (remoção do `"$@"`).
  - Hook da raiz regenerado via `./harness bootstrap`. Provado de ponta a ponta: `./.git/hooks/post-merge 0` retorna `exit 0`.
- **Suíte verde: 111 passed** (`.venv/bin/python -m pytest` a partir de `harness-core/`).

## Próximos passos

- **Cuidado operacional registrado:** `./harness bootstrap` instala em `os.getcwd()/.git/hooks`. Rodá-lo com o cwd dentro de `harness-core/` cria um `.git` degenerado lá (só `hooks/`, sem HEAD/objects) — aconteceu uma vez nesta sessão e foi removido. Rodar sempre a partir da raiz do projeto.

## Pendências / bloqueios

- Inconsistência menor não corrigida (herdada): no MCP, `process_decisions` deriva `header_file` de `os.path.join(dir, "_cabecalho.md")` e ignora o override `config.decisions.header_file`.
- `001/W001–W003` acumulam 3 vereditos verdes consecutivos (limiar `archive-after=3`): candidatos a arquivamento. Ação manual do mantenedor.

## Ponteiros

- Microdecisão da correção: `.harness/decisoes/MD-0006.md` (relaciona MD-0005, footprint per-projeto).
- Gerador do hook: `harness-core/src/core/bootstrap/service.py::_post_merge_script` (linha ~53).
- Testes: `harness-core/tests/test_bootstrap.py`.
- Memória do bug: `post-merge-hook-arg-bug.md` (atualizar para resolvido).
