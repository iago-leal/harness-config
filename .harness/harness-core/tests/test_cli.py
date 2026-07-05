import json
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


def test_encerrar_sem_sessao_e_noop_silencioso(tmp_path):
    # 016/D1: sem estado de sessão, encerrar é no-op RUIDOSO (exit 0), sem fechar
    # nem emitir marcadores. Reverte a falha barulhenta da 015 para o caso ausente.
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
    assert "Nenhuma sessão" in result.stdout
    assert "[HARNESS:" not in result.stdout


def test_cli_materialize_writes_session_skill(tmp_path):
    # Feature 012 (Modo 1, código real) + 018: o subcomando interno `materialize`,
    # rodado como o upgrade o invocaria no destino, produz a SKILL de sessão a
    # partir do CÓDIGO LOCAL — prova de que a materialização não é stale.
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
    skill_dir = tmp_path / ".claude" / "skills" / "encerrar-sessao"
    assert (skill_dir / "SKILL.md").exists()
    assert (skill_dir / "scripts" / "encerrar_sessao.py").exists()


def _harness_cli_paths():
    main_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../src/main.py")
    )
    python_bin = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../.venv/bin/python3")
    )
    return main_path, python_bin


def _seed_session_repo(tmp_path, commit, status):
    """Repo git com harness.toml e um estado de sessão escrito como TEXTO bruto.

    Escrever direto (sem o serializer) permite reproduzir o estado legado de hash
    curto, que o modelo `SessionState` atual recusaria.
    """
    subprocess.run(["git", "init"], cwd=str(tmp_path), capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "t@t.t"], cwd=str(tmp_path), capture_output=True
    )
    subprocess.run(
        ["git", "config", "user.name", "t"], cwd=str(tmp_path), capture_output=True
    )
    (tmp_path / "harness.toml").write_text('[harness]\nactive_harness = "claude"\n')
    estado = tmp_path / ".harness" / "estado-da-sessao.md"
    estado.parent.mkdir(parents=True, exist_ok=True)
    estado.write_text(
        f"---\ncommit: {commit}\nfeature: feat-1\n"
        f"start_time: 2026-06-01T10:00:00+00:00\nstatus: {status}\n---\n\n"
        "## O que foi feito\n- x\n"
    )
    return estado


def test_encerrar_hash_curto_falha_barulhento(tmp_path):
    # Estado legado de hash curto (anterior à validação de 40 chars): o encerrar
    # EXPLÍCITO falha barulhento (exit != 0), nunca no-op com exit 0 (RN-01/RN-04).
    main_path, python_bin = _harness_cli_paths()
    _seed_session_repo(tmp_path, "abc1234", "active")

    result = subprocess.run(
        [python_bin, main_path, "cmd", "encerrar-sessao"],
        capture_output=True,
        text=True,
        cwd=str(tmp_path),
    )

    assert result.returncode != 0
    assert "estado-da-sessao.md" in result.stderr
    assert "[HARNESS:" not in result.stdout


def test_encerrar_sessao_inativa_reativa_e_fecha(tmp_path):
    # 016/D1/D3: sessão válida porém inativa → reativa, fecha e commita num passo
    # (exit 0), anunciando a reativação. Reverte a falha barulhenta da 015.
    main_path, python_bin = _harness_cli_paths()
    _seed_session_repo(tmp_path, "a" * 40, "inactive")
    # Limpa a working tree para não disparar o pré-check de trabalho pendente.
    subprocess.run(["git", "add", "-A"], cwd=str(tmp_path), capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "seed"], cwd=str(tmp_path), capture_output=True
    )

    result = subprocess.run(
        [python_bin, main_path, "cmd", "encerrar-sessao"],
        capture_output=True,
        text=True,
        cwd=str(tmp_path),
    )

    assert result.returncode == 0
    assert "Sessão encerrada com sucesso" in result.stdout
    assert "reativ" in result.stdout.lower()


def test_encerrar_com_trabalho_solto_emite_marker_e_nao_fecha(tmp_path):
    # 016/RN-03: trabalho solto fora de .harness/ → marker COMMIT_PENDENTE e o
    # fechamento NÃO ocorre (early return, exit 0). A sessão segue ativa.
    main_path, python_bin = _harness_cli_paths()
    estado = _seed_session_repo(tmp_path, "a" * 40, "active")
    subprocess.run(["git", "add", "-A"], cwd=str(tmp_path), capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "seed"], cwd=str(tmp_path), capture_output=True
    )
    # Trabalho não commitado fora de .harness/
    (tmp_path / "trabalho.txt").write_text("rascunho")

    result = subprocess.run(
        [python_bin, main_path, "cmd", "encerrar-sessao"],
        capture_output=True,
        text=True,
        cwd=str(tmp_path),
    )

    assert result.returncode == 0
    assert "[HARNESS:COMMIT_PENDENTE" in result.stdout
    assert "trabalho.txt" in result.stdout
    # Não fechou: o estado permanece ativo.
    assert "status: active" in estado.read_text()


