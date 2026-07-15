"""Gate de registro de microdecisões (feature 022).

Avaliação PURA de pendência de registro: houve trabalho substantivo na sessão
(diff da âncora ∪ working tree sujo) sem nenhuma ficha ``MD-*.md`` nova ou
modificada? O veredito deriva só de sinal físico verificável (RN-02 da 022),
nunca de metadado auto-declarado. Agnóstico ao harness (RN-N5): este módulo não
conhece ``active_harness`` nem decide COMO interceptar — bloqueio, lembrete ou
advisory são escolhas da borda (close_flow, ``decisions --gate``, agy-hook).

Trabalho substantivo é qualquer mudança versionável, SEM filtro por tipo de
arquivo (esclarecimento de 2026-07-15: repositórios documentais — contratos,
documentos — contam tanto quanto código). Excluem-se apenas os artefatos de
estado do próprio harness e as fichas de decisão em si.
"""

import hashlib
import re
from typing import List, Optional

from pydantic import BaseModel, Field

_FICHA_RE = re.compile(r"^MD-.*\.md$")


class GateVerdict(BaseModel):
    """Resultado da avaliação. Não é persistido — só os fingerprints sobrevivem,
    nos campos de anti-loop do ``SessionState``.

    Dupla identidade (feature 023): ``fingerprint`` é a identidade FINA
    (âncora + HEAD + sujos), consumida pelo portão do encerramento — lá,
    trabalho novo deve rearmar a garantia. ``fingerprint_lembrete`` é a
    identidade GROSSA (só a âncora), consumida pelo lembrete do fim de turno —
    estável na sessão, o lembrete dispara no máximo uma vez."""

    pendente: bool
    mudancas: List[str] = Field(default_factory=list)
    fichas_tocadas: List[str] = Field(default_factory=list)
    fingerprint: str = ""
    fingerprint_lembrete: str = ""
    aviso: Optional[str] = None


def compute_fingerprint(anchor: str, head: str, dirty: list) -> str:
    """Identidade determinística do estado de pendência (D-03).

    ``sha1(âncora + HEAD + sujos ordenados)``: mudança nova → HEAD ou o conjunto
    sujo mudam → fingerprint muda → o gate volta a valer. Sem relógio.
    """
    payload = "\n".join([anchor or "", head or "", *sorted(dirty or [])])
    return hashlib.sha1(payload.encode("utf-8")).hexdigest()


def compute_lembrete_fingerprint(anchor: str) -> str:
    """Identidade grossa do lembrete (023/D-02): ``sha1(âncora)``.

    A âncora é estável do início ao encerramento da sessão, então o lembrete
    do fim de turno dispara no máximo uma vez por sessão — nem arquivo tocado
    nem commit novo o rearmam. A finura de ``compute_fingerprint`` fica
    reservada ao portão do encerramento, onde trabalho novo DEVE rearmar."""
    return hashlib.sha1((anchor or "").encode("utf-8")).hexdigest()


def evaluate_registration_gate(git, repo_path: str, session, config) -> GateVerdict:
    """Avalia a pendência de registro para a sessão dada.

    Fail-open barulhento (RN-05): âncora ilegível, repo sem commit ou falha de
    git devolvem ``pendente=False`` com ``aviso`` preenchido — o gate nunca
    trava o agente por erro interno; cabe à borda ecoar o aviso em stderr.
    """
    anchor = session.commit_hash
    try:
        head = git.get_head_commit(repo_path)
        dirty = git.list_dirty_paths(repo_path)
        changed = git.list_changed_paths_since(repo_path, anchor)
    except Exception as exc:
        return GateVerdict(
            pendente=False,
            aviso=f"gate de registro pulado (baseline ilegível): {exc}",
        )

    fingerprint = compute_fingerprint(anchor, head, dirty)
    universo = sorted(set(changed) | set(dirty))

    excluidos = {
        config.session.state_file,
        config.decisions.index_file,
        config.decisions.header_file,
    }
    dir_prefix = config.decisions.dir.rstrip("/") + "/"
    fichas = [
        p
        for p in universo
        if p.startswith(dir_prefix) and _FICHA_RE.match(p[len(dir_prefix):])
    ]
    mudancas = [p for p in universo if p not in excluidos and p not in fichas]

    return GateVerdict(
        pendente=bool(mudancas) and not fichas,
        mudancas=mudancas,
        fichas_tocadas=fichas,
        fingerprint=fingerprint,
        fingerprint_lembrete=compute_lembrete_fingerprint(anchor),
    )
