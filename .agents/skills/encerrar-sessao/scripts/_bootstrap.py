"""Bootstrap fino da skill encerrar-sessao (feature 018; fallback à fonte única na 020).

Resolve a raiz do projeto via git, localiza o Harness Core e o torna importável
sob o venv do core. Não reimplementa lógica de domínio: é só a cola de ambiente
para o entry point poder chamar os serviços do core. Erro barulhento
(``CoreNotFoundError``) quando o core não existe — nunca falha em silêncio.

A resolução do core segue a MESMA ordem do shim ``./harness`` (ver
``src/core/bootstrap/shim.py``): primeiro o core vendorizado em
``.harness/harness-core``; se ausente — projeto migrado à fonte única (feature
020), que não copia mais o core —, cai para o core do ``upstream_path`` registrado
no ``harness.toml``. Sem esse fallback a skill quebrava em todo projeto migrado.
"""

import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional

# Caminho do core relativo à raiz do projeto (mesmo de CORE_REL_PATH no core).
CORE_REL = os.path.join(".harness", "harness-core")


class CoreNotFoundError(RuntimeError):
    """Harness Core ausente, ou raiz do projeto não resolvível via git."""


def _core_at(base) -> Optional[Path]:
    """Diretório do core sob ``base`` se ele expõe ``src/main.py``; senão ``None``."""
    core = Path(base) / CORE_REL
    return core if (core / "src" / "main.py").exists() else None


def _read_upstream_path(root) -> Optional[str]:
    """Lê ``upstream_path`` do ``harness.toml`` da raiz, ou ``None`` se ausente.

    Projeto migrado à fonte única não tem core local: o ``harness.toml`` registra o
    ``upstream_path`` do repositório-fonte, de onde o core roda. A leitura é por
    regex de linha — o mesmo contrato do ``sed`` do shim (``shim.py``) — para não
    depender de biblioteca toml antes do re-exec sob o venv do core.
    """
    toml = Path(root) / "harness.toml"
    if not toml.exists():
        return None
    for line in toml.read_text(encoding="utf-8").splitlines():
        match = re.match(r'\s*upstream_path\s*=\s*"(.*)"', line)
        if match:
            return match.group(1)
    return None


def resolve_core(root) -> Path:
    """Devolve o diretório do core a usar sob ``root`` ou levanta ``CoreNotFoundError``.

    Resolve na mesma ordem do shim: core local primeiro; na ausência, o core do
    ``upstream_path`` do ``harness.toml`` (projeto migrado à fonte única). Erro
    barulhento quando nenhum dos dois expõe ``src/main.py``. Função sem git nem
    re-exec: é o ponto testável do bootstrap.
    """
    local = _core_at(root)
    if local is not None:
        return local

    upstream = _read_upstream_path(root)
    if upstream:
        remote = _core_at(upstream)
        if remote is not None:
            return remote

    origem = (
        f"upstream_path={upstream}" if upstream else "sem upstream_path no harness.toml"
    )
    raise CoreNotFoundError(
        f"Harness Core não encontrado: ausente localmente em {Path(root) / CORE_REL} "
        f"e no upstream ({origem}). Rode a skill encerrar-sessao dentro de um projeto "
        "com o Harness instalado (reinstale com 'harness init' ou reconcilie o "
        "'harness migrate' se necessário)."
    )


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
