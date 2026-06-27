from typing import Tuple

from src.core.ports.process import ProcessPort
from src.core.domain.config import HarnessConfig


class RegenService:
    """Dispara o comando de regeneração declarado em ``[regen]`` (feature 016).

    O core não conhece o que cada projeto deriva (RN-N5 / baixo acoplamento): só
    executa, pelo ``ProcessPort``, o comando de shell declarado no ``harness.toml``.
    Comando ausente → no-op (exit 0). Falha do comando → barulhenta (exit ≠ 0),
    para que o fluxo "faz tudo" aborte antes de fechar a sessão (D-07/D2).
    """

    def __init__(self, process: ProcessPort):
        self.process = process

    def run(self, config: HarnessConfig, repo_path: str) -> Tuple[int, str]:
        """Executa o regen. Devolve ``(exit_code, mensagem)`` para a borda mapear.

        O ``sh -c`` permite comandos compostos (``&&``, pipes) declarados pelo
        dono do projeto.
        """
        command = config.regen.command
        if not command:
            return 0, "Nenhum comando de regen configurado em [regen]; nada a fazer."

        code, out, err = self.process.run_command(["sh", "-c", command], cwd=repo_path)
        if code == 0:
            tail = (out or "").strip()
            return 0, "Regen concluído." + (f"\n{tail}" if tail else "")

        detail = (err or out or "").strip()
        return (code or 1), f"Regen falhou (exit {code})." + (
            f"\n{detail}" if detail else ""
        )
