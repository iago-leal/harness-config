"""Testes do SessionCloseFlow (feature 018, T003).

Fluxo de fachada do encerramento, extraído da borda CLI (D-01) e compartilhado
com os scripts finos da skill. Cobre as decisões do fluxo — pré-check de
pendência, no-op por ausência, fechamento feliz, ofertas pós-sucesso e os dois
caminhos barulhentos (estado malformado, falha de commit do estado) — com IO
injetado, sem tocar git/fs reais.
"""

from unittest.mock import MagicMock


from src.core.domain.config import HarnessConfig
from src.core.domain.models import SessionState, SessionNarrative
from src.core.commands.service import CommandService
from src.core.ports.git import GitPort
from src.core.session import serializer
from src.core.session.close_flow import SessionCloseFlow
from tests.helpers import MockFileSystem

STATE_FILE = ".harness/estado-da-sessao.md"
WORK_HEAD = "a" * 40
CLOSING_HEAD = "c" * 40


class FakeGit(GitPort):
    """Git fake mínimo: HEAD fixo, dirty configurável, commit que avança o HEAD."""

    def __init__(
        self,
        head=WORK_HEAD,
        dirty=None,
        commit_raises=False,
        baseline_text=None,
        changed_since=None,
    ):
        self._head = head
        self._dirty = dirty or []
        self._commit_raises = commit_raises
        self._baseline_text = baseline_text
        self._changed_since = changed_since or []
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

    def list_changed_paths_since(self, repo_path: str, ref: str) -> list:
        return list(self._changed_since)

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
        return self._baseline_text

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


def _seed_active_session(fs, git, narrative=None):
    """Grava um estado de sessão ativo e válido sobre WORK_HEAD.

    A narrativa default é NÃO-vazia: o gate de narrativa viva bloqueia o
    fechamento de uma sessão com narrativa vazia, então os testes que exercitam
    o caminho de fechamento precisam de uma narrativa preenchida.
    """
    state = SessionState(
        commit_hash=WORK_HEAD,
        active_feature="feat-1",
        narrative=narrative
        if narrative is not None
        else SessionNarrative(feito=["consolidou o trabalho da sessão"]),
    )
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


def test_pendente_inclui_decisoes_de_harness_exceto_estado():
    # Feature 019: decisões e índice de .harness/ entram na oferta; só o
    # estado-da-sessao.md (que o fechamento versiona) é excluído.
    fs = MockFileSystem()
    git = FakeGit(
        dirty=[".harness/decisoes/MD-0007.md", ".harness/microdecisoes.md", STATE_FILE]
    )
    _seed_active_session(fs, git)
    flow = SpyFlow(fs, git, MagicMock())

    code, outs, _ = _run(flow)

    assert code == 0
    marker = next(o for o in outs if "[HARNESS:COMMIT_PENDENTE" in o)
    assert ".harness/decisoes/MD-0007.md" in marker
    assert ".harness/microdecisoes.md" in marker
    assert STATE_FILE not in marker
    # Não fechou: nenhum commit do estado e nenhuma oferta.
    assert git.commit_calls == []
    assert flow.offers_called == 0


def test_apenas_estado_sujo_fecha_sem_oferta():
    # Feature 019/RF-02: o state_file como único sujo é tratado como árvore limpa.
    fs = MockFileSystem()
    git = FakeGit(dirty=[STATE_FILE])
    _seed_active_session(fs, git)
    flow = SpyFlow(fs, git, MagicMock())

    code, outs, _ = _run(flow)

    assert code == 0
    assert not any("[HARNESS:COMMIT_PENDENTE" in o for o in outs)
    assert any("Sessão encerrada com sucesso" in o for o in outs)
    assert flow.offers_called == 1


# --- Gate de narrativa viva -------------------------------------------------
# O fechamento não pode carimbar uma âncora nova por cima de uma narrativa vazia
# ou congelada desde o início da sessão: a narrativa é escrita pelo agente, e o
# gate a exige de forma barulhenta (marker NARRATIVA_PENDENTE), sem fechar.


def _rendered_state(narrative, *, is_active=False):
    """Texto de um estado-da-sessao (front-matter + narrativa) para servir de baseline."""
    return serializer.render(
        SessionState(
            commit_hash=WORK_HEAD,
            active_feature="feat-1",
            is_active=is_active,
            narrative=narrative,
        )
    )


