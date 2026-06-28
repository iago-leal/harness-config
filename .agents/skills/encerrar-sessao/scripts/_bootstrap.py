"""Bootstrap fino da skill encerrar-sessao (feature 018).

Resolve a raiz do projeto via git, localiza o Harness Core em
``.harness/harness-core`` e o torna importável sob o venv do core. Não
reimplementa lógica de domínio: é só a cola de ambiente para o entry point poder
chamar os serviços do core. Erro barulhento (``CoreNotFoundError``) quando o core
não existe — nunca falha em silêncio.
"""

import os
import subprocess
import sys
from pathlib import Path

# Caminho do core relativo à raiz do projeto (mesmo de CORE_REL_PATH no core).
CORE_REL = os.path.join(".harness", "harness-core")


class CoreNotFoundError(RuntimeError):
    """Harness Core ausente, ou raiz do projeto não resolvível via git."""


def resolve_core(root) -> Path:
    """Devolve o diretório do core sob ``root`` ou levanta ``CoreNotFoundError``.

    Função PURA (sem git, sem re-exec): é o ponto testável do bootstrap.
    """
    core = Path(root) / CORE_REL
    if not (core / "src" / "main.py").exists():
        raise CoreNotFoundError(
            f"Harness Core não encontrado em {core}. Rode a skill encerrar-sessao "
            "dentro de um projeto com o Harness instalado (reinstale com "
            "'./harness init' se necessário)."
        )
    return core


def _repo_root() -> Path:
    """Raiz do projeto via ``git rev-parse --show-toplevel`` (erro barulhento)."""
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        raise CoreNotFoundError(
            "não foi possível resolver a raiz do projeto via git; a skill "
            "encerrar-sessao precisa rodar dentro de um repositório git"
        ) from exc
    return Path(proc.stdout.strip())


def bootstrap_core() -> Path:
    """Resolve a raiz, localiza o core e o torna importável; devolve a raiz.

    Quando o venv do core existe e o intérprete atual não é o dele, re-executa o
    próprio script sob esse venv (pydantic/toml precisam estar disponíveis). Em
    seguida garante o core no ``sys.path`` para os imports ``src.*``.
    """
    root = _repo_root()
    core = resolve_core(root)

    # Re-executa sob o venv do core quando ainda NÃO estamos nele. O teste é por
    # `sys.prefix` (a raiz do ambiente ativo), não pelo binário: um venv e o
    # Python-base de onde ele foi criado podem resolver para o MESMO executável,
    # mas só o venv expõe as deps (pydantic/toml). `resolve()` nos dois lados
    # absorve symlinks e evita laço de re-exec.
    venv_dir = core / ".venv"
    venv_py = venv_dir / "bin" / "python3"
    if venv_py.exists() and Path(sys.prefix).resolve() != venv_dir.resolve():
        os.execv(str(venv_py), [str(venv_py), *sys.argv])

    if str(core) not in sys.path:
        sys.path.insert(0, str(core))
    return root
