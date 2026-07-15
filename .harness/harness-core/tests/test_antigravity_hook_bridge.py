"""Testes do adaptador de borda do Antigravity (`hook_bridge`).

Cobrem o contrato stdin/stdout por evento (`pre-tool-use`, `post-tool-use`,
`stop`) descrito em
`_reversa_forward/009-hooks-antigravity/interfaces/antigravity-hook-io.md`,
e o caráter NÃO-BLOQUEANTE: qualquer exceção interna é logada, mas o stdout
exigido ainda é emitido. Usa payloads-fixture e dublês dos serviços de domínio.
"""

import json
import os


from src.adapters.antigravity.hook_bridge import AntigravityHookBridge
from tests.helpers import MockFileSystem


# --------------------------------------------------------------------------- #
# Dublês dos serviços de domínio
# --------------------------------------------------------------------------- #


class SpyFormattingService:
    """Dublê de FormattingService: registra os caminhos formatados."""

    def __init__(self):
        self.formatted = []
        self.return_value = 0

    def format_file(self, file_path: str) -> int:
        self.formatted.append(file_path)
        return self.return_value


class SpyDecisionService:
    """Dublê de DecisionService: registra as chamadas de processamento."""

    def __init__(self):
        self.load_calls = []
        self.validate_calls = []
        self.compile_calls = []

    def load_decisions(self, directory):
        self.load_calls.append(directory)
        return []

    def validate_integrity(self, decisions):
        self.validate_calls.append(decisions)
        return []

    def compile_index(self, decisions, output_filepath, header_filepath=None):
        self.compile_calls.append((output_filepath, header_filepath))


class ExplodingFormattingService:
    """Dublê que sempre lança — para verificar o caráter não-bloqueante."""

    def format_file(self, file_path: str) -> int:
        raise RuntimeError("falha simulada de formatação")


class ExplodingDecisionService:
    def load_decisions(self, directory):
        raise RuntimeError("falha simulada de decisões")

    def validate_integrity(self, decisions):
        raise RuntimeError("falha simulada de decisões")

    def compile_index(self, decisions, output_filepath, header_filepath=None):
        raise RuntimeError("falha simulada de decisões")


# --------------------------------------------------------------------------- #
# Fixtures de payload (camelCase, conforme o contrato do Antigravity)
# --------------------------------------------------------------------------- #

ARTIFACT_DIR = "/proj/.windsurf/artifacts/conv-1"
SCRATCH_FILE = os.path.join(ARTIFACT_DIR, ".harness-agy", "pending-format.json")


def _pre_payload(step_idx=3, target="/proj/src/app.py"):
    return json.dumps(
        {
            "conversationId": "conv-1",
            "workspacePaths": ["/proj"],
            "artifactDirectoryPath": ARTIFACT_DIR,
            "stepIdx": step_idx,
            "toolCall": {
                "name": "write_to_file",
                "args": {"TargetFile": target},
            },
        }
    )


def _post_payload(step_idx=3, error=None):
    payload = {
        "conversationId": "conv-1",
        "workspacePaths": ["/proj"],
        "artifactDirectoryPath": ARTIFACT_DIR,
        "stepIdx": step_idx,
    }
    if error is not None:
        payload["error"] = error
    return json.dumps(payload)


def _stop_payload():
    return json.dumps(
        {
            "conversationId": "conv-1",
            "workspacePaths": ["/proj"],
            "terminationReason": "model_stop",
            "fullyIdle": True,
        }
    )


def _make_bridge(fs=None, formatting=None, decisions=None, gate_evaluator=None):
    return AntigravityHookBridge(
        fs=fs or MockFileSystem(),
        formatting_service=formatting or SpyFormattingService(),
        decision_service=decisions or SpyDecisionService(),
        decisions_dir=".reversa/decisoes",
        decisions_index_file=".reversa/microdecisoes.md",
        decisions_header_file=".reversa/decisoes/_cabecalho.md",
        gate_evaluator=gate_evaluator,
    )


# --------------------------------------------------------------------------- #
# pre-tool-use
# --------------------------------------------------------------------------- #


