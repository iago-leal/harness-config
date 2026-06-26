"""Testes da materialização dos slash commands de sessão (feature 010, T002).

Cobrem:
- grava `.claude/commands/encerrar-sessao.md` e `.agents/workflows/encerrar-sessao.md`;
- Claude usa `./harness` relativo à raiz; Antigravity usa o `command_path` absoluto;
- escrita atômica via `write_file_atomic`;
- idempotência na reexecução;
- preserva arquivos de terceiros nos diretórios de comando;
- nenhuma escrita fora do `project_path` (footprint global zero).
"""

import os

from src.core.install.session_commands import materialize_session_commands
from tests.helpers import MockFileSystem, RecordingFileSystem


def _claude_path(project: str) -> str:
    return os.path.join(project, ".claude", "commands", "encerrar-sessao.md")


def _antigravity_path(project: str) -> str:
    return os.path.join(project, ".agents", "workflows", "encerrar-sessao.md")


def test_materializa_os_dois_arquivos_em_projeto_vazio():
    fs = MockFileSystem()
    project = "/Users/iagoleal/projeto-x"

    materialize_session_commands(fs, project, project)

    assert fs.exists(_claude_path(project))
    assert fs.exists(_antigravity_path(project))


def test_claude_resolve_raiz_via_git():
    fs = MockFileSystem()
    project = "/Users/iagoleal/projeto-x"

    materialize_session_commands(fs, project, "/abs/projeto-x")

    content = fs.read_file(_claude_path(project))
    # `cd` para a raiz do git antes de `./harness`: funciona de qualquer
    # subdiretório (o `!`-bash não garante cwd na raiz).
    assert (
        'cd "$(git rev-parse --show-toplevel)" && ./harness cmd encerrar-sessao'
        in content
    )
    assert "${CLAUDE_PROJECT_DIR}" not in content


def test_antigravity_usa_command_path_absoluto():
    fs = MockFileSystem()
    project = "/Users/iagoleal/projeto-x"
    command_path = "/abs/projeto-x"

    materialize_session_commands(fs, project, command_path)

    content = fs.read_file(_antigravity_path(project))
    assert f"{command_path}/harness cmd encerrar-sessao" in content


def test_escreve_de_forma_atomica():
    class AtomicSpyFS(MockFileSystem):
        def __init__(self):
            super().__init__()
            self.atomic_writes = []

        def write_file_atomic(self, path, content):
            self.atomic_writes.append(path)
            super().write_file_atomic(path, content)

    fs = AtomicSpyFS()
    project = "/Users/iagoleal/projeto-x"

    materialize_session_commands(fs, project, project)

    assert _claude_path(project) in fs.atomic_writes
    assert _antigravity_path(project) in fs.atomic_writes


def test_preserva_arquivos_de_terceiros_nos_diretorios():
    project = "/Users/iagoleal/projeto-x"
    outro = os.path.join(project, ".claude", "commands", "outro-comando.md")
    fs = MockFileSystem()
    fs.existing_files.add(outro)
    fs.written_files[outro] = "comando do usuário"

    materialize_session_commands(fs, project, project)

    assert fs.exists(_claude_path(project))
    # O comando de terceiro permanece intacto (não-destrutivo).
    assert fs.read_file(outro) == "comando do usuário"


def test_idempotente_na_reexecucao():
    fs = MockFileSystem()
    project = "/Users/iagoleal/projeto-x"

    materialize_session_commands(fs, project, "/abs/projeto-x")
    primeiro = fs.read_file(_claude_path(project))
    materialize_session_commands(fs, project, "/abs/projeto-x")

    assert fs.read_file(_claude_path(project)) == primeiro


def test_nada_e_escrito_fora_do_project_path():
    project_root = "/Users/iagoleal/projeto-x"
    fs = RecordingFileSystem(repo_root=project_root)

    materialize_session_commands(fs, project_root, project_root)

    for p in fs.writes:
        abs_p = os.path.abspath(os.path.join(project_root, p))
        assert abs_p == project_root or abs_p.startswith(project_root + os.sep)
    assert any("encerrar-sessao.md" in p for p in fs.writes)
