import json
import pytest

from src.core.session.sinks import HookContextSink, FileProjectionSink, get_sink
from tests.helpers import MockFileSystem


def test_hook_sink_emits_valid_json(capsys):
    HookContextSink().emit("estado da sessão anterior")
    out = capsys.readouterr().out
    payload = json.loads(out)
    assert payload["hookSpecificOutput"]["hookEventName"] == "SessionStart"
    assert (
        payload["hookSpecificOutput"]["additionalContext"]
        == "estado da sessão anterior"
    )


def test_hook_sink_truncates_above_limit(capsys):
    HookContextSink().emit("x" * 20000)
    out = capsys.readouterr().out
    ctx = json.loads(out)["hookSpecificOutput"]["additionalContext"]
    assert len(ctx) <= HookContextSink.MAX_CHARS
    assert "truncado" in ctx


def test_file_projection_sink_writes_file():
    fs = MockFileSystem()
    sink = FileProjectionSink(fs, ".agents/rules/estado-sessao.md")
    sink.emit("conteudo projetado")
    assert fs.read_file(".agents/rules/estado-sessao.md") == "conteudo projetado"


def test_get_sink_by_harness():
    fs = MockFileSystem()
    assert isinstance(get_sink("claude", fs), HookContextSink)
    assert isinstance(get_sink("gemini", fs), HookContextSink)
    assert isinstance(get_sink("antigravity", fs), FileProjectionSink)


def test_get_sink_unknown_harness_raises():
    with pytest.raises(ValueError):
        get_sink("desconhecido", MockFileSystem())
