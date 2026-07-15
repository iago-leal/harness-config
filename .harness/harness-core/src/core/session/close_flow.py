"""Orquestração do encerramento de sessão (feature 018).

Fonte ÚNICA do fluxo ``encerrar-sessao``, extraída da borda ``main.py`` (D-01)
para que a CLI e os scripts finos da skill a consumam sem duplicar lógica
(DRY, RN-N5: o core segue agnóstico ao harness). O serviço orquestra:

    pré-check de trabalho pendente (016) → fechamento via CommandService →
    ofertas de fim de sessão (014: push → upgrade)

Todo IO é injetável (``out``/``err``/``asker``/``is_interactive``) para manter o
serviço testável e para que ambas as bordas compartilhem o mesmo comportamento
(markers sem TTY, perguntas com TTY). ``run`` devolve o código de saída que a
borda repassa ao ``sys.exit``.
"""

import sys
from typing import Optional


def pending_work_paths(git, repo_path: str, session_file: str) -> list:
    """Caminhos sujos da working tree, EXCETO o arquivo de estado (feature 019).

    Exclui apenas ``session_file`` (ex.: ``.harness/estado-da-sessao.md``), que o
    próprio commit de fechamento versiona (RN-N31). Todo o restante — inclusive
    decisões e o índice em ``.harness/`` — é trabalho a commitar antes de encerrar
    (RN-03). Caches de runtime de ``.harness/`` ficam de fora pelo ``.gitignore``
    (``git status --porcelain`` omite ignorados). Read-only — não toca o working tree.
    """
    dirty = git.list_dirty_paths(repo_path)
    return [p for p in dirty if p != session_file]


def render_commit_pendente_marker(paths: list, *, cap: int = 20) -> str:
    """Marker estruturado de trabalho pendente (modo sem TTY).

    Contrato consumido pelo agente (ver
    `_reversa_forward/019-oferta-commit-cobre-harness/interfaces/commit-pendente-marker.md`,
    delta de semântica sobre o da feature 016).
    """
    shown = paths[:cap]
    truncado = "" if len(paths) <= cap else f" truncado=true mostrados={len(shown)}"
    arquivos = ",".join(shown)
    return (
        f'[HARNESS:COMMIT_PENDENTE arquivos="{arquivos}" total={len(paths)}{truncado} '
        'acao="git add -- <arquivos> e git commit (mensagem descritiva); '
        'depois rode novamente encerrar-sessao"]'
    )


def conduct_commit_pendente(paths, *, is_interactive=None, out=print) -> None:
    """Anuncia trabalho pendente antes de encerrar (dualidade TTY × marker).

    Sem TTY, emite o marker estruturado para o agente mediar. Com TTY, lista os
    arquivos em texto legível. Em ambos os casos NÃO commita nem fecha: o commit
    com mensagem descritiva cabe ao agente/usuário, que então re-roda o comando
    (RN-03, abortar-e-reexecutar; o core nunca faz ``git add`` do trabalho).
    """
    if is_interactive is None:
        is_interactive = sys.stdin.isatty()
    if not is_interactive:
        out(render_commit_pendente_marker(paths))
        return
    out("Há trabalho não commitado (exceto o estado de sessão) antes de encerrar:")
    for p in paths:
        out(f"  - {p}")
    out(
        "Commit esse trabalho (git add -- <arquivo> && git commit, com mensagem "
        "descritiva) e rode encerrar-sessao novamente."
    )


