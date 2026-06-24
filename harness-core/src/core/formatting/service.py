import os
import fnmatch
from typing import Optional
from src.core.ports.fs import FileSystemPort
from src.core.ports.process import ProcessPort
from src.core.domain.config import HarnessConfig

class FormattingService:
    def __init__(self, fs: FileSystemPort, process: ProcessPort, config: Optional[HarnessConfig] = None):
        self.fs = fs
        self.process = process
        self.config = config or HarnessConfig()

    def format_file(self, file_path: str) -> int:
        """
        Formata o arquivo utilizando o formatador adequado e respeitando as regras de segurança e precedência.
        Retorna sempre 0 (não bloqueia).
        """
        try:
            abs_path = os.path.abspath(file_path)
            
            # 1. Blindagem de diretórios pessoais (BR-MIGRAR-007)
            home = os.path.expanduser("~")
            if abs_path == home:
                return 0
                
            notas_path = os.path.join(home, "Notas")
            claude_path = os.path.join(home, ".claude")
            
            if abs_path.startswith(notas_path) or abs_path.startswith(claude_path):
                return 0

            # 2. Encontrar raiz do projeto e verificar Opt-out (BR-MIGRAR-009)
            project_root = None
            current = os.path.dirname(abs_path)
            
            opt_out_filename = self.config.formatting.opt_out_file or ".no-autoformat"
            
            while True:
                # Checa opt-out neste nível
                opt_out_file = os.path.join(current, opt_out_filename)
                if self.fs.exists(opt_out_file):
                    return 0 # Opt-out ativo, cancela formatação com sucesso
                
                # Checa se é a raiz do projeto (presença de .git ou harness.toml)
                if self.fs.exists(os.path.join(current, ".git")) or self.fs.exists(os.path.join(current, "harness.toml")):
                    project_root = current
                
                parent = os.path.dirname(current)
                if parent == current:
                    break
                current = parent

            if not project_root:
                project_root = os.getcwd()

            # 2.5. Verificar Exclusão Dinâmica por caminhos e glob patterns
            rel_path = os.path.relpath(abs_path, project_root)
            for pattern in self.config.formatting.exclude_paths:
                pattern = pattern.strip()
                if not pattern:
                    continue
                # Se o padrão contiver curingas, usamos fnmatch
                if any(c in pattern for c in ("*", "?", "[", "]")):
                    if fnmatch.fnmatch(rel_path, pattern) or fnmatch.fnmatch(os.path.basename(abs_path), pattern):
                        return 0
                else:
                    # Checagem de prefixo (diretório) ou correspondência exata
                    if rel_path.startswith(pattern) or rel_path == pattern:
                        return 0

            # 3. Determinar formatador por extensão
            _, ext = os.path.splitext(abs_path)
            ext = ext.lower()
            
            formatter_name = None
            if ext == ".py":
                formatter_name = "ruff"
            elif ext in {".js", ".ts", ".json", ".css", ".md"}:
                formatter_name = "prettier"
            elif ext == ".rs":
                formatter_name = "rustfmt"
                
            if not formatter_name:
                return 0 # Nenhuma extensão suportada para formatação

            # 4. Precedência de executáveis locais (BR-MIGRAR-008)
            local_path = None
            if formatter_name == "ruff":
                # Tenta .venv/bin/ruff ou venv/bin/ruff
                venv_ruff = os.path.join(project_root, ".venv", "bin", "ruff")
                venv_ruff_alt = os.path.join(project_root, "venv", "bin", "ruff")
                if self.fs.exists(venv_ruff):
                    local_path = venv_ruff
                elif self.fs.exists(venv_ruff_alt):
                    local_path = venv_ruff_alt
            elif formatter_name == "prettier":
                node_prettier = os.path.join(project_root, "node_modules", ".bin", "prettier")
                if self.fs.exists(node_prettier):
                    local_path = node_prettier

            # 5. Executar formatação via ProcessPort
            # Retorna sempre 0 independente do resultado do formatador (BR-MIGRAR-006)
            self.process.execute_formatter(
                formatter_name=formatter_name,
                file_path=abs_path,
                executable_path=local_path
            )
            return 0
            
        except Exception:
            # Blindagem absoluta de erros (BR-MIGRAR-006)
            return 0
