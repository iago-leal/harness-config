#!/usr/bin/env python3
import os
import sys
import argparse
import json

# Adiciona o diretório contendo 'src' ao sys.path para imports absolutos funcionarem de qualquer lugar
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.adapters.fs.local import LocalFileSystemAdapter
from src.adapters.git.subprocess import SubprocessGitAdapter
from src.adapters.process.formatter import HostFormatterAdapter
from src.core.bootstrap.service import BootstrapService, NotAGitRepositoryError
from src.core.formatting.service import FormattingService
from src.core.decisions.service import DecisionService
from src.core.commands.service import CommandService
from src.core.documentation.service import DocumentationService
from src.core.domain.config import CORE_VERSION, load_config

# Helpers de orquestração do encerramento vivem no core (feature 018, D-01) e são
# reexportados aqui: a borda CLI e os scripts finos da skill compartilham a mesma
# fonte, sem duplicar. Reexpostos via `src.main` para compat. dos testes da 014.
from src.core.session.close_flow import (  # noqa: F401
    render_offer_markers,
    conduct_end_session_offers,
    pending_work_paths,
    render_commit_pendente_marker,
    conduct_commit_pendente,
    render_encerramento_nao_versionado_marker,
    conduct_encerramento_nao_versionado,
    render_decisao_pendente_marker,
    conduct_decisao_pendente,
    SessionCloseFlow,
)


def resolve_format_target(arg_path):
    """Resolve o arquivo a formatar.

    Precedência: argumento explícito da CLI; na ausência, o campo
    ``tool_input.file_path`` do JSON que o hook PostToolUse entrega no stdin.
    Retorna ``None`` quando não há alvo (uso manual sem argumento, stdin vazio
    ou payload inválido), caso em que o formatador é um no-op silencioso.
    """
    if arg_path:
        return arg_path
    if sys.stdin.isatty():
        return None
    try:
        raw = sys.stdin.read()
    except Exception:
        return None
    if not raw.strip():
        return None
    try:
        payload = json.loads(raw)
    except Exception:
        return None
    tool_input = payload.get("tool_input") or {}
    return tool_input.get("file_path")


def offer_git_init(repo_path: str) -> bool:
    """Oferece ao usuário inicializar um repositório git em repo_path.

    Retorna True se o usuário aceitar. Em contexto não-interativo (sem TTY),
    retorna False sem perguntar — cabe ao chamador abortar sem instalar nada.
    Espelha a guarda de ``sys.stdin.isatty()`` usada em ``resolve_format_target``.
    """
    if not sys.stdin.isatty():
        return False
    resposta = input(
        f"Não há repositório git em '{repo_path}'. "
        "Inicializar agora com 'git init'? [s/N] "
    )
    return resposta.strip().lower() in ("s", "sim", "y", "yes")


