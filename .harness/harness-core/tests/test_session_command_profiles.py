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
    assert "./harness cmd encerrar-sessao" in content
    # `${CLAUDE_PROJECT_DIR}` não é expandida no `!`-bash de slash commands
    # (vira `/harness`); o comando resolve a raiz via git em vez disso.
    assert "${CLAUDE_PROJECT_DIR}" not in content


def test_claude_roda_da_raiz_independente_do_cwd():
    # O `!`-bash de slash command pode rodar de um subdiretório; `./harness`
    # relativo quebraria fora da raiz. O comando faz `cd` para a raiz do git
    # antes, resolvendo o wrapper E o cwd do core de qualquer subdiretório.
    _, content = ClaudeProfile().session_command_artifact("/abs/projeto")
    assert 'cd "$(git rev-parse --show-toplevel)"' in content


def test_antigravity_roda_da_raiz_independente_do_cwd():
    _, content = AntigravityProfile().session_command_artifact("/abs/projeto")
    assert "cd /abs/projeto && " in content


def test_antigravity_expoe_comando_em_agent_workflows():
    rel, content = AntigravityProfile().session_command_artifact("/abs/projeto")
    # feature 017: caminho singular reconhecido pelo Antigravity (IDE e CLI).
    assert rel == ".agent/workflows/encerrar-sessao.md"
    assert "harness cmd encerrar-sessao" in content


def test_antigravity_resolve_command_path_absoluto():
    _, content = AntigravityProfile().session_command_artifact("/abs/projeto")
    assert "/abs/projeto/harness cmd encerrar-sessao" in content


def test_gemini_nao_expoe_comando():
    assert GeminiProfile().session_command_artifact("/abs/projeto") is None


def test_claude_descreve_commit_de_encerramento():
    _, content = ClaudeProfile().session_command_artifact("/abs/projeto")
    assert "commit de registro" in content
    assert "último commit de trabalho" in content


def test_antigravity_descreve_commit_de_encerramento():
    _, content = AntigravityProfile().session_command_artifact("/abs/projeto")
    assert "commit de registro" in content
    assert "último commit de trabalho" in content


def test_perfis_mencionam_ofertas_de_fim_de_sessao():
    # Feature 014 (RF-12): o texto dos slash commands menciona as ofertas de
    # publicar (push) e atualizar (upgrade), consistente entre os perfis.
    for profile in (ClaudeProfile(), AntigravityProfile()):
        _, content = profile.session_command_artifact("/abs/projeto")
        assert "push" in content
        assert "upgrade" in content


def test_perfis_sequenciam_regen_e_tratam_commit_pendente():
    # Feature 016 (RF-08/D-06): o slash command sequencia regen → encerrar e
    # instrui o agente a tratar o marker COMMIT_PENDENTE, em ambos os perfis.
    for profile in (ClaudeProfile(), AntigravityProfile()):
        _, content = profile.session_command_artifact("/abs/projeto")
        assert "harness cmd regen" in content
        assert "COMMIT_PENDENTE" in content