def test_narrativa_vazia_emite_marker_e_nao_fecha():
    fs = MockFileSystem()
    git = FakeGit(dirty=[])
    _seed_active_session(fs, git, narrative=SessionNarrative())  # vazia
    flow = SpyFlow(fs, git, MagicMock())

    code, outs, _ = _run(flow)

    assert code == 0
    assert any("[HARNESS:NARRATIVA_PENDENTE" in o for o in outs)
    # Não fechou: nenhum commit do estado e nenhuma oferta.
    assert git.commit_calls == []
    assert flow.offers_called == 0


def test_narrativa_inalterada_vs_ancora_emite_marker_e_nao_fecha():
    # A narrativa atual é idêntica à do commit-âncora de partida → esquecimento.
    narrative = SessionNarrative(feito=["fez X"], proximos_passos=["fará Y"])
    fs = MockFileSystem()
    git = FakeGit(dirty=[], baseline_text=_rendered_state(narrative))
    _seed_active_session(fs, git, narrative=narrative)
    flow = SpyFlow(fs, git, MagicMock())

    code, outs, _ = _run(flow)

    assert code == 0
    assert any("[HARNESS:NARRATIVA_PENDENTE" in o for o in outs)
    assert git.commit_calls == []
    assert flow.offers_called == 0


def test_narrativa_atualizada_vs_ancora_fecha():
    # Narrativa mudou desde a âncora → o agente consolidou; pode fechar.
    baseline = SessionNarrative(feito=["trabalho antigo"])
    atual = SessionNarrative(feito=["trabalho NOVO desta sessão"])
    fs = MockFileSystem()
    git = FakeGit(dirty=[], baseline_text=_rendered_state(baseline))
    _seed_active_session(fs, git, narrative=atual)
    flow = SpyFlow(fs, git, MagicMock())

    code, outs, _ = _run(flow)

    assert code == 0
    assert not any("[HARNESS:NARRATIVA_PENDENTE" in o for o in outs)
    assert any("Sessão encerrada com sucesso" in o for o in outs)
    assert git.commit_calls and git.commit_calls[0][1] == [STATE_FILE]
    assert flow.offers_called == 1


def test_primeira_sessao_sem_baseline_fecha_com_narrativa_preenchida():
    # Sem baseline legível na âncora (1ª sessão): narrativa preenchida basta.
    fs = MockFileSystem()
    git = FakeGit(dirty=[], baseline_text=None)
    _seed_active_session(
        fs, git, narrative=SessionNarrative(feito=["primeira entrega"])
    )
    flow = SpyFlow(fs, git, MagicMock())

    code, outs, _ = _run(flow)

    assert code == 0
    assert not any("[HARNESS:NARRATIVA_PENDENTE" in o for o in outs)
    assert any("Sessão encerrada com sucesso" in o for o in outs)
    assert flow.offers_called == 1


def test_narrativa_pendente_tty_orienta_sem_perguntar():
    # Com TTY, o gate orienta em texto legível e não lê entrada (não há asker).
    fs = MockFileSystem()
    git = FakeGit(dirty=[])
    _seed_active_session(fs, git, narrative=SessionNarrative())  # vazia → dispara
    flow = SpyFlow(fs, git, MagicMock())

    def asker_proibido(_q):
        raise AssertionError("o gate de narrativa não deve perguntar")

    outs = []
    code = flow.run(
        "repo/",
        _config(),
        out=outs.append,
        err=lambda _m: None,
        asker=asker_proibido,
        is_interactive=True,
    )

    assert code == 0
    assert any("não foi atualizada nesta sessão" in o for o in outs)
    assert not any("[HARNESS:NARRATIVA_PENDENTE" in o for o in outs)
    assert git.commit_calls == []
    assert flow.offers_called == 0


# ---------------------------------------------------------------------------
# Gate de registro de decisões (feature 022): 3º portão do encerramento.
# Protocolo abortar-e-reexecutar, na família do COMMIT/NARRATIVA_PENDENTE.


def test_gate_decisao_pendente_emite_marker_e_nao_fecha():
    fs = MockFileSystem()
    git = FakeGit(dirty=[], changed_since=["Empresas/contrato-clausula7.md"])
    _seed_active_session(fs, git)
    flow = SpyFlow(fs, git, MagicMock())

    code, outs, _ = _run(flow)

    assert code == 0
    marker = next(o for o in outs if "[HARNESS:DECISAO_PENDENTE" in o)
    assert "Empresas/contrato-clausula7.md" in marker
    assert "MD-NNNN" in marker
    assert "--sem-decisao" in marker
    assert git.commit_calls == []
    assert flow.offers_called == 0
    # Anti-loop: o fingerprint do bloqueio ficou persistido no estado.
    persisted = serializer.parse(fs.read_file(STATE_FILE))
    assert persisted.gate_encerramento_fingerprint


