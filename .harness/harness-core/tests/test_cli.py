import subprocess
import os
from unittest import mock


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


def test_bootstrap_refuses_without_git_repo(tmp_path):
    # Sem repositório git e sem TTY (subprocess), `bootstrap` recusa: não instala
    # hooks, não cria um .git degenerado, e falha de forma barulhenta (exit != 0).
    main_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../src/main.py")
    )
    python_bin = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../.venv/bin/python3")
    )

    result = subprocess.run(
        [python_bin, main_path, "bootstrap"],
        capture_output=True,
        text=True,
        cwd=str(tmp_path),
    )

    assert result.returncode != 0
    assert "repositório git" in (result.stdout + result.stderr)
    assert not (tmp_path / ".git").exists()


def test_bootstrap_installs_hooks_in_git_repo(tmp_path):
    # Com um repositório git presente, `bootstrap` instala os dois hooks.
    main_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../src/main.py")
    )
    python_bin = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../.venv/bin/python3")
    )

    subprocess.run(["git", "init"], cwd=str(tmp_path), capture_output=True)

    result = subprocess.run(
        [python_bin, main_path, "bootstrap"],
        capture_output=True,
        text=True,
        cwd=str(tmp_path),
    )

    assert result.returncode == 0
    assert (tmp_path / ".git" / "hooks" / "pre-commit").exists()
    assert (tmp_path / ".git" / "hooks" / "post-merge").exists()


def test_offer_git_init_noninteractive_returns_false():
    # Sem TTY, a oferta não pergunta nada e recusa (o chamador então aborta).
    from src.main import offer_git_init

    with mock.patch("sys.stdin.isatty", return_value=False):
        assert offer_git_init("/qualquer/caminho") is False


def test_offer_git_init_parses_affirmative_answers():
    from src.main import offer_git_init

    with mock.patch("sys.stdin.isatty", return_value=True):
        for sim in ("s", "S", "sim", "y", "yes", " Sim "):
            with mock.patch("builtins.input", return_value=sim):
                assert offer_git_init("/repo") is True
        for nao in ("", "n", "não", "nope", "x"):
            with mock.patch("builtins.input", return_value=nao):
                assert offer_git_init("/repo") is False


def test_cli_upgrade_has_force_flag():
    # Feature 012: o subcomando `upgrade` expõe a flag --force.
    main_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../src/main.py")
    )
    python_bin = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../.venv/bin/python3")
    )

    result = subprocess.run(
        [python_bin, main_path, "upgrade", "--help"], capture_output=True, text=True
    )

    assert result.returncode == 0
    assert "--force" in result.stdout


def test_cli_materialize_writes_session_command(tmp_path):
    # Feature 012 (Modo 1, código real): o subcomando interno `materialize`,
    # rodado como o upgrade o invocaria no destino, produz o slash command de
    # sessão a partir do CÓDIGO LOCAL — prova de que a materialização não é stale.
    main_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../src/main.py")
    )
    python_bin = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../.venv/bin/python3")
    )

    (tmp_path / "harness.toml").write_text('[harness]\nactive_harness = "claude"\n')

    result = subprocess.run(
        [python_bin, main_path, "materialize"],
        capture_output=True,
        text=True,
        cwd=str(tmp_path),
    )

    assert result.returncode == 0
    assert (tmp_path / ".claude" / "commands" / "encerrar-sessao.md").exists()