def narrative_is_stale(git, repo_path: str, session_file: str, session) -> bool:
    """A narrativa da sessão não foi atualizada NESTA sessão? (narrativa viva)

    O ``estado-da-sessao.md`` tem duas metades: o front-matter (âncora/status, que o
    fechamento mantém) e a narrativa (as 4 seções ``##``, escritas PELO agente). O core
    nunca inventa a narrativa; mas pode exigir, de forma barulhenta, que ela não fique
    para trás. Duas condições disparam o gate: (1) narrativa VAZIA — não se encerra sem
    narrar; (2) narrativa IDÊNTICA à do commit-âncora de partida (``session.commit_hash``,
    o estado como retomado) — sinal de que o agente esqueceu de consolidar o que fez.

    Fail-OPEN (não bloqueia) apenas quando não há baseline legível na âncora — 1ª sessão
    ou histórico ausente/malformado — e a narrativa atual já está preenchida: aí o
    preenchimento basta. Read-only: não toca o working tree.
    """
    from src.core.session import serializer
    from src.core.session.errors import MalformedSessionStateError

    narrative = session.narrative
    if narrative is None or narrative.is_empty():
        return True

    baseline_raw = git.get_file_at_ref(repo_path, session.commit_hash, session_file)
    if not baseline_raw:
        # Sem baseline na âncora (1ª sessão real): narrativa preenchida já basta.
        return False
    try:
        baseline = serializer.parse(baseline_raw)
    except MalformedSessionStateError:
        # Estado histórico ilegível não pode travar o encerramento de hoje.
        return False
    if baseline is None or baseline.narrative is None:
        return False
    return narrative == baseline.narrative


def render_narrativa_pendente_marker(session_file: str) -> str:
    """Marker estruturado de narrativa não atualizada (modo sem TTY).

    Simétrico ao ``COMMIT_PENDENTE``: o agente reescreve as 4 seções e re-roda o
    encerramento. Contrato consumido pela skill ``encerrar-sessao``.
    """
    return (
        f'[HARNESS:NARRATIVA_PENDENTE arquivo="{session_file}" '
        'acao="atualize a narrativa da sessão (as 4 seções: O que foi feito / '
        "Próximos passos / Pendências / bloqueios / Ponteiros) refletindo o "
        'trabalho desta sessão; depois rode novamente encerrar-sessao"]'
    )


def conduct_narrativa_pendente(
    session_file: str, *, is_interactive=None, out=print
) -> None:
    """Anuncia narrativa desatualizada antes de encerrar (dualidade TTY × marker).

    Sem TTY, emite o marker para o agente mediar. Com TTY, orienta em texto legível.
    Em ambos os casos NÃO fecha: consolidar a narrativa cabe ao agente, que então
    re-roda o comando (mesmo protocolo abortar-e-reexecutar do ``COMMIT_PENDENTE``).
    """
    if is_interactive is None:
        is_interactive = sys.stdin.isatty()
    if not is_interactive:
        out(render_narrativa_pendente_marker(session_file))
        return
    out(
        f"A narrativa da sessão em {session_file} não foi atualizada nesta sessão "
        "(está vazia ou idêntica à do início)."
    )
    out(
        "Reescreva as 4 seções (O que foi feito / Próximos passos / Pendências / "
        "bloqueios / Ponteiros) refletindo o trabalho desta sessão e rode "
        "encerrar-sessao novamente."
    )


def render_decisao_pendente_marker(paths: list, *, cap: int = 20) -> str:
    """Marker estruturado de decisão não registrada (modo sem TTY, feature 022).

    Terceiro da família COMMIT/NARRATIVA_PENDENTE, mesmo protocolo
    abortar-e-reexecutar. Contrato consumido pelo agente (ver
    `_reversa_forward/022-hook-registro-decisoes/interfaces/decisao-pendente-marker.md`).
    """
    shown = paths[:cap]
    truncado = "" if len(paths) <= cap else f" truncado=true mostrados={len(shown)}"
    arquivos = ",".join(shown)
    return (
        f'[HARNESS:DECISAO_PENDENTE mudancas="{arquivos}" total={len(paths)}{truncado} '
        'acao="registre a(s) decisão(ões) não óbvia(s) desta sessão como ficha '
        ".harness/decisoes/MD-NNNN.md (front-matter id/gancho/estado/relacoes + "
        "seções D/PORQUÊ/DESCARTADO/ESTADO), commite e rode novamente "
        "encerrar-sessao; se não houve decisão não óbvia, rode encerrar-sessao "
        '--sem-decisao"]'
    )


