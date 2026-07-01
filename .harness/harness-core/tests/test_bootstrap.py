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


def _hook_path(name):
    return os.path.join("repo", ".git", "hooks", name)


def test_foreign_pre_commit_preserved_in_local_and_chained():
    # Feature 020 (RN-07): um pre-commit PRÓPRIO do projeto (sem a assinatura do
    # harness) não pode ser descartado. É preservado em pre-commit.local e o hook
    # do harness passa a encadeá-lo.
    fs = _git_repo_fs()
    pre = _hook_path("pre-commit")
    fs.write_file(pre, "#!/bin/bash\necho meu-pre-commit\n")  # alheio, sem assinatura

    BootstrapService(fs).install_hooks("repo")

    local = pre + ".local"
    assert fs.exists(local)
    assert "meu-pre-commit" in fs.read_file(local)  # conteúdo do projeto preservado
    harness_pre = fs.read_file(pre)
    assert "Harness Core" in harness_pre  # hook do harness ativo
    assert "pre-commit.local" in harness_pre  # e encadeia o do projeto


def test_own_hook_updated_without_creating_local():
    # Um pre-commit que JÁ é do harness (tem a assinatura) é atualizado no lugar,
    # sem gerar um .local (não se encadeia a si mesmo).
    fs = _git_repo_fs()
    pre = _hook_path("pre-commit")
    fs.write_file(pre, "#!/bin/bash\n# Hook pre-commit — Harness Core\n# antigo\n")

    BootstrapService(fs).install_hooks("repo")

    assert not fs.exists(pre + ".local")
    assert "Harness Core" in fs.read_file(pre)


def test_foreign_commit_msg_untouched():
    # Hooks de OUTRO nome nunca são tocados.
    fs = _git_repo_fs()
    cm = _hook_path("commit-msg")
    original = "#!/bin/bash\necho meu-commit-msg\n"
    fs.write_file(cm, original)

    BootstrapService(fs).install_hooks("repo")

    assert fs.read_file(cm) == original


def test_hooks_invoke_shim_not_local_python():
    # Os hooks passam a chamar o shim `./harness`, desacoplando-se do layout do
    # core (não mais o python local via CORE_MAIN_REL_PATH/CORE_VENV_PYTHON_REL_PATH).
    fs = _git_repo_fs()
    BootstrapService(fs).install_hooks("repo")

    pre = fs.read_file(_hook_path("pre-commit"))
    post = fs.read_file(_hook_path("post-merge"))
    assert "./harness format" in pre
    assert "./harness decisions" in post
    assert ".venv/bin/python3" not in pre
    assert "src/main.py" not in pre
