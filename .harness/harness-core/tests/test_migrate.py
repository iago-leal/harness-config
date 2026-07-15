"""Migração para a fonte única (feature 020) — MigrateService com FakeFS.

O migrate atua sobre OUTROS projetos por design (exceção consciente ao footprint
zero), então NÃO usa o RecordingFileSystem. O FakeFS abaixo modela diretórios
(para `list_dir`/`remove_tree`) além de arquivos.
"""

import json

from src.core.ports.fs import FileSystemPort
from src.core.migrate.service import MigrateService

UPSTREAM = "/dev/harness"
UP_MAIN = "/dev/harness/.harness/harness-core/src/main.py"


class FakeFS(FileSystemPort):
    def __init__(self):
        self.files = {}
        self.dirs = set()
        self.executable = set()

    # -- seed helpers -------------------------------------------------------
    def seed_file(self, path, content=""):
        self.write_file(path, content)

    def seed_dir(self, path):
        self.makedirs(path)

    # -- FileSystemPort -----------------------------------------------------
    def read_file(self, path):
        return self.files.get(path, "")

    def write_file(self, path, content):
        self.files[path] = content
        d = path.rsplit("/", 1)[0]
        while d:
            self.dirs.add(d)
            if "/" not in d:
                break
            d = d.rsplit("/", 1)[0]

    def write_file_atomic(self, path, content):
        self.write_file(path, content)

    def exists(self, path):
        return path in self.files or path in self.dirs

    def list_dir(self, path):
        prefix = path.rstrip("/") + "/"
        names = set()
        for p in list(self.files) + list(self.dirs):
            if p.startswith(prefix):
                names.add(p[len(prefix) :].split("/")[0])
        return list(names)

    def makedirs(self, path):
        d = path
        while d:
            self.dirs.add(d)
            if "/" not in d:
                break
            d = d.rsplit("/", 1)[0]

    def remove(self, path):
        self.files.pop(path, None)
        self.dirs.discard(path)

    def remove_tree(self, path):
        prefix = path + "/"
        self.files = {
            p: c
            for p, c in self.files.items()
            if p != path and not p.startswith(prefix)
        }
        self.dirs = {d for d in self.dirs if d != path and not d.startswith(prefix)}

    def is_dir(self, path):
        return path in self.dirs

    def make_executable(self, path):
        self.executable.add(path)


def _base_fs():
    fs = FakeFS()
    # Upstream real (fonte do core) + seu harness.toml autoreferente.
    fs.seed_file(UP_MAIN, "# core do upstream")
    fs.seed_file(
        "/dev/harness/harness.toml",
        f'[harness]\nactive_harness = "claude"\nupstream_path = "{UPSTREAM}"\n',
    )
    return fs


def _seed_installation(fs, proj, *, with_git=True, foreign_pre_commit=False):
    fs.seed_file(
        f"{proj}/harness.toml",
        f'[harness]\nactive_harness = "claude"\nupstream_path = "{UPSTREAM}"\nversion = "1.2.0"\n',
    )
    fs.seed_file(f"{proj}/harness", "wrapper antigo copiado")
    # Cópia local do core (código + "venv").
    fs.seed_file(f"{proj}/.harness/harness-core/src/main.py", "core copiado")
    fs.seed_file(f"{proj}/.harness/harness-core/.venv/bin/python3", "")
    # Estado por-projeto (deve ser preservado).
    fs.seed_file(f"{proj}/.harness/decisoes/MD-0001.md", "decisao do usuario")
    if with_git:
        fs.seed_dir(f"{proj}/.git")
    if foreign_pre_commit:
        fs.seed_file(f"{proj}/.git/hooks/pre-commit", "#!/bin/bash\necho meu-hook\n")


