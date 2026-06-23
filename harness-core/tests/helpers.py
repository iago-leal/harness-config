import os
from src.core.ports.fs import FileSystemPort

class MockFileSystem(FileSystemPort):
    def __init__(self, existing_files=None):
        self.existing_files = existing_files or set()
        self.written_files = {}

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
