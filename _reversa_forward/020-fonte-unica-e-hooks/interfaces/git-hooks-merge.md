# Contrato: instalação não-destrutiva dos hooks git

> Feature: `020-fonte-unica-e-hooks` · Tipo: arquivo · Confidência: 🟢
> Altera `bootstrap/service.py::install_hooks` (RN-N15). Espelha a não-destrutividade de RN-N28/N29.

## Problema atual

`install_hooks` faz `write_file(pre_commit_path, ...)` e `write_file(post_merge_path, ...)` **incondicionalmente** (service.py:44-52): sobrescreve qualquer `pre-commit`/`post-merge` preexistente, inclusive um hook próprio do projeto. (Hooks de **outro nome** — `commit-msg`, `pre-push` — já são preservados, pois nunca são tocados.)

## Contrato novo — por assinatura

Assinatura do harness = a linha de comentário estável já presente nos scripts: `# Hook <nome> — Harness Core`.

Para cada hook gerenciado `pre-commit` e `post-merge`:

| Estado do arquivo                              | Ação                                                                                                                                                                                                                       |
| ---------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Ausente**                                    | Cria o hook do harness (via shim)                                                                                                                                                                                          |
| **Presente COM** a assinatura `— Harness Core` | Substitui (atualiza) — é o próprio hook antigo do harness                                                                                                                                                                  |
| **Presente SEM** a assinatura (hook alheio)    | **Preserva**: move o conteúdo para `<hook>.local` (se ainda não existir) e grava um hook do harness que **invoca `<hook>.local` primeiro** (encadeamento), depois o passo do harness. Nunca descarta o conteúdo do projeto |

## Conteúdo do hook (via shim)

Os hooks passam a chamar o **shim**, não o python local — desacopla do layout do core:

```bash
#!/bin/bash
# Hook pre-commit — Harness Core
[ -x "$(dirname "$0")/../../pre-commit.local" ] && "$(dirname "$0")/../../pre-commit.local" "$@" || true   # encadeamento, quando houver
./harness format "$@"
exit $?
```

(análogo para `post-merge` → `./harness decisions`). A resolução do `.local` deve usar caminho estável dentro de `.git/hooks/`.

## Preservação garantida

- Hooks de outro nome (`commit-msg`, `pre-push`, `prepare-commit-msg`, …) → nunca lidos nem tocados.
- Um `pre-commit` próprio do projeto → preservado e encadeado, nunca perdido.
- A pasta `.git/hooks` nunca é apagada — só os dois arquivos nomeados são gerenciados.

## Idempotência

Reexecutar converge: um hook já do harness é reescrito igual; um `<hook>.local` já criado não é recriado (guarda "se ainda não existir"); a assinatura evita re-encadear em cima de si mesmo.

## Critérios de aceite (testes)

- `pre-commit` alheio → preservado em `.local` + hook do harness ativo que o invoca.
- `pre-commit` do harness antigo → atualizado no lugar, sem criar `.local`.
- Sem `pre-commit` → criado direto.
- `commit-msg` de terceiro presente → intacto após `bootstrap`.
