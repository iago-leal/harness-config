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
