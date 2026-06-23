from abc import ABC, abstractmethod

class GitPort(ABC):
    @abstractmethod
    def get_head_commit(self, repo_path: str) -> str:
        """Retorna o commit hash do HEAD local."""
        pass

    @abstractmethod
    def get_remote_commit(self, repo_path: str, remote_name: str = "origin", branch_name: str = "main") -> str:
        """Retorna o commit hash da branch remota utilizando ls-remote."""
        pass
