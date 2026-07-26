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
from src.core.session.close_flow import (
    SessionCloseFlow,
    conduct_commit_pendente,
    render_commit_pendente_marker,
    render_encerramento_nao_versionado_marker,
)
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


def _run(
    flow,
    *,
    out=None,
    err=None,
    is_interactive=False,
    asker=None,
    sem_decisao=False,
    com_pendencias=False,
    versionar_encerramento=True,
):
    """Roda o fluxo com o desfecho de fechamento AUTORIZADO por default.

    ``versionar_encerramento=True`` por default: os testes deste helper exercitam
    o caminho que de fato fecha, e a feature 024 exige aval explícito para o commit
    de encerramento (sem terminal, o default se inverte). Os testes do
    consentimento em si passam o valor conforme o cenário; os de aborto (pendência
    / narrativa / registro) nem chegam a esta decisão.
    """
    outs, errs = [], []
    kwargs = dict(
        out=(out or outs.append),
        err=(err or errs.append),
        is_interactive=is_interactive,
        sem_decisao=sem_decisao,
        com_pendencias=com_pendencias,
        versionar_encerramento=versionar_encerramento,
    )
    if asker is not None:
        kwargs["asker"] = asker
    code = flow.run("repo/", _config(), **kwargs)
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
        versionar_encerramento=True,
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


def test_gate_portao_rearma_com_trabalho_novo_apos_bloqueio():
    # Guarda da 023 (D-06): o PORTÃO mantém a identidade fina — trabalho novo
    # sem ficha (commitado pelo pré-check → HEAD novo) rearma a garantia dura,
    # ao contrário do lembrete do Stop, que passa à identidade grossa.
    fs = MockFileSystem()
    git = FakeGit(dirty=[], changed_since=["docs/novo-contrato.md"])
    _seed_active_session(fs, git)
    _code1, outs1, _ = _run(SpyFlow(fs, git, MagicMock()))
    assert any("[HARNESS:DECISAO_PENDENTE" in o for o in outs1)

    # Trabalho novo commitado: HEAD avançou e o diff da âncora cresceu.
    git2 = FakeGit(
        head="d" * 40,
        dirty=[],
        changed_since=["docs/novo-contrato.md", "docs/outro.md"],
    )
    code2, outs2, _ = _run(SpyFlow(fs, git2, MagicMock()))

    assert code2 == 0
    assert any("[HARNESS:DECISAO_PENDENTE" in o for o in outs2)
    assert not any("Sessão encerrada com sucesso" in o for o in outs2)


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
        "repo/",
        config,
        out=outs.append,
        err=lambda _m: None,
        is_interactive=False,
        versionar_encerramento=True,
    )

    assert code == 0
    assert any("Sessão encerrada com sucesso" in o for o in outs)
    assert not any("DECISAO_PENDENTE" in o for o in outs)


def test_gate_fingerprints_zerados_no_fechamento():
    fs = MockFileSystem()
    git = FakeGit(dirty=[], changed_since=["docs/x.md", ".harness/decisoes/MD-0015.md"])
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


# ===========================================================================
# Feature 024 — oferta de commit consentida (fim do commit automático).
# Dois pontos de decisão: commit do trabalho pendente (RN-06) e commit de
# encerramento (RN-04/RN-08), com default assimétrico por borda (D-07).


def _config_sem_gate_decisoes():
    # Isola os cenários de pendência/encerramento do 3º portão (022): o gate de
    # decisões é ortogonal a esta feature e dispararia sobre o trabalho sujo.
    return HarnessConfig(
        session={"state_file": STATE_FILE},
        decisions={"require_registration": False},
    )


# --- T003/T004: renderizadores (unidade) -----------------------------------


def test_marker_commit_pendente_vira_oferta_preservando_formato():
    # RF-01/RF-10: o campo `acao` deixa de ordenar e passa a descrever a oferta;
    # arquivos/total/truncado/mostrados e o teto de 20 ficam byte a byte.
    marker = render_commit_pendente_marker(["a.txt", "b.txt"])
    assert 'arquivos="a.txt,b.txt"' in marker
    assert "total=2" in marker
    assert "truncado" not in marker
    # Oferta, não ordem: pergunta antes, e aponta a saída da recusa.
    assert "pergunte ao usuário se deve commitar" in marker
    assert "--com-pendencias" in marker

    # Truncamento: total real preservado, teto de 20 mantido.
    muitos = [f"f{i}.txt" for i in range(34)]
    marker_trunc = render_commit_pendente_marker(muitos)
    assert "total=34" in marker_trunc
    assert "truncado=true mostrados=20" in marker_trunc


