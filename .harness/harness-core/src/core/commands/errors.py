class SessionCommitError(Exception):
    """Falha ao versionar o registro de encerramento da sessão.

    Levantada quando o commit do estado de sessão não pode ser criado (ex.:
    identidade git ausente, repositório inconsistente). Falha barulhenta no
    espírito de ``MalformedSessionStateError`` (RN-N4): o comando nunca devolve
    "sucesso" quando o commit não aconteceu. O arquivo de estado já gravado é
    preservado em disco (não é revertido).
    """


class NoActiveSessionError(Exception):
    """Tentativa de encerrar uma sessão ausente ou inativa.

    Levantada quando ``encerrar-sessao`` é invocado sem uma sessão ativa para
    fechar — arquivo de estado ausente, ou presente mas com ``is_active`` falso
    (sessão já encerrada antes). Falha barulhenta no espírito de
    ``MalformedSessionStateError`` (RN-N4 estendida à terceira categoria,
    "válida porém inativa"): o comando explícito nunca devolve ``exit 0``
    silencioso. A borda distingue boot (``resume``, não-bloqueante) de invocação
    explícita e converte esta exceção em saída diferente de zero.
    """
