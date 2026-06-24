import subprocess
import os


def test_cli_help():
    # Caminho do main.py
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
    assert "Harness Core CLI" in result.stdout
    assert "bootstrap" in result.stdout
    assert "format" in result.stdout
    assert "decisions" in result.stdout
    assert "cmd" in result.stdout


def test_cli_cmd_clarificar():
    main_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../src/main.py")
    )
    python_bin = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../.venv/bin/python3")
    )

    result = subprocess.run(
        [python_bin, main_path, "cmd", "clarificar"], capture_output=True, text=True
    )

    assert result.returncode == 0
    assert "Clarificação de Requisitos" in result.stdout
    assert "limitado a no máximo" in result.stdout


def test_agy_hook_nonblocking_on_malformed_config(tmp_path):
    """Gancho de borda não-bloqueante: harness.toml malformado no projeto-alvo
    não pode escapar como traceback/exit 1. O ramo deve emitir o fallback do
    evento no stdout (`{}` para stop) e encerrar com 0.

    Reproduz o cenário do finding HIGH (config corrompida após pausa longa).
    """
    main_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../src/main.py")
    )
    python_bin = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../.venv/bin/python3")
    )

    # harness.toml deliberadamente quebrado no diretório de trabalho.
    (tmp_path / "harness.toml").write_text('[harness\nactive_harness = "claude"\n')

    result = subprocess.run(
        [python_bin, main_path, "agy-hook", "stop"],
        input="{}",
        capture_output=True,
        text=True,
        cwd=str(tmp_path),
    )

    assert result.returncode == 0
    assert result.stdout.strip() == "{}"


def test_agy_hook_nonblocking_pre_tool_use_fallback(tmp_path):
    """Para `pre-tool-use`, o fallback não-bloqueante deve liberar a ação
    (`{"decision": "allow"}`), nunca bloquear por config quebrada."""
    main_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../src/main.py")
    )
    python_bin = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../.venv/bin/python3")
    )

    (tmp_path / "harness.toml").write_text('[harness\nactive_harness = "claude"\n')

    result = subprocess.run(
        [python_bin, main_path, "agy-hook", "pre-tool-use"],
        input="{}",
        capture_output=True,
        text=True,
        cwd=str(tmp_path),
    )

    assert result.returncode == 0
    assert '"decision": "allow"' in result.stdout


def test_main_dropped_legacy_config_loader():
    # Feature 006: via única de config tipada; load_harness_config removido (dívida T5).
    import importlib

    main_mod = importlib.import_module("src.main")
    assert not hasattr(main_mod, "load_harness_config")
    assert hasattr(main_mod, "load_config")
