"""Smoke do shim `harness` (feature 020) com bash real.

O shim é um contrato de shell: não dá para exercitá-lo com FakeFs. Estes testes
montam um upstream fake (um "python" que ecoa args e cwd) e um projeto com o shim
de `render_shim()`, e executam via subprocess.
"""

import os
import shutil
import stat
import subprocess

import pytest

from src.core.bootstrap.shim import render_shim

pytestmark = pytest.mark.skipif(
    shutil.which("bash") is None, reason="o shim é bash; requer bash no PATH"
)


def _make_executable(path):
    os.chmod(
        path,
        os.stat(path).st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH,
    )


def _fake_upstream(root):
    """Upstream fake: um 'python3' que ecoa os args e o cwd, e um main.py."""
    core = os.path.join(root, ".harness", "harness-core")
    venv_bin = os.path.join(core, ".venv", "bin")
    os.makedirs(venv_bin)
    os.makedirs(os.path.join(core, "src"))
    py = os.path.join(venv_bin, "python3")
    with open(py, "w") as f:
        f.write('#!/bin/bash\necho "ARGS: $@"\necho "CWD: $(pwd)"\n')
    _make_executable(py)
    with open(os.path.join(core, "src", "main.py"), "w") as f:
        f.write("# fake main\n")


def _project(root, upstream_path):
    proj = os.path.join(root, "proj")
    os.makedirs(proj)
    with open(os.path.join(proj, "harness.toml"), "w") as f:
        f.write(f'[harness]\nupstream_path = "{upstream_path}"\n')
    shim = os.path.join(proj, "harness")
    with open(shim, "w") as f:
        f.write(render_shim())
    _make_executable(shim)
    return proj, shim


def test_shim_executes_upstream_and_forwards_args(tmp_path):
    up = os.path.join(str(tmp_path), "up")
    os.makedirs(up)
    _fake_upstream(up)
    proj, shim = _project(str(tmp_path), up)

    # Roda de uma SUBPASTA: prova que o shim faz cd para a raiz do projeto.
    subdir = os.path.join(proj, "sub")
    os.makedirs(subdir)
    result = subprocess.run(
        [shim, "cmd", "resume"], cwd=subdir, capture_output=True, text=True
    )

    assert result.returncode == 0, result.stderr
    assert "cmd resume" in result.stdout  # args do usuário repassados
    assert "src/main.py" in result.stdout  # MAIN do upstream repassado como 1º arg
    cwd_line = next(
        line for line in result.stdout.splitlines() if line.startswith("CWD:")
    )
    assert cwd_line.strip().endswith("/proj")  # cwd na raiz, não na subpasta
    assert not cwd_line.strip().endswith("/sub")


def test_shim_fails_loudly_without_upstream(tmp_path):
    proj, shim = _project(str(tmp_path), "/caminho/inexistente")

    result = subprocess.run([shim], cwd=proj, capture_output=True, text=True)

    assert result.returncode != 0
    assert "Erro" in result.stderr


# Wrapper LOCAL do repositório upstream (era da cópia vendorizada): resolve o
# core pelo próprio diretório, mas até o BUG-20260811-TVCP preservava o cwd do
# chamador — e o core é cwd-relativo, então hook/script invocado de subpasta
# semeava .harness/ fora da raiz (episódio: SessionStart do compact com o shell
# em .harness/harness-core/). O contrato é o mesmo do shim da 020: âncora na raiz.
LOCAL_WRAPPER = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "harness")
)


def test_wrapper_local_do_upstream_ancora_o_cwd(tmp_path):
    if not os.path.isfile(LOCAL_WRAPPER):
        pytest.skip("wrapper local do upstream ausente neste checkout")
    root = str(tmp_path)
    # O layout que o wrapper espera é o mesmo do upstream fake: core vendorizado
    # em .harness/harness-core com venv própria.
    _fake_upstream(root)
    wrapper = os.path.join(root, "harness")
    shutil.copyfile(LOCAL_WRAPPER, wrapper)
    _make_executable(wrapper)

    subdir = os.path.join(root, "sub")
    os.makedirs(subdir)
    result = subprocess.run(
        [wrapper, "cmd", "resume"], cwd=subdir, capture_output=True, text=True
    )

    assert result.returncode == 0, result.stderr
    cwd_line = next(
        line for line in result.stdout.splitlines() if line.startswith("CWD:")
    )
    reported = os.path.realpath(cwd_line.split("CWD:", 1)[1].strip())
    assert reported == os.path.realpath(root)  # raiz, nunca a subpasta do chamador
