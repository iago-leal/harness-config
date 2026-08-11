"""Exportador kanban da ``Medicao`` (feature 027).

ÚNICO módulo do core que conhece o schema do board do vscode-kanban (fork do
mantenedor): colunas ``todo``/``in-progress``/``testing``/``done``, cards com
``id``/``title``/``type``/``prio``/``creation_time``/``description``/
``details``/``category``. Se o fork mudar o schema, muda este arquivo (D-01).

Posse por namespace: cards ``category == "harness"`` pertencem ao exportador
e são recomputados do zero a cada exportação; qualquer outro card é MANUAL,
preservado byte a byte na coluna onde estiver (RN-01) e, fora da coluna
``done``, medido como demanda de entrada do mantenedor (RN-06).

Determinismo (RN-03): ids derivados dos ids reais (``hns:*``),
``creation_time`` derivado das fontes; nenhum caminho consulta a hora
corrente.
"""

import json

_CATEGORIA_GERENCIADA = "harness"
_COLUNAS = ("todo", "in-progress", "testing", "done")


def extrair_manuais(board_json: str):
    """``{coluna: [cards manuais]}`` do board existente, ordem preservada.

    Levanta ``ValueError`` se o texto não for um board JSON válido (objeto no
    topo, colunas como listas): a borda trata como falha real (RN-07) e nunca
    sobrescreve o arquivo.
    """
    board = json.loads(board_json)
    if not isinstance(board, dict):
        raise ValueError("board não é um objeto JSON")
    manuais = {}
    for coluna in _COLUNAS:
        cards = board.get(coluna) or []
        if not isinstance(cards, list):
            raise ValueError(f"coluna '{coluna}' não é uma lista")
        manuais[coluna] = [
            c
            for c in cards
            if not (isinstance(c, dict) and c.get("category") == _CATEGORIA_GERENCIADA)
        ]
    return manuais


def _card(card_id, title, type_, prio, creation_time, descricao):
    return {
        "id": card_id,
        "title": title,
        "type": type_,
        "prio": prio,
        "creation_time": creation_time,
        "description": {"content": descricao, "mime": "text/markdown"},
        "category": _CATEGORIA_GERENCIADA,
    }


def _nome(feature):
    if feature.short_name:
        return f"{feature.feature_id}-{feature.short_name}"
    return feature.feature_id


def _card_resumo(feature, papel_rotulo, creation_time, prio):
    return _card(
        f"hns:{feature.feature_id}",
        f"{_nome(feature)} — {feature.feitas}/{feature.total} ações",
        "note",
        prio,
        creation_time,
        f"Feature {papel_rotulo} (estágio físico: {feature.estagio_fisico}).",
    )


def render_board(medicao, board_atual):
    """Serializa o board: namespace gerenciado recomputado + manuais intactos.

    ``board_atual`` é o conteúdo do arquivo existente ou ``None`` (primeira
    exportação). ``creation_time`` vem inteiro da ``Medicao`` (``criada_em``
    das ações, ``iniciada_em`` das features, D-06): nenhum caminho consulta a
    hora corrente. Levanta ``ValueError`` para board existente ilegível.
    """
    manuais = (
        extrair_manuais(board_atual)
        if board_atual is not None
        else {coluna: [] for coluna in _COLUNAS}
    )

    gerenciados = {coluna: [] for coluna in _COLUNAS}
    ativa = medicao.ativa
    base = ativa.iniciada_em if ativa is not None else ""
    if ativa is not None:
        gerenciados["in-progress"].append(_card_resumo(ativa, "ativa", base, 1))
        for acao in ativa.acoes:
            coluna = "done" if acao.feita else "todo"
            gerenciados[coluna].append(
                _card(
                    f"hns:{ativa.feature_id}:{acao.acao_id}",
                    f"{acao.acao_id} — {acao.descricao}",
                    "note",
                    0,
                    acao.criada_em,
                    f"Ação da feature `{_nome(ativa)}`, fase '{acao.fase}'.",
                )
            )
    for pausada in medicao.pausadas:
        gerenciados["todo"].append(
            _card_resumo(pausada, "pausada", pausada.iniciada_em, 1)
        )
    for alerta in medicao.alertas:
        gerenciados["todo"].append(
            _card(
                f"hns:alerta:{alerta.origem}",
                f"[{alerta.severidade}] {alerta.mensagem}",
                "bug",
                9 if alerta.severidade == "alta" else 5,
                base,
                f"Origem: `{alerta.origem}`. O alerta existe enquanto a causa existir.",
            )
        )

    board = {coluna: gerenciados[coluna] + manuais[coluna] for coluna in _COLUNAS}
    return json.dumps(board, ensure_ascii=False, indent=2) + "\n"