def test_pre_tool_use_grava_mapa_step_para_target():
    fs = MockFileSystem()
    bridge = _make_bridge(fs=fs)

    out = bridge.handle(
        "pre-tool-use", _pre_payload(step_idx=3, target="/proj/src/app.py")
    )

    assert SCRATCH_FILE in fs.written_files
    mapa = json.loads(fs.written_files[SCRATCH_FILE])
    assert mapa["3"] == "/proj/src/app.py"
    # stdout: nunca bloqueia
    assert json.loads(out) == {"decision": "allow"}


def test_pre_tool_use_preserva_entradas_anteriores_do_mapa():
    fs = MockFileSystem()
    fs.written_files[SCRATCH_FILE] = json.dumps({"1": "/proj/old.py"})
    bridge = _make_bridge(fs=fs)

    bridge.handle("pre-tool-use", _pre_payload(step_idx=2, target="/proj/new.py"))

    mapa = json.loads(fs.written_files[SCRATCH_FILE])
    assert mapa == {"1": "/proj/old.py", "2": "/proj/new.py"}


def test_pre_tool_use_nunca_emite_deny():
    bridge = _make_bridge()
    out = bridge.handle("pre-tool-use", _pre_payload())
    parsed = json.loads(out)
    assert parsed.get("decision") != "deny"
    assert parsed == {"decision": "allow"}


# --------------------------------------------------------------------------- #
# post-tool-use
# --------------------------------------------------------------------------- #


def test_post_tool_use_formata_o_caminho_do_mapa():
    fs = MockFileSystem()
    fs.written_files[SCRATCH_FILE] = json.dumps({"3": "/proj/src/app.py"})
    spy_fmt = SpyFormattingService()
    bridge = _make_bridge(fs=fs, formatting=spy_fmt)

    out = bridge.handle("post-tool-use", _post_payload(step_idx=3))

    assert spy_fmt.formatted == ["/proj/src/app.py"]
    assert json.loads(out) == {}


def test_post_tool_use_emite_objeto_vazio():
    fs = MockFileSystem()
    fs.written_files[SCRATCH_FILE] = json.dumps({"3": "/proj/src/app.py"})
    bridge = _make_bridge(fs=fs)
    out = bridge.handle("post-tool-use", _post_payload(step_idx=3))
    assert json.loads(out) == {}


def test_post_tool_use_sem_mapa_nao_chama_formatador():
    fs = MockFileSystem()  # scratch ausente
    spy_fmt = SpyFormattingService()
    bridge = _make_bridge(fs=fs, formatting=spy_fmt)

    out = bridge.handle("post-tool-use", _post_payload(step_idx=3))

    assert spy_fmt.formatted == []
    assert json.loads(out) == {}


def test_post_tool_use_step_ausente_no_mapa_nao_formata():
    fs = MockFileSystem()
    fs.written_files[SCRATCH_FILE] = json.dumps({"1": "/proj/outro.py"})
    spy_fmt = SpyFormattingService()
    bridge = _make_bridge(fs=fs, formatting=spy_fmt)

    out = bridge.handle("post-tool-use", _post_payload(step_idx=3))

    assert spy_fmt.formatted == []
    assert json.loads(out) == {}


def test_post_tool_use_com_erro_da_tool_nao_formata():
    fs = MockFileSystem()
    fs.written_files[SCRATCH_FILE] = json.dumps({"3": "/proj/src/app.py"})
    spy_fmt = SpyFormattingService()
    bridge = _make_bridge(fs=fs, formatting=spy_fmt)

    out = bridge.handle("post-tool-use", _post_payload(step_idx=3, error="boom"))

    assert spy_fmt.formatted == []
    assert json.loads(out) == {}


# --------------------------------------------------------------------------- #
# stop
# --------------------------------------------------------------------------- #


def test_stop_chama_servico_de_decisoes():
    spy_dec = SpyDecisionService()
    bridge = _make_bridge(decisions=spy_dec)

    out = bridge.handle("stop", _stop_payload())

    assert spy_dec.load_calls == [".reversa/decisoes"]
    assert len(spy_dec.compile_calls) == 1
    assert json.loads(out) == {}


def test_stop_nunca_emite_continue():
    spy_dec = SpyDecisionService()
    bridge = _make_bridge(decisions=spy_dec)

    out = bridge.handle("stop", _stop_payload())
    parsed = json.loads(out)

    assert parsed.get("decision") != "continue"
    assert parsed == {}


