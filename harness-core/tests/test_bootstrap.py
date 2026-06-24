import os
from src.core.bootstrap.service import BootstrapService
from tests.helpers import MockFileSystem


def test_bootstrap_install_hooks():
    fs = MockFileSystem()
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


def test_post_merge_hook_does_not_forward_git_args_to_decisions():
    # Regressão: o git invoca post-merge com um flag posicional (0/1 de squash).
    # O subcomando `decisions` não aceita posicional; repassar "$@" quebrava o
    # hook com "unrecognized arguments: 0". O gerador não deve repassar os args
    # do git ao `decisions`.
    fs = MockFileSystem()
    service = BootstrapService(fs)

    service.install_hooks("repo")
    post_merge = os.path.join("repo", ".git", "hooks", "post-merge")
    content = fs.read_file(post_merge)

    invocation = next(line for line in content.splitlines() if "decisions" in line)
    assert invocation.strip().endswith("decisions")
    assert '"$@"' not in invocation
