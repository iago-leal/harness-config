import os
from typing import Optional
from mcp.server.fastmcp import FastMCP

from src.adapters.fs.local import LocalFileSystemAdapter
from src.adapters.git.subprocess import SubprocessGitAdapter
from src.adapters.process.formatter import HostFormatterAdapter
from src.core.formatting.service import FormattingService
from src.core.sync.service import SyncService
from src.core.decisions.service import DecisionService
from src.core.commands.service import CommandService
from src.core.domain.config import load_config
from src.core.domain.layout import SYNC_CACHE_REL_PATH

# Criação do Servidor FastMCP
mcp = FastMCP("Harness")

# Instanciação comum de adaptadores físicos
fs = LocalFileSystemAdapter()
git = SubprocessGitAdapter()
process = HostFormatterAdapter()


@mcp.tool(
    name="format_file",
    description="Formata automaticamente um arquivo suportado (Python, JS/TS/JSON, Rust)",
)
def format_file(file_path: str) -> str:
    config = load_config(fs)
    service = FormattingService(fs, process, config)
    # format_file retorna sempre 0 (sucesso/não bloqueia)
    service.format_file(file_path)
    return f"Formatação processada para: {file_path}"


@mcp.tool(
    name="check_repository_sync",
    description="Verifica se o repositório Git local está sincronizado com a branch remota",
)
def check_repository_sync(repo_path: Optional[str] = None) -> str:
    path = repo_path or os.getcwd()
    cache_filepath = SYNC_CACHE_REL_PATH
    cache_ttl = 24

    service = SyncService(
        fs, git, cache_filepath=cache_filepath, cache_ttl_hours=cache_ttl
    )
    in_sync = service.check_sync(path)
    if in_sync:
        return "Sincronizado: O repositório está atualizado ou checado no TTL."
    else:
        return "Alerta: O repositório local está defasado em relação à branch remota."


@mcp.tool(
    name="process_decisions",
    description="Carrega, valida integridade do grafo e compila o índice consolidado de microdecisões",
)
def process_decisions(
    decisoes_dir: Optional[str] = None, output_file: Optional[str] = None
) -> str:
    config = load_config(fs)
    decisoes_dir = decisoes_dir or config.decisions.dir
    output_file = output_file or config.decisions.index_file
    service = DecisionService(fs)
    header_file = os.path.join(decisoes_dir, "_cabecalho.md")

    try:
        decisions = service.load_decisions(decisoes_dir)
        errors = service.validate_integrity(decisions)

        result_msg = ""
        if errors:
            result_msg += "Erros de integridade encontrados no grafo de decisões:\n"
            for err in errors:
                result_msg += f" - {err}\n"
        else:
            result_msg += "Grafo de microdecisões validado com sucesso (zero erros).\n"

        service.compile_index(decisions, output_file, header_file)
        result_msg += f"Índice de decisões compilado com sucesso em '{output_file}'."
        return result_msg

    except Exception as e:
        return f"Erro ao processar decisões: {e}"


@mcp.tool(
    name="session_command",
    description="Executa um comando de sessão interativa (encerrar-sessao, resume, handoff, clarificar)",
)
def session_command(cmd_name: str, active_feature: Optional[str] = None) -> str:
    """Borda MCP dos comandos de sessão.

    Assimetria deliberada da feature 024 (D-04): esta borda NÃO tem interlocutor a
    quem perguntar o consentimento do commit de encerramento, então mantém o
    default ``versionar_estado=True`` de ``execute_command`` — encerrar via MCP
    segue versionando o estado, sem pergunta. Propagar aqui a inversão da RN-08
    produziria fechamento não versionado silencioso, o oposto do pedido. A ressalva
    está declarada na RN-04 do requirements da 024.
    """
    service = CommandService(fs, git)
    config = load_config(fs)
    session_file = config.session.state_file
    args = [active_feature] if active_feature else []

    return service.execute_command(
        command=cmd_name,
        args=args,
        repo_path=os.getcwd(),
        session_filepath=session_file,
    )
