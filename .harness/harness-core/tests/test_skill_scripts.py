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


# --- Fallback à fonte única (feature 020): core do upstream via harness.toml ---


def _plant_core(base):
    """Cria a árvore mínima de um core (``src/main.py``) sob ``base`` e a devolve."""
    core_src = base / ".harness" / "harness-core" / "src"
    core_src.mkdir(parents=True)
    (core_src / "main.py").write_text("print('core')")
    return base / ".harness" / "harness-core"


def _write_toml(root, upstream):
    """Grava um ``harness.toml`` de projeto-shim apontando para ``upstream``."""
    (root / "harness.toml").write_text(
        "[harness]\n"
        'active_harness = "claude"\n'
        f'upstream_path = "{upstream}"\n\n'
        "[session]\n"
        'state_file = ".harness/estado-da-sessao.md"\n'
    )


def test_resolve_core_falls_back_to_upstream(tmp_path):
    # Projeto migrado à fonte única: sem core local, o bootstrap resolve o core do
    # upstream registrado em upstream_path — mesmo contrato do shim ./harness.
    bs = _load_bootstrap()
    upstream = tmp_path / "upstream"
    upstream.mkdir()
    upstream_core = _plant_core(upstream)

    project = tmp_path / "projeto-shim"
    project.mkdir()
    _write_toml(project, upstream)

    assert bs.resolve_core(project) == upstream_core


def test_resolve_core_prefers_local_over_upstream(tmp_path):
    # Havendo core local E upstream, o local vence (precedência preservada da 018).
    bs = _load_bootstrap()
    upstream = tmp_path / "upstream"
    upstream.mkdir()
    _plant_core(upstream)

    project = tmp_path / "projeto"
    project.mkdir()
    local_core = _plant_core(project)
    _write_toml(project, upstream)

    assert bs.resolve_core(project) == local_core


def test_resolve_core_raises_when_upstream_core_missing(tmp_path):
    # upstream_path aponta para um diretório sem core → erro barulhento que cita o
    # upstream, nunca falha em silêncio nem devolve um caminho inexistente.
    bs = _load_bootstrap()
    upstream = tmp_path / "upstream-vazio"
    upstream.mkdir()

    project = tmp_path / "projeto-shim"
    project.mkdir()
    _write_toml(project, upstream)

    with pytest.raises(bs.CoreNotFoundError) as exc:
        bs.resolve_core(project)
    assert "upstream" in str(exc.value).lower()


def test_read_upstream_path_extrai_valor(tmp_path):
    # O leitor do upstream_path segue o mesmo contrato de linha do sed do shim.
    bs = _load_bootstrap()
    _write_toml(tmp_path, "/algum/caminho/upstream")
    assert bs._read_upstream_path(tmp_path) == "/algum/caminho/upstream"


def test_read_upstream_path_ausente_devolve_none(tmp_path):
    # Sem harness.toml (ou sem o campo), devolve None — o resolve cai no erro loud.
    bs = _load_bootstrap()
    assert bs._read_upstream_path(tmp_path) is None
    (tmp_path / "harness.toml").write_text('[harness]\nactive_harness = "claude"\n')
    assert bs._read_upstream_path(tmp_path) is None
