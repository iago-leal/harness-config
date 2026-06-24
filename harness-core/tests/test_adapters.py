import os
import pytest
import re
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


def test_subprocess_git_adapter():
    adapter = SubprocessGitAdapter()
    repo_path = "/Users/iagoleal/dev/harness"

    # Testa se rev-parse HEAD retorna um hash SHA1 de 40 hexadecimais
    try:
        head_commit = adapter.get_head_commit(repo_path)
        assert len(head_commit) == 40
        assert re.match(r"^[a-f0-9]{40}$", head_commit)
    except RuntimeError as e:
        pytest.fail(f"Erro ao obter HEAD do Git: {e}")


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
