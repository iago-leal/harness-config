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
    # MESMO evento gerenciado pelo harness (Stop) deve sobreviver ao lado do item
    # do harness — não ser descartado pela substituição do array inteiro.
    fs = MockFileSystem()
    fs.write_file(
        SETTINGS,
        json.dumps(
            {
                "hooks": {
                    "Stop": [
                        {
                            "hooks": [{"type": "command", "command": "meu-notificador.sh"}],
                        }
                    ]
                }
            }
        ),
    )
    materialize_claude_settings(fs, "proj")

    stop = json.loads(fs.written_files[SETTINGS])["hooks"]["Stop"]
    blob = json.dumps(stop)
    assert "meu-notificador.sh" in blob  # item alheio preservado
    assert "harness decisions" in blob  # item do harness inserido no mesmo array
    assert len(stop) == 2  # os dois convivem, sem clobber


def test_second_run_does_not_duplicate_harness_item_in_array():
    # Idempotência POR-ITEM: reexecutar não acumula cópias do item do harness no
    # array do evento, e ainda preserva o item alheio.
    fs = MockFileSystem()
    fs.write_file(
        SETTINGS,
        json.dumps(
            {
                "hooks": {
                    "Stop": [
                        {
                            "hooks": [{"type": "command", "command": "meu-notificador.sh"}],
                        }
                    ]
                }
            }
        ),
    )
    materialize_claude_settings(fs, "proj")
    materialize_claude_settings(fs, "proj")

    stop = json.loads(fs.written_files[SETTINGS])["hooks"]["Stop"]
    harness_items = [i for i in stop if "harness decisions" in json.dumps(i)]
    assert len(harness_items) == 1  # não duplicou
    assert any("meu-notificador.sh" in json.dumps(i) for i in stop)  # alheio preservado


def test_materialized_stop_item_uses_gate_flag():
    # Feature 022: o item Stop materializado invoca `harness decisions --gate`.
    fs = MockFileSystem()
    materialize_claude_settings(fs, "proj")

    blob = json.dumps(json.loads(fs.written_files[SETTINGS])["hooks"]["Stop"])
    assert "harness decisions --gate" in blob


def test_replaces_legacy_decisions_item_with_gate_variant():
    # Instalação pré-022 tem Stop → "harness decisions" (sem flag). O merge
    # por-item SUBSTITUI pelo item novo (mesma assinatura), sem duplicar e
    # preservando o item alheio no mesmo evento (RN-N39).
    fs = MockFileSystem()
    fs.write_file(
        SETTINGS,
        json.dumps(
            {
                "hooks": {
                    "Stop": [
                        {
                            "hooks": [
                                {
                                    "type": "command",
                                    "command": "${CLAUDE_PROJECT_DIR}/harness decisions",
                                    "timeout": 10,
                                }
                            ]
                        },
                        {
                            "hooks": [{"type": "command", "command": "meu-notificador.sh"}],
                        },
                    ]
                }
            }
        ),
    )
    materialize_claude_settings(fs, "proj")

    stop = json.loads(fs.written_files[SETTINGS])["hooks"]["Stop"]
    blob = json.dumps(stop)
    assert "harness decisions --gate" in blob
    harness_items = [i for i in stop if "harness decisions" in json.dumps(i)]
    assert len(harness_items) == 1  # substituiu, não duplicou
    assert "meu-notificador.sh" in blob  # alheio preservado


def test_absent_creates_single_item_per_harness_event():
    # Sem settings prévio: cada evento do harness nasce com exatamente um item.
    fs = MockFileSystem()
    materialize_claude_settings(fs, "proj")

    hooks = json.loads(fs.written_files[SETTINGS])["hooks"]
    for event in ("SessionStart", "Stop"):
        assert len(hooks[event]) == 1
    # PostToolUse (format-on-edit) não é mais materializado.
    assert "PostToolUse" not in hooks


def test_session_start_matcher_covers_compact():
    """MD-0024: o SessionStart deve disparar também após compact/auto-compact,
    para o `cmd resume` reabrir a sessão encerrada na mesma conversa."""
    fs = MockFileSystem()
    materialize_claude_settings(fs, "proj")

    data = json.loads(fs.written_files[SETTINGS])
    matcher = data["hooks"]["SessionStart"][0]["matcher"]
    assert matcher == "startup|resume|clear|compact"


def test_replaces_legacy_matcher_without_compact():
    """Instalação pré-MD-0024 (matcher sem `compact`) é substituída pelo
    merge por-item, sem duplicar o gancho."""
    fs = MockFileSystem()
    fs.write_file(
        SETTINGS,
        json.dumps(
        {
            "hooks": {
                "SessionStart": [
                    {
                        "matcher": "startup|resume|clear",
                        "hooks": [
                            {
                                "type": "command",
                                "command": "${CLAUDE_PROJECT_DIR}/harness cmd resume",
                                "timeout": 12,
                            }
                        ],
                    }
                ]
            }
        }
        ),
    )
    materialize_claude_settings(fs, "proj")

    data = json.loads(fs.written_files[SETTINGS])
    session_start = data["hooks"]["SessionStart"]
    assert len(session_start) == 1
    assert session_start[0]["matcher"] == "startup|resume|clear|compact"
