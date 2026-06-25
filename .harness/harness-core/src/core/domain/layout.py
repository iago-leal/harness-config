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

# Caminho do config.py (fonte da versão do core), relativo à raiz do projeto.
CORE_CONFIG_REL_PATH = f"{CORE_REL_PATH}/src/core/domain/config.py"

# Caminho legado do core (pré-feature 011, quando vivia na raiz). Mantido apenas
# como candidato de leitura — nunca como destino de escrita.
_LEGACY_CORE_REL_PATH = "harness-core"

# Caminhos-candidato do config.py para a leitura da versão do upstream, em ordem
# de preferência: o layout canônico atual e o legado da raiz. Varrer candidatos
# torna a detecção de versão resiliente a relocações do core no upstream — sem
# isso, um relayout faz a leitura cair num caminho fixo inexistente e a versão
# "indeterminada" coincidir com a local, gerando um upgrade fantasma. Fonte
# única: um só ponto de mudança quando o layout evoluir (feature 012).
CORE_CONFIG_CANDIDATE_RELPATHS = (
    CORE_CONFIG_REL_PATH,
    f"{_LEGACY_CORE_REL_PATH}/src/core/domain/config.py",
)
