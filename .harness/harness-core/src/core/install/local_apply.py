"""Materialização local compartilhada por ``init`` e ``upgrade`` (feature 012).

Função única que aplica os materializadores de IDE sob ``project_path``: os
slash commands de sessão (sempre, RN-N28) e o ``.agents/hooks.json`` do
Antigravity (somente quando o harness ativo é o Antigravity, RN-N27).

Centralizar a chamada aqui permite que ``init`` a execute in-process — lá o
código em execução já é o do upstream, fresco — e que ``upgrade`` a invoque via
subprocesso do python de destino, garantindo que a materialização rode com o
código recém-copiado, nunca com os módulos antigos carregados em memória
(o bug stale do Modo 1).
"""

from src.core.ports.fs import FileSystemPort
from src.core.install.session_commands import materialize_session_commands
from src.core.install.antigravity_hooks import materialize_hooks_json


def apply_local_materializers(
    fs: FileSystemPort,
    project_path: str,
    command_path: str,
    active_harness: str,
) -> None:
    """Aplica os materializadores de IDE sob ``project_path``.

    ``command_path`` é o caminho absoluto do wrapper ``./harness`` do projeto,
    embutido no comando do Antigravity. Toda escrita ocorre sob ``project_path``
    (footprint global zero, RN-N17).
    """
    materialize_session_commands(fs, project_path, command_path)
    if active_harness == "antigravity":
        materialize_hooks_json(fs, project_path, command_path)
