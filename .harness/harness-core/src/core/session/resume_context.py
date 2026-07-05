"""Feature 021 — apêndice do índice de decisões para o resume.

Função pura, agnóstica ao harness (RN-N5): a borda calcula `enabled` — que já
embute o gate por harness (Claude-first) e o flag `session.inject_decisions_index`
— e o repassa. Não escreve em stderr: o aviso de índice ausente é da borda.
"""

from src.core.ports.fs import FileSystemPort

_HEADER = "\n\n---\n## Índice de decisões (consulte antes de buscas amplas)\n\n"


def build_decisions_appendix(fs: FileSystemPort, index_file: str, enabled: bool) -> str:
    """Devolve o bloco a anexar ao contexto do resume, ou "" quando não se aplica.

    Retorna "" se `enabled` for falso, se o índice não existir ou se estiver vazio
    (não-bloqueante, RN-N4). Caso contrário, devolve um cabeçalho de orientação
    seguido do conteúdo do índice, já prefixado por separação para concatenar
    depois do estado (estado primeiro; sob truncamento no teto, o índice cede).
    """
    if not enabled:
        return ""
    if not fs.exists(index_file):
        return ""
    content = fs.read_file(index_file).strip()
    if not content:
        return ""
    return _HEADER + content + "\n"
