class SessionCommitError(Exception):
    """Falha ao versionar o registro de encerramento da sessão.

    Levantada quando o commit do estado de sessão não pode ser criado (ex.:
    identidade git ausente, repositório inconsistente). Falha barulhenta no
    espírito de ``MalformedSessionStateError`` (RN-N4): o comando nunca devolve
    "sucesso" quando o commit não aconteceu. O arquivo de estado já gravado é
    preservado em disco (não é revertido).
    """


# NOTA (feature 016): a antiga ``NoActiveSessionError`` foi removida. Sessão
# ausente ou inativa deixou de ser falha barulhenta — o encerramento agora as
# tolera (ausente → no-op; inativa → reativa e fecha; D1/D3). Apenas o estado
# MALFORMADO segue barulhento, via ``MalformedSessionStateError`` (RN-N4).
