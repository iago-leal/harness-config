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


# --- Ofertas de fim de sessão (feature 014) -------------------------------


def _offers(push=None, upgrade=None):
    from src.core.session.offers import EndSessionOffers

    return EndSessionOffers(push=push, upgrade=upgrade)


def _push(branch="feature-x", ahead=2, is_default=False):
    from src.core.session.offers import PushOffer

    return PushOffer(branch=branch, ahead=ahead, is_default_branch=is_default)


def _upgrade(current="1.0.0", target="2.0.0", up="/up"):
    from src.core.session.offers import UpgradeOffer

    return UpgradeOffer(
        current_version=current, target_version=target, upstream_path=up
    )


def test_render_offer_markers_push_e_upgrade():
    from src.main import render_offer_markers

    lines = render_offer_markers(_offers(push=_push(), upgrade=_upgrade()))
    assert len(lines) == 2
    assert lines[0].startswith("[HARNESS:PUSH_DISPONIVEL")
    assert "branch=feature-x" in lines[0]
    assert "ahead=2" in lines[0]
    assert "principal=false" in lines[0]
    assert lines[1].startswith("[HARNESS:UPGRADE_DISPONIVEL")
    assert "atual=1.0.0" in lines[1]
    assert "alvo=2.0.0" in lines[1]


def test_render_offer_markers_vazio():
    from src.main import render_offer_markers

    assert render_offer_markers(_offers()) == []


def test_conduct_sem_tty_emite_marcadores_sem_ler_entrada():
    from src.main import conduct_end_session_offers

    saidas = []

    def asker_proibido(_q):
        raise AssertionError("não deve perguntar sem TTY")

    conduct_end_session_offers(
        _offers(push=_push(), upgrade=_upgrade()),
        "repo",
        git=mock.MagicMock(),
        run_upgrade=lambda u: (_ for _ in ()).throw(
            AssertionError("não deve atualizar sem TTY")
        ),
        is_interactive=False,
        asker=asker_proibido,
        out=saidas.append,
    )
    assert any(s.startswith("[HARNESS:PUSH_DISPONIVEL") for s in saidas)
    assert any(s.startswith("[HARNESS:UPGRADE_DISPONIVEL") for s in saidas)


def test_conduct_tty_aceita_na_ordem_push_depois_upgrade():
    from src.core.ports.git import GitPort
    from src.main import conduct_end_session_offers

    seq = []
    git = mock.MagicMock(spec=GitPort)
    git.push.side_effect = lambda repo: seq.append("push")

    conduct_end_session_offers(
        _offers(push=_push(), upgrade=_upgrade()),
        "repo",
        git=git,
        run_upgrade=lambda u: seq.append("upgrade"),
        is_interactive=True,
        asker=lambda _q: True,
        out=lambda _m: None,
    )
    assert seq == ["push", "upgrade"]


def test_conduct_tty_recusa_nao_executa_nada():
    from src.core.ports.git import GitPort
    from src.main import conduct_end_session_offers

    git = mock.MagicMock(spec=GitPort)
    chamou_upgrade = []

    conduct_end_session_offers(
        _offers(push=_push(), upgrade=_upgrade()),
        "repo",
        git=git,
        run_upgrade=lambda u: chamou_upgrade.append(True),
        is_interactive=True,
        asker=lambda _q: False,
        out=lambda _m: None,
    )
    git.push.assert_not_called()
    assert chamou_upgrade == []


def test_conduct_falha_no_push_nao_aborta_upgrade():
    from src.core.ports.git import GitPort
    from src.main import conduct_end_session_offers

    git = mock.MagicMock(spec=GitPort)
    git.push.side_effect = RuntimeError("rede caiu")
    seq = []
    erros = []

    conduct_end_session_offers(
        _offers(push=_push(), upgrade=_upgrade()),
        "repo",
        git=git,
        run_upgrade=lambda u: seq.append("upgrade"),
        is_interactive=True,
        asker=lambda _q: True,
        out=lambda _m: None,
        err=erros.append,
    )
    # push falhou, mas o upgrade ainda foi oferecido e executado (RN-02).
    assert seq == ["upgrade"]
    assert any("push" in e for e in erros)


def test_encerrar_sem_sessao_ativa_nao_dispara_ofertas(tmp_path):
    # D-10: as ofertas só rodam após encerramento com sucesso. Sem sessão ativa,
    # o comando reporta o erro e NÃO emite marcadores de oferta.
    main_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../src/main.py")
    )
    python_bin = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../.venv/bin/python3")
    )
    subprocess.run(["git", "init"], cwd=str(tmp_path), capture_output=True)
    (tmp_path / "harness.toml").write_text('[harness]\nactive_harness = "claude"\n')

    result = subprocess.run(
        [python_bin, main_path, "cmd", "encerrar-sessao"],
        capture_output=True,
        text=True,
        cwd=str(tmp_path),
    )

    assert result.returncode == 0
    assert "Nenhuma sessão ativa" in result.stdout
    assert "[HARNESS:" not in result.stdout


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
