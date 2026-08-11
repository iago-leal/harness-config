"""Feature 021 (→028) — apêndice de decisões para o resume.

Função pura, agnóstica ao harness (RN-N5): a borda calcula `enabled` — que já
embute o gate por harness (Claude-first) e o flag `session.inject_decisions_index`
— e o repassa. Não escreve em stderr: os avisos (compacta ausente, índice
ausente) são da borda. Desde a feature 028 a injeção preferencial é a visão
COMPACTA (`decisions.compact_file`); o índice integral só entra como fallback,
na janela entre o upgrade e a primeira reindexação que deriva a compacta.
"""

from src.core.ports.fs import FileSystemPort
from typing import Optional

_HEADER = "\n\n---\n## Índice de decisões (consulte antes de buscas amplas)\n\n"
_HEADER_COMPACT = "\n\n---\n## Decisões recentes (índice completo sob demanda)\n\n"


def _read_nonempty(fs: FileSystemPort, path: str) -> str:
    if not fs.exists(path):
        return ""
    return fs.read_file(path).strip()


def build_decisions_appendix(
    fs: FileSystemPort,
    index_file: str,
    enabled: bool,
    compact_file: Optional[str] = None,
) -> str:
    """Devolve o bloco a anexar ao contexto do resume, ou "" quando não se aplica.

    Retorna "" se `enabled` for falso ou se nenhuma das fontes existir/tiver
    conteúdo (não-bloqueante, RN-N4). Precedência: visão compacta quando
    presente e não-vazia; senão o índice integral (fallback autoresolvente,
    028/D-02). O bloco vem prefixado por separação para concatenar depois do
    estado (estado primeiro; sob truncamento no teto, o apêndice cede).
    """
    if not enabled:
        return ""
    if compact_file:
        content = _read_nonempty(fs, compact_file)
        if content:
            return _HEADER_COMPACT + content + "\n"
    content = _read_nonempty(fs, index_file)
    if not content:
        return ""
    return _HEADER + content + "\n"