def conduct_decisao_pendente(paths, *, is_interactive=None, out=print) -> None:
    """Anuncia decisão não registrada antes de encerrar (dualidade TTY × marker).

    Sem TTY, emite o marker para o agente mediar. Com TTY, orienta em texto
    legível. Em ambos os casos NÃO fecha nem cria a ficha: registrar (ou
    declarar a ausência com ``--sem-decisao``) cabe ao agente/usuário, que então
    re-roda o comando (protocolo abortar-e-reexecutar).
    """
    if is_interactive is None:
        is_interactive = sys.stdin.isatty()
    if not is_interactive:
        out(render_decisao_pendente_marker(paths))
        return
    out("Há trabalho substantivo nesta sessão sem microdecisão registrada:")
    for p in paths:
        out(f"  - {p}")
    out(
        "Registre a(s) decisão(ões) não óbvia(s) como ficha "
        ".harness/decisoes/MD-NNNN.md (seções D/PORQUÊ/DESCARTADO/ESTADO) e rode "
        "encerrar-sessao novamente; se não houve decisão não óbvia, use "
        "encerrar-sessao --sem-decisao."
    )


def render_offer_markers(offers) -> list:
    """Modo sem TTY: linhas-marcador estáveis das ofertas, sem ler entrada.

    Contrato consumido pelo agente (ver
    `_reversa_forward/014-oferta-upgrade-ao-encerrar/interfaces/session-end-offers.md`).
    Uma linha por oferta cabível; ordem push → upgrade.
    """
    lines = []
    if offers.push:
        lines.append(
            "[HARNESS:PUSH_DISPONIVEL "
            f"branch={offers.push.branch} remote={offers.push.remote} "
            f"ahead={offers.push.ahead} "
            f"principal={'true' if offers.push.is_default_branch else 'false'} "
            'acao="git push"]'
        )
    if offers.upgrade:
        lines.append(
            "[HARNESS:UPGRADE_DISPONIVEL "
            f"atual={offers.upgrade.current_version} "
            f"alvo={offers.upgrade.target_version} "
            'acao="./harness upgrade"]'
        )
    return lines


def _ask_yes(question: str) -> bool:
    return input(question).strip().lower() in ("s", "sim", "y", "yes")


def conduct_end_session_offers(
    offers,
    repo_path: str,
    git,
    run_upgrade,
    *,
    is_interactive=None,
    asker=_ask_yes,
    out=print,
    err=None,
):
    """Conduz as ofertas de fim de sessão (push → upgrade), feature 014.

    Sem TTY, emite os marcadores estruturados e não lê entrada. Com TTY,
    pergunta ``[s/N]`` por oferta, na ordem push → upgrade (RN-10), executando a
    aceita. Cada ação é protegida para que uma falha (rede/push/upgrade) avise e
    siga, sem abortar a outra nem o encerramento já feito (RN-02/RN-09).
    """
    if err is None:

        def err(message):
            print(message, file=sys.stderr)

    if not offers.has_any:
        return
    if is_interactive is None:
        is_interactive = sys.stdin.isatty()

    if not is_interactive:
        for line in render_offer_markers(offers):
            out(line)
        return

    if offers.push:
        p = offers.push
        if p.is_default_branch:
            question = (
                f"⚠️  '{p.branch}' é a branch principal. Publicar diretamente em "
                f"{p.remote}/{p.branch} ({p.ahead} commit(s)) com git push? [s/N] "
            )
        else:
            question = (
                f"Há {p.ahead} commit(s) à frente de {p.remote}/{p.branch}. "
                "Publicar agora (git push)? [s/N] "
            )
        if asker(question):
            try:
                git.push(repo_path)
                out("Trabalho publicado com sucesso.")
            except Exception as exc:
                err(f"Falha ao publicar (git push): {exc}")

    if offers.upgrade:
        u = offers.upgrade
        if asker(
            f"🔼 Atualização do Harness Core disponível: {u.current_version} → "
            f"{u.target_version}. Atualizar agora? [s/N] "
        ):
            try:
                run_upgrade(u)
            except Exception as exc:
                err(f"Falha ao atualizar o Harness Core: {exc}")


