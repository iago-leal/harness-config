import pytest
from src.adapters.fs.local import LocalFileSystemAdapter
from src.core.install.service import InstallPromptService
from src.main import build_parser


def _render(harness):
    fs = LocalFileSystemAdapter()
    return InstallPromptService(fs).render(harness, build_parser())


def test_prompt_has_core_steps():
    out = _render("claude")
    assert "ambiente virtual" in out.lower()
    assert "requirements.txt" in out
    assert "./harness" in out
    assert "./harness decisions" in out
    assert "Verificação de saúde" in out


def test_prompt_scopes_to_project_settings():
    out = _render("claude")
    assert ".claude/settings.json" in out
    assert "~/.claude" in out
    assert "Nunca edite" in out


def test_prompt_signals_sessionstart_gap():
    out = _render("claude")
    assert "SessionStart" in out
    assert "pendente" in out.lower()
    assert "MD-0001" in out


def test_prompt_parametrized_by_harness():
    claude = _render("claude")
    gemini = _render("gemini")
    assert "claude" in claude.lower()
    assert "context." in gemini
    assert claude != gemini


def test_unknown_harness_raises():
    fs = LocalFileSystemAdapter()
    with pytest.raises(ValueError):
        InstallPromptService(fs).render("naoexiste", build_parser())
