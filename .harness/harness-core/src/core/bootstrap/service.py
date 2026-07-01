import os
from typing import List
from src.core.ports.fs import FileSystemPort

# Assinatura estável que marca um hook como sendo do harness (linha de comentário
# presente nos scripts gerados). Um hook próprio do projeto não a contém.
HARNESS_HOOK_SIGNATURE = "Harness Core"


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
        """Instala os hooks Git locais (pre-commit e post-merge) de forma
        NÃO-DESTRUTIVA (feature 020, RN-07), apontando para o shim `./harness`.

        Recusa-se a operar fora de um repositório git (`NotAGitRepositoryError`)
        para não criar um `.git/hooks` órfão. Só os dois hooks nomeados são
        gerenciados; hooks de outro nome nunca são lidos nem tocados.
        """
        if not self.fs.exists(os.path.join(repo_path, ".git")):
            raise NotAGitRepositoryError(repo_path)

        hooks_dir = os.path.join(repo_path, ".git", "hooks")
        self.fs.makedirs(hooks_dir)

        return [
            self._install_one_hook(hooks_dir, "pre-commit", self._pre_commit_script()),
            self._install_one_hook(hooks_dir, "post-merge", self._post_merge_script()),
        ]

    def _install_one_hook(self, hooks_dir: str, name: str, script: str) -> str:
        """Instala um hook preservando um hook alheio preexistente (RN-07).

        - Ausente → cria o hook do harness.
        - Presente COM a assinatura `Harness Core` → atualiza no lugar (é o hook
          do harness antigo); não gera `.local`.
        - Presente SEM a assinatura (hook próprio do projeto) → preserva o
          conteúdo em `<hook>.local` (se ainda não existir) e grava o hook do
          harness, que encadeia o `.local` em runtime. Nunca descarta o hook do
          projeto.
        """
        hook_path = os.path.join(hooks_dir, name)
        local_path = hook_path + ".local"
        if self.fs.exists(hook_path):
            existing = self.fs.read_file(hook_path)
            if HARNESS_HOOK_SIGNATURE not in existing and not self.fs.exists(
                local_path
            ):
                # Hook alheio: preserva-o para ser encadeado pelo hook do harness.
                self.fs.write_file(local_path, existing)
                self.fs.make_executable(local_path)
        self.fs.write_file(hook_path, script)
        self.fs.make_executable(hook_path)
        return hook_path

    @staticmethod
    def _pre_commit_script() -> str:
        return (
            "#!/bin/bash\n"
            "# Hook pre-commit — Harness Core\n"
            'HOOK_DIR="$(dirname "$0")"\n'
            # Encadeia um pre-commit próprio do projeto preservado (RN-07). Se ele
            # falhar, aborta o commit propagando o código de saída.
            'if [ -x "$HOOK_DIR/pre-commit.local" ]; then\n'
            '    "$HOOK_DIR/pre-commit.local" "$@" || exit $?\n'
            "fi\n"
            # Via shim `./harness` (fonte única, feature 020). Shim ausente →
            # não bloqueia o commit (não-bloqueante, RN-N15 preservada).
            "if [ -x ./harness ]; then\n"
            '    ./harness format "$@"\n'
            "    exit $?\n"
            "fi\n"
            "exit 0\n"
        )

    @staticmethod
    def _post_merge_script() -> str:
        return (
            "#!/bin/bash\n"
            "# Hook post-merge — Harness Core\n"
            'HOOK_DIR="$(dirname "$0")"\n'
            'if [ -x "$HOOK_DIR/post-merge.local" ]; then\n'
            '    "$HOOK_DIR/post-merge.local" "$@"\n'
            "fi\n"
            # `decisions` não aceita posicional: nunca repassar "$@" a ele.
            "if [ -x ./harness ]; then\n"
            "    ./harness decisions\n"
            "    exit $?\n"
            "fi\n"
            "exit 0\n"
        )
