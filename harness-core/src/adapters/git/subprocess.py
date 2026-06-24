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
