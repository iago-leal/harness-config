import subprocess
from typing import List, Optional, Tuple
from src.core.ports.process import ProcessPort

class HostFormatterAdapter(ProcessPort):
    def execute_formatter(
        self, 
        formatter_name: str, 
        file_path: str, 
        executable_path: Optional[str] = None
    ) -> Tuple[int, str, str]:
        executable = executable_path or formatter_name
        
        # Determina os argumentos com base no formatador
        if formatter_name.lower() == "ruff":
            args = [executable, "format", file_path]
        elif formatter_name.lower() == "prettier":
            args = [executable, "--write", file_path]
        elif formatter_name.lower() == "rustfmt":
            args = [executable, file_path]
        else:
            # Fallback genérico para outros formatadores
            args = [executable, file_path]
            
        try:
            result = subprocess.run(
                args,
                capture_output=True,
                text=True
            )
            return result.returncode, result.stdout, result.stderr
        except FileNotFoundError as e:
            return 127, "", f"Formatador '{executable}' não encontrado no host: {e}"
        except Exception as e:
            return -1, "", f"Erro inesperado ao executar formatador: {str(e)}"

    def run_command(self, args: List[str], cwd: Optional[str] = None) -> Tuple[int, str, str]:
        try:
            result = subprocess.run(
                args,
                capture_output=True,
                text=True,
                cwd=cwd
            )
            return result.returncode, result.stdout, result.stderr
        except FileNotFoundError as e:
            return 127, "", f"Comando '{args[0]}' não encontrado: {e}"
        except Exception as e:
            return -1, "", f"Erro inesperado ao executar comando: {str(e)}"