# --------------------------------------------------------------------------- #
# stop — advisory do gate de registro (feature 022, RN-N26 preservada)
# --------------------------------------------------------------------------- #


def _verdict(pendente, mudancas=None):
    from src.core.decisions.gate import GateVerdict

    return GateVerdict(
        pendente=pendente,
        mudancas=mudancas or [],
        fichas_tocadas=[],
        fingerprint="f" * 40,
    )


def test_stop_com_pendencia_avisa_em_stderr_e_emite_vazio(capsys):
    bridge = _make_bridge(gate_evaluator=lambda: _verdict(True, ["contrato.md"]))

    out = bridge.handle("stop", _stop_payload())

    assert json.loads(out) == {}  # advisory: stdout intocado, nunca bloqueia
    captured = capsys.readouterr()
    assert "pendente" in captured.err


def test_stop_sem_pendencia_nao_avisa(capsys):
    bridge = _make_bridge(gate_evaluator=lambda: _verdict(False))

    out = bridge.handle("stop", _stop_payload())

    assert json.loads(out) == {}
    assert capsys.readouterr().err == ""


def test_stop_avaliador_explodindo_nao_bloqueia(capsys):
    def boom():
        raise RuntimeError("git indisponível")

    bridge = _make_bridge(gate_evaluator=boom)

    out = bridge.handle("stop", _stop_payload())

    assert json.loads(out) == {}
    assert capsys.readouterr().err


# --------------------------------------------------------------------------- #
# Não-bloqueante: exceções internas nunca abortam o stdout exigido
# --------------------------------------------------------------------------- #


def test_post_tool_use_excecao_no_formatador_ainda_emite_vazio(capsys):
    fs = MockFileSystem()
    fs.written_files[SCRATCH_FILE] = json.dumps({"3": "/proj/src/app.py"})
    bridge = _make_bridge(fs=fs, formatting=ExplodingFormattingService())

    out = bridge.handle("post-tool-use", _post_payload(step_idx=3))

    assert json.loads(out) == {}
    captured = capsys.readouterr()
    assert captured.err  # erro barulhento em stderr


def test_stop_excecao_no_servico_ainda_emite_vazio(capsys):
    bridge = _make_bridge(decisions=ExplodingDecisionService())

    out = bridge.handle("stop", _stop_payload())

    assert json.loads(out) == {}
    captured = capsys.readouterr()
    assert captured.err


def test_pre_tool_use_stdin_invalido_ainda_emite_allow(capsys):
    bridge = _make_bridge()

    out = bridge.handle("pre-tool-use", "isto não é json")

    assert json.loads(out) == {"decision": "allow"}
    captured = capsys.readouterr()
    assert captured.err


def test_post_tool_use_stdin_invalido_ainda_emite_vazio():
    bridge = _make_bridge()
    out = bridge.handle("post-tool-use", "{quebrado")
    assert json.loads(out) == {}


def test_evento_desconhecido_emite_vazio_sem_quebrar():
    bridge = _make_bridge()
    out = bridge.handle("evento-inexistente", "{}")
    assert json.loads(out) == {}


# --------------------------------------------------------------------------- #
# Integração fina com a CLI (subcomando agy-hook)
# --------------------------------------------------------------------------- #


def test_cli_registra_subcomando_agy_hook():
    import subprocess

    main_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../src/main.py")
    )
    python_bin = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../.venv/bin/python3")
    )
    result = subprocess.run(
        [python_bin, main_path, "--help"], capture_output=True, text=True
    )
    assert result.returncode == 0
    assert "agy-hook" in result.stdout


def test_cli_agy_hook_pre_tool_use_emite_allow():
    import subprocess

    main_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../src/main.py")
    )
    python_bin = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../.venv/bin/python3")
    )
    result = subprocess.run(
        [python_bin, main_path, "agy-hook", "pre-tool-use"],
        input=_pre_payload(),
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert json.loads(result.stdout.strip().splitlines()[-1]) == {"decision": "allow"}


def test_cli_agy_hook_rejeita_evento_invalido():
    import subprocess

    main_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../src/main.py")
    )
    python_bin = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../.venv/bin/python3")
    )
    result = subprocess.run(
        [python_bin, main_path, "agy-hook", "evento-invalido"],
        capture_output=True,
        text=True,
    )
    # argparse rejeita choices inválidos com exit code 2
    assert result.returncode == 2
