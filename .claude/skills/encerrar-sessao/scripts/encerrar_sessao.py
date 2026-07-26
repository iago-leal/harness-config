#!/usr/bin/env python3
"""Ponto de entrada fino da skill encerrar-sessao (feature 018).

Não reimplementa lógica: resolve o Harness Core via git (``_bootstrap``), roda da
raiz do projeto e delega aos serviços testados do core — ``RegenService`` para
regenerar os artefatos derivados e ``SessionCloseFlow`` para o fechamento (mesmo
fluxo da borda CLI ``cmd encerrar-sessao``). Falha barulhenta se o core não for
encontrado/importável.
"""

import argparse
import os
import sys
from pathlib import Path

# O bootstrap fica ao lado deste script; importável antes de qualquer `src.*`.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _bootstrap import bootstrap_core, CoreNotFoundError  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Encerra a sessão do Harness.")
    parser.add_argument(
        "--sem-decisao",
        action="store_true",
        dest="sem_decisao",
        help=(
            "Declara que não houve decisão não óbvia nesta sessão (satisfaz o "
            "gate de registro; a declaração fica registrada na narrativa)."
        ),
    )
    # Feature 024: paridade de superfície com a borda CLI (RN-N33). Mesmas flags,
    # mesmos textos de --help (consequência, não efeito mecânico).
    parser.add_argument(
        "--com-pendencias",
        action="store_true",
        dest="com_pendencias",
        help=(
            "Encerra mesmo havendo trabalho não commitado (a declaração fica "
            "registrada na narrativa)."
        ),
    )
    grupo_commit_encerramento = parser.add_mutually_exclusive_group()
    grupo_commit_encerramento.add_argument(
        "--com-commit-encerramento",
        action="store_true",
        dest="com_commit_encerramento",
        help=(
            "Autoriza versionar o estado de sessão ao encerrar. Sem terminal "
            "interativo, sem esta flag o estado não é versionado."
        ),
    )
    grupo_commit_encerramento.add_argument(
        "--sem-commit-encerramento",
        action="store_true",
        dest="sem_commit_encerramento",
        help=(
            "Encerra sem versionar o estado de sessão; ele fica como mudança "
            "pendente no working tree."
        ),
    )
    args = parser.parse_args()

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

    # 2. Encerra a sessão: pré-check de pendência → gate de narrativa → gate de
    #    registro de decisões (022) → fechamento consentido (024) → ofertas.
    versionar_encerramento = None
    if args.com_commit_encerramento:
        versionar_encerramento = True
    elif args.sem_commit_encerramento:
        versionar_encerramento = False
    return SessionCloseFlow(fs, git, process).run(
        os.getcwd(),
        config,
        sem_decisao=args.sem_decisao,
        com_pendencias=args.com_pendencias,
        versionar_encerramento=versionar_encerramento,
    )


if __name__ == "__main__":
    sys.exit(main())
