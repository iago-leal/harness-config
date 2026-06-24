import os
import pytest
from src.core.bootstrap.init_service import InitializationService
from src.core.ports.fs import FileSystemPort
from src.core.ports.process import ProcessPort
from typing import List, Optional, Tuple


class InitMockFileSystem(FileSystemPort):
    def __init__(self):
        self.files = {
            "harness-core/src/main.py": "print('cli original')",
            "harness-core/src/core/bootstrap/init_service.py": "print('init_service original')",
            "harness-core/requirements.txt": "pydantic\ntoml",
            "harness": "#!/bin/bash\npython3 harness-core/src/main.py $@\n",
            "destino/.git/config": "[core]\nrepositoryformatversion = 0",
        }
        self.dirs = {
            "destino/.git",
            "origem",
            "/Users/iagoleal/dev/harness",
            "destino",
        }

    def _norm(self, path: str) -> str:
        repo_root = "/Users/iagoleal/dev/harness"
        abs_path = os.path.abspath(path)
        if abs_path.startswith(repo_root):
            rel = os.path.relpath(abs_path, repo_root)
            if rel == ".":
                return ""
            if rel.startswith("origem/"):
                return rel[7:]
            elif rel == "origem":
                return ""
            return rel
        return path


    def read_file(self, path: str) -> str:
        path = self._norm(path)
        return self.files.get(path, "")

    def write_file(self, path: str, content: str) -> None:
        path = self._norm(path)
        self.files[path] = content

    def write_file_atomic(self, path: str, content: str) -> None:
        self.write_file(path, content)

    def exists(self, path: str) -> bool:
        path = self._norm(path)
        if path in self.dirs or path == "." or path == "":
            return True
        if path in self.files:
            return True
        for f in self.files:
            if f.startswith(path + "/"):
                return True
        for d in self.dirs:
            if d.startswith(path + "/"):
                return True
        return False

    def list_dir(self, path: str) -> List[str]:
        path = self._norm(path)
        results = set()
        prefix = path + "/" if path != "." and path != "" else ""
        for f in self.files:
            if f.startswith(prefix):
                rel = f[len(prefix):]
                parts = rel.split("/")
                results.add(parts[0])
        for d in self.dirs:
            if d.startswith(prefix):
                rel = d[len(prefix):]
                parts = rel.split("/")
                if parts[0]:
                    results.add(parts[0])
        return list(results)

    def makedirs(self, path: str) -> None:
        path = self._norm(path)
        self.dirs.add(path)

    def remove(self, path: str) -> None:
        path = self._norm(path)
        self.files.pop(path, None)
        self.dirs.discard(path)

    def is_dir(self, path: str) -> bool:
        norm_path = self._norm(path)
        res = False
        if norm_path in self.dirs or norm_path == "." or norm_path == "":
            res = True
        else:
            for f in self.files:
                if f.startswith(norm_path + "/"):
                    res = True
                    break
            if not res:
                for d in self.dirs:
                    if d.startswith(norm_path + "/"):
                        res = True
                        break
        print(f"is_dir({path}) -> norm: {norm_path} -> {res}")
        return res




class MockProcessPort(ProcessPort):
    def __init__(self):
        self.commands = []

    def execute_formatter(
        self, formatter_name: str, file_path: str, executable_path: Optional[str] = None
    ) -> Tuple[int, str, str]:
        return 0, "", ""

    def run_command(self, args: List[str], cwd: Optional[str] = None) -> Tuple[int, str, str]:
        self.commands.append((args, cwd))
        return 0, "mock stdout", "mock stderr"


def test_init_not_git_directory():
    fs = InitMockFileSystem()
    process = MockProcessPort()
    service = InitializationService(fs, process)

    # Inicializar em uma pasta que não tem .git deve falhar barulhento
    with pytest.raises(ValueError, match="não é um repositório git válido"):
        service.initialize_project(target_path="destino-sem-git", upstream_path="harness")


def test_init_success():
    fs = InitMockFileSystem()
    process = MockProcessPort()
    service = InitializationService(fs, process)

    # Executa a inicialização a partir da pasta de origem de simulação
    service.initialize_project(target_path="/Users/iagoleal/dev/harness/destino", active_harness="claude", upstream_path="/Users/iagoleal/dev/harness")

    print("\nCHAVES GRAVADAS:", list(fs.files.keys()))

    # Verifica se os arquivos foram copiados
    assert fs.exists("/Users/iagoleal/dev/harness/destino/harness-core/src/main.py")
    assert fs.exists("/Users/iagoleal/dev/harness/destino/harness-core/src/core/bootstrap/init_service.py")
    assert fs.exists("/Users/iagoleal/dev/harness/destino/harness")
    assert fs.exists("/Users/iagoleal/dev/harness/destino/.harness/decisoes/_cabecalho.md")
    assert fs.exists("/Users/iagoleal/dev/harness/destino/.harness/estado-da-sessao.md")
    assert fs.exists("/Users/iagoleal/dev/harness/destino/harness.toml")

    # Verifica se o harness.toml tem os metadados do upstream gravados
    toml_content = fs.read_file("/Users/iagoleal/dev/harness/destino/harness.toml")
    assert 'upstream_path = "/Users/iagoleal/dev/harness"' in toml_content
    assert 'version = "1.2.43"' in toml_content

    # Verifica se os ganchos git foram instalados e se a venv foi configurada via subprocesso
    assert len(process.commands) >= 1
    # Deve ter rodado python3 -m venv no destino
    venv_cmd = any("venv" in arg for arg, _ in process.commands)
    assert venv_cmd


def test_upgrade_success():
    fs = InitMockFileSystem()
    # Adiciona versão antiga no destino e versão nova na origem
    fs.write_file("/Users/iagoleal/dev/harness/destino/harness.toml", '[harness]\nupstream_path = "/Users/iagoleal/dev/harness/origem"\nversion = "1.2.0"\n')
    fs.write_file("/Users/iagoleal/dev/harness/origem/harness-core/src/main.py", "print('versao nova main')")
    fs.write_file("/Users/iagoleal/dev/harness/origem/harness-core/requirements.txt", "pydantic\ntoml")
    fs.write_file("/Users/iagoleal/dev/harness/origem/harness", "wrapper_novo")
    fs.write_file("/Users/iagoleal/dev/harness/destino/.harness/decisoes/MD-0001.md", "decisao original")

    process = MockProcessPort()
    service = InitializationService(fs, process)

    # Executa upgrade a partir da pasta de destino
    service.upgrade_project(target_path="/Users/iagoleal/dev/harness/destino")

    # Core deve ter sido atualizado com o código do upstream
    assert fs.read_file("/Users/iagoleal/dev/harness/destino/harness-core/src/main.py") == "print('versao nova main')"
    assert fs.read_file("/Users/iagoleal/dev/harness/destino/harness") == "wrapper_novo"

    # Decisões do usuário em .harness/ devem ter sido preservadas
    assert fs.read_file("/Users/iagoleal/dev/harness/destino/.harness/decisoes/MD-0001.md") == "decisao original"
    
    # Configuração de versão deve ter sido atualizada no toml
    assert 'version = "1.2.43"' in fs.read_file("/Users/iagoleal/dev/harness/destino/harness.toml")

