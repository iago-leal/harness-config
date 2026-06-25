from src.core.install.local_apply import apply_local_materializers
from tests.helpers import MockFileSystem


def test_apply_local_materializers_claude_writes_session_commands_only():
    """Para harness não-Antigravity, materializa só os slash commands de sessão
    (Claude + Antigravity), sem o hooks.json do Antigravity (gate RN-N27).
    """
    fs = MockFileSystem()
    apply_local_materializers(fs, "proj", "/abs/proj", "claude")

    assert "proj/.claude/commands/encerrar-sessao.md" in fs.written_files
    assert "proj/.agents/workflows/encerrar-sessao.md" in fs.written_files
    # hooks.json só sai quando o harness ativo é o Antigravity.
    assert "proj/.agents/hooks.json" not in fs.written_files


def test_apply_local_materializers_antigravity_also_writes_hooks_json():
    """Para harness Antigravity, além dos slash commands, materializa o
    .agents/hooks.json com o <ABS> resolvido para o caminho do projeto.
    """
    fs = MockFileSystem()
    apply_local_materializers(fs, "proj", "/abs/proj", "antigravity")

    assert "proj/.claude/commands/encerrar-sessao.md" in fs.written_files
    assert "proj/.agents/hooks.json" in fs.written_files
    content = fs.written_files["proj/.agents/hooks.json"]
    assert '"harness"' in content
    assert "/abs/proj/harness agy-hook" in content
    assert "<ABS>" not in content
