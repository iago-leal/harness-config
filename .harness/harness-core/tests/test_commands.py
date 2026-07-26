from unittest.mock import MagicMock
import pytest
from src.core.ports.git import GitPort
from src.core.commands.service import CommandService
from src.core.commands.errors import SessionCommitError
from src.core.domain.models import SessionState
from tests.helpers import MockFileSystem


class FakeGit(GitPort):
    """Git fake que modela a transição de HEAD ao commitar.

    ``get_head_commit`` devolve o HEAD corrente; ``commit_paths`` registra a
    chamada, avança o HEAD para o hash do commit de encerramento e o devolve.
    Assim o teste asseria que a âncora gravada é o HEAD PRÉ-commit.
    """

    CLOSING_HEAD = "c" * 40

    def __init__(self, head: str):
        self._head = head
        self.commit_calls = []  # lista de (repo_path, paths, message)

    def get_head_commit(self, repo_path: str) -> str:
        return self._head

    def get_remote_commit(
        self, repo_path: str, remote_name: str = "origin", branch_name: str = "main"
    ) -> str:
        return self._head

    def init_repo(self, repo_path: str) -> None:
        pass

    def commit_paths(self, repo_path: str, paths: list[str], message: str) -> str:
        self.commit_calls.append((repo_path, list(paths), message))
        self._head = self.CLOSING_HEAD
        return self._head

    # Capacidades de fim de sessão (feature 014): defaults inócuos — o
    # CommandService não as usa; existem só para o fake satisfazer o contrato.
    def fetch(
        self, repo_path: str, remote: str = "origin", branch: str | None = None
    ) -> None:
        pass

    def get_current_branch(self, repo_path: str) -> str:
        return "main"

    def get_default_branch(self, repo_path: str, remote: str = "origin") -> str:
        return "main"

    def count_commits_ahead(self, repo_path: str, rev: str = "@{u}..HEAD") -> int:
        return 0

    def get_file_at_ref(self, repo_path: str, ref: str, rel_path: str) -> str | None:
        return None

    def is_working_tree_clean(self, repo_path: str) -> bool:
        return True

    def list_dirty_paths(self, repo_path: str) -> list[str]:
        return []

    def list_changed_paths_since(self, repo_path: str, ref: str) -> list[str]:
        return []

    def merge_ff_only(self, repo_path: str, ref: str) -> bool:
        return True

    def push(
        self, repo_path: str, remote: str | None = None, branch: str | None = None
    ) -> None:
        pass


class FakeGitCommitFalha(FakeGit):
    """Variante cujo commit não pode ser criado (falha barulhenta)."""

    def commit_paths(self, repo_path: str, paths: list[str], message: str) -> str:
        raise RuntimeError("git sem identidade configurada")


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
    work_head = "a" * 40
    git = FakeGit(work_head)
    service = CommandService(fs, git)
    session_file = "session.md"
    repo_path = "repo/"

    # Prepara sessão ativa sobre o commit de trabalho.
    state = SessionState(commit_hash=work_head, active_feature="feat-1")
    service.save_session(session_file, state)

    msg = service.execute_command("encerrar-sessao", [], repo_path, session_file)

    # Âncora gravada = HEAD PRÉ-commit (commit de trabalho), não o de encerramento.
    loaded = service.load_session(session_file)
    assert loaded.is_active is False
    assert loaded.commit_hash == work_head

    # commit_paths recebeu SOMENTE o state_file (nunca git add -A).
    assert len(git.commit_calls) == 1
    called_repo, called_paths, called_msg = git.commit_calls[0]
    assert called_repo == repo_path
    assert called_paths == [session_file]
    assert "feat-1" in called_msg
    assert work_head in called_msg  # âncora citada na mensagem do commit

    # A saída reporta os DOIS hashes: âncora (trabalho) e encerramento.
    assert "Sessão encerrada com sucesso" in msg
    assert work_head in msg
    assert FakeGit.CLOSING_HEAD in msg


