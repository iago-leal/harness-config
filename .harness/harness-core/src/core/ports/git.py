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

    # --- Capacidades de fim de sessão (feature 014) -----------------------
    # Verbos usados pela detecção das ofertas (push/upgrade) e pela
    # sincronização não-destrutiva do upstream. O domínio só fala com git por
    # aqui (RN-N5); as consultas são chamadas pela borda sob try/except, então
    # devem sinalizar ausência por valor (0/None/False) quando isso é estado
    # normal, e levantar RuntimeError apenas em falha real de execução.

    @abstractmethod
    def fetch(
        self, repo_path: str, remote: str = "origin", branch: str | None = None
    ) -> None:
        """Atualiza as refs remotas (``git fetch <remote> [<branch>]``)."""
        pass

    @abstractmethod
    def get_current_branch(self, repo_path: str) -> str:
        """Nome do branch corrente (``git rev-parse --abbrev-ref HEAD``)."""
        pass

    @abstractmethod
    def get_default_branch(self, repo_path: str, remote: str = "origin") -> str:
        """Nome do branch principal do remoto.

        Resolve ``refs/remotes/<remote>/HEAD`` por ``symbolic-ref``; em sua
        ausência, recai sobre ``main``/``master`` por existência de ref. Nunca
        levanta: devolve o melhor palpite.
        """
        pass

    @abstractmethod
    def count_commits_ahead(self, repo_path: str, rev: str = "@{u}..HEAD") -> int:
        """Quantos commits o HEAD está à frente do upstream de rastreamento.

        Devolve ``0`` (não levanta) quando não há upstream tracking — sinal de
        que não há push a oferecer (RN-11).
        """
        pass

    @abstractmethod
    def get_file_at_ref(self, repo_path: str, ref: str, rel_path: str) -> str | None:
        """Conteúdo de ``rel_path`` na ref dada (``git show <ref>:<rel_path>``).

        Read-only: não toca o working tree. Devolve ``None`` quando o arquivo
        não existe naquela ref.
        """
        pass

    @abstractmethod
    def is_working_tree_clean(self, repo_path: str) -> bool:
        """``True`` se ``git status --porcelain`` é vazio (sem pendências)."""
        pass

    @abstractmethod
    def list_dirty_paths(self, repo_path: str) -> list[str]:
        """Caminhos sujos da working tree (``git status --porcelain``).

        Inclui modificados, adicionados, deletados, renomeados e não rastreados,
        relativos à raiz do repositório. Árvore limpa → lista vazia. A consulta é
        read-only; falha real de execução levanta ``RuntimeError`` (RN-N4).
        """
        pass

    @abstractmethod
    def list_changed_paths_since(self, repo_path: str, ref: str) -> list[str]:
        """Caminhos alterados entre ``ref`` e o HEAD (``git diff --name-only <ref> HEAD``).

        Enxerga o trabalho já COMMITADO na sessão (o diff da âncora), complemento
        de ``list_dirty_paths`` (trabalho ainda não commitado) — feature 022.
        Read-only; ref inválida ou falha real de execução levanta ``RuntimeError``
        (RN-N4), cabendo à borda tratar como ausência de baseline.
        """
        pass

    @abstractmethod
    def merge_ff_only(self, repo_path: str, ref: str) -> bool:
        """Avança o branch corrente até ``ref`` apenas por fast-forward.

        Devolve ``True`` quando o fast-forward é aplicado; ``False`` quando não
        é possível (working tree sujo ou divergência), sem sobrescrever nada.
        """
        pass

    @abstractmethod
    def push(
        self, repo_path: str, remote: str | None = None, branch: str | None = None
    ) -> None:
        """Publica os commits do branch corrente (``git push``).

        Respeita o rastreamento configurado e **nunca** usa ``--force``.
        """
        pass
