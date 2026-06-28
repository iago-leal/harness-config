"""Fumaça dos scripts finos da skill encerrar-sessao (feature 018, T007).

Carrega o `_bootstrap.py` materializável a partir dos assets do core e exercita a
parte PURA (`resolve_core`): core ausente → erro barulhento (`CoreNotFoundError`),
nunca silencioso; core presente → caminho resolvido. A cola de git/re-exec não é
testada aqui (é shell de ambiente, não lógica).
"""

import importlib.util
import os
import sys

import pytest

_BOOTSTRAP_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "src",
    "core",
    "install",
    "assets",
    "skills",
    "encerrar-sessao",
    "scripts",
    "_bootstrap.py",
)


def _load_bootstrap():
    """Carrega o módulo do arquivo de asset real, sem gravar bytecode no source."""
    prev = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec = importlib.util.spec_from_file_location(
            "encerrar_sessao_bootstrap", _BOOTSTRAP_PATH
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    finally:
        sys.dont_write_bytecode = prev


def test_bootstrap_asset_existe():
    assert os.path.exists(_BOOTSTRAP_PATH)


def test_resolve_core_raises_when_core_absent(tmp_path):
    bs = _load_bootstrap()
    with pytest.raises(bs.CoreNotFoundError):
        bs.resolve_core(tmp_path)


def test_resolve_core_returns_path_when_present(tmp_path):
    bs = _load_bootstrap()
    core_src = tmp_path / ".harness" / "harness-core" / "src"
    core_src.mkdir(parents=True)
    (core_src / "main.py").write_text("print('core')")

    resolved = bs.resolve_core(tmp_path)
    assert resolved == tmp_path / ".harness" / "harness-core"


def test_core_not_found_error_message_is_loud(tmp_path):
    bs = _load_bootstrap()
    with pytest.raises(bs.CoreNotFoundError) as exc:
        bs.resolve_core(tmp_path)
    # Mensagem orientadora: cita o caminho e o caminho de conserto.
    assert "Harness Core" in str(exc.value)
    assert "harness init" in str(exc.value)
