"""Shim de execução do Harness (feature 020, fonte única).

A partir da 020, o `init` deixa de copiar o `harness-core` e de criar uma venv
no projeto-alvo: o alvo recebe apenas este shim, que executa o core que vive no
**upstream** (repositório-fonte registrado em `upstream_path` no `harness.toml`),
com o cwd do projeto. Como o core é cwd-relativo, opera sobre o `.harness/` e o
`harness.toml` do projeto sem precisar residir nele.

`render_shim()` é a fonte única do conteúdo do wrapper, reutilizada por `init` e
por `migrate`. Contrato completo em
`_reversa_forward/020-fonte-unica-e-hooks/interfaces/shim-execution.md`.
"""

from src.core.domain.layout import CORE_MAIN_REL_PATH, CORE_VENV_PYTHON_REL_PATH


def render_shim() -> str:
    """Devolve o conteúdo bash do shim `harness` do projeto-alvo.

    O shim: (1) força o cwd para a raiz do projeto (onde ele mesmo mora), de modo
    que o core resolva `.harness/`/`harness.toml` do projeto mesmo se invocado de
    uma subpasta; (2) lê `upstream_path` do `harness.toml`; (3) executa o
    python+`main.py` do core do upstream, repassando os argumentos. Se o upstream
    não expõe o core, falha barulhento (stderr + exit 1), nunca degradado.
    """
    return (
        "#!/bin/bash\n"
        "# Shim do Harness — executa o core do upstream (fonte única, feature 020)\n"
        'SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"\n'
        'cd "$SCRIPT_DIR" || exit 1\n'
        "UPSTREAM=$(sed -n 's/^upstream_path = \"\\(.*\\)\"/\\1/p' harness.toml | head -1)\n"
        f'PY="$UPSTREAM/{CORE_VENV_PYTHON_REL_PATH}"\n'
        f'MAIN="$UPSTREAM/{CORE_MAIN_REL_PATH}"\n'
        'if [ -z "$UPSTREAM" ] || [ ! -f "$MAIN" ] || [ ! -f "$PY" ]; then\n'
        '    echo "Erro: core do Harness não encontrado no upstream '
        '(confira upstream_path em harness.toml)." >&2\n'
        "    exit 1\n"
        "fi\n"
        'exec "$PY" "$MAIN" "$@"\n'
    )
