"""Testes do `AntigravityProfile` e da nota de escopo por perfil (feature 009, T002).

Cobrem o contrato pinado em `interfaces/antigravity-hook-io.md`: `hooks_block()`
emite um `hooks.json` parseável com o named-hook `harness` cobrindo
`PreToolUse`/`PostToolUse`/`Stop`, e `apply_instructions()` aponta para
`.agents/hooks.json` sem o aviso de placeholder. Também garantem que o texto de
escopo migrou para o `apply_instructions()` de cada perfil (Claude, Gemini,
Antigravity), sem reintroduzir o placeholder.
"""

import json

import pytest

from src.core.install.harness_profiles import (
    AntigravityProfile,
    ClaudeProfile,
    GeminiProfile,
    get_profile,
)

WRITE_MATCHER = "write_to_file|replace_file_content|multi_replace_file_content"


@pytest.fixture
def block():
    return json.loads(AntigravityProfile().hooks_block())


def test_hooks_block_parses_as_json():
    parsed = json.loads(AntigravityProfile().hooks_block())
    assert isinstance(parsed, dict)


def test_hooks_block_has_harness_named_hook(block):
    assert "harness" in block
    harness = block["harness"]
    assert "PreToolUse" in harness
    assert "PostToolUse" in harness
    assert "Stop" in harness


def test_pre_tool_use_matcher_and_command(block):
    entry = block["harness"]["PreToolUse"][0]
    assert entry["matcher"] == WRITE_MATCHER
    hook = entry["hooks"][0]
    assert hook["type"] == "command"
    assert hook["command"] == "<ABS>/harness agy-hook pre-tool-use"
    assert hook["timeout"] == 10


def test_post_tool_use_matcher_and_command(block):
    entry = block["harness"]["PostToolUse"][0]
    assert entry["matcher"] == WRITE_MATCHER
    hook = entry["hooks"][0]
    assert hook["type"] == "command"
    assert hook["command"] == "<ABS>/harness agy-hook post-tool-use"
    assert hook["timeout"] == 30


def test_stop_has_no_matcher_and_command(block):
    entry = block["harness"]["Stop"][0]
    assert "matcher" not in entry
    hook = entry["hooks"][0]
    assert hook["type"] == "command"
    assert hook["command"] == "<ABS>/harness agy-hook stop"
    assert hook["timeout"] == 10


def test_hooks_block_keeps_abs_placeholder_literal():
    # `<ABS>` é substituído só na materialização; o bloco do perfil o mantém literal.
    assert "<ABS>" in AntigravityProfile().hooks_block()


def test_apply_instructions_points_to_agents_hooks_json():
    text = AntigravityProfile().apply_instructions()
    assert ".agents/hooks.json" in text


def test_apply_instructions_drops_placeholder_warning():
    text = AntigravityProfile().apply_instructions().lower()
    assert "ainda não confirmado" not in text
    assert "ainda não está documentado" not in text


def test_hooks_block_drops_placeholder_warning():
    block = AntigravityProfile().hooks_block().lower()
    assert "ainda não confirmado" not in block
    assert "placeholder" not in block


def test_claude_scope_note_in_apply_instructions():
    text = ClaudeProfile().apply_instructions()
    assert ".claude/settings.json" in text
    assert "~/.claude" in text
    assert "Nunca edite" in text


def test_gemini_scope_note_in_apply_instructions():
    text = GeminiProfile().apply_instructions()
    assert "settings.json" in text
    assert "gemini" in text.lower()


def test_get_profile_resolves_antigravity():
    assert isinstance(get_profile("antigravity"), AntigravityProfile)


def test_get_profile_unknown_raises():
    with pytest.raises(ValueError):
        get_profile("naoexiste")


# --- feature 017: caminho singular do workflow + frontmatter mínimo + órfão ---


def test_session_command_artifact_uses_singular_workflows_path():
    rel_path, _ = AntigravityProfile().session_command_artifact("/abs/proj")
    # O Antigravity registra slash commands a partir de `.agent/workflows/`
    # (singular); o plural `.agents/workflows/` é ignorado.
    assert rel_path == ".agent/workflows/encerrar-sessao.md"


def test_session_command_artifact_frontmatter_has_description_and_no_name():
    _, content = AntigravityProfile().session_command_artifact("/abs/proj")
    assert "description:" in content
    # A doc do Antigravity só exige `description`; `name` foi removido (017).
    assert "\nname:" not in content


def test_stale_session_command_paths_lists_legacy_plural():
    assert AntigravityProfile().stale_session_command_paths() == [
        ".agents/workflows/encerrar-sessao.md"
    ]


def test_base_profiles_have_empty_stale_paths_by_default():
    # Perfis sem override do caminho não declaram órfãos a remover.
    assert ClaudeProfile().stale_session_command_paths() == []
    assert GeminiProfile().stale_session_command_paths() == []
