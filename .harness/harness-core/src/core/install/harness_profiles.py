import json
from abc import ABC, abstractmethod
from typing import List, Optional


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

    def skills_dir(self) -> Optional[str]:
        """Diretório (relativo ao projeto) onde o harness lê skills versionáveis.

        A capacidade `encerrar-sessao` é entregue como uma skill (`SKILL.md` +
        `scripts/`) materializada aqui (feature 018). Devolve o prefixo por
        harness (ex.: ``.claude/skills``) ou ``None`` quando o harness não expõe
        superfície de skill para esta capacidade. Por padrão, ``None``.
        """
        return None

    def stale_session_command_paths(self) -> List[str]:
        """Caminhos relativos de artefatos de slash command LEGADOS a remover.

        Quando um perfil muda o caminho de materialização do seu artefato, os
        arquivos gravados por versões anteriores viram órfãos. Cada perfil
        declara aqui os caminhos legados que a materialização deve limpar — só o
        arquivo nomeado, nunca o diretório (não-destrutivo, RN-03). Por padrão,
        vazio.
        """
        return []


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
            "(crie o arquivo se não existir). Aplique SEMPRE no `.claude/settings.json` do "
            "**projeto**. Nunca edite a configuração global em `~/.claude`."
        )

    def skills_dir(self) -> Optional[str]:
        # O Claude lê skills de projeto de `.claude/skills/<nome>/SKILL.md`.
        return ".claude/skills"

    def stale_session_command_paths(self) -> List[str]:
        # Migração 010/016 → 018: o slash command `.claude/commands/encerrar-sessao.md`
        # que delegava ao binário foi substituído pela skill versionável. Remove
        # o órfão (só o arquivo nomeado, não-destrutivo).
        return [".claude/commands/encerrar-sessao.md"]


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
            "Configure via a ponte `context.*` no `settings.json` do Gemini do **projeto** "
            "(referência: SPEC-memoria-no-gemini do ALICERCE); nunca toque na configuração "
            "global do Gemini em `~`."
        )


class AntigravityProfile(HarnessProfile):
    name = "antigravity"

    # Caminho absoluto do `./harness` do projeto, gravado na materialização (D-06).
    # Mantido literal aqui; `materialize_hooks_json` o substitui pelo caminho real.
    ABS_PLACEHOLDER = "<ABS>"

    # Tools de escrita do Antigravity cobertas pelos ganchos de captura/formatação.
    WRITE_MATCHER = "write_to_file|replace_file_content|multi_replace_file_content"

    def _harness_named_hook(self) -> dict:
        """Named-hook `harness` no esquema do `hooks.json` do Antigravity.

        Espelha o contrato pinado em `interfaces/antigravity-hook-io.md`: captura
        em `PreToolUse`, formatação em `PostToolUse` e decisões em `Stop`.
        """
        cmd = f"{self.ABS_PLACEHOLDER}/harness agy-hook"
        return {
            "harness": {
                "PreToolUse": [
                    {
                        "matcher": self.WRITE_MATCHER,
                        "hooks": [
                            {
                                "type": "command",
                                "command": f"{cmd} pre-tool-use",
                                "timeout": 10,
                            }
                        ],
                    }
                ],
                "PostToolUse": [
                    {
                        "matcher": self.WRITE_MATCHER,
                        "hooks": [
                            {
                                "type": "command",
                                "command": f"{cmd} post-tool-use",
                                "timeout": 30,
                            }
                        ],
                    }
                ],
                "Stop": [
                    {
                        "hooks": [
                            {
                                "type": "command",
                                "command": f"{cmd} stop",
                                "timeout": 10,
                            }
                        ]
                    }
                ],
            }
        }

    def hooks_block(self) -> str:
        # JSON colável e parseável; `<ABS>` permanece literal até a materialização.
        return json.dumps(self._harness_named_hook(), indent=2, ensure_ascii=False)

    def apply_instructions(self) -> str:
        return (
            "Grave o bloco abaixo em `.agents/hooks.json` do **projeto** (o `./harness init` "
            "já o materializa por merge; cole-o à mão só se for ajustar). Escopo SEMPRE no "
            "`.agents/hooks.json` do projeto: nunca em diretório global do usuário."
        )

    def skills_dir(self) -> Optional[str]:
        # O Antigravity lê skills de projeto de `.agents/skills/<nome>/SKILL.md`
        # (ativação semântica por contexto). Plural `.agents`, ao contrário do
        # workflow legado, que vivia em `.agent/workflows` (singular).
        return ".agents/skills"

    def stale_session_command_paths(self) -> List[str]:
        # Migração 017 → 018: o workflow `.md` que delegava ao binário foi
        # substituído pela skill versionável. Remove o órfão do caminho singular
        # atual (017) E o do plural legado (anterior à 017). Só os arquivos
        # nomeados, nunca o diretório nem workflows de terceiros (não-destrutivo).
        return [
            ".agent/workflows/encerrar-sessao.md",
            ".agents/workflows/encerrar-sessao.md",
        ]


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