def test_execute_encerrar_sessao_sem_versionar_fecha_sem_commit():
    # Feature 024/D-03: versionar_estado=False fecha o estado no arquivo, NÃO
    # chama commit_paths e acrescenta a linha declarativa na narrativa (D-05).
    fs = MockFileSystem()
    work_head = "a" * 40
    git = FakeGit(work_head)
    service = CommandService(fs, git)
    session_file = "session.md"

    state = SessionState(commit_hash=work_head, active_feature="feat-1")
    service.save_session(session_file, state)

    msg = service.execute_command(
        "encerrar-sessao", [], "repo/", session_file, versionar_estado=False
    )

    # Estado fechado no arquivo, mas nenhum commit criado.
    loaded = service.load_session(session_file)
    assert loaded.is_active is False
    assert loaded.commit_hash == work_head
    assert git.commit_calls == []

    # Mensagem anuncia o não-versionamento (não "com sucesso").
    assert "sem versionar" in msg
    assert "com sucesso" not in msg

    # Linha declarativa gravada na narrativa (visível na retomada seguinte).
    assert any("não versionado" in item for item in loaded.narrative.feito)


def test_execute_encerrar_sessao_versionar_default_preserva_rn_n31():
    # Teste-guarda: o default versionar_estado=True mantém o comportamento da
    # RN-N31 (commit do estado por cima do trabalho), intacto para o MCP e demais.
    fs = MockFileSystem()
    work_head = "a" * 40
    git = FakeGit(work_head)
    service = CommandService(fs, git)
    session_file = "session.md"
    service.save_session(
        session_file, SessionState(commit_hash=work_head, active_feature="feat-1")
    )

    msg = service.execute_command("encerrar-sessao", [], "repo/", session_file)

    assert len(git.commit_calls) == 1
    assert git.commit_calls[0][1] == [session_file]
    assert "Sessão encerrada com sucesso" in msg


def test_execute_encerrar_sessao_falha_commit_preserva_estado():
    fs = MockFileSystem()
    work_head = "a" * 40
    git = FakeGitCommitFalha(work_head)
    service = CommandService(fs, git)
    session_file = "session.md"
    repo_path = "repo/"

    state = SessionState(commit_hash=work_head, active_feature="feat-1")
    service.save_session(session_file, state)

    # Falha barulhenta: erro nomeado, sem mensagem de sucesso.
    with pytest.raises(SessionCommitError):
        service.execute_command("encerrar-sessao", [], repo_path, session_file)

    # O estado salvo é PRESERVADO (save_session ocorreu antes do commit).
    loaded = service.load_session(session_file)
    assert loaded is not None
    assert loaded.is_active is False
    assert loaded.commit_hash == work_head


def test_execute_encerrar_sessao_ausente_e_noop():
    """Encerrar sem arquivo de sessão (None) → no-op ruidoso, sem commit (D1/016).

    A 016 reverte a falha barulhenta da 015 para a categoria *ausente*: não há
    nada a encerrar, então o comando devolve um aviso explícito e NÃO commita.
    Não levanta exceção, e a mensagem não começa por "Sessão encerrada".
    """
    fs = MockFileSystem()
    git = FakeGit("a" * 40)
    service = CommandService(fs, git)

    msg = service.execute_command("encerrar-sessao", [], "repo/", "session.md")

    assert "Nenhuma sessão" in msg
    assert not msg.startswith("Sessão encerrada")
    assert git.commit_calls == []


def test_execute_encerrar_sessao_inativa_reativa_e_fecha():
    """Sessão inativa → reativa, fecha e commita num passo (D1/D3, 016).

    Reverte a falha barulhenta da 015 para a categoria *inativa*: o comando
    reativa preservando a narrativa, fecha e versiona o estado; a âncora segue
    sendo o HEAD de trabalho, e a saída anuncia a reativação automática.
    """
    fs = MockFileSystem()
    work_head = "a" * 40
    git = FakeGit(work_head)
    service = CommandService(fs, git)
    session_file = "session.md"

    state = SessionState(
        commit_hash=work_head, active_feature="feat-1", is_active=False
    )
    service.save_session(session_file, state)

    msg = service.execute_command("encerrar-sessao", [], "repo/", session_file)

    # Fechou de fato e commitou só o estado, com âncora no trabalho.
    loaded = service.load_session(session_file)
    assert loaded.is_active is False
    assert loaded.commit_hash == work_head
    assert len(git.commit_calls) == 1
    assert git.commit_calls[0][1] == [session_file]

    # Caminho feliz + anúncio ruidoso de reativação.
    assert msg.startswith("Sessão encerrada com sucesso")
    assert "reativ" in msg.lower()


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
