import pytest
from src.adapters.mcp.server import session_command, format_file

def test_mcp_session_command_execution():
    # Executa a função diretamente
    result = session_command("clarificar")
    assert "Clarificação de Requisitos" in result
    assert "limitado a no máximo **2 rodadas**" in result

def test_mcp_format_file_execution(tmp_path):
    # Executa a formatação num arquivo temporário de outra extensão (ignorado, retorna mensagem)
    dummy_file = str(tmp_path / "test.txt")
    result = format_file(dummy_file)
    assert "Formatação processada" in result
