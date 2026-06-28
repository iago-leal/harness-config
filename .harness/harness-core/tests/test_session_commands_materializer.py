"""Testes da materialização dos slash commands de sessão (feature 010, T002).

Cobrem:
- grava `.claude/commands/encerrar-sessao.md` e `.agent/workflows/encerrar-sessao.md`;
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
    # feature 017: caminho singular reconhecido pelo Antigravity.
    return os.path.join(project, ".agent", "workflows", "encerrar-sessao.md")


def _antigravity_stale_path(project: str) -> str:
    # Caminho plural legado (gerado por versões anteriores), a ser limpo.
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


# --- feature 017: migração do órfão `.agents/workflows/` -> `.agent/workflows/` ---


def test_remove_orfao_do_caminho_plural_legado():
    project = "/Users/iagoleal/projeto-x"
    stale = _antigravity_stale_path(project)
    fs = MockFileSystem()
    fs.existing_files.add(stale)
    fs.written_files[stale] = "workflow antigo (plural)"

    materialize_session_commands(fs, project, project)

    # Grava no caminho novo (singular)...
    assert fs.exists(_antigravity_path(project))
    # ...e remove o órfão do caminho plural legado.
    assert not fs.exists(stale)


def test_preserva_workflow_de_terceiro_no_diretorio_plural():
    project = "/Users/iagoleal/projeto-x"
    stale = _antigravity_stale_path(project)
    terceiro = os.path.join(project, ".agents", "workflows", "outro-workflow.md")
    fs = MockFileSystem()
    fs.existing_files.update({stale, terceiro})
    fs.written_files[stale] = "workflow antigo"
    fs.written_files[terceiro] = "workflow de terceiro"

    materialize_session_commands(fs, project, project)

    assert not fs.exists(stale)
    # Terceiro intacto: a limpeza remove só o arquivo nomeado (não-destrutivo, RN-03).
    assert fs.read_file(terceiro) == "workflow de terceiro"


def test_sem_orfao_projeto_novo_nao_falha():
    fs = MockFileSystem()
    project = "/Users/iagoleal/projeto-x"

    materialize_session_commands(fs, project, project)

    assert fs.exists(_antigravity_path(project))
    assert not fs.exists(_antigravity_stale_path(project))


def test_perfil_sem_stale_paths_nao_remove_nada():
    from src.core.install.harness_profiles import HarnessProfile

    class FakeProfile(HarnessProfile):
        name = "fake"

        def hooks_block(self):
            return ""

        def apply_instructions(self):
            return ""

        def session_command_artifact(self, command_path):
            return (".fake/cmd.md", "x")

        # sem override de stale_session_command_paths -> default [].

    project = "/proj"
    pre_existente = os.path.join(project, ".agents", "workflows", "encerrar-sessao.md")
    fs = MockFileSystem()
    fs.existing_files.add(pre_existente)
    fs.written_files[pre_existente] = "intacto"

    materialize_session_commands(fs, project, project, profiles=[FakeProfile()])

    # FakeProfile não declara órfãos -> nada é removido.
    assert fs.exists(pre_existente)
