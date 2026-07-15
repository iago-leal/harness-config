"""Serialização round-trip do estado de sessão.

Formato canônico de `.harness/estado-da-sessao.md`: front-matter YAML (header-máquina)
mais corpo Markdown em seções `##` (a narrativa). Reusa `pyyaml` (já dependência) e
o domínio `SessionState`/`SessionNarrative`. Invariante: `parse(render(x)) == x`.
"""

import re
from datetime import datetime, timezone
from typing import Optional

import yaml

from src.core.domain.models import SessionNarrative, SessionState
from src.core.session.errors import MalformedSessionStateError

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", re.DOTALL)

# (título da seção no corpo, atributo do SessionNarrative) — ordem é a de renderização
_SECTIONS = [
    ("O que foi feito", "feito"),
    ("Próximos passos", "proximos_passos"),
    ("Pendências / bloqueios", "pendencias"),
    ("Ponteiros", "ponteiros"),
]
_ATTR_BY_TITLE = {title: attr for title, attr in _SECTIONS}
_REQUIRED_META = ("commit", "feature", "start_time", "status")


def parse(text: str) -> Optional[SessionState]:
    """Lê o arquivo de estado de sessão.

    Retorna ``None`` quando o conteúdo é o template inicial gravado pelo ``init``
    (os campos obrigatórios todos ``null``): equivale a "sem sessão", como um
    arquivo ausente. Levanta ``MalformedSessionStateError`` para corrupção real —
    front-matter ausente, YAML inválido, campos faltando ou nulos PARCIAIS (RN-N4).
    """
    match = _FRONTMATTER_RE.match(text.strip() + "\n")
    if not match:
        raise MalformedSessionStateError(
            "Estado de sessão sem front-matter YAML delimitado por '---'."
        )

    raw_meta, body = match.group(1), match.group(2)
    try:
        meta = yaml.safe_load(raw_meta) or {}
    except yaml.YAMLError as exc:
        raise MalformedSessionStateError(f"Front-matter YAML inválido: {exc}") from exc
    if not isinstance(meta, dict):
        raise MalformedSessionStateError("Front-matter YAML não é um mapeamento.")

    missing = [k for k in _REQUIRED_META if k not in meta]
    if missing:
        raise MalformedSessionStateError(
            f"Front-matter sem campos obrigatórios: {', '.join(missing)}."
        )

    if all(meta[k] is None for k in _REQUIRED_META):
        # Estado inicial do `init`: todos os obrigatórios null. Sessão inexistente,
        # não corrupção — não há degradação em silêncio porque o nulo é total e
        # explícito. Nulo PARCIAL não entra aqui e segue para o caminho barulhento.
        return None

    start_time = _coerce_datetime(meta["start_time"])
    try:
        return SessionState(
            commit_hash=str(meta["commit"]),
            active_feature=str(meta["feature"]),
            start_time=start_time,
            is_active=str(meta["status"]).strip().lower() == "active",
            narrative=_parse_body(body),
            # Anti-loop do gate de registro (022): opcionais — estados pré-022
            # (sem as chaves) herdam None, preservando a retrocompatibilidade.
            gate_lembrete_fingerprint=meta.get("gate_lembrete_fingerprint"),
            gate_encerramento_fingerprint=meta.get("gate_encerramento_fingerprint"),
        )
    except ValueError as exc:
        raise MalformedSessionStateError(f"Campos de estado inválidos: {exc}") from exc


def render(state: SessionState) -> str:
    """Serializa o SessionState para o formato canônico (front-matter + corpo)."""
    meta = {
        "commit": state.commit_hash,
        "feature": state.active_feature,
        "start_time": state.start_time.isoformat(),
        "status": "active" if state.is_active else "inactive",
    }
    # Chaves do gate (022) só quando preenchidas: sem gate acionado, o arquivo
    # permanece byte-compatível com o formato pré-022.
    if state.gate_lembrete_fingerprint:
        meta["gate_lembrete_fingerprint"] = state.gate_lembrete_fingerprint
    if state.gate_encerramento_fingerprint:
        meta["gate_encerramento_fingerprint"] = state.gate_encerramento_fingerprint
    front = yaml.safe_dump(meta, sort_keys=False, allow_unicode=True).strip()
    body = render_narrative(state.narrative or SessionNarrative())
    return f"---\n{front}\n---\n\n{body}"


def render_narrative(narrative: SessionNarrative) -> str:
    """Renderiza apenas o corpo (as seções) — usado também na reinjeção de contexto."""
    blocks = []
    for title, attr in _SECTIONS:
        lines = [f"## {title}"]
        lines.extend(f"- {item}" for item in (getattr(narrative, attr) or []))
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks) + "\n"


def _coerce_datetime(value) -> datetime:
    if isinstance(value, datetime):
        dt = value
    else:
        try:
            dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except ValueError as exc:
            raise MalformedSessionStateError(f"start_time inválido: {value!r}") from exc
    return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt


def _parse_body(body: str) -> SessionNarrative:
    data = {attr: [] for _, attr in _SECTIONS}
    current = None
    for line in body.splitlines():
        header = re.match(r"^##\s+(.*?)\s*$", line)
        if header:
            current = _ATTR_BY_TITLE.get(header.group(1).strip())
            continue
        item = re.match(r"^-\s+(.*?)\s*$", line)
        if item and current:
            data[current].append(item.group(1))
    return SessionNarrative(**data)
