"""Fonte única do caminho do harness-core dentro de um projeto.

A partir da feature 011, o core mora em ``.harness/harness-core`` (e não mais
na raiz). Centralizar o caminho aqui evita espalhar o literal pelo wrapper, pelo
serviço de init/upgrade, pela checagem de versão e pelo gerador de ganchos Git —
um único ponto de mudança (baixo acoplamento).
"""

# Caminho do diretório do core, relativo à raiz do projeto.
CORE_REL_PATH = ".harness/harness-core"

# Caminho da CLI Python, relativo à raiz do projeto.
CORE_MAIN_REL_PATH = f"{CORE_REL_PATH}/src/main.py"

# Caminho do interpretador da venv local, relativo à raiz do projeto.
CORE_VENV_PYTHON_REL_PATH = f"{CORE_REL_PATH}/.venv/bin/python3"

# Entrada de .gitignore que oculta a cópia vendored do core nos projetos-alvo.
CORE_GITIGNORE_ENTRY = f"{CORE_REL_PATH}/"
