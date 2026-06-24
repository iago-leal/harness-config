import os
import re
import subprocess
from src.adapters.fs.local import LocalFileSystemAdapter
from src.adapters.git.subprocess import SubprocessGitAdapter
from src.adapters.process.formatter import HostFormatterAdapter


def test_local_file_system_adapter(tmp_path):
    adapter = LocalFileSystemAdapter()
    test_file = os.path.join(tmp_path, "test.txt")

    # Escrita normal
    adapter.write_file(test_file, "conteudo normal")
    assert adapter.exists(test_file)
    assert adapter.read_file(test_file) == "conteudo normal"

    # Escrita atômica
    adapter.write_file_atomic(test_file, "conteudo atomico")
    assert adapter.exists(test_file)
    assert adapter.read_file(test_file) == "conteudo atomico"

    # Listar dir e remoção
    files = adapter.list_dir(str(tmp_path))
    assert "test.txt" in files

    adapter.remove(test_file)
    assert not adapter.exists(test_file)


def test_subprocess_git_adapter(tmp_path):
    adapter = SubprocessGitAdapter()
    repo_path = str(tmp_path)

    # Repositório portável com um commit, para o rev-parse ter um HEAD.
    # (O teste anterior chumbava /Users/iagoleal/dev/harness e falhava no CI.)
    adapter.init_repo(repo_path)
    run = dict(cwd=repo_path, capture_output=True, check=True)
    subprocess.run(["git", "config", "user.email", "ci@example.com"], **run)
    subprocess.run(["git", "config", "user.name", "CI"], **run)
    subprocess.run(["git", "commit", "--allow-empty", "-m", "init"], **run)

    head_commit = adapter.get_head_commit(repo_path)
    assert len(head_commit) == 40
    assert re.match(r"^[a-f0-9]{40}$", head_commit)


def test_subprocess_git_adapter_init_repo(tmp_path):
    adapter = SubprocessGitAdapter()
    # init_repo deve criar um repositório git novo no diretório vazio.
    assert not os.path.exists(os.path.join(tmp_path, ".git"))
    adapter.init_repo(str(tmp_path))
    assert os.path.isdir(os.path.join(tmp_path, ".git"))


def test_host_formatter_adapter_non_existent():
    adapter = HostFormatterAdapter()
    # Executa formatador inexistente e deve retornar 127 (command not found)
    exit_code, stdout, stderr = adapter.execute_formatter(
        formatter_name="nonexistent_formatter_cmd", file_path="dummy.txt"
    )
    assert exit_code == 127
    assert "não encontrado" in stderr
