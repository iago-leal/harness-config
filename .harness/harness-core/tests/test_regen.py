"""RegenService — execução do comando de regen declarado (feature 016)."""

from typing import List, Optional, Tuple

from src.core.ports.process import ProcessPort
from src.core.domain.config import HarnessConfig
from src.core.regen.service import RegenService


class FakeProcess(ProcessPort):
    """ProcessPort fake que registra a chamada e devolve um resultado fixo."""

    def __init__(self, result: Tuple[int, str, str] = (0, "ok", "")):
        self.result = result
        self.calls: List[Tuple[List[str], Optional[str]]] = []

    def execute_formatter(self, formatter_name, file_path, executable_path=None):
        return (0, "", "")

    def run_command(self, args: List[str], cwd: Optional[str] = None):
        self.calls.append((list(args), cwd))
        return self.result


def _config(command):
    cfg = HarnessConfig()
    cfg.regen.command = command
    return cfg


def test_regen_absent_command_is_noop():
    proc = FakeProcess()
    service = RegenService(proc)
    code, _msg = service.run(_config(None), "/repo")
    assert code == 0
    assert proc.calls == []  # não executou nada


def test_regen_runs_via_shell_with_cwd():
    proc = FakeProcess((0, "site gerado", ""))
    service = RegenService(proc)
    code, msg = service.run(
        _config("python gerar_site.py && python empacotar.py"), "/repo"
    )
    assert code == 0
    assert len(proc.calls) == 1
    args, cwd = proc.calls[0]
    assert args == ["sh", "-c", "python gerar_site.py && python empacotar.py"]
    assert cwd == "/repo"
    assert "site gerado" in msg


def test_regen_failure_is_loud():
    proc = FakeProcess((3, "", "boom"))
    service = RegenService(proc)
    code, msg = service.run(_config("exit 3"), "/repo")
    assert code != 0
    assert "boom" in msg or "3" in msg
