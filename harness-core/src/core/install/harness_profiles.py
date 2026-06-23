from abc import ABC, abstractmethod


class HarnessProfile(ABC):
    """Estratégia por harness: encapsula o mecanismo de ganchos de um agente.

    Cada perfil sabe produzir o bloco de configuração de ganchos e as instruções
    de aplicação adequadas ao seu harness, sem que o serviço precise de `if`s
    espalhados.
    """

    name = "base"

    @abstractmethod
    def hooks_block(self) -> str:
        """Bloco de configuração de ganchos, pronto para colar."""

    @abstractmethod
    def apply_instructions(self) -> str:
        """Instrução em uma frase sobre onde e como aplicar o bloco."""


class ClaudeProfile(HarnessProfile):
    name = "claude"

    def hooks_block(self) -> str:
        return (
            "{\n"
            '  "hooks": {\n'
            '    "SessionStart": [\n'
            '      { "matcher": "startup|resume|clear", "hooks": [\n'
            '        { "type": "command", "command": "${CLAUDE_PROJECT_DIR}/harness cmd resume", "timeout": 12 } ] }\n'
            "    ],\n"
            '    "PostToolUse": [\n'
            '      { "matcher": "Write|Edit", "hooks": [\n'
            '        { "type": "command", "command": "${CLAUDE_PROJECT_DIR}/harness format", "timeout": 30 } ] }\n'
            "    ],\n"
            '    "Stop": [\n'
            '      { "hooks": [\n'
            '        { "type": "command", "command": "${CLAUDE_PROJECT_DIR}/harness decisions", "timeout": 10 } ] }\n'
            "    ]\n"
            "  }\n"
            "}"
        )

    def apply_instructions(self) -> str:
        return (
            "Mescle o bloco abaixo na chave `hooks` do `.claude/settings.json` do PROJETO "
            "(crie o arquivo se não existir)."
        )


class GeminiProfile(HarnessProfile):
    name = "gemini"

    def hooks_block(self) -> str:
        return (
            "# Gemini CLI: os ganchos sobem pela ponte `context.*` do settings.json do Gemini,\n"
            "# não pelo mesmo esquema `hooks` do Claude. Aponte o SessionStart/PostToolUse/Stop\n"
            "# para `./harness` via os campos `context.*` correspondentes."
        )

    def apply_instructions(self) -> str:
        return (
            "Configure via a ponte `context.*` no settings.json do Gemini do projeto "
            "(referência: SPEC-memoria-no-gemini do ALICERCE)."
        )


class AntigravityProfile(HarnessProfile):
    name = "antigravity"

    def hooks_block(self) -> str:
        return "# (mecanismo de ganchos do antigravity ainda não confirmado no _reversa_sdd/)"

    def apply_instructions(self) -> str:
        return (
            "⚠️ O mecanismo de ganchos do antigravity ainda não está documentado — "
            "confirme antes de aplicar."
        )


_PROFILES = {
    "claude": ClaudeProfile,
    "gemini": GeminiProfile,
    "antigravity": AntigravityProfile,
}


def get_profile(active_harness: str) -> HarnessProfile:
    """Resolve o perfil pelo nome do harness ativo. Desconhecido → erro barulhento."""
    profile_cls = _PROFILES.get(active_harness)
    if profile_cls is None:
        raise ValueError(
            f"Harness desconhecido: {active_harness!r}. "
            f"Esperado um de {sorted(_PROFILES)}."
        )
    return profile_cls()
