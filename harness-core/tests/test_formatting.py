import os
import pytest
from unittest.mock import MagicMock
from src.core.ports.fs import FileSystemPort
from src.core.ports.process import ProcessPort
from src.core.formatting.service import FormattingService
from src.core.domain.config import HarnessConfig
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

def test_formatting_service_dynamic_opt_out(tmp_path):
    fs = MockFileSystem()
    process = MagicMock(spec=ProcessPort)
    
    # Configura opt_out_file customizado no HarnessConfig
    config = HarnessConfig()
    config.formatting.opt_out_file = ".ignorar-format"
    
    service = FormattingService(fs, process, config)

    # Cria opt-out customizado na raiz do projeto
    project_root = str(tmp_path)
    fs.existing_files.add(os.path.join(project_root, "harness.toml"))
    
    opt_out_file = os.path.join(project_root, ".ignorar-format")
    fs.existing_files.add(opt_out_file)

    test_file = os.path.join(project_root, "src", "main.py")
    
    assert service.format_file(test_file) == 0
    process.execute_formatter.assert_not_called()

def test_formatting_service_exclude_paths_glob(tmp_path):
    fs = MockFileSystem()
    process = MagicMock(spec=ProcessPort)
    
    # Configura caminhos excluídos
    config = HarnessConfig()
    config.formatting.exclude_paths = ["logs/*", "**/*.excluida.py"]
    
    service = FormattingService(fs, process, config)

    project_root = str(tmp_path)
    fs.existing_files.add(os.path.join(project_root, "harness.toml"))
    fs.existing_files.add(os.path.join(project_root, ".venv", "bin", "ruff")) # Para formatar Python

    # Caso 1: Excluído por prefixo de pasta com curinga
    file1 = os.path.join(project_root, "logs", "app.py")
    assert service.format_file(file1) == 0
    process.execute_formatter.assert_not_called()

    # Caso 2: Excluído por padrão de extensão com curinga
    file2 = os.path.join(project_root, "src", "teste.excluida.py")
    assert service.format_file(file2) == 0
    process.execute_formatter.assert_not_called()

    # Caso 3: Não excluído (deve tentar formatar)
    file3 = os.path.join(project_root, "src", "valida.py")
    process.execute_formatter.return_value = (0, "", "")
    assert service.format_file(file3) == 0
    process.execute_formatter.assert_called_once()

def test_formatting_service_exclude_paths_prefix(tmp_path):
    fs = MockFileSystem()
    process = MagicMock(spec=ProcessPort)
    
    # Configura exclusão por pasta inteira (prefixo)
    config = HarnessConfig()
    config.formatting.exclude_paths = ["ignored_dir/"]
    
    service = FormattingService(fs, process, config)

    project_root = str(tmp_path)
    fs.existing_files.add(os.path.join(project_root, "harness.toml"))

    file1 = os.path.join(project_root, "ignored_dir", "sub", "file.py")
    assert service.format_file(file1) == 0
    process.execute_formatter.assert_not_called()