def test_marker_encerramento_nao_versionado_formato():
    # RF-09: contrato do marker pós-fechamento (arquivo, ancora, motivo, acao).
    marker = render_encerramento_nao_versionado_marker(
        STATE_FILE, WORK_HEAD, "sem-autorizacao"
    )
    assert marker.startswith("[HARNESS:ENCERRAMENTO_NAO_VERSIONADO")
    assert f'arquivo="{STATE_FILE}"' in marker
    assert f'ancora="{WORK_HEAD}"' in marker
    assert 'motivo="sem-autorizacao"' in marker
    assert "--com-commit-encerramento" in marker


# --- T006: pré-check interativo (unidade + fluxo) --------------------------


def test_conduct_commit_pendente_interativo_conta_lista_e_pergunta():
    # RF-04: contagem à frente, lista abaixo, pergunta de segunda ordem (RN-06).
    outs, perguntas = [], []

    def asker(q, *, default=False):
        perguntas.append(q)
        return True

    autorizado = conduct_commit_pendente(
        ["a.txt", "b.txt", "c.txt", "d.txt", "e.txt", "f.txt", "g.txt"],
        is_interactive=True,
        out=outs.append,
        asker=asker,
    )

    assert autorizado is True
    assert any("há 7 mudanças não commitadas" in o for o in outs)
    # A lista dos caminhos aparece abaixo da contagem.
    assert any("  - a.txt" in o for o in outs)
    # Pergunta o DESFECHO (encerrar assim mesmo), não "quer que eu commite?".
    assert perguntas and "Encerrar mesmo com 7 mudança" in perguntas[0]


def test_conduct_commit_pendente_sem_tty_emite_marker_e_nega():
    outs = []
    autorizado = conduct_commit_pendente(
        ["x.txt"], is_interactive=False, out=outs.append, asker=None
    )
    assert autorizado is False
    assert any("[HARNESS:COMMIT_PENDENTE" in o for o in outs)


def test_flow_pendente_recusa_no_terminal_aborta_sem_fechar():
    # RF-06: recusada a segunda ordem ("encerrar assim mesmo?"), não fecha.
    fs = MockFileSystem()
    git = FakeGit(dirty=["trabalho.txt"])
    _seed_active_session(fs, git)
    flow = SpyFlow(fs, git, MagicMock())

    code, outs, _ = _run(
        flow,
        is_interactive=True,
        asker=lambda q, *, default=False: False,  # recusa a 2ª ordem
    )

    assert code == 0
    assert any("há 1 mudança não commitada" in o for o in outs)
    assert git.commit_calls == []
    assert flow.offers_called == 0


# --- T027: pendências autorizadas gravam a declaração ----------------------


def test_flow_com_pendencias_fecha_e_declara_na_narrativa():
    # --com-pendencias libera o 1º portão (sem terminal) e grava o rastro.
    fs = MockFileSystem()
    git = FakeGit(dirty=["trabalho.txt"])
    _seed_active_session(fs, git)
    flow = SpyFlow(fs, git, MagicMock())

    outs = []
    code = flow.run(
        "repo/",
        _config_sem_gate_decisoes(),
        out=outs.append,
        err=lambda _m: None,
        is_interactive=False,
        com_pendencias=True,
        versionar_encerramento=True,
    )

    assert code == 0
    assert any("Sessão encerrada com sucesso" in o for o in outs)
    # Ainda anuncia (marker), mas fecha por causa da flag.
    assert any("[HARNESS:COMMIT_PENDENTE" in o for o in outs)
    persisted = serializer.parse(fs.read_file(STATE_FILE))
    assert any(
        "não commitada(s) por escolha do usuário" in item
        for item in persisted.narrative.feito
    )


# --- T007: decisão do commit de encerramento -------------------------------


def test_encerramento_consentido_no_terminal_versiona():
    fs = MockFileSystem()
    git = FakeGit(dirty=[])
    _seed_active_session(fs, git)
    flow = SpyFlow(fs, git, MagicMock())

    perguntas = []

    def asker(q, *, default=False):
        perguntas.append((q, default))
        return True  # autoriza

    code, outs, _ = _run(
        flow, is_interactive=True, asker=asker, versionar_encerramento=None
    )

    assert code == 0
    assert any("Sessão encerrada com sucesso" in o for o in outs)
    assert git.commit_calls and git.commit_calls[0][1] == [STATE_FILE]
    # A pergunta do encerramento tem default AFIRMATIVO (D-07).
    assert any(
        "commit de encerramento" in q and default is True for q, default in perguntas
    )


def test_encerramento_recusado_no_terminal_fecha_sem_commit_com_marker():
    fs = MockFileSystem()
    git = FakeGit(dirty=[])
    _seed_active_session(fs, git)
    flow = SpyFlow(fs, git, MagicMock())

    code, outs, _ = _run(
        flow,
        is_interactive=True,
        asker=lambda q, *, default=False: False,  # recusa o encerramento
        versionar_encerramento=None,
    )

    assert code == 0
    assert any("Sessão encerrada (sem versionar" in o for o in outs)
    assert git.commit_calls == []  # nada versionado
    marker = next(o for o in outs if "[HARNESS:ENCERRAMENTO_NAO_VERSIONADO" in o)
    assert 'motivo="recusa-explicita"' in marker
    # Ofertas ainda conduzidas após o fechamento (não bloqueadas).
    assert flow.offers_called == 1


