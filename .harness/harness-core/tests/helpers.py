import os
from src.core.ports.fs import FileSystemPort


class MockFileSystem(FileSystemPort):
    def __init__(self, existing_files=None):
        self.existing_files = existing_files or set()
        self.written_files = {}
        self.executable_files = set()

    def read_file(self, path: str) -> str:
        if path in self.written_files:
            return self.written_files[path]
        return ""

    def write_file(self, path: str, content: str) -> None:
        self.written_files[path] = content

    def write_file_atomic(self, path: str, content: str) -> None:
        self.write_file(path, content)

    def exists(self, path: str) -> bool:
        return path in self.existing_files or path in self.written_files

    def list_dir(self, path: str) -> list[str]:
        return []

    def makedirs(self, path: str) -> None:
        pass

    def remove(self, path: str) -> None:
        if path in self.existing_files:
            self.existing_files.remove(path)
        if path in self.written_files:
            del self.written_files[path]

    def is_dir(self, path: str) -> bool:
        for f in self.written_files:
            if f.startswith(path + "/"):
                return True
        return False

    def make_executable(self, path: str) -> None:
        self.executable_files.add(path)


class FootprintViolation(AssertionError):
    """Levantada pelo RecordingFileSystem quando uma escrita do harness
    mira fora do repositório ou sob um diretório global protegido."""


class RecordingFileSystem(FileSystemPort):
    """Spy de FileSystemPort para o contrato de footprint global zero (feature 006).

    Captura toda escrita (write_file, write_file_atomic, makedirs, remove) e
    falha de forma BARULHENTA (FootprintViolation) se o caminho resolver para
    fora da raiz do repositório ou sob ~/.claude / ~/.agent-memory.
    """

    def __init__(self, repo_root=None, existing_files=None):
        self.repo_root = os.path.abspath(repo_root or os.getcwd())
        self.existing_files = set(existing_files or set())
        self.written_files = {}
        self.executable_files = set()
        self.writes = []  # caminhos de escrita aceitos (auditoria do teste)
        home = os.path.expanduser("~")
        self._forbidden = (
            os.path.join(home, ".claude"),
            os.path.join(home, ".agent-memory"),
        )

    def _guard(self, path: str) -> str:
        abs_path = os.path.abspath(os.path.join(self.repo_root, path))
        for bad in self._forbidden:
            if abs_path == bad or abs_path.startswith(bad + os.sep):
                raise FootprintViolation(
                    f"Escrita global proibida: {path} -> {abs_path}"
                )
        if not (
            abs_path == self.repo_root or abs_path.startswith(self.repo_root + os.sep)
        ):
            raise FootprintViolation(
                f"Escrita fora do repositório: {path} -> {abs_path}"
            )
        return abs_path

    def read_file(self, path: str) -> str:
        return self.written_files.get(path, "")

    def write_file(self, path: str, content: str) -> None:
        self._guard(path)
        self.writes.append(path)
        self.written_files[path] = content

    def write_file_atomic(self, path: str, content: str) -> None:
        self.write_file(path, content)

    def exists(self, path: str) -> bool:
        return path in self.existing_files or path in self.written_files

    def list_dir(self, path: str) -> list[str]:
        return []

    def makedirs(self, path: str) -> None:
        self._guard(path)
        self.writes.append(path)

    def remove(self, path: str) -> None:
        self._guard(path)
        self.existing_files.discard(path)
        self.written_files.pop(path, None)

    def is_dir(self, path: str) -> bool:
        for f in self.written_files:
            if f.startswith(path + "/"):
                return True
        return False

    def make_executable(self, path: str) -> None:
        self._guard(path)
        self.executable_files.add(path)
