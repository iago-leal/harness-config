from abc import ABC, abstractmethod
from typing import List


class FileSystemPort(ABC):
    @abstractmethod
    def read_file(self, path: str) -> str:
        pass

    @abstractmethod
    def write_file(self, path: str, content: str) -> None:
        pass

    @abstractmethod
    def write_file_atomic(self, path: str, content: str) -> None:
        pass

    @abstractmethod
    def exists(self, path: str) -> bool:
        pass

    @abstractmethod
    def list_dir(self, path: str) -> List[str]:
        pass

    @abstractmethod
    def makedirs(self, path: str) -> None:
        pass

    @abstractmethod
    def remove(self, path: str) -> None:
        pass

    @abstractmethod
    def remove_tree(self, path: str) -> None:
        """Remove um diretório e todo o seu conteúdo, recursivamente.

        Usado pela migração (feature 020) para apagar a cópia vendored do core
        (`.harness/harness-core/`). A validação do alvo cabe ao chamador.
        """
        pass

    @abstractmethod
    def is_dir(self, path: str) -> bool:
        pass

    @abstractmethod
    def make_executable(self, path: str) -> None:
        pass
