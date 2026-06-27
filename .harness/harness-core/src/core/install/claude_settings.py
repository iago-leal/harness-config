"""Materialização do `.claude/settings.json` do Claude (feature 016, RN-05).

Rotina única, compartilhada por `init` e `upgrade`, que GARANTE de forma
idempotente a presença dos ganchos do harness (`SessionStart → cmd resume`,
`PostToolUse → format`, `Stop → decisions`) no `settings.json` do projeto-alvo,
preservando as demais chaves de topo e eventos de hook de terceiros. O conteúdo
canônico vem do `ClaudeProfile` (`hooks_block()`). Toda escrita ocorre sob
`project_path` (footprint global zero, RN-N17). Espelha o molde de
`antigravity_hooks.materialize_hooks_json`.

Antes da 016, este `settings.json` nunca era escrito automaticamente: o bloco de
ganchos do Claude só era emitido como texto colável no install-prompt, o que
deixava consumidores sem o `SessionStart → cmd resume` e, por isso, com a sessão
presa em `inactive`.
"""

import json
import os

from src.core.ports.fs import FileSystemPort
from src.core.install.harness_profiles import ClaudeProfile


def materialize_claude_settings(fs: FileSystemPort, project_path: str) -> None:
    """Grava (merge idempotente) os ganchos do harness em `<project_path>/.claude/settings.json`.

    Lê o `settings.json` existente se houver, garante os eventos de hook do
    harness e grava de forma atômica via `fs.write_file_atomic`, preservando
    quaisquer outras chaves de topo e eventos de terceiros.
    """
    harness_hooks = json.loads(ClaudeProfile().hooks_block())["hooks"]

    claude_dir = os.path.join(project_path, ".claude")
    settings_path = os.path.join(claude_dir, "settings.json")

    existing = _read_existing(fs, settings_path)
    hooks = existing.get("hooks")
    if not isinstance(hooks, dict):
        hooks = {}
    # Garante os eventos do harness; preserva eventos de terceiros (ex.: um
    # PreToolUse do usuário) e demais chaves de topo (model, theme, permissions…).
    for event, value in harness_hooks.items():
        hooks[event] = value
    existing["hooks"] = hooks

    fs.makedirs(claude_dir)
    fs.write_file_atomic(
        settings_path, json.dumps(existing, indent=2, ensure_ascii=False) + "\n"
    )


def _read_existing(fs: FileSystemPort, settings_path: str) -> dict:
    """Lê o `settings.json` atual se existir e for JSON válido; senão, dict vazio."""
    if not fs.exists(settings_path):
        return {}
    raw = fs.read_file(settings_path)
    if not raw.strip():
        return {}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}
