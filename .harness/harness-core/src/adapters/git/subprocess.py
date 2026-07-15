import subprocess
from src.core.ports.git import GitPort


class SubprocessGitAdapter(GitPort):
    def get_head_commit(self, repo_path: str) -> str:
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            raise RuntimeError(
                f"Falha ao executar git rev-parse HEAD: {e.stderr.strip()}"
            )

    def get_remote_commit(
        self, repo_path: str, remote_name: str = "origin", branch_name: str = "main"
    ) -> str:
        try:
            # Comando git ls-remote origin main
            result = subprocess.run(
                ["git", "ls-remote", remote_name, branch_name],
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True,
            )
            output = result.stdout.strip()
            if not output:
                raise RuntimeError(
                    f"Nenhum commit encontrado para o remote {remote_name}/{branch_name}"
                )
            # Retorna apenas o hash (primeiro token)
            return output.split()[0]
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Falha ao executar git ls-remote: {e.stderr.strip()}")

    def init_repo(self, repo_path: str) -> None:
        try:
            subprocess.run(
                ["git", "init"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True,
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Falha ao executar git init: {e.stderr.strip()}")

    def commit_paths(self, repo_path: str, paths: list[str], message: str) -> str:
        # `git add -- <paths>`: o `--` separa opções de caminhos e restringe o
        # stage EXCLUSIVAMENTE aos caminhos dados — nunca `git add -A`, para não
        # arrastar mudanças alheias do working tree.
        try:
            subprocess.run(
                ["git", "add", "--", *paths],
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True,
            )
            subprocess.run(
                ["git", "commit", "-m", message],
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True,
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Falha ao criar commit de caminhos: {e.stderr.strip()}")
        return self.get_head_commit(repo_path)

    # --- Capacidades de fim de sessão (feature 014) -----------------------

    def fetch(
        self, repo_path: str, remote: str = "origin", branch: str | None = None
    ) -> None:
        args = ["git", "fetch", remote]
        if branch:
            args.append(branch)
        try:
            subprocess.run(
                args, cwd=repo_path, capture_output=True, text=True, check=True
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Falha ao executar git fetch: {e.stderr.strip()}")

    def get_current_branch(self, repo_path: str) -> str:
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            raise RuntimeError(
                f"Falha ao resolver o branch corrente: {e.stderr.strip()}"
            )

    def get_default_branch(self, repo_path: str, remote: str = "origin") -> str:
        # Preferência: o HEAD simbólico do remoto (default real do servidor).
        try:
            result = subprocess.run(
                ["git", "symbolic-ref", "--short", f"refs/remotes/{remote}/HEAD"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True,
            )
            ref = result.stdout.strip()  # ex.: "origin/main"
            if ref:
                return ref.split("/", 1)[1] if "/" in ref else ref
        except subprocess.CalledProcessError:
            pass
        # Fallback: a primeira de main/master cuja ref exista; senão "main".
        for candidate in ("main", "master"):
            existe = subprocess.run(
                ["git", "rev-parse", "--verify", "--quiet", candidate],
                cwd=repo_path,
                capture_output=True,
                text=True,
            )
            if existe.returncode == 0:
                return candidate
        return "main"

    def count_commits_ahead(self, repo_path: str, rev: str = "@{u}..HEAD") -> int:
        # Sem upstream tracking, `@{u}` é indefinido: devolve 0 (não há push a
        # oferecer) em vez de levantar — é estado normal, não falha (RN-11).
        result = subprocess.run(
            ["git", "rev-list", "--count", rev],
            cwd=repo_path,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            return 0
        try:
            return int(result.stdout.strip())
        except ValueError:
            return 0

    def get_file_at_ref(self, repo_path: str, ref: str, rel_path: str) -> str | None:
        # Read-only; não toca o working tree. Ausência do arquivo na ref → None.
        result = subprocess.run(
            ["git", "show", f"{ref}:{rel_path}"],
            cwd=repo_path,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            return None
        return result.stdout

    def is_working_tree_clean(self, repo_path: str) -> bool:
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True,
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Falha ao ler git status: {e.stderr.strip()}")
        return result.stdout.strip() == ""

    def list_dirty_paths(self, repo_path: str) -> list[str]:
        try:
            # --untracked-files=all expande diretórios não rastreados em arquivos
            # individuais; sem isso o porcelain colapsa um subdiretório novo numa
            # única linha (ex.: ".harness/"), e a oferta de commit pendente (019)
            # não consegue separar o estado-da-sessao.md do restante de .harness/.
            result = subprocess.run(
                ["git", "status", "--porcelain", "--untracked-files=all"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True,
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Falha ao listar a working tree: {e.stderr.strip()}")
        paths = []
        for line in result.stdout.splitlines():
            if not line.strip():
                continue
            # Porcelain v1: 'XY <path>' ou 'XY <old> -> <new>' (rename/copy).
            rest = line[3:] if len(line) > 3 else line.strip()
            if " -> " in rest:
                rest = rest.split(" -> ", 1)[1]
            path = rest.strip().strip('"')
            if path:
                paths.append(path)
        return paths

    def list_changed_paths_since(self, repo_path: str, ref: str) -> list[str]:
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only", ref, "HEAD"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True,
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(
                f"Falha ao listar mudanças desde {ref}: {e.stderr.strip()}"
            )
        return [line.strip() for line in result.stdout.splitlines() if line.strip()]

    def merge_ff_only(self, repo_path: str, ref: str) -> bool:
        # Não-fast-forward (working tree sujo ou divergência) não é falha fatal:
        # devolve False sem sobrescrever nada, deixando a borda abortar o upgrade.
        result = subprocess.run(
            ["git", "merge", "--ff-only", ref],
            cwd=repo_path,
            capture_output=True,
            text=True,
        )
        return result.returncode == 0

    def push(
        self, repo_path: str, remote: str | None = None, branch: str | None = None
    ) -> None:
        # Sem `--force`, jamais. Sem remote/branch, respeita o rastreamento.
        args = ["git", "push"]
        if remote:
            args.append(remote)
            if branch:
                args.append(branch)
        try:
            subprocess.run(
                args, cwd=repo_path, capture_output=True, text=True, check=True
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Falha ao executar git push: {e.stderr.strip()}")
