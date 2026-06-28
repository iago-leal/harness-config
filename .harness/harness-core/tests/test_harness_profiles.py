"""Testes do contrato de skill por perfil (feature 018, T004).

Substitui os testes de `session_command_artifact` (removido): agora cada perfil
expõe um `skills_dir` por harness e os caminhos legados a limpar na migração
command/workflow → skill. A árvore da skill é agnóstica (mesmos bytes para
todos), validada à parte em `test_session_skills.py`.
"""

from src.core.install.harness_profiles import (
    AntigravityProfile,
    ClaudeProfile,
    GeminiProfile,
    get_profile,
)


def test_claude_skills_dir():
    assert ClaudeProfile().skills_dir() == ".claude/skills"


def test_antigravity_skills_dir_is_plural():
    # `.agents/skills` (plural), distinto do workflow legado `.agent/workflows`.
    assert AntigravityProfile().skills_dir() == ".agents/skills"


def test_gemini_has_no_skills_dir():
    assert GeminiProfile().skills_dir() is None


def test_claude_stale_paths_list_legacy_command():
    # Migração 010/016 → 018: o slash command `.md` vira órfão.
    assert ClaudeProfile().stale_session_command_paths() == [
        ".claude/commands/encerrar-sessao.md"
    ]


def test_antigravity_stale_paths_cover_singular_and_plural_workflows():
    # 017 (singular) e o plural legado anterior à 017, ambos órfãos após a 018.
    assert AntigravityProfile().stale_session_command_paths() == [
        ".agent/workflows/encerrar-sessao.md",
        ".agents/workflows/encerrar-sessao.md",
    ]


def test_gemini_has_no_stale_paths():
    assert GeminiProfile().stale_session_command_paths() == []


def test_get_profile_resolves_known_harnesses():
    assert isinstance(get_profile("claude"), ClaudeProfile)
    assert isinstance(get_profile("antigravity"), AntigravityProfile)
    assert isinstance(get_profile("gemini"), GeminiProfile)
