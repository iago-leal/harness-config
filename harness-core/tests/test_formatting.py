import os
import pytest
from unittest.mock import MagicMock
from src.core.ports.fs import FileSystemPort
from src.core.ports.process import ProcessPort
from src.core.formatting.service import FormattingService
from tests.helpers import MockFileSystem

def test_formatting_service_blindagem():
    fs = MockFileSystem()
    process = MagicMock(spec=ProcessPort)
    service = FormattingService(fs, process)

    home = os.path.expanduser("~")
    
    # Arquivo em ~/Notas
    notas_file = os.path.join(home, "Notas", "notebook.md")
    assert service.format_file(notas_file) == 0
    process.execute_formatter.assert_not_called()

    # Arquivo em ~/.claude
    claude_file = os.path.join(home, ".claude", "logs", "session.log")
    assert service.format_file(claude_file) == 0
    process.execute_formatter.assert_not_called()

def test_formatting_service_opt_out(tmp_path):
    fs = MockFileSystem()
    process = MagicMock(spec=ProcessPort)
    service = FormattingService(fs, process)

    # Cria opt-out na raiz do projeto
    opt_out_file = os.path.join(str(tmp_path), ".no-autoformat")
    fs.existing_files.add(opt_out_file)

    test_file = os.path.join(str(tmp_path), "src", "main.py")
    
    assert service.format_file(test_file) == 0
    process.execute_formatter.assert_not_called()

def test_formatting_service_precedence_local_ruff(tmp_path):
    fs = MockFileSystem()
    process = MagicMock(spec=ProcessPort)
    service = FormattingService(fs, process)

    # Configura o mock do git/harness.toml na raiz
    project_root = str(tmp_path)
    fs.existing_files.add(os.path.join(project_root, "harness.toml"))

    # Configura executável local do ruff
    local_ruff = os.path.join(project_root, ".venv", "bin", "ruff")
    fs.existing_files.add(local_ruff)

    test_file = os.path.join(project_root, "app.py")
    
    process.execute_formatter.return_value = (0, "", "")
    assert service.format_file(test_file) == 0
    
    # Verifica se chamou usando o executável local
    process.execute_formatter.assert_called_once_with(
        formatter_name="ruff",
        file_path=os.path.abspath(test_file),
        executable_path=local_ruff
    )

def test_formatting_service_always_returns_zero_on_error(tmp_path):
    fs = MockFileSystem()
    process = MagicMock(spec=ProcessPort)
    service = FormattingService(fs, process)

    test_file = os.path.join(str(tmp_path), "main.py")
    
    # Simula que o formatador retorna erro
    process.execute_formatter.return_value = (1, "", "syntax error")
    
    # Deve continuar retornando 0 (não-bloqueante)
    assert service.format_file(test_file) == 0
