from abc import ABC, abstractmethod


class GitPort(ABC):
    @abstractmethod
    def get_head_commit(self, repo_path: str) -> str:
        """Retorna o commit hash do HEAD local."""
        pass

    @abstractmethod
    def get_remote_commit(
        self, repo_path: str, remote_name: str = "origin", branch_name: str = "main"
    ) -> str:
        """Retorna o commit hash da branch remota utilizando ls-remote."""
        pass

    @abstractmethod
    def init_repo(self, repo_path: str) -> None:
        """Inicializa um repositório git vazio em repo_path (git init)."""
        pass

    @abstractmethod
    def commit_paths(self, repo_path: str, paths: list[str], message: str) -> str:
        """Cria um commit contendo APENAS os caminhos informados.

        Faz ``git add`` somente de ``paths`` (nunca ``git add -A``) e
        ``git commit``, devolvendo o hash do novo HEAD. Não arrasta outras
        mudanças pendentes do working tree.
        """
        pass
