#!/usr/bin/env python3
import os
import sys
import argparse
import toml
from typing import List

# Adiciona o diretório contendo 'src' ao sys.path para imports absolutos funcionarem de qualquer lugar
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.adapters.fs.local import LocalFileSystemAdapter
from src.adapters.git.subprocess import SubprocessGitAdapter
from src.adapters.process.formatter import HostFormatterAdapter
from src.core.bootstrap.service import BootstrapService
from src.core.formatting.service import FormattingService
from src.core.sync.service import SyncService
from src.core.decisions.service import DecisionService
from src.core.commands.service import CommandService

def load_harness_config(fs: LocalFileSystemAdapter) -> dict:
    """Carrega as configurações do harness.toml se existir."""
    default_config = {
        "harness": {"active_harness": "claude"},
        "formatting": {"exclude_paths": [], "opt_out_file": ".no-autoformat"},
        "sync": {"cache_ttl_hours": 24, "remote_check_enabled": True}
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
            print(f"Aviso: Falha ao carregar harness.toml: {e}. Usando configuração padrão.")
    return default_config

def main():
    parser = argparse.ArgumentParser(description="Harness Core CLI v2.0.0")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # 1. Comando: bootstrap
    parser_bootstrap = subparsers.add_parser("bootstrap", help="Instala ganchos Git locais")
    parser_bootstrap.add_argument("--shadow", action="store_true", help="Instala em modo Shadow (Coexistência)")
    parser_bootstrap.add_argument("--active", action="store_false", dest="shadow", help="Instala em modo Ativo Definitivo")

    # 2. Comando: format
    parser_format = subparsers.add_parser("format", help="Formata um arquivo específico")
    parser_format.add_argument("file_path", help="Caminho do arquivo a formatar")
    parser_format.add_argument("--shadow", action="store_true", help="Executa em modo Shadow (dry-run)")

    # 3. Comando: decisions
    parser_decisions = subparsers.add_parser("decisions", help="Valida e indexa microdecisões Markdown")
    parser_decisions.add_argument("--shadow", action="store_true", help="Executa em modo Shadow (validação de logs)")

    # 4. Comando: cmd
    parser_cmd = subparsers.add_parser("cmd", help="Executa um slash command de sessão")
    parser_cmd.add_argument("cmd_name", help="Nome do comando (ex: encerrar-sessao, resume, handoff, clarificar)")
    parser_cmd.add_argument("cmd_args", nargs="*", help="Argumentos opcionais do comando")

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
        installed = service.install_hooks(os.getcwd(), shadow_mode=args.shadow)
        print(f"Sucesso: Hooks Git instalados com sucesso. Arquivos: {', '.join(installed)}")
        sys.exit(0)

    elif args.command == "format":
        service = FormattingService(fs, process)
        # Se for shadow, apenas executa sem afetar o workflow, mas no shadow o FormattingService
        # é chamado. Para o formatador, o retorno do format_file é sempre 0 de qualquer forma.
        exit_code = service.format_file(args.file_path)
        sys.exit(exit_code)

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
                if not args.shadow:
                    # Em modo ativo bloqueia o post-merge se houver erro grave
                    sys.exit(1)
            else:
                print("Grafo de microdecisões validado com sucesso (zero erros).")

            # Compila o índice consolidado
            service.compile_index(decisions, output_file, header_file)
            print(f"Índice de decisões compilado com sucesso em '{output_file}'.")
            sys.exit(0)
        except Exception as e:
            print(f"Erro ao processar microdecisões: {e}")
            sys.exit(1 if not args.shadow else 0)

    elif args.command == "cmd":
        service = CommandService(fs, git)
        session_file = "ESTADO-DA-SESSAO.md"
        result_msg = service.execute_command(
            command=args.cmd_name,
            args=args.cmd_args,
            repo_path=os.getcwd(),
            session_filepath=session_file
        )
        print(result_msg)
        sys.exit(0)

if __name__ == "__main__":
    main()
