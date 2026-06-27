"""Materialização do .claude/settings.json do Claude (feature 016, RN-05)."""

import json

from src.core.install.claude_settings import materialize_claude_settings
from tests.helpers import MockFileSystem

SETTINGS = "proj/.claude/settings.json"


def test_creates_settings_with_resume_hook_when_absent():
    fs = MockFileSystem()
    materialize_claude_settings(fs, "proj")

    assert SETTINGS in fs.written_files
    data = json.loads(fs.written_files[SETTINGS])
    blob = json.dumps(data)
    assert "SessionStart" in data["hooks"]
    assert "harness cmd resume" in blob


def test_idempotent_second_run_equals_first():
    fs = MockFileSystem()
    materialize_claude_settings(fs, "proj")
    first = fs.written_files[SETTINGS]
    materialize_claude_settings(fs, "proj")
    assert fs.written_files[SETTINGS] == first


def test_preserves_third_party_keys_and_hooks():
    fs = MockFileSystem()
    fs.write_file(
        SETTINGS,
        json.dumps(
            {
                "model": "opus",
                "hooks": {
                    "PreToolUse": [{"matcher": "X", "hooks": []}],
                },
            }
        ),
    )
    materialize_claude_settings(fs, "proj")

    data = json.loads(fs.written_files[SETTINGS])
    # Chave de topo de terceiros preservada.
    assert data["model"] == "opus"
    # Evento de hook de terceiros preservado.
    assert "PreToolUse" in data["hooks"]
    # Hook do harness garantido.
    assert "SessionStart" in data["hooks"]
    assert "harness cmd resume" in json.dumps(data["hooks"]["SessionStart"])