def build_parser() -> argparse.ArgumentParser:
    """Configura e retorna o parser de argumentos CLI do Harness Core."""
    parser = argparse.ArgumentParser(description=f"Harness Core CLI v{CORE_VERSION}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # 1. Comando: bootstrap
    subparsers.add_parser(
        "bootstrap", help="Instala ganchos Git locais (pre-commit e post-merge)"
    )

    # 2. Comando: format
    parser_format = subparsers.add_parser(
        "format", help="Formata um arquivo específico"
    )
    parser_format.add_argument(
        "file_path",
        nargs="?",
        help="Caminho do arquivo a formatar. Se omitido, é lido do JSON do hook PostToolUse no stdin (tool_input.file_path).",
    )

    # 3. Comando: decisions
    parser_decisions = subparsers.add_parser(
        "decisions",
        help=(
            "Valida e indexa microdecisões Markdown. Com --gate (hook Stop do "
            "Claude), também avalia pendência de registro: trabalho substantivo "
            "sem ficha MD-NNNN gera um aviso em stderr, único por sessão, sem "
            "bloquear o turno (desativável por decisions.require_registration)."
        ),
    )
    parser_decisions.add_argument(
        "--gate",
        action="store_true",
        help=(
            "Modo hook Stop: toda a saída (informativos e o aviso de registro) "
            "vai para stderr; o stdout fica sempre vazio (exit 0 sempre)."
        ),
    )

    # 4. Comando: cmd
    parser_cmd = subparsers.add_parser(
        "cmd",
        help=(
            "Executa um slash command de sessão. `resume` reinjeta o estado de "
            ".harness/estado-da-sessao.md no contexto do harness ativo (JSON no "
            "stdout para Claude/Gemini; arquivo para Antigravity). No Claude, o "
            "resume também anexa a visão compacta de decisões "
            "(.harness/decisoes-recentes.md; fallback para o índice completo) "
            "para ancorar a busca do agente, desativável por "
            "session.inject_decisions_index."
        ),
    )
    parser_cmd.add_argument(
        "cmd_name",
        help="Nome do comando (ex: encerrar-sessao, resume, handoff, clarificar)",
    )
    parser_cmd.add_argument(
        "cmd_args", nargs="*", help="Argumentos opcionais do comando"
    )
    parser_cmd.add_argument(
        "--sem-decisao",
        action="store_true",
        dest="sem_decisao",
        help=(
            "Só para encerrar-sessao: declara que não houve decisão não óbvia "
            "nesta sessão (satisfaz o gate de registro; a declaração fica "
            "registrada na narrativa do estado de sessão)."
        ),
    )
    # Feature 024: consentimento para escrita no git ao encerrar. Os textos de
    # --help dizem a CONSEQUÊNCIA, não o efeito mecânico, e são idênticos ao
    # script fino da skill (paridade RN-N33).
    parser_cmd.add_argument(
        "--com-pendencias",
        action="store_true",
        dest="com_pendencias",
        help=(
            "Só para encerrar-sessao: encerra mesmo havendo trabalho não "
            "commitado (a declaração fica registrada na narrativa)."
        ),
    )
    grupo_commit_encerramento = parser_cmd.add_mutually_exclusive_group()
    grupo_commit_encerramento.add_argument(
        "--com-commit-encerramento",
        action="store_true",
        dest="com_commit_encerramento",
        help=(
            "Só para encerrar-sessao: autoriza versionar o estado de sessão ao "
            "encerrar. Sem terminal interativo, sem esta flag o estado não é "
            "versionado."
        ),
    )
    grupo_commit_encerramento.add_argument(
        "--sem-commit-encerramento",
        action="store_true",
        dest="sem_commit_encerramento",
        help=(
            "Só para encerrar-sessao: encerra sem versionar o estado de sessão; "
            "ele fica como mudança pendente no working tree."
        ),
    )

    # 5. Comando: doc-gen
    subparsers.add_parser("doc-gen", help="Gera o arquivo HTML de documentação local")

    # 6. Comando: doc-serve
    parser_doc_serve = subparsers.add_parser(
        "doc-serve", help="Inicia o servidor HTTP local da documentação"
    )
    parser_doc_serve.add_argument(
        "--port", type=int, default=8000, help="Porta para o servidor (padrão: 8000)"
    )

    # 7. Comando: install-prompt
    subparsers.add_parser(
        "install-prompt",
        help="Imprime o prompt de instalação colável no agente",
    )

    # 8. Comando: init
    parser_init = subparsers.add_parser(
        "init",
        help="Inicializa um projeto de destino com o Harness (fonte única: shim que executa o core do upstream)",
    )
    parser_init.add_argument("target_path", help="Caminho do repositório de destino")
    parser_init.add_argument(
        "--harness",
        choices=["claude", "gemini", "antigravity"],
        default="claude",
        help="Harness ativo no destino (padrão: claude)",
    )

    # 9. Comando: upgrade
    parser_upgrade = subparsers.add_parser(
        "upgrade",
        help="Atualiza a instalação do Harness Core no projeto a partir do upstream configurado",
    )
    parser_upgrade.add_argument(
        "--force",
        action="store_true",
        help="Ignora a comparação de versão e força recópia + rematerialização do core",
    )

    # 10. Comando: agy-hook
    parser_agy_hook = subparsers.add_parser(
        "agy-hook",
        help=(
            "Driver de borda dos ganchos do Antigravity. Lê o payload JSON no "
            "stdin e emite o JSON exigido por evento no stdout (não-bloqueante)."
        ),
    )
    parser_agy_hook.add_argument(
        "event",
        choices=["pre-tool-use", "post-tool-use", "stop"],
        help="Evento do ciclo de vida do Antigravity a tratar",
    )

    # 11. Comando: materialize (interno)
    # Materializa os artefatos de IDE (slash commands de sessão; hooks.json do
    # Antigravity) sob o projeto atual com o código LOCAL. O `upgrade` o invoca
    # via subprocesso do python de destino para rematerializar com o código
    # recém-copiado, nunca com os módulos antigos em memória (feature 012).
    # Também é útil avulso para recriar os artefatos sem um upgrade completo.
    subparsers.add_parser(
        "materialize",
        help="(interno) Materializa os artefatos de IDE do projeto atual com o código local",
    )

    # 12. Comando: migrate (feature 020)
    parser_migrate = subparsers.add_parser(
        "migrate",
        help="Converte as instalações sob uma raiz do layout copiado para a fonte única (shim + core do upstream)",
    )
    parser_migrate.add_argument(
        "root",
        nargs="?",
        default=os.path.expanduser("~/dev"),
        help="Raiz que contém as instalações a migrar (padrão: ~/dev)",
    )
    parser_migrate.add_argument(
        "--dry-run",
        action="store_true",
        help="Apenas relata o que faria (espaço a liberar, ações), sem escrever nem remover",
    )

    # 13. Comando: progress (feature 026)
    parser_progress = subparsers.add_parser(
        "progress",
        help=(
            "Mede o progresso dos entregáveis (ciclo forward + harness) e regrava "
            "o artefato derivado quando o estado mudou"
        ),
    )
    grupo_progress = parser_progress.add_mutually_exclusive_group()
    grupo_progress.add_argument(
        "--json",
        dest="json_mode",
        action="store_true",
        help="Emite a medição em JSON no stdout (com aferido_em), sem tocar o artefato",
    )
    grupo_progress.add_argument(
        "--em-hook",
        dest="em_hook",
        action="store_true",
        help=(
            "Modo pre-commit: regrava o artefato defasado e falha (exit 1) para o "
            "commit incluí-lo; alerta grave vira aviso, nunca bloqueio"
        ),
    )

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    # Instanciação dos adaptadores físicos
    fs = LocalFileSystemAdapter()
    git = SubprocessGitAdapter()
    process = HostFormatterAdapter()

    # Carrega configurações (via única tipada — feature 006 removeu o dict legado).
    # Pulado para `agy-hook`: o gancho de borda precisa carregar a config dentro do
    # seu próprio try/except não-bloqueante, para que um harness.toml malformado não
    # escape como traceback antes do ramo. `init`/`upgrade` também não usam esta
    # config (recarregam o que precisam internamente).
    config = None
    if args.command not in ("init", "upgrade", "agy-hook", "materialize", "migrate"):
        config = load_config(fs)

    # Alerta de atualização passiva
    if (
        args.command not in ("init", "upgrade", "agy-hook", "materialize", "migrate")
        and config.harness.upstream_path
    ):
        from src.core.domain.layout import SYNC_CACHE_REL_PATH
        from src.core.sync.service import SyncService

        sync_service = SyncService(fs, git, SYNC_CACHE_REL_PATH)
        new_ver = sync_service.check_version_update(
            config.harness.version, config.harness.upstream_path
        )
        if new_ver:
            print(
                f"\n⚠️  Aviso: Uma nova versão do Harness Core ({new_ver}) está disponível no upstream.\n"
                f"   Execute './harness upgrade' para atualizar seu núcleo local.\n",
                file=sys.stderr,
            )

    # Execução das sub-ações da CLI
    if args.command == "bootstrap":
        service = BootstrapService(fs)
        cwd = os.getcwd()
        if not fs.exists(os.path.join(cwd, ".git")):
            # Sem repositório git: oferece a inicialização em vez de instalar
            # cegamente e criar um .git/hooks órfão.
            if not offer_git_init(cwd):
                print(
                    f"Erro: '{cwd}' não é um repositório git. "
                    "Os hooks não foram instalados. Inicialize o repositório "
                    "('git init') e rode novamente.",
                    file=sys.stderr,
                )
                sys.exit(1)
            git.init_repo(cwd)
            print(f"Repositório git inicializado em '{cwd}'.")
        try:
            installed = service.install_hooks(cwd)
        except NotAGitRepositoryError as e:
            print(f"Erro: {e}", file=sys.stderr)
            sys.exit(1)
        print(
            f"Sucesso: Hooks Git instalados com sucesso. Arquivos: {', '.join(installed)}"
        )
        sys.exit(0)

    elif args.command == "format":
        config = load_config(fs)
        service = FormattingService(fs, process, config)
        file_path = resolve_format_target(args.file_path)
        if not file_path:
            sys.exit(0)
        sys.exit(service.format_file(file_path))

    elif args.command == "decisions":
        service = DecisionService(fs)
        config = load_config(fs)
        decisoes_dir = config.decisions.dir
        output_file = config.decisions.index_file
        header_file = config.decisions.header_file

        # Sob --gate (hook Stop do Claude, feature 022/D-09), o stdout é
        # reservado ao JSON do hook: informativos migram para stderr e o exit é
        # sempre 0 (padrão não-bloqueante dos ganchos). Sem a flag, o
        # comportamento permanece byte-idêntico (uso manual e git post-merge,
        # MD-0006).
        gate_mode = args.gate
        info = (lambda m: print(m, file=sys.stderr)) if gate_mode else print

        try:
            decisions = service.load_decisions(decisoes_dir)
            errors = service.validate_integrity(decisions)

            if errors:
                info("Erros de integridade encontrados no grafo de decisões:")
                for err in errors:
                    info(f" - {err}")
                if not gate_mode:
                    sys.exit(1)
            else:
                info("Grafo de microdecisões validado com sucesso (zero erros).")
                # Compila o índice consolidado e, na MESMA passada, a visão
                # compacta que o `cmd resume` injeta no SessionStart (028/D-01).
                service.compile_index(decisions, output_file, header_file)
                service.compile_compact_view(
                    decisions,
                    config.decisions.compact_file,
                    output_file,
                    decisoes_dir,
                    config.decisions.compact_index_size,
                )
                info(f"Índice de decisões compilado com sucesso em '{output_file}'.")
                info(
                    f"Visão compacta derivada em '{config.decisions.compact_file}'."
                )
            if not gate_mode:
                sys.exit(0)
        except Exception as e:
            info(f"Erro ao processar microdecisões: {e}")
            if not gate_mode:
                sys.exit(1)

        # Gate de registro (022→025): advisory em stderr, no máximo UM por
        # sessão (023: identidade grossa — a âncora — persistida no estado; a
        # identidade fina fica com o portão do encerramento). O stdout fica
        # sempre vazio: nenhum JSON de controle alcança o runner de hooks
        # (MD-0018 aposentou o soft-block das MD-0015/0016).
        # Qualquer falha interna avisa em stderr e libera o turno.
        try:
            from src.core.decisions.gate import evaluate_registration_gate

            cmd_service = CommandService(fs, git)
            session = cmd_service.load_session(config.session.state_file)
            if (
                config.decisions.require_registration
                and session is not None
                and session.is_active
            ):
                verdict = evaluate_registration_gate(git, os.getcwd(), session, config)
                if verdict.aviso:
                    print(f"Aviso: {verdict.aviso}", file=sys.stderr)
                if (
                    verdict.pendente
                    and session.gate_lembrete_fingerprint
                    != verdict.fingerprint_lembrete
                ):
                    session.gate_lembrete_fingerprint = verdict.fingerprint_lembrete
                    cmd_service.save_session(config.session.state_file, session)
                    aviso = (
                        "Aviso: "
                        + render_decisao_pendente_marker(verdict.mudancas)
                        + " Registre a decisão como ficha MD-NNNN em "
                        + f"{decisoes_dir}/ (ou declare a ausência ao encerrar "
                        "com --sem-decisao)."
                    )
                    print(aviso, file=sys.stderr)
        except Exception as e:
            print(
                f"Aviso: gate de registro (não-bloqueante) falhou: {e}",
                file=sys.stderr,
            )
        sys.exit(0)

    elif args.command == "cmd":
        from src.core.session.sinks import get_sink
        from src.core.session.errors import MalformedSessionStateError
        from src.core.session.resume_context import build_decisions_appendix

        service = CommandService(fs, git)
        session_file = config.session.state_file
        cmd_name_norm = args.cmd_name.strip().lower().lstrip("/")

        # Subcomando `regen` (016): regenera os artefatos derivados declarados em
        # [regen]. Não passa pelo CommandService (depende do ProcessPort, não de
        # git); ausente → no-op exit 0; falha do comando → exit ≠ 0 (barulhento),
        # de modo que o fluxo "faz tudo" aborte antes de fechar.
        if cmd_name_norm == "regen":
            from src.core.regen.service import RegenService

            code, message = RegenService(process).run(config, os.getcwd())
            print(message, file=(sys.stdout if code == 0 else sys.stderr))
            sys.exit(code)

        # Encerrar-sessao: delega ao fluxo único do core (feature 018, D-01), que
        # também alimenta os scripts finos da skill — fonte única, sem duplicar a
        # orquestração (pré-check de pendência → fechamento → ofertas).
        if cmd_name_norm == "encerrar-sessao":
            # Tri-estado do commit de encerramento a partir das flags exclusivas
            # (024): ausência das duas → None (default resolvido pela borda).
            versionar_encerramento = None
            if args.com_commit_encerramento:
                versionar_encerramento = True
            elif args.sem_commit_encerramento:
                versionar_encerramento = False
            sys.exit(
                SessionCloseFlow(fs, git, process).run(
                    os.getcwd(),
                    config,
                    sem_decisao=args.sem_decisao,
                    com_pendencias=args.com_pendencias,
                    versionar_encerramento=versionar_encerramento,
                )
            )

        # Demais comandos de sessão (resume, handoff, clarificar).
        try:
            result_msg = service.execute_command(
                command=args.cmd_name,
                args=args.cmd_args,
                repo_path=os.getcwd(),
                session_filepath=session_file,
            )
        except MalformedSessionStateError as exc:
            # Boot (resume) é não-bloqueante: estado malformado não pode travar o
            # SessionStart do agente — aviso em stderr e exit 0. Comando explícito
            # falha barulhento (exit != 0): nunca um falso sucesso (RN-N4/RN-04).
            print(
                f"Aviso: estado de sessão malformado em {session_file}: {exc}",
                file=sys.stderr,
            )
            if cmd_name_norm == "resume":
                sys.exit(0)
            print(
                "Comando abortado: corrija a âncora do estado de sessão em "
                f"{session_file} para um SHA-1 de 40 caracteres e tente de novo.",
                file=sys.stderr,
            )
            sys.exit(1)

        # Só o `resume` alimenta o SessionStart: entrega via sink do harness ativo.
        # Os demais comandos (handoff, clarificar) imprimem normal.
        if cmd_name_norm == "resume":
            # Feature 021 (→028): no Claude, ancora a busca do agente anexando a
            # visão COMPACTA de decisões ao estado reinjetado; o índice integral
            # vira consulta sob demanda e só entra como fallback autoresolvente
            # (janela entre o upgrade e a primeira reindexação). O gate por
            # harness vive na borda (RN-N5); a composição é pura. Não-bloqueante:
            # fonte ausente → aviso em stderr e segue.
            enabled = (
                config.harness.active_harness == "claude"
                and config.session.inject_decisions_index
            )
            if enabled and not fs.exists(config.decisions.compact_file):
                if fs.exists(config.decisions.index_file):
                    print(
                        f"Aviso: visão compacta ainda não derivada em "
                        f"{config.decisions.compact_file}; injetando o índice "
                        "completo (rode ./harness decisions ou aguarde o "
                        "próximo fim de turno).",
                        file=sys.stderr,
                    )
                else:
                    print(
                        f"Aviso: índice de decisões ausente em "
                        f"{config.decisions.index_file}; reinjetando só o estado.",
                        file=sys.stderr,
                    )
            result_msg += build_decisions_appendix(
                fs,
                config.decisions.index_file,
                enabled,
                compact_file=config.decisions.compact_file,
            )
            sink = get_sink(config.harness.active_harness, fs)
            sink.emit(result_msg)
        else:
            print(result_msg)

        sys.exit(0)

    elif args.command == "doc-gen":
        service = DocumentationService(fs)
        # Localiza o diretório do script atual para montar os caminhos relativos ao projeto
        base_dir = os.path.dirname(os.path.abspath(__file__))
        template_path = os.path.join(base_dir, "core", "documentation", "template.html")
        domain_path = "_reversa_sdd/domain.md"
        state_path = ".reversa/state.json"
        output_path = "harness-docs.html"

        try:
            parser_for_introspect = build_parser()
            service.generate_html(
                parser=parser_for_introspect,
                template_path=template_path,
                domain_path=domain_path,
                state_path=state_path,
                output_path=output_path,
            )
            print(f"Sucesso: Documentação compilada e salva em '{output_path}'.")
            sys.exit(0)
        except Exception as e:
            print(f"Erro ao gerar documentação: {e}")
            sys.exit(1)

    elif args.command == "doc-serve":
        port = args.port
        output_path = "harness-docs.html"

        if not fs.exists(output_path):
            print(f"Aviso: '{output_path}' não encontrado. Gerando antes de iniciar...")
            service = DocumentationService(fs)
            base_dir = os.path.dirname(os.path.abspath(__file__))
            template_path = os.path.join(
                base_dir, "core", "documentation", "template.html"
            )
            domain_path = "_reversa_sdd/domain.md"
            state_path = ".reversa/state.json"
            try:
                parser_for_introspect = build_parser()
                service.generate_html(
                    parser=parser_for_introspect,
                    template_path=template_path,
                    domain_path=domain_path,
                    state_path=state_path,
                    output_path=output_path,
                )
            except Exception as e:
                print(f"Erro ao gerar documentação inicial: {e}")
                sys.exit(1)

        import http.server
        import socketserver

        class SafeHandler(http.server.SimpleHTTPRequestHandler):
            def do_GET(self):
                if self.path == "/" or self.path == "/index.html":
                    self.path = "/harness-docs.html"
                return super().do_GET()

        try:
            socketserver.TCPServer.allow_reuse_address = True
            with socketserver.TCPServer(("", port), SafeHandler) as httpd:
                print(
                    f"Servidor HTTP local da documentação iniciado em http://localhost:{port}"
                )
                print("Pressione Ctrl+C para encerrar.")
                httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServidor HTTP encerrado de forma amigável.")
            sys.exit(0)
        except Exception as e:
            print(f"Erro ao iniciar o servidor HTTP: {e}")
            sys.exit(1)

    elif args.command == "install-prompt":
        from src.core.install.service import InstallPromptService

        cfg = load_config(fs)
        service = InstallPromptService(fs)
        print(service.render(cfg.harness.active_harness, build_parser()))
        sys.exit(0)

    elif args.command == "init":
        from src.core.bootstrap.init_service import InitializationService

        service = InitializationService(fs, process)
        try:
            service.initialize_project(args.target_path, args.harness)
            print(
                f"Sucesso: Projeto em '{args.target_path}' inicializado com Harness Core."
            )
            sys.exit(0)
        except Exception as e:
            print(f"Erro ao inicializar projeto: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.command == "upgrade":
        from src.core.bootstrap.init_service import InitializationService

        service = InitializationService(fs, process)
        try:
            service.upgrade_project(os.getcwd(), force=args.force)
            print("Sucesso: Harness Core atualizado com sucesso a partir do upstream.")
            sys.exit(0)
        except Exception as e:
            print(f"Erro ao atualizar Harness Core: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.command == "materialize":
        from src.core.install.local_apply import apply_local_materializers

        cfg = load_config(fs)
        target = os.getcwd()
        try:
            apply_local_materializers(
                fs, target, os.path.abspath(target), cfg.harness.active_harness
            )
            print("Sucesso: Artefatos de IDE materializados com o código local.")
            sys.exit(0)
        except Exception as e:
            print(f"Erro ao materializar artefatos de IDE: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.command == "migrate":
        from src.core.migrate.service import MigrateService

        # O upstream a partir do qual ESTE core roda: 4 níveis acima de main.py
        # (src → harness-core → .harness → <upstream>). Nunca é migrado (guarda).
        upstream_self = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        )
        results = MigrateService(fs).migrate(
            args.root, dry_run=args.dry_run, upstream_self=upstream_self
        )
        prefixo = "[dry-run] " if args.dry_run else ""
        migrated = 0
        for r in results:
            if r["status"] == "migrated":
                migrated += 1
                alvo = ", ".join(r["removed"]) or "—"
                print(f"{prefixo}migrado: {r['project']} (removido: {alvo})")
            elif r["status"] == "would-migrate":
                alvo = ", ".join(r["removes"]) or "—"
                print(f"{prefixo}migraria: {r['project']} (removeria: {alvo})")
            else:
                print(f"{prefixo}pulado: {r['project']} — {r.get('reason', '')}")
        print(
            f"{prefixo}{len(results)} instalação(ões) avaliada(s); {migrated} migrada(s)."
        )
        sys.exit(0)

    elif args.command == "progress":
        from datetime import datetime

        from src.core.progress.render import render_json, render_markdown
        from src.core.progress.service import ProgressService

        medicao = ProgressService(fs, git).measure(os.getcwd(), config)
        for aviso in medicao.avisos:
            print(f"Aviso: {aviso}", file=sys.stderr)
        if medicao.falhas:
            # Falha REAL de leitura (fonte presente mas ilegível): não regrava o
            # artefato, para não sobrescrever medição boa com medição degradada.
            for falha in medicao.falhas:
                print(f"Erro de leitura: {falha}", file=sys.stderr)
            sys.exit(2)

        if args.json_mode:
            print(render_json(medicao, datetime.now().astimezone().isoformat()))
            sys.exit(0)

        target = config.progress.file
        novo = render_markdown(medicao)
        atual = fs.read_file(target) if fs.exists(target) else None

        if args.em_hook:
            if atual is None and not fs.exists(".reversa"):
                # Instalação sem Reversa e sem artefato prévio: nada a vigiar.
                sys.exit(0)
            if novo != atual:
                pai = os.path.dirname(target)
                if pai and not fs.exists(pai):
                    fs.makedirs(pai)
                fs.write_file_atomic(target, novo)
                print(
                    f"{target} estava defasado e foi regravado. Confira e repita "
                    f"o commit: git add {target} && git commit",
                    file=sys.stderr,
                )
                sys.exit(1)
            for alerta in medicao.alertas:
                if alerta.severidade == "alta":
                    print(
                        f"Aviso: [{alerta.severidade}] {alerta.origem}: "
                        f"{alerta.mensagem}",
                        file=sys.stderr,
                    )
            sys.exit(0)

        if novo != atual:
            pai = os.path.dirname(target)
            if pai and not fs.exists(pai):
                fs.makedirs(pai)
            fs.write_file_atomic(target, novo)
            print(f"{target} regravado.")
        else:
            print(f"{target} já estava em dia.")

        if medicao.board_habilitado:
            # Exportador kanban (027): segundo artefato derivado, só no modo
            # padrão e por opt-in. Board ilegível nunca chega aqui — vira
            # falha real na medição e o comando já saiu com 2 lá em cima.
            from src.core.progress.kanban import render_board

            board_path = config.progress.kanban.file
            board_atual = fs.read_file(board_path) if fs.exists(board_path) else None
            board_novo = render_board(medicao, board_atual)
            if board_novo != board_atual:
                pai = os.path.dirname(board_path)
                if pai and not fs.exists(pai):
                    fs.makedirs(pai)
                fs.write_file_atomic(board_path, board_novo)
                print(f"{board_path} regravado.")
            else:
                print(f"{board_path} já estava em dia.")
        sys.exit(0)

    elif args.command == "agy-hook":
        # Driver de borda do Antigravity. Constrói os mesmos adaptadores concretos
        # já usados pela CLI e delega ao adaptador, que fala o protocolo de ganchos
        # e emite o stdout JSON exigido por evento (sempre não-bloqueante, exit 0).
        #
        # Garantia não-bloqueante de borda: TODO o ramo — resolução de config,
        # leitura do stdin, construção dos serviços/bridge e a delegação — roda
        # sob try/except. O fallback exigido por evento é pré-computado a partir
        # de `args.event` (já validado pelo argparse) ANTES de qualquer operação
        # que possa lançar, de modo que config corrompida/parcial, stdin ilegível
        # ou qualquer outra falha ainda emite o stdout exigido e encerra com 0.
        fallback = '{"decision": "allow"}' if args.event == "pre-tool-use" else "{}"
        try:
            from src.adapters.antigravity.hook_bridge import AntigravityHookBridge

            agy_config = load_config(fs)
            formatting_service = FormattingService(fs, process, agy_config)
            decision_service = DecisionService(fs)

            def gate_evaluator():
                # Advisory do gate de registro (022): montado na borda para o
                # bridge permanecer sem git/config. Sem sessão ativa ou com o
                # gate desligado, não há veredito (None → silêncio).
                from src.core.decisions.gate import evaluate_registration_gate

                if not agy_config.decisions.require_registration:
                    return None
                session = CommandService(fs, git).load_session(
                    agy_config.session.state_file
                )
                if session is None or not session.is_active:
                    return None
                return evaluate_registration_gate(git, os.getcwd(), session, agy_config)

            bridge = AntigravityHookBridge(
                fs=fs,
                formatting_service=formatting_service,
                decision_service=decision_service,
                decisions_dir=agy_config.decisions.dir,
                decisions_index_file=agy_config.decisions.index_file,
                decisions_header_file=agy_config.decisions.header_file,
                gate_evaluator=gate_evaluator,
                decisions_compact_file=agy_config.decisions.compact_file,
                decisions_compact_size=agy_config.decisions.compact_index_size,
            )

            stdin_text = "" if sys.stdin.isatty() else sys.stdin.read()
            print(bridge.handle(args.event, stdin_text))
        except Exception as exc:
            print(
                f"Aviso: gancho agy-hook {args.event!r} falhou de forma "
                f"não-bloqueante: {exc}",
                file=sys.stderr,
            )
            print(fallback)
        sys.exit(0)


if __name__ == "__main__":
    main()
