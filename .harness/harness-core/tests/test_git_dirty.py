"""GitPort.list_dirty_paths — listagem da working tree suja (feature 016)."""

import subprocess

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