def test_gate_ficha_tocada_libera_fechamento():
    fs = MockFileSystem()
    git = FakeGit(
        dirty=[],
        changed_since=["Empresas/contrato.md", ".harness/decisoes/MD-0015.md"],
    )
    _seed_active_session(fs, git)
    flow = SpyFlow(fs, git, MagicMock())

    code, outs, _ = _run(flow)

    assert code == 0
    assert any("Sessão encerrada com sucesso" in o for o in outs)
    assert not any("DECISAO_PENDENTE" in o for o in outs)
    assert flow.offers_called == 1


def test_gate_so_artefatos_do_harness_nao_dispara():
    fs = MockFileSystem()
    git = FakeGit(changed_since=[STATE_FILE, ".harness/microdecisoes.md"])
    _seed_active_session(fs, git)
    flow = SpyFlow(fs, git, MagicMock())

    code, outs, _ = _run(flow)

    assert code == 0
    assert any("Sessão encerrada com sucesso" in o for o in outs)
    assert not any("DECISAO_PENDENTE" in o for o in outs)


def test_gate_escape_sem_decisao_registra_na_narrativa_e_fecha():
    fs = MockFileSystem()
    git = FakeGit(dirty=[], changed_since=["docs/novo-contrato.md"])
    _seed_active_session(fs, git)
    flow = SpyFlow(fs, git, MagicMock())

    outs = []
    code = flow.run(
        "repo/",
        _config(),
        out=outs.append,
        err=lambda _m: None,
        is_interactive=False,
        sem_decisao=True,
    )

    assert code == 0
    assert any("Sessão encerrada com sucesso" in o for o in outs)
    assert not any("DECISAO_PENDENTE" in o for o in outs)
    # Rastro auditável no estado da sessão (escolha 5a de 2026-07-15).
    persisted = serializer.parse(fs.read_file(STATE_FILE))
    assert any("sem decisão não óbvia" in item for item in persisted.narrative.feito)


def test_gate_anti_loop_segunda_tentativa_fecha_com_aviso():
    fs = MockFileSystem()
    git = FakeGit(dirty=[], changed_since=["docs/novo-contrato.md"])
    _seed_active_session(fs, git)

    flow1 = SpyFlow(fs, git, MagicMock())
    _code1, outs1, _ = _run(flow1)
    assert any("[HARNESS:DECISAO_PENDENTE" in o for o in outs1)

    # Nada mudou (mesmo fingerprint): a 2ª tentativa nunca re-bloqueia (RF-04).
    flow2 = SpyFlow(fs, git, MagicMock())
    code2, outs2, errs2 = _run(flow2)

    assert code2 == 0
    assert any("Sessão encerrada com sucesso" in o for o in outs2)
    assert any("pendência" in e.lower() for e in errs2)


def test_gate_desligado_por_config_nao_dispara():
    fs = MockFileSystem()
    git = FakeGit(dirty=[], changed_since=["docs/x.md"])
    _seed_active_session(fs, git)
    flow = SpyFlow(fs, git, MagicMock())

    config = HarnessConfig(
        session={"state_file": STATE_FILE},
        decisions={"require_registration": False},
    )
    outs = []
    code = flow.run(
        "repo/", config, out=outs.append, err=lambda _m: None, is_interactive=False
    )

    assert code == 0
    assert any("Sessão encerrada com sucesso" in o for o in outs)
    assert not any("DECISAO_PENDENTE" in o for o in outs)


def test_gate_fingerprints_zerados_no_fechamento():
    fs = MockFileSystem()
    git = FakeGit(
        dirty=[], changed_since=["docs/x.md", ".harness/decisoes/MD-0015.md"]
    )
    _seed_active_session(fs, git)
    # Estado herdado com fingerprint de lembrete (Stop) preenchido.
    state = serializer.parse(fs.read_file(STATE_FILE))
    state.gate_lembrete_fingerprint = "f" * 40
    CommandService(fs, git).save_session(STATE_FILE, state)
    flow = SpyFlow(fs, git, MagicMock())

    _code, outs, _ = _run(flow)

    assert any("Sessão encerrada com sucesso" in o for o in outs)
    persisted = serializer.parse(fs.read_file(STATE_FILE))
    assert persisted.gate_lembrete_fingerprint is None
    assert persisted.gate_encerramento_fingerprint is None
