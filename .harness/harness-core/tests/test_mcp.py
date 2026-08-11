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

        def execute_command(
            self, command, args, repo_path, session_filepath, caminhos_extras=None
        ):
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


def test_mcp_check_repository_sync_usa_cache_canonico(monkeypatch):
    # T7 (G-12): o MCP gravava o cache em .harness/sync_cache.json (underscore),
    # fora do caminho canônico que o init registra no .gitignore — desde a
    # feature 019, o arquivo escaparia para a oferta de commit. O caminho deve
    # vir da fonte única em layout.py, idêntico ao da CLI e do close_flow.
    import src.adapters.mcp.server as srv
    from src.core.domain.layout import SYNC_CACHE_REL_PATH

    captured = {}

    class FakeSyncService:
        def __init__(self, fs, git, cache_filepath, cache_ttl_hours=24):
            captured["cache"] = cache_filepath

        def check_sync(self, path):
            return True

    monkeypatch.setattr(srv, "SyncService", FakeSyncService)
    result = srv.check_repository_sync("/tmp")
    assert "Sincronizado" in result
    assert captured["cache"] == SYNC_CACHE_REL_PATH


def test_mcp_process_decisions_deriva_visao_compacta(tmp_path, monkeypatch):
    # T8 (G-20): a borda MCP compilava só o índice; a visão compacta (f028)
    # deve ser derivada na MESMA passada, como na CLI e na ponte Antigravity
    # (RN-N56 — nunca existe passada que atualize só uma visão), lendo os
    # caminhos de config.decisions.compact_file/compact_index_size.
    import os

    import src.adapters.mcp.server as srv
    from src.core.domain.config import DecisionsSection, HarnessConfig

    decisoes_dir = str(tmp_path / "decisoes")
    index_file = str(tmp_path / "microdecisoes.md")
    compact_file = str(tmp_path / "decisoes-recentes.md")
    srv.fs.makedirs(decisoes_dir)
    srv.fs.write_file(
        os.path.join(decisoes_dir, "_cabecalho.md"), "# Índice de Microdecisões\n"
    )
    srv.fs.write_file(
        os.path.join(decisoes_dir, "MD-0001.md"),
        """---
id: MD-0001
gancho: pre-commit
relacoes: []
estado: ativo
---

# MD-0001 — Decisão de teste
- **D:** conteúdo mínimo
""",
    )
    monkeypatch.setattr(
        srv,
        "load_config",
        lambda fs: HarnessConfig(
            decisions=DecisionsSection(
                dir=decisoes_dir,
                index_file=index_file,
                compact_file=compact_file,
                compact_index_size=10,
            )
        ),
    )

    result = srv.process_decisions()

    assert "compilado com sucesso" in result
    assert srv.fs.exists(index_file)
    assert srv.fs.exists(compact_file)
    compact = srv.fs.read_file(compact_file)
    assert "- **MD-0001** — Decisão de teste" in compact


def _config_encerramento(tmp_path):
    from src.core.domain.config import (
        DecisionsSection,
        HarnessConfig,
        SessionSection,
    )
    import os

    return HarnessConfig(
        session=SessionSection(state_file=str(tmp_path / "estado.md")),
        decisions=DecisionsSection(
            dir=str(tmp_path / "decisoes"),
            index_file=str(tmp_path / "microdecisoes.md"),
            header_file=os.path.join(str(tmp_path / "decisoes"), "_cabecalho.md"),
            compact_file=str(tmp_path / "decisoes-recentes.md"),
            compact_index_size=10,
        ),
    )


def test_mcp_encerrar_sessao_deriva_visoes_e_versiona_junto(tmp_path, monkeypatch):
    # Dívida da MD-0025 fechada na MD-0026: a borda MCP também é uma borda de
    # encerramento (RN-N56) — deriva as duas visões ANTES do fechamento e as
    # inclui no commit de encerramento, para a árvore terminar limpa.
    import os

    import src.adapters.mcp.server as srv
    from src.core.domain.models import SessionState
    from src.core.session import serializer
    from tests.test_commands import FakeGit

    config = _config_encerramento(tmp_path)
    srv.fs.makedirs(config.decisions.dir)
    srv.fs.write_file(
        os.path.join(config.decisions.dir, "_cabecalho.md"),
        "# Índice de Microdecisões\n",
    )
    srv.fs.write_file(
        os.path.join(config.decisions.dir, "MD-0001.md"),
        """---
id: MD-0001
gancho: teste
relacoes: []
estado: ativo
---

# MD-0001 — Decisão da borda MCP
- **D:** d
- **PORQUÊ:** p
- **DESCARTADO:** nada
- **ESTADO:** feito
""",
    )
    srv.fs.write_file(
        config.session.state_file,
        serializer.render(
            SessionState(commit_hash="a" * 40, active_feature="feat-mcp")
        ),
    )
    fake_git = FakeGit("a" * 40)
    monkeypatch.setattr(srv, "git", fake_git)
    monkeypatch.setattr(srv, "load_config", lambda fs: config)

    result = srv.session_command("encerrar-sessao")

    assert "Sessão encerrada com sucesso" in result
    assert srv.fs.exists(config.decisions.index_file)
    assert srv.fs.exists(config.decisions.compact_file)
    compact = srv.fs.read_file(config.decisions.compact_file)
    assert "- **MD-0001** — Decisão da borda MCP" in compact
    # As visões entram no MESMO commit de encerramento, junto do estado.
    assert len(fake_git.commit_calls) == 1
    _, called_paths, _ = fake_git.commit_calls[0]
    assert called_paths == [
        config.session.state_file,
        config.decisions.index_file,
        config.decisions.compact_file,
    ]


def test_mcp_encerrar_sessao_sem_sessao_nao_deriva(tmp_path, monkeypatch):
    # Sessão ausente é no-op (D1 da 016): sem fechamento, sem derivação.
    import os

    import src.adapters.mcp.server as srv
    from tests.test_commands import FakeGit

    config = _config_encerramento(tmp_path)
    srv.fs.makedirs(config.decisions.dir)
    srv.fs.write_file(
        os.path.join(config.decisions.dir, "MD-0001.md"),
        "---\nid: MD-0001\ngancho: t\nrelacoes: []\nestado: ativo\n---\n\n# MD-0001 — X\n",
    )
    fake_git = FakeGit("a" * 40)
    monkeypatch.setattr(srv, "git", fake_git)
    monkeypatch.setattr(srv, "load_config", lambda fs: config)

    result = srv.session_command("encerrar-sessao")

    assert "Nenhuma sessão para encerrar" in result
    assert not srv.fs.exists(config.decisions.index_file)
    assert not srv.fs.exists(config.decisions.compact_file)
    assert fake_git.commit_calls == []
