"""Materialização dos slash commands de sessão (feature 010).

Rotina única, compartilhada por `init` e `upgrade`, que grava os arquivos de
slash command que acionam `./harness cmd encerrar-sessao` na IDE do agente. A
escrita é INCONDICIONAL (não depende do `active_harness`): grava para todo
perfil que exponha um artefato de comando — hoje o Claude (`.claude/commands/`)
e o Antigravity (`.agents/workflows/`). O conteúdo de cada arquivo vive no
respectivo `HarnessProfile`; aqui só iteramos e gravamos, sempre sob
`project_path` (footprint global zero, RN-N17). Espelha o molde de
`antigravity_hooks.materialize_hooks_json`.
"""

import os
from typing import List, Optional

from src.core.ports.fs import FileSystemPort
from src.core.install.harness_profiles import (
    AntigravityProfile,
    ClaudeProfile,
    GeminiProfile,
)

# Perfis consultados para o artefato de comando. Os que devolvem ``None`` são
# pulados, deixando a porta aberta a outros harnesses sem mudar esta rotina.
_COMMAND_PROFILES = (ClaudeProfile, AntigravityProfile, GeminiProfile)


def materialize_session_commands(
    fs: FileSystemPort,
    project_path: str,
    command_path: str,
    profiles: Optional[List[object]] = None,
) -> None:
    """Grava os arquivos de slash command de encerrar-sessao sob `project_path`.

    Para cada perfil que devolva um artefato ``(rel_path, content)``, cria o
    diretório alvo e grava o arquivo de forma atômica. ``command_path`` é o
    caminho absoluto do wrapper ``./harness`` do projeto, embutido no comando do
    Antigravity. Perfis que devolvem ``None`` (ex.: Gemini) são ignorados.
    """
    if profiles is None:
        profiles = [cls() for cls in _COMMAND_PROFILES]

    for profile in profiles:
        artifact = profile.session_command_artifact(command_path)
        if artifact is None:
            continue
        rel_path, content = artifact
        dest = os.path.join(project_path, rel_path)
        fs.makedirs(os.path.dirname(dest))
        fs.write_file_atomic(dest, content)
