class MalformedSessionStateError(Exception):
    """Estado de sessão presente mas com formato inválido — front-matter quebrado
    ou campos-máquina ausentes.

    Falha barulhenta (RN-N4): distingue "arquivo ausente" (sessão nova, normal)
    de "arquivo presente mas corrompido" (erro explícito, nunca silencioso).
    """
