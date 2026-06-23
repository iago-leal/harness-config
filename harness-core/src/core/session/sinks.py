"""Estratégia de entrega do estado ao contexto do agente (na borda).

Duas famílias confirmadas (ver `decisoes/MD-0003.md`):
- HookContextSink: hook `SessionStart` + `hookSpecificOutput.additionalContext`
  no stdout. Serve Claude Code e Gemini CLI (mesmo contrato).
- FileProjectionSink: projeta o estado num arquivo estático relido a cada boot.
  Para o Antigravity (`agy`), que não injeta stdout no contexto.

O core não conhece harness (RN-N5); a seleção por `active_harness` vive aqui.
"""

import json
import os
from abc import ABC, abstractmethod

from src.core.ports.fs import FileSystemPort


class SessionSink(ABC):
    @abstractmethod
    def emit(self, context_text: str) -> None:
        """Entrega o texto de estado ao contexto do agente, pelo mecanismo do harness."""


class HookContextSink(SessionSink):
    """Família A — Claude Code e Gemini CLI."""

    MAX_CHARS = 10000  # teto do additionalContext no Claude

    def emit(self, context_text: str) -> None:
        text = context_text
        if len(text) > self.MAX_CHARS:
            text = (
                text[: self.MAX_CHARS - 60]
                + "\n\n…[truncado: estado excede 10000 caracteres]"
            )
        payload = {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": text,
            }
        }
        print(json.dumps(payload, ensure_ascii=False))


class FileProjectionSink(SessionSink):
    """Família B — Antigravity (`agy`)."""

    def __init__(
        self, fs: FileSystemPort, target_path: str = ".agents/rules/estado-sessao.md"
    ):
        self.fs = fs
        self.target_path = target_path

    def emit(self, context_text: str) -> None:
        parent = os.path.dirname(self.target_path)
        if parent:
            self.fs.makedirs(parent)
        self.fs.write_file_atomic(self.target_path, context_text)


_FAMILY_BY_HARNESS = {
    "claude": "hook",
    "gemini": "hook",
    "antigravity": "file",
}


def get_sink(active_harness: str, fs: FileSystemPort) -> SessionSink:
    """Resolve o sink pelo harness ativo. Desconhecido → erro barulhento."""
    family = _FAMILY_BY_HARNESS.get(active_harness)
    if family is None:
        raise ValueError(
            f"Harness desconhecido: {active_harness!r}. "
            f"Esperado um de {sorted(_FAMILY_BY_HARNESS)}."
        )
    return HookContextSink() if family == "hook" else FileProjectionSink(fs)
