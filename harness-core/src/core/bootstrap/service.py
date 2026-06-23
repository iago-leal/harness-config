import os
from typing import List
from src.core.ports.fs import FileSystemPort

class BootstrapService:
    def __init__(self, fs: FileSystemPort):
        self.fs = fs

    def install_hooks(self, repo_path: str, shadow_mode: bool = True) -> List[str]:
        """
        Instala os hooks de pre-commit e post-merge locais na pasta .git/hooks.
        Se shadow_mode for True, configura a execução paralela (coexistência).
        """
        hooks_dir = os.path.join(repo_path, ".git", "hooks")
        self.fs.makedirs(hooks_dir)

        installed_paths = []
        
        # 1. Pre-commit Hook
        pre_commit_path = os.path.join(hooks_dir, "pre-commit")
        if shadow_mode:
            # Roda format-on-edit.sh legado e despacha Python format-shadow em background
            content = (
                "#!/bin/bash\n"
                "# Hook pre-commit em modo Parallel Run (Shadow)\n"
                "LEGADO_HOOK=\"harness-config/hooks/format-on-edit.sh\"\n"
                "if [ -f \"$LEGADO_HOOK\" ]; then\n"
                "    # Executa legado e captura exit code\n"
                "    $LEGADO_HOOK \"$@\"\n"
                "    EXIT_CODE=$?\n"
                "else\n"
                "    EXIT_CODE=0\n"
                "fi\n\n"
                "# Executa novo Python em shadow background\n"
                "mkdir -p .reversa/logs\n"
                "PYTHON_CLI=\"harness-core/src/main.py\"\n"
                "PYTHON_BIN=\"harness-core/.venv/bin/python3\"\n"
                "if [ -f \"$PYTHON_CLI\" ]; then\n"
                "    $PYTHON_BIN $PYTHON_CLI format --shadow \"$@\" >> .reversa/logs/shadow-validation.log 2>&1 &\n"
                "fi\n\n"
                "exit $EXIT_CODE\n"
            )
        else:
            # Corte definitivo: executa diretamente o novo compilador Python
            content = (
                "#!/bin/bash\n"
                "# Hook pre-commit ativo\n"
                "PYTHON_CLI=\"harness-core/src/main.py\"\n"
                "PYTHON_BIN=\"harness-core/.venv/bin/python3\"\n"
                "if [ -f \"$PYTHON_CLI\" ]; then\n"
                "    $PYTHON_BIN $PYTHON_CLI format \"$@\"\n"
                "    exit $?\n"
                "fi\n"
                "exit 0\n"
            )
        self.fs.write_file(pre_commit_path, content)
        installed_paths.append(pre_commit_path)

        # 2. Post-merge Hook (Sincronização e Compilação de Decisões)
        post_merge_path = os.path.join(hooks_dir, "post-merge")
        if shadow_mode:
            # Roda indexador legado e despacha Python compile-shadow em background
            content = (
                "#!/bin/bash\n"
                "# Hook post-merge em modo Parallel Run (Shadow)\n"
                "LEGADO_HOOK=\"harness-config/bin/gerar-index-decisoes.sh\"\n"
                "if [ -f \"$LEGADO_HOOK\" ]; then\n"
                "    $LEGADO_HOOK \"$@\"\n"
                "    EXIT_CODE=$?\n"
                "else\n"
                "    EXIT_CODE=0\n"
                "fi\n\n"
                "# Executa novo compilador em shadow background\n"
                "mkdir -p .reversa/logs\n"
                "PYTHON_CLI=\"harness-core/src/main.py\"\n"
                "PYTHON_BIN=\"harness-core/.venv/bin/python3\"\n"
                "if [ -f \"$PYTHON_CLI\" ]; then\n"
                "    $PYTHON_BIN $PYTHON_CLI decisions --shadow \"$@\" >> .reversa/logs/shadow-validation.log 2>&1 &\n"
                "fi\n\n"
                "exit $EXIT_CODE\n"
            )
        else:
            # Corte definitivo: executa diretamente o novo indexador Python
            content = (
                "#!/bin/bash\n"
                "# Hook post-merge ativo\n"
                "PYTHON_CLI=\"harness-core/src/main.py\"\n"
                "PYTHON_BIN=\"harness-core/.venv/bin/python3\"\n"
                "if [ -f \"$PYTHON_CLI\" ]; then\n"
                "    $PYTHON_BIN $PYTHON_CLI decisions \"$@\"\n"
                "    exit $?\n"
                "fi\n"
                "exit 0\n"
            )
        self.fs.write_file(post_merge_path, content)
        installed_paths.append(post_merge_path)

        return installed_paths
