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


def test_main_dropped_legacy_config_loader():
    # Feature 006: via única de config tipada; load_harness_config removido (dívida T5).
    import importlib

    main_mod = importlib.import_module("src.main")
    assert not hasattr(main_mod, "load_harness_config")
    assert hasattr(main_mod, "load_config")
