class SessionCommitError(Exception):
    """Falha ao versionar o registro de encerramento da sessão.

    Levantada quando o commit do estado de sessão não pode ser criado (ex.:
    identidade git ausente, repositório inconsistente). Falha barulhenta no
    espírito de ``MalformedSessionStateError`` (RN-N4): o comando nunca devolve
    "sucesso" quando o commit não aconteceu. O arquivo de estado já gravado é
    preservado em disco (não é revertido).
    """
