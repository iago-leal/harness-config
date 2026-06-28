#!/usr/bin/env python3
"""Ponto de entrada fino da skill encerrar-sessao (feature 018).

Não reimplementa lógica: resolve o Harness Core via git (``_bootstrap``), roda da
raiz do projeto e delega aos serviços testados do core — ``RegenService`` para
regenerar os artefatos derivados e ``SessionCloseFlow`` para o fechamento (mesmo
fluxo da borda CLI ``cmd encerrar-sessao``). Falha barulhenta se o core não for
encontrado/importável.
"""

import os
import sys
from pathlib import Path

# O bootstrap fica ao lado deste script; importável antes de qualquer `src.*`.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _bootstrap import bootstrap_core, CoreNotFoundError  # noqa: E402


def main() -> int:
    try:
        root = bootstrap_core()
    except CoreNotFoundError as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return 1

    # Roda da raiz do projeto: harness.toml e o estado-da-sessao são relativos a ela.
    os.chdir(root)

    from src.adapters.fs.local import LocalFileSystemAdapter
    from src.adapters.git.subprocess import SubprocessGitAdapter
    from src.adapters.process.formatter import HostFormatterAdapter
    from src.core.domain.config import load_config
    from src.core.regen.service import RegenService
    from src.core.session.close_flow import SessionCloseFlow

    fs = LocalFileSystemAdapter()
    git = SubprocessGitAdapter()
    process = HostFormatterAdapter()
    config = load_config(fs)

    # 1. Regenera os artefatos derivados (016). Falha barulhenta aborta o
    #    encerramento ANTES de fechar — não se encerra sobre artefato stale.
    code, message = RegenService(process).run(config, os.getcwd())
    if code != 0:
        print(message, file=sys.stderr)
        return code

    # 2. Encerra a sessão: pré-check de pendência → fechamento → ofertas.
    return SessionCloseFlow(fs, git, process).run(os.getcwd(), config)


if __name__ == "__main__":
    sys.exit(main())
