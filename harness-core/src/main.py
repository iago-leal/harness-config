#!/usr/bin/env python3
import os
import sys
import argparse
import toml

# Adiciona o diretório contendo 'src' ao sys.path para imports absolutos funcionarem de qualquer lugar
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.adapters.fs.local import LocalFileSystemAdapter
from src.adapters.git.subprocess import SubprocessGitAdapter
from src.adapters.process.formatter import HostFormatterAdapter
from src.core.bootstrap.service import BootstrapService
from src.core.formatting.service import FormattingService
from src.core.decisions.service import DecisionService
from src.core.commands.service import CommandService
from src.core.documentation.service import DocumentationService


def load_harness_config(fs: LocalFileSystemAdapter) -> dict:
    """Carrega as configurações do harness.toml se existir."""
    default_config = {
        "harness": {"active_harness": "claude"},
        "formatting": {"exclude_paths": [], "opt_out_file": ".no-autoformat"},
        "sync": {"cache_ttl_hours": 24, "remote_check_enabled": True},
    }
    config_file = "harness.toml"
    if fs.exists(config_file):
        try:
            content = fs.read_file(config_file)
            user_config = toml.loads(content)
            # Merge simples
            for section in default_config:
                if section in user_config:
                    default_config[section].update(user_config[section])
        except Exception as e:
            print(
                f"Aviso: Falha ao carregar harness.toml: {e}. Usando configuração padrão."
            )
    return default_config


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


def build_parser() -> argparse.ArgumentParser:
    """Configura e retorna o parser de argumentos CLI do Harness Core."""
    parser = argparse.ArgumentParser(description="Harness Core CLI v2.0.0")
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
        "decisions", help="Valida e indexa microdecisões Markdown"
    )

    # 4. Comando: cmd
    parser_cmd = subparsers.add_parser("cmd", help="Executa um slash command de sessão")
    parser_cmd.add_argument(
        "cmd_name",
        help="Nome do comando (ex: encerrar-sessao, resume, handoff, clarificar)",
    )
    parser_cmd.add_argument(
        "cmd_args", nargs="*", help="Argumentos opcionais do comando"
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

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    # Instanciação dos adaptadores físicos
    fs = LocalFileSystemAdapter()
    git = SubprocessGitAdapter()
    process = HostFormatterAdapter()

    # Carrega configurações
    config = load_harness_config(fs)

    # Execução das sub-ações da CLI
    if args.command == "bootstrap":
        service = BootstrapService(fs)
        installed = service.install_hooks(os.getcwd())
        print(
            f"Sucesso: Hooks Git instalados com sucesso. Arquivos: {', '.join(installed)}"
        )
        sys.exit(0)

    elif args.command == "format":
        service = FormattingService(fs, process)
        file_path = resolve_format_target(args.file_path)
        if not file_path:
            sys.exit(0)
        sys.exit(service.format_file(file_path))

    elif args.command == "decisions":
        service = DecisionService(fs)
        decisoes_dir = "decisoes"
        output_file = "microdecisoes.md"
        header_file = "decisoes/_cabecalho.md"

        try:
            decisions = service.load_decisions(decisoes_dir)
            errors = service.validate_integrity(decisions)

            if errors:
                print("Erros de integridade encontrados no grafo de decisões:")
                for err in errors:
                    print(f" - {err}")
                sys.exit(1)
            else:
                print("Grafo de microdecisões validado com sucesso (zero erros).")

            # Compila o índice consolidado
            service.compile_index(decisions, output_file, header_file)
            print(f"Índice de decisões compilado com sucesso em '{output_file}'.")
            sys.exit(0)
        except Exception as e:
            print(f"Erro ao processar microdecisões: {e}")
            sys.exit(1)

    elif args.command == "cmd":
        service = CommandService(fs, git)
        session_file = "ESTADO-DA-SESSAO.md"
        result_msg = service.execute_command(
            command=args.cmd_name,
            args=args.cmd_args,
            repo_path=os.getcwd(),
            session_filepath=session_file,
        )
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
        from src.core.domain.config import load_config

        cfg = load_config(fs)
        service = InstallPromptService(fs)
        print(service.render(cfg.harness.active_harness, build_parser()))
        sys.exit(0)


if __name__ == "__main__":
    main()
