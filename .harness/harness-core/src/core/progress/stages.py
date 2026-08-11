"""Detecção de estágio físico e contagem de checkboxes (feature 026, D-04).

PARIDADE OBRIGATÓRIA: este módulo é a implementação em código da tabela de
estágio físico e da regra de contagem que vivem em prosa no skill
``.claude/skills/reversa-requirements/SKILL.md`` (seção "Detecção de feature
em andamento"). Se a tabela do skill mudar, este módulo muda junto — item de
vigilância da feature 026.

Regra de contagem: só linhas de TABELA terminadas em ``| [ ] |``/``| [X] |``
contam como ação; o checkbox pode vir envolto em crase (formato real dos
``actions.md`` gerados). Cabeçalhos, separadores e listas livres são
ignorados.
"""

import re
from typing import List, Tuple

_CHECKBOX_ROW = re.compile(r"^\|.*\|\s*`?\[( |X)\]`?\s*\|$")
_FASE_HEADING = re.compile(r"^##\s+(.+?)\s*$")


def detectar_estagio(fs, feature_dir: str) -> str:
    """Estágio físico da feature, derivado só dos artefatos em disco.

    ``vazio`` | ``requirements`` | ``plan`` | ``coding-em-progresso`` |
    ``done``. Um ``actions.md`` presente mas ainda sem nenhuma linha de ação
    conta como ``plan``: a decomposição não terminou.
    """
    base = feature_dir.rstrip("/")
    if not fs.exists(f"{base}/requirements.md"):
        return "vazio"
    if not fs.exists(f"{base}/roadmap.md"):
        return "requirements"
    if not fs.exists(f"{base}/actions.md"):
        return "plan"
    feitas, total = contar_checkboxes(fs.read_file(f"{base}/actions.md"))
    if total == 0:
        return "plan"
    return "done" if feitas == total else "coding-em-progresso"


def contar_checkboxes(actions_md: str) -> Tuple[int, int]:
    """``(feitas, total)`` sobre o documento inteiro."""
    feitas = total = 0
    for linha in actions_md.splitlines():
        m = _CHECKBOX_ROW.match(linha.strip())
        if not m:
            continue
        total += 1
        if m.group(1) == "X":
            feitas += 1
    return feitas, total


def listar_acoes(actions_md: str) -> List[Tuple[str, str, str, bool]]:
    """``[(fase, acao_id, descricao, feita), ...]`` na ordem do documento.

    Mesmo critério de linha de ação de ``contar_checkboxes`` (paridade com o
    skill); as duas primeiras células da linha são o ID real (``T00N``) e a
    descrição. Necessário ao exportador kanban (027), que emite um card por
    ação com id estável ``hns:<feature>:<T00N>``.
    """
    resultado: List[Tuple[str, str, str, bool]] = []
    fase = ""
    for linha in actions_md.splitlines():
        h = _FASE_HEADING.match(linha)
        if h:
            fase = h.group(1)
            continue
        limpa = linha.strip()
        m = _CHECKBOX_ROW.match(limpa)
        if not m:
            continue
        celulas = [c.strip() for c in limpa.strip("|").split("|")]
        acao_id = celulas[0] if celulas else ""
        descricao = celulas[1] if len(celulas) > 1 else ""
        resultado.append((fase, acao_id, descricao, m.group(1) == "X"))
    return resultado


def contar_por_fase(actions_md: str) -> List[Tuple[str, int, int]]:
    """``[(titulo_da_secao, feitas, total), ...]`` na ordem do documento.

    Seções ``##`` sem nenhuma linha de ação (Resumo, Notas) ficam de fora.
    """
    resultado: List[Tuple[str, int, int]] = []
    atual = None  # [titulo, feitas, total]
    for linha in actions_md.splitlines():
        h = _FASE_HEADING.match(linha)
        if h:
            if atual and atual[2] > 0:
                resultado.append(tuple(atual))
            atual = [h.group(1), 0, 0]
            continue
        m = _CHECKBOX_ROW.match(linha.strip())
        if m and atual:
            atual[2] += 1
            if m.group(1) == "X":
                atual[1] += 1
    if atual and atual[2] > 0:
        resultado.append(tuple(atual))
    return resultado
