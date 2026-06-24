import os
from typing import List
from src.core.ports.fs import FileSystemPort


class NotAGitRepositoryError(Exception):
    """Levantada quando `install_hooks` é chamado fora de um repositório git.

    Os hooks vivem em `.git/hooks`; sem um `.git` legítimo, instalá-los apenas
    criaria um diretório degenerado. A oferta de inicializar o repositório
    (`git init`) cabe à camada de apresentação, não ao domínio.
    """

    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        super().__init__(
            f"O diretório '{repo_path}' não é um repositório git "
            "(falta a subpasta .git)."
        )


class BootstrapService:
    def __init__(self, fs: FileSystemPort):
        self.fs = fs

    def install_hooks(self, repo_path: str) -> List[str]:
        """
        Instala os hooks Git locais (pre-commit e post-merge) apontando
        diretamente para a CLI Python do harness-core. Operação idempotente:
        reescreve os arquivos a cada execução.

        Recusa-se a operar fora de um repositório git (`NotAGitRepositoryError`)
        para não criar um `.git/hooks` órfão.
        """
        if not self.fs.exists(os.path.join(repo_path, ".git")):
            raise NotAGitRepositoryError(repo_path)

        hooks_dir = os.path.join(repo_path, ".git", "hooks")
        self.fs.makedirs(hooks_dir)

        installed_paths = []

        pre_commit_path = os.path.join(hooks_dir, "pre-commit")
        self.fs.write_file(pre_commit_path, self._pre_commit_script())
        installed_paths.append(pre_commit_path)

        post_merge_path = os.path.join(hooks_dir, "post-merge")
        self.fs.write_file(post_merge_path, self._post_merge_script())
        installed_paths.append(post_merge_path)

        return installed_paths

    @staticmethod
    def _pre_commit_script() -> str:
        return (
            "#!/bin/bash\n"
            "# Hook pre-commit — Harness Core\n"
            'PYTHON_CLI="harness-core/src/main.py"\n'
            'PYTHON_BIN="harness-core/.venv/bin/python3"\n'
            'if [ -f "$PYTHON_CLI" ]; then\n'
            '    "$PYTHON_BIN" "$PYTHON_CLI" format "$@"\n'
            "    exit $?\n"
            "fi\n"
            "exit 0\n"
        )

    @staticmethod
    def _post_merge_script() -> str:
        return (
            "#!/bin/bash\n"
            "# Hook post-merge — Harness Core\n"
            'PYTHON_CLI="harness-core/src/main.py"\n'
            'PYTHON_BIN="harness-core/.venv/bin/python3"\n'
            'if [ -f "$PYTHON_CLI" ]; then\n'
            '    "$PYTHON_BIN" "$PYTHON_CLI" decisions\n'
            "    exit $?\n"
            "fi\n"
            "exit 0\n"
        )
