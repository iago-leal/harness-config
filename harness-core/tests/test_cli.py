import subprocess
import os
import sys

def test_cli_help():
    # Caminho do main.py
    main_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../src/main.py"))
    python_bin = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.venv/bin/python3"))

    result = subprocess.run(
        [python_bin, main_path, "--help"],
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0
    assert "Harness Core CLI" in result.stdout
    assert "bootstrap" in result.stdout
    assert "format" in result.stdout
    assert "decisions" in result.stdout
    assert "cmd" in result.stdout

def test_cli_cmd_clarificar():
    main_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../src/main.py"))
    python_bin = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.venv/bin/python3"))

    result = subprocess.run(
        [python_bin, main_path, "cmd", "clarificar"],
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0
    assert "Clarificação de Requisitos" in result.stdout
    assert "limitado a no máximo" in result.stdout
