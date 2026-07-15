"""GitPort.list_dirty_paths — listagem da working tree suja (feature 016).

Feature 022 acrescenta list_changed_paths_since (diff da âncora), testado aqui
com git REAL: mock de porcelain/diff já mascarou comportamento antes (lição 019).
"""

import subprocess

import pytest

from src.adapters.git.subprocess import SubprocessGitAdapter


def _git(tmp_path, *args):
    subprocess.run(["git", *args], cwd=str(tmp_path), capture_output=True, check=True)


def _init_repo(tmp_path):
    _git(tmp_path, "init")
    _git(tmp_path, "config", "user.email", "t@t.t")
    _git(tmp_path, "config", "user.name", "t")


def test_list_dirty_paths_empty_on_clean_tree(tmp_path):
    _init_repo(tmp_path)
    (tmp_path / "a.txt").write_text("x")
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-m", "init")

    git = SubprocessGitAdapter()
    assert git.list_dirty_paths(str(tmp_path)) == []


def test_list_dirty_paths_reports_untracked_and_modified(tmp_path):
    _init_repo(tmp_path)
    (tmp_path / "a.txt").write_text("x")
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-m", "init")

    # modifica rastreado + cria não rastreado
    (tmp_path / "a.txt").write_text("y")
    (tmp_path / "novo.txt").write_text("z")

    git = SubprocessGitAdapter()
    dirty = git.list_dirty_paths(str(tmp_path))
    assert "a.txt" in dirty
    assert "novo.txt" in dirty


def test_list_dirty_paths_expands_untracked_subdir(tmp_path):
    # Feature 019: arquivo não rastreado dentro de subdiretório novo deve vir como
    # caminho de arquivo, não o diretório colapsado (--untracked-files=all). Sem
    # isso, pending_work_paths não distingue o estado-da-sessao.md do resto de
    # .harness/, e a oferta de commit pendente ofereceria o diretório inteiro.
    _init_repo(tmp_path)
    (tmp_path / "a.txt").write_text("x")
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-m", "init")

    sub = tmp_path / ".harness" / "decisoes"
    sub.mkdir(parents=True)
    (sub / "MD-1.md").write_text("d")

    git = SubprocessGitAdapter()
    dirty = git.list_dirty_paths(str(tmp_path))
    assert ".harness/decisoes/MD-1.md" in dirty
    assert ".harness" not in dirty
    assert ".harness/" not in dirty


def _head(tmp_path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=str(tmp_path),
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def test_list_changed_paths_since_ve_commits_apos_ancora(tmp_path):
    # Feature 022: o gate de registro enxerga trabalho já COMMITADO na sessão
    # pelo diff da âncora — list_dirty_paths sozinho é cego a isso.
    _init_repo(tmp_path)
    (tmp_path / "a.txt").write_text("x")
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-m", "ancora")
    ancora = _head(tmp_path)

    (tmp_path / "contrato.md").write_text("cláusula nova")
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-m", "trabalho da sessão")

    git = SubprocessGitAdapter()
    assert git.list_changed_paths_since(str(tmp_path), ancora) == ["contrato.md"]
    # Âncora == HEAD → sem mudanças.
    assert git.list_changed_paths_since(str(tmp_path), _head(tmp_path)) == []


def test_list_changed_paths_since_ref_invalida_levanta(tmp_path):
    # RN-N4: falha real de execução é barulhenta (RuntimeError), nunca lista vazia
    # silenciosa — cabe à borda do gate tratar como ausência de baseline.
    _init_repo(tmp_path)
    (tmp_path / "a.txt").write_text("x")
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-m", "init")

    git = SubprocessGitAdapter()
    with pytest.raises(RuntimeError):
        git.list_changed_paths_since(str(tmp_path), "deadbeef" * 5)
