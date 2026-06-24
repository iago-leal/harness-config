"""Testes do artefato de slash command por perfil (feature 010, T003).

`ClaudeProfile` e `AntigravityProfile` devolvem `(rel_path, content)` do arquivo
de comando que aciona `./harness cmd encerrar-sessao`; `GeminiProfile` devolve
`None` (sem superfície de slash command definida para esta capacidade).
"""

from src.core.install.harness_profiles import (
    AntigravityProfile,
    ClaudeProfile,
    GeminiProfile,
)


def test_claude_expoe_comando_em_claude_commands():
    rel, content = ClaudeProfile().session_command_artifact("/abs/projeto")
    assert rel == ".claude/commands/encerrar-sessao.md"
    assert "!`./harness cmd encerrar-sessao`" in content
    # `${CLAUDE_PROJECT_DIR}` não é expandida no `!`-bash de slash commands
    # (vira `/harness`); o comando usa `./harness`, relativo à raiz do projeto.
    assert "${CLAUDE_PROJECT_DIR}" not in content


def test_antigravity_expoe_comando_em_agents_workflows():
    rel, content = AntigravityProfile().session_command_artifact("/abs/projeto")
    assert rel == ".agents/workflows/encerrar-sessao.md"
    assert "harness cmd encerrar-sessao" in content


def test_antigravity_resolve_command_path_absoluto():
    _, content = AntigravityProfile().session_command_artifact("/abs/projeto")
    assert "/abs/projeto/harness cmd encerrar-sessao" in content


def test_gemini_nao_expoe_comando():
    assert GeminiProfile().session_command_artifact("/abs/projeto") is None