def test_migrate_installs_shim_and_removes_core():
    fs = _base_fs()
    _seed_installation(fs, "/dev/projA", foreign_pre_commit=True)
    # settings.json com um hook próprio do usuário no mesmo evento do harness.
    fs.seed_file(
        "/dev/projA/.claude/settings.json",
        json.dumps(
            {
                "hooks": {
                    "PostToolUse": [
                        {
                            "matcher": "Write",
                            "hooks": [{"type": "command", "command": "meu-linter.sh"}],
                        }
                    ]
                }
            }
        ),
    )

    results = MigrateService(fs).migrate("/dev", upstream_self=UPSTREAM)

    a = next(r for r in results if r["project"] == "/dev/projA")
    assert a["status"] == "migrated"
    # Shim instalado.
    assert "Shim do Harness" in fs.read_file("/dev/projA/harness")
    # Core copiado removido.
    assert not fs.exists("/dev/projA/.harness/harness-core/src/main.py")
    assert not fs.exists("/dev/projA/.harness/harness-core")
    # Estado preservado.
    assert (
        fs.read_file("/dev/projA/.harness/decisoes/MD-0001.md") == "decisao do usuario"
    )
    # version removido do toml.
    assert "version" not in fs.read_file("/dev/projA/harness.toml")
    assert "upstream_path" in fs.read_file("/dev/projA/harness.toml")
    # Hooks reescritos p/ shim, preservando o pre-commit alheio.
    pre = fs.read_file("/dev/projA/.git/hooks/pre-commit")
    assert "./harness format" in pre
    assert (
        fs.read_file("/dev/projA/.git/hooks/pre-commit.local")
        == "#!/bin/bash\necho meu-hook\n"
    )
    # settings mesclado por-item: o hook alheio no PostToolUse (evento não mais
    # gerenciado pelo harness) é preservado intacto, e os ganchos do harness
    # (SessionStart/Stop) são inseridos ao lado.
    settings = fs.read_file("/dev/projA/.claude/settings.json")
    assert "meu-linter.sh" in settings
    assert "harness cmd resume" in settings


def test_migrate_never_touches_the_upstream():
    fs = _base_fs()
    _seed_installation(fs, "/dev/projA")

    results = MigrateService(fs).migrate("/dev", upstream_self=UPSTREAM)

    # O core do upstream permanece intacto.
    assert fs.exists(UP_MAIN)
    up = next(r for r in results if r["project"] == "/dev/harness")
    assert up["status"] == "skipped"


def test_migrate_dry_run_writes_nothing():
    fs = _base_fs()
    _seed_installation(fs, "/dev/projA")
    before_harness = fs.read_file("/dev/projA/harness")

    results = MigrateService(fs).migrate("/dev", dry_run=True, upstream_self=UPSTREAM)

    a = next(r for r in results if r["project"] == "/dev/projA")
    assert a["status"] == "would-migrate"
    assert "/dev/projA/.harness/harness-core" in a["removes"]
    # Nada foi escrito nem removido.
    assert fs.read_file("/dev/projA/harness") == before_harness
    assert fs.exists("/dev/projA/.harness/harness-core/src/main.py")
    assert "version" in fs.read_file("/dev/projA/harness.toml")


def test_migrate_is_idempotent():
    fs = _base_fs()
    _seed_installation(fs, "/dev/projA")

    MigrateService(fs).migrate("/dev", upstream_self=UPSTREAM)
    # 2ª passada não deve levantar nem reintroduzir o core.
    results = MigrateService(fs).migrate("/dev", upstream_self=UPSTREAM)

    assert not fs.exists("/dev/projA/.harness/harness-core")
    a = next(r for r in results if r["project"] == "/dev/projA")
    assert a["status"] == "migrated"


def test_migrate_livro_mfc_dual_layout():
    fs = _base_fs()
    proj = "/dev/livro-mfc"
    _seed_installation(fs, proj)
    # Layout legado adicional na raiz do projeto (pré-011).
    fs.seed_file(f"{proj}/harness-core/src/main.py", "core legado na raiz")

    MigrateService(fs).migrate("/dev", upstream_self=UPSTREAM)

    assert not fs.exists(f"{proj}/.harness/harness-core")
    assert not fs.exists(f"{proj}/harness-core")


def test_migrate_skips_when_upstream_core_absent():
    fs = _base_fs()
    fs.seed_file(
        "/dev/projC/harness.toml",
        '[harness]\nactive_harness = "claude"\nupstream_path = "/dev/nao-existe"\n',
    )
    fs.seed_file("/dev/projC/.harness/harness-core/src/main.py", "core")

    results = MigrateService(fs).migrate("/dev", upstream_self=UPSTREAM)

    c = next(r for r in results if r["project"] == "/dev/projC")
    assert c["status"] == "skipped"
    # Não removeu nada (upstream inválido).
    assert fs.exists("/dev/projC/.harness/harness-core/src/main.py")