def test_arvore_limpa_vai_direto_a_decisao_de_encerramento():
    # Gherkin "árvore limpa": só o estado sujo → pula a oferta de commit do
    # trabalho e vai direto à decisão do commit de encerramento.
    fs = MockFileSystem()
    git = FakeGit(dirty=[STATE_FILE])
    _seed_active_session(fs, git)
    flow = SpyFlow(fs, git, MagicMock())

    perguntas = []

    def asker(q, *, default=False):
        perguntas.append(q)
        return True

    code, outs, _ = _run(
        flow, is_interactive=True, asker=asker, versionar_encerramento=None
    )

    assert code == 0
    assert not any("[HARNESS:COMMIT_PENDENTE" in o for o in outs)
    # A única pergunta feita é a do commit de encerramento.
    assert len(perguntas) == 1
    assert "commit de encerramento" in perguntas[0]


# --- T026: flag vence a pergunta -------------------------------------------


def test_flag_de_encerramento_vence_a_pergunta_no_terminal():
    # Com a flag, o asker não é chamado para a decisão do encerramento.
    fs = MockFileSystem()
    git = FakeGit(dirty=[])
    _seed_active_session(fs, git)
    flow = SpyFlow(fs, git, MagicMock())

    def asker_proibido(q, *, default=False):
        raise AssertionError("a flag já respondeu; não deve perguntar")

    code, outs, _ = _run(
        flow,
        is_interactive=True,
        asker=asker_proibido,
        versionar_encerramento=False,  # recusa explícita por flag
    )

    assert code == 0
    assert git.commit_calls == []
    marker = next(o for o in outs if "[HARNESS:ENCERRAMENTO_NAO_VERSIONADO" in o)
    assert 'motivo="recusa-explicita"' in marker


# --- T009: duas sessões encadeadas após fechamento não versionado ----------


def test_estado_sujo_nao_dispara_precheck_nem_gate_na_sessao_seguinte():
    # O state_file deixado sujo pelo fechamento não versionado NÃO vira pendência
    # em cascata (excluído por caminho exato, RN-N34) nem infla o 3º portão
    # (excluído do universo do gate, RN-N43).
    fs = MockFileSystem()
    git = FakeGit(dirty=[STATE_FILE], changed_since=[STATE_FILE])
    _seed_active_session(fs, git)
    flow = SpyFlow(fs, git, MagicMock())

    code, outs, _ = _run(flow)

    assert code == 0
    assert not any("[HARNESS:COMMIT_PENDENTE" in o for o in outs)
    assert not any("[HARNESS:DECISAO_PENDENTE" in o for o in outs)
    assert any("Sessão encerrada com sucesso" in o for o in outs)


# --- T010: os portões 2 e 3 seguem inalterados sob as flags novas ----------


def test_flags_novas_nao_furam_o_gate_de_narrativa():
    # Guarda: as flags de consentimento não bypassam o gate de narrativa viva.
    fs = MockFileSystem()
    git = FakeGit(dirty=[])
    _seed_active_session(fs, git, narrative=SessionNarrative())  # vazia
    flow = SpyFlow(fs, git, MagicMock())

    code, outs, _ = _run(flow, com_pendencias=True, versionar_encerramento=True)

    assert code == 0
    assert any("[HARNESS:NARRATIVA_PENDENTE" in o for o in outs)
    assert git.commit_calls == []
    assert flow.offers_called == 0


def test_marker_nao_versionado_sai_depois_do_sucesso_e_antes_das_ofertas():
    # Invariantes do contrato §5/§6 (A014): o marker pós-fechamento é emitido
    # DEPOIS da mensagem de sucesso e ANTES da oferta de push.
    fs = MockFileSystem()
    git = FakeGit(dirty=[])
    _seed_active_session(fs, git)

    class OrderFlow(SessionCloseFlow):
        def _conduct_offers(self, *args, **kwargs):
            kwargs.get("out", print)("[SENTINELA_OFERTAS]")

    flow = OrderFlow(fs, git, MagicMock())
    outs = []
    code = flow.run(
        "repo/",
        _config(),
        out=outs.append,
        err=lambda _m: None,
        is_interactive=False,
        versionar_encerramento=False,
    )

    assert code == 0
    idx_sucesso = next(
        i for i, o in enumerate(outs) if o.startswith("Sessão encerrada")
    )
    idx_marker = next(
        i for i, o in enumerate(outs) if "ENCERRAMENTO_NAO_VERSIONADO" in o
    )
    idx_oferta = next(i for i, o in enumerate(outs) if "SENTINELA_OFERTAS" in o)
    assert idx_sucesso < idx_marker < idx_oferta
