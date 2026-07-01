"""Migração das instalações do layout copiado para a FONTE ÚNICA (feature 020).

Converte cada projeto sob uma raiz (default ``~/dev``) do modelo antigo — uma
cópia do ``harness-core`` + venv por projeto — para o shim que executa o core do
upstream. Ordem segura: instala o shim e reescreve os hooks ANTES de remover a
cópia local, para nunca deixar o projeto sem executor.

**Exceção consciente ao footprint global zero (RN-N17):** ao contrário de
``init``/``materialize``, o migrate atua sobre OUTROS projetos por design — é uma
ferramenta de manutenção da base instalada. A guarda inegociável é nunca remover
o core do próprio **upstream** (a fonte de todos) nem de uma autoreferência.
"""

import os
import re

from src.core.ports.fs import FileSystemPort
from src.core.domain.layout import CORE_REL_PATH, CORE_MAIN_REL_PATH
from src.core.bootstrap.shim import render_shim
from src.core.bootstrap.service import BootstrapService, NotAGitRepositoryError
from src.core.install.claude_settings import materialize_claude_settings

# Diretório do core no layout legado (pré-011, core na raiz do projeto). O
# `livro-mfc` carrega os dois (legado + `.harness/harness-core`).
_LEGACY_CORE_DIRNAME = "harness-core"
_CORE_BASENAME = "harness-core"


class MigrateService:
    def __init__(self, fs: FileSystemPort):
        self.fs = fs

    def migrate(
        self, root: str, dry_run: bool = False, upstream_self: str = None
    ) -> list:
        """Migra todas as instalações sob ``root``.

        ``upstream_self`` é o caminho absoluto do upstream a partir do qual este
        próprio core roda; esse diretório NUNCA é migrado (guarda de segurança).
        Devolve uma lista de dicionários de resultado, um por instalação achada.
        """
        root = os.path.abspath(root)
        self_abs = os.path.abspath(upstream_self) if upstream_self else None
        results = []
        for name in sorted(self._safe_list(root)):
            proj = os.path.join(root, name)
            toml_path = os.path.join(proj, "harness.toml")
            if not self.fs.exists(toml_path):
                continue
            results.append(self._migrate_one(proj, toml_path, dry_run, self_abs))
        return results

    def _migrate_one(self, proj, toml_path, dry_run, self_abs):
        proj_abs = os.path.abspath(proj)
        toml = self.fs.read_file(toml_path)
        upstream = self._field(toml, "upstream_path")
        active = self._field(toml, "active_harness") or "claude"

        # GUARDA 1: nunca migrar o próprio upstream (a fonte real do core).
        if self_abs and proj_abs == self_abs:
            return _skip(proj, "upstream (fonte do core)")

        # GUARDA 2: nunca migrar uma autoreferência (upstream dentro do alvo).
        if upstream:
            up_abs = os.path.abspath(upstream)
            if up_abs == proj_abs or up_abs.startswith(proj_abs + os.sep):
                return _skip(proj, "upstream (autoreferência)")
        else:
            return _skip(proj, "sem upstream_path")

        # O core do upstream precisa existir para o shim funcionar.
        if not self.fs.exists(
            os.path.join(os.path.abspath(upstream), CORE_MAIN_REL_PATH)
        ):
            return _skip(proj, "core do upstream ausente")

        core_dir = os.path.join(proj, CORE_REL_PATH)
        legacy_dir = os.path.join(proj, _LEGACY_CORE_DIRNAME)
        has_core = self.fs.exists(core_dir)
        has_legacy = self.fs.exists(os.path.join(legacy_dir, "src", "main.py"))
        to_remove = [
            d for d, ok in ((core_dir, has_core), (legacy_dir, has_legacy)) if ok
        ]

        if dry_run:
            return {"project": proj, "status": "would-migrate", "removes": to_remove}

        # 1. Shim no lugar do wrapper.
        wrapper = os.path.join(proj, "harness")
        self.fs.write_file(wrapper, render_shim())
        self.fs.make_executable(wrapper)

        # 2. Hooks git (não-destrutivo, via shim). Sem .git → segue sem hooks.
        try:
            BootstrapService(self.fs).install_hooks(proj)
        except NotAGitRepositoryError:
            pass

        # 3. Settings do Claude (merge por-item), quando aplicável.
        if active == "claude":
            materialize_claude_settings(self.fs, proj)

        # 4. Remove o campo `version` do harness.toml.
        self.fs.write_file(toml_path, self._strip_version(toml))

        # 5. Remove a(s) cópia(s) do core POR ÚLTIMO — shim e hooks já apontam
        # para o upstream, então o projeto nunca fica sem executor.
        for d in to_remove:
            self._safe_remove_core(d)

        return {"project": proj, "status": "migrated", "removed": to_remove}

    def _safe_remove_core(self, path):
        """Remove a árvore do core, recusando qualquer alvo que não seja um
        diretório ``harness-core`` (guarda contra um `rm -rf` malformado)."""
        if os.path.basename(os.path.normpath(path)) != _CORE_BASENAME:
            raise ValueError(
                f"Recusando remover árvore que não é '{_CORE_BASENAME}': {path}"
            )
        self.fs.remove_tree(path)

    def _safe_list(self, root):
        try:
            return self.fs.list_dir(root)
        except Exception:
            return []

    @staticmethod
    def _field(toml, name):
        m = re.search(rf'{name}\s*=\s*"([^"]*)"', toml)
        return m.group(1) if m else None

    @staticmethod
    def _strip_version(toml):
        return re.sub(r'^version\s*=\s*"[^"]*"\n?', "", toml, flags=re.MULTILINE)


def _skip(proj, reason):
    return {"project": proj, "status": "skipped", "reason": reason}
