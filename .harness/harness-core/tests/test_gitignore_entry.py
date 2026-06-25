"""Feature 011: escrita idempotente da entrada do core no .gitignore do alvo.

`_ensure_gitignore_entry` é a rotina que registra `.harness/harness-core/` no
.gitignore do projeto-alvo, tornando a cópia vendored um artefato regenerável
sem poluir o histórico do projeto.
"""

from src.core.bootstrap.init_service import InitializationService

ENTRY = ".harness/harness-core/"


class _DictFileSystem:
    """FileSystem mínimo em memória para exercitar a rotina."""

    def __init__(self):
        self.files = {}

    def exists(self, path: str) -> bool:
        return path in self.files

    def read_file(self, path: str) -> str:
        return self.files.get(path, "")

    def write_file(self, path: str, content: str) -> None:
        self.files[path] = content

    def write_file_atomic(self, path: str, content: str) -> None:
        self.files[path] = content


def _service(fs):
    # `_ensure_gitignore_entry` só toca self.fs; o ProcessPort é dispensável.
    return InitializationService(fs, None)


def test_creates_gitignore_with_entry_when_absent():
    fs = _DictFileSystem()
    _service(fs)._ensure_gitignore_entry("/proj", ENTRY)
    content = fs.files["/proj/.gitignore"]
    assert ENTRY in content
    assert content.endswith("\n")


def test_idempotent_does_not_duplicate_on_reexecution():
    fs = _DictFileSystem()
    svc = _service(fs)
    svc._ensure_gitignore_entry("/proj", ENTRY)
    svc._ensure_gitignore_entry("/proj", ENTRY)
    content = fs.files["/proj/.gitignore"]
    assert content.count(ENTRY) == 1


def test_preserves_existing_content():
    fs = _DictFileSystem()
    fs.files["/proj/.gitignore"] = "node_modules/\n.venv/\n"
    _service(fs)._ensure_gitignore_entry("/proj", ENTRY)
    content = fs.files["/proj/.gitignore"]
    assert "node_modules/" in content
    assert ".venv/" in content
    assert ENTRY in content


def test_handles_missing_trailing_newline():
    fs = _DictFileSystem()
    fs.files["/proj/.gitignore"] = "*.log"  # sem newline final
    _service(fs)._ensure_gitignore_entry("/proj", ENTRY)
    content = fs.files["/proj/.gitignore"]
    assert "*.log\n" in content
    assert content.count(ENTRY) == 1
