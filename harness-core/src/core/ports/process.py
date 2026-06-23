from abc import ABC, abstractmethod
from typing import Optional, Tuple

class ProcessPort(ABC):
    @abstractmethod
    def execute_formatter(
        self, 
        formatter_name: str, 
        file_path: str, 
        executable_path: Optional[str] = None
    ) -> Tuple[int, str, str]:
        """
        Executa um formatador (ruff, prettier, rustfmt) em um arquivo específico.
        Retorna (exit_code, stdout, stderr).
        """
        pass
