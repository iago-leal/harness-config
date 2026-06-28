"""Testes do SessionCloseFlow (feature 018, T003).

Fluxo de fachada do encerramento, extraído da borda CLI (D-01) e compartilhado
com os scripts finos da skill. Cobre as decisões do fluxo — pré-check de
pendência, no-op por ausência, fechamento feliz, ofertas pós-sucesso e os dois
caminhos barulhentos (estado malformado, falha de commit do estado) — com IO
injetado, sem tocar git/fs reais.
"""

from unittest.mock import MagicMock


from src.core.domain.config import HarnessConfig
from src.core.domain.models import SessionState
from src.core.commands.service import CommandService
from src.core.ports.git import GitPort
from src.core.session.close_flow import SessionCloseFlow
from tests.helpers import MockFileSystem

STATE_FILE = ".harness/estado-da-sessao.md"
WORK_HEAD = "a" * 40
CLOSING_HEAD = "c" * 40


class FakeGit(GitPort):
    """Git fake mínimo: HEAD fixo, dirty configurável, commit que avança o HEAD."""

    def __init__(self, head=WORK_HEAD, dirty=None, commit_raises=False):
        self._head = head
        self._dirty = dirty or []
        self._commit_raises = commit_raises
        self.commit_calls = []

    def get_head_commit(self, repo_path: str) -> str:
        return self._head

    def commit_paths(self, repo_path: str, paths, message: str) -> str:
        if self._commit_raises:
            raise RuntimeError("git sem identidade configurada")
        self.commit_calls.append((repo_path, list(paths), message))
        self._head = CLOSING_HEAD
        return self._head

    def list_dirty_paths(self, repo_path: str) -> list:
        return list(self._dirty)

    # Demais membros do contrato: defaults inócuos (o fluxo feliz não os usa).
    def get_remote_commit(self, repo_path, remote_name="origin", branch_name="main"):
        return self._head

    def init_repo(self, repo_path: str) -> None:
        pass

    def fetch(self, repo_path, remote="origin", branch=None) -> None:
        pass

    def get_current_branch(self, repo_path: str) -> str:
        return "main"

    def get_default_branch(self, repo_path: str, remote: str = "origin") -> str:
        return "main"

    def count_commits_ahead(self, repo_path: str, rev: str = "@{u}..HEAD") -> int:
        return 0

    def get_file_at_ref(self, repo_path: str, ref: str, rel_path: str):
        return None

    def is_working_tree_clean(self, repo_path: str) -> bool:
        return not self._dirty

    def merge_ff_only(self, repo_path: str, ref: str) -> bool:
        return True

    def push(self, repo_path, remote=None, branch=None) -> None:
        pass


class SpyFlow(SessionCloseFlow):
    """Conta as conduções de oferta sem disparar a detecção real (testada à parte)."""

    def __init__(self, *args):
        super().__init__(*args)
        self.offers_called = 0

    def _conduct_offers(self, *args, **kwargs):
        self.offers_called += 1


def _config():
    return HarnessConfig(session={"state_file": STATE_FILE})


def _seed_active_session(fs, git):
    """Grava um estado de sessão ativo e válido sobre WORK_HEAD."""
    state = SessionState(commit_hash=WORK_HEAD, active_feature="feat-1")
    CommandService(fs, git).save_session(STATE_FILE, state)


def _run(flow, *, out=None, err=None, is_interactive=False):
    outs, errs = [], []
    code = flow.run(
        "repo/",
        _config(),
        out=(out or outs.append),
        err=(err or errs.append),
        is_interactive=is_interactive,
    )
    return code, outs, errs


def test_caminho_feliz_fecha_e_conduz_ofertas():
    fs = MockFileSystem()
    git = FakeGit(dirty=[])
    _seed_active_session(fs, git)
    flow = SpyFlow(fs, git, MagicMock())

    code, outs, _ = _run(flow)

    assert code == 0
    assert any("Sessão encerrada com sucesso" in o for o in outs)
    assert git.commit_calls and git.commit_calls[0][1] == [STATE_FILE]
    # Ofertas conduzidas SÓ após sucesso.
    assert flow.offers_called == 1


def test_trabalho_pendente_emite_marker_e_nao_fecha():
    fs = MockFileSystem()
    git = FakeGit(dirty=["trabalho.txt", STATE_FILE])
    _seed_active_session(fs, git)
    flow = SpyFlow(fs, git, MagicMock())

    code, outs, _ = _run(flow)

    assert code == 0
    assert any("[HARNESS:COMMIT_PENDENTE" in o for o in outs)
    assert any("trabalho.txt" in o for o in outs)
    # Não fechou: nenhum commit do estado e nenhuma oferta.
    assert git.commit_calls == []
    assert flow.offers_called == 0


def test_sessao_ausente_e_noop_sem_ofertas():
    fs = MockFileSystem()
    git = FakeGit(dirty=[])
    flow = SpyFlow(fs, git, MagicMock())

    code, outs, _ = _run(flow)

    assert code == 0
    assert any("Nenhuma sessão" in o for o in outs)
    assert git.commit_calls == []
    assert flow.offers_called == 0


def test_estado_malformado_aborta_barulhento():
    fs = MockFileSystem()
    git = FakeGit(dirty=[])
    # Estado legado de hash curto: o serializer recusa → MalformedSessionStateError.
    fs.written_files[STATE_FILE] = (
        "---\ncommit: abc1234\nfeature: feat-1\n"
        "start_time: 2026-06-01T10:00:00+00:00\nstatus: active\n---\n\n## x\n- y\n"
    )
    fs.existing_files.add(STATE_FILE)
    flow = SpyFlow(fs, git, MagicMock())

    code, _outs, errs = _run(flow)

    assert code == 1
    assert any("estado-da-sessao.md" in e for e in errs)
    assert any("abortado" in e.lower() for e in errs)
    assert git.commit_calls == []
    assert flow.offers_called == 0


def test_falha_de_commit_do_estado_aborta_barulhento():
    fs = MockFileSystem()
    git = FakeGit(dirty=[], commit_raises=True)
    _seed_active_session(fs, git)
    flow = SpyFlow(fs, git, MagicMock())

    code, _outs, errs = _run(flow)

    assert code == 1
    assert any("abortado" in e.lower() for e in errs)
    assert flow.offers_called == 0


def test_sem_tty_nao_pergunta_no_caminho_pendente():
    # Sem TTY, o pré-check de pendência emite o marker e não lê entrada.
    fs = MockFileSystem()
    git = FakeGit(dirty=["x.txt"])
    _seed_active_session(fs, git)
    flow = SpyFlow(fs, git, MagicMock())

    def asker_proibido(_q):
        raise AssertionError("não deve perguntar sem TTY")

    outs = []
    code = flow.run(
        "repo/",
        _config(),
        out=outs.append,
        err=lambda _m: None,
        asker=asker_proibido,
        is_interactive=False,
    )
    assert code == 0
    assert any("[HARNESS:COMMIT_PENDENTE" in o for o in outs)
