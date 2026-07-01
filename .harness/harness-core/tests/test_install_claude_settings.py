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


def test_preserves_user_item_in_same_harness_event():
    # Feature 020 (RN-06): o merge é POR-ITEM. Um hook próprio do usuário no
    # MESMO evento gerenciado pelo harness (PostToolUse) deve sobreviver ao lado
    # do item do harness — não ser descartado pela substituição do array inteiro.
    fs = MockFileSystem()
    fs.write_file(
        SETTINGS,
        json.dumps(
            {
                "hooks": {
                    "PostToolUse": [
                        {
                            "matcher": "Write",
                            "hooks": [{"type": "command", "command": "meu-linter.sh"}],
                        }
                    ]
                }
            }
        ),
    )
    materialize_claude_settings(fs, "proj")

    post = json.loads(fs.written_files[SETTINGS])["hooks"]["PostToolUse"]
    blob = json.dumps(post)
    assert "meu-linter.sh" in blob  # item alheio preservado
    assert "harness format" in blob  # item do harness inserido no mesmo array
    assert len(post) == 2  # os dois convivem, sem clobber


def test_second_run_does_not_duplicate_harness_item_in_array():
    # Idempotência POR-ITEM: reexecutar não acumula cópias do item do harness no
    # array do evento, e ainda preserva o item alheio.
    fs = MockFileSystem()
    fs.write_file(
        SETTINGS,
        json.dumps(
            {
                "hooks": {
                    "PostToolUse": [
                        {
                            "matcher": "Write",
                            "hooks": [{"type": "command", "command": "meu-linter.sh"}],
                        }
                    ]
                }
            }
        ),
    )
    materialize_claude_settings(fs, "proj")
    materialize_claude_settings(fs, "proj")

    post = json.loads(fs.written_files[SETTINGS])["hooks"]["PostToolUse"]
    harness_items = [i for i in post if "harness format" in json.dumps(i)]
    assert len(harness_items) == 1  # não duplicou
    assert any("meu-linter.sh" in json.dumps(i) for i in post)  # alheio preservado


def test_absent_creates_single_item_per_harness_event():
    # Sem settings prévio: cada evento do harness nasce com exatamente um item.
    fs = MockFileSystem()
    materialize_claude_settings(fs, "proj")

    hooks = json.loads(fs.written_files[SETTINGS])["hooks"]
    for event in ("SessionStart", "PostToolUse", "Stop"):
        assert len(hooks[event]) == 1
