import os
from src.core.bootstrap.service import BootstrapService
from tests.helpers import MockFileSystem

def test_bootstrap_install_hooks_shadow():
    fs = MockFileSystem()
    service = BootstrapService(fs)
    repo_path = "repo"

    installed = service.install_hooks(repo_path, shadow_mode=True)
    
    assert len(installed) == 2
    pre_commit = os.path.join(repo_path, ".git", "hooks", "pre-commit")
    post_merge = os.path.join(repo_path, ".git", "hooks", "post-merge")
    
    assert pre_commit in installed
    assert post_merge in installed
    
    assert fs.exists(pre_commit)
    assert fs.exists(post_merge)

    # Verifica se os ganchos estão configurados em modo shadow
    pre_content = fs.read_file(pre_commit)
    assert "Parallel Run (Shadow)" in pre_content
    assert "format --shadow" in pre_content
    assert "shadow-validation.log" in pre_content

    post_content = fs.read_file(post_merge)
    assert "Parallel Run (Shadow)" in post_content
    assert "decisions --shadow" in post_content
    assert "shadow-validation.log" in post_content

def test_bootstrap_install_hooks_active():
    fs = MockFileSystem()
    service = BootstrapService(fs)
    repo_path = "repo"

    installed = service.install_hooks(repo_path, shadow_mode=False)
    
    assert len(installed) == 2
    pre_commit = os.path.join(repo_path, ".git", "hooks", "pre-commit")
    post_merge = os.path.join(repo_path, ".git", "hooks", "post-merge")
    
    assert fs.exists(pre_commit)
    assert fs.exists(post_merge)

    # Verifica se os ganchos estão em modo ativo direto
    pre_content = fs.read_file(pre_commit)
    assert "Hook pre-commit ativo" in pre_content
    assert "format --shadow" not in pre_content

    post_content = fs.read_file(post_merge)
    assert "Hook post-merge ativo" in post_content
    assert "decisions --shadow" not in post_content
