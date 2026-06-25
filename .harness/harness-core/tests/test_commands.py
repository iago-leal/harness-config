from unittest.mock import MagicMock
from src.core.ports.git import GitPort
from src.core.commands.service import CommandService
from src.core.domain.models import SessionState
from tests.helpers import MockFileSystem


def test_load_and_save_session():
    fs = MockFileSystem()
    git = MagicMock(spec=GitPort)
    service = CommandService(fs, git)
    session_file = "session.md"

    # Salva sessão
    state = SessionState(commit_hash="a" * 40, active_feature="my-feat")
    service.save_session(session_file, state)

    assert fs.exists(session_file)

    # Carrega sessão
    loaded = service.load_session(session_file)
    assert loaded is not None
    assert loaded.active_feature == "my-feat"
    assert loaded.commit_hash == "a" * 40
    assert loaded.is_active is True


def test_execute_encerrar_sessao():
    fs = MockFileSystem()
    git = MagicMock(spec=GitPort)
    service = CommandService(fs, git)
    session_file = "session.md"
    repo_path = "repo/"

    # Prepara sessão ativa
    initial_commit = "a" * 40
    state = SessionState(commit_hash=initial_commit, active_feature="feat-1")
    service.save_session(session_file, state)

    # Configura git mock
    new_commit = "b" * 40
    git.get_head_commit.return_value = new_commit

    # Executa comando
    msg = service.execute_command("encerrar-sessao", [], repo_path, session_file)
    assert "Sessão encerrada com sucesso" in msg
    assert new_commit in msg

    # Carrega para confirmar
    loaded = service.load_session(session_file)
    assert loaded.is_active is False
    assert loaded.commit_hash == new_commit


def test_execute_resume_alignment_warning():
    fs = MockFileSystem()
    git = MagicMock(spec=GitPort)
    service = CommandService(fs, git)
    session_file = "session.md"
    repo_path = "repo/"

    # Salva sessão com um commit antigo
    old_commit = "a" * 40
    state = SessionState(
        commit_hash=old_commit, active_feature="feat-1", is_active=False
    )
    service.save_session(session_file, state)

    # Git mock retorna um commit diferente (divergente)
    current_commit = "b" * 40
    git.get_head_commit.return_value = current_commit

    # Executa resume
    msg = service.execute_command("resume", [], repo_path, session_file)

    # Deve emitir o Alerta de divergência Git
    assert "ALERTA: O commit HEAD atual" in msg
    assert "diverge do commit âncora" in msg

    # Verifica que ativou a sessão no novo commit
    loaded = service.load_session(session_file)
    assert loaded.is_active is True
    assert loaded.commit_hash == current_commit


def test_execute_clarificar_and_handoff():
    fs = MockFileSystem()
    git = MagicMock(spec=GitPort)
    service = CommandService(fs, git)
    session_file = "session.md"
    repo_path = "repo/"

    git.get_head_commit.return_value = "a" * 40

    # Teste Clarificar
    msg_clarify = service.execute_command("clarificar", [], repo_path, session_file)
    assert "limitado a no máximo **2 rodadas**" in msg_clarify

    # Teste Handoff
    msg_handoff = service.execute_command("handoff", [], repo_path, session_file)
    assert "Handoff Bastão" in msg_handoff
    assert "a" * 40 in msg_handoff
