from src.core.install.local_apply import apply_local_materializers
from tests.helpers import MockFileSystem


def test_apply_local_materializers_claude_writes_commands_and_settings():
    """Para o Claude: slash commands de sessão (Claude + Antigravity) E o
    .claude/settings.json com o hook de resume (016/RN-05); sem o hooks.json do
    Antigravity (gate RN-N27).
    """
    fs = MockFileSystem()
    apply_local_materializers(fs, "proj", "/abs/proj", "claude")

    assert "proj/.claude/commands/encerrar-sessao.md" in fs.written_files
    assert "proj/.agents/workflows/encerrar-sessao.md" in fs.written_files
    # hooks.json só sai quando o harness ativo é o Antigravity.
    assert "proj/.agents/hooks.json" not in fs.written_files
    # 016/RN-05: para o Claude, o settings.json com o hook de resume é plantado.
    assert "proj/.claude/settings.json" in fs.written_files
    assert "harness cmd resume" in fs.written_files["proj/.claude/settings.json"]


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
    # settings.json do Claude é gated por active_harness == "claude".
    assert "proj/.claude/settings.json" not in fs.written_files
