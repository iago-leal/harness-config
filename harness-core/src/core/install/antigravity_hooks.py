"""Materialização do `.agents/hooks.json` do Antigravity (feature 009).

Rotina única, compartilhada por `init` e `upgrade`, que escreve o named-hook
`harness` no `hooks.json` do projeto-alvo preservando chaves de terceiros. O
conteúdo canônico do named-hook vem do `AntigravityProfile` (`hooks_block()`),
com o placeholder `<ABS>` substituído pelo caminho absoluto do projeto.
"""

import json
import os
from typing import Optional

from src.core.ports.fs import FileSystemPort
from src.core.install.harness_profiles import AntigravityProfile

ABS_PLACEHOLDER = "<ABS>"


def materialize_hooks_json(
    fs: FileSystemPort,
    project_path: str,
    command_path: str,
    profile: Optional[object] = None,
) -> None:
    """Grava (merge) o named-hook `harness` em `<project_path>/.agents/hooks.json`.

    Lê o `hooks.json` existente se houver, substitui o named-hook `harness` pelo
    bloco canônico do perfil (com `<ABS>` resolvido para `command_path`) e grava
    de forma atômica via `fs.write_file_atomic`, preservando quaisquer outras
    chaves de terceiros. Toda escrita ocorre sob `project_path`.
    """
    if profile is None:
        profile = AntigravityProfile()

    harness_block = _resolve_harness_block(profile.hooks_block(), command_path)

    agents_dir = os.path.join(project_path, ".agents")
    hooks_path = os.path.join(agents_dir, "hooks.json")

    existing = _read_existing(fs, hooks_path)
    existing["harness"] = harness_block

    fs.makedirs(agents_dir)
    fs.write_file_atomic(
        hooks_path, json.dumps(existing, indent=2, ensure_ascii=False) + "\n"
    )


def _resolve_harness_block(hooks_block: str, command_path: str) -> dict:
    """Extrai o named-hook `harness` da STRING JSON do perfil e resolve `<ABS>`."""
    resolved = hooks_block.replace(ABS_PLACEHOLDER, command_path)
    data = json.loads(resolved)
    return data["harness"]


def _read_existing(fs: FileSystemPort, hooks_path: str) -> dict:
    """Lê o `hooks.json` atual se existir e for JSON válido; senão, dict vazio."""
    if not fs.exists(hooks_path):
        return {}
    raw = fs.read_file(hooks_path)
    if not raw.strip():
        return {}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}
