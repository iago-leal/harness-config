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
                rel = f[len(prefix) :]
                parts = rel.split("/")
                results.add(parts[0])
        for d in self.dirs:
            if d.startswith(prefix):
                rel = d[len(prefix) :]
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

    def make_executable(self, path: str) -> None:
        pass


class MockProcessPort(ProcessPort):
    def __init__(self):
        self.commands = []

    def execute_formatter(
        self, formatter_name: str, file_path: str, executable_path: Optional[str] = None
    ) -> Tuple[int, str, str]:
        return 0, "", ""

    def run_command(
        self, args: List[str], cwd: Optional[str] = None
    ) -> Tuple[int, str, str]:
        self.commands.append((args, cwd))
        return 0, "mock stdout", "mock stderr"


def test_init_not_git_directory():
    fs = InitMockFileSystem()
    process = MockProcessPort()
    service = InitializationService(fs, process)

    # Inicializar em uma pasta que não tem .git deve falhar barulhento
    with pytest.raises(ValueError, match="não é um repositório git válido"):
        service.initialize_project(
            target_path="destino-sem-git", upstream_path="harness"
        )


def test_init_success():
    fs = InitMockFileSystem()
    process = MockProcessPort()
    service = InitializationService(fs, process)

    # Executa a inicialização a partir da pasta de origem de simulação
    service.initialize_project(
        target_path="/Users/iagoleal/dev/harness/destino",
        active_harness="claude",
        upstream_path="/Users/iagoleal/dev/harness",
    )

    print("\nCHAVES GRAVADAS:", list(fs.files.keys()))

    # Verifica se os arquivos foram copiados
    assert fs.exists("/Users/iagoleal/dev/harness/destino/harness-core/src/main.py")
    assert fs.exists(
        "/Users/iagoleal/dev/harness/destino/harness-core/src/core/bootstrap/init_service.py"
    )
    assert fs.exists("/Users/iagoleal/dev/harness/destino/harness")
    assert fs.exists(
        "/Users/iagoleal/dev/harness/destino/.harness/decisoes/_cabecalho.md"
    )
    assert fs.exists("/Users/iagoleal/dev/harness/destino/.harness/estado-da-sessao.md")
    assert fs.exists("/Users/iagoleal/dev/harness/destino/harness.toml")

    # Verifica se o harness.toml tem os metadados do upstream gravados
    toml_content = fs.read_file("/Users/iagoleal/dev/harness/destino/harness.toml")
    assert 'upstream_path = "/Users/iagoleal/dev/harness"' in toml_content
    assert 'version = "1.2.46"' in toml_content

    # Verifica se os ganchos git foram instalados e se a venv foi configurada via subprocesso
    assert len(process.commands) >= 1
    # Deve ter rodado python3 -m venv no destino
    venv_cmd = any("venv" in arg for arg, _ in process.commands)
    assert venv_cmd


def test_upgrade_success():
    fs = InitMockFileSystem()
    # Adiciona versão antiga no destino e versão nova na origem
    fs.write_file(
        "/Users/iagoleal/dev/harness/destino/harness.toml",
        '[harness]\nupstream_path = "/Users/iagoleal/dev/harness/origem"\nversion = "1.2.0"\n',
    )
    fs.write_file(
        "/Users/iagoleal/dev/harness/origem/harness-core/src/main.py",
        "print('versao nova main')",
    )
    fs.write_file(
        "/Users/iagoleal/dev/harness/origem/harness-core/requirements.txt",
        "pydantic\ntoml",
    )
    fs.write_file("/Users/iagoleal/dev/harness/origem/harness", "wrapper_novo")
    fs.write_file(
        "/Users/iagoleal/dev/harness/destino/.harness/decisoes/MD-0001.md",
        "decisao original",
    )

    process = MockProcessPort()
    service = InitializationService(fs, process)

    # Executa upgrade a partir da pasta de destino
    service.upgrade_project(target_path="/Users/iagoleal/dev/harness/destino")

    # Core deve ter sido atualizado com o código do upstream
    assert (
        fs.read_file("/Users/iagoleal/dev/harness/destino/harness-core/src/main.py")
        == "print('versao nova main')"
    )
    assert fs.read_file("/Users/iagoleal/dev/harness/destino/harness") == "wrapper_novo"

    # Decisões do usuário em .harness/ devem ter sido preservadas
    assert (
        fs.read_file("/Users/iagoleal/dev/harness/destino/.harness/decisoes/MD-0001.md")
        == "decisao original"
    )

    # Configuração de versão deve ter sido atualizada no toml
    assert 'version = "1.2.46"' in fs.read_file(
        "/Users/iagoleal/dev/harness/destino/harness.toml"
    )


def test_upgrade_nao_propaga_harness_runtime():
    # Regressão: .harness/ é estado de runtime por-instalação (sessão,
    # microdecisões). O upgrade jamais deve copiá-lo do upstream para o alvo —
    # senão polui o projeto e pode até sobrescrever o estado local.
    fs = InitMockFileSystem()
    fs.write_file(
        "/Users/iagoleal/dev/harness/destino/harness.toml",
        '[harness]\nupstream_path = "/Users/iagoleal/dev/harness/origem"\nversion = "1.2.0"\n',
    )
    fs.write_file(
        "/Users/iagoleal/dev/harness/origem/harness-core/src/main.py",
        "print('novo')",
    )
    fs.write_file(
        "/Users/iagoleal/dev/harness/origem/harness-core/.harness/microdecisoes.md",
        "lixo de runtime do upstream",
    )

    process = MockProcessPort()
    service = InitializationService(fs, process)

    service.upgrade_project(target_path="/Users/iagoleal/dev/harness/destino")

    # O core foi atualizado...
    assert (
        fs.read_file("/Users/iagoleal/dev/harness/destino/harness-core/src/main.py")
        == "print('novo')"
    )
    # ...mas o .harness/ do upstream não viajou para o alvo.
    assert (
        fs.read_file(
            "/Users/iagoleal/dev/harness/destino/harness-core/.harness/microdecisoes.md"
        )
        == ""
    )


