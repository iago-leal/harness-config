"""Gate de registro de microdecisões (feature 022) — avaliação pura.

`evaluate_registration_gate` decide, por sinal físico (diff da âncora ∪ working
tree sujo, cruzado com as fichas), se há trabalho substantivo sem decisão
registrada. Puro e agnóstico ao harness (RN-N5): não conhece `active_harness`
nem decide COMO interceptar — isso é da borda.
"""

from src.core.decisions.gate import compute_fingerprint, evaluate_registration_gate
from src.core.domain.config import HarnessConfig
from src.core.domain.models import SessionState

ANCHOR = "a" * 40
HEAD = "b" * 40
STATE_FILE = ".harness/estado-da-sessao.md"
INDEX_FILE = ".harness/microdecisoes.md"
HEADER_FILE = ".harness/decisoes/_cabecalho.md"


class GateGit:
    """Dublê mínimo: só os três verbos que o gate consulta."""

    def __init__(self, changed=None, dirty=None, head=HEAD, changed_raises=False):
        self._changed = changed or []
        self._dirty = dirty or []
        self._head = head
        self._changed_raises = changed_raises

    def get_head_commit(self, repo_path):
        return self._head

    def list_dirty_paths(self, repo_path):
        return list(self._dirty)

    def list_changed_paths_since(self, repo_path, ref):
        if self._changed_raises:
            raise RuntimeError("ref inválida ou repo sem commit")
        return list(self._changed)


def _session():
    return SessionState(commit_hash=ANCHOR, active_feature="feat-x")


def _evaluate(git):
    return evaluate_registration_gate(git, "repo/", _session(), HarnessConfig())


def test_mudanca_sem_ficha_e_pendente():
    verdict = _evaluate(GateGit(changed=["src/app.py"]))
    assert verdict.pendente is True
    assert verdict.mudancas == ["src/app.py"]
    assert verdict.fichas_tocadas == []


def test_mudanca_documental_e_pendente():
    # Esclarecimento de 2026-07-15: repositório não é só código — contrato e
    # documento contam como trabalho substantivo.
    verdict = _evaluate(GateGit(changed=["Empresas/contrato-clausula7.md"]))
    assert verdict.pendente is True


def test_ficha_commitada_no_conjunto_satisfaz():
    verdict = _evaluate(
        GateGit(changed=["src/app.py", ".harness/decisoes/MD-0015.md"])
    )
    assert verdict.pendente is False
    assert verdict.fichas_tocadas == [".harness/decisoes/MD-0015.md"]


def test_ficha_suja_nao_commitada_satisfaz():
    # A ficha recém-escrita no working tree também conta (caminho do Stop).
    verdict = _evaluate(
        GateGit(changed=["src/app.py"], dirty=[".harness/decisoes/MD-0022.md"])
    )
    assert verdict.pendente is False


def test_so_artefatos_do_harness_nao_e_pendente():
    # Estado de sessão, índice derivado e cabeçalho não são trabalho substantivo.
    verdict = _evaluate(GateGit(changed=[STATE_FILE, INDEX_FILE, HEADER_FILE]))
    assert verdict.pendente is False
    assert verdict.mudancas == []


def test_sem_mudanca_nenhuma_nao_e_pendente():
    verdict = _evaluate(GateGit())
    assert verdict.pendente is False


def test_ancora_ilegivel_fail_open_com_aviso():
    # RN-05: repo sem commit / ref inválida não trava — permissivo e barulhento.
    verdict = _evaluate(GateGit(dirty=["src/app.py"], changed_raises=True))
    assert verdict.pendente is False
    assert verdict.aviso


def test_fingerprint_deterministico_e_sensivel_a_mudanca():
    fp1 = compute_fingerprint(ANCHOR, HEAD, ["b.md", "a.md"])
    fp2 = compute_fingerprint(ANCHOR, HEAD, ["a.md", "b.md"])
    assert fp1 == fp2  # ordem dos sujos não altera (determinismo)
    assert fp1 != compute_fingerprint(ANCHOR, HEAD, ["a.md"])  # conjunto muda
    assert fp1 != compute_fingerprint(ANCHOR, "c" * 40, ["b.md", "a.md"])  # HEAD muda


def test_verdict_carrega_fingerprint_do_estado_avaliado():
    git = GateGit(changed=["src/app.py"], dirty=["novo.md"])
    verdict = _evaluate(git)
    assert verdict.fingerprint == compute_fingerprint(ANCHOR, HEAD, ["novo.md"])
