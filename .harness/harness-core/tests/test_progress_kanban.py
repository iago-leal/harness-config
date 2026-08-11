"""Testes do exportador kanban (feature 027).

O board é a SEGUNDA projeção da ``Medicao`` (a primeira é o markdown): cards
``category == "harness"`` são recomputados do zero a cada exportação, com ids
estáveis ``hns:*`` e ``creation_time`` derivado das fontes (nunca da hora
corrente); cards manuais são preservados intactos na coluna onde estiverem
(RN-01); a coluna ``testing`` nunca recebe card gerenciado.
"""

import json

from src.core.progress.kanban import extrair_manuais, render_board
from src.core.progress.service import (
    AcaoProgresso,
    Alerta,
    FeatureProgresso,
    Medicao,
)


def _medicao():
    return Medicao(
        forward_disponivel=True,
        ativa=FeatureProgresso(
            feature_id="026",
            short_name="x",
            papel="ativa",
            estagio_fisico="coding-em-progresso",
            iniciada_em="2026-08-10T09:00:00Z",
            feitas=1,
            total=2,
            acoes=[
                AcaoProgresso(
                    acao_id="T001",
                    descricao="a",
                    fase="Fase 1, Preparação",
                    feita=True,
                    criada_em="2026-08-11T12:00:00Z",
                ),
                AcaoProgresso(
                    acao_id="T002",
                    descricao="b",
                    fase="Fase 1, Preparação",
                    feita=False,
                    criada_em="2026-08-10T09:00:00Z",
                ),
            ],
        ),
        pausadas=[
            FeatureProgresso(
                feature_id="024",
                short_name="p",
                papel="pausada",
                estagio_fisico="coding-em-progresso",
                iniciada_em="2026-08-01T08:00:00Z",
                feitas=1,
                total=2,
            )
        ],
        alertas=[
            Alerta(
                severidade="alta", origem="_reversa_forward/026-x", mensagem="diverge"
            ),
            Alerta(severidade="media", origem="w.md", mensagem="pendência"),
        ],
    )


def _cards_por_id(board):
    return {c["id"]: c for coluna in board.values() for c in coluna}


def test_board_deterministico_byte_a_byte():
    assert render_board(_medicao(), None) == render_board(_medicao(), None)


def test_namespace_e_ids_estaveis():
    board = json.loads(render_board(_medicao(), None))
    cards = _cards_por_id(board)
    assert set(cards) == {
        "hns:026",
        "hns:026:T001",
        "hns:026:T002",
        "hns:024",
        "hns:alerta:_reversa_forward/026-x",
        "hns:alerta:w.md",
    }
    assert all(c["category"] == "harness" for c in cards.values())


def test_mapeamento_de_colunas():
    board = json.loads(render_board(_medicao(), None))
    por_coluna = {col: [c["id"] for c in cards] for col, cards in board.items()}
    assert por_coluna["in-progress"] == ["hns:026"]
    assert "hns:026:T001" in por_coluna["done"]
    assert "hns:026:T002" in por_coluna["todo"]
    assert "hns:024" in por_coluna["todo"]
    assert "hns:alerta:w.md" in por_coluna["todo"]
    # `testing` pertence ao fluxo humano: nenhum card gerenciado (RN-04).
    assert por_coluna["testing"] == []


def test_alertas_viram_bug_com_prioridade_por_severidade():
    cards = _cards_por_id(json.loads(render_board(_medicao(), None)))
    alta = cards["hns:alerta:_reversa_forward/026-x"]
    media = cards["hns:alerta:w.md"]
    assert (alta["type"], alta["prio"]) == ("bug", 9)
    assert (media["type"], media["prio"]) == ("bug", 5)


def test_creation_time_derivado_das_fontes():
    cards = _cards_por_id(json.loads(render_board(_medicao(), None)))
    assert cards["hns:026:T001"]["creation_time"] == "2026-08-11T12:00:00Z"
    assert cards["hns:026"]["creation_time"] == "2026-08-10T09:00:00Z"
    assert cards["hns:024"]["creation_time"] == "2026-08-01T08:00:00Z"
    assert cards["hns:alerta:w.md"]["creation_time"] == "2026-08-10T09:00:00Z"


def test_merge_preserva_manuais_e_recomputa_gerenciados():
    manual_todo = {
        "id": "99",
        "title": "Nova demanda",
        "type": "note",
        "prio": 0,
        "creation_time": "2026-08-05T00:00:00.000Z",
        "category": "medico",
    }
    manual_testing = {"id": "77", "title": "Validando à mão", "type": "note"}
    adulterado = {
        "id": "hns:026:T001",
        "title": "título editado à mão",
        "category": "harness",
    }
    board_atual = json.dumps(
        {
            "todo": [manual_todo, adulterado],
            "in-progress": [],
            "testing": [manual_testing],
            "done": [],
        }
    )
    board = json.loads(render_board(_medicao(), board_atual))
    assert manual_todo in board["todo"]
    assert board["testing"] == [manual_testing]
    # O gerenciado adulterado foi recomputado: volta a `done` com título derivado.
    cards = _cards_por_id(board)
    assert cards["hns:026:T001"]["title"] == "T001 — a"
    assert cards["hns:026:T001"] in board["done"]
    assert all(c["id"] != "hns:026:T001" for c in board["todo"])


def test_manuais_ficam_depois_dos_gerenciados_na_coluna():
    manual = {"id": "99", "title": "m", "category": ""}
    board_atual = json.dumps(
        {"todo": [manual], "in-progress": [], "testing": [], "done": []}
    )
    board = json.loads(render_board(_medicao(), board_atual))
    assert board["todo"][-1] == manual


def test_sem_ciclo_forward_board_so_tem_manuais():
    manual = {"id": "1", "title": "m"}
    board_atual = json.dumps(
        {"todo": [manual], "in-progress": [], "testing": [], "done": []}
    )
    board = json.loads(render_board(Medicao(), board_atual))
    assert board["todo"] == [manual]
    assert board["in-progress"] == [] and board["done"] == []


def test_extrair_manuais_reprova_board_invalido():
    for texto in ("{ quebrado", "[1, 2]", '{"todo": {"a": 1}}'):
        try:
            extrair_manuais(texto)
        except ValueError:
            continue
        raise AssertionError(f"board inválido aceito: {texto!r}")