def test_init_antigravity_materializes_hooks_json():
    """Cobre a fiação init -> materialize_hooks_json (não só a rotina isolada).

    Antes da feature 009, `materialize_hooks_json` era chamado mas nunca importado;
    este teste exercita o ramo `active_harness="antigravity"` ponta-a-ponta para
    barrar a regressão do NameError no CI.
    """
    fs = InitMockFileSystem()
    process = MockProcessPort()
    service = InitializationService(fs, process)

    service.initialize_project(
        target_path="/Users/iagoleal/dev/harness/destino",
        active_harness="antigravity",
        upstream_path="/Users/iagoleal/dev/harness",
    )

    hooks_path = "/Users/iagoleal/dev/harness/destino/.agents/hooks.json"
    assert fs.exists(hooks_path)
    content = fs.read_file(hooks_path)
    assert '"harness"' in content
    # O `<ABS>` deve ter sido resolvido para o caminho absoluto do projeto-alvo.
    assert "/Users/iagoleal/dev/harness/destino/harness agy-hook" in content
    assert "<ABS>" not in content


def test_upgrade_antigravity_materializes_hooks_json():
    """Cobre a fiação upgrade -> materialize_hooks_json para harness antigravity."""
    fs = InitMockFileSystem()
    fs.write_file(
        "/Users/iagoleal/dev/harness/destino/harness.toml",
        '[harness]\nactive_harness = "antigravity"\nupstream_path = "/Users/iagoleal/dev/harness/origem"\nversion = "1.2.0"\n',
    )
    fs.write_file(
        "/Users/iagoleal/dev/harness/origem/harness-core/src/main.py",
        "print('versao nova main')",
    )
    fs.write_file(
        "/Users/iagoleal/dev/harness/origem/harness-core/requirements.txt",
        "pydantic\ntoml",
    )
    fs.write_file("/Users/iagoleal/dev/harness/origem/harness", "wrapper_novo")

    process = MockProcessPort()
    service = InitializationService(fs, process)

    service.upgrade_project(target_path="/Users/iagoleal/dev/harness/destino")

    hooks_path = "/Users/iagoleal/dev/harness/destino/.agents/hooks.json"
    assert fs.exists(hooks_path)
    content = fs.read_file(hooks_path)
    assert '"harness"' in content
    assert "/Users/iagoleal/dev/harness/destino/harness agy-hook" in content
    assert "<ABS>" not in content


def test_init_materializes_session_commands_for_both_harnesses():
    """Feature 010: init grava os dois comandos de IDE, independente do active_harness.

    O `active_harness` é propositalmente 'gemini' para provar a incondicionalidade:
    o comando precisa surgir para Claude E Antigravity mesmo quando nenhum dos dois
    é o harness ativo (D-03).
    """
    fs = InitMockFileSystem()
    process = MockProcessPort()
    service = InitializationService(fs, process)

    service.initialize_project(
        target_path="/Users/iagoleal/dev/harness/destino",
        active_harness="gemini",
        upstream_path="/Users/iagoleal/dev/harness",
    )

    claude_cmd = (
        "/Users/iagoleal/dev/harness/destino/.claude/commands/encerrar-sessao.md"
    )
    agy_cmd = "/Users/iagoleal/dev/harness/destino/.agents/workflows/encerrar-sessao.md"
    assert fs.exists(claude_cmd)
    assert fs.exists(agy_cmd)
    assert "harness cmd encerrar-sessao" in fs.read_file(claude_cmd)
    # O Antigravity embute o caminho absoluto do wrapper do projeto.
    assert (
        "/Users/iagoleal/dev/harness/destino/harness cmd encerrar-sessao"
        in fs.read_file(agy_cmd)
    )


def test_upgrade_materializes_session_commands():
    """Feature 010: upgrade (re)materializa os dois comandos de IDE."""
    fs = InitMockFileSystem()
    fs.write_file(
        "/Users/iagoleal/dev/harness/destino/harness.toml",
        '[harness]\nactive_harness = "claude"\nupstream_path = "/Users/iagoleal/dev/harness/origem"\nversion = "1.2.0"\n',
    )
    fs.write_file(
        "/Users/iagoleal/dev/harness/origem/harness-core/src/main.py",
        "print('versao nova main')",
    )
    fs.write_file(
        "/Users/iagoleal/dev/harness/origem/harness-core/requirements.txt",
        "pydantic\ntoml",
    )
    fs.write_file("/Users/iagoleal/dev/harness/origem/harness", "wrapper_novo")

    process = MockProcessPort()
    service = InitializationService(fs, process)

    service.upgrade_project(target_path="/Users/iagoleal/dev/harness/destino")

    claude_cmd = (
        "/Users/iagoleal/dev/harness/destino/.claude/commands/encerrar-sessao.md"
    )
    agy_cmd = "/Users/iagoleal/dev/harness/destino/.agents/workflows/encerrar-sessao.md"
    assert fs.exists(claude_cmd)
    assert fs.exists(agy_cmd)
