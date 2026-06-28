import os
import pytest
from src.core.bootstrap.init_service import (
    InitializationService,
    UpstreamVersionUndeterminedError,
)
from src.core.ports.fs import FileSystemPort
from src.core.ports.process import ProcessPort
from typing import List, Optional, Tuple


class InitMockFileSystem(FileSystemPort):
    def __init__(self):
        self.files = {
            ".harness/harness-core/src/main.py": "print('cli original')",
            ".harness/harness-core/src/core/bootstrap/init_service.py": "print('init_service original')",
            ".harness/harness-core/requirements.txt": "pydantic\ntoml",
            "harness": "#!/bin/bash\npython3 .harness/harness-core/src/main.py $@\n",
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
    assert fs.exists(
        "/Users/iagoleal/dev/harness/destino/.harness/harness-core/src/main.py"
    )
    assert fs.exists(
        "/Users/iagoleal/dev/harness/destino/.harness/harness-core/src/core/bootstrap/init_service.py"
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
    assert 'version = "1.2.55"' in toml_content

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
        "/Users/iagoleal/dev/harness/origem/.harness/harness-core/src/main.py",
        "print('versao nova main')",
    )
    fs.write_file(
        "/Users/iagoleal/dev/harness/origem/.harness/harness-core/requirements.txt",
        "pydantic\ntoml",
    )
    fs.write_file("/Users/iagoleal/dev/harness/origem/harness", "wrapper_novo")
    # Novo contrato (feature 012): a versão do upstream é lida de um config.py
    # determinável (sem mais fallback silencioso) e a venv do destino precisa
    # existir para o subprocesso de bootstrap/materialização.
    fs.write_file(
        "/Users/iagoleal/dev/harness/origem/.harness/harness-core/src/core/domain/config.py",
        'version: str = "1.2.47"',
    )
    fs.write_file(
        "/Users/iagoleal/dev/harness/destino/.harness/harness-core/.venv/bin/python3",
        "",
    )
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
        fs.read_file(
            "/Users/iagoleal/dev/harness/destino/.harness/harness-core/src/main.py"
        )
        == "print('versao nova main')"
    )
    assert fs.read_file("/Users/iagoleal/dev/harness/destino/harness") == "wrapper_novo"

    # Decisões do usuário em .harness/ devem ter sido preservadas
    assert (
        fs.read_file("/Users/iagoleal/dev/harness/destino/.harness/decisoes/MD-0001.md")
        == "decisao original"
    )

    # Configuração de versão deve ter sido atualizada no toml
    assert 'version = "1.2.47"' in fs.read_file(
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
        "/Users/iagoleal/dev/harness/origem/.harness/harness-core/src/main.py",
        "print('novo')",
    )
    fs.write_file(
        "/Users/iagoleal/dev/harness/origem/.harness/harness-core/.harness/microdecisoes.md",
        "lixo de runtime do upstream",
    )
    fs.write_file(
        "/Users/iagoleal/dev/harness/origem/.harness/harness-core/src/core/domain/config.py",
        'version: str = "1.2.47"',
    )
    fs.write_file(
        "/Users/iagoleal/dev/harness/destino/.harness/harness-core/.venv/bin/python3",
        "",
    )

    process = MockProcessPort()
    service = InitializationService(fs, process)

    service.upgrade_project(target_path="/Users/iagoleal/dev/harness/destino")

    # O core foi atualizado...
    assert (
        fs.read_file(
            "/Users/iagoleal/dev/harness/destino/.harness/harness-core/src/main.py"
        )
        == "print('novo')"
    )
    # ...mas o .harness/ do upstream não viajou para o alvo.
    assert (
        fs.read_file(
            "/Users/iagoleal/dev/harness/destino/.harness/harness-core/.harness/microdecisoes.md"
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


def test_upgrade_invokes_materialize_subprocess():
    """Feature 012 (Modo 1): o upgrade NÃO materializa in-process — delega ao
    subcomando `materialize` rodado via subprocesso do python de DESTINO, para
    usar o código recém-copiado e nunca os módulos antigos em memória.
    """
    fs = InitMockFileSystem()
    fs.write_file(
        "/Users/iagoleal/dev/harness/destino/harness.toml",
        '[harness]\nactive_harness = "claude"\nupstream_path = "/Users/iagoleal/dev/harness/origem"\nversion = "1.2.0"\n',
    )
    fs.write_file(
        "/Users/iagoleal/dev/harness/origem/.harness/harness-core/src/main.py",
        "print('versao nova main')",
    )
    fs.write_file(
        "/Users/iagoleal/dev/harness/origem/.harness/harness-core/src/core/domain/config.py",
        'version: str = "1.2.47"',
    )
    fs.write_file("/Users/iagoleal/dev/harness/origem/harness", "wrapper_novo")
    fs.write_file(
        "/Users/iagoleal/dev/harness/destino/.harness/harness-core/.venv/bin/python3",
        "",
    )

    process = MockProcessPort()
    service = InitializationService(fs, process)
    service.upgrade_project(target_path="/Users/iagoleal/dev/harness/destino")

    materialize_calls = [
        (arg, cwd) for arg, cwd in process.commands if arg and arg[-1] == "materialize"
    ]
    assert materialize_calls, "upgrade deve invocar o subcomando materialize"
    arg, cwd = materialize_calls[0]
    assert arg[0].endswith("/.venv/bin/python3")
    assert arg[1].endswith("/src/main.py")
    assert "/destino/.harness/harness-core/" in arg[0]
    assert cwd == "/Users/iagoleal/dev/harness/destino"


def test_upgrade_aborts_on_indeterminate_version():
    """Feature 012 (Modo 2): sem config.py determinável no upstream e sem
    --force, o upgrade ABORTA barulhento — não cai em fallback nem finge sucesso.
    """
    fs = InitMockFileSystem()
    fs.write_file(
        "/Users/iagoleal/dev/harness/destino/harness.toml",
        '[harness]\nupstream_path = "/Users/iagoleal/dev/harness/origem"\nversion = "1.2.0"\n',
    )
    fs.write_file(
        "/Users/iagoleal/dev/harness/origem/.harness/harness-core/src/main.py",
        "print('novo')",
    )
    fs.write_file("/Users/iagoleal/dev/harness/origem/harness", "wrapper_novo")

    process = MockProcessPort()
    service = InitializationService(fs, process)
    with pytest.raises(UpstreamVersionUndeterminedError):
        service.upgrade_project(target_path="/Users/iagoleal/dev/harness/destino")
    # Aborta antes de qualquer cópia ou subprocesso.
    assert process.commands == []


def test_upgrade_force_bypasses_version_compare():
    """Feature 012 (--force): com versões IGUAIS, --force força a recópia e a
    rematerialização em vez de encerrar cedo por igualdade de versão.
    """
    fs = InitMockFileSystem()
    fs.write_file(
        "/Users/iagoleal/dev/harness/destino/harness.toml",
        '[harness]\nupstream_path = "/Users/iagoleal/dev/harness/origem"\nversion = "1.2.47"\n',
    )
    fs.write_file(
        "/Users/iagoleal/dev/harness/origem/.harness/harness-core/src/main.py",
        "print('mesma versao, conteudo novo')",
    )
    fs.write_file(
        "/Users/iagoleal/dev/harness/origem/.harness/harness-core/src/core/domain/config.py",
        'version: str = "1.2.47"',
    )
    fs.write_file("/Users/iagoleal/dev/harness/origem/harness", "wrapper_novo")
    fs.write_file(
        "/Users/iagoleal/dev/harness/destino/.harness/harness-core/.venv/bin/python3",
        "",
    )

    process = MockProcessPort()
    service = InitializationService(fs, process)

    # Sem --force: versões iguais -> no-op (nenhum subprocesso).
    service.upgrade_project(target_path="/Users/iagoleal/dev/harness/destino")
    assert process.commands == []

    # Com --force: copia e rematerializa mesmo com versões iguais.
    service.upgrade_project(
        target_path="/Users/iagoleal/dev/harness/destino", force=True
    )
    assert (
        fs.read_file(
            "/Users/iagoleal/dev/harness/destino/.harness/harness-core/src/main.py"
        )
        == "print('mesma versao, conteudo novo')"
    )
    assert any(arg and arg[-1] == "materialize" for arg, _ in process.commands), (
        "upgrade --force deve rematerializar"
    )


def test_init_materializes_session_skill_for_both_harnesses():
    """Feature 018: init grava a skill `encerrar-sessao` para Claude E Antigravity,
    independente do active_harness.

    O `active_harness` é propositalmente 'gemini' para provar a incondicionalidade:
    a skill precisa surgir para Claude E Antigravity mesmo quando nenhum dos dois
    é o harness ativo (D-04).
    """
    fs = InitMockFileSystem()
    process = MockProcessPort()
    service = InitializationService(fs, process)

    service.initialize_project(
        target_path="/Users/iagoleal/dev/harness/destino",
        active_harness="gemini",
        upstream_path="/Users/iagoleal/dev/harness",
    )

    base = "/Users/iagoleal/dev/harness/destino"
    claude_skill = f"{base}/.claude/skills/encerrar-sessao/SKILL.md"
    agy_skill = f"{base}/.agents/skills/encerrar-sessao/SKILL.md"
    claude_entry = f"{base}/.claude/skills/encerrar-sessao/scripts/encerrar_sessao.py"
    assert fs.exists(claude_skill)
    assert fs.exists(agy_skill)
    assert fs.exists(claude_entry)
    # A skill é agnóstica: front-matter com a capacidade, sem caminho chumbado.
    assert "encerrar-sessao" in fs.read_file(claude_skill)


def test_get_upstream_version_reads_canonical_layout():
    """Feature 012: a versão vem do config.py no layout canônico."""
    fs = InitMockFileSystem()
    fs.write_file(
        "/Users/iagoleal/dev/harness/origem/.harness/harness-core/src/core/domain/config.py",
        'version: str = "9.9.9"',
    )
    service = InitializationService(fs, MockProcessPort())
    assert (
        service._get_upstream_version("/Users/iagoleal/dev/harness/origem") == "9.9.9"
    )


def test_get_upstream_version_falls_back_to_legacy_layout():
    """Feature 012: se o canônico não existe, lê o config.py no layout legado
    (core na raiz) — resiliência durante a transição de layout do upstream.
    """
    fs = InitMockFileSystem()
    fs.write_file(
        "/Users/iagoleal/dev/harness/origem/harness-core/src/core/domain/config.py",
        'version: str = "8.8.8"',
    )
    service = InitializationService(fs, MockProcessPort())
    assert (
        service._get_upstream_version("/Users/iagoleal/dev/harness/origem") == "8.8.8"
    )


def test_get_upstream_version_raises_when_no_candidate():
    """Feature 012 (RN-04): nenhum candidato -> erro barulhento, sem fallback
    silencioso para a versão local.
    """
    fs = InitMockFileSystem()
    service = InitializationService(fs, MockProcessPort())
    with pytest.raises(UpstreamVersionUndeterminedError):
        service._get_upstream_version("/Users/iagoleal/dev/harness/origem")
