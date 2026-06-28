"""Materialização da skill de sessão `encerrar-sessao` (feature 018).

Substitui `materialize_session_commands`: em vez de gravar um arquivo `.md` que
delega ao binário, grava a ÁRVORE de uma skill versionável (`SKILL.md` +
`scripts/`) sob o diretório de skills de cada harness — Claude (`.claude/skills`)
e Antigravity (`.agents/skills`); o Gemini, sem superfície de skill
(`skills_dir` → `None`), é pulado. A árvore é AGNÓSTICA ao harness (mesmos bytes
em todos), lida dos assets do core — recurso estático que viaja na cópia do
`init`/`upgrade` —, de modo que só o diretório-prefixo varia por harness (RN-N5).

A migração remove os artefatos antigos (command/workflow `.md`) via
`stale_session_command_paths`, estendendo o mecanismo da 017: apaga só o arquivo
nomeado pelo perfil, nunca o diretório nem arquivos de terceiros (não-destrutivo,
RN-03). Toda escrita ocorre sob `project_path` (footprint global zero, RN-N17).
"""

import os
from typing import List, Optional

from src.core.ports.fs import FileSystemPort
from src.core.install.harness_profiles import (
    AntigravityProfile,
    ClaudeProfile,
    GeminiProfile,
)

_SKILL_NAME = "encerrar-sessao"
_ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets", "skills", _SKILL_NAME)

# Perfis consultados para o diretório de skills. Os que devolvem ``None`` (Gemini)
# têm a escrita da árvore pulada, mas ainda têm seus órfãos legados limpos.
_PROFILES = (ClaudeProfile, AntigravityProfile, GeminiProfile)


def skill_tree(assets_dir: str = _ASSETS_DIR) -> dict:
    """Árvore agnóstica da skill: ``{caminho_relativo: conteúdo}``.

    Lê os assets do core do disco (mesmos bytes para todos os harnesses). Ignora
    ``__pycache__`` e ``.pyc`` para não materializar lixo de compilação.
    """
    tree = {}
    for dirpath, dirs, files in os.walk(assets_dir):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for fn in files:
            if fn.endswith(".pyc"):
                continue
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, assets_dir)
            with open(full, "r", encoding="utf-8") as fh:
                tree[rel] = fh.read()
    return tree


def materialize_session_skills(
    fs: FileSystemPort,
    project_path: str,
    profiles: Optional[List[object]] = None,
) -> None:
    """Grava a skill `encerrar-sessao` por harness e limpa os artefatos antigos.

    Para cada perfil: remove os órfãos legados declarados (command/workflow `.md`)
    e, se o perfil expõe um `skills_dir`, grava a árvore da skill (atômica) sob
    ``<project_path>/<skills_dir>/encerrar-sessao/``.
    """
    if profiles is None:
        profiles = [cls() for cls in _PROFILES]

    tree = skill_tree()
    for profile in profiles:
        # Remove órfãos dos artefatos antigos (migração command/workflow → skill),
        # tenha o perfil superfície de skill ou não. Só o arquivo nomeado.
        for stale_rel in profile.stale_session_command_paths():
            stale_dest = os.path.join(project_path, stale_rel)
            if fs.exists(stale_dest):
                fs.remove(stale_dest)

        skills_dir = profile.skills_dir()
        if skills_dir is None:
            continue
        base = os.path.join(project_path, skills_dir, _SKILL_NAME)
        for rel, content in tree.items():
            dest = os.path.join(base, rel)
            fs.makedirs(os.path.dirname(dest))
            fs.write_file_atomic(dest, content)