def test_cmd_regen_runs_configured_command(tmp_path):
    # 016/RF-02: cmd regen executa o comando declarado em [regen].
    main_path, python_bin = _harness_cli_paths()
    (tmp_path / "harness.toml").write_text(
        '[harness]\nactive_harness = "claude"\n\n[regen]\ncommand = "touch regen_marker.txt"\n'
    )

    result = subprocess.run(
        [python_bin, main_path, "cmd", "regen"],
        capture_output=True,
        text=True,
        cwd=str(tmp_path),
    )

    assert result.returncode == 0
    assert (tmp_path / "regen_marker.txt").exists()


def test_cmd_regen_absent_is_noop(tmp_path):
    # 016/RF-02: sem [regen], cmd regen é no-op (exit 0).
    main_path, python_bin = _harness_cli_paths()
    (tmp_path / "harness.toml").write_text('[harness]\nactive_harness = "claude"\n')

    result = subprocess.run(
        [python_bin, main_path, "cmd", "regen"],
        capture_output=True,
        text=True,
        cwd=str(tmp_path),
    )

    assert result.returncode == 0


def test_cmd_regen_failure_is_loud(tmp_path):
    # 016/RF-03: comando de regen com exit != 0 → cmd regen falha barulhento.
    main_path, python_bin = _harness_cli_paths()
    (tmp_path / "harness.toml").write_text(
        '[harness]\nactive_harness = "claude"\n\n[regen]\ncommand = "exit 3"\n'
    )

    result = subprocess.run(
        [python_bin, main_path, "cmd", "regen"],
        capture_output=True,
        text=True,
        cwd=str(tmp_path),
    )

    assert result.returncode != 0


def test_resume_sobre_estado_malformado_nao_bloqueia(tmp_path):
    # Boot (resume) é não-bloqueante: estado malformado não pode travar o
    # SessionStart — exit 0 (RN-02/RF-02), mesmo com o encerrar endurecido.
    main_path, python_bin = _harness_cli_paths()
    _seed_session_repo(tmp_path, "abc1234", "active")

    result = subprocess.run(
        [python_bin, main_path, "cmd", "resume"],
        capture_output=True,
        text=True,
        cwd=str(tmp_path),
    )

    assert result.returncode == 0


# --- Resume ancora no índice de decisões (feature 021) --------------------


def _seed_resume_repo(tmp_path, harness_toml):
    """Repo git com HEAD real (commit), estado de sessão válido e harness.toml
    fornecido. HEAD real evita que `git rev-parse HEAD` falhe no resume."""
    _seed_session_repo(tmp_path, "a" * 40, "active")
    (tmp_path / "harness.toml").write_text(harness_toml)
    subprocess.run(["git", "add", "-A"], cwd=str(tmp_path), capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "seed"], cwd=str(tmp_path), capture_output=True
    )


def _resume_context(tmp_path):
    main_path, python_bin = _harness_cli_paths()
    result = subprocess.run(
        [python_bin, main_path, "cmd", "resume"],
        capture_output=True,
        text=True,
        cwd=str(tmp_path),
    )
    return result


def test_resume_anexa_indice_no_claude(tmp_path):
    # Claude + flag padrão (on): o additionalContext traz o índice de decisões.
    _seed_resume_repo(tmp_path, '[harness]\nactive_harness = "claude"\n')
    (tmp_path / ".harness" / "microdecisoes.md").write_text(
        "- **MD-0001** — Decisão de teste\n"
    )

    result = _resume_context(tmp_path)
    assert result.returncode == 0
    ctx = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]
    assert "MD-0001" in ctx
    assert "Índice de decisões" in ctx


def test_resume_flag_off_suprime_indice(tmp_path):
    # inject_decisions_index = false: só o estado, sem o índice.
    _seed_resume_repo(
        tmp_path,
        '[harness]\nactive_harness = "claude"\n\n'
        "[session]\ninject_decisions_index = false\n",
    )
    (tmp_path / ".harness" / "microdecisoes.md").write_text(
        "- **MD-0001** — Decisão de teste\n"
    )

    result = _resume_context(tmp_path)
    assert result.returncode == 0
    ctx = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]
    assert "MD-0001" not in ctx


def test_resume_gemini_nao_anexa_indice(tmp_path):
    # Corte Claude-first (gate D-04): Gemini usa o mesmo sink, mas não recebe o
    # apêndice nesta iteração.
    _seed_resume_repo(tmp_path, '[harness]\nactive_harness = "gemini"\n')
    (tmp_path / ".harness" / "microdecisoes.md").write_text(
        "- **MD-0001** — Decisão de teste\n"
    )

    result = _resume_context(tmp_path)
    assert result.returncode == 0
    ctx = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]
    assert "MD-0001" not in ctx


def test_resume_indice_ausente_nao_trava(tmp_path):
    # Não-bloqueio (RN-03/RN-N4): índice ausente → aviso em stderr, resume segue
    # com o estado e exit 0.
    _seed_resume_repo(tmp_path, '[harness]\nactive_harness = "claude"\n')
    # Sem .harness/microdecisoes.md.

    result = _resume_context(tmp_path)
    assert result.returncode == 0
    assert "microdecisoes" in result.stderr
    ctx = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]
    assert "Sessão retomada" in ctx
