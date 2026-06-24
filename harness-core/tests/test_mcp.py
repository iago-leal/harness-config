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


def test_mcp_session_command_uses_config_path(monkeypatch):
    # Feature 006: o caminho de sessão vem de config.session.state_file, não de literal chumbado.
    import src.adapters.mcp.server as srv
    from src.core.domain.config import HarnessConfig, SessionSection

    captured = {}

    class FakeCommandService:
        def __init__(self, fs, git):
            pass

        def execute_command(self, command, args, repo_path, session_filepath):
            captured["path"] = session_filepath
            return "ok"

    monkeypatch.setattr(srv, "CommandService", FakeCommandService)
    monkeypatch.setattr(
        srv,
        "load_config",
        lambda fs: HarnessConfig(session=SessionSection(state_file="custom/estado.md")),
    )

    result = srv.session_command("resume")
    assert result == "ok"
    assert captured["path"] == "custom/estado.md"