class SessionCloseFlow:
    """Fluxo de encerramento de sessão, compartilhado por CLI e skill.

    Recebe os adaptadores concretos (``fs``/``git``/``process``) e expõe um único
    ``run`` que decide e executa o fechamento, devolvendo o código de saída. A
    lógica de domínio continua em ``CommandService``/``GitPort``/serviços de
    oferta — este serviço apenas orquestra a sequência da borda.
    """

    def __init__(self, fs, git, process):
        self.fs = fs
        self.git = git
        self.process = process

    def run(
        self,
        repo_path: str,
        config,
        *,
        out=print,
        err=None,
        asker=_ask_yes,
        is_interactive: Optional[bool] = None,
        sem_decisao: bool = False,
    ) -> int:
        """Executa o encerramento e devolve o código de saída (0 sucesso, ≠0 falha).

        Sequência (espelha o contrato da skill): pré-check de pendência →
        fechamento → ofertas. Estado malformado e falha de commit do estado
        encerram barulhento (exit 1), nunca em silêncio (RN-N4/RN-31).
        """
        from src.core.commands.service import CommandService
        from src.core.commands.errors import SessionCommitError
        from src.core.session.errors import MalformedSessionStateError

        if err is None:

            def err(message):
                print(message, file=sys.stderr)

        service = CommandService(self.fs, self.git)
        session_file = config.session.state_file

        # Pré-check de trabalho pendente (016/RN-03): só com sessão presente.
        # Estado malformado é barulhento (RN-N4): nunca degrada para no-op.
        try:
            sessao_existente = service.load_session(session_file)
        except MalformedSessionStateError as exc:
            return self._abort_malformed(session_file, exc, err)

        if sessao_existente is not None:
            pendentes = pending_work_paths(self.git, repo_path, session_file)
            if pendentes:
                # Emite marker / lista (não fecha). O agente commita o trabalho
                # real e re-roda o encerrar-sessao.
                conduct_commit_pendente(
                    pendentes, is_interactive=is_interactive, out=out
                )
                return 0

            # Gate de narrativa viva: não se encerra com a narrativa vazia ou
            # congelada desde o início da sessão. Barulhento e não-fechante — o
            # agente consolida as 4 seções e re-roda (mesmo protocolo do pendente).
            if narrative_is_stale(self.git, repo_path, session_file, sessao_existente):
                conduct_narrativa_pendente(
                    session_file, is_interactive=is_interactive, out=out
                )
                return 0

            # 3º portão (feature 022): registro obrigatório de microdecisões.
            # Roda por último — o pré-check já forçou o commit do trabalho, então
            # o diff da âncora enxerga a sessão inteira. Fail-open barulhento em
            # erro interno; anti-loop por fingerprint (RF-04): o mesmo estado de
            # pendência nunca bloqueia duas vezes.
            if config.decisions.require_registration:
                from src.core.decisions.gate import evaluate_registration_gate

                verdict = evaluate_registration_gate(
                    self.git, repo_path, sessao_existente, config
                )
                if verdict.aviso:
                    err(f"Aviso: {verdict.aviso}")
                if verdict.pendente and sem_decisao:
                    # Escape auditável (RN-03): a declaração explícita vira
                    # registro na narrativa — não é o core inventando narrativa
                    # (RN-N3), é o rastro de um ato deliberado do agente/usuário.
                    sessao_existente.narrative.feito.append(
                        "Declarado: sem decisão não óbvia nesta sessão "
                        "(gate de registro)."
                    )
                    service.save_session(session_file, sessao_existente)
                elif verdict.pendente:
                    if (
                        sessao_existente.gate_encerramento_fingerprint
                        == verdict.fingerprint
                    ):
                        err(
                            "Aviso: pendência de registro de decisão não sanada "
                            "(o gate já bloqueou uma vez para este estado); "
                            "encerrando mesmo assim."
                        )
                    else:
                        sessao_existente.gate_encerramento_fingerprint = (
                            verdict.fingerprint
                        )
                        service.save_session(session_file, sessao_existente)
                        conduct_decisao_pendente(
                            verdict.mudancas, is_interactive=is_interactive, out=out
                        )
                        return 0

        try:
            result_msg = service.execute_command(
                command="encerrar-sessao",
                args=[],
                repo_path=repo_path,
                session_filepath=session_file,
            )
        except MalformedSessionStateError as exc:
            return self._abort_malformed(session_file, exc, err)
        except SessionCommitError as exc:
            err(f"Encerramento abortado: {exc}")
            return 1

        out(result_msg)

        # Ofertas de fim de sessão (014): SÓ após sucesso, como etapa POSTERIOR e
        # estritamente não-bloqueante (RN-01/02).
        if result_msg.startswith("Sessão encerrada com sucesso"):
            self._conduct_offers(
                repo_path,
                config,
                out=out,
                err=err,
                asker=asker,
                is_interactive=is_interactive,
            )
        return 0

    @staticmethod
    def _abort_malformed(session_file: str, exc, err) -> int:
        """Encerramento explícito com estado malformado: aborta barulhento (1)."""
        err(f"Aviso: estado de sessão malformado em {session_file}: {exc}")
        err(
            "Encerramento abortado: corrija a âncora do estado de sessão em "
            f"{session_file} para um SHA-1 de 40 caracteres e tente de novo."
        )
        return 1

    def _conduct_offers(
        self, repo_path, config, *, out, err, asker, is_interactive
    ) -> None:
        """Detecta e conduz as ofertas push/upgrade sob try/except não-bloqueante."""
        try:
            from src.core.domain.layout import SYNC_CACHE_REL_PATH
            from src.core.sync.service import SyncService
            from src.core.session.offers import EndSessionOffersService

            sync_service = SyncService(self.fs, self.git, SYNC_CACHE_REL_PATH)
            offers = EndSessionOffersService(self.git, sync_service).detect(
                repo_path, config
            )

            def run_upgrade(upgrade_offer):
                # D-05 (014): sincroniza o clone do upstream por fast-forward antes
                # de copiar; não-FF (sujo/divergente) aborta sem sobrescrever.
                up = upgrade_offer.upstream_path
                default = self.git.get_default_branch(up)
                if not self.git.merge_ff_only(up, f"origin/{default}"):
                    raise RuntimeError(
                        "não foi possível sincronizar o upstream por "
                        "fast-forward (working tree sujo ou divergência); "
                        "upgrade abortado sem sobrescrever trabalho"
                    )
                from src.core.bootstrap.init_service import InitializationService

                InitializationService(self.fs, self.process).upgrade_project(repo_path)
                out("Harness Core atualizado com sucesso.")

            conduct_end_session_offers(
                offers,
                repo_path,
                self.git,
                run_upgrade,
                is_interactive=is_interactive,
                asker=asker,
                out=out,
                err=err,
            )
        except Exception as exc:
            err(f"Aviso: ofertas de fim de sessão (não-bloqueantes) falharam: {exc}")


__all__ = [
    "pending_work_paths",
    "render_commit_pendente_marker",
    "conduct_commit_pendente",
    "narrative_is_stale",
    "render_narrativa_pendente_marker",
    "conduct_narrativa_pendente",
    "render_decisao_pendente_marker",
    "conduct_decisao_pendente",
    "render_offer_markers",
    "conduct_end_session_offers",
    "SessionCloseFlow",
]
