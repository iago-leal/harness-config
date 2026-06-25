import os
import pytest
from src.core.bootstrap.service import BootstrapService, NotAGitRepositoryError
from tests.helpers import MockFileSystem


def _git_repo_fs():
    """MockFileSystem simulando um repositório git (subpasta .git presente)."""
    return MockFileSystem(existing_files={os.path.join("repo", ".git")})


def test_bootstrap_install_hooks():
    fs = _git_repo_fs()
    service = BootstrapService(fs)
    repo_path = "repo"

    installed = service.install_hooks(repo_path)

    assert len(installed) == 2
    pre_commit = os.path.join(repo_path, ".git", "hooks", "pre-commit")
    post_merge = os.path.join(repo_path, ".git", "hooks", "post-merge")

    assert pre_commit in installed
    assert post_merge in installed
    assert fs.exists(pre_commit)
    assert fs.exists(post_merge)

    pre_content = fs.read_file(pre_commit)
    assert "Harness Core" in pre_content
    assert 'format "$@"' in pre_content
    assert "--shadow" not in pre_content
    assert "harness-config" not in pre_content

    post_content = fs.read_file(post_merge)
    assert "Harness Core" in post_content
    assert "decisions" in post_content
    assert 'decisions "$@"' not in post_content
    assert "--shadow" not in post_content
    assert "harness-config" not in post_content


def test_install_hooks_marks_them_executable():
    # Regressão: hook gravado sem bit de execução não roda — o git o ignora em
    # silêncio (falha muda). install_hooks deve marcar pre-commit e post-merge
    # como executáveis após gravá-los.
    fs = _git_repo_fs()
    service = BootstrapService(fs)

    service.install_hooks("repo")

    pre_commit = os.path.join("repo", ".git", "hooks", "pre-commit")
    post_merge = os.path.join("repo", ".git", "hooks", "post-merge")
    assert pre_commit in fs.executable_files
    assert post_merge in fs.executable_files


def test_post_merge_hook_does_not_forward_git_args_to_decisions():
    # Regressão: o git invoca post-merge com um flag posicional (0/1 de squash).
    # O subcomando `decisions` não aceita posicional; repassar "$@" quebrava o
    # hook com "unrecognized arguments: 0". O gerador não deve repassar os args
    # do git ao `decisions`.
    fs = _git_repo_fs()
    service = BootstrapService(fs)

    service.install_hooks("repo")
    post_merge = os.path.join("repo", ".git", "hooks", "post-merge")
    content = fs.read_file(post_merge)

    invocation = next(line for line in content.splitlines() if "decisions" in line)
    assert invocation.strip().endswith("decisions")
    assert '"$@"' not in invocation


def test_install_hooks_refuses_outside_git_repo():
    # Sem repositório git, install_hooks recusa e não escreve nada — em vez de
    # criar um .git/hooks degenerado. A oferta de `git init` fica a cargo da
    # camada de apresentação (CLI).
    fs = MockFileSystem()
    service = BootstrapService(fs)

    with pytest.raises(NotAGitRepositoryError):
        service.install_hooks("repo")

    assert fs.written_files == {}
